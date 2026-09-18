import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import create_focus_router, install_focus_api
from app.focus_domain.application import (
    FocusAttemptInputKind,
    FocusServiceFacade,
)
from app.focus_domain.learner_profile import (
    LearnerProfileAggregator,
    PrerequisiteChainHealth,
    PREREQUISITE_GRAPH,
)
from app.focus_domain.models import KCId, KCState
from app.focus_domain.learner_state import LearnerEvidenceSnapshot
from app.focus_domain.persistence import FocusEpisodePersistenceService


def _service():
    return FocusServiceFacade(FocusEpisodePersistenceService())


def test_prerequisite_graph_structure():
    # Verify Alpha foundational invariants in prerequisite graph
    assert PREREQUISITE_GRAPH[KCId.N1] == set()
    assert PREREQUISITE_GRAPH[KCId.N2] == set()
    assert PREREQUISITE_GRAPH[KCId.N3] == set()
    assert KCId.N1 in PREREQUISITE_GRAPH[KCId.F2]
    assert KCId.N2 in PREREQUISITE_GRAPH[KCId.F2]
    assert KCId.F1 in PREREQUISITE_GRAPH[KCId.F2]


def test_profile_aggregation_precedence():
    snap1 = LearnerEvidenceSnapshot(
        kc_states={KCId.N1: KCState.CONFIRMED_GAP, KCId.F2: KCState.SUPPORTED_GAP}
    )
    snap2 = LearnerEvidenceSnapshot(
        kc_states={KCId.N1: KCState.DURABLE_EVIDENCE, KCId.F2: KCState.TEMPORARILY_RECOVERED}
    )

    profile = LearnerProfileAggregator.aggregate([snap1, snap2])

    # Durable evidence supersedes confirmed gap
    assert profile.kc_states[KCId.N1] == KCState.DURABLE_EVIDENCE
    # Temporarily recovered supersedes supported gap
    assert profile.kc_states[KCId.F2] == KCState.TEMPORARILY_RECOVERED
    assert profile.total_episodes_evaluated == 2


def test_prerequisite_chain_health_evaluation():
    # When N1 is blocked (CONFIRMED_GAP), F2 prerequisite chain must be BLOCKED
    snap = LearnerEvidenceSnapshot(
        kc_states={KCId.N1: KCState.CONFIRMED_GAP}
    )
    profile = LearnerProfileAggregator.aggregate([snap])
    f2_health = profile.kc_health[KCId.F2]

    assert f2_health.prerequisite_health == PrerequisiteChainHealth.BLOCKED
    assert KCId.N1 in f2_health.unresolved_prerequisites

    # Diagnose re-entry
    diag = LearnerProfileAggregator.diagnose_re_entry(profile, KCId.F2)
    assert diag.can_attempt_target is False
    assert diag.recommended_focus_kc == KCId.N1


def test_prerequisite_chain_health_when_all_prereqs_healthy():
    snap = LearnerEvidenceSnapshot(
        kc_states={
            KCId.N1: KCState.DURABLE_EVIDENCE,
            KCId.N2: KCState.DURABLE_EVIDENCE,
            KCId.F1: KCState.DURABLE_EVIDENCE,
        }
    )
    profile = LearnerProfileAggregator.aggregate([snap])
    f2_health = profile.kc_health[KCId.F2]

    assert f2_health.prerequisite_health == PrerequisiteChainHealth.HEALTHY
    assert len(f2_health.unresolved_prerequisites) == 0

    diag = LearnerProfileAggregator.diagnose_re_entry(profile, KCId.F2)
    assert diag.can_attempt_target is True
    assert diag.recommended_focus_kc == KCId.F2


def test_multi_episode_service_and_api():
    service = _service()

    # Episode 1: Learner exhibits N1 gap during S1
    service.start_ctqf1_episode(
        episode_id="ep-1",
        b=5,
        c=6,
        idempotency_key="ep1:start",
    )
    res = service.submit_attempt(
        episode_id="ep-1",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[-2, -3],
        idempotency_key="ep1:att1",
        expected_previous_sequence=1,
    )
    # Apply probe response -> F2 gap / repair
    service.apply_probe_response(
        episode_id="ep-1",
        probe_id=res.decision.probe_id,
        response_code="PRODUCT_ONLY",
        idempotency_key="ep1:probe",
        expected_previous_sequence=2,
    )

    # Episode 2: Second episode
    service.start_ctqf1_episode(
        episode_id="ep-2",
        b=7,
        c=12,
        idempotency_key="ep2:start",
    )

    # Fetch cross-episode profile
    profile = service.get_multi_episode_learner_profile()
    assert profile.total_episodes_evaluated == 2
    assert KCId.F2 in profile.kc_states

    # Check API endpoints
    app = FastAPI()
    install_focus_api(app, enabled=True, service=service)
    client = TestClient(app)

    # GET /profile
    r_prof = client.get("/focus/v1/profile")
    assert r_prof.status_code == 200
    p_data = r_prof.json()
    assert p_data["total_episodes_evaluated"] == 2
    assert "KC-F2" in p_data["kc_health"]

    # GET /diagnostics/re-entry/{target_kc}
    r_diag = client.get("/focus/v1/diagnostics/re-entry/KC-F2")
    assert r_diag.status_code == 200
    d_data = r_diag.json()
    assert d_data["target_kc"] == "KC-F2"
    assert "can_attempt_target" in d_data
