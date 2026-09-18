from __future__ import annotations

from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Set, Union

from pydantic import BaseModel, Field, model_validator

from .learner_state import (
    LearnerEvidenceEvent,
    LearnerEvidenceEventType,
    LearnerEvidenceSnapshot,
    LearnerStateTransitionService,
)
from .models import (
    AttemptJudgment,
    BarrierState,
    CTINEQ1TaskContext,
    CTLIN1TaskContext,
    CTPAR1TaskContext,
    CTPOLY1TaskContext,
    CTTRIG1TaskContext,
    CTLOG1TaskContext,
    CTLIM1TaskContext,
    CTDERIV1TaskContext,
    CTINT1TaskContext,
    CTQF1TaskContext,
    KCId,
    KCState,
    ProbeEvidenceKind,
    StageId,
)
from .probe_evaluator import ProbeEvaluationResult, ProbeResponseEvaluator
from .registry import ACTIVE_DIAGNOSTIC_ROUTES, INTERVENTION_TEMPLATES, REPAIR_EDGES
from .repair_evaluator import (
    RepairEdgeEligibilityEvaluator,
    RepairEligibilityResult,
    RepairEligibilityStatus,
    RepairEvidenceContext,
)
from .rules import apply_valid_shortcut


class EpisodePhase(str, Enum):
    WORKSPACE = "WORKSPACE"
    PROBING = "PROBING"
    REPAIRING = "REPAIRING"
    AWAITING_ORIGINAL_SELF_CORRECTION = "AWAITING_ORIGINAL_SELF_CORRECTION"
    AWAITING_TRANSFER = "AWAITING_TRANSFER"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


class NextActionType(str, Enum):
    ADVANCE = "ADVANCE"
    REQUEST_COMPLETION = "REQUEST_COMPLETION"
    COMPLETE_TASK = "COMPLETE_TASK"
    REQUEST_PROBE = "REQUEST_PROBE"
    START_REPAIR = "START_REPAIR"
    NEUTRAL_SUPPORT = "NEUTRAL_SUPPORT"
    CLARIFY_INPUT = "CLARIFY_INPUT"
    FAIL_CLOSED = "FAIL_CLOSED"
    CLEAN_STOP = "CLEAN_STOP"


class FocusDecision(BaseModel):
    action: NextActionType
    reason: str
    probe_id: Optional[str] = None
    repair_edge_id: Optional[str] = None
    diagnostic_route_id: Optional[str] = None
    target_kc: Optional[KCId] = None
    barrier_id: Optional[str] = None
    intervention_id: Optional[str] = None


