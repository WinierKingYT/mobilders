import pytest

from app.focus_domain.learner_state import (
    InvalidLearnerStateTransition,
    LearnerEvidenceEvent,
    LearnerEvidenceEventType,
    LearnerEvidenceSnapshot,
    LearnerStateTransitionService,
)
from app.focus_domain.models import (
    AttemptJudgment,
    BarrierState,
    KCId,
    KCState,
    ProbeEvidenceKind,
)
from app.focus_domain.observations import (
    ErrorObservationCode,
    ErrorObservationProducer,
)
from app.focus_domain.repair_evaluator import (
    RepairEdgeEligibilityEvaluator,
    RepairEligibilityStatus,
    RepairEvidenceContext,
)
from app.focus_domain.registry import REPAIR_EDGES, validate_focus_registry
from app.focus_domain.truth_adapter import (
    AlphaQuadraticTaskSpec,
    AlphaTruthAdapter,
    TruthFactCode,
)


def test_generated_ctqf1_spec_is_deterministic_and_supports_difference_of_squares():
    spec = AlphaQuadraticTaskSpec(m=3, n=-3)
    assert spec.b == 0
    assert spec.c == -9
    assert spec.factor_pair == (-3, 3)
    assert spec.branch_equations == frozenset({"x+3=0", "x-3=0"})
    assert spec.roots == frozenset({-3, 3})
    assert spec.polynomial == "x^2-9=0"


def test_generated_ctqf1_spec_rejects_zero_repeated_and_out_of_generation_bound():
    with pytest.raises(ValueError):
        AlphaQuadraticTaskSpec(m=0, n=3)
    with pytest.raises(ValueError):
        AlphaQuadraticTaskSpec(m=2, n=2)
    with pytest.raises(ValueError):
        AlphaQuadraticTaskSpec(m=7, n=-2)


def test_truth_factor_pair_separates_sum_and_product_constraint_failures():
    truth = AlphaTruthAdapter()

    product_only = truth.check_factor_pair(b=5, c=6, pair=(1, 6))
    assert product_only.is_valid is False
    assert product_only.facts == frozenset({TruthFactCode.FACTOR_PAIR_SUM_MISMATCH})

    sum_only = truth.check_factor_pair(b=5, c=6, pair=(2, 3))
    assert sum_only.is_valid is True
    assert sum_only.facts == frozenset()

    neither = truth.check_factor_pair(b=5, c=6, pair=(1, 5))
    assert neither.facts == frozenset({
        TruthFactCode.FACTOR_PAIR_SUM_MISMATCH,
        TruthFactCode.FACTOR_PAIR_PRODUCT_MISMATCH,
    })


def test_truth_signed_multiplication_only_labels_sign_fact_when_magnitude_matches():
    truth = AlphaTruthAdapter()
    sign_error = truth.check_signed_multiplication(-3, -2, -6)
    assert sign_error.facts == frozenset({TruthFactCode.SIGN_WRONG})

    magnitude_error = truth.check_signed_multiplication(-3, -2, 5)
    assert magnitude_error.is_valid is False
    assert magnitude_error.facts == frozenset()


def test_truth_distribution_can_emit_partial_and_sign_composition_facts():
    truth = AlphaTruthAdapter()

    partial = truth.check_distribution(
        outside=3,
        inner_constant=2,
        observed_x_coefficient=3,
        observed_constant=2,
    )
    assert TruthFactCode.PARTIAL_DISTRIBUTION in partial.facts

    sign = truth.check_distribution(
        outside=-3,
        inner_constant=-2,
        observed_x_coefficient=-3,
        observed_constant=-6,
    )
    assert TruthFactCode.DISTRIBUTION_SIGN_COMPOSITION_WRONG in sign.facts
    assert TruthFactCode.SIGN_WRONG in sign.facts


def test_error_observation_producer_never_turns_valid_incomplete_into_math_error():
    truth = AlphaTruthAdapter().check_factor_pair(b=5, c=6, pair=(1, 6))
    producer = ErrorObservationProducer()

    observations = producer.produce(
        attempt_judgment=AttemptJudgment.VALID_INCOMPLETE,
        truth_result=truth,
        attempt_id="a1",
    )
    assert observations == ()


def test_error_observation_producer_maps_invalid_truth_facts_only():
    truth = AlphaTruthAdapter().check_factor_pair(b=5, c=6, pair=(1, 6))
    producer = ErrorObservationProducer()

    observations = producer.produce(
        attempt_judgment=AttemptJudgment.INVALID_MATHEMATICS,
        truth_result=truth,
        attempt_id="a2",
    )
    assert [obs.code for obs in observations] == [ErrorObservationCode.FACTOR_PAIR_SUM_MISMATCH]
    assert observations[0].target_kc == KCId.F2


