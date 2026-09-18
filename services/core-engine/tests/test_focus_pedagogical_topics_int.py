from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.focus_domain.api import install_focus_api
from app.focus_domain.application import FocusAttemptInputKind, FocusServiceFacade
from app.focus_domain.models import AttemptJudgment, KCId, StageId, ProbeEvidenceKind
from app.focus_domain.decision_pipeline import EpisodePhase, NextActionType
from app.focus_domain.persistence import (
    FocusEpisodePersistenceService,
    InMemoryFocusEventRepository,
    InMemoryFocusSnapshotRepository,
)
from app.focus_domain.registry import (
    PROBE_TEMPLATES,
    INTERVENTION_TEMPLATES,
    ACTIVE_DIAGNOSTIC_ROUTES,
    REPAIR_EDGES,
    validate_focus_registry,
)
from app.root_pedagogy.root_dag import RootPrerequisiteDAG


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


# ==============================================================================
# 1. ROOT DAG & MISCONCEPTION MAPPING TESTS (BUG-INT-01..10)
# ==============================================================================

def test_root_dag_integral_misconceptions():
    """Verify all 10 integral misconceptions map to Level -3..-1 root nodes."""
    dag = RootPrerequisiteDAG()
    for bug_idx in range(1, 11):
        bug_id = f"BUG-INT-{bug_idx:02d}"
        node_id = dag.map_bug_to_root_node(bug_id)
        assert node_id is not None, f"{bug_id} must map to a root node"
        assert node_id in dag.nodes, f"Node {node_id} must exist in DAG nodes"
        node = dag.nodes[node_id]
        assert node.level in (-3, -2.5, -2, -1), f"Root node {node_id} level must be in -3..-1, got {node.level}"


# ==============================================================================
# 2. CAS INTEGRAL SYMBOLIC VERIFICATION TESTS
# ==============================================================================

def test_cas_integral_methods():
    """Verify CAS engine handles indefinite, definite, Riemann sum, and verification."""
    cas = SymbolicEquivalenceEngine()

    # Indefinite integral: int(2*x, x) = x**2
    indef = cas.compute_indefinite_integral("2*x", "x")
    assert "x**2" in str(indef) or "x^2" in str(indef)

    # Definite integral: int(2*x, x, 0, 3) = 9
    exact, val = cas.compute_definite_integral("2*x", var="x", a=0, b=3)
    assert exact == 9
    assert val == 9.0

    # Verification of candidate antiderivative
    assert cas.verify_integral("2*x", "x**2 + 5") is True
    assert cas.verify_integral("2*x", "2*x**2") is False

    # Riemann sum
    riemann = cas.compute_riemann_sum("2*x", 0, 3, 6, method="midpoint")
    assert abs(riemann - 9.0) < 0.1


# ==============================================================================
# 3. REGISTRY CONTRACT INVARIANTS FOR INTEGRAL
# ==============================================================================

def test_registry_contract_invariants():
    """Validate frozen contract lengths and presence of CT-INT1 items."""
    validate_focus_registry()
    assert len(PROBE_TEMPLATES) == 11
    assert len(INTERVENTION_TEMPLATES) == 12

    assert "PR-IN1-01" in PROBE_TEMPLATES
    assert "IT-IN1-01" in INTERVENTION_TEMPLATES
    assert "DR-IN1-01" in ACTIVE_DIAGNOSTIC_ROUTES
    assert "RE-IN1-N2" in REPAIR_EDGES

    route = ACTIVE_DIAGNOSTIC_ROUTES["DR-IN1-01"]
    assert route.active_kc == KCId.IN1
    assert route.probe_id == "PR-IN1-01"
    assert route.intervention_id == "IT-IN1-01"

    edge = REPAIR_EDGES["RE-IN1-N2"]
    assert edge.from_kc == KCId.IN1
    assert edge.to_kc == KCId.N2
    assert edge.preferred_probe_id == "PR-N2-01"


# ==============================================================================
# 4. CT-INT1 INITIALIZATION & HAPPY PATH
# ==============================================================================