class FocusEpisodeState(BaseModel):
    workspace_kc: KCId
    composite_task_id: Optional[str] = None
    current_stage: Optional[StageId] = None
    task_context: Optional[
        Union[
            CTQF1TaskContext,
            CTLIN1TaskContext,
            CTINEQ1TaskContext,
            CTPAR1TaskContext,
            CTPOLY1TaskContext,
            CTTRIG1TaskContext,
            CTLOG1TaskContext,
            CTLIM1TaskContext,
            CTDERIV1TaskContext,
            CTINT1TaskContext,
            Dict[str, Any],
        ]
    ] = None
    phase: EpisodePhase = EpisodePhase.WORKSPACE
    learner: LearnerEvidenceSnapshot = Field(default_factory=LearnerEvidenceSnapshot)
    probe_evidence: Dict[str, ProbeEvidenceKind] = Field(default_factory=dict)
    flags: Set[str] = Field(default_factory=set)
    probe_budget_remaining: int = Field(default=1, ge=0, le=1)
    used_probe_ids: Set[str] = Field(default_factory=set)
    last_judgment: Optional[AttemptJudgment] = None
    last_observations: FrozenSet[str] = frozenset()
    pending_probe_id: Optional[str] = None
    repair_kc: Optional[KCId] = None
    repair_edge_id: Optional[str] = None
    repair_diagnostic_route_id: Optional[str] = None
    repair_barrier_id: Optional[str] = None
    repair_intervention_id: Optional[str] = None
    intervention_task_context: Optional[Dict[str, Any]] = None
    transfer_task_context: Optional[Dict[str, Any]] = None
    retest_task_context: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def _hydrate_task_context(cls, data: Any) -> Any:
        if isinstance(data, dict):
            ctx = data.get("task_context")
            cid = data.get("composite_task_id")
            if isinstance(ctx, dict):
                if cid == "CT-QF1" or "factor_pair" in ctx:
                    data["task_context"] = CTQF1TaskContext.model_validate(ctx)
                elif cid == "CT-LIN1":
                    data["task_context"] = CTLIN1TaskContext.model_validate(ctx)
                elif cid == "CT-INEQ1" or "comparator" in ctx:
                    data["task_context"] = CTINEQ1TaskContext.model_validate(ctx)
                elif cid == "CT-PAR1" or "expected_r" in ctx:
                    data["task_context"] = CTPAR1TaskContext.model_validate(ctx)
                elif cid == "CT-POLY1" or "divisor_root" in ctx:
                    data["task_context"] = CTPOLY1TaskContext.model_validate(ctx)
                elif cid == "CT-TRIG1" or "expected_principal_deg" in ctx:
                    data["task_context"] = CTTRIG1TaskContext.model_validate(ctx)
                elif cid == "CT-LOG1" or "expected_power" in ctx:
                    data["task_context"] = CTLOG1TaskContext.model_validate(ctx)
                elif cid == "CT-LIM1" or "expected_indeterminate_form" in ctx:
                    data["task_context"] = CTLIM1TaskContext.model_validate(ctx)
                elif cid == "CT-DERIV1" or "expected_tangent_line" in ctx:
                    data["task_context"] = CTDERIV1TaskContext.model_validate(ctx)
                elif cid == "CT-INT1" or "expected_definite_value" in ctx:
                    data["task_context"] = CTINT1TaskContext.model_validate(ctx)
        return data



class ProbeApplicationResult(BaseModel):
    state: FocusEpisodeState
    probe_result: ProbeEvaluationResult
    decision: FocusDecision


