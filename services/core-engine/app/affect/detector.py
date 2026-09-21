"""
Affective State Detector and Circuit Breaker Engine.
Based on D'Mello & Graesser (2012, 2014) and Pekrun (2006) Affective Dynamics.
Features:
- 5-State Affective Hidden Markov Model (Flow, Confusion, Frustration, Boredom, Delight).
- Multi-modal Telemetry Tracker (Latency Freezing, Rage Clicks/Thrashing, Help Abuse, Despair NLP Triggers).
- Affective Circuit Breaker (F_score >= 0.85): Pauses session, shows empathetic historical normalization,
  pivots to Worked Example, and enforces psychometric penalty quarantine.
"""

from __future__ import annotations
import math
import re
import threading
from collections import OrderedDict
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class AffectiveState(str, Enum):
    FLOW = "FLOW"
    CONFUSION = "CONFUSION"
    FRUSTRATION = "FRUSTRATION"
    BOREDOM = "BOREDOM"
    DELIGHT = "DELIGHT"


class BehaviorObservation(BaseModel):
    response_time_ms: float = Field(0.0, ge=0.0)
    is_correct: bool
    thrash_events_count: int = Field(0, ge=0, description="Rapid repeated clicks/submits in <= 5 seconds")
    consecutive_errors: int = Field(0, ge=0)
    hint_requests_count: int = Field(0, ge=0)
    input_text: Optional[str] = None

    @field_validator("response_time_ms", mode="before")
    @classmethod
    def sanitize_response_time(cls, v: Any) -> float:
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val) or val < 0:
                return 0.0
            return val
        except (TypeError, ValueError):
            return 0.0

    @field_validator("thrash_events_count", "consecutive_errors", "hint_requests_count", mode="before")
    @classmethod
    def sanitize_counts(cls, v: Any) -> int:
        try:
            val = int(v)
            return max(0, val)
        except (TypeError, ValueError):
            return 0


class AffectiveAssessment(BaseModel):
    primary_state: AffectiveState
    state_probabilities: Dict[AffectiveState, float]
    frustration_score: float = Field(..., ge=0.0, le=1.0)
    is_circuit_breaker_tripped: bool
    is_freezing_detected: bool
    is_rapid_guessing_detected: bool
    quarantine_active: bool
    pivot_to_worked_example: bool
    intervention_title: Optional[str] = None
    intervention_message: Optional[str] = None


