import pytest
from app.affect.cognitive_hesitation_sensor import CognitiveHesitationSensor, HesitationSignal


def test_no_hesitation_below_threshold():
    signal = CognitiveHesitationSensor.evaluate_hesitation(
        elapsed_ms=5000.0,
        current_input="",
        target_equation="2x + 4 = 10",
    )
    assert signal.is_hesitating is False
    assert signal.whisper_message is None
    assert signal.confidence == 0.0


def test_hesitation_triggered_empty_input():
    signal = CognitiveHesitationSensor.evaluate_hesitation(
        elapsed_ms=9500.0,
        current_input="",
        target_equation="2x + 4 = 10",
    )
    assert signal.is_hesitating is True
    assert signal.whisper_message is not None
    assert "karşıya geçirmeye" in signal.whisper_message
    assert signal.confidence >= 0.6


def test_contextual_whisper_parenthesis():
    signal = CognitiveHesitationSensor.evaluate_hesitation(
        elapsed_ms=12000.0,
        current_input="",
        target_equation="3(x + 4) = 18",
    )
    assert signal.is_hesitating is True
    assert "parantezin önündeki" in signal.whisper_message


def test_active_typing_suppresses_hesitation():
    signal = CognitiveHesitationSensor.evaluate_hesitation(
        elapsed_ms=15000.0,
        current_input="3x",
        target_equation="3(x + 4) = 18",
    )
    assert signal.is_hesitating is False
    assert signal.whisper_message is None
    assert signal.confidence == 0.0


def test_confidence_scales_with_elapsed_time():
    sig1 = CognitiveHesitationSensor.evaluate_hesitation(
        elapsed_ms=8500.0,
        current_input="",
        target_equation="x = 5",
    )
    sig2 = CognitiveHesitationSensor.evaluate_hesitation(
        elapsed_ms=18500.0,
        current_input="",
        target_equation="x = 5",
    )
    assert sig2.confidence > sig1.confidence
    assert sig2.confidence <= 1.0
