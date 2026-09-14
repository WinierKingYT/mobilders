"""
Bayesian Knowledge Tracing (BKT) Engine.
Implements:
1. Individualized BKT (iBKT) with logistic link functions for student covariates and item parameters.
2. Continuous-Time BKT (CT-BKT) with Kolmogorov master equation and FSRS memory stability decay.
"""

from __future__ import annotations
import math
from typing import NamedTuple, Optional
from pydantic import BaseModel, Field


def sigmoid(z: float) -> float:
    """Numerically stable sigmoid function."""
    if z >= 35.0:
        return 1.0
    if z <= -35.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-z))


class BKTParameters(BaseModel):
    """Parameters for Bayesian Knowledge Tracing."""
    p_l0: float = Field(0.20, ge=0.0, le=1.0, description="Prior probability of knowing the skill")
    p_t: float = Field(0.15, ge=0.0, le=1.0, description="Probability of transition (learning)")
    p_s: float = Field(0.10, ge=0.0, le=0.25, description="Probability of slip (mistake despite knowing)")
    p_g: float = Field(0.02, ge=0.0, le=0.50, description="Probability of guess (correct without knowing)")


class IndividualizedBKT:
    """
    Individualized Bayesian Knowledge Tracing (iBKT) Engine.
    Incorporates student covariates and item parameters to individualize
    p_l0, p_t, p_s, and p_g.
    """

    @staticmethod
    def personalize_parameters(
        beta_0: float = 0.0,
        gamma_0: float = 0.0,
        b_0: float = 0.0,
        beta_t: float = -1.5,
        eta_i: float = 0.0,
        alpha_j: float = 1.0,
        d_j: float = 0.0,
        beta_s: float = -2.2,
        theta_proc: float = 0.0,
        kappa_i: float = 1.0,
        omega_j: float = 0.0,
        beta_g: float = -4.0,
        a_j: float = 1.0,
        theta_i: float = 0.0,
        b_j: float = 0.0,
        num_choices: Optional[int] = None,
    ) -> BKTParameters:
        """
        Calculates individualized BKT parameters using logistic link functions:
        - P(L_0) = sigma(beta_0 + gamma_0 - b_0)
        - P(T)   = sigma(beta_t + eta_i * alpha_j - d_j)
        - P(S)   = min(0.25, sigma(beta_s - kappa_i * theta_proc + omega_j))
        - P(G)   = (1 / K) * sigma(beta_g - a_j * (theta_i - b_j)) [or open-ended default]
        """
        # Prior knowledge
        z_l0 = beta_0 + gamma_0 - b_0
        p_l0 = max(0.01, min(0.95, sigmoid(z_l0)))

        # Learning rate
        z_t = beta_t + (eta_i * alpha_j) - d_j
        p_t = max(0.01, min(0.60, sigmoid(z_t)))

        # Slip probability (strictly bounded <= 0.25)
        z_s = beta_s - (kappa_i * theta_proc) + omega_j
        p_s = min(0.25, max(0.01, sigmoid(z_s)))

        # Guess probability
        z_g = beta_g - (a_j * (theta_i - b_j))
        if num_choices and num_choices > 1:
            p_g = (1.0 / float(num_choices)) * sigmoid(z_g)
        else:
            # Open-ended math input: guess is very low
            p_g = 0.05 * sigmoid(z_g)
        p_g = max(0.001, min(0.25, p_g))

        return BKTParameters(p_l0=p_l0, p_t=p_t, p_s=p_s, p_g=p_g)

    @staticmethod
    def update_mastery(
        p_l: float,
        is_correct: bool,
        params: Optional[BKTParameters] = None,
    ) -> tuple[float, float]:
        """
        Performs Bayesian posterior update followed by transition update.
        Returns (posterior_p_l, next_p_l).
        """
        if params is None:
            params = BKTParameters()

        p_l = max(1e-6, min(1.0 - 1e-6, p_l))
        p_s = params.p_s
        p_g = params.p_g
        p_t = params.p_t

        if is_correct:
            # P(L | y=1) = [P(L)*(1 - P(S))] / [P(L)*(1 - P(S)) + (1 - P(L))*P(G)]
            numerator = p_l * (1.0 - p_s)
            denominator = numerator + ((1.0 - p_l) * p_g)
        else:
            # P(L | y=0) = [P(L)*P(S)] / [P(L)*P(S) + (1 - P(L))*(1 - P(G))]
            numerator = p_l * p_s
            denominator = numerator + ((1.0 - p_l) * (1.0 - p_g))

        if denominator <= 1e-12:
            posterior_p_l = p_l
        else:
            posterior_p_l = numerator / denominator

        # Transition to next step: P(L_{t+1}) = P(L_t | y) + (1 - P(L_t | y)) * P(T)
        next_p_l = posterior_p_l + ((1.0 - posterior_p_l) * p_t)

        # Numerical clamping
        posterior_p_l = max(1e-5, min(1.0 - 1e-5, posterior_p_l))
        next_p_l = max(1e-5, min(1.0 - 1e-5, next_p_l))

        return posterior_p_l, next_p_l

    @staticmethod
    def predict_observation(p_l: float, params: Optional[BKTParameters] = None) -> float:
        """
        Predicts probability of a correct response: P(Y=1) = P(L)*(1 - P(S)) + (1 - P(L))*P(G)
        """
        if params is None:
            params = BKTParameters()
        return (p_l * (1.0 - params.p_s)) + ((1.0 - p_l) * params.p_g)


class ContinuousTimeBKT:
    """
    Continuous-Time BKT (CT-BKT).
    Solves Kolmogorov forward differential equation to model forgetting over elapsed time:
    P(L(t + dt)) = P_inf + (P(L(t)) - P_inf) * exp(-(lambda_t + lambda_f) * dt)
    Where lambda_f is derived from FSRS stability: lambda_f = -ln(0.90) / S.
    """

    TARGET_RETRIEVAL_RATE = 0.90  # Standard FSRS threshold

    @classmethod
    def calculate_forgetting_rate(cls, stability_days: float) -> float:
        """
        Calculates hazard rate of forgetting from memory stability:
        lambda_f = -ln(R_target) / S
        """
        if stability_days <= 0.01:
            stability_days = 0.01
        return -math.log(cls.TARGET_RETRIEVAL_RATE) / stability_days

    @classmethod
    def decay_mastery(
        cls,
        p_l_initial: float,
        elapsed_days: float,
        stability_days: float = 1.0,
        learning_flow_rate: float = 0.0,
    ) -> float:
        """
        Decays mastery over elapsed_days.
        - If learning_flow_rate == 0.0: Pure passive forgetting P(L) = P(L_0) * exp(-lambda_f * dt).
        - If learning_flow_rate > 0.0: Active session transition with steady state P_inf.
        """
        if elapsed_days <= 0.0:
            return max(0.0, min(1.0, p_l_initial))

        lambda_f = cls.calculate_forgetting_rate(stability_days)
        lambda_t = max(0.0, learning_flow_rate)

        total_rate = lambda_t + lambda_f
        if total_rate <= 1e-12:
            return p_l_initial

        if lambda_t == 0.0:
            # Passive forgetting
            decayed = p_l_initial * math.exp(-lambda_f * elapsed_days)
        else:
            p_inf = lambda_t / total_rate
            decayed = p_inf + ((p_l_initial - p_inf) * math.exp(-total_rate * elapsed_days))

        return max(1e-5, min(1.0 - 1e-5, decayed))
