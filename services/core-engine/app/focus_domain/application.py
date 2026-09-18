from __future__ import annotations

from enum import Enum
from typing import Any, FrozenSet, List, Optional

from pydantic import BaseModel, Field

from .attempt_language import NormalizedAttempt, SupportedAttemptNormalizer
from .decision_pipeline import FocusDecision, FocusEpisodeState
from .models import (
    AttemptActionType,
    AttemptJudgment,
    BranchAssignmentStatus,
    BranchWorkItem,
    BranchWorkSet,
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
    StageId,
)
from .observations import ErrorObservationProducer
from .persistence import (
    EpisodeNotFound,
    EventJournalConflict,
    FocusEpisodePersistenceService,
    FocusEvent,
    FocusEventType,
)
from .stage_judgment import (
    CTINEQ1StageJudgmentService,
    CTLIN1StageJudgmentService,
    CTPAR1StageJudgmentService,
    CTPOLY1StageJudgmentService,
    CTTRIG1StageJudgmentService,
    CTLOG1StageJudgmentService,
    CTLIM1StageJudgmentService,
    CTDERIV1StageJudgmentService,
    CTINT1StageJudgmentService,
    CTQF1StageJudgmentService,
    StageJudgmentResult,
)
from .truth_adapter import AlphaTruthAdapter, AlphaTruthResult


class FocusAttemptInputKind(str, Enum):
    FACTOR_PAIR = "FACTOR_PAIR"
    BRANCH_DECOMPOSITION = "BRANCH_DECOMPOSITION"
    BRANCH_WORK = "BRANCH_WORK"
    SOLUTION_SET = "SOLUTION_SET"
    EQUATION_REWRITE = "EQUATION_REWRITE"
    EXPRESSION_REWRITE = "EXPRESSION_REWRITE"
    VARIABLE_ASSIGNMENT = "VARIABLE_ASSIGNMENT"
    INEQUALITY_REWRITE = "INEQUALITY_REWRITE"
    COORDINATE_ASSIGNMENT = "COORDINATE_ASSIGNMENT"
    CLASSIFICATION = "CLASSIFICATION"
    ARITHMETIC_RESULT = "ARITHMETIC_RESULT"


class FocusApplicationError(ValueError):
    pass


class FocusStageMismatch(FocusApplicationError):
    pass


class FocusAttemptAssessment(BaseModel):
    normalized: NormalizedAttempt
    stage_result: StageJudgmentResult
    observations: FrozenSet[str] = frozenset()


class FocusCommandResult(BaseModel):
    episode_id: str
    stream_version: int
    state: FocusEpisodeState
    event_id: str
    event_type: str
    decision: Optional[FocusDecision] = None
    judgment: Optional[AttemptJudgment] = None
    observations: FrozenSet[str] = frozenset()
    composite_failure: Optional[str] = None
    repair_evaluation_success: Optional[bool] = None
    repair_evaluation_feedback: Optional[str] = None



class FocusEpisodeView(BaseModel):
    episode_id: str
    stream_version: int
    state: FocusEpisodeState


