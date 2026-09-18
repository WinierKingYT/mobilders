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
from app.focus_domain.models import AttemptJudgment, KCId, KCState
from app.focus_domain.persistence import FocusEpisodePersistenceService
from app.focus_domain.repair_work_evaluator import (
    DelayedRetestEvaluator,
    RetestTaskGenerator,
)


def _service():
    return FocusServiceFacade(FocusEpisodePersistenceService())


def _setup_temporarily_recovered_episode(service, episode_id="r08-ep"):
    # 1. Start
    service.start_ctqf1_episode(
        episode_id=episode_id,
        b=5,
        c=6,
        idempotency_key=f"{episode_id}:start",
    )
    # 2. Trigger probe on S1 incorrect attempt
    res_att = service.submit_attempt(
        episode_id=episode_id,
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[-2, -3],
        idempotency_key=f"{episode_id}:att1",
        expected_previous_sequence=1,
    )
    probe_id = res_att.decision.probe_id

    # 3. Probe response -> START_REPAIR
    service.apply_probe_response(
        episode_id=episode_id,
        probe_id=probe_id,
        response_code="PRODUCT_ONLY",
        idempotency_key=f"{episode_id}:probe1",
        expected_previous_sequence=2,
    )

    # 4. Begin repair
    service.begin_current_repair(
        episode_id=episode_id,
        idempotency_key=f"{episode_id}:begin",
        expected_previous_sequence=3,
    )

    # 5. Submit repair work
    service.submit_repair_work(
        episode_id=episode_id,
        raw_work=[2, 3],
        idempotency_key=f"{episode_id}:work1",
        expected_previous_sequence=4,
    )

    # 6. Submit self-correction
    res_sc = service.submit_original_self_correction(
        episode_id=episode_id,
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key=f"{episode_id}:sc1",
        expected_previous_sequence=5,
    )

    # 7. Submit transfer work
    transfer_task = res_sc.state.transfer_task_context
    t_ans = transfer_task.get("expected_pair", transfer_task.get("expected_answer"))
    res_transfer = service.submit_transfer_work(
        episode_id=episode_id,
        raw_work=t_ans,
        idempotency_key=f"{episode_id}:transfer1",
        expected_previous_sequence=6,
    )
    assert res_transfer.state.learner.kc_states[KCId.F2] == KCState.TEMPORARILY_RECOVERED
    return res_transfer


def test_retest_task_generator_and_evaluator_unit():
    generator = RetestTaskGenerator()
    task = generator.generate_retest_task(KCId.F2)
    assert task["target_kc"] == KCId.F2.value
    assert "prompt" in task
    assert "expected_answer" in task or "expected_pair" in task

    evaluator = DelayedRetestEvaluator()
    ans = task.get("expected_pair", task.get("expected_answer"))
    assert evaluator.evaluate(retest_context=task, raw_work=ans).is_success
    assert not evaluator.evaluate(retest_context=task, raw_work="completely_wrong").is_success


def test_cannot_schedule_retest_unless_temporarily_recovered():
    service = _service()
    service.start_ctqf1_episode(
        episode_id="unrecovered-ep",
        b=5,
        c=6,
        idempotency_key="unrec:start",
    )
    # KCId.F2 is UNKNOWN / UNRESOLVED, not TEMPORARILY_RECOVERED
    with pytest.raises(FocusApplicationError) as exc_info:
        service.schedule_retest(
            episode_id="unrecovered-ep",
            target_kc=KCId.F2,
            idempotency_key="unrec:sched",
            expected_previous_sequence=1,
        )
    assert "requires TEMPORARILY_RECOVERED" in str(exc_info.value)


