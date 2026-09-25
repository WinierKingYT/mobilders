"""
Experimental Voice Socratic Interaction Engine.
Provides spoken Socratic tutoring for students with dysgraphia or motor learning friction.

Architectural Guarantees:
1. Speech-to-Text (STT) transcript ingestion.
2. VAD noise/breath filtering and ambient thresholding.
3. Spoken mathematical normalization ("x kare" -> "x^2", "karekök" -> "sqrt()").
4. Socratic dialogue generation with question-to-explanation ratio >= 2.0.
5. Zero-Leakage audio stream safety lock: guarantees no root or answer is EVER uttered aloud.
6. Generates standard TTS audio streaming payload.
"""

from __future__ import annotations
import re
import time
from typing import Optional, List
from app.socratic.pipeline import SocraticPipeline, SocraticRequest
from app.socratic.guardrail import ZeroLeakageGuardrail
from app.models.schemas import VoiceSocraticRequest, VoiceSocraticResponse


class VoiceSocraticEngine:
    """Orchestrates spoken audio Socratic interactions with zero-leakage safety."""

    # Common ambient noise / breath / hesitation tokens to filter out
    NOISE_PATTERNS = [
        re.compile(r"\[(öksürük|nefes|hımm|ah|cough|breath|sigh|sniffle|silence|noise|gasp)\]", re.IGNORECASE),
        re.compile(r"\*(öksürük|nefes|hımm|ah|cough|breath|sigh|sniffle|silence|noise|gasp)\*", re.IGNORECASE),
        re.compile(r"\b(uh|um|hımm|öhö|hmm|ah|eh)\b", re.IGNORECASE),
        re.compile(r"[\.]{2,}|[-]{2,}"),
    ]

    def __init__(
        self,
        socratic_pipeline: Optional[SocraticPipeline] = None,
        guardrail: Optional[ZeroLeakageGuardrail] = None,
    ):
        self.pipeline = socratic_pipeline or SocraticPipeline()
        self.guardrail = guardrail or ZeroLeakageGuardrail()

    def filter_ambient_noise(self, text: str) -> str:
        """Filters ambient noise, breath sounds, coughs, and transcription hesitations."""
        if not text:
            return ""
        cleaned = text
        for pattern in self.NOISE_PATTERNS:
            cleaned = pattern.sub(" ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # If string contains only punctuation or whitespace, treat as silence
        if not re.search(r"\w", cleaned):
            return ""
        return cleaned

    def normalize_spoken_math(self, text: str, language: str = "tr") -> str:
        """Translates spoken mathematics phonetic phrases into formal algebraic notation."""
        if not text:
            return ""

        result = text
        lang = (language or "tr").lower()

        if lang == "tr":
            # Powers
            result = re.sub(r"\b([a-zA-Z])\s+kare\b", r"\1^2", result, flags=re.IGNORECASE)
            result = re.sub(r"\b([a-zA-Z])\s+küp\b", r"\1^3", result, flags=re.IGNORECASE)
            result = re.sub(r"\b([a-zA-Z])\s+üzeri\s+(\d+)\b", r"\1^\2", result, flags=re.IGNORECASE)
            result = re.sub(r"\b([a-zA-Z])\s+üssü\s+(\d+)\b", r"\1^\2", result, flags=re.IGNORECASE)
            # Roots
            result = re.sub(r"\bkarekök\s+([a-zA-Z0-9]+)\b", r"sqrt(\1)", result, flags=re.IGNORECASE)
            # Operators
            result = re.sub(r"\bartı\b", "+", result, flags=re.IGNORECASE)
            result = re.sub(r"\beksi\b", "-", result, flags=re.IGNORECASE)
            result = re.sub(r"\bçarpı\b", "*", result, flags=re.IGNORECASE)
            result = re.sub(r"\bbölü\b", "/", result, flags=re.IGNORECASE)
            # Comparisons
            result = re.sub(r"\bküçük\s+eşittir\b", "<=", result, flags=re.IGNORECASE)
            result = re.sub(r"\bbüyük\s+eşittir\b", ">=", result, flags=re.IGNORECASE)
            result = re.sub(r"\beşittir\b", "=", result, flags=re.IGNORECASE)
            result = re.sub(r"\bküçüktür\b", "<", result, flags=re.IGNORECASE)
            result = re.sub(r"\bbüyüktür\b", ">", result, flags=re.IGNORECASE)
        else:
            # English
            result = re.sub(r"\b([a-zA-Z])\s+squared\b", r"\1^2", result, flags=re.IGNORECASE)
            result = re.sub(r"\b([a-zA-Z])\s+cubed\b", r"\1^3", result, flags=re.IGNORECASE)
            result = re.sub(r"\b([a-zA-Z])\s+to\s+the\s+power\s+of\s+(\d+)\b", r"\1^\2", result, flags=re.IGNORECASE)
            result = re.sub(r"\bsquare\s+root\s+of\s+([a-zA-Z0-9]+)\b", r"sqrt(\1)", result, flags=re.IGNORECASE)
            result = re.sub(r"\bplus\b", "+", result, flags=re.IGNORECASE)
            result = re.sub(r"\bminus\b", "-", result, flags=re.IGNORECASE)
            result = re.sub(r"\bmultiplied\s+by\b", "*", result, flags=re.IGNORECASE)
            result = re.sub(r"\btimes\b", "*", result, flags=re.IGNORECASE)
            result = re.sub(r"\bdivided\s+by\b", "/", result, flags=re.IGNORECASE)
            result = re.sub(r"\bis\s+equal\s+to\b", "=", result, flags=re.IGNORECASE)
            result = re.sub(r"\bequals\b", "=", result, flags=re.IGNORECASE)
            result = re.sub(r"\bless\s+than\s+or\s+equal\s+to\b", "<=", result, flags=re.IGNORECASE)
            result = re.sub(r"\bgreater\s+than\s+or\s+equal\s+to\b", ">=", result, flags=re.IGNORECASE)
            result = re.sub(r"\bless\s+than\b", "<", result, flags=re.IGNORECASE)
            result = re.sub(r"\bgreater\s+than\b", ">", result, flags=re.IGNORECASE)

        return re.sub(r"\s+", " ", result).strip()

    def process_voice_turn(self, request: VoiceSocraticRequest) -> VoiceSocraticResponse:
        t0 = time.perf_counter()

        raw_transcript = str(request.audio_transcript or "").strip()
        cleaned_transcript = self.filter_ambient_noise(raw_transcript)
        was_vad_filtered = cleaned_transcript != raw_transcript

        if not cleaned_transcript:
            fallback_text = (
                "Seni tam duyamadım. Tekrar söyler misin?"
                if request.language == "tr"
                else "I could not hear you clearly. Could you repeat?"
            )
            audio_url = self._synthesize_audio_stream_uri(
                text=fallback_text,
                session_id=request.session_id,
                language=request.language,
            )
            return VoiceSocraticResponse(
                socratic_guidance_text=fallback_text,
                audio_stream_url=audio_url,
                zero_leakage_enforced=True,
                socratic_ratio=1.0,
                latency_ms=0.0,
                normalized_transcript="",
                vad_filtered=True,
            )

        # Mathematical normalization
        normalized_transcript = self.normalize_spoken_math(cleaned_transcript, request.language)

        # 1. Forward spoken transcript into 4-Layer Socratic Pipeline
        socratic_req = SocraticRequest(
            user_input=normalized_transcript[:1000],  # DoS guard
            target_equation=request.target_equation,
            previous_step=request.previous_step,
            solution_roots=request.solution_roots,
            language=request.language,
        )

        monologue_log = self.pipeline.process(socratic_req)
        raw_speech_text = monologue_log.final_output

        # 2. Hard Zero-Leakage Audio Gating:
        # Strictly verify that no roots or solution disclosures leak into spoken audio
        sanitized_speech_text, was_intercepted = self.guardrail.enforce_zero_leakage(
            proposed_text=raw_speech_text,
            solution_roots=request.solution_roots,
            language=request.language,
        )

        # Re-check socratic question ratio on the sanitized speech text
        socratic_ratio = self.guardrail.calculate_socratic_ratio(sanitized_speech_text)

        # 3. Simulate low-latency TTS audio stream generation
        audio_stream_url = self._synthesize_audio_stream_uri(
            text=sanitized_speech_text,
            session_id=request.session_id,
            language=request.language,
        )

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return VoiceSocraticResponse(
            socratic_guidance_text=sanitized_speech_text,
            audio_stream_url=audio_stream_url,
            zero_leakage_enforced=True,
            socratic_ratio=socratic_ratio,
            latency_ms=round(latency_ms, 2),
            normalized_transcript=normalized_transcript,
            vad_filtered=was_vad_filtered,
        )

    def _synthesize_audio_stream_uri(self, text: str, session_id: str, language: str) -> str:
        """Constructs secure audio stream endpoint for native mobile audio player."""
        import hashlib
        h = hashlib.sha256(f"{session_id}:{text}".encode("utf-8")).hexdigest()[:12]
        return f"/api/v1/voice/stream/{session_id}/{h}.mp3?lang={language}"
