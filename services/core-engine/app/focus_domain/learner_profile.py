"""Multi-Episode Learner Profile & Prerequisite Graph Maintenance (Round 09).

Maintains cross-episode learner profiles, prerequisite chain health, and
session re-entry diagnostics without violating the frozen cognitive authority.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field

from .models import BarrierState, KCId, KCState
from .learner_state import LearnerEvidenceSnapshot
from .registry import REPAIR_EDGES


# Static Prerequisite Graph extracted from the frozen Alpha authority & REPAIR_EDGES
PREREQUISITE_GRAPH: Dict[KCId, Set[KCId]] = {
    KCId.N1: set(),
    KCId.N2: set(),
    KCId.N3: set(),
    KCId.E1: {KCId.N2, KCId.N3},
    KCId.E2: set(),
    KCId.Q0: set(),
    KCId.Q1: {KCId.Q0, KCId.N3, KCId.N1},
    KCId.F1: {KCId.E1, KCId.E2, KCId.N1, KCId.N2},
    KCId.F2: {KCId.N1, KCId.N2, KCId.F1},
    KCId.Z1: set(),
}


class PrerequisiteChainHealth(str, Enum):
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"


class KCHealthSummary(BaseModel):
    kc_id: KCId
    state: KCState
    direct_prerequisites: List[KCId] = Field(default_factory=list)
    prerequisite_health: PrerequisiteChainHealth
    unresolved_prerequisites: List[KCId] = Field(default_factory=list)
    barrier_states: Dict[str, BarrierState] = Field(default_factory=dict)
    retest_due: bool = False


class ReEntryDiagnostic(BaseModel):
    target_kc: KCId
    can_attempt_target: bool
    blocking_kcs: List[KCId] = Field(default_factory=list)
    recommended_focus_kc: KCId
    rationale: str


class MultiEpisodeLearnerProfile(BaseModel):
    """Aggregated cross-episode learner profile."""
    total_episodes_evaluated: int = 0
    kc_states: Dict[KCId, KCState] = Field(default_factory=dict)
    barrier_states: Dict[str, BarrierState] = Field(default_factory=dict)
    retest_due: Set[KCId] = Field(default_factory=set)
    kc_health: Dict[KCId, KCHealthSummary] = Field(default_factory=dict)


# Precedence for aggregating KC states across episodes:
# Stronger/more recent evidence takes precedence
_KC_STATE_PRECEDENCE = {
    KCState.DURABLE_EVIDENCE: 60,
    KCState.TEMPORARILY_RECOVERED: 50,
    KCState.RETEST_DUE: 45,
    KCState.RELAPSED: 40,
    KCState.CONFIRMED_GAP: 35,
    KCState.SUPPORTED_GAP: 30,
    KCState.REPAIRING: 20,
    KCState.UNKNOWN: 10,
}

_BARRIER_STATE_PRECEDENCE = {
    BarrierState.DURABLE_EVIDENCE: 60,
    BarrierState.TEMPORARILY_RECOVERED: 50,
    BarrierState.RETEST_DUE: 45,
    BarrierState.RELAPSED: 40,
    BarrierState.CONFIRMED: 35,
    BarrierState.SUPPORTED: 30,
    BarrierState.REPAIRING: 20,
    BarrierState.UNSEEN: 10,
}

_BLOCKING_STATES = {
    KCState.CONFIRMED_GAP,
    KCState.RELAPSED,
    KCState.SUPPORTED_GAP,
    KCState.RETEST_DUE,
}


class LearnerProfileAggregator:
    """Computes cross-episode learner profile, prerequisite chain health, and diagnostics."""

    @classmethod
    def aggregate(
        cls,
        snapshots: List[LearnerEvidenceSnapshot],
    ) -> MultiEpisodeLearnerProfile:
        merged_kc_states: Dict[KCId, KCState] = {}
        merged_barrier_states: Dict[str, BarrierState] = {}
        merged_retest_due: Set[KCId] = set()

        for snap in snapshots:
            # Aggregate KC states
            for kc, st in snap.kc_states.items():
                curr = merged_kc_states.get(kc)
                if curr is None:
                    merged_kc_states[kc] = st
                else:
                    # Choose higher precedence
                    if _KC_STATE_PRECEDENCE.get(st, 0) >= _KC_STATE_PRECEDENCE.get(curr, 0):
                        merged_kc_states[kc] = st

            # Aggregate Barrier states
            for bid, bst in snap.barrier_states.items():
                curr_b = merged_barrier_states.get(bid)
                if curr_b is None:
                    merged_barrier_states[bid] = bst
                else:
                    if _BARRIER_STATE_PRECEDENCE.get(bst, 0) >= _BARRIER_STATE_PRECEDENCE.get(curr_b, 0):
                        merged_barrier_states[bid] = bst

            # Retest due set
            merged_retest_due.update(snap.retest_due)

        # Remove retest_due if KC reached durable evidence or relapsed
        for kc in list(merged_retest_due):
            st = merged_kc_states.get(kc)
            if st not in {KCState.RETEST_DUE, KCState.TEMPORARILY_RECOVERED}:
                merged_retest_due.discard(kc)

        # Compute health summaries for all 10 KCs
        kc_health = {}
        for kc in KCId:
            st = merged_kc_states.get(kc, KCState.UNKNOWN)
            direct_prereqs = sorted(PREREQUISITE_GRAPH.get(kc, set()), key=lambda k: k.value)

            unresolved = [
                pkc for pkc in direct_prereqs
                if merged_kc_states.get(pkc, KCState.UNKNOWN) in _BLOCKING_STATES
            ]

            if not direct_prereqs:
                health = PrerequisiteChainHealth.HEALTHY
            elif not unresolved:
                health = PrerequisiteChainHealth.HEALTHY
            elif any(merged_kc_states.get(pkc) in {KCState.CONFIRMED_GAP, KCState.RELAPSED} for pkc in unresolved):
                health = PrerequisiteChainHealth.BLOCKED
            else:
                health = PrerequisiteChainHealth.AT_RISK

            # Related barriers
            related_barriers = {
                bid: bst for bid, bst in merged_barrier_states.items()
                if bid.startswith(f"BH-{kc.value.replace('KC-', '')}")
            }

            kc_health[kc] = KCHealthSummary(
                kc_id=kc,
                state=st,
                direct_prerequisites=direct_prereqs,
                prerequisite_health=health,
                unresolved_prerequisites=unresolved,
                barrier_states=related_barriers,
                retest_due=kc in merged_retest_due,
            )

        return MultiEpisodeLearnerProfile(
            total_episodes_evaluated=len(snapshots),
            kc_states=merged_kc_states,
            barrier_states=merged_barrier_states,
            retest_due=merged_retest_due,
            kc_health=kc_health,
        )

    @classmethod
    def diagnose_re_entry(
        cls,
        profile: MultiEpisodeLearnerProfile,
        target_kc: KCId,
    ) -> ReEntryDiagnostic:
        """Diagnose session re-entry/cold-start readiness for a target KC."""
        summary = profile.kc_health.get(target_kc)
        if summary is None or summary.prerequisite_health == PrerequisiteChainHealth.HEALTHY:
            return ReEntryDiagnostic(
                target_kc=target_kc,
                can_attempt_target=True,
                blocking_kcs=[],
                recommended_focus_kc=target_kc,
                rationale=f"Prerequisite chains for {target_kc.value} are healthy. Safe to proceed.",
            )

        # If blocked or at risk, recommend root unresolved prerequisite
        blocking = summary.unresolved_prerequisites
        recommended = blocking[0] if blocking else target_kc
        can_attempt = summary.prerequisite_health != PrerequisiteChainHealth.BLOCKED

        return ReEntryDiagnostic(
            target_kc=target_kc,
            can_attempt_target=can_attempt,
            blocking_kcs=blocking,
            recommended_focus_kc=recommended,
            rationale=(
                f"{target_kc.value} prerequisite chain is {summary.prerequisite_health.value} "
                f"due to unresolved prerequisites: {[k.value for k in blocking]}. "
                f"Recommended prior repair: {recommended.value}."
            ),
        )
