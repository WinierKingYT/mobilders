import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import create_focus_router, install_focus_api
from app.focus_domain.application import (
    FocusApplicationError,
    FocusAttemptInputKind,
    FocusServiceFacade,
)
from app.focus_domain.decision_pipeline import EpisodePhase
from app.focus_domain.models import AttemptJudgment, KCId, KCState, StageId
from app.focus_domain.persistence import FocusEpisodePersistenceService
from app.focus_domain.repair_work_evaluator import RepairWorkEvaluator, TransferTaskGenerator


def _service():
    return FocusServiceFacade(FocusEpisodePersistenceService())


def _start_and_trigger_repair(service, episode_id="r07-ep"):
    # b=5, c=6 -> roots -2, -3. Factor pair (2, 3)
    service.start_ctqf1_episode(
        episode_id=episode_id,
        b=5,
        c=6,
        idempotency_key=f"{episode_id}:start",
    )
    # Incorrect attempt at S1: sum/product error: e.g. [-2, -3] -> INCORRECT
    result = service.submit_attempt(
        episode_id=episode_id,
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[-2, -3],
        idempotency_key=f"{episode_id}:att1",
        expected_previous_sequence=1,
    )
    # Decision requests probe PR-F2-01
    assert result.decision is not None
    probe_id = result.decision.probe_id
    assert probe_id == "PR-F2-01"

    # Submit probe response
    res_probe = service.apply_probe_response(
        episode_id=episode_id,
        probe_id=probe_id,
        response_code="PRODUCT_ONLY",
        idempotency_key=f"{episode_id}:probe1",
        expected_previous_sequence=2,
    )
    assert res_probe.decision.action.value == "START_REPAIR"

    # Begin repair
    res_repair = service.begin_current_repair(
        episode_id=episode_id,
        idempotency_key=f"{episode_id}:begin",
        expected_previous_sequence=3,
    )
    return res_repair


def test_repair_work_evaluator_unit():
    evaluator = RepairWorkEvaluator()

    # IT-N1-01
    assert evaluator.evaluate_repair(intervention_id="IT-N1-01", raw_work=1).is_success
    assert not evaluator.evaluate_repair(intervention_id="IT-N1-01", raw_work="invalid").is_success

    # IT-N2-01
    assert evaluator.evaluate_repair(intervention_id="IT-N2-01", raw_work=[-15, 15]).is_success
    assert not evaluator.evaluate_repair(intervention_id="IT-N2-01", raw_work=[15, 15]).is_success

    # IT-F2-01
    assert evaluator.evaluate_repair(intervention_id="IT-F2-01", raw_work=[2, 3], context={"b": 5, "c": 6}).is_success
    assert evaluator.evaluate_repair(intervention_id="IT-F2-01", raw_work=[3, 2], context={"b": 5, "c": 6}).is_success
    assert not evaluator.evaluate_repair(intervention_id="IT-F2-01", raw_work=[1, 6], context={"b": 5, "c": 6}).is_success


def test_transfer_task_generator():
    task_n1 = TransferTaskGenerator.generate_transfer_task(KCId.N1)
    assert task_n1["target_kc"] == KCId.N1.value
    assert "prompt" in task_n1
    assert "expected_answer" in task_n1

    evaluator = RepairWorkEvaluator()
    assert evaluator.evaluate_transfer(transfer_context=task_n1, raw_work=task_n1["expected_answer"]).is_success
    assert not evaluator.evaluate_transfer(transfer_context=task_n1, raw_work="wrong").is_success


def test_full_repair_to_transfer_flow_success():
    service = _service()
    res = _start_and_trigger_repair(service, "flow-ep")
    assert res.state.phase == EpisodePhase.REPAIRING
    assert res.state.repair_intervention_id == "IT-F2-01"

    # Step 1: Submit valid repair work for IT-F2-01: factor pair [2, 3]
    res_work = service.submit_repair_work(
        episode_id="flow-ep",
        raw_work=[2, 3],
        idempotency_key="flow-ep:work1",
        expected_previous_sequence=4,
    )
    assert res_work.repair_evaluation_success is True
    assert res_work.state.phase == EpisodePhase.AWAITING_ORIGINAL_SELF_CORRECTION

    # Step 2: Submit original self-correction (correct factor pair [2, 3] for b=5, c=6)
    res_sc = service.submit_original_self_correction(
        episode_id="flow-ep",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="flow-ep:sc1",
        expected_previous_sequence=5,
    )
    assert res_sc.judgment == AttemptJudgment.VALID_EXPECTED
    assert res_sc.state.phase == EpisodePhase.AWAITING_TRANSFER
    assert res_sc.state.transfer_task_context is not None

    # Step 3: Submit transfer work
    transfer_task = res_sc.state.transfer_task_context
    t_ans = transfer_task.get("expected_pair", transfer_task.get("expected_answer"))

    res_transfer = service.submit_transfer_work(
        episode_id="flow-ep",
        raw_work=t_ans,
        idempotency_key="flow-ep:transfer1",
        expected_previous_sequence=6,
    )
    assert res_transfer.repair_evaluation_success is True
    assert res_transfer.state.phase == EpisodePhase.WORKSPACE
    # KC F2 should be TEMPORARILY_RECOVERED
    assert res_transfer.state.learner.kc_states[KCId.F2] == KCState.TEMPORARILY_RECOVERED


