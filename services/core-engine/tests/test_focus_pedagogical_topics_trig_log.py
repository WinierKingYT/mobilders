from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import install_focus_api
from app.focus_domain.application import FocusAttemptInputKind, FocusServiceFacade
from app.focus_domain.models import AttemptJudgment, KCId, StageId, ProbeEvidenceKind
from app.focus_domain.decision_pipeline import EpisodePhase, NextActionType
from app.focus_domain.persistence import (
    FocusEpisodePersistenceService,
    InMemoryFocusEventRepository,
    InMemoryFocusSnapshotRepository,
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
# 1. CT-TRIG1 TRIGONOMETRIC EQUATIONS TESTS
# ==============================================================================

def test_cttrig1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: 2*sin(x) - 1 = 0 -> sin(x) = 0.5 -> x = 30 -> x = 150 -> COMPLETED."""
    res = facade.start_cttrig1_episode(
        episode_id="ep_trig_01",
        a=2,
        c=1,
        idempotency_key="idemp_trig_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-TRIG1"
    assert state.workspace_kc == KCId.TR1
    assert state.current_stage == StageId.S1_ISOLATE_TRIG_VALUE
    assert state.task_context.expected_ratio == 0.5
    assert state.task_context.expected_principal_deg == 30
    assert state.task_context.expected_secondary_deg == 150

    # S1: Isolate ratio sin(x) = 1/2 or 0.5
    r1 = facade.submit_attempt(
        episode_id="ep_trig_01",
        input_kind=FocusAttemptInputKind.ARITHMETIC_RESULT,
        raw_input="1/2",
        idempotency_key="idemp_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_DETERMINE_PRINCIPAL_ANGLE
    assert r1.state.workspace_kc == KCId.TR1

    # S2: Determine principal angle x = 30
    r2 = facade.submit_attempt(
        episode_id="ep_trig_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="x = 30",
        idempotency_key="idemp_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_DETERMINE_SECONDARY_ROOT
    assert r2.state.workspace_kc == KCId.TR1

    # S3: Determine secondary root x = 150
    r3 = facade.submit_attempt(
        episode_id="ep_trig_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="150°",
        idempotency_key="idemp_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_cttrig1_axis_confusion_observation(facade: FocusServiceFacade):
    """BUG-TRIG-03: sin(x) = 1/2 -> learner confuses axes and answers x = 60°."""
    res = facade.start_cttrig1_episode(
        episode_id="ep_trig_bug_axis",
        a=2,
        c=1,
        idempotency_key="idemp_start",
    )
    r1 = facade.submit_attempt(
        episode_id="ep_trig_bug_axis",
        input_kind=FocusAttemptInputKind.ARITHMETIC_RESULT,
        raw_input="0.5",
        idempotency_key="idemp_s1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED

    r2 = facade.submit_attempt(
        episode_id="ep_trig_bug_axis",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="60",
        idempotency_key="idemp_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-TRIG-AXIS-CONFUSED" in r2.observations
    assert r2.decision.action == NextActionType.REQUEST_PROBE
    assert r2.decision.probe_id == "PR-TR1-01"


def test_cttrig1_secondary_root_omitted_observation(facade: FocusServiceFacade):
    """BUG-TRIG-04: Learner forgets second quadrant symmetry and enters x = 30° again."""
    res = facade.start_cttrig1_episode(
        episode_id="ep_trig_bug_root",
        a=2,
        c=1,
        idempotency_key="idemp_start",
    )
    r1 = facade.submit_attempt(
        episode_id="ep_trig_bug_root",
        input_kind=FocusAttemptInputKind.ARITHMETIC_RESULT,
        raw_input="0.5",
        idempotency_key="idemp_s1",
        expected_previous_sequence=res.stream_version,
    )
    r2 = facade.submit_attempt(
        episode_id="ep_trig_bug_root",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="30",
        idempotency_key="idemp_s2",
        expected_previous_sequence=r1.stream_version,
    )
    r3 = facade.submit_attempt(
        episode_id="ep_trig_bug_root",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="30",
        idempotency_key="idemp_s3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-TRIG-SECONDARY-ROOT-OMITTED" in r3.observations
    assert r3.decision.action == NextActionType.REQUEST_PROBE
    assert r3.decision.probe_id == "PR-TR1-01"


def test_cttrig1_probe_application(facade: FocusServiceFacade):
    """Probe response 150_DEG successfully weakens barrier."""
    res = facade.start_cttrig1_episode(
        episode_id="ep_trig_probe",
        a=2,
        c=1,
        idempotency_key="idemp_start",
    )
    r1 = facade.submit_attempt(
        episode_id="ep_trig_probe",
        input_kind=FocusAttemptInputKind.ARITHMETIC_RESULT,
        raw_input="0.5",
        idempotency_key="idemp_s1",
        expected_previous_sequence=res.stream_version,
    )
    r2 = facade.submit_attempt(
        episode_id="ep_trig_probe",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="60",
        idempotency_key="idemp_s2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.decision.action == NextActionType.REQUEST_PROBE

    probe_res = facade.apply_probe_response(
        episode_id="ep_trig_probe",
        probe_id="PR-TR1-01",
        response_code="150_DEG",
        idempotency_key="idemp_probe_ans",
        expected_previous_sequence=r2.stream_version,
    )
    assert probe_res.state.probe_evidence["PR-TR1-01"] == ProbeEvidenceKind.POSITIVE


# ==============================================================================
# 2. CT-LOG1 LOGARITHMIC EQUATIONS TESTS
# ==============================================================================

def test_ctlog1_initialization_and_happy_path(facade: FocusServiceFacade):
    """Happy path: log_2(x - 3) = 3 -> power = 8 -> x = 11 -> gecerli -> COMPLETED."""
    res = facade.start_ctlog1_episode(
        episode_id="ep_log_01",
        base=2,
        c=3,
        k=3,
        idempotency_key="idemp_log_start",
    )
    state = res.state
    assert state.composite_task_id == "CT-LOG1"
    assert state.workspace_kc == KCId.LG1
    assert state.current_stage == StageId.S1_EXPONENTIAL_CONVERSION
    assert state.task_context.expected_power == 8
    assert state.task_context.expected_x == 11
    assert state.task_context.is_domain_valid is True

    # S1: Convert to exponential power 2^3 = 8
    r1 = facade.submit_attempt(
        episode_id="ep_log_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="power = 8",
        idempotency_key="idemp_l1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.VALID_EXPECTED
    assert r1.state.current_stage == StageId.S2_ISOLATE_VARIABLE
    assert r1.state.workspace_kc == KCId.LG1

    # S2: Solve for x = 11
    r2 = facade.submit_attempt(
        episode_id="ep_log_01",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="x = 11",
        idempotency_key="idemp_l2",
        expected_previous_sequence=r1.stream_version,
    )
    assert r2.judgment == AttemptJudgment.VALID_EXPECTED
    assert r2.state.current_stage == StageId.S3_VERIFY_DOMAIN_CONSTRAINT
    assert r2.state.workspace_kc == KCId.LG1

    # S3: Verify domain constraint (11 - 3 > 0 -> gecerli)
    r3 = facade.submit_attempt(
        episode_id="ep_log_01",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="gecerli",
        idempotency_key="idemp_l3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.VALID_EXPECTED
    assert r3.decision.action == NextActionType.COMPLETE_TASK
    assert r3.state.phase == EpisodePhase.COMPLETED


def test_ctlog1_exponent_multiplication_trap_observation(facade: FocusServiceFacade):
    """BUG-LOG-02 / BUG-LOG-05: log_2(x - 3) = 3 -> learner computes 2*3 = 6 instead of 2^3 = 8."""
    res = facade.start_ctlog1_episode(
        episode_id="ep_log_bug_exp",
        base=2,
        c=3,
        k=3,
        idempotency_key="idemp_start",
    )
    r1 = facade.submit_attempt(
        episode_id="ep_log_bug_exp",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="6",
        idempotency_key="idemp_l1",
        expected_previous_sequence=res.stream_version,
    )
    assert r1.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-LOG-EXPONENT-CALCULATION-WRONG" in r1.observations
    assert r1.decision.action == NextActionType.REQUEST_PROBE
    assert r1.decision.probe_id == "PR-LG1-01"


def test_ctlog1_domain_constraint_violation(facade: FocusServiceFacade):
    """BUG-LOG-03: Learner claims solution is invalid (gecersiz) when argument is valid."""
    res = facade.start_ctlog1_episode(
        episode_id="ep_log_bug_dom",
        base=2,
        c=3,
        k=3,
        idempotency_key="idemp_start",
    )
    r1 = facade.submit_attempt(
        episode_id="ep_log_bug_dom",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="8",
        idempotency_key="idemp_l1",
        expected_previous_sequence=res.stream_version,
    )
    r2 = facade.submit_attempt(
        episode_id="ep_log_bug_dom",
        input_kind=FocusAttemptInputKind.COORDINATE_ASSIGNMENT,
        raw_input="11",
        idempotency_key="idemp_l2",
        expected_previous_sequence=r1.stream_version,
    )
    r3 = facade.submit_attempt(
        episode_id="ep_log_bug_dom",
        input_kind=FocusAttemptInputKind.CLASSIFICATION,
        raw_input="gecersiz",
        idempotency_key="idemp_l3",
        expected_previous_sequence=r2.stream_version,
    )
    assert r3.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert "EO-LOG-DOMAIN-CONSTRAINT-VIOLATED" in r3.observations
    assert r3.decision.action == NextActionType.REQUEST_PROBE
    assert r3.decision.probe_id == "PR-LG1-01"


# ==============================================================================
# 3. ROOT PREREQUISITE NETWORK MAPPING (BUG-TRIG-01..05 & BUG-LOG-01..05)
# ==============================================================================

def test_root_dag_mapping_all_hedef5_bugs():
    """Verify that all 10 Hedef 5 misconceptions map correctly into Level -3..-1 root ontology."""
    dag = RootPrerequisiteDAG()

    expected_mappings = {
        "BUG-TRIG-01": "N_ROOT_10",  # Dağılma Özelliği
        "BUG-TRIG-02": "N_ROOT_14",  # Örtük Çarpma / Fonksiyon Sezgisi
        "BUG-TRIG-03": "N_ROOT_05",  # Kesir Bir Bölmedir
        "BUG-TRIG-04": "N_ROOT_13",  # Gizli Sayı Kutusu
        "BUG-TRIG-05": "N_ROOT_04",  # İşaret Kuralları
        "BUG-LOG-01": "N_ROOT_10",   # Dağılma Özelliği
        "BUG-LOG-02": "N_ROOT_11",   # Üs Bir Çarpma Sayacıdır
        "BUG-LOG-03": "N_ROOT_01",   # Sayı Doğrusu / Pozitiflik
        "BUG-LOG-04": "N_ROOT_06",   # Denk Kesirler
        "BUG-LOG-05": "N_ROOT_11",   # Üs Bir Çarpma Sayacıdır
    }

    for bug_id, expected_root_node in expected_mappings.items():
        mapped_node = dag.map_bug_to_root_node(bug_id)
        assert mapped_node == expected_root_node, f"{bug_id} mapped to {mapped_node}, expected {expected_root_node}"
        assert mapped_node in dag.nodes, f"Target node {mapped_node} does not exist in RootPrerequisiteDAG"


# ==============================================================================
# 4. FASTAPI CLIENT INTEGRATION TESTS
# ==============================================================================

def test_api_start_and_attempt_cttrig1(client: TestClient):
    """Test start episode and stage attempts for CT-TRIG1 via HTTP API."""
    res = client.post(
        "/focus/v1/episodes",
        json={
            "episode_id": "api_trig_01",
            "topic_id": "CT-TRIG1",
            "a": 2,
            "c": 1,
        },
        headers={"Idempotency-Key": "idemp_api_start"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["state"]["composite_task_id"] == "CT-TRIG1"
    assert data["state"]["current_stage"] == "S1_ISOLATE_TRIG_VALUE"

    # Submit S1
    att1 = client.post(
        "/focus/v1/episodes/api_trig_01/attempts",
        json={
            "input_kind": "ARITHMETIC_RESULT",
            "input": "0.5",
        },
        headers={
            "Idempotency-Key": "idemp_api_att1",
            "X-Focus-Expected-Sequence": str(data["stream_version"]),
        },
    )
    assert att1.status_code == 200
    att1_data = att1.json()
    assert att1_data["judgment"] == "VALID_EXPECTED"
    assert att1_data["state"]["current_stage"] == "S2_DETERMINE_PRINCIPAL_ANGLE"


def test_api_start_and_attempt_ctlog1(client: TestClient):
    """Test start episode and stage attempts for CT-LOG1 via HTTP API."""
    res = client.post(
        "/focus/v1/episodes",
        json={
            "episode_id": "api_log_01",
            "topic_id": "CT-LOG1",
            "a": 2,  # base
            "b": 3,  # c
            "c": 3,  # k
        },
        headers={"Idempotency-Key": "idemp_api_log_start"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["state"]["composite_task_id"] == "CT-LOG1"
    assert data["state"]["current_stage"] == "S1_EXPONENTIAL_CONVERSION"

    # Submit S1
    att1 = client.post(
        "/focus/v1/episodes/api_log_01/attempts",
        json={
            "input_kind": "COORDINATE_ASSIGNMENT",
            "input": "power = 8",
        },
        headers={
            "Idempotency-Key": "idemp_api_log_att1",
            "X-Focus-Expected-Sequence": str(data["stream_version"]),
        },
    )
    assert att1.status_code == 200
    att1_data = att1.json()
    assert att1_data["judgment"] == "VALID_EXPECTED"
    assert att1_data["state"]["current_stage"] == "S2_ISOLATE_VARIABLE"
