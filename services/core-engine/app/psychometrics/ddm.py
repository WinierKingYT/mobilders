"""
Ratcliff Drift-Diffusion Model (DDM) Engine.
Implements EZ-Diffusion closed-form parameter estimation (Wagenmakers et al., 2007)
to extract cognitive drift rate (v), boundary separation / caution (a),
and non-decision time (Ter) from millisecond telemetry.
"""

from __future__ import annotations
import math
from typing import List, Optional
from pydantic import BaseModel, Field


class DDMParameters(BaseModel):
    """Estimated DDM Parameters and Cognitive State Classification."""
    drift_rate: float = Field(..., description="v: Cognitive processing speed and information quality")
    boundary_separation: float = Field(..., description="a: Cautiousness / boundary separation")
    non_decision_time: float = Field(..., description="Ter: Non-decision time (motor + encoding) in seconds")
    mean_decision_time: float = Field(..., description="M_karar: Mean time spent in decision integration")
    proportion_correct: float = Field(..., description="Pc: Proportion of correct responses after correction")
    cognitive_state: str = Field(..., description="Diagnostic classification: fluent_mastery, rapid_guessing, cautious_effort, high_friction, etc.")


class EZDiffusionSolver:
    """
    EZ-Diffusion closed-form solver for Ratcliff Diffusion Model.
    Reference: Wagenmakers, E.-J., van der Maas, H. L. J., & Grasman, R. P. P. P. (2007).
    An EZ-diffusion model for response time and accuracy. Psychonomic Bulletin & Review, 14(1), 3-22.
    """

    DEFAULT_SCALE_S = 0.1  # Standard scaling constant in literature

    @classmethod
    def solve(
        cls,
        mrt: float,
        vrt: float,
        pc: float,
        n_trials: Optional[int] = None,
        s: float = DEFAULT_SCALE_S,
        custom_thresholds: Optional[Dict[str, float]] = None,
    ) -> DDMParameters:
        """
        Solves DDM parameters analytically using closed-form equations.

        Args:
            mrt: Mean Response Time in seconds (e.g. 1.85 for 1850ms).
            vrt: Variance of Response Time in seconds^2 (e.g. 0.05).
            pc: Proportion of correct responses (0.0 to 1.0).
            n_trials: Optional total count of trials for Laplace edge correction.
            s: Scaling constant for diffusion coefficient (default 0.1).

        Returns:
            DDMParameters instance with v, a, Ter, and cognitive state.

        Raises:
            ValueError: If MRT < 0.100s or VRT <= 0.0 (ERR_DDM_DEGENERATE_DATA).
        """
        if mrt < 0.100:
            raise ValueError(
                f"Degenerate response time: MRT={mrt:.3f}s is below physiological minimum (100ms) [ERR_DDM_DEGENERATE_DATA 3002]"
            )
        if vrt <= 1e-7:
            raise ValueError(
                f"Degenerate variance: VRT={vrt:.6f}s^2 is zero or negative [ERR_DDM_DEGENERATE_DATA 3002]"
            )

        # 1. Edge Correction for Pc (Laplace smoothing if 0.0 or 1.0)
        pc_corrected = pc
        if n_trials is not None and n_trials > 0:
            if pc >= 1.0:
                pc_corrected = (n_trials - 0.5) / float(n_trials)
            elif pc <= 0.0:
                pc_corrected = 0.5 / float(n_trials)
        else:
            pc_corrected = max(0.001, min(0.999, pc_corrected))

        # Avoid exact 0.5 singularity where logit L = 0
        if abs(pc_corrected - 0.5) < 1e-6:
            pc_corrected = 0.5001

        # 2. Logit transformation
        logit_l = math.log(pc_corrected / (1.0 - pc_corrected))

        # 3. Intermediate term: x = L * (Pc^2 * L - Pc * L + Pc - 0.5) / VRT
        numerator = logit_l * (
            (pc_corrected ** 2 * logit_l)
            - (pc_corrected * logit_l)
            + pc_corrected
            - 0.5
        )
        x = max(1e-12, numerator / vrt)

        # 4. Drift rate (v)
        sign = 1.0 if pc_corrected > 0.5 else -1.0
        drift_rate = sign * s * (x ** 0.25)

        # 5. Boundary separation (a)
        if abs(drift_rate) < 1e-9:
            boundary_separation = 0.05
        else:
            boundary_separation = (s ** 2 * logit_l) / drift_rate

        # 6. Mean Decision Time (M_karar) and Non-Decision Time (Ter)
        # Using the exact identity: (1 - e^y)/(1 + e^y) = 2*Pc - 1 where y = -v*a / s^2 = -L
        mean_decision_time = (boundary_separation / (2.0 * drift_rate)) * (2.0 * pc_corrected - 1.0)
        non_decision_time = mrt - mean_decision_time

        # If non-decision time is non-physiologically negative, bound it cleanly
        if non_decision_time < 0.05:
            non_decision_time = 0.05

        # 7. Cognitive State Diagnostic Classification
        cognitive_state = cls._classify_state(
            drift_rate=drift_rate,
            boundary_separation=boundary_separation,
            mrt=mrt,
            pc=pc_corrected,
            s=s,
            custom_thresholds=custom_thresholds,
        )

        return DDMParameters(
            drift_rate=round(drift_rate, 4),
            boundary_separation=round(boundary_separation, 4),
            non_decision_time=round(non_decision_time, 4),
            mean_decision_time=round(mean_decision_time, 4),
            proportion_correct=round(pc_corrected, 4),
            cognitive_state=cognitive_state,
        )

    @classmethod
    def _classify_state(
        cls,
        drift_rate: float,
        boundary_separation: float,
        mrt: float,
        pc: float,
        s: float,
        custom_thresholds: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        Classifies cognitive profile based on DDM parameters:
        - fluent_mastery: High drift rate, balanced caution.
        - rapid_guessing: Low RT, very low caution (a), accuracy near chance.
        - cautious_effort: High caution (a), moderate drift rate, longer RT.
        - high_friction: Negative or very low drift rate, struggling with misconceptions.
        - imposter_success: High caution (a), high accuracy, but self-doubt / slow.
        """
        # Relative thresholds scaled by s (default s=0.1)
        scale_ratio = s / 0.1
        if custom_thresholds:
            v_high = custom_thresholds.get("v_high", 0.12) * scale_ratio
            v_low = custom_thresholds.get("v_low", 0.03) * scale_ratio
            a_low = custom_thresholds.get("a_low", 0.07) * scale_ratio
            a_high = custom_thresholds.get("a_high", 0.14) * scale_ratio
        else:
            v_high = 0.12 * scale_ratio
            v_low = 0.03 * scale_ratio
            a_low = 0.07 * scale_ratio
            a_high = 0.14 * scale_ratio

        if (mrt < 2.5 and pc < 0.65) or (mrt < 3.5 and boundary_separation <= (a_low + 0.02) and pc < 0.65):
            return "rapid_guessing"
        if drift_rate >= v_high and boundary_separation <= a_high:
            return "fluent_mastery"
        if drift_rate > 0.0 and boundary_separation > a_high:
            return "imposter_success" if pc >= 0.85 else "cautious_effort"
        if drift_rate <= v_low or pc < 0.50:
            return "high_friction"
        return "balanced_learning"

    @classmethod
    def solve_from_trials(
        cls,
        reaction_times: List[float],
        correctness: List[bool],
        filter_outliers: bool = True,
        s: float = DEFAULT_SCALE_S,
        custom_thresholds: Optional[Dict[str, float]] = None,
    ) -> DDMParameters:
        """
        Filters outliers and computes MRT, VRT, and Pc from raw trials list.
        Outlier filter: excludes RT < 0.15s and RT > 15.0s (per Document 19).
        """
        if len(reaction_times) != len(correctness):
            raise ValueError("reaction_times and correctness lists must have identical lengths")

        paired = list(zip(reaction_times, correctness))
        if filter_outliers:
            # Filter background interruptions (>15s) and physiological reflex glitches (<0.15s)
            paired = [(rt, c) for rt, c in paired if 0.15 <= rt <= 15.0]

        if len(paired) < 3:
            raise ValueError("At least 3 valid non-outlier trials required to compute DDM variance")

        rts = [p[0] for p in paired]
        corrects = [p[1] for p in paired]

        mrt = sum(rts) / len(rts)
        variance = sum((rt - mrt) ** 2 for rt in rts) / (len(rts) - 1)
        pc = sum(1 for c in corrects if c) / len(corrects)

        return cls.solve(
            mrt=mrt,
            vrt=variance,
            pc=pc,
            n_trials=len(corrects),
            s=s,
            custom_thresholds=custom_thresholds,
        )
