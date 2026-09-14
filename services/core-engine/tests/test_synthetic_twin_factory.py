"""
Test Suite: Synthetic Twin Cohort Simulation Factory & Bottleneck Detector.
Verifies:
1. StudentTwinProfile parameterization for all 5 cognitive personas.
2. BottleneckDetector empirical friction point detection and pruning recommendations.
3. VectorizedCohortSimulationFactory high-throughput Monte Carlo execution (including 100,000 agents over 30 virtual days).
4. Persona behavioral divergence (ECE, reaction times, retention, mastery).
5. /api/v1/simulation/run-cohort API endpoint integration.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.simulation.student_twin import CognitivePersonaType, StudentTwinProfile
from app.simulation.bottleneck_detector import BottleneckDetector
from app.simulation.cohort_factory import VectorizedCohortSimulationFactory
from app.models.schemas import SimulationCohortRequest

client = TestClient(app)


def test_student_twin_profiles():
    profiles = StudentTwinProfile.get_defaults()
    assert len(profiles) == 5

    # Check that all 5 personas exist
    assert CognitivePersonaType.FAST_FORGETTER in profiles
    assert CognitivePersonaType.OVERCONFIDENT in profiles
    assert CognitivePersonaType.IMPOSTER in profiles
    assert CognitivePersonaType.SLIP_PRONE in profiles
    assert CognitivePersonaType.FLUENT_MASTER in profiles

    # Check characteristic persona traits
    fast_f = profiles[CognitivePersonaType.FAST_FORGETTER]
    assert fast_f.fsrs_s0 <= 2.5

    overconf = profiles[CognitivePersonaType.OVERCONFIDENT]
    assert overconf.confidence_bias >= 0.25

    imposter = profiles[CognitivePersonaType.IMPOSTER]
    assert imposter.confidence_bias <= -0.20
    assert imposter.ddm_boundary_a >= 1.8  # high caution/evidence threshold

    slip_prone = profiles[CognitivePersonaType.SLIP_PRONE]
    assert slip_prone.p_s >= 0.25

    fluent = profiles[CognitivePersonaType.FLUENT_MASTER]
    assert fluent.p_l0 >= 0.35
    assert fluent.fsrs_s0 >= 10.0


def test_bottleneck_detector_logic():
    # Scenario: Clean node vs Bottleneck node
    pass_rates = {"NODE_01": 0.85, "NODE_02": 0.45, "NODE_03": 0.70}
    median_trials = {"NODE_01": 3.2, "NODE_02": 11.0, "NODE_03": 4.5}
    overload_rates = {"NODE_01": 0.05, "NODE_02": 0.35, "NODE_03": 0.12}

    bottlenecks = BottleneckDetector.analyze_node_trajectories(
        node_pass_rates=pass_rates,
        node_median_trials=median_trials,
        node_overload_rates=overload_rates,
    )

    assert len(bottlenecks) == 1
    bn = bottlenecks[0]
    assert bn["node_id"] == "NODE_02"
    assert bn["pass_rate_pct"] == 45.0
    assert bn["median_trials_to_master"] == 11.0
    assert bn["cognitive_overload_pct"] == 35.0
    assert len(bn["reasons"]) == 3
    assert "intermediate sub-nodes" in bn["recommended_pruning_action"]


def test_vectorized_cohort_simulation_small():
    factory = VectorizedCohortSimulationFactory()
    req = SimulationCohortRequest(
        cohort_size=1000,
        virtual_days=5,
    )
    res = factory.run_simulation(req)

    assert res.cohort_size == 1000
    assert res.virtual_days == 5
    assert res.total_learning_trials == 1000 * 3 * 5
    assert len(res.persona_outcomes) == 5
    assert any(b["node_id"] == "NODE_05" for b in res.bottleneck_nodes)


def test_vectorized_cohort_simulation_100k_agents():
    factory = VectorizedCohortSimulationFactory()
    req = SimulationCohortRequest(
        cohort_size=100000,
        virtual_days=30,
    )
    res = factory.run_simulation(req)

    # Verifications for full 100,000 student scale
    assert res.cohort_size == 100000
    assert res.virtual_days == 30
    assert res.total_learning_trials == 100000 * 3 * 30  # 9,000,000 trials
    assert res.runtime_seconds < 10.0  # Ultra-fast vectorized execution
    assert len(res.persona_outcomes) == 5

    # Check persona outcomes
    persona_map = {p.persona_name: p for p in res.persona_outcomes}
    fluent = persona_map[CognitivePersonaType.FLUENT_MASTER.value]
    fast_f = persona_map[CognitivePersonaType.FAST_FORGETTER.value]
    overconf = persona_map[CognitivePersonaType.OVERCONFIDENT.value]
    imposter = persona_map[CognitivePersonaType.IMPOSTER.value]

    # Fluent master has significantly higher mastery and retention
    assert fluent.mean_mastery_pct > fast_f.mean_mastery_pct
    assert fluent.mean_retention_30d > fast_f.mean_retention_30d

    # Imposter has higher reaction time due to high decision boundary
    assert imposter.mean_rt_seconds > fluent.mean_rt_seconds

    # Overconfident has substantial calibration error (ECE)
    assert overconf.mean_ece_calibration > 0.15

    # Verify empirical bottleneck on NODE_05 was captured
    assert any(b["node_id"] == "NODE_05" for b in res.bottleneck_nodes)


def test_simulation_api_endpoint():
    payload = {
        "cohort_size": 2000,
        "virtual_days": 7,
    }
    res = client.post("/api/v1/simulation/run-cohort", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["cohort_size"] == 2000
    assert data["virtual_days"] == 7
    assert len(data["persona_outcomes"]) == 5
    assert "bottleneck_nodes" in data
