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
from app.focus_domain.registry import PROBE_TEMPLATES, INTERVENTION_TEMPLATES, ACTIVE_DIAGNOSTIC_ROUTES, REPAIR_EDGES
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
# 1. CT-LIM1 0/0 INDETERMINATE LIMIT TESTS
# ==============================================================================

def test_ctlim1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: lim_{x->2} (x^2-4)/(x-2) -> 0/0 -> x + 2 -> 4.0 -> COMPLETED."""
    res = facade.start_ctlim1_episode(
        episode_id="ep_lim_01",
        a=2,
        idempotency_key="idemp_lim_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-LIM1"
    assert state.workspace_kc == KCId.LM1
    assert state.current_stage == StageId.S1_EVALUATE_LIMIT_FORM
    assert state.task_context.expected_indeterminate_form == "0/0"
    assert state.task_context.expected_simplified_expr == "x + 2"
    assert state.task_context.expected_limit_val == 4.0

    # S1: Identify indeterminate form 0/0
    r1 = facade.submit_attempt(
        episode_id="ep_lim_01",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="0/0",
        idempotency_key="idemp_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_SIMPLIFY_EXPRESSION
    assert r1.state.workspace_kc == KCId.LM1

    # S2: Simplify expression x + 2
    r2 = facade.submit_attempt(
        episode_id="ep_lim_01",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x + 2",
        idempotency_key="idemp_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_COMPUTE_FINAL_LIMIT
    assert r2.state.workspace_kc == KCId.LM1

    # S3: Compute final limit value 4
    r3 = facade.submit_attempt(
        episode_id="ep_lim_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="4",
        idempotency_key="idemp_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctlim1_input_variations(facade: FocusServiceFacade):
    """Input variations like 'belirsiz', 'x+2', 'L = 4'."""
    res = facade.start_ctlim1_episode(
        episode_id="ep_lim_var",
        a=2,
        idempotency_key="idemp_lim_var_start",
    )
    # S1 variation: 'belirsiz'
    r1 = facade.submit_attempt(
        episode_id="ep_lim_var",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="belirsiz",
        idempotency_key="idemp_var_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED

    # S2 variation: 'x+2' without spaces
    r2 = facade.submit_attempt(
        episode_id="ep_lim_var",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x+2",
        idempotency_key="idemp_var_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED

    # S3 variation: 'L = 4.0'
    r3 = facade.submit_attempt(
        episode_id="ep_lim_var",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="L = 4.0",
        idempotency_key="idemp_var_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctlim1_invalid_attempts_and_observations(facade: FocusServiceFacade):
    """Invalid responses generate expected error observations."""
    res = facade.start_ctlim1_episode(
        episode_id="ep_lim_err",
        a=2,
        idempotency_key="idemp_lim_err_start",
    )

    # S1 error: claiming 0 instead of 0/0
    r1 = facade.submit_attempt(
        episode_id="ep_lim_err",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="0",
        idempotency_key="idemp_err_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-LIMIT-FORM-WRONG" in r1.observations

    # Correct S1 to advance
    r1_ok = facade.submit_attempt(
        episode_id="ep_lim_err",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="0/0",
        idempotency_key="idemp_s1_fix",
        expected_previous_sequence=r1.stream_version,
    )
    assert r1_ok.judgment == AttemptJudgment.VALID_EXPECTED

    # S2 error: wrong simplified expression 'x - 2'
    r2 = facade.submit_attempt(
        episode_id="ep_lim_err",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x - 2",
        idempotency_key="idemp_err_s2",
        expected_previous_sequence=r1_ok.stream_version,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-SIMPLIFICATION-WRONG" in r2.observations

    # Correct S2 to advance
    r2_ok = facade.submit_attempt(
        episode_id="ep_lim_err",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="x + 2",
        idempotency_key="idemp_s2_fix",
        expected_previous_sequence=r2.stream_version,
    )
    assert r2_ok.judgment == AttemptJudgment.VALID_EXPECTED

    # S3 error: wrong limit value 6
    r3 = facade.submit_attempt(
        episode_id="ep_lim_err",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="6",
        idempotency_key="idemp_err_s3",
        expected_previous_sequence=r2_ok.stream_version,
    )
    assert r3.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-LIMIT-VALUE-WRONG" in r3.observations


# ==============================================================================
# 2. CT-DERIV1 POLYNOMIAL DERIVATIVE & TANGENT LINE TESTS
# ==============================================================================

def test_ctderiv1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: f(x) = x^2 - 3x + 2 at x0=2 -> f'(x)=2x-3 -> m=1 -> y = x - 2 -> COMPLETED."""
    res = facade.start_ctderiv1_episode(
        episode_id="ep_deriv_01",
        a=1,
        b=-3,
        c=2,
        x0=2,
        idempotency_key="idemp_deriv_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-DERIV1"
    assert state.workspace_kc == KCId.DV1
    assert state.current_stage == StageId.S1_COMPUTE_DERIVATIVE
    assert state.task_context.expected_derivative_str == "2x - 3"
    assert state.task_context.expected_slope == 1.0
    assert state.task_context.expected_y0 == 0.0
    assert state.task_context.expected_tangent_line == "y = 1x - 2"

    # S1: Compute derivative 2x - 3
    r1 = facade.submit_attempt(
        episode_id="ep_deriv_01",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="2x - 3",
        idempotency_key="idemp_deriv_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_EVALUATE_SLOPE
    assert r1.state.workspace_kc == KCId.DV1

    # S2: Evaluate slope m = 1
    r2 = facade.submit_attempt(
        episode_id="ep_deriv_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="m = 1",
        idempotency_key="idemp_deriv_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_DETERMINE_TANGENT_LINE
    assert r2.state.workspace_kc == KCId.DV1

    # S3: Determine tangent line equation y = x - 2
    r3 = facade.submit_attempt(
        episode_id="ep_deriv_01",
        input_kind=FocusAttemptInputKind.EQUATION_REWRITE,
        raw_input="y = x - 2",
        idempotency_key="idemp_deriv_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctderiv1_input_variations(facade: FocusServiceFacade):
    """Input variations like 'f'(x) = 2*x - 3', raw numeric slope '1', etc."""
    res = facade.start_ctderiv1_episode(
        episode_id="ep_deriv_var",
        a=1,
        b=-3,
        c=2,
        x0=2,
        idempotency_key="idemp_deriv_var_start",
    )
    # S1 variation: 'f\'(x) = 2*x - 3'
    r1 = facade.submit_attempt(
        episode_id="ep_deriv_var",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="f'(x) = 2*x - 3",
        idempotency_key="idemp_deriv_var_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED

    # S2 variation: raw number 1.0
    r2 = facade.submit_attempt(
        episode_id="ep_deriv_var",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input=1.0,
        idempotency_key="idemp_deriv_var_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED

    # S3 variation: 'y - 0 = 1*(x - 2)' -> equivalent tangent line
    r3 = facade.submit_attempt(
        episode_id="ep_deriv_var",
        input_kind=FocusAttemptInputKind.EQUATION_REWRITE,
        raw_input="y = 1*x - 2",
        idempotency_key="idemp_deriv_var_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctderiv1_invalid_attempts_and_observations(facade: FocusServiceFacade):
    """Errors generate appropriate derivative error observations."""
    res = facade.start_ctderiv1_episode(
        episode_id="ep_deriv_err",
        a=1,
        b=-3,
        c=2,
        x0=2,
        idempotency_key="idemp_deriv_err_start",
    )

    # S1 error: power rule forgot constant derivative: '2x'
    r1 = facade.submit_attempt(
        episode_id="ep_deriv_err",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="2x",
        idempotency_key="idemp_err_d1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-DERIVATIVE-POWER-WRONG" in r1.observations

    # Correct S1
    r1_ok = facade.submit_attempt(
        episode_id="ep_deriv_err",
        input_kind=FocusAttemptInputKind.EXPRESSION_REWRITE,
        raw_input="2x - 3",
        idempotency_key="idemp_fix_d1",
        expected_previous_sequence=r1.stream_version,
    )
    assert r1_ok.judgment == AttemptJudgment.VALID_EXPECTED

    # S2 error: wrong slope evaluation 5
    r2 = facade.submit_attempt(
        episode_id="ep_deriv_err",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="5",
        idempotency_key="idemp_err_d2",
        expected_previous_sequence=r1_ok.stream_version,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-SLOPE-WRONG" in r2.observations

    # Correct S2
    r2_ok = facade.submit_attempt(
        episode_id="ep_deriv_err",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="1",
        idempotency_key="idemp_fix_d2",
        expected_previous_sequence=r2.stream_version,
    )
    assert r2_ok.judgment == AttemptJudgment.VALID_EXPECTED

    # S3 error: wrong tangent line equation
    r3 = facade.submit_attempt(
        episode_id="ep_deriv_err",
        input_kind=FocusAttemptInputKind.EQUATION_REWRITE,
        raw_input="y = 2x + 1",
        idempotency_key="idemp_err_d3",
        expected_previous_sequence=r2_ok.stream_version,
    )
    assert r3.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-CALC-TANGENT-WRONG" in r3.observations


# ==============================================================================
# 3. REGISTRY, PROBE AND INTERVENTION SPECIFICATION TESTS
# ==============================================================================

def test_calculus_probes_and_interventions():
    """Verify registry invariants and template accessibility for LM1 and DV1."""
    assert len(PROBE_TEMPLATES) == 11, "Frozen primary count must stay 11"
    assert len(INTERVENTION_TEMPLATES) == 12, "Frozen primary count must stay 12"

    assert "PR-LM1-01" in PROBE_TEMPLATES
    probe_lm = PROBE_TEMPLATES["PR-LM1-01"]
    assert probe_lm.target_kc == KCId.LM1
    codes_lm = {r.code: r.evidence_kind for r in probe_lm.response_classes}
    assert codes_lm["ZERO_OVER_ZERO"] == ProbeEvidenceKind.POSITIVE
    assert codes_lm["UNDEFINED"] == ProbeEvidenceKind.BARRIER_SUPPORT

    assert "PR-DV1-01" in PROBE_TEMPLATES
    probe_dv = PROBE_TEMPLATES["PR-DV1-01"]
    assert probe_dv.target_kc == KCId.DV1
    codes_dv = {r.code: r.evidence_kind for r in probe_dv.response_classes}
    assert codes_dv["THREE_X_SQUARED"] == ProbeEvidenceKind.POSITIVE
    assert codes_dv["X_SQUARED"] == ProbeEvidenceKind.BARRIER_SUPPORT

    assert "IT-LM1-01" in INTERVENTION_TEMPLATES
    assert INTERVENTION_TEMPLATES["IT-LM1-01"].target_kc == KCId.LM1

    assert "IT-DV1-01" in INTERVENTION_TEMPLATES
    assert INTERVENTION_TEMPLATES["IT-DV1-01"].target_kc == KCId.DV1

    assert "DR-LM1-01" in ACTIVE_DIAGNOSTIC_ROUTES
    assert "DR-DV1-01" in ACTIVE_DIAGNOSTIC_ROUTES

    assert "RE-LM1-N2" in REPAIR_EDGES
    assert "RE-DV1-N2" in REPAIR_EDGES


# ==============================================================================
# 4. ROOT PREREQUISITE DAG MAPPING (BUG-CALC-01..10)
# ==============================================================================

def test_root_dag_calc_misconception_mappings():
    """Verify BUG-CALC-01..10 map to appropriate root prerequisite nodes in Level -3..-1."""
    dag = RootPrerequisiteDAG()
    expected = {
        "BUG-CALC-01": "N_ROOT_05",  # 0/0 belirsizliğini tanımsız sanma -> Kesir Bir Bölmedir
        "BUG-CALC-02": "N_ROOT_16",  # Limiti doğrudan f(a) sanma -> Fonksiyon Fabrikası
        "BUG-CALC-03": "N_ROOT_04",  # Sadeleştirme sonrası işaret hatası -> İşaret Kuralları
        "BUG-CALC-04": "N_ROOT_11",  # Kuvvet kuralında üs azaltmayı unutma -> Üs Bir Çarpma Sayacıdır
        "BUG-CALC-05": "N_ROOT_14",  # Sabitin türevini kendisi sanma -> Değişken vs Sabit Terim
        "BUG-CALC-06": "N_ROOT_10",  # Zincir kuralında iç türevi unutma -> Hediye Paketi Dağılma
        "BUG-CALC-07": "N_ROOT_04",  # Bölüm türevinde payda eksi yerine artı -> İşaret Kuralları
        "BUG-CALC-08": "N_ROOT_15",  # Teğet eğimini denklem sanma -> Denklem Formu
        "BUG-CALC-09": "N_ROOT_01",  # Teğet denkleminde koordinat tersliği -> Sayı Doğrusu ve Yön
        "BUG-CALC-10": "N_ROOT_16",  # f'(x)=0 her noktayı mutlak ekstremum sanma -> Fonksiyon Fabrikası
    }
    for bug_id, expected_root in expected.items():
        assert dag.map_bug_to_root_node(bug_id) == expected_root, f"Failed for {bug_id}"


# ==============================================================================
# 5. CAS SYMBOLIC ENGINE CALCULUS VALIDATION
# ==============================================================================

def test_cas_calculus_engine_features():
    """Verify compute_limit, compute_derivative, verify_derivative, compute_tangent_line."""
    cas = SymbolicEquivalenceEngine()

    # Limit of (x^2 - 4)/(x - 2) as x -> 2
    lim_val, is_finite = cas.compute_limit("(x**2 - 4)/(x - 2)", var="x", target_val=2)
    assert is_finite is True
    assert float(lim_val) == 4.0

    # Derivative of x^2 - 3x + 2
    deriv = cas.compute_derivative("x**2 - 3*x + 2", var="x", order=1)
    assert str(deriv).replace(" ", "") in ("2*x-3", "-3+2*x")

    # Verify derivative
    assert cas.verify_derivative("x**2 - 3*x + 2", "2*x - 3", var="x") is True
    assert cas.verify_derivative("x**2 - 3*x + 2", "2*x", var="x") is False

    # Tangent line at x0 = 2 for f(x) = x^2 - 3x + 2
    tan_expr, slope, y0 = cas.compute_tangent_line("x**2 - 3*x + 2", x0=2.0)
    assert slope == 1.0
    assert y0 == 0.0
    assert str(tan_expr).replace(" ", "") in ("x-2.0", "x-2", "1.0*x-2.0")

    # Continuity check
    is_cont, lim, fval = cas.check_continuity("x**2 + 1", var="x", pt=1.0)
    assert is_cont is True
    assert lim == 2.0
    assert fval == 2.0


# ==============================================================================
# 6. HTTP API ENDPOINTS FOR CALCULUS TOPICS
# ==============================================================================

def test_http_api_ctlim1_workflow(client: TestClient):
    """Uçtan uca CT-LIM1 REST API akışı."""
    # Start episode
    resp = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http_lim_start"},
        json={"episode_id": "http_ep_lim_1", "topic_id": "CT-LIM1", "a": 2},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["state"]["composite_task_id"] == "CT-LIM1"
    assert data["state"]["current_stage"] == "S1_EVALUATE_LIMIT_FORM"
    seq = data["stream_version"]

    # S1
    resp_s1 = client.post(
        "/focus/v1/episodes/http_ep_lim_1/attempts",
        headers={"Idempotency-Key": "http_lim_s1", "X-Focus-Expected-Sequence": str(seq)},
        json={"input_kind": "CLASSIFICATION", "input": "0/0"},
    )
    assert resp_s1.status_code == 200
    assert resp_s1.json()["judgment"] == "VALID_EXPECTED"
    assert resp_s1.json()["state"]["current_stage"] == "S2_SIMPLIFY_EXPRESSION"
    seq = resp_s1.json()["stream_version"]

    # S2
    resp_s2 = client.post(
        "/focus/v1/episodes/http_ep_lim_1/attempts",
        headers={"Idempotency-Key": "http_lim_s2", "X-Focus-Expected-Sequence": str(seq)},
        json={"input_kind": "EXPRESSION_REWRITE", "input": "x + 2"},
    )
    assert resp_s2.status_code == 200
    assert resp_s2.json()["judgment"] == "VALID_EXPECTED"
    assert resp_s2.json()["state"]["current_stage"] == "S3_COMPUTE_FINAL_LIMIT"
    seq = resp_s2.json()["stream_version"]

    # S3
    resp_s3 = client.post(
        "/focus/v1/episodes/http_ep_lim_1/attempts",
        headers={"Idempotency-Key": "http_lim_s3", "X-Focus-Expected-Sequence": str(seq)},
        json={"input_kind": "COORDINATE_ASSIGNMENT", "input": "4"},
    )
    assert resp_s3.status_code == 200
    assert resp_s3.json()["judgment"] == "VALID_EXPECTED"
    assert resp_s3.json()["state"]["phase"] == "COMPLETED"


def test_http_api_ctderiv1_workflow(client: TestClient):
    """Uçtan uca CT-DERIV1 REST API akışı."""
    # Start episode
    resp = client.post(
        "/focus/v1/episodes",
        headers={"Idempotency-Key": "http_deriv_start"},
        json={
            "episode_id": "http_ep_deriv_1",
            "topic_id": "CT-DERIV1",
            "a": 1,
            "b": -3,
            "c": 2,
            "divisor_root": 2,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["state"]["composite_task_id"] == "CT-DERIV1"
    assert data["state"]["current_stage"] == "S1_COMPUTE_DERIVATIVE"
    seq = data["stream_version"]

    # S1
    resp_s1 = client.post(
        "/focus/v1/episodes/http_ep_deriv_1/attempts",
        headers={"Idempotency-Key": "http_deriv_s1", "X-Focus-Expected-Sequence": str(seq)},
        json={"input_kind": "EXPRESSION_REWRITE", "input": "2x - 3"},
    )
    assert resp_s1.status_code == 200
    assert resp_s1.json()["judgment"] == "VALID_EXPECTED"
    assert resp_s1.json()["state"]["current_stage"] == "S2_EVALUATE_SLOPE"
    seq = resp_s1.json()["stream_version"]

    # S2
    resp_s2 = client.post(
        "/focus/v1/episodes/http_ep_deriv_1/attempts",
        headers={"Idempotency-Key": "http_deriv_s2", "X-Focus-Expected-Sequence": str(seq)},
        json={"input_kind": "COORDINATE_ASSIGNMENT", "input": "1"},
    )
    assert resp_s2.status_code == 200
    assert resp_s2.json()["judgment"] == "VALID_EXPECTED"
    assert resp_s2.json()["state"]["current_stage"] == "S3_DETERMINE_TANGENT_LINE"
    seq = resp_s2.json()["stream_version"]

    # S3
    resp_s3 = client.post(
        "/focus/v1/episodes/http_ep_deriv_1/attempts",
        headers={"Idempotency-Key": "http_deriv_s3", "X-Focus-Expected-Sequence": str(seq)},
        json={"input_kind": "EQUATION_REWRITE", "input": "y = x - 2"},
    )
    assert resp_s3.status_code == 200
    assert resp_s3.json()["judgment"] == "VALID_EXPECTED"
    assert resp_s3.json()["state"]["phase"] == "COMPLETED"
