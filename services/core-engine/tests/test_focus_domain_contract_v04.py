import pytest
from pydantic import ValidationError

from app.focus_domain.models import (
    AttemptJudgment,
    BarrierState,
    BranchAssignmentStatus,
    BranchWorkItem,
    BranchWorkSet,
    CompositeTaskFailureCode,
    CompositeTaskState,
    KCId,
    KCState,
)
from app.focus_domain.registry import (
    INTERVENTION_TEMPLATES,
    PROBE_TEMPLATES,
    REPAIR_EDGES,
    validate_focus_registry,
)
from app.focus_domain.rules import apply_valid_shortcut, judge_branch_work


def _branch_work(a_status, b_status):
    return BranchWorkSet(
        branch_items=[
            BranchWorkItem(
                branch_id="A",
                source_factor="x-2",
                expected_equation="x-2=0",
                expected_assignment="x=2",
                assignment_status=a_status,
            ),
            BranchWorkItem(
                branch_id="B",
                source_factor="x+3",
                expected_equation="x+3=0",
                expected_assignment="x=-3",
                assignment_status=b_status,
            ),
        ]
    )


def test_attempt_judgment_has_valid_incomplete():
    assert AttemptJudgment.VALID_INCOMPLETE.value == "VALID_INCOMPLETE"
    assert len(AttemptJudgment) == 7


def test_one_correct_branch_is_valid_incomplete_not_math_error():
    judgment, failure = judge_branch_work(
        _branch_work(BranchAssignmentStatus.VALID, BranchAssignmentStatus.PENDING)
    )
    assert judgment == AttemptJudgment.VALID_INCOMPLETE
    assert failure == CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE


def test_two_correct_branches_complete_expected_stage():
    judgment, failure = judge_branch_work(
        _branch_work(BranchAssignmentStatus.VALID, BranchAssignmentStatus.VALID)
    )
    assert judgment == AttemptJudgment.VALID_EXPECTED
    assert failure is None


def test_invalid_branch_is_invalid_mathematics():
    judgment, failure = judge_branch_work(
        _branch_work(BranchAssignmentStatus.VALID, BranchAssignmentStatus.INVALID)
    )
    assert judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert failure is None


def test_repeated_root_branch_work_is_rejected_by_alpha_model():
    with pytest.raises(ValidationError):
        BranchWorkSet(
            branch_items=[
                BranchWorkItem(
                    branch_id="A",
                    source_factor="x+2",
                    expected_equation="x+2=0",
                    expected_assignment="x=-2",
                ),
                BranchWorkItem(
                    branch_id="B",
                    source_factor="x+2",
                    expected_equation="x+2=0",
                    expected_assignment="x=-2",
                ),
            ]
        )


def test_valid_shortcut_preserves_existing_gap_and_retest():
    result = apply_valid_shortcut(
        existing_kc_states={
            KCId.F2: KCState.RETEST_DUE,
            KCId.Z1: KCState.SUPPORTED_GAP,
        },
        existing_barrier_states={"BH-F2-01": BarrierState.SUPPORTED},
        existing_retest_due={KCId.F2},
    )

    assert result.task_state == CompositeTaskState.COMPLETED_INDEPENDENTLY
    assert result.kc_states[KCId.F2] == KCState.RETEST_DUE
    assert result.kc_states[KCId.Z1] == KCState.SUPPORTED_GAP
    assert result.barrier_states["BH-F2-01"] == BarrierState.SUPPORTED
    assert KCId.F2 in result.retest_due
    assert result.preserved_existing_evidence is True


def test_declared_retest_shortcut_can_only_clear_that_retest_marker():
    result = apply_valid_shortcut(
        existing_kc_states={KCId.F2: KCState.RETEST_DUE},
        existing_barrier_states={"BH-F2-01": BarrierState.SUPPORTED},
        existing_retest_due={KCId.F2, KCId.N1},
        declared_retest_kc=KCId.F2,
        declared_retest_passed=True,
    )

    assert KCId.F2 not in result.retest_due
    assert KCId.N1 in result.retest_due
    # The function intentionally does not invent a new mastery/recovery state.
    assert result.kc_states[KCId.F2] == KCState.RETEST_DUE
    assert result.barrier_states["BH-F2-01"] == BarrierState.SUPPORTED


def test_v04_registry_counts_and_references_are_closed():
    validate_focus_registry()
    assert len(PROBE_TEMPLATES) == 11
    assert len(INTERVENTION_TEMPLATES) == 12


def test_all_n1_repair_edges_use_pr_n1_01():
    edges = [edge for edge in REPAIR_EDGES.values() if edge.to_kc == KCId.N1]
    assert edges
    assert all(edge.preferred_probe_id == "PR-N1-01" for edge in edges)


def test_q0_probe_matches_bounded_additive_equality_microdomain():
    probe = PROBE_TEMPLATES["PR-Q0-01"]
    assert probe.target_kc == KCId.Q0
    assert "x+a=r" in probe.prompt_schema


def test_task_failure_intervention_does_not_require_barrier_state():
    template = INTERVENTION_TEMPLATES["IT-QF1-01"]
    assert template.target_task == "CT-QF1"
    assert CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE in template.eligible_failures
    assert not template.eligible_barriers