def test_repair_edge_requires_matching_active_kc_and_observation():
    evaluator = RepairEdgeEligibilityEvaluator()
    edge = REPAIR_EDGES["RE-F2-N1"]

    wrong_kc = evaluator.evaluate(
        edge,
        RepairEvidenceContext(
            active_kc=KCId.F1,
            observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
        ),
    )
    assert wrong_kc.status == RepairEligibilityStatus.INELIGIBLE_ACTIVE_KC

    no_observation = evaluator.evaluate(
        edge,
        RepairEvidenceContext(active_kc=KCId.F2),
    )
    assert no_observation.status == RepairEligibilityStatus.INELIGIBLE_OBSERVATION


def test_repair_edge_requests_probe_when_evidence_missing_and_budget_available():
    evaluator = RepairEdgeEligibilityEvaluator()
    result = evaluator.evaluate_edge_id(
        "RE-F2-N1",
        RepairEvidenceContext(
            active_kc=KCId.F2,
            observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
            probe_budget_remaining=1,
        ),
    )
    assert result.status == RepairEligibilityStatus.NEEDS_PROBE
    assert result.recommended_probe_id == "PR-N1-01"


def test_repair_edge_blocks_when_probe_budget_exhausted():
    evaluator = RepairEdgeEligibilityEvaluator()
    result = evaluator.evaluate_edge_id(
        "RE-F2-N1",
        RepairEvidenceContext(
            active_kc=KCId.F2,
            observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
            probe_budget_remaining=0,
        ),
    )
    assert result.status == RepairEligibilityStatus.BLOCKED_PROBE_BUDGET
    assert result.fallback_action == "IT-F2-01"


def test_repair_edge_becomes_eligible_from_registered_probe_evidence():
    evaluator = RepairEdgeEligibilityEvaluator()
    result = evaluator.evaluate_edge_id(
        "RE-F2-N1",
        RepairEvidenceContext(
            active_kc=KCId.F2,
            observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
            probe_evidence={"PR-N1-01": ProbeEvidenceKind.GAP},
        ),
    )
    assert result.status == RepairEligibilityStatus.ELIGIBLE


def test_prior_gap_state_only_counts_when_explicitly_fresh():
    evaluator = RepairEdgeEligibilityEvaluator()
    base = dict(
        active_kc=KCId.F2,
        observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
        kc_states={KCId.N1: KCState.CONFIRMED_GAP},
    )

    stale = evaluator.evaluate_edge_id("RE-F2-N1", RepairEvidenceContext(**base))
    assert stale.status == RepairEligibilityStatus.BLOCKED_PROBE_BUDGET

    fresh = evaluator.evaluate_edge_id(
        "RE-F2-N1",
        RepairEvidenceContext(**base, flags=frozenset({"FRESH_TARGET_GAP_EVIDENCE"})),
    )
    assert fresh.status == RepairEligibilityStatus.ELIGIBLE


def test_recent_transfer_disqualifies_prior_gap_route():
    evaluator = RepairEdgeEligibilityEvaluator()
    result = evaluator.evaluate_edge_id(
        "RE-F2-N1",
        RepairEvidenceContext(
            active_kc=KCId.F2,
            observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
            kc_states={KCId.N1: KCState.CONFIRMED_GAP},
            flags=frozenset({
                "FRESH_TARGET_GAP_EVIDENCE",
                "RECENT_KC_N1_TRANSFER_SUCCESS",
            }),
        ),
    )
    assert result.status == RepairEligibilityStatus.DISQUALIFIED


def test_q1_to_n3_requires_q0_pass_context_even_with_n3_probe_support():
    evaluator = RepairEdgeEligibilityEvaluator()
    base = RepairEvidenceContext(
        active_kc=KCId.Q1,
        observations=frozenset({"EO-SIMPLE-ROOT-SIGN-WRONG"}),
        probe_evidence={"PR-N3-01": ProbeEvidenceKind.BARRIER_SUPPORT},
    )
    missing = evaluator.evaluate_edge_id("RE-Q1-N3", base)
    assert missing.status == RepairEligibilityStatus.MISSING_REQUIRED_CONTEXT

    eligible = evaluator.evaluate_edge_id(
        "RE-Q1-N3",
        base.model_copy(update={"flags": frozenset({"Q0_PASSED"})}),
    )
    assert eligible.status == RepairEligibilityStatus.ELIGIBLE


def test_repair_success_and_original_self_correction_do_not_create_recovery():
    service = LearnerStateTransitionService()
    snap = LearnerEvidenceSnapshot(
        kc_states={KCId.F2: KCState.CONFIRMED_GAP},
        barrier_states={"BH-F2-01": BarrierState.CONFIRMED},
    )

    started = service.apply(
        snap,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.REPAIR_STARTED,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
        ),
    ).snapshot
    assert started.kc_states[KCId.F2] == KCState.REPAIRING
    assert started.barrier_states["BH-F2-01"] == BarrierState.REPAIRING

    repaired = service.apply(
        started,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.REPAIR_ACTION_SUCCESS,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
        ),
    )
    assert repaired.changed is False
    assert repaired.snapshot.kc_states[KCId.F2] == KCState.REPAIRING

    self_corrected = service.apply(
        repaired.snapshot,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.ORIGINAL_SELF_CORRECTION_SUCCESS,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
        ),
    )
    assert self_corrected.changed is False
    assert self_corrected.snapshot.kc_states[KCId.F2] == KCState.REPAIRING


