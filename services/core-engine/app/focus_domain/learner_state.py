from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Set

from pydantic import BaseModel, Field

from .models import BarrierState, KCId, KCState


class LearnerEvidenceEventType(str, Enum):
    GAP_SUPPORTED = "GAP_SUPPORTED"
    GAP_CONFIRMED = "GAP_CONFIRMED"
    BARRIER_SUPPORTED = "BARRIER_SUPPORTED"
    BARRIER_CONFIRMED = "BARRIER_CONFIRMED"
    REPAIR_STARTED = "REPAIR_STARTED"
    REPAIR_ACTION_SUCCESS = "REPAIR_ACTION_SUCCESS"
    ORIGINAL_SELF_CORRECTION_SUCCESS = "ORIGINAL_SELF_CORRECTION_SUCCESS"
    TRANSFER_SUCCESS = "TRANSFER_SUCCESS"
    TRANSFER_FAILURE = "TRANSFER_FAILURE"
    RETEST_SCHEDULED = "RETEST_SCHEDULED"
    DELAYED_RETEST_SUCCESS = "DELAYED_RETEST_SUCCESS"
    DELAYED_RETEST_FAILURE = "DELAYED_RETEST_FAILURE"


class LearnerEvidenceSnapshot(BaseModel):
    kc_states: Dict[KCId, KCState] = Field(default_factory=dict)
    barrier_states: Dict[str, BarrierState] = Field(default_factory=dict)
    retest_due: Set[KCId] = Field(default_factory=set)


class LearnerEvidenceEvent(BaseModel):
    event_type: LearnerEvidenceEventType
    target_kc: KCId
    barrier_id: Optional[str] = None
    # Needed to restore evidence after a failed repair/transfer without
    # pretending we know more or less than before repair started.
    prior_gap_state: Optional[KCState] = None
    prior_barrier_state: Optional[BarrierState] = None


class LearnerStateTransitionResult(BaseModel):
    snapshot: LearnerEvidenceSnapshot
    changed: bool
    reason: str


class InvalidLearnerStateTransition(ValueError):
    pass


_STRONGER_THAN_SUPPORTED_GAP = {
    KCState.CONFIRMED_GAP,
    KCState.REPAIRING,
    KCState.TEMPORARILY_RECOVERED,
    KCState.RETEST_DUE,
    KCState.RELAPSED,
    KCState.DURABLE_EVIDENCE,
}

_STRONGER_THAN_BARRIER_SUPPORTED = {
    BarrierState.CONFIRMED,
    BarrierState.REPAIRING,
    BarrierState.TEMPORARILY_RECOVERED,
    BarrierState.RETEST_DUE,
    BarrierState.RELAPSED,
    BarrierState.DURABLE_EVIDENCE,
}


