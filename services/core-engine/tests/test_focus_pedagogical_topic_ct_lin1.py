import pytest
from app.focus_domain.application import (
    FocusAttemptInputKind,
    FocusCommandResult,
    FocusServiceFacade,
)
from app.focus_domain.decision_pipeline import EpisodePhase, NextActionType
from app.focus_domain.models import (
    AttemptJudgment,
    CTINEQ1TaskContext,
    CTLIN1TaskContext,
    KCId,
    StageId,
)
from app.focus_domain.persistence import (
    FocusEpisodePersistenceService,
    InMemoryFocusEventRepository,
    InMemoryFocusSnapshotRepository,
)
from app.focus_domain.repair_work_evaluator import (
    RepairWorkEvaluator,
    TransferTaskGenerator,
)
from app.focus_domain.truth_adapter import AlphaTruthAdapter, TruthFactCode


def _service() -> FocusServiceFacade:
    persistence = FocusEpisodePersistenceService(
        journal=InMemoryFocusEventRepository(),
        snapshots=InMemoryFocusSnapshotRepository(),
    )
    return FocusServiceFacade(persistence=persistence)


def test_start_ctlin1_episode_deterministic_initialization():
    """Verify server creates deterministic CT-LIN1 episode with correct KC and context."""
    service = _service()
    res = service.start_ctlin1_episode(
        episode_id="ep-lin-1",
        a=2,
        b=4,
        c=10,
        idempotency_key="k-lin-init",
    )
    assert res.stream_version == 1
    assert res.state.composite_task_id == "CT-LIN1"
    assert res.state.workspace_kc == KCId.L1
    assert res.state.current_stage == StageId.S1_ISOLATE_TERM
    assert res.state.phase == EpisodePhase.WORKSPACE

    ctx = res.state.task_context
    assert isinstance(ctx, CTLIN1TaskContext)
    assert ctx.a == 2
    assert ctx.b == 4
    assert ctx.c == 10
    assert ctx.expected_intermediate_rhs == 6  # 10 - 4
    assert ctx.expected_root == 3  # 6 / 2


def test_start_ctineq1_episode_deterministic_initialization():
    """Verify server creates deterministic CT-INEQ1 episode with correct negative flip requirement."""
    service = _service()
    res = service.start_ctineq1_episode(
        episode_id="ep-ineq-1",
        a=-3,
        b=5,
        c=14,
        comparator="<=",
        idempotency_key="k-ineq-init",
    )
    assert res.stream_version == 1
    assert res.state.composite_task_id == "CT-INEQ1"
    assert res.state.workspace_kc == KCId.I1
    assert res.state.current_stage == StageId.S1_ISOLATE_TERM

    ctx = res.state.task_context
    assert isinstance(ctx, CTINEQ1TaskContext)
    assert ctx.a == -3
    assert ctx.b == 5
    assert ctx.c == 14
    assert ctx.comparator == "<="
    assert ctx.expected_intermediate_rhs == 9  # 14 - 5
    assert ctx.expected_root == -3  # 9 / -3
    assert ctx.expected_comparator == ">="


