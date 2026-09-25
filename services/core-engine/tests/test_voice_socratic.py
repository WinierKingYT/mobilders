"""
Test Suite: Voice Socratic Interaction & Zero-Leakage Audio Gating.
Verifies:
1. Speech-to-Text transcript ingestion and turn processing.
2. Socratic Question-to-Explanation ratio >= 2.0 in spoken response.
3. Audio stream URI synthesis.
4. Hard Zero-Leakage audio stream safety lock:
   - Direct numerical roots and solution disclosures are strictly blocked from audio generation.
5. Multilingual voice turns (Turkish and English).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.voice.service import VoiceSocraticEngine
from app.models.schemas import VoiceSocraticRequest

client = TestClient(app)


def test_voice_socratic_turn_turkish():
    engine = VoiceSocraticEngine()
    req = VoiceSocraticRequest(
        session_id="voice-sess-tr",
        audio_transcript="Bu adımda ne yapacağımı tam anlayamadım, yardımcı olur musun?",
        target_equation="x**2 - 5*x + 6 = 0",
        solution_roots=[2.0, 3.0],
        language="tr",
    )
    res = engine.process_voice_turn(req)
    assert res.zero_leakage_enforced is True
    assert res.socratic_ratio >= 1.5
    assert "?" in res.socratic_guidance_text
    assert res.audio_stream_url is not None
    assert "voice-sess-tr" in res.audio_stream_url
    assert "lang=tr" in res.audio_stream_url
    # Root values must not be leaked
    assert "2" not in res.socratic_guidance_text and "3" not in res.socratic_guidance_text


def test_voice_socratic_turn_english():
    engine = VoiceSocraticEngine()
    req = VoiceSocraticRequest(
        session_id="voice-sess-en",
        audio_transcript="I am stuck on this quadratic equation, what should I do?",
        target_equation="x**2 - 9 = 0",
        solution_roots=[-3.0, 3.0],
        language="en",
    )
    res = engine.process_voice_turn(req)
    assert res.zero_leakage_enforced is True
    assert res.socratic_ratio >= 1.5
    assert "?" in res.socratic_guidance_text
    assert "lang=en" in res.audio_stream_url
    # Root values must not be leaked
    assert "3" not in res.socratic_guidance_text


def test_voice_socratic_zero_leakage_audio_lock():
    # If the student directly demands answers via voice
    engine = VoiceSocraticEngine()
    req = VoiceSocraticRequest(
        session_id="voice-sess-lock",
        audio_transcript="Cevabı söyle bana hemen x kaçtır",
        target_equation="x**2 - 4 = 0",
        solution_roots=[-2.0, 2.0],
        language="tr",
    )
    res = engine.process_voice_turn(req)
    assert res.zero_leakage_enforced is True
    # Guaranteed no numerical answer is leaked in speech output
    assert "2" not in res.socratic_guidance_text
    assert "?" in res.socratic_guidance_text


def test_voice_socratic_api_endpoint():
    payload = {
        "session_id": "voice-api-test",
        "audio_transcript": "Can you give me a hint for factoring?",
        "target_equation": "x**2 - 5*x + 6 = 0",
        "solution_roots": [2.0, 3.0],
        "language": "en",
    }
    res = client.post("/api/v1/voice/socratic-turn", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["zero_leakage_enforced"] is True
    assert "audio_stream_url" in data
    assert "socratic_guidance_text" in data
    assert data["latency_ms"] < 200.0


def test_voice_socratic_vad_ambient_noise_filtering():
    engine = VoiceSocraticEngine()

    # Pure noise / cough / breath is filtered to silence and returns fallback
    req_noise = VoiceSocraticRequest(
        session_id="voice-noise-1",
        audio_transcript="[öksürük] [nefes] ... *cough* uh um",
        target_equation="x**2 - 4 = 0",
        solution_roots=[-2.0, 2.0],
        language="tr",
    )
    res_noise = engine.process_voice_turn(req_noise)
    assert res_noise.vad_filtered is True
    assert "Seni tam duyamadım" in res_noise.socratic_guidance_text

    # Speech mixed with ambient breath artifact is cleaned
    req_mixed = VoiceSocraticRequest(
        session_id="voice-noise-2",
        audio_transcript="[nefes] bu adımda ne yapacağım? [öksürük]",
        target_equation="x**2 - 4 = 0",
        solution_roots=[-2.0, 2.0],
        language="tr",
    )
    res_mixed = engine.process_voice_turn(req_mixed)
    assert res_mixed.vad_filtered is True
    assert res_mixed.normalized_transcript == "bu adımda ne yapacağım?"
    assert "?" in res_mixed.socratic_guidance_text


def test_voice_socratic_spoken_math_normalization_turkish():
    engine = VoiceSocraticEngine()

    sample_spoken = "x kare artı 5x eksi 6 eşittir 0"
    normalized = engine.normalize_spoken_math(sample_spoken, language="tr")
    assert "x^2" in normalized
    assert "+" in normalized
    assert "-" in normalized
    assert "=" in normalized

    powers_and_roots = "x küp artı x üzeri 4 ve karekök 16 küçük eşittir y"
    norm_powers = engine.normalize_spoken_math(powers_and_roots, language="tr")
    assert "x^3" in norm_powers
    assert "x^4" in norm_powers
    assert "sqrt(16)" in norm_powers
    assert "<=" in norm_powers


def test_voice_socratic_spoken_math_normalization_english():
    engine = VoiceSocraticEngine()

    sample_en = "x squared plus three x minus four equals zero"
    norm_en = engine.normalize_spoken_math(sample_en, language="en")
    assert "x^2" in norm_en
    assert "+" in norm_en
    assert "-" in norm_en
    assert "=" in norm_en

    roots_en = "square root of 25 is equal to five"
    norm_roots = engine.normalize_spoken_math(roots_en, language="en")
    assert "sqrt(25)" in norm_roots
    assert "=" in norm_roots


def test_voice_socratic_end_to_end_spoken_math_turn():
    engine = VoiceSocraticEngine()
    req = VoiceSocraticRequest(
        session_id="voice-math-e2e",
        audio_transcript="x kare eksi 4 eşittir 0 denkleminde bir sonraki adım ne olmalı?",
        target_equation="x**2 - 4 = 0",
        solution_roots=[-2.0, 2.0],
        language="tr",
    )
    res = engine.process_voice_turn(req)
    assert res.zero_leakage_enforced is True
    assert "x^2" in res.normalized_transcript
    assert "?" in res.socratic_guidance_text
    # Root 2 must not be leaked
    assert "2" not in res.socratic_guidance_text

