"""
Psychometrics Test Suite.
Tests:
1. Individualized BKT (iBKT): Posterior updates, transitions, parameter personalization.
2. Continuous-Time BKT (CT-BKT): Memory decay over time with FSRS stability.
3. Ratcliff Drift-Diffusion Model (DDM / EZ-Diffusion): Drift rate, boundary separation, cognitive profiling, edge cases.
4. API Integration: Psychometrics returned in step verification responses.
"""

import math
import pytest
from app.psychometrics.bkt import IndividualizedBKT, ContinuousTimeBKT, BKTParameters
from app.psychometrics.ddm import EZDiffusionSolver, DDMParameters
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


# ==========================================
# 1. BKT TESTS
# ==========================================

def test_bkt_correct_step_increases_mastery():
    """Verify that consecutive correct steps monotonically increase mastery P(L)."""
    p_l = 0.20
    params = BKTParameters(p_l0=0.20, p_t=0.15, p_s=0.10, p_g=0.02)

    mastery_history = [p_l]
    for _ in range(3):
        posterior, p_l = IndividualizedBKT.update_mastery(p_l, is_correct=True, params=params)
        mastery_history.append(p_l)

    # Monotonically strictly increasing
    for i in range(len(mastery_history) - 1):
        assert mastery_history[i + 1] > mastery_history[i]

    # After 3 correct steps, mastery should be > 0.85
    assert p_l > 0.85


def test_bkt_incorrect_step_decreases_mastery():
    """Verify that consecutive incorrect steps decrease mastery."""
    p_l = 0.80
    params = BKTParameters(p_l0=0.20, p_t=0.15, p_s=0.10, p_g=0.02)

    posterior, p_l_next = IndividualizedBKT.update_mastery(p_l, is_correct=False, params=params)

    # Posterior must drop significantly after an error
    assert posterior < 0.80
    assert posterior < p_l


def test_bkt_individualized_parameters():
    """Verify that student cognitive covariates alter BKT parameters appropriately."""
    # Student with high procedural mastery and high cognitive agility
    high_student_params = IndividualizedBKT.personalize_parameters(
        eta_i=1.5,        # High learning agility
        theta_proc=2.0,   # High procedural mastery
        kappa_i=1.2,      # High attention
        num_choices=None, # Open-ended math
    )

    # Student with low agility and low procedural mastery
    low_student_params = IndividualizedBKT.personalize_parameters(
        eta_i=-1.5,
        theta_proc=-1.0,
        kappa_i=0.5,
        num_choices=None,
    )

    # High agility student learns faster (higher P(T))
    assert high_student_params.p_t > low_student_params.p_t

    # High procedural student makes fewer careless slips (lower P(S))
    assert high_student_params.p_s < low_student_params.p_s

    # In all cases, slip must not exceed theoretical ceiling of 0.20 and guess <= 0.30, and p_t in [0.05, 0.40]
    assert high_student_params.p_s <= 0.20
    assert low_student_params.p_s <= 0.20
    assert high_student_params.p_g <= 0.30
    assert low_student_params.p_g <= 0.30
    assert 0.05 <= high_student_params.p_t <= 0.40
    assert 0.05 <= low_student_params.p_t <= 0.40


# ==========================================
# 2. CONTINUOUS-TIME BKT TESTS
# ==========================================

def test_ct_bkt_forgetting_over_time():
    """Verify memory decay over days based on FSRS stability."""
    initial_mastery = 0.90
    stability = 3.0  # 3 days stability

    # No time elapsed -> no decay
    assert ContinuousTimeBKT.decay_mastery(initial_mastery, elapsed_days=0.0, stability_days=stability) == initial_mastery

    # 3 days elapsed (1 stability interval) -> R should be around R_target (0.90) of original
    # P(L) = 0.90 * exp(-lambda_f * 3) = 0.90 * 0.90 = 0.81
    decayed_3d = ContinuousTimeBKT.decay_mastery(initial_mastery, elapsed_days=3.0, stability_days=stability)
    assert 0.80 <= decayed_3d <= 0.82

    # 14 days elapsed -> substantial decay
    decayed_14d = ContinuousTimeBKT.decay_mastery(initial_mastery, elapsed_days=14.0, stability_days=stability)
    assert decayed_14d < 0.60
    assert decayed_14d < decayed_3d


# ==========================================
# 3. RATCLIFF DDM (EZ-DIFFUSION) TESTS
# ==========================================

def test_ez_diffusion_fluent_master_profile():
    """Fluent master: High accuracy (95%), fast response time (1.8s), low variance."""
    ddm = EZDiffusionSolver.solve(mrt=1.8, vrt=0.03, pc=0.95, n_trials=20)

    assert ddm.drift_rate > 0.10  # Strong positive drift
    assert ddm.boundary_separation > 0.0
    assert ddm.non_decision_time > 0.0
    assert ddm.cognitive_state == "fluent_mastery"


