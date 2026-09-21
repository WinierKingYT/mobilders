"""
Cognitive Hesitation Sensor.
Bölüm 1 - Bilişsel Öğretim Manifestosu.
Monitors latency inactivity in the 8-10 second window (before 90s freezing).
Provides a gentle, non-condescending 1-sentence focus whisper to unblock students.
"""

from __future__ import annotations
import math
from typing import Optional
from pydantic import BaseModel, Field


class HesitationSignal(BaseModel):
    is_hesitating: bool
    elapsed_ms: float = Field(..., ge=0.0)
    whisper_message: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)


class CognitiveHesitationSensor:
    HESITATION_THRESHOLD_MS = 8000.0  # 8.0 seconds of complete idle
    MAX_HESITATION_MS = 90000.0        # Above 90s, it escalates to Freezing

    @classmethod
    def evaluate_hesitation(
        cls,
        elapsed_ms: float,
        current_input: str,
        target_equation: str = "",
    ) -> HesitationSignal:
        if not math.isfinite(elapsed_ms) or elapsed_ms < 0.0:
            return HesitationSignal(
                is_hesitating=False,
                elapsed_ms=0.0,
                whisper_message=None,
                confidence=0.0,
            )

        trimmed = str(current_input or "").strip()

        # If student is actively writing, there is no hesitation
        if len(trimmed) > 0:
            return HesitationSignal(
                is_hesitating=False,
                elapsed_ms=elapsed_ms,
                whisper_message=None,
                confidence=0.0,
            )

        # Normal deliberation time (< 8s)
        if elapsed_ms < cls.HESITATION_THRESHOLD_MS:
            return HesitationSignal(
                is_hesitating=False,
                elapsed_ms=elapsed_ms,
                whisper_message=None,
                confidence=0.0,
            )

        # Generate gentle, supportive 1-sentence whisper based on formula context
        whisper = cls._generate_contextual_whisper(str(target_equation or ""))

        confidence = min(1.0, (elapsed_ms - cls.HESITATION_THRESHOLD_MS) / 10000.0 + 0.6)

        return HesitationSignal(
            is_hesitating=True,
            elapsed_ms=elapsed_ms,
            whisper_message=whisper,
            confidence=round(confidence, 2),
        )

    @classmethod
    def _generate_contextual_whisper(cls, equation: str) -> str:
        clean = equation.replace(" ", "")
        if "(" in clean:
            return "Önce parantezin önündeki sayıya veya işarete odaklanalım mı?"
        if "^2" in clean or "x²" in clean:
            return "Önce tüm terimleri eşitliğin bir tarafına toplayıp sıfır yapalım mı?"
        if "/" in clean:
            return "Önce paydaları eşitlemek veya içler-dışlar yapmak işimizi kolaylaştırabilir mi?"
        if "=" in clean:
            return "Önce x'in yanındaki sabit sayıyı karşıya geçirmeye ne dersin?"
        return "Küçük bir ilk adımla başlayalım mı?"
