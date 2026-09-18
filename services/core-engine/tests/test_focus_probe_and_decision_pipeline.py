import pytest

from app.focus_domain.decision_pipeline import (
    EpisodePhase,
    FocusDecisionPipeline,
    FocusEpisodeOrchestrator,
    FocusEpisodeState,
    NextActionType,
)
from app.focus_domain.learner_state import LearnerEvidenceSnapshot
from app.focus_domain.models import (
    AttemptJudgment,
    BarrierState,
    KCId,
    KCState,
    ProbeEvidenceKind,
)
from app.focus_domain.probe_evaluator import ProbeResponseEvaluator, UnknownProbeResponse


def test_n1_probe_gap_updates_kc_without_inventing_barrier():
    result = ProbeResponseEvaluator().evaluate(
        snapshot=LearnerEvidenceSnapshot(),
        probe_id="PR-N1-01",
        response_code="SIGN_INVERTED",
    )
    assert result.evidence_kind == ProbeEvidenceKind.GAP
    assert result.snapshot.kc_states[KCId.N1] == KCState.SUPPORTED_GAP
    assert result.specific_barrier_id is None
    assert result.snapshot.barrier_states == {}


def test_unique_barrier_support_updates_barrier_and_kc():
    result = ProbeResponseEvaluator().evaluate(
        snapshot=LearnerEvidenceSnapshot(),
        probe_id="PR-N2-01",
        response_code="EXACT_NEGATIVE",
    )
    assert result.specific_barrier_id == "BH-N2-01"
    assert result.snapshot.kc_states[KCId.N2] == KCState.SUPPORTED_GAP
    assert result.snapshot.barrier_states["BH-N2-01"] == BarrierState.SUPPORTED


def test_multi_candidate_probe_does_not_fake_specific_barrier():
    result = ProbeResponseEvaluator().evaluate(
        snapshot=LearnerEvidenceSnapshot(),
        probe_id="PR-E1-02",
        response_code="NEGATIVE_PRODUCT",
    )
    assert result.specific_barrier_id is None
    assert result.snapshot.kc_states[KCId.E1] == KCState.SUPPORTED_GAP
    assert result.snapshot.barrier_states == {}


def test_q0_positive_probe_adds_q0_passed_flag_without_erasing_evidence():
    snap = LearnerEvidenceSnapshot(kc_states={KCId.Q0: KCState.SUSPECTED_GAP})
    result = ProbeResponseEvaluator().evaluate(
        snapshot=snap,
        probe_id="PR-Q0-01",
        response_code="SAME_OPERATION",
    )
    assert "Q0_PASSED" in result.derived_flags
    assert result.snapshot.kc_states[KCId.Q0] == KCState.SUSPECTED_GAP


def test_n2_positive_probe_marks_n2_alternative_insufficient():
    result = ProbeResponseEvaluator().evaluate(
        snapshot=LearnerEvidenceSnapshot(),
        probe_id="PR-N2-01",
        response_code="CORRECT_POSITIVE",
    )
    assert "N2_ALTERNATIVE_INSUFFICIENT" in result.derived_flags


def test_factor_constraint_subtype_is_preserved_as_attribute():
    result = ProbeResponseEvaluator().evaluate(
        snapshot=LearnerEvidenceSnapshot(),
        probe_id="PR-F2-01",
        response_code="PRODUCT_ONLY",
    )
    assert result.barrier_attributes["ignored_constraint"] == "SUM"
    assert result.specific_barrier_id == "BH-F2-01"


def test_unknown_probe_response_fails_closed():
    with pytest.raises(UnknownProbeResponse):
        ProbeResponseEvaluator().evaluate(
            snapshot=LearnerEvidenceSnapshot(),
            probe_id="PR-N1-01",
            response_code="NOT_A_REAL_CLASS",
        )


def test_invalid_f2_sum_mismatch_probes_active_f2_before_prerequisite_descent():
    state = FocusEpisodeState(workspace_kc=KCId.F2)
    decision = FocusDecisionPipeline().decide_after_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
    )
    assert decision.action == NextActionType.REQUEST_PROBE
    assert decision.probe_id == "PR-F2-01"


def test_direct_f2_probe_support_starts_active_kc_repair():
    orch = FocusEpisodeOrchestrator()
    state = FocusEpisodeState(workspace_kc=KCId.F2)
    state, first = orch.handle_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
    )
    assert first.probe_id == "PR-F2-01"

    applied = orch.apply_probe_response(
        state, probe_id="PR-F2-01", response_code="PRODUCT_ONLY"
    )
    assert applied.decision.action == NextActionType.START_REPAIR
    assert applied.decision.target_kc == KCId.F2
    assert applied.decision.barrier_id == "BH-F2-01"
    assert applied.decision.intervention_id == "IT-F2-01"

    repairing = orch.begin_repair(applied.state, applied.decision)
    assert repairing.learner.kc_states[KCId.F2] == KCState.REPAIRING
    repaired = orch.record_repair_action_success(repairing)
    corrected = orch.record_original_self_correction_success(repaired)
    transferred = orch.record_transfer_result(corrected, success=True)
    assert transferred.learner.kc_states[KCId.F2] == KCState.TEMPORARILY_RECOVERED


def test_fresh_prior_n1_gap_can_drive_prerequisite_repair_after_direct_probe_used():
    state = FocusEpisodeState(
        workspace_kc=KCId.F2,
        learner=LearnerEvidenceSnapshot(kc_states={KCId.N1: KCState.CONFIRMED_GAP}),
        probe_evidence={"PR-F2-01": ProbeEvidenceKind.POSITIVE},
        used_probe_ids={"PR-F2-01"},
        flags={"FRESH_TARGET_GAP_EVIDENCE"},
        probe_budget_remaining=0,
    )
    decision = FocusDecisionPipeline().decide_after_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
    )
    assert decision.action == NextActionType.START_REPAIR
    assert decision.target_kc == KCId.N1
    assert decision.intervention_id == "IT-N1-01"