def test_ctint1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: int_0^3 2x dx -> F(x)=x^2 -> F(3)-F(0)=9 -> Area=9 -> COMPLETED."""
    res = facade.start_ctint1_episode(
        episode_id="ep_int_01",
        m=2,
        n=0,
        a=0,
        b=3,
        idempotency_key="idemp_int_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-INT1"
    assert state.workspace_kc == KCId.IN1
    assert state.current_stage == StageId.S1_FIND_ANTIDERIVATIVE
    assert state.task_context.expected_antiderivative_str == "x^2"
    assert state.task_context.expected_fb == 9.0
    assert state.task_context.expected_fa == 0.0
    assert state.task_context.expected_definite_value == 9.0

    # S1: Antiderivative x^2
    r1 = facade.submit_attempt(
        episode_id="ep_int_01",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x^2",
        idempotency_key="idemp_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_APPLY_LIMITS
    assert r1.state.workspace_kc == KCId.IN1

    # S2: Apply limits F(3) - F(0) = 9
    r2 = facade.submit_attempt(
        episode_id="ep_int_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="9",
        idempotency_key="idemp_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_COMPUTE_DEFINITE_INTEGRAL
    assert r2.state.workspace_kc == KCId.IN1

    # S3: Definite integral / area value 9
    r3 = facade.submit_attempt(
        episode_id="ep_int_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="9",
        idempotency_key="idemp_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


# ==============================================================================
# 5. CT-INT1 INPUT VARIATIONS & FORMATTING TOLERANCE
# ==============================================================================

def test_ctint1_input_variations(facade: FocusServiceFacade):
    """Verify input variations like 'x^2 + C', 'x**2', 'F(b)-F(a)=9', 'Alan = 9'."""
    res = facade.start_ctint1_episode(
        episode_id="ep_int_var",
        m=2,
        n=0,
        a=0,
        b=3,
        idempotency_key="idemp_int_var_start",
    )

    # S1 variation: 'x^2 + C'
    r1 = facade.submit_attempt(
        episode_id="ep_int_var",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x^2 + C",
        idempotency_key="idemp_var_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED

    # S2 variation: '9 - 0'
    r2 = facade.submit_attempt(
        episode_id="ep_int_var",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="9 - 0",
        idempotency_key="idemp_var_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED

    # S3 variation: 'Alan = 9.0'
    r3 = facade.submit_attempt(
        episode_id="ep_int_var",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="Alan = 9.0",
        idempotency_key="idemp_var_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.state.phase == EpisodePhase.COMPLETED


# ==============================================================================
# 6. CT-INT1 INVALID ATTEMPTS & ERROR OBSERVATIONS
# ==============================================================================

def test_ctint1_invalid_attempts_and_observations(facade: FocusServiceFacade):
    """Invalid attempts generate specific error observations."""
    res = facade.start_ctint1_episode(
        episode_id="ep_int_err",
        m=2,
        n=0,
        a=0,
        b=3,
        idempotency_key="idemp_int_err_start",
    )

    # S1 error: wrong antiderivative 2x^2 (failed to divide by exponent)
    r1 = facade.submit_attempt(
        episode_id="ep_int_err",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="2x^2",
        idempotency_key="idemp_err_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-INTEGRAL-ANTIDERIV-WRONG" in r1.observations

    # Correct S1 to advance
    r1_ok = facade.submit_attempt(
        episode_id="ep_int_err",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x^2",
        idempotency_key="idemp_s1_fix",
        expected_previous_sequence=r1.stream_version,
    )
    assert r1_ok.judgment == AttemptJudgment.VALID_EXPECTED

    # S2 error: wrong limits difference 3
    r2 = facade.submit_attempt(
        episode_id="ep_int_err",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="3",
        idempotency_key="idemp_err_s2",
        expected_previous_sequence=r1_ok.stream_version,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-INTEGRAL-LIMITS-WRONG" in r2.observations

    # Correct S2 to advance
    r2_ok = facade.submit_attempt(
        episode_id="ep_int_err",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="9",
        idempotency_key="idemp_s2_fix",
        expected_previous_sequence=r2.stream_version,
    )
    assert r2_ok.judgment == AttemptJudgment.VALID_EXPECTED

    # S3 error: wrong definite value 12
    r3 = facade.submit_attempt(
        episode_id="ep_int_err",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="12",
        idempotency_key="idemp_err_s3",
        expected_previous_sequence=r2_ok.stream_version,
    )
    assert r3.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-INTEGRAL-VALUE-WRONG" in r3.observations


# ==============================================================================
# 7. CT-INT1 GENERIC START_EPISODE DISPATCH
# ==============================================================================

def test_ctint1_generic_start_episode_dispatch(facade: FocusServiceFacade):
    """Verify start_episode(topic_id='CT-INT1') correctly creates CT-INT1 episode."""
    res = facade.start_episode(
        episode_id="ep_int_generic",
        topic_id="CT-INT1",
        a=2,
        b=0,
        c=3,
        divisor_root=0,
        idempotency_key="idemp_int_generic",
    )
    assert res.state.composite_task_id == "CT-INT1"
    assert res.state.workspace_kc == KCId.IN1
    assert res.state.current_stage == StageId.S1_FIND_ANTIDERIVATIVE
    assert res.state.task_context.expected_definite_value == 9.0


# ==============================================================================
# 8. REST API INTEGRATION VIA FASTAPI CLIENT
# ==============================================================================

def test_ctint1_rest_api(client: TestClient):
    """End-to-end HTTP API roundtrip for CT-INT1."""
    # 1. Start episode
    start_resp = client.post(
        "/focus/v1/episodes",
        json={
            "episode_id": "api_int_01",
            "topic_id": "CT-INT1",
            "a": 2,
            "b": 0,
            "c": 3,
            "divisor_root": 0,
        },
        headers={"Idempotency-Key": "api_idemp_start"},
    )
    assert start_resp.status_code == 201, start_resp.text
    data = start_resp.json()
    assert data["state"]["composite_task_id"] == "CT-INT1"
    assert data["state"]["current_stage"] == "S1_FIND_ANTIDERIVATIVE"
    stream_version = data["stream_version"]

    # 2. Submit S1 attempt: 'x^2'
    s1_resp = client.post(
        "/focus/v1/episodes/api_int_01/attempts",
        json={
            "input_kind": "EXPRESSION_REWRITE",
            "input": "x^2",
        },
        headers={
            "Idempotency-Key": "api_idemp_s1",
            "X-Focus-Expected-Sequence": str(stream_version),
        },
    )
    assert s1_resp.status_code == 200, s1_resp.text
    s1_data = s1_resp.json()
    assert s1_data["judgment"] == "VALID_EXPECTED"
    assert s1_data["state"]["current_stage"] == "S2_APPLY_LIMITS"
    stream_version = s1_data["stream_version"]

    # 3. Submit S2 attempt: '9'
    s2_resp = client.post(
        "/focus/v1/episodes/api_int_01/attempts",
        json={
            "input_kind": "COORDINATE_ASSIGNMENT",
            "input": "9",
        },
        headers={
            "Idempotency-Key": "api_idemp_s2",
            "X-Focus-Expected-Sequence": str(stream_version),
        },
    )
    assert s2_resp.status_code == 200, s2_resp.text
    s2_data = s2_resp.json()
    assert s2_data["judgment"] == "VALID_EXPECTED"
    assert s2_data["state"]["current_stage"] == "S3_COMPUTE_DEFINITE_INTEGRAL"
    stream_version = s2_data["stream_version"]

    # 4. Submit S3 attempt: '9' -> COMPLETE
    s3_resp = client.post(
        "/focus/v1/episodes/api_int_01/attempts",
        json={
            "input_kind": "COORDINATE_ASSIGNMENT",
            "input": "9",
        },
        headers={
            "Idempotency-Key": "api_idemp_s3",
            "X-Focus-Expected-Sequence": str(stream_version),
        },
    )
    assert s3_resp.status_code == 200, s3_resp.text
    s3_data = s3_resp.json()
    assert s3_data["judgment"] == "VALID_EXPECTED"
    assert s3_data["state"]["phase"] == "COMPLETED"
    assert s3_data["decision"]["action"] == "COMPLETE_TASK"
