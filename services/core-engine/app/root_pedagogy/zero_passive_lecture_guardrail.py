"""
Zero Passive Lecture Guardrail.
Bölüm 1 - Bilişsel Öğretim Manifestosu.
Enforces that no tutor, hint, or dialog outputs passive, long lectures.
Rules:
1. Max 3 sentences.
2. Max 40 words.
3. Must end with an actionable prompt / question (ends with '?', '!', or imperative).
4. Rejects passive monolog markers (e.g. "şimdi bu konuyu dinleyelim", "özetle anlatmak gerekirse").
"""

from __future__ import annotations
import re
from typing import Optional
from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    is_valid: bool
    sentence_count: int
    word_count: int
    violation_reason: Optional[str] = None
    sanitized_text: str
    actionable_directive: Optional[str] = None


class ZeroPassiveLectureGuardrail:
    MAX_SENTENCES = 3
    MAX_WORDS = 40

    PASSIVE_PATTERNS = [
        r"\b(dinleyelim|dinleyin|izleyelim|izleyin)\b",
        r"\b(özetle\s+anlatmak\s+gerekirse|özetlemek\s+gerekirse)\b",
        r"\b(öncelikle\s+bilmelisiniz\s+ki|bilindiği\s+üzere)\b",
        r"\b(teorik\s+olarak\s+açıklarsak|konu\s+anlatımına\s+geçelim)\b",
        r"\b(videoyu\s+izleyin|dersi\s+dinleyin)\b",
        r"\b(burayı\s+ezberleyelim|ezberlememiz\s+gerekir)\b",
        r"\b(şimdi\s+arkamıza\s+yaslanalım)\b",
    ]

    ACTION_ENDINGS = (
        "?",
        "!",
        "yaz.",
        "yazın.",
        "dene.",
        "deneyin.",
        "çöz.",
        "hesapla.",
        "bakalım.",
        "bul.",
        "bulun.",
        "belirle.",
        "söyle.",
    )

    @classmethod
    def enforce(cls, text: str, fallback_directive: str = "Şimdi sen dene?") -> str:
        """
        Guarantees actionable, non-passive text. If invalid or passive, returns sanitized version.
        """
        result = cls.validate_and_sanitize(text)
        if result.is_valid:
            return result.sanitized_text
        if result.sanitized_text:
            return result.sanitized_text
        return fallback_directive

    @classmethod
    def validate_and_sanitize(cls, text: str) -> GuardrailResult:
        trimmed = text.strip()
        if not trimmed:
            return GuardrailResult(
                is_valid=False,
                sentence_count=0,
                word_count=0,
                violation_reason="İfade boş olamaz.",
                sanitized_text="",
            )

        # 1. Passive pattern detection
        for pat in cls.PASSIVE_PATTERNS:
            if re.search(pat, trimmed, re.IGNORECASE):
                return GuardrailResult(
                    is_valid=False,
                    sentence_count=len(re.split(r"[.!?]+", trimmed)),
                    word_count=len(trimmed.split()),
                    violation_reason=f"Pasif monolog kalıbı tespit edildi: '{pat}'",
                    sanitized_text="",
                )

        # 2. Count sentences and words
        # Split sentences by period, exclamation, question mark
        raw_sentences = [s.strip() for s in re.split(r"[.!?]+", trimmed) if s.strip()]
        sentence_count = len(raw_sentences)
        words = trimmed.split()
        word_count = len(words)

        # 3. Check bounds
        if sentence_count > cls.MAX_SENTENCES:
            # Crop to max sentences and append quick action question
            cropped = ". ".join(raw_sentences[: cls.MAX_SENTENCES]) + "?"
            return GuardrailResult(
                is_valid=False,
                sentence_count=sentence_count,
                word_count=word_count,
                violation_reason=f"Cümle sayısı sınırı aşıldı ({sentence_count} > {cls.MAX_SENTENCES}).",
                sanitized_text=cropped,
                actionable_directive="Bir sonraki adımı dene?",
            )

        if word_count > cls.MAX_WORDS:
            cropped = " ".join(words[: cls.MAX_WORDS])
            if not cropped.endswith(cls.ACTION_ENDINGS):
                cropped += "?"
            return GuardrailResult(
                is_valid=False,
                sentence_count=sentence_count,
                word_count=word_count,
                violation_reason=f"Kelime sayısı sınırı aşıldı ({word_count} > {cls.MAX_WORDS}).",
                sanitized_text=cropped,
                actionable_directive="Şimdi sen dene?",
            )

        # 4. Actionable directive check
        ends_with_action = trimmed.endswith(cls.ACTION_ENDINGS)
        if not ends_with_action:
            # Append prompt to ensure active co-solving
            sanitized = trimmed + " Şimdi sen dene?"
            return GuardrailResult(
                is_valid=False,
                sentence_count=sentence_count,
                word_count=word_count,
                violation_reason="İfade eyleme dönük bir soru veya yönerge ile bitmiyor.",
                sanitized_text=sanitized,
                actionable_directive="Şimdi sen dene?",
            )

        return GuardrailResult(
            is_valid=True,
            sentence_count=sentence_count,
            word_count=word_count,
            sanitized_text=trimmed,
            actionable_directive=raw_sentences[-1] if raw_sentences else None,
        )