class FocusDecisionPipeline:
    """Pure bounded decision policy for the frozen Alpha Focus kernel."""

    _REPAIRABLE_KC_STATES = {
        KCState.SUPPORTED_GAP,
        KCState.CONFIRMED_GAP,
        KCState.RELAPSED,
    }

    def __init__(self) -> None:
        self._repair = RepairEdgeEligibilityEvaluator()

    def decide_after_attempt(
        self,
        state: FocusEpisodeState,
        *,
        judgment: AttemptJudgment,
        observations: FrozenSet[str] = frozenset(),
    ) -> FocusDecision:
        if judgment == AttemptJudgment.VALID_EXPECTED:
            return FocusDecision(
                action=NextActionType.ADVANCE,
                reason="Expected supported work is mathematically valid.",
            )

        if judgment == AttemptJudgment.VALID_INCOMPLETE:
            return FocusDecision(
                action=NextActionType.REQUEST_COMPLETION,
                reason="Work is mathematically valid but the stage contract is incomplete.",
            )

        if judgment == AttemptJudgment.VALID_SHORTCUT:
            return FocusDecision(
                action=NextActionType.COMPLETE_TASK,
                reason="Correct shortcut may complete the composite task without laundering bypassed KC evidence.",
            )

        if judgment == AttemptJudgment.AMBIGUOUS_INPUT:
            return FocusDecision(
                action=NextActionType.CLARIFY_INPUT,
                reason="Ambiguous input cannot create cognitive evidence.",
            )

        if judgment in {
            AttemptJudgment.UNSUPPORTED_STEP_FORM,
            AttemptJudgment.UNSUPPORTED_DOMAIN,
        }:
            return FocusDecision(
                action=NextActionType.FAIL_CLOSED,
                reason="Unsupported representation/domain must fail closed without learner diagnosis.",
            )

        if judgment != AttemptJudgment.INVALID_MATHEMATICS:
            return FocusDecision(
                action=NextActionType.CLEAN_STOP,
                reason="No legal Alpha decision exists for the supplied attempt state.",
            )

        direct = self._direct_active_kc_decision(state, observations)
        if direct is not None:
            return direct

        candidates = [
            edge
            for edge in REPAIR_EDGES.values()
            if edge.from_kc == state.workspace_kc
            and bool(edge.eligible_observations & observations)
        ]
        if not candidates:
            return FocusDecision(
                action=NextActionType.CLEAN_STOP,
                reason="Invalid mathematics is real, but no bounded diagnostic or prerequisite repair route is authorized.",
            )

        context = RepairEvidenceContext(
            active_kc=state.workspace_kc,
            observations=observations,
            probe_evidence=state.probe_evidence,
            kc_states=state.learner.kc_states,
            flags=frozenset(state.flags),
            probe_budget_remaining=state.probe_budget_remaining,
        )
        results = [self._repair.evaluate(edge, context) for edge in candidates]

        eligible = [r for r in results if r.status == RepairEligibilityStatus.ELIGIBLE]
        if len(eligible) == 1:
            return self._decision_for_eligible(state, eligible[0])
        if len(eligible) > 1:
            return FocusDecision(
                action=NextActionType.NEUTRAL_SUPPORT,
                reason="Multiple repair routes are simultaneously eligible; arbitrary tie-breaking is forbidden.",
            )

        needs_probe = [r for r in results if r.status == RepairEligibilityStatus.NEEDS_PROBE]
        probe_ids = {r.recommended_probe_id for r in needs_probe if r.recommended_probe_id}
        if needs_probe and len(probe_ids) == 1:
            probe_id = next(iter(probe_ids))
            return FocusDecision(
                action=NextActionType.REQUEST_PROBE,
                probe_id=probe_id,
                reason="One discriminating Alpha probe can establish the missing repair evidence.",
            )
        if len(probe_ids) > 1:
            return FocusDecision(
                action=NextActionType.NEUTRAL_SUPPORT,
                reason="Material alternatives require different probes; one-probe budget forbids arbitrary selection.",
            )

        # A fallback may only be executed if it is itself an authorized template
        # for the current target and safe under unresolved barrier uncertainty.
        fallback_ids = {r.fallback_action for r in results}
        if len(fallback_ids) == 1:
            fallback = next(iter(fallback_ids))
            template = INTERVENTION_TEMPLATES.get(fallback)
            if (
                template is not None
                and template.target_kc == state.workspace_kc
                and (not template.eligible_barriers or template.neutral_support_allowed)
            ):
                return FocusDecision(
                    action=NextActionType.NEUTRAL_SUPPORT,
                    target_kc=state.workspace_kc,
                    intervention_id=fallback,
                    reason="Specific repair evidence is unavailable; a whitelisted low-risk support action is allowed.",
                )

        return FocusDecision(
            action=NextActionType.CLEAN_STOP,
            reason="Evidence/probe budget does not authorize repair and no safe executable fallback exists.",
        )

    def _direct_active_kc_decision(
        self,
        state: FocusEpisodeState,
        observations: FrozenSet[str],
    ) -> Optional[FocusDecision]:
        routes = [
            route
            for route in ACTIVE_DIAGNOSTIC_ROUTES.values()
            if route.active_kc == state.workspace_kc
            and bool(route.eligible_observations & observations)
        ]
        if not routes:
            return None

        supported_routes = []
        for route in routes:
            if route.barrier_id and state.learner.barrier_states.get(
                route.barrier_id, BarrierState.UNSEEN
            ) in {BarrierState.SUPPORTED, BarrierState.CONFIRMED, BarrierState.RELAPSED}:
                supported_routes.append(route)

        if len(supported_routes) == 1:
            route = supported_routes[0]
            return FocusDecision(
                action=NextActionType.START_REPAIR,
                diagnostic_route_id=route.route_id,
                target_kc=route.active_kc,
                barrier_id=route.barrier_id,
                intervention_id=route.intervention_id,
                reason="Direct active-KC barrier evidence authorizes the smallest bounded repair.",
            )
        if len(supported_routes) > 1:
            return FocusDecision(
                action=NextActionType.NEUTRAL_SUPPORT,
                reason="Multiple active-KC barriers remain supported; no arbitrary repair selection is allowed.",
            )

        barrier_free = [route for route in routes if route.barrier_id is None]
        if len(barrier_free) == 1:
            route = barrier_free[0]
            current = state.learner.kc_states.get(route.active_kc, KCState.UNKNOWN)
            template = INTERVENTION_TEMPLATES[route.intervention_id]
            if current in template.allowed_kc_states:
                return FocusDecision(
                    action=NextActionType.START_REPAIR,
                    diagnostic_route_id=route.route_id,
                    target_kc=route.active_kc,
                    intervention_id=route.intervention_id,
                    reason="Direct KC-level evidence authorizes a bounded barrier-free repair.",
                )

        probe_ids = {route.probe_id for route in routes}
        unused_probe_ids = probe_ids - state.used_probe_ids
        if len(unused_probe_ids) == 1 and state.probe_budget_remaining > 0:
            return FocusDecision(
                action=NextActionType.REQUEST_PROBE,
                probe_id=next(iter(unused_probe_ids)),
                reason="Probe the active KC before descending to a prerequisite repair.",
            )
        if len(unused_probe_ids) > 1:
            return FocusDecision(
                action=NextActionType.NEUTRAL_SUPPORT,
                reason="Multiple direct active-KC probes compete; the policy refuses arbitrary probe choice.",
            )

        return None

    def _decision_for_eligible(
        self,
        state: FocusEpisodeState,
        result: RepairEligibilityResult,
    ) -> FocusDecision:
        edge = REPAIR_EDGES[result.edge_id]
        intervention_ids = sorted(result.intervention_ids)
        if len(intervention_ids) != 1:
            return FocusDecision(
                action=NextActionType.CLEAN_STOP,
                reason="Eligible edge does not resolve to exactly one executable intervention.",
            )

        intervention_id = intervention_ids[0]
        template = INTERVENTION_TEMPLATES[intervention_id]
        target_state = state.learner.kc_states.get(edge.to_kc, KCState.UNKNOWN)

        supported_barriers = [
            barrier_id
            for barrier_id in template.eligible_barriers
            if state.learner.barrier_states.get(barrier_id, BarrierState.UNSEEN)
            in template.allowed_barrier_states
        ]
        if len(supported_barriers) == 1:
            return FocusDecision(
                action=NextActionType.START_REPAIR,
                repair_edge_id=edge.edge_id,
                target_kc=edge.to_kc,
                barrier_id=supported_barriers[0],
                intervention_id=intervention_id,
                reason="A unique supported barrier authorizes its bounded intervention.",
            )

        if not template.eligible_barriers and target_state in template.allowed_kc_states:
            return FocusDecision(
                action=NextActionType.START_REPAIR,
                repair_edge_id=edge.edge_id,
                target_kc=edge.to_kc,
                intervention_id=intervention_id,
                reason="KC-level gap evidence authorizes a bounded barrier-free repair.",
            )

        if template.neutral_support_allowed and target_state in self._REPAIRABLE_KC_STATES:
            return FocusDecision(
                action=NextActionType.NEUTRAL_SUPPORT,
                repair_edge_id=edge.edge_id,
                target_kc=edge.to_kc,
                intervention_id=intervention_id,
                reason="KC gap is supported but the durable barrier is not; use the template only as neutral support.",
            )

        return FocusDecision(
            action=NextActionType.CLEAN_STOP,
            repair_edge_id=edge.edge_id,
            target_kc=edge.to_kc,
            reason="RepairEdge evidence is sufficient, but intervention authority is not.",
        )


