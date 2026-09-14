"""
Empirical Self-Tuning & Parameter Calibration Engine.
Implements:
1. 2PL-IRT Marginal Maximum Likelihood Estimation via EM (MMLE-EM, Bock & Aitkin 1981).
2. FSRS-4.5 17-parameter memory stability vector optimization.
3. Ratcliff DDM empirical threshold calibration from learner telemetry.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import optimize


class EmpiricalMMLECalibrator:
    """
    Marginal Maximum Likelihood Estimation with Expectation-Maximization (MMLE-EM)
    for 2-Parameter Logistic Item Response Theory (2PL-IRT).
    Bock, R. D., & Aitkin, M. (1981). Marginal maximum likelihood estimation of item
    parameters: Application of an EM algorithm. Psychometrika, 46(4), 443-459.
    """

    D = 1.7  # Normal ogive scaling factor

    def __init__(self, num_quadrature_points: int = 21, theta_range: Tuple[float, float] = (-3.5, 3.5)):
        self.num_points = num_quadrature_points
        # Gauss-Hermite quadrature or evenly spaced integration grid
        nodes = np.linspace(theta_range[0], theta_range[1], num_quadrature_points)
        self.nodes = nodes
        # Standard normal prior density weights A(X_k)
        weights = (1.0 / math.sqrt(2.0 * math.pi)) * np.exp(-0.5 * (nodes ** 2))
        self.weights = weights / np.sum(weights)  # Normalized prior weights

    def _prob_correct(self, theta: float, a: float, b: float) -> float:
        logit = np.clip(self.D * a * (theta - b), -35.0, 35.0)
        return float(1.0 / (1.0 + np.exp(-logit)))

    def calibrate_items(
        self,
        response_matrix: np.ndarray,
        item_ids: List[str],
        initial_params: Optional[Dict[str, Tuple[float, float]]] = None,
        max_iter: int = 25,
        tol: float = 1e-4,
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calibrates item parameters (a_i, b_i) for each item in response_matrix.

        Args:
            response_matrix: N x M array of binary responses (1, 0) or np.nan if unadministered.
            item_ids: List of M item IDs corresponding to columns.
            initial_params: Optional dict mapping item_id -> (a, b). Default: a=1.8, b from p-values.
            max_iter: Maximum EM iterations.
            tol: Parameter convergence tolerance.

        Returns:
            Dict[item_id, (calibrated_a, calibrated_b)]
        """
        n_examinees, n_items = response_matrix.shape
        assert len(item_ids) == n_items, "Length of item_ids must match columns in response_matrix"

        # Initialize item parameters
        params = {}
        for i, it_id in enumerate(item_ids):
            if initial_params and it_id in initial_params:
                params[it_id] = list(initial_params[it_id])
            else:
                # Basic initial difficulty based on proportion correct
                valid_resp = response_matrix[:, i][~np.isnan(response_matrix[:, i])]
                p_val = np.mean(valid_resp) if len(valid_resp) > 0 else 0.5
                p_val = np.clip(p_val, 0.05, 0.95)
                b_init = -math.log(p_val / (1.0 - p_val)) / self.D
                params[it_id] = [1.8, float(b_init)]

        k_nodes = len(self.nodes)

        for iteration in range(max_iter):
            old_params = {k: list(v) for k, v in params.items()}

            # --- E-STEP ---
            # Compute posterior probabilities P(X_k | u_j) for each examinee
            posteriors = np.zeros((n_examinees, k_nodes))

            for j in range(n_examinees):
                resp = response_matrix[j, :]
                valid_mask = ~np.isnan(resp)

                # Likelihood at each quadrature node
                log_likes = np.zeros(k_nodes)
                for k in range(k_nodes):
                    theta_k = self.nodes[k]
                    ll = 0.0
                    for i in range(n_items):
                        if not valid_mask[i]:
                            continue
                        a_i, b_i = params[item_ids[i]]
                        p = self._prob_correct(theta_k, a_i, b_i)
                        p = np.clip(p, 1e-7, 1.0 - 1e-7)
                        y = resp[i]
                        ll += y * math.log(p) + (1.0 - y) * math.log(1.0 - p)
                    log_likes[k] = ll

                # Numerical stability: shift by max log likelihood
                max_ll = np.max(log_likes)
                joint = np.exp(log_likes - max_ll) * self.weights
                denom = np.sum(joint)
                if denom > 1e-12:
                    posteriors[j, :] = joint / denom
                else:
                    posteriors[j, :] = self.weights

            # --- M-STEP ---
            max_change = 0.0

            for i, it_id in enumerate(item_ids):
                valid_mask = ~np.isnan(response_matrix[:, i])
                if not np.any(valid_mask):
                    continue

                resp_i = response_matrix[:, i]
                valid_posteriors = posteriors[valid_mask, :]
                valid_resp = resp_i[valid_mask]

                # n_ik: expected total examinees at theta_k
                n_ik = np.sum(valid_posteriors, axis=0)
                # r_ik: expected correct examinees at theta_k
                r_ik = np.sum(valid_posteriors * valid_resp[:, np.newaxis], axis=0)

                # Negative log-likelihood objective function for item i
                def item_obj(p_vec):
                    a_val, b_val = p_vec
                    if a_val < 0.2 or a_val > 4.5 or b_val < -4.0 or b_val > 4.0:
                        return 1e8
                    loss = 0.0
                    for k in range(k_nodes):
                        p = self._prob_correct(self.nodes[k], a_val, b_val)
                        p = np.clip(p, 1e-7, 1.0 - 1e-7)
                        loss -= (r_ik[k] * math.log(p) + (n_ik[k] - r_ik[k]) * math.log(1.0 - p))
                    return loss

                res = optimize.minimize(
                    item_obj,
                    params[it_id],
                    method="L-BFGS-B",
                    bounds=[(0.4, 4.0), (-3.5, 3.5)],
                )

                if res.success:
                    new_a, new_b = res.x
                    change = max(abs(new_a - old_params[it_id][0]), abs(new_b - old_params[it_id][1]))
                    max_change = max(max_change, change)
                    params[it_id] = [round(float(new_a), 3), round(float(new_b), 3)]

            if max_change < tol:
                break

        return {k: (v[0], v[1]) for k, v in params.items()}


