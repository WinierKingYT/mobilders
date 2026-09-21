"""
FSRS-4.5 (Free Spaced Repetition Scheduler) Engine.
Implements the 17-parameter DSR (Difficulty, Stability, Retrievability) memory model
adapted for procedural mathematics and cognitive skill retention.
Includes:
- Walker & Stickgold Circadian Sleep Barrier (delta_t < 14h -> delta_S = 0)
- Session fatigue discount (t > 15min -> S * 0.85)
"""

from __future__ import annotations
import math
from enum import IntEnum
from typing import Tuple, Optional
from pydantic import BaseModel, Field


class Rating(IntEnum):
    AGAIN = 1  # Failure, misconception, formula error
    HARD = 2   # High hesitation / latency (>2x median), but correct
    GOOD = 3   # Fluent standard execution
    EASY = 4   # Effortless, immediate execution (<0.5x median latency)


class DSRState(BaseModel):
    difficulty: float = Field(..., ge=1.0, le=10.0, description="D: Cognitive complexity (1.0 to 10.0)")
    stability: float = Field(..., ge=0.01, description="S: Memory stability in days")
    retrievability: float = Field(..., ge=0.0, le=1.0, description="R: Probability of recall")
    repetitions: int = Field(0, ge=0)
    lapses: int = Field(0, ge=0)


class FSRSEngine:
    """
    FSRS-4.5 Memory Engine for algebraic skill retention.
    """

    # 17 default parameters calibrated for mathematical and procedural skills
    DEFAULT_WEIGHTS: Tuple[float, ...] = (
        0.4, 0.9, 2.3, 10.9,    # w0..w3: S0(1)..S0(4)
        4.93, 0.94, 0.86, 0.01, # w4..w7: D0 and difficulty dynamics
        1.49, 0.14, 0.94,       # w8..w10: Stability increase on success
        2.18, 0.05, 0.34, 1.26, # w11..w14: Stability decay on lapse
        0.29, 2.61              # w15, w16: Rating modifiers for Hard and Easy
    )

    FACTOR = 19.0 / 81.0  # (1/0.90^2 - 1) for 90% target retention
    CIRCADIAN_SLEEP_HOURS = 14.0  # Minimum hours for sleep-dependent consolidation

    def __init__(self, weights: Optional[Tuple[float, ...]] = None):
        self.w = weights if weights is not None else self.DEFAULT_WEIGHTS
        if len(self.w) != 17:
            raise ValueError(f"FSRS-4.5 requires exactly 17 parameters, got {len(self.w)}")

    def retrievability(self, elapsed_days: float, stability: float) -> float:
        """
        Computes power-law retrievability R(t, S) = (1 + FACTOR * (t / S))^-0.5
        """
        if elapsed_days <= 0.0:
            return 1.0
        if stability <= 0.01:
            stability = 0.01

        r = (1.0 + self.FACTOR * (elapsed_days / stability)) ** -0.5
        return max(0.0, min(1.0, r))

    def init_dsr(self, rating: Rating) -> DSRState:
        """
        Initializes DSR state on the student's first encounter with a Knowledge Component.
        """
        g = float(rating.value)
        # S0 = w_{G-1}
        init_s = max(0.1, self.w[rating.value - 1])

        # D0 = w4 - e^(w5 * (G - 1)) + 1
        raw_d = self.w[4] - math.exp(self.w[5] * (g - 1.0)) + 1.0
        init_d = max(1.0, min(10.0, raw_d))

        return DSRState(
            difficulty=round(init_d, 4),
            stability=round(init_s, 4),
            retrievability=1.0,
            repetitions=1,
            lapses=1 if rating == Rating.AGAIN else 0,
        )

    def review(
        self,
        current_state: DSRState,
        rating: Rating,
        elapsed_days: float,
        session_duration_minutes: float = 0.0,
    ) -> DSRState:
        """
        Updates DSR state following a review attempt after elapsed_days.
        Enforces Circadian Sleep Barrier (Walker & Stickgold):
        If elapsed_days < 14h (0.5833 days), delta_S = 0 (same-day cramming produces no stability increase).
        """
        g = float(rating.value)
        s = current_state.stability
        d = current_state.difficulty
        r = self.retrievability(elapsed_days, s)

        # 1. Update Difficulty
        delta_d = -self.w[6] * (g - 3.0)
        d0_good = self.w[4] - math.exp(self.w[5] * 2.0) + 1.0  # D0(3)
        new_d = (self.w[7] * d0_good) + ((1.0 - self.w[7]) * (d + delta_d))
        new_d = max(1.0, min(10.0, new_d))

        # 2. Check Circadian Sleep Consolidation Barrier
        # 14 hours in days: 14.0 / 24.0 = 0.5833 days
        is_circadian_locked = elapsed_days < (self.CIRCADIAN_SLEEP_HOURS / 24.0)

        # 3. Update Stability
        delta_r = max(0.0, min(1.0, 1.0 - r))
        if rating == Rating.AGAIN:
            # Lapse / Forgetting: old stability leaves a residue (Savings Effect)
            exp_term = math.exp(min(20.0, self.w[14] * delta_r))
            new_s = (
                self.w[11]
                * (new_d ** -self.w[12])
                * (((s + 1.0) ** self.w[13]) - 1.0)
                * exp_term
            )
            new_s = max(0.1, min(new_s, s))  # Stability drops on lapse
            new_lapses = current_state.lapses + 1
        else:
            # Successful retrieval (Hard, Good, Easy)
            if is_circadian_locked:
                # Circadian lock active: No sleep consolidation yet; stability does not advance
                new_s = s
            else:
                k_g = self.w[15] if rating == Rating.HARD else (self.w[16] if rating == Rating.EASY else 1.0)
                exp_term = math.exp(min(20.0, self.w[10] * delta_r)) - 1.0
                s_factor = math.exp(self.w[8]) * (11.0 - new_d) * (s ** -self.w[9]) * exp_term * k_g
                s_increment = s * (1.0 + max(0.0, s_factor))
                new_s = max(s + 0.1, s_increment)

            new_lapses = current_state.lapses

        # 4. Session Fatigue Discount (Doc 10: session > 15 mins reduces acquisition efficiency)
        if session_duration_minutes > 15.0:
            new_s = max(0.1, new_s * 0.85)

        return DSRState(
            difficulty=round(new_d, 4),
            stability=round(new_s, 4),
            retrievability=round(self.retrievability(0.0, new_s), 4),
            repetitions=current_state.repetitions + 1,
            lapses=new_lapses,
        )
