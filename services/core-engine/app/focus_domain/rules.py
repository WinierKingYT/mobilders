from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional, Set

from .models import (
    AttemptJudgment,
    BarrierState,
    BranchAssignmentStatus,
    BranchWorkSet,
    CompositeTaskFailureCode,
    CompositeTaskState,
    KCId,
    KCState,
    ShortcutEvidenceResult,
)


def judge_branch_work(
    branch_work: BranchWorkSet,
) -> tuple[AttemptJudgment, Optional[CompositeTaskFailureCode]]:
    """Judge CT-QF1 S3 branch completeness without conflating validity with completeness."""

    statuses = [item.assignment_status for item in branch_work.branch_items]

    if all(status == BranchAssignmentStatus.VALID for status in statuses):
        return AttemptJudgment.VALID_EXPECTED, None

    if any(status == BranchAssignmentStatus.INVALID for status in statuses):
        return AttemptJudgment.INVALID_MATHEMATICS, None

    if any(status == BranchAssignmentStatus.UNSUPPORTED for status in statuses):
        return AttemptJudgment.UNSUPPORTED_STEP_FORM, None

    valid_count = sum(
        status == BranchAssignmentStatus.VALID for status in statuses
    )
    pending_count = sum(
        status == BranchAssignmentStatus.PENDING for status in statuses
    )

    if valid_count >= 1 and pending_count >= 1:
        return (
            AttemptJudgment.VALID_INCOMPLETE,
            CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE,
        )

    # No branch has supplied mathematical work yet. This is task-incomplete,
    # but not enough to call the submission mathematically invalid.
    return (
        AttemptJudgment.VALID_INCOMPLETE,
        CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE,
    )


def apply_valid_shortcut(
    *,
    existing_kc_states: Mapping[KCId, KCState],
    existing_barrier_states: Mapping[str, BarrierState],
    existing_retest_due: Iterable[KCId] = (),
    declared_retest_kc: Optional[KCId] = None,
    declared_retest_passed: bool = False,
) -> ShortcutEvidenceResult:
    """Apply v0.4 VALID_SHORTCUT semantics.

    A correct final/later-stage answer may complete the composite task but
    does not erase debt for bypassed KCs. Only a shortcut explicitly declared
    as a retest for a specific KC may satisfy that one retest, and this function
    still does not invent DURABLE_EVIDENCE; the caller must apply the retest
    evidence contract separately.
    """

    kc_states: Dict[KCId, KCState] = dict(existing_kc_states)
    barrier_states: Dict[str, BarrierState] = dict(existing_barrier_states)
    retest_due: Set[KCId] = set(existing_retest_due)

    if declared_retest_kc is not None and declared_retest_passed:
        retest_due.discard(declared_retest_kc)

    return ShortcutEvidenceResult(
        task_state=CompositeTaskState.COMPLETED_INDEPENDENTLY,
        kc_states=kc_states,
        barrier_states=barrier_states,
        retest_due=retest_due,
        preserved_existing_evidence=True,
    )
