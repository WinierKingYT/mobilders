from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet, Optional

from pydantic import BaseModel, Field

from .models import KCId, KCState, ProbeEvidenceKind, RepairEdge
from .registry import REPAIR_EDGES


class RepairEligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NEEDS_PROBE = "NEEDS_PROBE"
    BLOCKED_PROBE_BUDGET = "BLOCKED_PROBE_BUDGET"
    MISSING_REQUIRED_CONTEXT = "MISSING_REQUIRED_CONTEXT"
    DISQUALIFIED = "DISQUALIFIED"
    INELIGIBLE_ACTIVE_KC = "INELIGIBLE_ACTIVE_KC"
    INELIGIBLE_OBSERVATION = "INELIGIBLE_OBSERVATION"


class RepairEvidenceContext(BaseModel):
    active_kc: KCId
    observations: FrozenSet[str] = frozenset()
    probe_evidence: Dict[str, ProbeEvidenceKind] = Field(default_factory=dict)
    kc_states: Dict[KCId, KCState] = Field(default_factory=dict)
    flags: FrozenSet[str] = frozenset()
    probe_budget_remaining: int = Field(default=0, ge=0, le=1)


class RepairEligibilityResult(BaseModel):
    edge_id: str
    status: RepairEligibilityStatus
    recommended_probe_id: Optional[str] = None
    intervention_ids: FrozenSet[str] = frozenset()
    fallback_action: str
    reason: str


class RepairEdgeEligibilityEvaluator:
    """Machine-evaluable RepairEdge gate.

    The human-readable ``required_evidence`` field in the registry is not
    interpreted. Authority comes only from the typed ``evidence_policy``.
    """

    def evaluate(self, edge: RepairEdge, context: RepairEvidenceContext) -> RepairEligibilityResult:
        if context.active_kc != edge.from_kc:
            return self._result(
                edge,
                RepairEligibilityStatus.INELIGIBLE_ACTIVE_KC,
                "RepairEdge does not originate from the active target KC.",
            )

        if not (edge.eligible_observations & context.observations):
            return self._result(
                edge,
                RepairEligibilityStatus.INELIGIBLE_OBSERVATION,
                "No eligible ErrorObservation is present for this edge.",
            )

        policy = edge.evidence_policy
        disqualifiers = set(policy.disqualifying_flags) | set(edge.disqualifying_evidence)
        if disqualifiers & set(context.flags):
            return self._result(
                edge,
                RepairEligibilityStatus.DISQUALIFIED,
                "Fresh contradictory/positive evidence disqualifies this repair route.",
            )

        missing_flags = set(policy.required_flags) - set(context.flags)
        if missing_flags:
            return self._result(
                edge,
                RepairEligibilityStatus.MISSING_REQUIRED_CONTEXT,
                f"Missing required diagnostic context: {sorted(missing_flags)}",
            )

        probe_support = False
        for probe_id, accepted_kinds in policy.accepted_probe_evidence.items():
            observed_kind = context.probe_evidence.get(probe_id)
            if observed_kind in accepted_kinds:
                probe_support = True
                break

        target_state = context.kc_states.get(edge.to_kc, KCState.UNKNOWN)
        state_support = target_state in policy.allowed_target_kc_states
        if state_support and not policy.state_support_required_flags.issubset(context.flags):
            state_support = False

        if probe_support or state_support:
            return self._result(
                edge,
                RepairEligibilityStatus.ELIGIBLE,
                "Structured evidence policy is satisfied.",
                intervention_ids=edge.entry_intervention_ids,
            )

        if edge.preferred_probe_id:
            if context.probe_budget_remaining > 0:
                return self._result(
                    edge,
                    RepairEligibilityStatus.NEEDS_PROBE,
                    "Required repair evidence is not established yet.",
                    recommended_probe_id=edge.preferred_probe_id,
                )
            return self._result(
                edge,
                RepairEligibilityStatus.BLOCKED_PROBE_BUDGET,
                "Required evidence is missing and the current probe budget is exhausted.",
            )

        return self._result(
            edge,
            RepairEligibilityStatus.MISSING_REQUIRED_CONTEXT,
            "Required evidence is missing and no legal probe is registered.",
        )

    def evaluate_edge_id(self, edge_id: str, context: RepairEvidenceContext) -> RepairEligibilityResult:
        return self.evaluate(REPAIR_EDGES[edge_id], context)

    @staticmethod
    def _result(
        edge: RepairEdge,
        status: RepairEligibilityStatus,
        reason: str,
        *,
        recommended_probe_id: Optional[str] = None,
        intervention_ids: FrozenSet[str] = frozenset(),
    ) -> RepairEligibilityResult:
        return RepairEligibilityResult(
            edge_id=edge.edge_id,
            status=status,
            recommended_probe_id=recommended_probe_id,
            intervention_ids=intervention_ids,
            fallback_action=edge.fallback_action,
            reason=reason,
        )
