"""
Synthetic Student Twin Persona Profiles.
Defines 5 core cognitive personas representing distinct learning, memory,
and metacognitive calibration archetypes.
"""

from __future__ import annotations
import math
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class CognitivePersonaType(str, Enum):
    FAST_FORGETTER = "fast_forgetter"
    OVERCONFIDENT = "overconfident"
    IMPOSTER = "imposter"
    SLIP_PRONE = "slip_prone"
    FLUENT_MASTER = "fluent_master"


@dataclass
class StudentTwinProfile:
    """Psychometric and cognitive parameters for a synthetic persona archetype."""
    persona_type: CognitivePersonaType
    p_l0: float           # Initial mastery probability
    p_t: float            # Knowledge transition rate per trial
    p_s: float            # Slip probability (making mistake despite knowing)
    p_g: float            # Guess probability (correct by luck)
    fsrs_s0: float        # Memory stability (half-life in days)
    confidence_bias: float # Metacognitive bias (+ for overconfident, - for imposter)
    ddm_boundary_a: float  # DDM threshold / caution
    ddm_drift_v: float     # DDM information accumulation rate

    def __post_init__(self) -> None:
        self.p_l0 = min(max(float(self.p_l0) if math.isfinite(self.p_l0) else 0.2, 0.001), 0.999)
        self.p_t = min(max(float(self.p_t) if math.isfinite(self.p_t) else 0.2, 0.001), 0.999)
        self.p_s = min(max(float(self.p_s) if math.isfinite(self.p_s) else 0.1, 0.001), 0.999)
        self.p_g = min(max(float(self.p_g) if math.isfinite(self.p_g) else 0.1, 0.001), 0.999)
        self.fsrs_s0 = max(float(self.fsrs_s0) if math.isfinite(self.fsrs_s0) else 5.0, 0.1)
        self.confidence_bias = min(max(float(self.confidence_bias) if math.isfinite(self.confidence_bias) else 0.0, -1.0), 1.0)
        self.ddm_boundary_a = max(float(self.ddm_boundary_a) if math.isfinite(self.ddm_boundary_a) else 1.0, 0.1)
        self.ddm_drift_v = max(float(self.ddm_drift_v) if math.isfinite(self.ddm_drift_v) else 1.0, 0.1)

    @staticmethod
    def get_defaults() -> Dict[CognitivePersonaType, StudentTwinProfile]:
        return {
            CognitivePersonaType.FAST_FORGETTER: StudentTwinProfile(
                persona_type=CognitivePersonaType.FAST_FORGETTER,
                p_l0=0.15,
                p_t=0.18,
                p_s=0.12,
                p_g=0.15,
                fsrs_s0=2.2,       # Forgets quickly without spaced rehearsal
                confidence_bias=0.0,
                ddm_boundary_a=1.2,
                ddm_drift_v=1.1,
            ),
            CognitivePersonaType.OVERCONFIDENT: StudentTwinProfile(
                persona_type=CognitivePersonaType.OVERCONFIDENT,
                p_l0=0.18,
                p_t=0.15,
                p_s=0.18,
                p_g=0.20,
                fsrs_s0=8.0,
                confidence_bias=+0.30, # Severe overestimation of competence
                ddm_boundary_a=0.75,  # Impulsive, low caution
                ddm_drift_v=1.2,
            ),
            CognitivePersonaType.IMPOSTER: StudentTwinProfile(
                persona_type=CognitivePersonaType.IMPOSTER,
                p_l0=0.25,
                p_t=0.28,
                p_s=0.04,
                p_g=0.08,
                fsrs_s0=16.0,
                confidence_bias=-0.35, # Severe underestimation despite high mastery
                ddm_boundary_a=2.4,   # Hyper-cautious, checks work multiple times
                ddm_drift_v=1.9,
            ),
            CognitivePersonaType.SLIP_PRONE: StudentTwinProfile(
                persona_type=CognitivePersonaType.SLIP_PRONE,
                p_l0=0.20,
                p_t=0.22,
                p_s=0.28,             # High computation / careless arithmetic slips
                p_g=0.14,
                fsrs_s0=10.0,
                confidence_bias=0.05,
                ddm_boundary_a=1.0,
                ddm_drift_v=1.4,
            ),
            CognitivePersonaType.FLUENT_MASTER: StudentTwinProfile(
                persona_type=CognitivePersonaType.FLUENT_MASTER,
                p_l0=0.40,
                p_t=0.42,
                p_s=0.03,             # Highly reliable, near-zero errors
                p_g=0.10,
                fsrs_s0=28.0,         # Long retention stability
                confidence_bias=0.02, # Highly calibrated metacognition
                ddm_boundary_a=1.4,
                ddm_drift_v=2.6,      # High drift rate, fast fluid solutions
            ),
        }