class LearnerStateTransitionService:
    """Pure evidence-state transitions for frozen Focus recovery semantics."""

    def apply(
        self,
        snapshot: LearnerEvidenceSnapshot,
        event: LearnerEvidenceEvent,
    ) -> LearnerStateTransitionResult:
        next_snapshot = snapshot.model_copy(deep=True)
        kc = event.target_kc
        current = next_snapshot.kc_states.get(kc, KCState.UNKNOWN)
        barrier_current = (
            next_snapshot.barrier_states.get(event.barrier_id, BarrierState.UNSEEN)
            if event.barrier_id
            else None
        )

        t = event.event_type

        if t == LearnerEvidenceEventType.GAP_SUPPORTED:
            if current in _STRONGER_THAN_SUPPORTED_GAP:
                return LearnerStateTransitionResult(
                    snapshot=next_snapshot,
                    changed=False,
                    reason="Weaker supported-gap evidence cannot downgrade a stronger KC state.",
                )
            next_snapshot.kc_states[kc] = KCState.SUPPORTED_GAP
            return self._done(snapshot, next_snapshot, "KC gap is supported by evidence.")

        if t == LearnerEvidenceEventType.GAP_CONFIRMED:
            if current == KCState.CONFIRMED_GAP:
                return LearnerStateTransitionResult(
                    snapshot=next_snapshot, changed=False, reason="KC gap is already confirmed."
                )
            if current in {
                KCState.REPAIRING, KCState.TEMPORARILY_RECOVERED, KCState.RETEST_DUE,
                KCState.RELAPSED, KCState.DURABLE_EVIDENCE
            }:
                raise InvalidLearnerStateTransition(
                    f"Stale GAP_CONFIRMED cannot overwrite advanced KC state {current}"
                )
            next_snapshot.kc_states[kc] = KCState.CONFIRMED_GAP
            return self._done(snapshot, next_snapshot, "KC gap is confirmed by discriminating evidence.")

        if t == LearnerEvidenceEventType.BARRIER_SUPPORTED:
            if not event.barrier_id:
                raise InvalidLearnerStateTransition("BARRIER_SUPPORTED requires barrier_id")
            if barrier_current not in _STRONGER_THAN_BARRIER_SUPPORTED:
                next_snapshot.barrier_states[event.barrier_id] = BarrierState.SUPPORTED
            if current in {KCState.UNKNOWN, KCState.EVIDENCE_SPARSE, KCState.LOOKS_STABLE, KCState.SUSPECTED_GAP}:
                next_snapshot.kc_states[kc] = KCState.SUPPORTED_GAP
            return self._done(snapshot, next_snapshot, "Barrier support updates barrier and bounded KC evidence.")

        if t == LearnerEvidenceEventType.BARRIER_CONFIRMED:
            if not event.barrier_id:
                raise InvalidLearnerStateTransition("BARRIER_CONFIRMED requires barrier_id")
            if barrier_current == BarrierState.CONFIRMED and current == KCState.CONFIRMED_GAP:
                return LearnerStateTransitionResult(
                    snapshot=next_snapshot, changed=False, reason="Barrier and KC gap are already confirmed."
                )
            if barrier_current in {
                BarrierState.REPAIRING, BarrierState.TEMPORARILY_RECOVERED, BarrierState.RETEST_DUE,
                BarrierState.RELAPSED, BarrierState.DURABLE_EVIDENCE
            } or current in {
                KCState.REPAIRING, KCState.TEMPORARILY_RECOVERED, KCState.RETEST_DUE,
                KCState.RELAPSED, KCState.DURABLE_EVIDENCE
            }:
                raise InvalidLearnerStateTransition(
                    "Stale BARRIER_CONFIRMED cannot overwrite advanced repair/recovery evidence"
                )
            next_snapshot.barrier_states[event.barrier_id] = BarrierState.CONFIRMED
            next_snapshot.kc_states[kc] = KCState.CONFIRMED_GAP
            return self._done(snapshot, next_snapshot, "Confirmed barrier implies confirmed KC gap evidence.")

        if t == LearnerEvidenceEventType.REPAIR_STARTED:
            if current not in {KCState.SUPPORTED_GAP, KCState.CONFIRMED_GAP, KCState.RELAPSED}:
                raise InvalidLearnerStateTransition(f"Cannot start repair from KC state {current}")
            next_snapshot.kc_states[kc] = KCState.REPAIRING
            if event.barrier_id:
                if barrier_current not in {BarrierState.SUPPORTED, BarrierState.CONFIRMED, BarrierState.RELAPSED}:
                    raise InvalidLearnerStateTransition(
                        f"Cannot start barrier repair from state {barrier_current}"
                    )
                next_snapshot.barrier_states[event.barrier_id] = BarrierState.REPAIRING
            return self._done(snapshot, next_snapshot, "Repair entered; no recovery claim is created.")

        if t in {
            LearnerEvidenceEventType.REPAIR_ACTION_SUCCESS,
            LearnerEvidenceEventType.ORIGINAL_SELF_CORRECTION_SUCCESS,
        }:
            if current != KCState.REPAIRING:
                raise InvalidLearnerStateTransition(
                    f"{t.value} requires KC state REPAIRING, got {current}"
                )
            # Frozen invariant: neither repair completion nor original
            # self-correction is recovery.
            return LearnerStateTransitionResult(
                snapshot=next_snapshot,
                changed=False,
                reason="Success recorded, but KC remains REPAIRING until independent transfer succeeds.",
            )

        if t == LearnerEvidenceEventType.TRANSFER_SUCCESS:
            if current != KCState.REPAIRING:
                raise InvalidLearnerStateTransition(
                    f"TRANSFER_SUCCESS requires KC state REPAIRING, got {current}"
                )
            next_snapshot.kc_states[kc] = KCState.TEMPORARILY_RECOVERED
            if event.barrier_id:
                if barrier_current != BarrierState.REPAIRING:
                    raise InvalidLearnerStateTransition(
                        f"Barrier transfer success requires REPAIRING, got {barrier_current}"
                    )
                next_snapshot.barrier_states[event.barrier_id] = BarrierState.TEMPORARILY_RECOVERED
            return self._done(snapshot, next_snapshot, "Independent transfer makes temporary recovery eligible.")

        if t == LearnerEvidenceEventType.TRANSFER_FAILURE:
            if current != KCState.REPAIRING:
                raise InvalidLearnerStateTransition(
                    f"TRANSFER_FAILURE requires KC state REPAIRING, got {current}"
                )
            restored_kc = event.prior_gap_state or KCState.SUPPORTED_GAP
            if restored_kc not in {KCState.SUPPORTED_GAP, KCState.CONFIRMED_GAP, KCState.RELAPSED}:
                raise InvalidLearnerStateTransition("prior_gap_state must represent unresolved gap evidence")
            next_snapshot.kc_states[kc] = restored_kc
            if event.barrier_id:
                restored_barrier = event.prior_barrier_state or BarrierState.SUPPORTED
                if restored_barrier not in {BarrierState.SUPPORTED, BarrierState.CONFIRMED, BarrierState.RELAPSED}:
                    raise InvalidLearnerStateTransition("prior_barrier_state must represent unresolved barrier evidence")
                next_snapshot.barrier_states[event.barrier_id] = restored_barrier
            return self._done(snapshot, next_snapshot, "Failed transfer restores unresolved evidence; no recovery claim.")

        if t == LearnerEvidenceEventType.RETEST_SCHEDULED:
            if current != KCState.TEMPORARILY_RECOVERED:
                raise InvalidLearnerStateTransition(
                    f"RETEST_SCHEDULED requires TEMPORARILY_RECOVERED, got {current}"
                )
            next_snapshot.kc_states[kc] = KCState.RETEST_DUE
            next_snapshot.retest_due.add(kc)
            if event.barrier_id and barrier_current == BarrierState.TEMPORARILY_RECOVERED:
                next_snapshot.barrier_states[event.barrier_id] = BarrierState.RETEST_DUE
            return self._done(snapshot, next_snapshot, "Temporary recovery now requires delayed evidence.")

        if t == LearnerEvidenceEventType.DELAYED_RETEST_SUCCESS:
            if current not in {KCState.RETEST_DUE, KCState.TEMPORARILY_RECOVERED}:
                raise InvalidLearnerStateTransition(
                    f"DELAYED_RETEST_SUCCESS requires RETEST_DUE/TEMPORARILY_RECOVERED, got {current}"
                )
            next_snapshot.kc_states[kc] = KCState.DURABLE_EVIDENCE
            next_snapshot.retest_due.discard(kc)
            if event.barrier_id and barrier_current in {
                BarrierState.RETEST_DUE,
                BarrierState.TEMPORARILY_RECOVERED,
            }:
                next_snapshot.barrier_states[event.barrier_id] = BarrierState.DURABLE_EVIDENCE
            return self._done(snapshot, next_snapshot, "Delayed independent retest creates durable recovery evidence.")

        if t == LearnerEvidenceEventType.DELAYED_RETEST_FAILURE:
            if current not in {KCState.RETEST_DUE, KCState.TEMPORARILY_RECOVERED}:
                raise InvalidLearnerStateTransition(
                    f"DELAYED_RETEST_FAILURE requires RETEST_DUE/TEMPORARILY_RECOVERED, got {current}"
                )
            next_snapshot.kc_states[kc] = KCState.RELAPSED
            next_snapshot.retest_due.discard(kc)
            if event.barrier_id and barrier_current in {
                BarrierState.RETEST_DUE,
                BarrierState.TEMPORARILY_RECOVERED,
            }:
                next_snapshot.barrier_states[event.barrier_id] = BarrierState.RELAPSED
            return self._done(snapshot, next_snapshot, "Delayed retest failure records relapse.")

        raise InvalidLearnerStateTransition(f"Unsupported event type {t}")

    @staticmethod
    def _done(
        previous: LearnerEvidenceSnapshot,
        current: LearnerEvidenceSnapshot,
        reason: str,
    ) -> LearnerStateTransitionResult:
        return LearnerStateTransitionResult(
            snapshot=current,
            changed=current != previous,
            reason=reason,
        )