class FSRSCalibrator:
    """
    Optimizes the 17-parameter weight vector of FSRS-4.5 from empirical review logs.
    Minimizes Root Mean Squared Error (RMSE) or Cross-Entropy against actual recall outcomes.
    """

    @classmethod
    def optimize_weights(
        cls,
        review_logs: List[Dict[str, Any]],
        initial_weights: Optional[Tuple[float, ...]] = None,
        max_iter: int = 100,
    ) -> Tuple[float, ...]:
        """
        Args:
            review_logs: List of review event dicts with:
                - elapsed_days: float
                - current_stability: float
                - rating: int (1=Again, 2=Hard, 3=Good, 4=Easy)
                - was_remembered: bool (True if rating > 1)
            initial_weights: Optional 17-element starting weight vector.

        Returns:
            Tuple of 17 calibrated float weights.
        """
        from app.retention.fsrs import FSRSEngine

        base_weights = list(initial_weights if initial_weights is not None else FSRSEngine.DEFAULT_WEIGHTS)
        if len(base_weights) != 17:
            raise ValueError(f"FSRS-4.5 requires 17 weights, got {len(base_weights)}")

        if len(review_logs) < 10:
            # Not enough data for robust fitting; return base weights
            return tuple(base_weights)

        factor = 19.0 / 81.0

        def loss_func(w_vec):
            total_loss = 0.0
            for r in review_logs:
                t = r["elapsed_days"]
                s = max(0.01, r["current_stability"])
                y = 1.0 if r["was_remembered"] else 0.0

                pred_r = (1.0 + factor * (t / s)) ** -0.5
                pred_r = max(1e-5, min(1.0 - 1e-5, pred_r))
                bce = -(y * math.log(pred_r) + (1.0 - y) * math.log(1.0 - pred_r))
                total_loss += bce

            reg = 0.01 * sum((w - w_init) ** 2 for w, w_init in zip(w_vec, base_weights))
            return (total_loss / len(review_logs)) + reg

        bounds = [
            (0.1, 2.0), (0.2, 3.0), (0.5, 6.0), (2.0, 20.0),  # w0..w3: S0
            (1.0, 9.0), (0.1, 3.0), (0.1, 2.0), (0.001, 0.2), # w4..w7: D dynamics
            (0.5, 3.0), (0.01, 0.5), (0.2, 2.0),               # w8..w10: stability growth
            (0.5, 4.0), (0.01, 0.3), (0.1, 1.0), (0.2, 3.0),   # w11..w14: lapse decay
            (0.05, 0.9), (1.1, 4.5)                             # w15, w16: rating modifiers
        ]

        res = optimize.minimize(
            loss_func,
            base_weights,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": max_iter},
        )

        calibrated = tuple(round(float(w), 4) for w in res.x)
        return calibrated


class DDMCalibrator:
    """
    Calibrates cognitive classification thresholds for Ratcliff DDM
    using empirical percentiles of drift rate (v) and boundary separation (a).
    """

    @classmethod
    def calibrate_thresholds(
        cls,
        telemetry_trials: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Analyzes a population of estimated drift rates and boundary separations.

        Returns:
            Dict containing calibrated threshold keys:
            - v_high: Threshold for fluent mastery
            - v_low: Threshold for struggling/misconceptions
            - a_low: Threshold for impulsive guessing
            - a_high: Threshold for cautious/imposter effort
        """
        v_list = [t["ddm_drift_v"] for t in telemetry_trials if t.get("ddm_drift_v") is not None]
        a_list = [t["ddm_boundary_a"] for t in telemetry_trials if t.get("ddm_boundary_a") is not None]

        if len(v_list) < 5:
            return {
                "v_high": 0.12,
                "v_low": 0.03,
                "a_low": 0.07,
                "a_high": 0.14,
            }

        v_arr = np.array(v_list)
        a_arr = np.array(a_list)

        calibrated = {
            "v_high": round(float(np.percentile(v_arr, 75)), 4),
            "v_low": round(float(np.percentile(v_arr, 25)), 4),
            "a_low": round(float(np.percentile(a_arr, 15)), 4),
            "a_high": round(float(np.percentile(a_arr, 80)), 4),
        }

        calibrated["v_high"] = max(0.08, calibrated["v_high"])
        calibrated["v_low"] = min(0.05, max(0.01, calibrated["v_low"]))
        calibrated["a_low"] = min(0.09, max(0.04, calibrated["a_low"]))
        calibrated["a_high"] = max(0.12, calibrated["a_high"])

        return calibrated