class CTQF1AttemptAssessmentService:
    """Server-side attempt authority for the public CT-QF1 API slice.

    The client supplies learner input only. It never supplies mathematical
    validity, ErrorObservation codes, KC state, or barrier state.
    """

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTQF1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-QF1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError(
                "Episode does not contain an authoritative CT-QF1 task context"
            )

        stage = state.current_stage
        context = state.task_context
        if isinstance(context, dict):
            context = CTQF1TaskContext.model_validate(context)

        # A complete/partial solution set is legal at every CT-QF1 stage.
        # At S1-S3 a complete set becomes VALID_SHORTCUT; a partial correct set
        # remains VALID_INCOMPLETE.
        if input_kind == FocusAttemptInputKind.SOLUTION_SET:
            normalized = self._normalizer.normalize_solution_set(raw_input)
            result = self._stage.judge_solution_set(
                normalized,
                expected_roots=frozenset(context.expected_roots),
                current_stage=stage,
            )
            observations = self._observations_for_result(
                state=state,
                result=result,
                normalized=normalized,
                attempt_id=attempt_id,
            )
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S1_FACTOR:
            if input_kind != FocusAttemptInputKind.FACTOR_PAIR:
                return self._unsupported_kind(stage, input_kind)
            normalized = self._normalizer.normalize_factor_pair(raw_input)
            result = self._stage.judge_factor_pair(
                normalized,
                expected_pair=context.factor_pair,
            )
            observations: FrozenSet[str] = frozenset()
            if (
                result.judgment == AttemptJudgment.INVALID_MATHEMATICS
                and normalized.factor_pair is not None
            ):
                truth = self._truth.check_factor_pair(
                    b=context.b,
                    c=context.c,
                    pair=normalized.factor_pair,
                )
                observations = self._produce_observations(
                    judgment=result.judgment,
                    truth=truth,
                    attempt_id=attempt_id,
                )
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_BRANCH:
            if input_kind != FocusAttemptInputKind.BRANCH_DECOMPOSITION:
                return self._unsupported_kind(stage, input_kind)
            normalized = self._normalizer.normalize_branch_decomposition(raw_input)
            result = self._stage.judge_branch_decomposition(
                normalized,
                expected_branch_equations=context.expected_branch_equations,
            )
            observations = self._observations_for_result(
                state=state,
                result=result,
                normalized=normalized,
                attempt_id=attempt_id,
            )
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_SOLVE_FACTOR_EQUATIONS:
            if input_kind != FocusAttemptInputKind.BRANCH_WORK:
                return self._unsupported_kind(stage, input_kind)
            return self._assess_branch_work(
                state=state,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )

        if stage == StageId.S4_COMPLETE_SOLUTION_SET:
            return self._unsupported_kind(stage, input_kind)

        raise FocusApplicationError(f"Unsupported CT-QF1 stage: {stage}")

    def _assess_branch_work(
        self,
        *,
        state: FocusEpisodeState,
        raw_input: Any,
        attempt_id: Optional[str],
    ) -> FocusAttemptAssessment:
        context = state.task_context
        assert context is not None
        if isinstance(context, dict):
            context = CTQF1TaskContext.model_validate(context)

        if not isinstance(raw_input, dict):
            return self._unsupported_kind(
                StageId.S3_SOLVE_FACTOR_EQUATIONS,
                FocusAttemptInputKind.BRANCH_WORK,
            )

        expected: dict[str, int] = {}
        for constant in context.factor_pair:
            equation = (
                f"x+{constant}=0"
                if constant > 0
                else f"x-{abs(constant)}=0"
            )
            expected[equation] = -constant

        extra = set(str(key).replace(" ", "") for key in raw_input) - set(expected)
        normalized = NormalizedAttempt(
            status="SUPPORTED",
            action_type=AttemptActionType.SOLUTION_ASSIGNMENT,
            canonical_text=str(raw_input),
        )
        if extra:
            result = StageJudgmentResult(
                stage_id=StageId.S3_SOLVE_FACTOR_EQUATIONS,
                judgment=AttemptJudgment.INVALID_MATHEMATICS,
                reason="Branch work contains a factor equation that is not part of the current task.",
            )
            observations = self._observations_for_result(
                state=state,
                result=result,
                normalized=normalized,
                attempt_id=attempt_id,
            )
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        items = []
        for index, (equation, expected_root) in enumerate(sorted(expected.items()), start=1):
            raw_assignment = None
            for raw_key, raw_value in raw_input.items():
                if str(raw_key).replace(" ", "") == equation:
                    raw_assignment = raw_value
                    break

            status = BranchAssignmentStatus.PENDING
            observed_attempt_id = None
            if raw_assignment is not None:
                assignment = self._normalizer.normalize_assignment(raw_assignment)
                observed_attempt_id = attempt_id
                if assignment.status.value != "SUPPORTED":
                    status = BranchAssignmentStatus.UNSUPPORTED
                elif assignment.assignment is not None and assignment.assignment.value == expected_root:
                    status = BranchAssignmentStatus.VALID
                else:
                    status = BranchAssignmentStatus.INVALID

            items.append(
                BranchWorkItem(
                    branch_id=f"B{index}",
                    source_factor=equation[:-2],
                    expected_equation=equation,
                    expected_assignment=f"x={expected_root}",
                    assignment_status=status,
                    observed_attempt_id=observed_attempt_id,
                )
            )

        branch_work = BranchWorkSet(branch_items=items)
        result = self._stage.judge_branch_work_set(branch_work)
        observations = self._observations_for_result(
            state=state,
            result=result,
            normalized=normalized,
            attempt_id=attempt_id,
        )
        return FocusAttemptAssessment(
            normalized=normalized,
            stage_result=result,
            observations=observations,
        )

    def _unsupported_kind(
        self,
        stage: StageId,
        input_kind: FocusAttemptInputKind,
    ) -> FocusAttemptAssessment:
        normalized = NormalizedAttempt(
            status="UNSUPPORTED_STEP_FORM",
            action_type=(
                "FACTOR_PAIR_SELECTION"
                if input_kind == FocusAttemptInputKind.FACTOR_PAIR
                else "BRANCH_DECOMPOSITION"
                if input_kind == FocusAttemptInputKind.BRANCH_DECOMPOSITION
                else "SOLUTION_ASSIGNMENT"
                if input_kind == FocusAttemptInputKind.BRANCH_WORK
                else "SOLUTION_SET"
            ),
            reason=f"{input_kind.value} is not an accepted input surface for {stage.value}.",
        )
        result = StageJudgmentResult(
            stage_id=stage,
            judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
            reason=normalized.reason or "Unsupported attempt surface.",
        )
        return FocusAttemptAssessment(normalized=normalized, stage_result=result)

    def _observations_for_result(
        self,
        *,
        state: FocusEpisodeState,
        result: StageJudgmentResult,
        normalized: NormalizedAttempt,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        if result.judgment != AttemptJudgment.INVALID_MATHEMATICS:
            return frozenset()

        # For currently unsupported fine-grained classifications (e.g. an
        # arbitrary wrong branch/root set), preserve deterministic invalidity
        # without inventing a specific misconception.
        truth = AlphaTruthResult(
            target_kc=state.workspace_kc,
            is_valid=False,
            facts=frozenset(),
            expected={"stage": result.stage_id.value},
            observed={"input": normalized.canonical_text or "supported-input"},
            reason=result.reason,
        )
        return self._produce_observations(
            judgment=result.judgment,
            truth=truth,
            attempt_id=attempt_id,
        )

    def _produce_observations(
        self,
        *,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTLIN1AttemptAssessmentService:
    """Server-side attempt authority for CT-LIN1 linear equations (ax + b = c)."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTLIN1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-LIN1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError("Episode does not contain an authoritative CT-LIN1 task context")

        stage = state.current_stage
        context: CTLIN1TaskContext = state.task_context
        if isinstance(context, dict):
            context = CTLIN1TaskContext.model_validate(context)

        if stage == StageId.S1_ISOLATE_TERM:
            normalized = self._normalizer.normalize_linear_equation(raw_input)
            result = self._stage.judge_isolate_term(
                normalized,
                expected_coeff=context.a,
                expected_rhs=context.expected_intermediate_rhs,
            )
            observations: FrozenSet[str] = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS and normalized.linear_rhs is not None:
                truth = self._truth.check_linear_term_isolation(
                    a=context.a,
                    b=context.b,
                    c=context.c,
                    observed_rhs=normalized.linear_rhs,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_ISOLATE_VARIABLE:
            if isinstance(raw_input, str) and "=" in raw_input:
                normalized = self._normalizer.normalize_assignment(raw_input)
            else:
                normalized = self._normalizer.normalize_integer(raw_input)
            result = self._stage.judge_isolate_variable(
                normalized,
                expected_root=context.expected_root,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                observed_val = (
                    normalized.assignment.value
                    if normalized.assignment is not None
                    else normalized.integer_value
                )
                if observed_val is not None:
                    truth = self._truth.check_linear_coefficient_division(
                        a=context.a,
                        d=context.expected_intermediate_rhs,
                        observed_x=observed_val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_VERIFY_SOLUTION:
            if isinstance(raw_input, int):
                normalized = self._normalizer.normalize_integer(raw_input)
            elif isinstance(raw_input, str) and "=" in raw_input:
                normalized = self._normalizer.normalize_assignment(raw_input)
            else:
                normalized = self._normalizer.normalize_integer(context.expected_root)
            result = self._stage.judge_verification(normalized, expected_root=context.expected_root)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=frozenset(),
            )

        raise FocusApplicationError(f"Unsupported CT-LIN1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTINEQ1AttemptAssessmentService:
    """Server-side attempt authority for CT-INEQ1 linear inequalities (ax + b <= c)."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTINEQ1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-INEQ1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError("Episode does not contain an authoritative CT-INEQ1 task context")

        stage = state.current_stage
        context: CTINEQ1TaskContext = state.task_context
        if isinstance(context, dict):
            context = CTINEQ1TaskContext.model_validate(context)

        if stage == StageId.S1_ISOLATE_TERM:
            normalized = self._normalizer.normalize_linear_inequality(raw_input)
            result = self._stage.judge_isolate_term(
                normalized,
                expected_coeff=context.a,
                expected_rhs=context.expected_intermediate_rhs,
                expected_comparator=context.comparator,
            )
            observations: FrozenSet[str] = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS and normalized.linear_rhs is not None:
                truth = self._truth.check_linear_term_isolation(
                    a=context.a,
                    b=context.b,
                    c=context.c,
                    observed_rhs=normalized.linear_rhs,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_DIRECTION_AWARE_DIVISION:
            normalized = self._normalizer.normalize_linear_inequality(raw_input)
            result = self._stage.judge_direction_division(
                normalized,
                expected_root=context.expected_root,
                expected_comparator=context.expected_comparator,
            )
            observations = frozenset()
            if (
                result.judgment == AttemptJudgment.INVALID_MATHEMATICS
                and normalized.linear_rhs is not None
                and normalized.comparator is not None
            ):
                truth = self._truth.check_inequality_division(
                    a=context.a,
                    d=context.expected_intermediate_rhs,
                    original_comparator=context.comparator,
                    observed_comparator=normalized.comparator,
                    observed_x=normalized.linear_rhs,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-INEQ1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTPAR1AttemptAssessmentService:
    """Focus attempt assessment service for CT-PAR1 parabola vertex."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTPAR1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-PAR1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError("Episode does not contain an authoritative CT-PAR1 task context")

        stage = state.current_stage
        context: CTPAR1TaskContext = state.task_context
        if isinstance(context, dict):
            context = CTPAR1TaskContext.model_validate(context)

        if stage == StageId.S1_CALCULATE_R:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="r")
            result = self._stage.judge_calculate_r(normalized, expected_r=context.expected_r)
            observations: FrozenSet[str] = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.float_value
                    if normalized.float_value is not None
                    else (float(normalized.integer_value) if normalized.integer_value is not None else None)
                )
                if val is not None:
                    truth = self._truth.check_parabola_vertex_r(
                        a=context.a,
                        b=context.b,
                        observed_r=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_CALCULATE_K:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="k")
            result = self._stage.judge_calculate_k(normalized, expected_k=context.expected_k)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.float_value
                    if normalized.float_value is not None
                    else (float(normalized.integer_value) if normalized.integer_value is not None else None)
                )
                if val is not None:
                    truth = self._truth.check_parabola_vertex_k(
                        a=context.a,
                        b=context.b,
                        c=context.c,
                        r=context.expected_r,
                        observed_k=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_EXTREMUM_CLASSIFICATION:
            normalized = self._normalizer.normalize_classification(raw_input)
            result = self._stage.judge_extremum(normalized, expected_is_min=context.is_minimum)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS and normalized.classification is not None:
                truth = self._truth.check_parabola_extremum(
                    a=context.a,
                    observed_is_min=(normalized.classification == "minimum"),
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-PAR1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTPOLY1AttemptAssessmentService:
    """Focus attempt assessment service for CT-POLY1 polynomial remainder."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTPOLY1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-POLY1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError("Episode does not contain an authoritative CT-POLY1 task context")

        stage = state.current_stage
        context: CTPOLY1TaskContext = state.task_context
        if isinstance(context, dict):
            context = CTPOLY1TaskContext.model_validate(context)

        if stage == StageId.S1_ROOT_OF_DIVISOR:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="x")
            result = self._stage.judge_divisor_root(normalized, expected_root=context.divisor_root)
            observations: FrozenSet[str] = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.integer_value
                    if normalized.integer_value is not None
                    else (int(normalized.float_value) if normalized.float_value is not None and normalized.float_value.is_integer() else None)
                )
                if val is not None:
                    truth = self._truth.check_polynomial_divisor_root(
                        divisor_root=context.divisor_root,
                        observed_root=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_EVALUATE_REMAINDER:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="kalan")
            result = self._stage.judge_remainder(normalized, expected_remainder=context.expected_remainder)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.integer_value
                    if normalized.integer_value is not None
                    else (int(normalized.float_value) if normalized.float_value is not None and normalized.float_value.is_integer() else None)
                )
                if val is not None:
                    truth = self._truth.check_polynomial_remainder(
                        a=context.a,
                        b=context.b,
                        c=context.c,
                        divisor_root=context.divisor_root,
                        observed_rem=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-POLY1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTTRIG1AttemptAssessmentService:
    """Focus attempt assessment service for CT-TRIG1 trigonometric equation."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTTRIG1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-TRIG1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError("Episode does not contain an authoritative CT-TRIG1 task context")

        stage = state.current_stage
        context: CTTRIG1TaskContext = state.task_context
        if isinstance(context, dict):
            context = CTTRIG1TaskContext.model_validate(context)

        if stage == StageId.S1_ISOLATE_TRIG_VALUE:
            normalized = self._normalizer.normalize_trig_ratio(raw_input)
            result = self._stage.judge_isolate_trig_value(normalized, expected_ratio=context.expected_ratio)
            observations: FrozenSet[str] = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.float_value
                    if normalized.float_value is not None
                    else (float(normalized.integer_value) if normalized.integer_value is not None else None)
                )
                if val is not None:
                    truth = self._truth.check_trig_ratio(
                        expected_ratio=context.expected_ratio,
                        observed_ratio=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_DETERMINE_PRINCIPAL_ANGLE:
            normalized = self._normalizer.normalize_trig_angle(raw_input, var_name="x")
            result = self._stage.judge_principal_angle(normalized, expected_principal_deg=context.expected_principal_deg)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.integer_value
                    if normalized.integer_value is not None
                    else (int(round(normalized.float_value)) if normalized.float_value is not None else None)
                )
                if val is not None:
                    truth = self._truth.check_trig_principal_angle(
                        expected_principal_deg=context.expected_principal_deg,
                        observed_deg=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_DETERMINE_SECONDARY_ROOT:
            normalized = self._normalizer.normalize_trig_angle(raw_input, var_name="x")
            result = self._stage.judge_secondary_root(normalized, expected_secondary_deg=context.expected_secondary_deg)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.integer_value
                    if normalized.integer_value is not None
                    else (int(round(normalized.float_value)) if normalized.float_value is not None else None)
                )
                if val is not None:
                    truth = self._truth.check_trig_secondary_root(
                        expected_secondary_deg=context.expected_secondary_deg,
                        observed_deg=val,
                        principal_deg=context.expected_principal_deg,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-TRIG1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTLOG1AttemptAssessmentService:
    """Focus attempt assessment service for CT-LOG1 logarithmic equation."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTLOG1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-LOG1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError("Episode does not contain an authoritative CT-LOG1 task context")

        stage = state.current_stage
        context: CTLOG1TaskContext = state.task_context
        if isinstance(context, dict):
            context = CTLOG1TaskContext.model_validate(context)

        if stage == StageId.S1_EXPONENTIAL_CONVERSION:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="power")
            result = self._stage.judge_exponential_conversion(normalized, expected_power=context.expected_power)
            observations: FrozenSet[str] = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.integer_value
                    if normalized.integer_value is not None
                    else (int(normalized.float_value) if normalized.float_value is not None and normalized.float_value.is_integer() else None)
                )
                if val is not None:
                    truth = self._truth.check_log_power(
                        base=context.base,
                        k=context.k,
                        expected_power=context.expected_power,
                        observed_power=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_ISOLATE_VARIABLE:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="x")
            result = self._stage.judge_isolate_variable(normalized, expected_x=context.expected_x)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.integer_value
                    if normalized.integer_value is not None
                    else (int(normalized.float_value) if normalized.float_value is not None and normalized.float_value.is_integer() else None)
                )
                if val is not None:
                    truth = self._truth.check_log_solution(
                        expected_x=context.expected_x,
                        observed_x=val,
                    )
                    observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_VERIFY_DOMAIN_CONSTRAINT:
            normalized = self._normalizer.normalize_domain_validity(raw_input)
            result = self._stage.judge_domain_constraint(normalized, is_domain_valid=context.is_domain_valid)
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                obs_valid = normalized.boolean_value if normalized.boolean_value is not None else (normalized.classification == "gecerli")
                truth = self._truth.check_log_domain_constraint(
                    is_domain_valid=context.is_domain_valid,
                    observed_valid=obs_valid,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-LOG1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTLIM1AttemptAssessmentService:
    """Server-side attempt authority for the public CT-LIM1 0/0 limit API slice."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTLIM1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-LIM1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError(
                "Episode does not contain an authoritative CT-LIM1 task context"
            )

        stage = state.current_stage
        context = state.task_context
        if isinstance(context, dict):
            context = CTLIM1TaskContext.model_validate(context)

        if stage == StageId.S1_EVALUATE_LIMIT_FORM:
            normalized = self._normalizer.normalize_limit_form(raw_input)
            result = self._stage.judge_limit_form(
                normalized,
                expected_form=context.expected_indeterminate_form,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                truth = self._truth.check_limit_form(
                    observed_form=normalized.classification or normalized.canonical_text or "",
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_SIMPLIFY_EXPRESSION:
            normalized = self._normalizer.normalize_simplified_expression(raw_input)
            result = self._stage.judge_simplified_expression(
                normalized,
                expected_expression=context.expected_simplified_expr,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                truth = self._truth.check_limit_simplification(
                    expected_expr=context.expected_simplified_expr,
                    observed_expr=normalized.canonical_text or "",
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_COMPUTE_FINAL_LIMIT:
            normalized = self._normalizer.normalize_coordinate_assignment(raw_input, var_name="L")
            result = self._stage.judge_final_limit(
                normalized,
                expected_value=context.expected_limit_val,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.float_value
                    if normalized.float_value is not None
                    else (float(normalized.integer_value) if normalized.integer_value is not None else 0.0)
                )
                truth = self._truth.check_limit_value(
                    expected_limit=context.expected_limit_val,
                    observed_limit=val,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-LIM1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTDERIV1AttemptAssessmentService:
    """Server-side attempt authority for the public CT-DERIV1 derivative & tangent API slice."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTDERIV1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-DERIV1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError(
                "Episode does not contain an authoritative CT-DERIV1 task context"
            )

        stage = state.current_stage
        context = state.task_context
        if isinstance(context, dict):
            context = CTDERIV1TaskContext.model_validate(context)

        if stage == StageId.S1_COMPUTE_DERIVATIVE:
            normalized = self._normalizer.normalize_derivative_function(raw_input)
            result = self._stage.judge_derivative_function(
                normalized,
                expected_derivative=context.expected_derivative_str,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                truth = self._truth.check_derivative_function(
                    expected_deriv=context.expected_derivative_str,
                    observed_deriv=normalized.canonical_text or "",
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_EVALUATE_SLOPE:
            normalized = self._normalizer.normalize_tangent_slope(raw_input)
            result = self._stage.judge_tangent_slope(
                normalized,
                expected_slope=context.expected_slope,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.float_value
                    if normalized.float_value is not None
                    else (float(normalized.integer_value) if normalized.integer_value is not None else 0.0)
                )
                truth = self._truth.check_tangent_slope(
                    expected_slope=context.expected_slope,
                    observed_slope=val,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_DETERMINE_TANGENT_LINE:
            normalized = self._normalizer.normalize_tangent_line(raw_input)
            result = self._stage.judge_tangent_line(
                normalized,
                expected_line=context.expected_tangent_line,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                truth = self._truth.check_tangent_line(
                    expected_line=context.expected_tangent_line,
                    observed_line=normalized.canonical_text or "",
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-DERIV1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class CTINT1AttemptAssessmentService:
    """Server-side attempt authority for the public CT-INT1 definite integral & area API slice."""

    def __init__(self) -> None:
        self._normalizer = SupportedAttemptNormalizer()
        self._stage = CTINT1StageJudgmentService()
        self._truth = AlphaTruthAdapter()
        self._observations = ErrorObservationProducer()

    def assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if (
            state.composite_task_id != "CT-INT1"
            or state.current_stage is None
            or state.task_context is None
        ):
            raise FocusApplicationError(
                "Episode does not contain an authoritative CT-INT1 task context"
            )

        stage = state.current_stage
        context = state.task_context
        if isinstance(context, dict):
            context = CTINT1TaskContext.model_validate(context)

        if stage == StageId.S1_FIND_ANTIDERIVATIVE:
            normalized = self._normalizer.normalize_antiderivative(raw_input)
            result = self._stage.judge_antiderivative(
                normalized,
                expected_antiderivative=context.expected_antiderivative_str,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                truth = self._truth.check_antiderivative(
                    expected_antideriv=context.expected_antiderivative_str,
                    observed_antideriv=normalized.canonical_text or "",
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S2_APPLY_LIMITS:
            normalized = self._normalizer.normalize_integral_limits_difference(raw_input)
            expected_diff_str = (
                f"{int(context.expected_f_b)} - {int(context.expected_f_a)}"
                if context.expected_f_b.is_integer() and context.expected_f_a.is_integer()
                else f"{context.expected_f_b} - {context.expected_f_a}"
            )
            result = self._stage.judge_integral_limits_evaluation(
                normalized,
                expected_diff_str=expected_diff_str,
                expected_diff_val=context.expected_definite_integral,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                truth = self._truth.check_integral_limits_evaluation(
                    expected_diff_str=expected_diff_str,
                    observed_diff_str=normalized.canonical_text or "",
                    expected_diff_val=context.expected_definite_integral,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        if stage == StageId.S3_COMPUTE_DEFINITE_INTEGRAL:
            normalized = self._normalizer.normalize_definite_integral_value(raw_input)
            result = self._stage.judge_definite_integral_value(
                normalized,
                expected_value=context.expected_definite_integral,
            )
            observations = frozenset()
            if result.judgment == AttemptJudgment.INVALID_MATHEMATICS:
                val = (
                    normalized.float_value
                    if normalized.float_value is not None
                    else (float(normalized.integer_value) if normalized.integer_value is not None else 0.0)
                )
                truth = self._truth.check_definite_integral_value(
                    expected_val=context.expected_definite_integral,
                    observed_val=val,
                )
                observations = self._produce_observations(result.judgment, truth, attempt_id)
            return FocusAttemptAssessment(
                normalized=normalized,
                stage_result=result,
                observations=observations,
            )

        raise FocusApplicationError(f"Unsupported CT-INT1 stage: {stage}")

    def _produce_observations(
        self,
        judgment: AttemptJudgment,
        truth: AlphaTruthResult,
        attempt_id: Optional[str],
    ) -> FrozenSet[str]:
        return frozenset(
            observation.code.value
            for observation in self._observations.produce(
                attempt_judgment=judgment,
                truth_result=truth,
                attempt_id=attempt_id,
            )
        )


class FocusServiceFacade:
    """Application boundary around the event-sourced Focus kernel."""

    def __init__(
        self,
        persistence: Optional[FocusEpisodePersistenceService] = None,
    ) -> None:
        self.persistence = persistence or FocusEpisodePersistenceService()
        self._ctqf1_assessor = CTQF1AttemptAssessmentService()
        self._ctlin1_assessor = CTLIN1AttemptAssessmentService()
        self._ctineq1_assessor = CTINEQ1AttemptAssessmentService()
        self._ctpar1_assessor = CTPAR1AttemptAssessmentService()
        self._ctpoly1_assessor = CTPOLY1AttemptAssessmentService()
        self._cttrig1_assessor = CTTRIG1AttemptAssessmentService()
        self._ctlog1_assessor = CTLOG1AttemptAssessmentService()
        self._ctlim1_assessor = CTLIM1AttemptAssessmentService()
        self._ctderiv1_assessor = CTDERIV1AttemptAssessmentService()
        self._ctint1_assessor = CTINT1AttemptAssessmentService()
        self._assessor = self._ctqf1_assessor

    def _assess(
        self,
        *,
        state: FocusEpisodeState,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        attempt_id: Optional[str] = None,
    ) -> FocusAttemptAssessment:
        if state.composite_task_id == "CT-LIN1":
            return self._ctlin1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-INEQ1":
            return self._ctineq1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-PAR1":
            return self._ctpar1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-POLY1":
            return self._ctpoly1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-TRIG1":
            return self._cttrig1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-LOG1":
            return self._ctlog1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-LIM1":
            return self._ctlim1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-DERIV1":
            return self._ctderiv1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        if state.composite_task_id == "CT-INT1":
            return self._ctint1_assessor.assess(
                state=state,
                input_kind=input_kind,
                raw_input=raw_input,
                attempt_id=attempt_id,
            )
        return self._ctqf1_assessor.assess(
            state=state,
            input_kind=input_kind,
            raw_input=raw_input,
            attempt_id=attempt_id,
        )

    def start_ctqf1_episode(
        self,
        *,
        episode_id: str,
        b: int,
        c: int,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTQF1TaskContext.from_coefficients(b=b, c=c)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.F2,
            composite_task_id="CT-QF1",
            current_stage=StageId.S1_FACTOR,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctlin1_episode(
        self,
        *,
        episode_id: str,
        a: int,
        b: int,
        c: int,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTLIN1TaskContext.from_coefficients(a=a, b=b, c=c)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.L1,
            composite_task_id="CT-LIN1",
            current_stage=StageId.S1_ISOLATE_TERM,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctineq1_episode(
        self,
        *,
        episode_id: str,
        a: int,
        b: int,
        c: int,
        comparator: str = "<=",
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTINEQ1TaskContext.from_coefficients(a=a, b=b, c=c, comparator=comparator)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.I1,
            composite_task_id="CT-INEQ1",
            current_stage=StageId.S1_ISOLATE_TERM,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctpar1_episode(
        self,
        *,
        episode_id: str,
        a: int = 1,
        b: int = -4,
        c: int = 3,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTPAR1TaskContext.from_coefficients(a=a, b=b, c=c)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.P1,
            composite_task_id="CT-PAR1",
            current_stage=StageId.S1_CALCULATE_R,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctpoly1_episode(
        self,
        *,
        episode_id: str,
        a: int = 1,
        b: int = 2,
        c: int = -3,
        divisor_root: int = 1,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTPOLY1TaskContext.from_coefficients(
                a=a, b=b, c=c, divisor_root=divisor_root
            )
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.PL1,
            composite_task_id="CT-POLY1",
            current_stage=StageId.S1_ROOT_OF_DIVISOR,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_cttrig1_episode(
        self,
        *,
        episode_id: str,
        a: int = 2,
        c: int = 1,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTTRIG1TaskContext.from_coefficients(a=a, c=c)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.TR1,
            composite_task_id="CT-TRIG1",
            current_stage=StageId.S1_ISOLATE_TRIG_VALUE,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctlog1_episode(
        self,
        *,
        episode_id: str,
        base: int = 2,
        c: int = 3,
        k: int = 3,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTLOG1TaskContext.from_parameters(base=base, c=c, k=k)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.LG1,
            composite_task_id="CT-LOG1",
            current_stage=StageId.S1_EXPONENTIAL_CONVERSION,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctlim1_episode(
        self,
        *,
        episode_id: str,
        a: int = 2,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTLIM1TaskContext.from_parameters(a=a)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.LM1,
            composite_task_id="CT-LIM1",
            current_stage=StageId.S1_EVALUATE_LIMIT_FORM,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctderiv1_episode(
        self,
        *,
        episode_id: str,
        a: int = 1,
        b: int = -3,
        c: int = 2,
        x0: int = 2,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTDERIV1TaskContext.from_coefficients(a=a, b=b, c=c, x0=x0)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.DV1,
            composite_task_id="CT-DERIV1",
            current_stage=StageId.S1_COMPUTE_DERIVATIVE,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_ctint1_episode(
        self,
        *,
        episode_id: str,
        m: int = 2,
        n: int = 0,
        a: int = 0,
        b: int = 3,
        idempotency_key: str,
    ) -> FocusCommandResult:
        try:
            context = CTINT1TaskContext.from_parameters(m=m, n=n, a=a, b=b)
        except ValueError as exc:
            raise FocusApplicationError(str(exc)) from exc
        initial = FocusEpisodeState(
            workspace_kc=KCId.IN1,
            composite_task_id="CT-INT1",
            current_stage=StageId.S1_FIND_ANTIDERIVATIVE,
            task_context=context,
        )
        state, event = self.persistence.start_episode(
            episode_id=episode_id,
            initial_state=initial,
            idempotency_key=idempotency_key,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
        )

    def start_episode(
        self,
        *,
        episode_id: str,
        topic_id: str = "CT-QF1",
        a: Optional[int] = None,
        b: int = 5,
        c: int = 6,
        divisor_root: Optional[int] = None,
        comparator: str = "<=",
        idempotency_key: str,
    ) -> FocusCommandResult:
        if topic_id == "CT-LIN1":
            return self.start_ctlin1_episode(
                episode_id=episode_id,
                a=a or 1,
                b=b,
                c=c,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-INEQ1":
            return self.start_ctineq1_episode(
                episode_id=episode_id,
                a=a or 1,
                b=b,
                c=c,
                comparator=comparator,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-PAR1":
            return self.start_ctpar1_episode(
                episode_id=episode_id,
                a=a if a is not None else 1,
                b=b,
                c=c,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-POLY1":
            return self.start_ctpoly1_episode(
                episode_id=episode_id,
                a=a if a is not None else 1,
                b=b,
                c=c,
                divisor_root=divisor_root if divisor_root is not None else 1,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-TRIG1":
            return self.start_cttrig1_episode(
                episode_id=episode_id,
                a=a if a is not None else 2,
                c=c if c is not None else 1,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-LOG1":
            return self.start_ctlog1_episode(
                episode_id=episode_id,
                base=a if a is not None else 2,
                c=b if b is not None else 3,
                k=c if c is not None else 3,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-LIM1":
            return self.start_ctlim1_episode(
                episode_id=episode_id,
                a=a if a is not None else 2,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-DERIV1":
            return self.start_ctderiv1_episode(
                episode_id=episode_id,
                a=a if a is not None else 1,
                b=b,
                c=c,
                x0=divisor_root if divisor_root is not None else 2,
                idempotency_key=idempotency_key,
            )
        if topic_id == "CT-INT1":
            return self.start_ctint1_episode(
                episode_id=episode_id,
                m=a if a is not None else 2,
                n=b if b is not None else 0,
                a=divisor_root if divisor_root is not None else 0,
                b=c if c is not None else 3,
                idempotency_key=idempotency_key,
            )
        return self.start_ctqf1_episode(
            episode_id=episode_id,
            b=b,
            c=c,
            idempotency_key=idempotency_key,
        )

    def get_episode(self, episode_id: str) -> FocusEpisodeView:
        state = self.persistence.load(episode_id)
        event = self.persistence.journal.last_event(episode_id)
        if event is None:
            raise EpisodeNotFound(episode_id)
        return FocusEpisodeView(
            episode_id=episode_id,
            stream_version=event.sequence,
            state=state,
        )

    def submit_attempt(
        self,
        *,
        episode_id: str,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        idempotency_key: str,
        expected_previous_sequence: int,
    ) -> FocusCommandResult:
        client_command = {
            "input_kind": input_kind.value,
            "raw_input": raw_input,
        }
        existing = self.persistence.journal.get_by_idempotency_key(
            episode_id,
            idempotency_key,
        )
        if existing is not None:
            if (
                existing.event_type != FocusEventType.ATTEMPT_HANDLED
                or existing.payload.get("client_command") != client_command
            ):
                raise EventJournalConflict(
                    "Idempotency key was already used for a different Focus command"
                )
            historical_state = self.persistence.load_at_sequence(
                episode_id,
                existing.sequence,
            )
            return self._command_result(
                episode_id=episode_id,
                state=historical_state,
                event=existing,
                decision=FocusDecision.model_validate(existing.payload["decision"]),
                judgment=AttemptJudgment(str(existing.payload["judgment"])),
                observations=frozenset(
                    str(value) for value in existing.payload.get("observations", [])
                ),
                normalized_input=existing.payload.get("normalized_input"),
                composite_failure=existing.payload.get("composite_failure"),
            )

        current_seq = self.persistence._current_sequence(episode_id)
        if 0 < expected_previous_sequence <= current_seq:
            state = self.persistence.load_at_sequence(
                episode_id,
                expected_previous_sequence,
            )
        else:
            state = self.persistence.load(episode_id)
        assessment = self._assess(
            state=state,
            input_kind=input_kind,
            raw_input=raw_input,
            attempt_id=idempotency_key,
        )
        next_state, decision, event = self.persistence.handle_attempt(
            episode_id=episode_id,
            judgment=assessment.stage_result.judgment,
            observations=assessment.observations,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
            command_metadata={
                "client_command": client_command,
                "normalized_input": assessment.normalized.canonical_text,
                "composite_failure": (
                    assessment.stage_result.composite_failure.value
                    if assessment.stage_result.composite_failure
                    else None
                ),
            },
        )
        return self._command_result(
            episode_id=episode_id,
            state=next_state,
            event=event,
            decision=decision,
            judgment=assessment.stage_result.judgment,
            observations=assessment.observations,
            normalized_input=assessment.normalized.canonical_text,
            composite_failure=(
                assessment.stage_result.composite_failure.value
                if assessment.stage_result.composite_failure
                else None
            ),
        )

    def apply_probe_response(
        self,
        *,
        episode_id: str,
        probe_id: str,
        response_code: str,
        idempotency_key: str,
        expected_previous_sequence: int,
    ) -> FocusCommandResult:
        state, decision, event = self.persistence.apply_probe_response(
            episode_id=episode_id,
            probe_id=probe_id,
            response_code=response_code,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            decision=decision,
        )

    def begin_current_repair(
        self,
        *,
        episode_id: str,
        idempotency_key: str,
        expected_previous_sequence: int,
    ) -> FocusCommandResult:
        state, decision, event = self.persistence.begin_current_repair(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
        )
        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            decision=decision,
        )

    @staticmethod
    def _command_result(
        *,
        episode_id: str,
        state: FocusEpisodeState,
        event: FocusEvent,
        decision: Optional[FocusDecision] = None,
        judgment: Optional[AttemptJudgment] = None,
        observations: FrozenSet[str] = frozenset(),
        normalized_input: Optional[str] = None,
        composite_failure: Optional[str] = None,
        repair_evaluation_success: Optional[bool] = None,
        repair_evaluation_feedback: Optional[str] = None,
    ) -> FocusCommandResult:
        return FocusCommandResult(
            episode_id=episode_id,
            stream_version=event.sequence,
            state=state,
            event_id=event.event_id,
            event_type=event.event_type.value,
            decision=decision,
            judgment=judgment,
            observations=observations,
            normalized_input=normalized_input,
            composite_failure=composite_failure,
            repair_evaluation_success=repair_evaluation_success,
            repair_evaluation_feedback=repair_evaluation_feedback,
        )

    def submit_repair_work(
        self,
        *,
        episode_id: str,
        raw_work: Any,
        idempotency_key: str,
        expected_previous_sequence: int,
    ) -> FocusCommandResult:
        """Evaluate learner work on an active intervention and advance or stay."""
        from .repair_work_evaluator import RepairWorkEvaluator, TransferTaskGenerator

        current = self.persistence.load(episode_id)
        if current.phase.value != "REPAIRING" or not current.repair_intervention_id:
            raise FocusApplicationError("Episode is not in an active REPAIRING phase")

        evaluator = RepairWorkEvaluator()
        ctx = current.task_context
        ctx_dict = None
        if ctx is not None:
            ctx_b = ctx.get("b", 0) if isinstance(ctx, dict) else getattr(ctx, "b", 0)
            ctx_c = ctx.get("c", 0) if isinstance(ctx, dict) else getattr(ctx, "c", 0)
            ctx_dict = {"b": ctx_b, "c": ctx_c}

        result = evaluator.evaluate_repair(
            intervention_id=current.repair_intervention_id,
            raw_work=raw_work,
            context=ctx_dict,
        )

        if not result.is_success:
            raise FocusApplicationError(
                f"Repair work was incorrect: {result.feedback}"
            )

        transfer_task = None
        if current.repair_kc:
            transfer_task = TransferTaskGenerator.generate_transfer_task(current.repair_kc)

        state, event = self.persistence.record_repair_action_success(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            transfer_task_context=transfer_task,
            expected_previous_sequence=expected_previous_sequence,
        )

        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            repair_evaluation_success=True,
            repair_evaluation_feedback=result.feedback,
        )

    def submit_original_self_correction(
        self,
        *,
        episode_id: str,
        input_kind: FocusAttemptInputKind,
        raw_input: Any,
        idempotency_key: str,
        expected_previous_sequence: int,
    ) -> FocusCommandResult:
        """Evaluate self-correction attempt on the original problem step."""
        current = self.persistence.load(episode_id)
        if current.phase.value != "AWAITING_ORIGINAL_SELF_CORRECTION":
            raise FocusApplicationError(
                "Episode is not in AWAITING_ORIGINAL_SELF_CORRECTION phase"
            )

        assessment = self._assess(
            state=current,
            input_kind=input_kind,
            raw_input=raw_input,
            attempt_id=idempotency_key,
        )

        if assessment.stage_result.judgment != AttemptJudgment.VALID_EXPECTED:
            raise FocusApplicationError(
                f"Self-correction failed with judgment {assessment.stage_result.judgment.value}"
            )

        state, event = self.persistence.record_original_self_correction_success(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
        )

        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            judgment=assessment.stage_result.judgment,
            repair_evaluation_success=True,
            repair_evaluation_feedback="Original self-correction succeeded.",
        )

    def submit_transfer_work(
        self,
        *,
        episode_id: str,
        raw_work: Any,
        idempotency_key: str,
        expected_previous_sequence: int,
    ) -> FocusCommandResult:
        """Evaluate learner work on the server-owned transfer problem."""
        from .repair_work_evaluator import RepairWorkEvaluator

        current = self.persistence.load(episode_id)
        if current.phase.value != "AWAITING_TRANSFER":
            raise FocusApplicationError("Episode is not in AWAITING_TRANSFER phase")

        evaluator = RepairWorkEvaluator()
        transfer_context = current.transfer_task_context or {
            "expected_answer": "valid",
            "target_kc": current.repair_kc.value if current.repair_kc else "KC-N1",
        }
        result = evaluator.evaluate_transfer(
            transfer_context=transfer_context,
            raw_work=raw_work,
        )

        state, event = self.persistence.record_transfer_result(
            episode_id=episode_id,
            success=result.is_success,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
        )

        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            repair_evaluation_success=result.is_success,
            repair_evaluation_feedback=result.feedback,
        )

    def schedule_retest(
        self,
        *,
        episode_id: str,
        target_kc: KCId,
        idempotency_key: str,
        expected_previous_sequence: int,
        barrier_id: Optional[str] = None,
    ) -> FocusCommandResult:
        """Schedule a delayed retest for a temporarily recovered KC."""
        from .repair_work_evaluator import RetestTaskGenerator

        current = self.persistence.load(episode_id)
        kc_state = current.learner.kc_states.get(target_kc)
        if kc_state != KCState.TEMPORARILY_RECOVERED:
            raise FocusApplicationError(
                f"Cannot schedule retest for {target_kc.value}: status is {kc_state}, requires TEMPORARILY_RECOVERED"
            )

        retest_task = RetestTaskGenerator.generate_retest_task(target_kc)

        state, event = self.persistence.record_retest_scheduled(
            episode_id=episode_id,
            target_kc=target_kc,
            barrier_id=barrier_id,
            retest_task_context=retest_task,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
        )

        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            repair_evaluation_feedback="Retest scheduled.",
        )

    def submit_delayed_retest_work(
        self,
        *,
        episode_id: str,
        target_kc: KCId,
        raw_work: Any,
        idempotency_key: str,
        expected_previous_sequence: int,
        barrier_id: Optional[str] = None,
    ) -> FocusCommandResult:
        """Evaluate learner work on a scheduled delayed retest task."""
        from .repair_work_evaluator import DelayedRetestEvaluator, RetestTaskGenerator

        current = self.persistence.load(episode_id)
        kc_state = current.learner.kc_states.get(target_kc)
        if kc_state not in {KCState.RETEST_DUE, KCState.TEMPORARILY_RECOVERED}:
            raise FocusApplicationError(
                f"Cannot evaluate delayed retest for {target_kc.value}: status is {kc_state}, requires RETEST_DUE or TEMPORARILY_RECOVERED"
            )

        retest_context = current.retest_task_context or RetestTaskGenerator.generate_retest_task(target_kc)
        evaluator = DelayedRetestEvaluator()
        result = evaluator.evaluate(
            retest_context=retest_context,
            raw_work=raw_work,
        )

        state, event = self.persistence.record_delayed_retest_result(
            episode_id=episode_id,
            target_kc=target_kc,
            success=result.is_success,
            barrier_id=barrier_id,
            idempotency_key=idempotency_key,
            expected_previous_sequence=expected_previous_sequence,
        )

        return self._command_result(
            episode_id=episode_id,
            state=state,
            event=event,
            repair_evaluation_success=result.is_success,
            repair_evaluation_feedback=result.feedback,
        )

    def get_multi_episode_learner_profile(
        self,
        episode_ids: Optional[List[str]] = None,
    ) -> MultiEpisodeLearnerProfile:
        """Aggregate cross-episode learner profiles from persistent history."""
        from .learner_profile import LearnerProfileAggregator

        target_ids = episode_ids if episode_ids is not None else self.persistence.list_episodes()
        snapshots = []
        for ep_id in target_ids:
            try:
                state = self.persistence.load(ep_id)
                snapshots.append(state.learner)
            except Exception:
                continue

        return LearnerProfileAggregator.aggregate(snapshots)

    def diagnose_session_re_entry(
        self,
        target_kc: KCId,
        episode_ids: Optional[List[str]] = None,
    ) -> ReEntryDiagnostic:
        """Diagnose prerequisite health and cold-start readiness for session re-entry."""
        from .learner_profile import LearnerProfileAggregator

        profile = self.get_multi_episode_learner_profile(episode_ids)
        return LearnerProfileAggregator.diagnose_re_entry(profile, target_kc)