def test_transfer_then_delayed_retest_is_required_for_durable_evidence():
    service = LearnerStateTransitionService()
    repairing = LearnerEvidenceSnapshot(
        kc_states={KCId.F2: KCState.REPAIRING},
        barrier_states={"BH-F2-01": BarrierState.REPAIRING},
    )

    transfer = service.apply(
        repairing,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.TRANSFER_SUCCESS,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
        ),
    ).snapshot
    assert transfer.kc_states[KCId.F2] == KCState.TEMPORARILY_RECOVERED
    assert transfer.barrier_states["BH-F2-01"] == BarrierState.TEMPORARILY_RECOVERED

    due = service.apply(
        transfer,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.RETEST_SCHEDULED,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
        ),
    ).snapshot
    assert due.kc_states[KCId.F2] == KCState.RETEST_DUE
    assert KCId.F2 in due.retest_due

    durable = service.apply(
        due,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.DELAYED_RETEST_SUCCESS,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
        ),
    ).snapshot
    assert durable.kc_states[KCId.F2] == KCState.DURABLE_EVIDENCE
    assert durable.barrier_states["BH-F2-01"] == BarrierState.DURABLE_EVIDENCE
    assert KCId.F2 not in durable.retest_due


def test_transfer_failure_restores_prior_gap_evidence_instead_of_recovery():
    service = LearnerStateTransitionService()
    repairing = LearnerEvidenceSnapshot(
        kc_states={KCId.F2: KCState.REPAIRING},
        barrier_states={"BH-F2-01": BarrierState.REPAIRING},
    )

    failed = service.apply(
        repairing,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.TRANSFER_FAILURE,
            target_kc=KCId.F2,
            barrier_id="BH-F2-01",
            prior_gap_state=KCState.CONFIRMED_GAP,
            prior_barrier_state=BarrierState.CONFIRMED,
        ),
    ).snapshot

    assert failed.kc_states[KCId.F2] == KCState.CONFIRMED_GAP
    assert failed.barrier_states["BH-F2-01"] == BarrierState.CONFIRMED


def test_delayed_retest_cannot_jump_from_unknown_to_durable():
    service = LearnerStateTransitionService()
    with pytest.raises(InvalidLearnerStateTransition):
        service.apply(
            LearnerEvidenceSnapshot(),
            LearnerEvidenceEvent(
                event_type=LearnerEvidenceEventType.DELAYED_RETEST_SUCCESS,
                target_kc=KCId.F2,
            ),
        )


def test_unknown_invalid_math_is_preserved_without_fake_specific_diagnosis():
    truth = AlphaTruthAdapter().check_signed_multiplication(-3, -2, 5)
    observations = ErrorObservationProducer().produce(
        attempt_judgment=AttemptJudgment.INVALID_MATHEMATICS,
        truth_result=truth,
        attempt_id="a-unknown",
    )
    assert len(observations) == 1
    assert observations[0].code == ErrorObservationCode.UNKNOWN_INVALID_STEP
    assert observations[0].source_fact is None


def test_weaker_gap_event_cannot_downgrade_confirmed_state():
    service = LearnerStateTransitionService()
    snapshot = LearnerEvidenceSnapshot(kc_states={KCId.F2: KCState.CONFIRMED_GAP})
    result = service.apply(
        snapshot,
        LearnerEvidenceEvent(
            event_type=LearnerEvidenceEventType.GAP_SUPPORTED,
            target_kc=KCId.F2,
        ),
    )
    assert result.changed is False
    assert result.snapshot.kc_states[KCId.F2] == KCState.CONFIRMED_GAP


def test_repair_cannot_start_merely_because_retest_is_due():
    service = LearnerStateTransitionService()
    snapshot = LearnerEvidenceSnapshot(kc_states={KCId.F2: KCState.RETEST_DUE})
    with pytest.raises(InvalidLearnerStateTransition):
        service.apply(
            snapshot,
            LearnerEvidenceEvent(
                event_type=LearnerEvidenceEventType.REPAIR_STARTED,
                target_kc=KCId.F2,
            ),
        )


def test_registry_structured_repair_policies_are_closed():
    validate_focus_registry()
    for edge in REPAIR_EDGES.values():
        assert edge.evidence_policy is not None
        assert edge.entry_intervention_ids
        for probe_id in edge.evidence_policy.accepted_probe_evidence:
            assert probe_id.startswith("PR-")


def test_all_n1_repair_routes_have_executable_n1_intervention():
    n1_edges = [edge for edge in REPAIR_EDGES.values() if edge.to_kc == KCId.N1]
    assert n1_edges
    assert all("IT-N1-01" in edge.entry_intervention_ids for edge in n1_edges)
