import pytest
from app.affect.detector import (
    AffectiveStateDetector,
    BehaviorObservation,
    AffectiveState,
)


@pytest.fixture
def detector():
    return AffectiveStateDetector(baseline_rt_ms=25000.0)


def test_flow_state_on_consistent_success(detector):
    # Student answers correctly at fluent pace
    obs = BehaviorObservation(
        response_time_ms=18000.0,
        is_correct=True,
        thrash_events_count=0,
        consecutive_errors=0,
    )
    assessment = detector.evaluate_telemetry(obs)
    assert assessment.primary_state in (AffectiveState.FLOW, AffectiveState.DELIGHT)
    assert assessment.frustration_score < 0.20
    assert assessment.is_circuit_breaker_tripped is False
    assert assessment.quarantine_active is False


def test_freezing_latency_detection(detector):
    # Student freezes for 95 seconds without action
    obs = BehaviorObservation(
        response_time_ms=95000.0,
        is_correct=False,
        thrash_events_count=0,
        consecutive_errors=1,
    )
    assessment = detector.evaluate_telemetry(obs)
    assert assessment.is_freezing_detected is True
    assert assessment.intervention_title == "Düşünce Molası"


def test_rapid_guessing_impulsive_slip(detector):
    # Impulsive response under 3.5s
    obs = BehaviorObservation(
        response_time_ms=2100.0,
        is_correct=False,
        thrash_events_count=0,
        consecutive_errors=1,
    )
    assessment = detector.evaluate_telemetry(obs)
    assert assessment.is_rapid_guessing_detected is True
    assert assessment.intervention_title == "Sezgi Freni"


def test_rage_clicks_thrashing_circuit_breaker_trip(detector):
    # Rage clicks: 5 rapid frustrated clicks
    obs = BehaviorObservation(
        response_time_ms=2500.0,
        is_correct=False,
        thrash_events_count=5,
        consecutive_errors=2,
    )
    assessment = detector.evaluate_telemetry(obs)
    assert assessment.frustration_score >= 0.85
    assert assessment.is_circuit_breaker_tripped is True
    assert assessment.quarantine_active is True
    assert assessment.pivot_to_worked_example is True
    assert assessment.intervention_title == "Bir Nefes Verelim"
    assert "Yalnız değilsin" in assessment.intervention_message


def test_despair_nlp_trigger_circuit_breaker_trip(detector):
    obs = BehaviorObservation(
        response_time_ms=15000.0,
        is_correct=False,
        consecutive_errors=2,
        input_text="olmuyor hocam anlamıyorum bir türlü",
    )
    assessment = detector.evaluate_telemetry(obs)
    assert assessment.frustration_score >= 0.85
    assert assessment.is_circuit_breaker_tripped is True
    assert assessment.quarantine_active is True
    assert assessment.pivot_to_worked_example is True
