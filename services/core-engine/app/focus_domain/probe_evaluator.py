from __future__ import annotations

from typing import Dict, FrozenSet, Optional

from pydantic import BaseModel, Field

from .learner_state import (
    LearnerEvidenceEvent,
    LearnerEvidenceEventType,
    LearnerEvidenceSnapshot,
    LearnerStateTransitionService,
)
from .models import KCId, ProbeEvidenceKind
from .registry import PROBE_TEMPLATES


class UnknownProbeResponse(ValueError):
    pass


class ProbeEvaluationResult(BaseModel):
    probe_id: str
    target_kc: KCId
    response_code: str
    evidence_kind: ProbeEvidenceKind
    candidate_barriers: FrozenSet[str] = frozenset()
    specific_barrier_id: Optional[str] = None
    barrier_attributes: Dict[str, str] = Field(default_factory=dict)
    derived_flags: FrozenSet[str] = frozenset()
    snapshot: LearnerEvidenceSnapshot
    learner_state_changed: bool = False


class ProbeResponseEvaluator:
    """Translate structured probe responses into bounded evidence updates.

    This class never upgrades a barrier to CONFIRMED. A single Alpha probe can
    support a barrier or KC gap, weaken a barrier, or remain inconclusive.
    Confirmation remains a higher-level evidence decision.
    """

    def __init__(self) -> None:
        self._state = LearnerStateTransitionService()

    def evaluate(
        self,
        *,
        snapshot: LearnerEvidenceSnapshot,
        probe_id: str,
        response_code: str,
    ) -> ProbeEvaluationResult:
        try:
            template = PROBE_TEMPLATES[probe_id]
        except KeyError as exc:
            raise UnknownProbeResponse(f"Unknown probe_id: {probe_id}") from exc

        response = next(
            (item for item in template.response_classes if item.code == response_code),
            None,
        )
        if response is None:
            raise UnknownProbeResponse(
                f"Unknown response_code {response_code!r} for probe {probe_id}"
            )

        current = snapshot
        changed = False
        specific_barrier_id: Optional[str] = None
        derived_flags = set()
        barrier_attributes: Dict[str, str] = {}

        if probe_id == "PR-Q0-01" and response.evidence_kind == ProbeEvidenceKind.POSITIVE:
            derived_flags.add("Q0_PASSED")

        if probe_id == "PR-N2-01" and response.evidence_kind == ProbeEvidenceKind.POSITIVE:
            # A clean direct signed-multiplication probe weakens N2 as the cause
            # of a distribution-sign failure. It does not prove N3/E1.
            derived_flags.add("N2_ALTERNATIVE_INSUFFICIENT")

        if probe_id == "PR-F2-01" and response.evidence_kind == ProbeEvidenceKind.BARRIER_SUPPORT:
            if response_code == "SUM_ONLY":
                barrier_attributes["ignored_constraint"] = "PRODUCT"
            elif response_code == "PRODUCT_ONLY":
                barrier_attributes["ignored_constraint"] = "SUM"

        if response.evidence_kind == ProbeEvidenceKind.GAP:
            transition = self._state.apply(
                current,
                LearnerEvidenceEvent(
                    event_type=LearnerEvidenceEventType.GAP_SUPPORTED,
                    target_kc=template.target_kc,
                ),
            )
            current = transition.snapshot
            changed = transition.changed

        elif response.evidence_kind == ProbeEvidenceKind.BARRIER_SUPPORT:
            if len(template.candidate_barriers) == 1:
                specific_barrier_id = next(iter(template.candidate_barriers))
                transition = self._state.apply(
                    current,
                    LearnerEvidenceEvent(
                        event_type=LearnerEvidenceEventType.BARRIER_SUPPORTED,
                        target_kc=template.target_kc,
                        barrier_id=specific_barrier_id,
                    ),
                )
                current = transition.snapshot
                changed = transition.changed
            else:
                # The response says "there is a gap somewhere in this candidate
                # set", but not which material alternative is responsible.
                transition = self._state.apply(
                    current,
                    LearnerEvidenceEvent(
                        event_type=LearnerEvidenceEventType.GAP_SUPPORTED,
                        target_kc=template.target_kc,
                    ),
                )
                current = transition.snapshot
                changed = transition.changed

        # POSITIVE, BARRIER_WEAKEN and INCONCLUSIVE responses intentionally do
        # not erase or downgrade prior learner evidence.

        return ProbeEvaluationResult(
            probe_id=probe_id,
            target_kc=template.target_kc,
            response_code=response_code,
            evidence_kind=response.evidence_kind,
            candidate_barriers=template.candidate_barriers,
            specific_barrier_id=specific_barrier_id,
            barrier_attributes=barrier_attributes,
            derived_flags=frozenset(derived_flags),
            snapshot=current,
            learner_state_changed=changed,
        )
