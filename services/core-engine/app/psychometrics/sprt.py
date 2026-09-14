"""
Wald Sequential Probability Ratio Test (SPRT) Engine.
Implements Truncated SPRT (Wald, 1947; Reckase, 1983) for statistically rigorous mastery classification:
- H0: theta <= theta_0 (p0 = 0.60, Non-master)
- H1: theta >= theta_1 (p1 = 0.88, Master)
- Alpha = 0.05 (False Mastery ceiling)
- Beta = 0.10 (False Remediation ceiling)
- Log thresholds: ln(A) = 2.8904, ln(B) = -2.2513
- Truncated boundary: N_max = 12
"""

from __future__ import annotations
import math
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class MasteryDecision(str, Enum):
    MASTERY_CONFIRMED = "MASTERY_CONFIRMED"
    NEEDS_REMEDIATION = "NEEDS_REMEDIATION"
    CONTINUE_SAMPLING = "CONTINUE_SAMPLING"
    CONDITIONAL_MASTERY = "CONDITIONAL_MASTERY"


class SPRTResult(BaseModel):
    decision: MasteryDecision
    cumulative_llr: float = Field(..., description="Lambda_n: Cumulative Log-Likelihood Ratio")
    trials_count: int
    correct_count: int
    upper_threshold_ln_a: float
    lower_threshold_ln_b: float
    is_terminal: bool


class WaldSPRT:
    """
    Wald Sequential Probability Ratio Test (SPRT) for Knowledge Component Mastery Gates.
    """

    def __init__(
        self,
        p0: float = 0.60,
        p1: float = 0.88,
        alpha: float = 0.05,
        beta: float = 0.10,
        max_trials: int = 12,
    ):
        if not (0.0 < p0 < p1 < 1.0):
            raise ValueError(f"Probabilities must satisfy 0 < p0 < p1 < 1, got p0={p0}, p1={p1}")
        if not (0.0 < alpha < 0.5 and 0.0 < beta < 0.5):
            raise ValueError(f"Error bounds must satisfy 0 < alpha, beta < 0.5, got alpha={alpha}, beta={beta}")

        self.p0 = p0
        self.p1 = p1
        self.alpha = alpha
        self.beta = beta
        self.max_trials = max_trials

        # Wald boundary thresholds
        # A = (1 - beta) / alpha
        self.a = (1.0 - beta) / alpha
        self.ln_a = math.log(self.a)

        # B = beta / (1 - alpha)
        self.b = beta / (1.0 - alpha)
        self.ln_b = math.log(self.b)

        # Log likelihood increments for correct (1) and incorrect (0)
        self.llr_correct = math.log(p1 / p0)
        self.llr_incorrect = math.log((1.0 - p1) / (1.0 - p0))

    def evaluate(self, responses: List[bool]) -> SPRTResult:
        """
        Evaluates a sequence of boolean responses (True: correct, False: incorrect).
        Returns an SPRTResult containing the decision and diagnostic values.
        """
        n = len(responses)
        if n == 0:
            return SPRTResult(
                decision=MasteryDecision.CONTINUE_SAMPLING,
                cumulative_llr=0.0,
                trials_count=0,
                correct_count=0,
                upper_threshold_ln_a=round(self.ln_a, 4),
                lower_threshold_ln_b=round(self.ln_b, 4),
                is_terminal=False,
            )

        correct_count = sum(1 for r in responses if r)
        incorrect_count = n - correct_count

        cumulative_llr = (correct_count * self.llr_correct) + (incorrect_count * self.llr_incorrect)

        # Check boundaries
        if cumulative_llr >= self.ln_a:
            decision = MasteryDecision.MASTERY_CONFIRMED
            is_terminal = True
        elif cumulative_llr <= self.ln_b:
            decision = MasteryDecision.NEEDS_REMEDIATION
            is_terminal = True
        elif n >= self.max_trials:
            # Truncated SPRT resolution
            is_terminal = True
            if cumulative_llr > 0.0:
                decision = MasteryDecision.CONDITIONAL_MASTERY
            else:
                decision = MasteryDecision.NEEDS_REMEDIATION
        else:
            decision = MasteryDecision.CONTINUE_SAMPLING
            is_terminal = False

        return SPRTResult(
            decision=decision,
            cumulative_llr=round(cumulative_llr, 4),
            trials_count=n,
            correct_count=correct_count,
            upper_threshold_ln_a=round(self.ln_a, 4),
            lower_threshold_ln_b=round(self.ln_b, 4),
            is_terminal=is_terminal,
        )