def test_ctlin1_happy_path_stage_progression_to_completion():
    """Verify complete valid path through S1 -> S2 -> S3 to COMPLETE_TASK for 2x + 4 = 10."""
    service = _service()
    service.start_ctlin1_episode(
        episode_id="ep-lin-happy",
        a=2,
        b=4,
        c=10,
        idempotency_key="k-init",
    )

    # S1: Isolate term: 2x = 6
    r1 = service.submit_attempt(
        episode_id="ep-lin-happy",
        input_kind=FocusAttemptInputKind.EQUATION_REWRITE,
        raw_input="2x = 6",
        idempotency_key="k-s1",
        expected_previous_sequence=1,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_ISOLATE_VARIABLE
    assert r1.decision.action == NextActionType.ADVANCE

    # S2: Isolate variable: x = 3
    r2 = service.submit_attempt(
        episode_id="ep-lin-happy",
        input_kind=FocusAttemptInputKind.VARIABLE_ASSIGNMENT,
        raw_input="x = 3",
        idempotency_key="k-s2",
        expected_previous_sequence=2,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_VERIFY_SOLUTION
    assert r2.decision.action == NextActionType.ADVANCE

    # S3: Verify solution: 3
    r3 = service.submit_attempt(
        episode_id="ep-lin-happy",
        input_kind=FocusAttemptInputKind.SOLUTION_SET,
        raw_input=[3],
        idempotency_key="k-s3",
        expected_previous_sequence=3,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctlin1_bug_found_15_one_sided_balance_error():
    """Verify BUG-FOUND-15: Student adds 4 instead of subtracting (2x = 14) triggers observation."""
    service = _service()
    service.start_ctlin1_episode(
        episode_id="ep-lin-bug15",
        a=2,
        b=4,
        c=10,
        idempotency_key="k-init",
    )

    r1 = service.submit_attempt(
        episode_id="ep-lin-bug15",
        input_kind=FocusAttemptInputKind.EQUATION_REWRITE,
        raw_input="2x = 14",  # 10 + 4 instead of 10 - 4
        idempotency_key="k-s1-bug",
        expected_previous_sequence=1,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-EQUALITY-ONE-SIDE-CHANGED" in r1.observations
    assert r1.state.current_stage == StageId.S1_ISOLATE_TERM


def test_ctlin1_bug_found_07_coefficient_subtracted_instead_of_divided():
    """Verify BUG-FOUND-07: Student does 6 - 2 = 4 instead of 6 / 2 = 3 at S2."""
    service = _service()
    service.start_ctlin1_episode(
        episode_id="ep-lin-bug07",
        a=2,
        b=4,
        c=10,
        idempotency_key="k-init",
    )

    # First pass S1 correctly
    service.submit_attempt(
        episode_id="ep-lin-bug07",
        input_kind=FocusAttemptInputKind.EQUATION_REWRITE,
        raw_input="2x = 6",
        idempotency_key="k-s1",
        expected_previous_sequence=1,
    )

    # S2: Submit x = 4 (6 - 2)
    r2 = service.submit_attempt(
        episode_id="ep-lin-bug07",
        input_kind=FocusAttemptInputKind.VARIABLE_ASSIGNMENT,
        raw_input="x = 4",
        idempotency_key="k-s2-bug",
        expected_previous_sequence=2,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-COEFFICIENT-SUBTRACTED" in r2.observations


def test_ctineq1_bug_found_14_inequality_direction_not_reversed():
    """Verify BUG-FOUND-14: Dividing -3x <= 9 by -3 without flipping direction produces direction error."""
    service = _service()
    service.start_ctineq1_episode(
        episode_id="ep-ineq-bug14",
        a=-3,
        b=5,
        c=14,
        comparator="<=",
        idempotency_key="k-init",
    )

    # S1: Isolate term correctly: -3x <= 9
    r1 = service.submit_attempt(
        episode_id="ep-ineq-bug14",
        input_kind=FocusAttemptInputKind.INEQUALITY_REWRITE,
        raw_input="-3x <= 9",
        idempotency_key="k-s1",
        expected_previous_sequence=1,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_DIRECTION_AWARE_DIVISION

    # S2: Mistake - does not flip direction: x <= -3
    r2 = service.submit_attempt(
        episode_id="ep-ineq-bug14",
        input_kind=FocusAttemptInputKind.INEQUALITY_REWRITE,
        raw_input="x <= -3",
        idempotency_key="k-s2-bug",
        expected_previous_sequence=2,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-INEQUALITY-DIRECTION-NOT-REVERSED" in r2.observations

    # Correct submission: x >= -3
    r3 = service.submit_attempt(
        episode_id="ep-ineq-bug14",
        input_kind=FocusAttemptInputKind.INEQUALITY_REWRITE,
        raw_input="x >= -3",
        idempotency_key="k-s2-correct",
        expected_previous_sequence=3,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_repair_and_transfer_evaluator_linear_and_inequality():
    """Verify repair work evaluation and transfer task generation for L1 and I1."""
    evaluator = RepairWorkEvaluator()

    # IT-L1-01: Balance & coefficient division repair
    r_l1 = evaluator.evaluate_repair(
        intervention_id="IT-L1-01",
        raw_work="divide",
    )
    assert r_l1.is_success is True

    # IT-I1-01: Negative multiplier flip repair
    r_i1 = evaluator.evaluate_repair(
        intervention_id="IT-I1-01",
        raw_work="flip",
    )
    assert r_i1.is_success is True

    # Transfer task generation
    task_l1 = TransferTaskGenerator.generate_transfer_task(KCId.L1)
    assert "3x = 15" in task_l1["prompt"]
    assert task_l1["expected_answer"] == "5"

    task_i1 = TransferTaskGenerator.generate_transfer_task(KCId.I1)
    assert "-2x <= 8" in task_i1["prompt"]
    assert ">=" in task_i1["expected_answer"]


def test_api_endpoints_ctlin1_and_ctineq1():
    """Verify HTTP API can launch and interact with CT-LIN1 and CT-INEQ1 episodes."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.focus_domain.api import install_focus_api

    app = FastAPI()
    service = _service()
    install_focus_api(app=app, service=service, enabled=True)
    client = TestClient(app)

    # Start CT-LIN1 episode via HTTP POST
    r_start = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http-lin:start"},
        json={"episode_id": "http-lin-1", "topic_id": "CT-LIN1", "a": 3, "b": 6, "c": 15},
    )
    assert r_start.status_code == 201
    data = r_start.json()
    assert data["state"]["composite_task_id"] == "CT-LIN1"
    assert data["state"]["current_stage"] == "S1_ISOLATE_TERM"

    # Submit S1 attempt via HTTP POST
    r_s1 = client.post(
        "/focus/v1/episodes/http-lin-1/attempts",
        headers={"Idempotency-Key": "http-lin:s1", "X-Focus-Expected-Sequence": "1"},
        json={"input_kind": "EQUATION_REWRITE", "input": "3x = 9"},
    )
    assert r_s1.status_code == 200
    res_s1 = r_s1.json()
    assert res_s1["judgment"] == "VALID_EXPECTED"
    assert res_s1["state"]["current_stage"] == "S2_ISOLATE_VARIABLE"

    # Start CT-INEQ1 episode via HTTP POST
    r_start_ineq = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http-ineq:start"},
        json={"episode_id": "http-ineq-1", "topic_id": "CT-INEQ1", "a": -2, "b": 3, "c": 7, "comparator": "<="},
    )
    assert r_start_ineq.status_code == 201
    data_ineq = r_start_ineq.json()
    assert data_ineq["state"]["composite_task_id"] == "CT-INEQ1"
    assert data_ineq["state"]["current_stage"] == "S1_ISOLATE_TERM"