class AffectiveStateDetector:
    """
    Real-time Affective State Analyzer and Circuit Breaker.
    """

    CIRCUIT_BREAKER_THRESHOLD = 0.85
    DEFAULT_BASELINE_RT_MS = 25000.0  # 25 seconds standard step baseline
    FREEZING_THRESHOLD_MS = 90000.0   # 90 seconds absolute latency freeze
    RAPID_GUESSING_THRESHOLD_MS = 3500.0  # 3.5 seconds impulsive guess threshold

    DESPAIR_PATTERNS = [
        r"\banlam(ı|i)yorum\b",
        r"\byapam(ı|i)yorum\b",
        r"\bsa(ç|c)mal(ı|i)k\b",
        r"\bb(ı|i)rak(ı|i)yorum\b",
        r"\bimkans(ı|i)z\b",
        r"\bolmuyor\b",
        r"\b(ç|c)(ı|i)km(ı|i)yor\b",
        r"\bpes\b",
        r"\byeter\b",
        r"\bdelir(e|i)cem\b",
    ]

    def __init__(self, baseline_rt_ms: float = DEFAULT_BASELINE_RT_MS):
        self.baseline_rt_ms = baseline_rt_ms
        self._lock = threading.Lock()
        self.MAX_SESSIONS = 1000
        self._session_beliefs: OrderedDict[str, Dict[AffectiveState, float]] = OrderedDict()
        # Initial belief distribution (global fallback / legacy single-user mode)
        self.beliefs: Dict[AffectiveState, float] = {
            AffectiveState.FLOW: 0.60,
            AffectiveState.CONFUSION: 0.20,
            AffectiveState.FRUSTRATION: 0.05,
            AffectiveState.BOREDOM: 0.05,
            AffectiveState.DELIGHT: 0.10,
        }

        # D'Mello & Graesser 5x5 Transition Matrix
        self.transitions: Dict[AffectiveState, Dict[AffectiveState, float]] = {
            AffectiveState.FLOW: {
                AffectiveState.FLOW: 0.65,
                AffectiveState.CONFUSION: 0.20,
                AffectiveState.FRUSTRATION: 0.05,
                AffectiveState.BOREDOM: 0.05,
                AffectiveState.DELIGHT: 0.05,
            },
            AffectiveState.CONFUSION: {
                AffectiveState.FLOW: 0.25,
                AffectiveState.CONFUSION: 0.40,
                AffectiveState.FRUSTRATION: 0.25,
                AffectiveState.BOREDOM: 0.05,
                AffectiveState.DELIGHT: 0.05,
            },
            AffectiveState.FRUSTRATION: {
                AffectiveState.FLOW: 0.10,
                AffectiveState.CONFUSION: 0.15,
                AffectiveState.FRUSTRATION: 0.60,
                AffectiveState.BOREDOM: 0.15,
                AffectiveState.DELIGHT: 0.00,
            },
            AffectiveState.BOREDOM: {
                AffectiveState.FLOW: 0.20,
                AffectiveState.CONFUSION: 0.10,
                AffectiveState.FRUSTRATION: 0.10,
                AffectiveState.BOREDOM: 0.60,
                AffectiveState.DELIGHT: 0.00,
            },
            AffectiveState.DELIGHT: {
                AffectiveState.FLOW: 0.50,
                AffectiveState.CONFUSION: 0.10,
                AffectiveState.FRUSTRATION: 0.00,
                AffectiveState.BOREDOM: 0.05,
                AffectiveState.DELIGHT: 0.35,
            },
        }

    def has_despair_triggers(self, text: Optional[str]) -> bool:
        if not text:
            return False
        lower = text.lower()
        for pat in self.DESPAIR_PATTERNS:
            if re.search(pat, lower):
                return True
        return False

    def evaluate_telemetry(
        self,
        obs: BehaviorObservation,
        session_id: Optional[str] = None,
    ) -> AffectiveAssessment:
        """
        Processes student observation vector and computes updated affective distribution.
        Supports session_id for isolated multi-tenant tracking.
        """
        # 0. Sanitize telemetry inputs
        rt_ms = obs.response_time_ms
        if not math.isfinite(rt_ms) or rt_ms < 0:
            rt_ms = self.baseline_rt_ms

        thrash_count = max(0, obs.thrash_events_count)
        consec_err = max(0, obs.consecutive_errors)
        hint_count = max(0, obs.hint_requests_count)

        # 1. Feature extraction
        is_freezing = rt_ms >= self.FREEZING_THRESHOLD_MS or (
            rt_ms >= 3.0 * self.baseline_rt_ms and not obs.is_correct
        )
        is_rapid_guessing = (
            rt_ms < self.RAPID_GUESSING_THRESHOLD_MS and not obs.is_correct
        )
        is_thrashing = thrash_count >= 4
        has_despair = self.has_despair_triggers(obs.input_text)
        is_help_abused = hint_count >= 3 and not obs.is_correct

        # 2. Emission Likelihoods P(obs | State)
        emission_likelihoods: Dict[AffectiveState, float] = {}

        if obs.is_correct:
            if rt_ms < 0.5 * self.baseline_rt_ms:
                emission_likelihoods = {
                    AffectiveState.FLOW: 0.50,
                    AffectiveState.CONFUSION: 0.02,
                    AffectiveState.FRUSTRATION: 0.01,
                    AffectiveState.BOREDOM: 0.15,
                    AffectiveState.DELIGHT: 0.32,
                }
            else:
                emission_likelihoods = {
                    AffectiveState.FLOW: 0.60,
                    AffectiveState.CONFUSION: 0.10,
                    AffectiveState.FRUSTRATION: 0.02,
                    AffectiveState.BOREDOM: 0.08,
                    AffectiveState.DELIGHT: 0.20,
                }
        else:
            # Incorrect step
            if is_thrashing or has_despair or is_help_abused or consec_err >= 3:
                # Acute destructive frustration signal
                emission_likelihoods = {
                    AffectiveState.FLOW: 0.01,
                    AffectiveState.CONFUSION: 0.09,
                    AffectiveState.FRUSTRATION: 0.85,
                    AffectiveState.BOREDOM: 0.04,
                    AffectiveState.DELIGHT: 0.01,
                }
            elif is_freezing or consec_err >= 2:
                emission_likelihoods = {
                    AffectiveState.FLOW: 0.05,
                    AffectiveState.CONFUSION: 0.55,
                    AffectiveState.FRUSTRATION: 0.35,
                    AffectiveState.BOREDOM: 0.04,
                    AffectiveState.DELIGHT: 0.01,
                }
            elif is_rapid_guessing:
                emission_likelihoods = {
                    AffectiveState.FLOW: 0.05,
                    AffectiveState.CONFUSION: 0.20,
                    AffectiveState.FRUSTRATION: 0.25,
                    AffectiveState.BOREDOM: 0.50,
                    AffectiveState.DELIGHT: 0.00,
                }
            else:
                emission_likelihoods = {
                    AffectiveState.FLOW: 0.15,
                    AffectiveState.CONFUSION: 0.60,
                    AffectiveState.FRUSTRATION: 0.15,
                    AffectiveState.BOREDOM: 0.09,
                    AffectiveState.DELIGHT: 0.01,
                }

        with self._lock:
            if session_id:
                if session_id in self._session_beliefs:
                    current_beliefs = dict(self._session_beliefs[session_id])
                    self._session_beliefs.move_to_end(session_id)
                else:
                    current_beliefs = {
                        AffectiveState.FLOW: 0.60,
                        AffectiveState.CONFUSION: 0.20,
                        AffectiveState.FRUSTRATION: 0.05,
                        AffectiveState.BOREDOM: 0.05,
                        AffectiveState.DELIGHT: 0.10,
                    }
            else:
                current_beliefs = dict(self.beliefs)

            # 3. HMM Belief Update: B_{t}(s_j) = P(o_t | s_j) * sum_i ( B_{t-1}(s_i) * A_{ij} )
            predicted_beliefs: Dict[AffectiveState, float] = {s: 0.0 for s in AffectiveState}
            for s_j in AffectiveState:
                for s_i in AffectiveState:
                    predicted_beliefs[s_j] += current_beliefs[s_i] * self.transitions[s_i][s_j]

            # Combine with emission
            unnormalized: Dict[AffectiveState, float] = {}
            for s in AffectiveState:
                p = predicted_beliefs[s] * emission_likelihoods[s]
                unnormalized[s] = p if math.isfinite(p) and p >= 0.0 else 0.0

            total_prob = sum(unnormalized.values())
            if total_prob > 0 and math.isfinite(total_prob):
                new_beliefs = {s: unnormalized[s] / total_prob for s in AffectiveState}
            else:
                new_beliefs = predicted_beliefs

            # Acute override: immediate rage click / thrashing / explicit despair immediately spikes frustration
            if is_thrashing or has_despair:
                new_beliefs[AffectiveState.FRUSTRATION] = max(0.90, new_beliefs[AffectiveState.FRUSTRATION])
                rem = 1.0 - new_beliefs[AffectiveState.FRUSTRATION]
                other_sum = sum(v for k, v in new_beliefs.items() if k != AffectiveState.FRUSTRATION)
                if other_sum > 0:
                    for k in new_beliefs:
                        if k != AffectiveState.FRUSTRATION:
                            new_beliefs[k] = (new_beliefs[k] / other_sum) * rem

            # Persist beliefs
            if session_id:
                self._session_beliefs[session_id] = dict(new_beliefs)
                self._session_beliefs.move_to_end(session_id)
                if len(self._session_beliefs) > self.MAX_SESSIONS:
                    self._session_beliefs.popitem(last=False)
            else:
                self.beliefs = dict(new_beliefs)

            primary_state = max(new_beliefs, key=new_beliefs.get)
            f_score = new_beliefs[AffectiveState.FRUSTRATION]
            if not math.isfinite(f_score):
                f_score = 0.05
            f_score = max(0.0, min(1.0, f_score))
            snapshot_beliefs = {k: round(v, 4) for k, v in new_beliefs.items()}

        # 4. Circuit Breaker Determination
        is_breaker_tripped = f_score >= self.CIRCUIT_BREAKER_THRESHOLD

        intervention_title = None
        intervention_message = None

        if is_breaker_tripped:
            intervention_title = "Bir Nefes Verelim"
            intervention_message = (
                "Dur bir saniye! Bu adım gerçekten çok çetin bir cebirsel aşama. "
                "Tarihte matematikçiler de tam burada benzer çıkmazlarla karşılaşmıştı. "
                "Yalnız değilsin; gel bu adımı çözümlü bir model üzerinde birlikte inceleyelim."
            )
        elif is_freezing:
            intervention_title = "Düşünce Molası"
            intervention_message = (
                "Adım üzerinde derinleştiğini görüyorum. Bu aşamada terimleri tek tek incelemek ister misin?"
            )
        elif is_rapid_guessing:
            intervention_title = "Sezgi Freni"
            intervention_message = (
                "Hemen yanıt vermeden önce denklemin iki tarafındaki terimleri 3 saniye gözlemleyelim."
            )

        return AffectiveAssessment(
            primary_state=primary_state,
            state_probabilities=snapshot_beliefs,
            frustration_score=round(f_score, 4),
            is_circuit_breaker_tripped=is_breaker_tripped,
            is_freezing_detected=is_freezing,
            is_rapid_guessing_detected=is_rapid_guessing,
            quarantine_active=is_breaker_tripped,
            pivot_to_worked_example=is_breaker_tripped,
            intervention_title=intervention_title,
            intervention_message=intervention_message,
        )