class FocusEpisodeOrchestrator:
    """Thin state machine that enforces probe and recovery ordering.

    Persistence, API transport, UI and content generation are deliberately out
    of scope. This orchestrator is pure application logic around the frozen
    Focus kernel.
    """

    def __init__(self) -> None:
        self._pipeline = FocusDecisionPipeline()
        self._probes = ProbeResponseEvaluator()
        self._state_service = LearnerStateTransitionService()

    @staticmethod
    def _is_ctqf1(state: FocusEpisodeState) -> bool:
        return (
            state.composite_task_id == "CT-QF1"
            and state.current_stage is not None
            and state.task_context is not None
        )

    @staticmethod
    def _advance_ctqf1_stage(state: FocusEpisodeState) -> None:
        mapping = {
            StageId.S1_FACTOR: (StageId.S2_BRANCH, KCId.Z1),
            StageId.S2_BRANCH: (StageId.S3_SOLVE_FACTOR_EQUATIONS, KCId.Q1),
            StageId.S3_SOLVE_FACTOR_EQUATIONS: (StageId.S4_COMPLETE_SOLUTION_SET, KCId.Q1),
        }
        if state.current_stage in mapping:
            next_stage, next_kc = mapping[state.current_stage]
            state.current_stage = next_stage
            state.workspace_kc = next_kc

    def handle_attempt(
        self,
        state: FocusEpisodeState,
        *,
        judgment: AttemptJudgment,
        observations: FrozenSet[str] = frozenset(),
    ) -> tuple[FocusEpisodeState, FocusDecision]:
        next_state = state.model_copy(deep=True)
        next_state.last_judgment = judgment
        next_state.last_observations = observations

        if judgment == AttemptJudgment.VALID_SHORTCUT:
            shortcut = apply_valid_shortcut(
                existing_kc_states=next_state.learner.kc_states,
                existing_barrier_states=next_state.learner.barrier_states,
                existing_retest_due=next_state.learner.retest_due,
            )
            next_state.learner.kc_states = shortcut.kc_states
            next_state.learner.barrier_states = shortcut.barrier_states
            next_state.learner.retest_due = shortcut.retest_due

        decision = self._pipeline.decide_after_attempt(
            next_state,
            judgment=judgment,
            observations=observations,
        )

        if (
            judgment == AttemptJudgment.VALID_EXPECTED
            and self._is_ctqf1(next_state)
        ):
            if next_state.current_stage == StageId.S4_COMPLETE_SOLUTION_SET:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="Complete CT-QF1 solution set satisfies the final stage contract.",
                )
            else:
                self._advance_ctqf1_stage(next_state)
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-LIN1"
        ):
            if next_state.current_stage == StageId.S1_ISOLATE_TERM:
                next_state.current_stage = StageId.S2_ISOLATE_VARIABLE
                next_state.workspace_kc = KCId.L1
            elif next_state.current_stage == StageId.S2_ISOLATE_VARIABLE:
                next_state.current_stage = StageId.S3_VERIFY_SOLUTION
                next_state.workspace_kc = KCId.L2
            elif next_state.current_stage == StageId.S3_VERIFY_SOLUTION:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-LIN1 linear equation solution verified successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-INEQ1"
        ):
            if next_state.current_stage == StageId.S1_ISOLATE_TERM:
                next_state.current_stage = StageId.S2_DIRECTION_AWARE_DIVISION
                next_state.workspace_kc = KCId.I1
            elif next_state.current_stage == StageId.S2_DIRECTION_AWARE_DIVISION:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-INEQ1 linear inequality solved with direction reversal.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-PAR1"
        ):
            if next_state.current_stage == StageId.S1_CALCULATE_R:
                next_state.current_stage = StageId.S2_CALCULATE_K
                next_state.workspace_kc = KCId.P1
            elif next_state.current_stage == StageId.S2_CALCULATE_K:
                next_state.current_stage = StageId.S3_EXTREMUM_CLASSIFICATION
                next_state.workspace_kc = KCId.P2
            elif next_state.current_stage == StageId.S3_EXTREMUM_CLASSIFICATION:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-PAR1 parabola vertex and extremum classification completed successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-POLY1"
        ):
            if next_state.current_stage == StageId.S1_ROOT_OF_DIVISOR:
                next_state.current_stage = StageId.S2_EVALUATE_REMAINDER
                next_state.workspace_kc = KCId.PL1
            elif next_state.current_stage == StageId.S2_EVALUATE_REMAINDER:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-POLY1 polynomial remainder theorem evaluation completed successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-TRIG1"
        ):
            if next_state.current_stage == StageId.S1_ISOLATE_TRIG_VALUE:
                next_state.current_stage = StageId.S2_DETERMINE_PRINCIPAL_ANGLE
                next_state.workspace_kc = KCId.TR1
            elif next_state.current_stage == StageId.S2_DETERMINE_PRINCIPAL_ANGLE:
                next_state.current_stage = StageId.S3_DETERMINE_SECONDARY_ROOT
                next_state.workspace_kc = KCId.TR1
            elif next_state.current_stage == StageId.S3_DETERMINE_SECONDARY_ROOT:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-TRIG1 trigonometric equation roots evaluated successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-LOG1"
        ):
            if next_state.current_stage == StageId.S1_EXPONENTIAL_CONVERSION:
                next_state.current_stage = StageId.S2_ISOLATE_VARIABLE
                next_state.workspace_kc = KCId.LG1
            elif next_state.current_stage == StageId.S2_ISOLATE_VARIABLE:
                next_state.current_stage = StageId.S3_VERIFY_DOMAIN_CONSTRAINT
                next_state.workspace_kc = KCId.LG1
            elif next_state.current_stage == StageId.S3_VERIFY_DOMAIN_CONSTRAINT:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-LOG1 logarithmic equation and domain constraints completed successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-LIM1"
        ):
            if next_state.current_stage == StageId.S1_EVALUATE_LIMIT_FORM:
                next_state.current_stage = StageId.S2_SIMPLIFY_EXPRESSION
                next_state.workspace_kc = KCId.LM1
            elif next_state.current_stage == StageId.S2_SIMPLIFY_EXPRESSION:
                next_state.current_stage = StageId.S3_COMPUTE_FINAL_LIMIT
                next_state.workspace_kc = KCId.LM1
            elif next_state.current_stage == StageId.S3_COMPUTE_FINAL_LIMIT:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-LIM1 limit evaluation completed successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-DERIV1"
        ):
            if next_state.current_stage == StageId.S1_COMPUTE_DERIVATIVE:
                next_state.current_stage = StageId.S2_EVALUATE_SLOPE
                next_state.workspace_kc = KCId.DV1
            elif next_state.current_stage == StageId.S2_EVALUATE_SLOPE:
                next_state.current_stage = StageId.S3_DETERMINE_TANGENT_LINE
                next_state.workspace_kc = KCId.DV1
            elif next_state.current_stage == StageId.S3_DETERMINE_TANGENT_LINE:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-DERIV1 polynomial derivative and tangent line completed successfully.",
                )
        elif (
            judgment == AttemptJudgment.VALID_EXPECTED
            and next_state.composite_task_id == "CT-INT1"
        ):
            if next_state.current_stage == StageId.S1_FIND_ANTIDERIVATIVE:
                next_state.current_stage = StageId.S2_APPLY_LIMITS
                next_state.workspace_kc = KCId.IN1
            elif next_state.current_stage == StageId.S2_APPLY_LIMITS:
                next_state.current_stage = StageId.S3_COMPUTE_DEFINITE_INTEGRAL
                next_state.workspace_kc = KCId.IN1
            elif next_state.current_stage == StageId.S3_COMPUTE_DEFINITE_INTEGRAL:
                decision = FocusDecision(
                    action=NextActionType.COMPLETE_TASK,
                    reason="CT-INT1 definite integral and area calculation completed successfully.",
                )

        if decision.action == NextActionType.REQUEST_PROBE:
            next_state.phase = EpisodePhase.PROBING
            next_state.pending_probe_id = decision.probe_id
        elif decision.action == NextActionType.COMPLETE_TASK:
            next_state.phase = EpisodePhase.COMPLETED
        elif decision.action == NextActionType.FAIL_CLOSED:
            next_state.phase = EpisodePhase.STOPPED
        return next_state, decision

    def apply_probe_response(
        self,
        state: FocusEpisodeState,
        *,
        probe_id: str,
        response_code: str,
    ) -> ProbeApplicationResult:
        if state.phase != EpisodePhase.PROBING:
            raise ValueError("Probe response is only legal while episode phase is PROBING")
        if state.pending_probe_id != probe_id:
            raise ValueError("Probe response does not match the pending probe")
        if state.probe_budget_remaining <= 0:
            raise ValueError("Probe budget is exhausted")

        probe_result = self._probes.evaluate(
            snapshot=state.learner,
            probe_id=probe_id,
            response_code=response_code,
        )
        next_state = state.model_copy(deep=True)
        next_state.learner = probe_result.snapshot
        next_state.probe_evidence[probe_id] = probe_result.evidence_kind
        next_state.flags.update(probe_result.derived_flags)
        next_state.used_probe_ids.add(probe_id)
        next_state.probe_budget_remaining -= 1
        next_state.pending_probe_id = None
        next_state.phase = EpisodePhase.WORKSPACE

        if next_state.last_judgment is None:
            raise ValueError("Cannot re-route probe evidence without a prior attempt")

        decision = self._pipeline.decide_after_attempt(
            next_state,
            judgment=next_state.last_judgment,
            observations=next_state.last_observations,
        )
        return ProbeApplicationResult(
            state=next_state,
            probe_result=probe_result,
            decision=decision,
        )

    def begin_repair(
        self,
        state: FocusEpisodeState,
        decision: FocusDecision,
    ) -> FocusEpisodeState:
        if decision.action != NextActionType.START_REPAIR:
            raise ValueError("begin_repair requires START_REPAIR decision")
        if not decision.target_kc or not decision.intervention_id:
            raise ValueError("START_REPAIR decision is incomplete")
        if not decision.repair_edge_id and not decision.diagnostic_route_id:
            raise ValueError("START_REPAIR must originate from a repair edge or diagnostic route")

        transition = self._state_service.apply(
            state.learner,
            LearnerEvidenceEvent(
                event_type=LearnerEvidenceEventType.REPAIR_STARTED,
                target_kc=decision.target_kc,
                barrier_id=decision.barrier_id,
            ),
        )
        next_state = state.model_copy(deep=True)
        next_state.learner = transition.snapshot
        next_state.phase = EpisodePhase.REPAIRING
        next_state.repair_kc = decision.target_kc
        next_state.repair_edge_id = decision.repair_edge_id
        next_state.repair_diagnostic_route_id = decision.diagnostic_route_id
        next_state.repair_barrier_id = decision.barrier_id
        next_state.repair_intervention_id = decision.intervention_id
        return next_state

    def record_repair_action_success(self, state: FocusEpisodeState) -> FocusEpisodeState:
        self._require_repair_state(state, EpisodePhase.REPAIRING)
        next_state = state.model_copy(deep=True)
        next_state.learner = self._state_service.apply(
            state.learner,
            LearnerEvidenceEvent(
                event_type=LearnerEvidenceEventType.REPAIR_ACTION_SUCCESS,
                target_kc=state.repair_kc,
                barrier_id=state.repair_barrier_id,
            ),
        ).snapshot
        next_state.phase = EpisodePhase.AWAITING_ORIGINAL_SELF_CORRECTION
        return next_state

    def record_original_self_correction_success(
        self,
        state: FocusEpisodeState,
    ) -> FocusEpisodeState:
        self._require_repair_state(state, EpisodePhase.AWAITING_ORIGINAL_SELF_CORRECTION)
        next_state = state.model_copy(deep=True)
        next_state.learner = self._state_service.apply(
            state.learner,
            LearnerEvidenceEvent(
                event_type=LearnerEvidenceEventType.ORIGINAL_SELF_CORRECTION_SUCCESS,
                target_kc=state.repair_kc,
                barrier_id=state.repair_barrier_id,
            ),
        ).snapshot
        next_state.phase = EpisodePhase.AWAITING_TRANSFER
        return next_state

    def record_transfer_result(
        self,
        state: FocusEpisodeState,
        *,
        success: bool,
        prior_gap_state: Optional[KCState] = None,
        prior_barrier_state: Optional[BarrierState] = None,
    ) -> FocusEpisodeState:
        self._require_repair_state(state, EpisodePhase.AWAITING_TRANSFER)
        event_type = (
            LearnerEvidenceEventType.TRANSFER_SUCCESS
            if success
            else LearnerEvidenceEventType.TRANSFER_FAILURE
        )
        transition = self._state_service.apply(
            state.learner,
            LearnerEvidenceEvent(
                event_type=event_type,
                target_kc=state.repair_kc,
                barrier_id=state.repair_barrier_id,
                prior_gap_state=prior_gap_state,
                prior_barrier_state=prior_barrier_state,
            ),
        )
        next_state = state.model_copy(deep=True)
        next_state.learner = transition.snapshot
        next_state.phase = EpisodePhase.WORKSPACE
        next_state.repair_kc = None
        next_state.repair_edge_id = None
        next_state.repair_diagnostic_route_id = None
        next_state.repair_barrier_id = None
        next_state.repair_intervention_id = None
        return next_state

    def record_retest_scheduled(
        self,
        state: FocusEpisodeState,
        *,
        target_kc: KCId,
        barrier_id: Optional[str] = None,
    ) -> FocusEpisodeState:
        transition = self._state_service.apply(
            state.learner,
            LearnerEvidenceEvent(
                event_type=LearnerEvidenceEventType.RETEST_SCHEDULED,
                target_kc=target_kc,
                barrier_id=barrier_id,
            ),
        )
        next_state = state.model_copy(deep=True)
        next_state.learner = transition.snapshot
        return next_state

    def record_delayed_retest_result(
        self,
        state: FocusEpisodeState,
        *,
        target_kc: KCId,
        success: bool,
        barrier_id: Optional[str] = None,
    ) -> FocusEpisodeState:
        event_type = (
            LearnerEvidenceEventType.DELAYED_RETEST_SUCCESS
            if success
            else LearnerEvidenceEventType.DELAYED_RETEST_FAILURE
        )
        transition = self._state_service.apply(
            state.learner,
            LearnerEvidenceEvent(
                event_type=event_type,
                target_kc=target_kc,
                barrier_id=barrier_id,
            ),
        )
        next_state = state.model_copy(deep=True)
        next_state.learner = transition.snapshot
        next_state.retest_task_context = None
        return next_state

    @staticmethod
    def _require_repair_state(state: FocusEpisodeState, phase: EpisodePhase) -> None:
        if state.phase != phase or state.repair_kc is None:
            raise ValueError(f"Expected repair phase {phase.value}")
