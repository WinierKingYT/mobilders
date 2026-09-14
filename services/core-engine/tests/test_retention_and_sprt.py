"""
Tests for Wald SPRT Mastery Gate, FSRS-4.5 Memory Engine, and Part-Whole Nilpotent DAG Propagation.
"""

import pytest
import numpy as np
from app.psychometrics.sprt import WaldSPRT, MasteryDecision
from app.retention.fsrs import FSRSEngine, Rating, DSRState
from app.retention.propagation import PartWholePropagator
from app.graph.knowledge_dag import KnowledgeDAG


# ==========================================
# 1. WALD SPRT TESTS
# ==========================================

def test_wald_sprt_mastery_confirmed_on_consistent_success():
    """Verify that consistent correct responses cross ln(A) and confirm mastery."""
    sprt = WaldSPRT(p0=0.60, p1=0.88, alpha=0.05, beta=0.10)

    # 8 consecutive correct steps
    responses = [True] * 8
    result = sprt.evaluate(responses)

    assert result.decision == MasteryDecision.MASTERY_CONFIRMED
    assert result.is_terminal is True
    assert result.cumulative_llr >= result.upper_threshold_ln_a
    assert result.trials_count == 8
    assert result.correct_count == 8


def test_wald_sprt_remediation_on_consistent_errors():
    """Verify that early consecutive errors cross ln(B) and halt testing for remediation."""
    sprt = WaldSPRT(p0=0.60, p1=0.88, alpha=0.05, beta=0.10)

    # 2 consecutive errors: 2 * -1.204 = -2.408 < ln(B) (-2.251)
    responses = [False, False]
    result = sprt.evaluate(responses)

    assert result.decision == MasteryDecision.NEEDS_REMEDIATION
    assert result.is_terminal is True
    assert result.cumulative_llr <= result.lower_threshold_ln_b


def test_wald_sprt_continue_sampling():
    """Verify that alternating/uncertain responses stay in indifference zone."""
    sprt = WaldSPRT(p0=0.60, p1=0.88, alpha=0.05, beta=0.10)

    # 3 correct, 1 wrong
    responses = [True, True, False, True]
    result = sprt.evaluate(responses)

    assert result.decision == MasteryDecision.CONTINUE_SAMPLING
    assert result.is_terminal is False
    assert result.lower_threshold_ln_b < result.cumulative_llr < result.upper_threshold_ln_a


def test_wald_sprt_truncation_at_max_trials():
    """Verify that reaching max_trials (12) terminates with truncated decision."""
    sprt = WaldSPRT(p0=0.60, p1=0.88, max_trials=12)

    # 10 correct, 2 incorrect: LLR stays strictly between ln(B) and ln(A), ending at ~+1.42 > 0
    responses = [True, True, True, True, False, True, True, True, False, True, True, True]
    assert len(responses) == 12

    result = sprt.evaluate(responses)
    assert result.is_terminal is True
    assert result.trials_count == 12
    assert result.cumulative_llr > 0.0
    # Since LLR > 0, truncated rule yields CONDITIONAL_MASTERY
    assert result.decision == MasteryDecision.CONDITIONAL_MASTERY


# ==========================================
# 2. FSRS-4.5 DSR TESTS
# ==========================================

def test_fsrs_initial_state_and_retrievability():
    """Verify initial DSR states for different ratings and power-law retrievability."""
    fsrs = FSRSEngine()

    # Good rating initial state
    good_state = fsrs.init_dsr(Rating.GOOD)
    assert good_state.stability == 2.3  # w2
    assert 1.0 <= good_state.difficulty <= 10.0
    assert good_state.retrievability == 1.0

    # Easy rating has higher initial stability
    easy_state = fsrs.init_dsr(Rating.EASY)
    assert easy_state.stability == 10.9  # w3
    assert easy_state.stability > good_state.stability

    # Retrievability at elapsed t = Stability should be ~0.90 (90%)
    r_at_s = fsrs.retrievability(elapsed_days=good_state.stability, stability=good_state.stability)
    assert 0.89 <= r_at_s <= 0.91

    # Retrievability decays as days increase
    r_after_10d = fsrs.retrievability(elapsed_days=10.0, stability=good_state.stability)
    assert r_after_10d < r_at_s


def test_fsrs_circadian_sleep_barrier():
    """Verify that reviews under 14 hours do NOT increase stability (Walker & Stickgold)."""
    fsrs = FSRSEngine()
    initial_state = fsrs.init_dsr(Rating.GOOD)
    initial_s = initial_state.stability

    # Review after 4 hours (0.166 days) with GOOD rating
    elapsed_4h = 4.0 / 24.0
    same_day_review = fsrs.review(initial_state, Rating.GOOD, elapsed_days=elapsed_4h)

    # Stability must NOT increase without sleep consolidation
    assert same_day_review.stability == initial_s

    # Review after 24 hours (1.0 day > 14h) with GOOD rating
    next_day_review = fsrs.review(initial_state, Rating.GOOD, elapsed_days=1.0)
    assert next_day_review.stability > initial_s


def test_fsrs_session_fatigue_discount():
    """Verify that sessions exceeding 15 minutes apply fatigue discount."""
    fsrs = FSRSEngine()
    initial_state = fsrs.init_dsr(Rating.GOOD)

    # Review at 24h with normal 10 min session
    normal_review = fsrs.review(
        initial_state, Rating.GOOD, elapsed_days=1.0, session_duration_minutes=10.0
    )

    # Review at 24h with fatigued 25 min session
    fatigued_review = fsrs.review(
        initial_state, Rating.GOOD, elapsed_days=1.0, session_duration_minutes=25.0
    )

    # Fatigued session stability must be discounted
    assert fatigued_review.stability < normal_review.stability


# ==========================================
# 3. PART-WHOLE PROPAGATION MATRIX TESTS
# ==========================================

def test_part_whole_propagation_nilpotent_matrix():
    """Verify analytical propagation matrix P = (I - gamma * A)^(-1)."""
    dag = KnowledgeDAG()
    propagator = PartWholePropagator(dag=dag, gamma=0.80)

    # Matrix shape must be 20x20
    assert propagator.p_matrix.shape == (20, 20)

    # Diagonal elements must all be 1.0 (direct node receives full 100% of impulse)
    for i in range(20):
        assert np.isclose(propagator.p_matrix[i, i], 1.0)

    # Root node N01 has no prerequisites: its column must have 1.0 at N01 and 0 elsewhere
    n01_weights = propagator.get_propagation_weights("N01")
    assert n01_weights == {"N01": 1.0}

    # Complex node N15 (Completing the Square) must propagate to ancestors
    n15_weights = propagator.get_propagation_weights("N15")
    assert n15_weights["N15"] == 1.0
    # Must propagate to direct prerequisites N14 and N13
    assert "N14" in n15_weights and n15_weights["N14"] > 0
    assert "N13" in n15_weights and n15_weights["N13"] > 0
    # Must propagate to root ancestor N01
    assert "N01" in n15_weights and n15_weights["N01"] > 0

    # Verify stability propagation update
    current_stabilities = {nid: 2.0 for nid in dag.nodes.keys()}
    updated = propagator.propagate_stability_increment(
        target_node_id="N15",
        delta_stability=3.0,
        current_stabilities=current_stabilities,
    )

    # N15 increases by full 3.0: 2.0 + 3.0 = 5.0
    assert np.isclose(updated["N15"], 5.0)
    # Ancestor N01 also increased due to propagation
    assert updated["N01"] > current_stabilities["N01"]
    assert updated["N01"] < updated["N15"]  # Discounted decay
