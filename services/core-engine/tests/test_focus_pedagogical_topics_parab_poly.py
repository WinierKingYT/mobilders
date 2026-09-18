from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import install_focus_api
from app.focus_domain.application import FocusAttemptInputKind, FocusServiceFacade
from app.focus_domain.models import AttemptJudgment, KCId, StageId
from app.focus_domain.decision_pipeline import EpisodePhase, NextActionType
from app.focus_domain.persistence import (
    FocusEpisodePersistenceService,
    InMemoryFocusEventRepository,
    InMemoryFocusSnapshotRepository,
)
from app.focus_domain.repair_work_evaluator import RepairWorkEvaluator, TransferTaskGenerator


def _service() -> FocusServiceFacade:
    persistence = FocusEpisodePersistenceService(
        journal=InMemoryFocusEventRepository(),
        snapshots=InMemoryFocusSnapshotRepository(),
    )
    return FocusServiceFacade(persistence=persistence)


@pytest.fixture
def facade() -> FocusServiceFacade:
    return _service()


@pytest.fixture
def client(facade: FocusServiceFacade) -> TestClient:
    app = FastAPI()
    install_focus_api(
        app=app,
        service=facade,
        enabled=True,
        canary_percentage=100,
        kill_switch=False,
    )
    return TestClient(app)


