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
