import pytest
import numpy as np
from app.adaptive.calibration import EmpiricalMMLECalibrator, FSRSCalibrator, DDMCalibrator
from app.adaptive.cat_engine import CATEngine
from app.retention.fsrs import FSRSEngine
from app.psychometrics.ddm import EZDiffusionSolver


def test_mmle_em_calibration():
    # 50 examinees, 6 items
    np.random.seed(42)
    n_examinees = 50
    item_ids = [f"CAT-ITEM-{i:02d}" for i in range(1, 7)]
    true_thetas = np.random.normal(0.0, 1.0, n_examinees)

    calibrator = EmpiricalMMLECalibrator(num_quadrature_points=15)

    # Generate synthetic response matrix
    resp_matrix = np.zeros((n_examinees, len(item_ids)))
    for j in range(n_examinees):
        for i in range(len(item_ids)):
            p = calibrator._prob_correct(true_thetas[j], a=2.0, b=float(i - 2.5) * 0.5)
            resp_matrix[j, i] = 1.0 if np.random.random() < p else 0.0

    calibrated_params = calibrator.calibrate_items(
        response_matrix=resp_matrix,
        item_ids=item_ids,
        max_iter=10,
    )

    assert len(calibrated_params) == 6
    for it_id, (a_est, b_est) in calibrated_params.items():
        assert 0.4 <= a_est <= 4.0
        assert -3.5 <= b_est <= 3.5

    # Test applying to CATEngine
    cat = CATEngine()
    cat.update_item_pool(calibrated_params)
    for it_id, (a_est, b_est) in calibrated_params.items():
        assert cat.item_pool[it_id].discrimination_a == a_est
        assert cat.item_pool[it_id].difficulty_b == b_est


def test_fsrs_calibration():
    # Synthetic review logs
    np.random.seed(42)
    review_logs = []
    for i in range(30):
        t = float(np.random.choice([1.0, 3.0, 7.0, 14.0]))
        s = float(np.random.uniform(5.0, 20.0))
        rem = np.random.random() < 0.85
        review_logs.append({
            "elapsed_days": t,
            "current_stability": s,
            "rating": 3 if rem else 1,
            "was_remembered": rem,
        })

    optimized_weights = FSRSCalibrator.optimize_weights(review_logs, max_iter=25)
    assert len(optimized_weights) == 17
    # Ensure FSRSEngine accepts the calibrated weights
    engine = FSRSEngine(weights=optimized_weights)
    ret = engine.retrievability(elapsed_days=7.0, stability=15.0)
    assert 0.0 < ret <= 1.0


def test_ddm_threshold_calibration():
    telemetry_trials = []
    for i in range(25):
        telemetry_trials.append({
            "ddm_drift_v": 0.15 + (i * 0.005),
            "ddm_boundary_a": 0.09 + (i * 0.002),
        })

    thresholds = DDMCalibrator.calibrate_thresholds(telemetry_trials)
    assert "v_high" in thresholds
    assert "v_low" in thresholds
    assert "a_low" in thresholds
    assert "a_high" in thresholds
    assert thresholds["v_high"] >= thresholds["v_low"]
    assert thresholds["a_high"] >= thresholds["a_low"]

    # Test solver with custom thresholds
    res = EZDiffusionSolver.solve(
        mrt=2.0,
        vrt=0.04,
        pc=0.88,
        custom_thresholds=thresholds,
    )
    assert res.cognitive_state in ["fluent_mastery", "cautious_effort", "imposter_success", "balanced_learning"]