def test_ctpar1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: f(x) = x^2 - 4x + 3. r = 2, k = -1, minimum."""
    res = facade.start_ctpar1_episode(
        episode_id="ep_par1_01",
        a=1,
        b=-4,
        c=3,
        idempotency_key="idemp_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-PAR1"
    assert state.workspace_kc == KCId.P1
    assert state.current_stage == StageId.S1_CALCULATE_R
    assert state.task_context.expected_r == 2.0
    assert state.task_context.expected_k == -1.0
    assert state.task_context.is_minimum is True

    # S1: Calculate r = 2
    r1 = facade.submit_attempt(
        episode_id="ep_par1_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="r = 2",
        idempotency_key="idemp_r",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_CALCULATE_K
    assert r1.state.workspace_kc == KCId.P1

    # S2: Calculate k = -1
    r2 = facade.submit_attempt(
        episode_id="ep_par1_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="k = -1",
        idempotency_key="idemp_k",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_EXTREMUM_CLASSIFICATION
    assert r2.state.workspace_kc == KCId.P2

    # S3: Extremum classification -> minimum
    r3 = facade.submit_attempt(
        episode_id="ep_par1_01",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="minimum",
        idempotency_key="idemp_min",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctpar1_bug_parab_01_sign_inverted(facade: FocusServiceFacade):
    """BUG-PARAB-01: f(x) = x^2 - 6x + 5. True r = 3. Student submits r = -3."""
    res = facade.start_ctpar1_episode(
        episode_id="ep_par1_bug1",
        a=1,
        b=-6,
        c=5,
        idempotency_key="idemp_start",
    )

    r1 = facade.submit_attempt(
        episode_id="ep_par1_bug1",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="r = -3",
        idempotency_key="idemp_bug1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-VERTEX-FORMULA-SIGN-INVERTED" in r1.observations
    assert r1.decision.action == NextActionType.REQUEST_PROBE
    assert r1.decision.probe_id == "PR-P1-01"


def test_ctpar1_bug_parab_02_ordinate_equals_constant(facade: FocusServiceFacade):
    """BUG-PARAB-02: f(x) = x^2 - 4x + 7. True r = 2, k = 3. Student submits k = 7."""
    res = facade.start_ctpar1_episode(
        episode_id="ep_par1_bug2",
        a=1,
        b=-4,
        c=7,
        idempotency_key="idemp_start",
    )
    # Stage 1: pass r = 2
    r1 = facade.submit_attempt(
        episode_id="ep_par1_bug2",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="2",
        idempotency_key="idemp_r",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_CALCULATE_K

    # Stage 2: submit k = 7 (constant term instead of k = 3)
    r2 = facade.submit_attempt(
        episode_id="ep_par1_bug2",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="k = 7",
        idempotency_key="idemp_k_bug",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-VERTEX-ORDINATE-CONFUSED-WITH-CONSTANT" in r2.observations


def test_ctpoly1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: P(x) = x^2 + 2x - 3, divisor (x - 1). Root is 1, remainder 0."""
    res = facade.start_ctpoly1_episode(
        episode_id="ep_poly1_01",
        a=1,
        b=2,
        c=-3,
        divisor_root=1,
        idempotency_key="idemp_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-POLY1"
    assert state.workspace_kc == KCId.PL1
    assert state.current_stage == StageId.S1_ROOT_OF_DIVISOR
    assert state.task_context.divisor_root == 1
    assert state.task_context.expected_remainder == 0

    # S1: Divisor root x = 1
    r1 = facade.submit_attempt(
        episode_id="ep_poly1_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="x = 1",
        idempotency_key="idemp_root",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_EVALUATE_REMAINDER
    assert r1.state.workspace_kc == KCId.PL1

    # S2: Remainder = 0
    r2 = facade.submit_attempt(
        episode_id="ep_poly1_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="kalan = 0",
        idempotency_key="idemp_rem",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.decision.action == NextActionType.COMPLETE_TASK
    assert r2.state.phase == EpisodePhase.COMPLETED


def test_ctpoly1_bug_poly_01_divisor_root_sign_inverted(facade: FocusServiceFacade):
    """BUG-POLY-01: Divisor (x - 2). Root is 2. Student submits x = -2."""
    res = facade.start_ctpoly1_episode(
        episode_id="ep_poly1_bug1",
        a=1,
        b=2,
        c=-3,
        divisor_root=2,
        idempotency_key="idemp_start",
    )

    r1 = facade.submit_attempt(
        episode_id="ep_poly1_bug1",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="x = -2",
        idempotency_key="idemp_root_bug",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-DIVISOR-ROOT-SIGN-INVERTED" in r1.observations
    assert r1.decision.action == NextActionType.REQUEST_PROBE
    assert r1.decision.probe_id == "PR-PL1-01"


def test_ctpoly1_bug_poly_02_remainder_confused_with_coeff_sum(facade: FocusServiceFacade):
    """BUG-POLY-02: P(x) = 2x^2 + 3x - 1, divisor (x - 2). True R = 13. Student submits P(1) = 4."""
    res = facade.start_ctpoly1_episode(
        episode_id="ep_poly1_bug2",
        a=2,
        b=3,
        c=-1,
        divisor_root=2,
        idempotency_key="idemp_start",
    )
    # Stage 1: pass x = 2
    r1 = facade.submit_attempt(
        episode_id="ep_poly1_bug2",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="2",
        idempotency_key="idemp_root",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_EVALUATE_REMAINDER

    # Stage 2: submit kalan = 4 (sum of coefficients)
    r2 = facade.submit_attempt(
        episode_id="ep_poly1_bug2",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="kalan = 4",
        idempotency_key="idemp_rem_bug",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-REMAINDER-CONFUSED-WITH-COEFF-SUM" in r2.observations


def test_parab_poly_repair_and_transfer_flows():
    evaluator = RepairWorkEvaluator()
    # IT-P1-01
    res_p = evaluator.evaluate_repair(intervention_id="IT-P1-01", raw_work="r = -b/(2a)")
    assert res_p.is_success is True
    res_p_fail = evaluator.evaluate_repair(intervention_id="IT-P1-01", raw_work="r = b/(2a)")
    assert res_p_fail.is_success is False

    # IT-PL1-01
    res_pl = evaluator.evaluate_repair(intervention_id="IT-PL1-01", raw_work="x = d yerine yazılır")
    assert res_pl.is_success is True

    # Transfer task generation
    generator = TransferTaskGenerator()
    tt_p = generator.generate_transfer_task(KCId.P1)
    assert tt_p["target_kc"] == KCId.P1.value
    tt_pl = generator.generate_transfer_task(KCId.PL1)
    assert tt_pl["target_kc"] == KCId.PL1.value


def test_fastapi_endpoints_parab_poly_live(client: TestClient):
    # 1. Start CT-PAR1
    resp1 = client.post(
        "/focus/v1/episodes",
        json={
            "episode_id": "api_par1",
            "topic_id": "CT-PAR1",
            "a": 1,
            "b": -4,
            "c": 3,
        },
        headers={"Idempotency-Key": "key_par1"},
    )
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["state"]["composite_task_id"] == "CT-PAR1"
    assert data1["state"]["current_stage"] == "S1_CALCULATE_R"

    # 2. Start CT-POLY1
    resp2 = client.post(
        "/focus/v1/episodes",
        json={
            "episode_id": "api_poly1",
            "topic_id": "CT-POLY1",
            "a": 1,
            "b": 2,
            "c": -3,
            "divisor_root": 1,
        },
        headers={"Idempotency-Key": "key_poly1"},
    )
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["state"]["composite_task_id"] == "CT-POLY1"
    assert data2["state"]["current_stage"] == "S1_ROOT_OF_DIVISOR"