def test_cannot_start_repair_directly_when_retest_is_due():
    # Strict rule: RETEST_DUE means collect delayed evidence; REPAIR_STARTED is not legal directly
    service = _service()
    res = _setup_temporarily_recovered_episode(service, "sched-no-repair-ep")

    # Schedule retest
    res_sched = service.schedule_retest(
        episode_id="sched-no-repair-ep",
        target_kc=KCId.F2,
        idempotency_key="sched-no-rep:retest",
        expected_previous_sequence=7,
    )
    assert res_sched.state.learner.kc_states[KCId.F2] == KCState.RETEST_DUE

    # Attempting to begin repair directly without failure evidence raises error
    with pytest.raises(Exception):
        service.begin_current_repair(
            episode_id="sched-no-repair-ep",
            idempotency_key="sched-no-rep:bad-repair",
            expected_previous_sequence=8,
        )


def test_delayed_retest_success_creates_durable_evidence():
    service = _service()
    _setup_temporarily_recovered_episode(service, "durable-ep")

    # Schedule retest
    res_sched = service.schedule_retest(
        episode_id="durable-ep",
        target_kc=KCId.F2,
        idempotency_key="durable:sched",
        expected_previous_sequence=7,
    )
    assert res_sched.state.learner.kc_states[KCId.F2] == KCState.RETEST_DUE
    retest_task = res_sched.state.retest_task_context
    assert retest_task is not None
    ans = retest_task.get("expected_pair", retest_task.get("expected_answer"))

    # Submit correct delayed retest work
    res_retest = service.submit_delayed_retest_work(
        episode_id="durable-ep",
        target_kc=KCId.F2,
        raw_work=ans,
        idempotency_key="durable:submit",
        expected_previous_sequence=8,
    )
    assert res_retest.repair_evaluation_success is True
    assert res_retest.state.learner.kc_states[KCId.F2] == KCState.DURABLE_EVIDENCE


def test_delayed_retest_failure_creates_relapsed_state():
    service = _service()
    _setup_temporarily_recovered_episode(service, "relapse-ep")

    # Schedule retest
    res_sched = service.schedule_retest(
        episode_id="relapse-ep",
        target_kc=KCId.F2,
        idempotency_key="relapse:sched",
        expected_previous_sequence=7,
    )
    assert res_sched.state.learner.kc_states[KCId.F2] == KCState.RETEST_DUE

    # Submit incorrect delayed retest work
    res_retest = service.submit_delayed_retest_work(
        episode_id="relapse-ep",
        target_kc=KCId.F2,
        raw_work="invalid_answer",
        idempotency_key="relapse:submit",
        expected_previous_sequence=8,
    )
    assert res_retest.repair_evaluation_success is False
    assert res_retest.state.learner.kc_states[KCId.F2] == KCState.RELAPSED


def test_retest_api_http_endpoints():
    app = FastAPI()
    service = _service()
    install_focus_api(app, enabled=True, service=service)
    client = TestClient(app)

    # Setup temporarily recovered episode
    _setup_temporarily_recovered_episode(service, "http-retest-ep")

    # Schedule retest via HTTP
    r_sched = client.post(
        "/focus/v1/episodes/http-retest-ep/retest/schedule",
        json={"target_kc": "KC-F2"},
        headers={"Idempotency-Key": "http-sched:1", "X-Focus-Expected-Sequence": "7"},
    )
    assert r_sched.status_code == 200
    state = r_sched.json()["state"]
    assert state["learner"]["kc_states"]["KC-F2"] == "RETEST_DUE"
    retest_task = state["retest_task_context"]
    assert retest_task is not None
    ans = retest_task.get("expected_pair", retest_task.get("expected_answer"))

    # Submit delayed retest work via HTTP
    r_submit = client.post(
        "/focus/v1/episodes/http-retest-ep/retest/submit",
        json={"target_kc": "KC-F2", "raw_work": ans},
        headers={"Idempotency-Key": "http-submit:1", "X-Focus-Expected-Sequence": "8"},
    )
    assert r_submit.status_code == 200
    res_body = r_submit.json()
    assert res_body["repair_evaluation_success"] is True
    assert res_body["state"]["learner"]["kc_states"]["KC-F2"] == "DURABLE_EVIDENCE"