def test_ez_diffusion_rapid_guessing_profile():
    """Rapid guesser: Very fast (1.2s), low caution boundary, low accuracy (50%)."""
    ddm = EZDiffusionSolver.solve(mrt=1.2, vrt=0.02, pc=0.52, n_trials=20)

    assert ddm.boundary_separation <= 0.09  # Very low boundary
    assert ddm.cognitive_state == "rapid_guessing"


def test_ez_diffusion_cautious_effort_profile():
    """Cautious student: High RT (6.5s), high boundary separation (a), moderate accuracy (75%)."""
    ddm = EZDiffusionSolver.solve(mrt=6.5, vrt=0.08, pc=0.75, n_trials=20)

    assert ddm.boundary_separation > 0.12  # Cautious boundary
    assert ddm.drift_rate > 0.0
    assert ddm.cognitive_state in ["cautious_effort", "balanced_learning"]


def test_ez_diffusion_laplace_edge_cases():
    """Verify that extreme accuracy rates (100% or 0%) do not produce math domain errors."""
    # 100% correct with Laplace smoothing
    ddm_100 = EZDiffusionSolver.solve(mrt=2.0, vrt=0.04, pc=1.0, n_trials=10)
    assert not math.isnan(ddm_100.drift_rate)
    assert not math.isnan(ddm_100.boundary_separation)
    assert ddm_100.drift_rate > 0

    # 0% correct with Laplace smoothing
    ddm_0 = EZDiffusionSolver.solve(mrt=2.0, vrt=0.04, pc=0.0, n_trials=10)
    assert not math.isnan(ddm_0.drift_rate)
    assert ddm_0.drift_rate < 0  # Negative drift indicates misconception


def test_ez_diffusion_solve_from_trials():
    """Verify trial list aggregation and outlier truncation (>15s)."""
    # 5 trials, one of which is an outlier of 25 seconds (phone distraction)
    rts = [1.8, 2.2, 1.9, 25.0, 2.1]
    corrects = [True, True, True, False, True]

    ddm = EZDiffusionSolver.solve_from_trials(reaction_times=rts, correctness=corrects, filter_outliers=True)

    assert ddm.drift_rate > 0
    # Mean RT must have excluded the 25.0s outlier (~2.0s average)
    assert ddm.non_decision_time < 3.0


def test_ez_diffusion_degenerate_data_raises_error():
    """Verify physiological limit guards (ERR_DDM_DEGENERATE_DATA)."""
    # Unphysiologically fast (<100ms)
    with pytest.raises(ValueError, match="ERR_DDM_DEGENERATE_DATA"):
        EZDiffusionSolver.solve(mrt=0.05, vrt=0.02, pc=0.8)

    # Zero or negative variance
    with pytest.raises(ValueError, match="ERR_DDM_DEGENERATE_DATA"):
        EZDiffusionSolver.solve(mrt=1.5, vrt=0.0, pc=0.8)


# ==========================================
# 4. API INTEGRATION TEST
# ==========================================

def test_api_verify_step_returns_psychometrics():
    """Verify that /api/v1/session/step/verify returns populated psychometrics block."""
    payload = {
        "session_id": "test-psych-session-001",
        "node_id": "N15",
        "step_number": 1,
        "user_expression": "x^2 - 5x + 6 = 0",
        "target_equation": "(x - 2)(x - 3) = 0",
        "elapsed_ms": 2200,
        "current_p_l": 0.35,
    }

    response = client.post("/api/v1/session/step/verify", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_valid"] is True
    assert "psychometrics" in data and data["psychometrics"] is not None

    psy = data["psychometrics"]
    assert psy["bkt_posterior_p_l"] > 0.35
    assert psy["bkt_next_p_l"] > psy["bkt_posterior_p_l"]
    assert psy["ddm_drift_rate"] is not None
    assert psy["ddm_boundary_separation"] is not None
    assert psy["ddm_cognitive_state"] is not None


def test_bkt_nan_and_extreme_inputs():
    """Verify that BKT gracefully handles NaN and extreme values without propagating NaNs."""
    # NaN p_l input
    post, next_pl = IndividualizedBKT.update_mastery(float("nan"), is_correct=True)
    assert not math.isnan(post)
    assert not math.isnan(next_pl)
    assert 0.0 < post < 1.0
    assert 0.0 < next_pl < 1.0

    # predict_observation with NaN
    pred = IndividualizedBKT.predict_observation(float("nan"))
    assert not math.isnan(pred)
    assert 0.0 < pred < 1.0


def test_ct_bkt_nan_and_boundary_inputs():
    """Verify that Continuous-Time BKT handles NaN and non-positive stability/elapsed days safely."""
    # NaN stability
    rate = ContinuousTimeBKT.calculate_forgetting_rate(float("nan"))
    assert not math.isnan(rate)
    assert rate > 0.0

    # NaN initial p_l and NaN elapsed_days
    decayed = ContinuousTimeBKT.decay_mastery(float("nan"), float("nan"))
    assert not math.isnan(decayed)
    assert 0.0 < decayed < 1.0

    # Negative elapsed days
    assert ContinuousTimeBKT.decay_mastery(0.75, -5.0) == 0.75