def test_multiple_eligible_repair_routes_never_use_arbitrary_tiebreak():
    state = FocusEpisodeState(
        workspace_kc=KCId.E1,
        learner=LearnerEvidenceSnapshot(
            kc_states={KCId.N2: KCState.SUPPORTED_GAP, KCId.N3: KCState.SUPPORTED_GAP},
            barrier_states={
                "BH-N2-01": BarrierState.SUPPORTED,
                "BH-N3-01": BarrierState.SUPPORTED,
            },
        ),
        probe_evidence={
            "PR-N2-01": ProbeEvidenceKind.BARRIER_SUPPORT,
            "PR-N3-01": ProbeEvidenceKind.BARRIER_SUPPORT,
        },
        flags={"N2_ALTERNATIVE_INSUFFICIENT"},
        probe_budget_remaining=0,
    )
    decision = FocusDecisionPipeline().decide_after_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-DISTRIBUTION-SIGN-COMPOSITION-WRONG"}),
    )
    assert decision.action == NextActionType.NEUTRAL_SUPPORT
    assert "arbitrary" in decision.reason.lower()


def test_generic_gap_evidence_does_not_authorize_barrier_specific_n2_repair():
    state = FocusEpisodeState(
        workspace_kc=KCId.E1,
        learner=LearnerEvidenceSnapshot(kc_states={KCId.N2: KCState.CONFIRMED_GAP}),
        flags={"FRESH_TARGET_GAP_EVIDENCE"},
        probe_budget_remaining=0,
    )
    decision = FocusDecisionPipeline().decide_after_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-SIGN-WRONG"}),
    )
    assert decision.action == NextActionType.NEUTRAL_SUPPORT
    assert decision.intervention_id == "IT-N2-01"
    assert decision.barrier_id is None


def test_valid_shortcut_completes_task_without_clearing_prior_debt():
    orch = FocusEpisodeOrchestrator()
    state = FocusEpisodeState(
        workspace_kc=KCId.F2,
        learner=LearnerEvidenceSnapshot(
            kc_states={KCId.F2: KCState.RETEST_DUE},
            barrier_states={"BH-F2-01": BarrierState.SUPPORTED},
            retest_due={KCId.F2},
        ),
    )
    state, decision = orch.handle_attempt(
        state,
        judgment=AttemptJudgment.VALID_SHORTCUT,
    )
    assert decision.action == NextActionType.COMPLETE_TASK
    assert state.phase == EpisodePhase.COMPLETED
    assert state.learner.kc_states[KCId.F2] == KCState.RETEST_DUE
    assert KCId.F2 in state.learner.retest_due
    assert state.learner.barrier_states["BH-F2-01"] == BarrierState.SUPPORTED


def test_unsupported_domain_stops_without_diagnosis():
    state, decision = FocusEpisodeOrchestrator().handle_attempt(
        FocusEpisodeState(workspace_kc=KCId.F2),
        judgment=AttemptJudgment.UNSUPPORTED_DOMAIN,
    )
    assert decision.action == NextActionType.FAIL_CLOSED
    assert state.phase == EpisodePhase.STOPPED
    assert state.learner.kc_states == {}


def test_probe_response_must_match_pending_probe():
    orch = FocusEpisodeOrchestrator()
    state = FocusEpisodeState(
        workspace_kc=KCId.F2,
        phase=EpisodePhase.PROBING,
        pending_probe_id="PR-N1-01",
    )
    with pytest.raises(ValueError):
        orch.apply_probe_response(
            state,
            probe_id="PR-N2-01",
            response_code="CORRECT_POSITIVE",
        )


def test_repair_order_cannot_skip_original_self_correction():
    orch = FocusEpisodeOrchestrator()
    state = FocusEpisodeState(
        workspace_kc=KCId.F2,
        phase=EpisodePhase.REPAIRING,
        repair_kc=KCId.N1,
        repair_edge_id="RE-F2-N1",
        repair_intervention_id="IT-N1-01",
        learner=LearnerEvidenceSnapshot(kc_states={KCId.N1: KCState.REPAIRING}),
    )
    with pytest.raises(ValueError):
        orch.record_transfer_result(state, success=True)



def test_active_n1_gap_uses_barrier_free_direct_repair_after_probe():
    orch = FocusEpisodeOrchestrator()
    state = FocusEpisodeState(workspace_kc=KCId.N1)
    state, first = orch.handle_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-SIGNED-SUM-WRONG"}),
    )
    assert first.action == NextActionType.REQUEST_PROBE
    assert first.probe_id == "PR-N1-01"

    applied = orch.apply_probe_response(
        state, probe_id="PR-N1-01", response_code="SIGN_INVERTED"
    )
    assert applied.decision.action == NextActionType.START_REPAIR
    assert applied.decision.target_kc == KCId.N1
    assert applied.decision.barrier_id is None
    assert applied.decision.intervention_id == "IT-N1-01"


def test_positive_direct_probe_does_not_repeat_same_probe_when_budget_is_spent():
    orch = FocusEpisodeOrchestrator()
    state = FocusEpisodeState(workspace_kc=KCId.F2)
    state, _ = orch.handle_attempt(
        state,
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
    )
    applied = orch.apply_probe_response(
        state, probe_id="PR-F2-01", response_code="BOTH"
    )
    assert applied.state.probe_budget_remaining == 0
    assert applied.decision.action in {NextActionType.CLEAN_STOP, NextActionType.NEUTRAL_SUPPORT}
    assert applied.decision.probe_id is None