def test_repair_work_rejection_on_incorrect_work():
    service = _service()
    res = _start_and_trigger_repair(service, "fail-ep")

    # Submit wrong work for IT-F2-01: invalid pair
    with pytest.raises(FocusApplicationError) as exc_info:
        service.submit_repair_work(
            episode_id="fail-ep",
            raw_work=[1, 99],
            idempotency_key="fail-ep:work-wrong",
            expected_previous_sequence=4,
        )
    assert "Repair work was incorrect" in str(exc_info.value)

    # State should remain in REPAIRING
    view = service.get_episode("fail-ep")
    assert view.state.phase == EpisodePhase.REPAIRING


def test_repair_api_http_endpoints():
    app = FastAPI()
    service = _service()
    install_focus_api(app, enabled=True, service=service)
    client = TestClient(app)

    # Start episode
    r = client.post(
        "/focus/v1/episodes",
        json={"episode_id": "http-ep", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-start"},
    )
    assert r.status_code == 201

    # Submit wrong attempt
    r = client.post(
        "/focus/v1/episodes/http-ep/attempts",
        json={"input_kind": "FACTOR_PAIR", "input": [-2, -3]},
        headers={"Idempotency-Key": "k-att1", "X-Focus-Expected-Sequence": "1"},
    )
    assert r.status_code == 200
    probe_id = r.json()["decision"]["probe_id"]

    # Probe response
    r = client.post(
        "/focus/v1/episodes/http-ep/probe-responses",
        json={"probe_id": probe_id, "response_code": "PRODUCT_ONLY"},
        headers={"Idempotency-Key": "k-p1", "X-Focus-Expected-Sequence": "2"},
    )
    assert r.status_code == 200

    # Begin repair
    r = client.post(
        "/focus/v1/episodes/http-ep/repair/begin",
        headers={"Idempotency-Key": "k-rep-begin", "X-Focus-Expected-Sequence": "3"},
    )
    assert r.status_code == 200
    state = r.json()["state"]
    assert state["phase"] == "REPAIRING"

    # Submit correct repair work
    r = client.post(
        "/focus/v1/episodes/http-ep/repair/work",
        json={"raw_work": [2, 3]},
        headers={"Idempotency-Key": "k-rep-work", "X-Focus-Expected-Sequence": "4"},
    )
    assert r.status_code == 200
    assert r.json()["repair_evaluation_success"] is True
    assert r.json()["state"]["phase"] == "AWAITING_ORIGINAL_SELF_CORRECTION"

    # Submit self correction
    r = client.post(
        "/focus/v1/episodes/http-ep/repair/self-correction",
        json={"input_kind": "FACTOR_PAIR", "input": [2, 3]},
        headers={"Idempotency-Key": "k-sc", "X-Focus-Expected-Sequence": "5"},
    )
    assert r.status_code == 200
    assert r.json()["judgment"] == "VALID_EXPECTED"
    assert r.json()["state"]["phase"] == "AWAITING_TRANSFER"

    # Submit transfer work
    transfer_task = r.json()["state"]["transfer_task_context"]
    t_ans = transfer_task.get("expected_pair", transfer_task.get("expected_answer"))

    r = client.post(
        "/focus/v1/episodes/http-ep/repair/transfer",
        json={"raw_work": t_ans},
        headers={"Idempotency-Key": "k-transfer", "X-Focus-Expected-Sequence": "6"},
    )
    assert r.status_code == 200
    assert r.json()["repair_evaluation_success"] is True
    assert r.json()["state"]["phase"] == "WORKSPACE"
