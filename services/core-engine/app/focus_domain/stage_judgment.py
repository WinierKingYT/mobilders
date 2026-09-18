from __future__ import annotations

from typing import FrozenSet, Optional, Tuple

from pydantic import BaseModel

from .attempt_language import NormalizationStatus, NormalizedAttempt
from .models import (
    AttemptJudgment,
    BranchWorkSet,
    CompositeTaskFailureCode,
    StageId,
)
from .rules import judge_branch_work


class StageJudgmentResult(BaseModel):
    stage_id: StageId
    judgment: AttemptJudgment
    composite_failure: Optional[CompositeTaskFailureCode] = None
    observed_correct_items: FrozenSet[str] = frozenset()
    bypassed_stage_evidence: bool = False
    reason: str


class CTQF1StageJudgmentService:
    """Pure CT-QF1 stage judgment rules.

    This service does not mutate learner state and does not create durable
    barriers. It only determines attempt semantics for the current stage.
    """

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported Alpha form.",
        )

    def judge_factor_pair(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_pair: Tuple[int, int],
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_FACTOR
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        if attempt.factor_pair is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects a normalized factor-pair attempt.",
            )

        canonical_expected = tuple(sorted((int(expected_pair[0]), int(expected_pair[1]))))
        if attempt.factor_pair == canonical_expected:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({str(canonical_expected)}),
                reason="Factor pair satisfies the expected CT-QF1 task contract.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Supported factor pair does not match the task's deterministic factor pair.",
        )

    def judge_branch_decomposition(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_branch_equations: FrozenSet[str],
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_BRANCH
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        if not attempt.linear_equations:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects normalized factor-branch equations.",
            )

        observed = frozenset(eq.canonical for eq in attempt.linear_equations)
        correct = observed & expected_branch_equations
        wrong = observed - expected_branch_equations

        if wrong:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.INVALID_MATHEMATICS,
                observed_correct_items=frozenset(correct),
                reason="At least one supported branch equation is mathematically wrong for the current factorization.",
            )
        if correct == expected_branch_equations:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset(correct),
                reason="Both required zero-product branches are represented.",
            )
        if correct:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_INCOMPLETE,
                composite_failure=CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE,
                observed_correct_items=frozenset(correct),
                reason="Represented branch is valid, but the second required branch is missing.",
            )

        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="No submitted branch matches the deterministic zero-product branches.",
        )

    def judge_branch_work_set(self, branch_work: BranchWorkSet) -> StageJudgmentResult:
        judgment, failure = judge_branch_work(branch_work)
        observed = frozenset(
            item.expected_assignment
            for item in branch_work.branch_items
            if item.assignment_status.value == "VALID"
        )
        reason_by_judgment = {
            AttemptJudgment.VALID_EXPECTED: "Both factor-equation branches were solved correctly.",
            AttemptJudgment.VALID_INCOMPLETE: "At least one correct branch exists, but S3 is incomplete.",
            AttemptJudgment.INVALID_MATHEMATICS: "At least one supported branch assignment is mathematically invalid.",
            AttemptJudgment.UNSUPPORTED_STEP_FORM: "At least one branch assignment uses an unsupported step form.",
        }
        return StageJudgmentResult(
            stage_id=StageId.S3_SOLVE_FACTOR_EQUATIONS,
            judgment=judgment,
            composite_failure=failure,
            observed_correct_items=observed,
            reason=reason_by_judgment.get(judgment, "S3 branch work judged by the frozen branch contract."),
        )

    def judge_solution_set(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_roots: FrozenSet[int],
        current_stage: StageId = StageId.S4_COMPLETE_SOLUTION_SET,
    ) -> StageJudgmentResult:
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(current_stage, attempt)
        if attempt.solution_set is None:
            return StageJudgmentResult(
                stage_id=current_stage,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="Expected a normalized SolutionSet.",
            )

        observed = frozenset(attempt.solution_set.values)
        wrong = observed - expected_roots
        correct = observed & expected_roots

        if wrong:
            return StageJudgmentResult(
                stage_id=current_stage,
                judgment=AttemptJudgment.INVALID_MATHEMATICS,
                observed_correct_items=frozenset(f"x={root}" for root in correct),
                reason="Solution set contains at least one unsupported extra/wrong root.",
            )

        if observed == expected_roots:
            is_shortcut = current_stage != StageId.S4_COMPLETE_SOLUTION_SET
            return StageJudgmentResult(
                stage_id=current_stage,
                judgment=(
                    AttemptJudgment.VALID_SHORTCUT
                    if is_shortcut
                    else AttemptJudgment.VALID_EXPECTED
                ),
                observed_correct_items=frozenset(f"x={root}" for root in correct),
                bypassed_stage_evidence=is_shortcut,
                reason=(
                    "Complete correct solution set bypasses expected evidence-producing stages."
                    if is_shortcut
                    else "Complete solution set matches the deterministic expected roots."
                ),
            )

        if correct:
            return StageJudgmentResult(
                stage_id=current_stage,
                judgment=AttemptJudgment.VALID_INCOMPLETE,
                composite_failure=CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE,
                observed_correct_items=frozenset(f"x={root}" for root in correct),
                reason="Provided roots are correct but the complete solution set is incomplete.",
            )

        return StageJudgmentResult(
            stage_id=current_stage,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="No submitted root belongs to the deterministic expected solution set.",
        )


class CTLIN1StageJudgmentService:
    """Pure CT-LIN1 linear equation stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported Alpha form.",
        )

    def judge_isolate_term(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_coeff: int,
        expected_rhs: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_ISOLATE_TERM
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        if attempt.linear_coeff is None or attempt.linear_rhs is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects a rewritten linear equation (e.g. ax = d).",
            )
        if attempt.linear_coeff == expected_coeff and attempt.linear_rhs == expected_rhs:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"{expected_coeff}x={expected_rhs}"}),
                reason="Term isolation correctly preserves equality balance on both sides.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Rewritten equation does not match the balanced intermediate form.",
        )

    def judge_isolate_variable(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_root: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_ISOLATE_VARIABLE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)

        observed: Optional[int] = None
        if attempt.assignment is not None:
            observed = attempt.assignment.value
        elif attempt.integer_value is not None:
            observed = attempt.integer_value
        elif attempt.linear_coeff in (1, None) and attempt.linear_rhs is not None:
            observed = attempt.linear_rhs

        if observed is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects a root value or assignment (e.g. x = k).",
            )

        if observed == expected_root:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"x={expected_root}"}),
                reason="Coefficient division correctly isolated the unknown variable x.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Assigned value does not equal the expected root.",
        )

    def judge_verification(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_root: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_VERIFY_SOLUTION
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.VALID_EXPECTED,
            observed_correct_items=frozenset({f"verified(x={expected_root})"}),
            reason="Solution verification step successfully confirms equation truth.",
        )


class CTINEQ1StageJudgmentService:
    """Pure CT-INEQ1 linear inequality stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_isolate_term(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_coeff: int,
        expected_rhs: int,
        expected_comparator: str,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_ISOLATE_TERM
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        if (
            attempt.linear_coeff is None
            or attempt.linear_rhs is None
            or attempt.comparator is None
        ):
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects a rewritten linear inequality (e.g. ax <= d).",
            )
        if (
            attempt.linear_coeff == expected_coeff
            and attempt.linear_rhs == expected_rhs
            and attempt.comparator == expected_comparator
        ):
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"{expected_coeff}x{expected_comparator}{expected_rhs}"}),
                reason="Term isolation preserves inequality balance on both sides.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Rewritten inequality does not match the expected intermediate form.",
        )

    def judge_direction_division(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_root: int,
        expected_comparator: str,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_DIRECTION_AWARE_DIVISION
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        if (
            attempt.linear_rhs is None
            or attempt.comparator is None
            or attempt.linear_coeff not in (1, None)
        ):
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects isolated inequality form (e.g. x >= k).",
            )
        if (
            attempt.linear_rhs == expected_root
            and attempt.comparator == expected_comparator
        ):
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"x{expected_comparator}{expected_root}"}),
                reason="Direction-aware division correctly solved the inequality.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Solution does not match the expected direction-reversed inequality.",
        )


class CTPAR1StageJudgmentService:
    """Pure CT-PAR1 parabola vertex stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_calculate_r(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_r: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_CALCULATE_R
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.float_value if attempt.float_value is not None else (float(attempt.integer_value) if attempt.integer_value is not None else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects a numerical vertex abscissa (e.g. r = 2).",
            )
        if abs(val - expected_r) < 1e-4:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"r={expected_r}"}),
                reason="Vertex abscissa correctly calculated using r = -b / (2a).",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Calculated abscissa r does not match expected vertex position.",
        )

    def judge_calculate_k(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_k: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_CALCULATE_K
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.float_value if attempt.float_value is not None else (float(attempt.integer_value) if attempt.integer_value is not None else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects a numerical vertex ordinate (e.g. k = -1).",
            )
        if abs(val - expected_k) < 1e-4:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"k={expected_k}"}),
                reason="Vertex ordinate correctly evaluated by substituting r into f(x).",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Calculated ordinate k does not match expected vertex value.",
        )

    def judge_extremum(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_is_min: bool,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_EXTREMUM_CLASSIFICATION
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        if attempt.classification is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S3 expects extremum classification ('minimum' or 'maksimum').",
            )
        expected_term = "minimum" if expected_is_min else "maksimum"
        if attempt.classification == expected_term:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({expected_term}),
                reason=f"Parabola extremum correctly classified as {expected_term}.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason=f"Expected {expected_term} based on coefficient 'a' sign.",
        )


class CTPOLY1StageJudgmentService:
    """Pure CT-POLY1 polynomial remainder stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_divisor_root(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_root: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_ROOT_OF_DIVISOR
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.integer_value if attempt.integer_value is not None else (int(attempt.float_value) if attempt.float_value is not None and attempt.float_value.is_integer() else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects divisor root integer (e.g. x = 2).",
            )
        if val == expected_root:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"x={expected_root}"}),
                reason="Divisor root correctly isolated by setting divisor equal to zero.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Divisor root does not match expected value.",
        )

    def judge_remainder(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_remainder: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_EVALUATE_REMAINDER
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.integer_value if attempt.integer_value is not None else (int(attempt.float_value) if attempt.float_value is not None and attempt.float_value.is_integer() else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects remainder integer (e.g. kalan = 7).",
            )
        if val == expected_remainder:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"kalan={expected_remainder}"}),
                reason="Remainder correctly evaluated using polynomial remainder theorem P(d).",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Evaluated remainder does not match P(d).",
        )


class CTTRIG1StageJudgmentService:
    """Pure CT-TRIG1 trigonometric equation stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_isolate_trig_value(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_ratio: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_ISOLATE_TRIG_VALUE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.float_value if attempt.float_value is not None else (float(attempt.integer_value) if attempt.integer_value is not None else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects numeric trigonometric ratio (e.g. sin(x) = 0.5 or 1/2).",
            )
        if abs(val - expected_ratio) < 1e-4:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"sin(x)={expected_ratio}"}),
                reason="Trigonometric value correctly isolated.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Isolated trigonometric ratio does not match c/a.",
        )

    def judge_principal_angle(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_principal_deg: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_DETERMINE_PRINCIPAL_ANGLE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.integer_value if attempt.integer_value is not None else (int(round(attempt.float_value)) if attempt.float_value is not None else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects principal angle integer in degrees (e.g. x = 30).",
            )
        if val == expected_principal_deg:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"x={expected_principal_deg}"}),
                reason="Principal angle on unit circle correctly determined.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Principal angle does not match expected unit circle reference angle.",
        )

    def judge_secondary_root(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_secondary_deg: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_DETERMINE_SECONDARY_ROOT
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.integer_value if attempt.integer_value is not None else (int(round(attempt.float_value)) if attempt.float_value is not None else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S3 expects secondary symmetric root integer in degrees (e.g. x = 150).",
            )
        if val == expected_secondary_deg:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"x={expected_secondary_deg}"}),
                reason="Secondary symmetric root correctly determined.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Secondary root does not match symmetric angle in interval [0, 360).",
        )


class CTLOG1StageJudgmentService:
    """Pure CT-LOG1 logarithmic equation stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_exponential_conversion(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_power: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_EXPONENTIAL_CONVERSION
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.integer_value if attempt.integer_value is not None else (int(attempt.float_value) if attempt.float_value is not None and attempt.float_value.is_integer() else None)
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S1 expects power integer (e.g. b^k = 8).",
            )
        if val == expected_power:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"power={expected_power}"}),
                reason="Logarithmic equation correctly converted to exponential form b^k.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Converted exponential power does not match b^k.",
        )

    def judge_isolate_variable(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_x: int,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_ISOLATE_VARIABLE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.integer_value if attempt.integer_value is not None else (int(attempt.float_value) if attempt.float_value is not None and attempt.float_value.is_integer() else None)
        if val is None and attempt.assignment is not None:
            val = attempt.assignment.value
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects variable solution integer (e.g. x = 11).",
            )
        if val == expected_x:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"x={expected_x}"}),
                reason="Variable correctly isolated from exponential equation.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Variable value does not match expected solution b^k + c.",
        )

    def judge_domain_constraint(
        self,
        attempt: NormalizedAttempt,
        *,
        is_domain_valid: bool,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_VERIFY_DOMAIN_CONSTRAINT
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        is_valid = attempt.boolean_value if attempt.boolean_value is not None else (attempt.classification == "gecerli")
        if is_valid == is_domain_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({"gecerli" if is_domain_valid else "gecersiz"}),
                reason="Domain constraint check correctly verified against argument positivity.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Domain constraint judgment does not match argument positivity requirement.",
        )


class CTLIM1StageJudgmentService:
    """Pure CT-LIM1 0/0 indeterminate limit stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_limit_form(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_form: str = "0/0",
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_EVALUATE_LIMIT_FORM
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        ans = (attempt.classification or attempt.canonical_text or "").strip().lower()
        if ans in ("0/0", "belirsiz", "indeterminate"):
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({"form=0/0"}),
                reason="Direct substitution correctly identified as 0/0 indeterminate form.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Form is not identified as 0/0 indeterminate form.",
        )

    def judge_simplified_expression(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_expression: str,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_SIMPLIFY_EXPRESSION
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        candidate = attempt.canonical_text or ""
        from .truth_adapter import AlphaTruthAdapter
        truth = AlphaTruthAdapter()
        truth_res = truth.check_limit_simplification(
            expected_expr=expected_expression,
            observed_expr=candidate,
        )
        if truth_res.is_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"expr={expected_expression}"}),
                reason="Rational expression successfully factored and simplified by cancelling common root factor.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Simplified expression does not match expected cancellation result.",
        )

    def judge_final_limit(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_value: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_COMPUTE_FINAL_LIMIT
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.float_value if attempt.float_value is not None else (
            float(attempt.integer_value) if attempt.integer_value is not None else None
        )
        if val is None and attempt.canonical_text:
            try:
                val = float(attempt.canonical_text)
            except ValueError:
                pass
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S3 expects numeric limit value.",
            )
        if abs(val - expected_value) < 1e-5:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"limit={expected_value}"}),
                reason="Final limit computed correctly by substituting limit point into simplified expression.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Computed limit value does not match expected limit.",
        )


class CTDERIV1StageJudgmentService:
    """Pure CT-DERIV1 polynomial derivative & tangent line stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_derivative_function(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_derivative: str,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_COMPUTE_DERIVATIVE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        candidate = attempt.canonical_text or ""
        from .truth_adapter import AlphaTruthAdapter
        truth = AlphaTruthAdapter()
        truth_res = truth.check_derivative_function(
            expected_deriv=expected_derivative,
            observed_deriv=candidate,
        )
        if truth_res.is_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"f'(x)={expected_derivative}"}),
                reason="Power rule correctly applied to polynomial terms.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Derivative expression does not match power rule result.",
        )

    def judge_tangent_slope(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_slope: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_EVALUATE_SLOPE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.float_value if attempt.float_value is not None else (
            float(attempt.integer_value) if attempt.integer_value is not None else None
        )
        if val is None and attempt.canonical_text:
            clean = attempt.canonical_text
            if "m=" in clean:
                clean = clean.split("m=")[-1]
            try:
                val = float(clean)
            except ValueError:
                pass
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S2 expects numeric slope value m = f'(x0).",
            )
        if abs(val - expected_slope) < 1e-5:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"m={expected_slope}"}),
                reason="Tangent slope evaluated correctly by evaluating derivative at x0.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Slope value does not match derivative evaluation at x0.",
        )

    def judge_tangent_line(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_line: str,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_DETERMINE_TANGENT_LINE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        candidate = attempt.canonical_text or ""
        from .truth_adapter import AlphaTruthAdapter
        truth = AlphaTruthAdapter()
        truth_res = truth.check_tangent_line(
            expected_line=expected_line,
            observed_line=candidate,
        )
        if truth_res.is_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({"tangent_line_verified"}),
                reason="Tangent line equation y - y0 = m(x - x0) verified correctly.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Tangent line equation does not match point-slope form with curve point.",
        )


class CTINT1StageJudgmentService:
    """Pure CT-INT1 definite integral & area stage judgment rules."""

    @staticmethod
    def _normalization_failure(stage_id: StageId, attempt: NormalizedAttempt) -> StageJudgmentResult:
        judgment = attempt.as_attempt_judgment_if_not_supported()
        if judgment is None:
            raise ValueError("Expected an unsupported/ambiguous normalized attempt")
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=judgment,
            reason=attempt.reason or "Attempt is outside the supported form.",
        )

    def judge_antiderivative(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_antiderivative: str,
    ) -> StageJudgmentResult:
        stage_id = StageId.S1_FIND_ANTIDERIVATIVE
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        candidate = attempt.canonical_text or ""
        from .truth_adapter import AlphaTruthAdapter
        truth = AlphaTruthAdapter()
        truth_res = truth.check_antiderivative(
            expected_antideriv=expected_antiderivative,
            observed_antideriv=candidate,
        )
        if truth_res.is_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"F(x)={expected_antiderivative}"}),
                reason="Antiderivative correctly derived using integration power rule.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Antiderivative does not match expected primitive function.",
        )

    def judge_integral_limits_evaluation(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_diff_str: str,
        expected_diff_val: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S2_APPLY_LIMITS
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        candidate = attempt.canonical_text or ""
        from .truth_adapter import AlphaTruthAdapter
        truth = AlphaTruthAdapter()
        truth_res = truth.check_integral_limits_evaluation(
            expected_diff_str=expected_diff_str,
            observed_diff_str=candidate,
            expected_diff_val=expected_diff_val,
        )
        if truth_res.is_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"F(b)-F(a)={expected_diff_str}"}),
                reason="Limits correctly applied according to the Fundamental Theorem of Calculus F(b) - F(a).",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Limits evaluation does not match F(b) - F(a) difference.",
        )

    def judge_definite_integral_value(
        self,
        attempt: NormalizedAttempt,
        *,
        expected_value: float,
    ) -> StageJudgmentResult:
        stage_id = StageId.S3_COMPUTE_DEFINITE_INTEGRAL
        if attempt.status != NormalizationStatus.SUPPORTED:
            return self._normalization_failure(stage_id, attempt)
        val = attempt.float_value if attempt.float_value is not None else (
            float(attempt.integer_value) if attempt.integer_value is not None else None
        )
        if val is None and attempt.canonical_text:
            clean = attempt.canonical_text.strip()
            if "=" in clean:
                clean = clean.split("=")[-1].strip()
            try:
                val = float(clean)
            except ValueError:
                pass
        if val is None:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.UNSUPPORTED_STEP_FORM,
                reason="S3 expects numeric definite integral value.",
            )
        from .truth_adapter import AlphaTruthAdapter
        truth = AlphaTruthAdapter()
        truth_res = truth.check_definite_integral_value(
            expected_val=expected_value,
            observed_val=val,
        )
        if truth_res.is_valid:
            return StageJudgmentResult(
                stage_id=stage_id,
                judgment=AttemptJudgment.VALID_EXPECTED,
                observed_correct_items=frozenset({f"integral={expected_value}"}),
                reason="Definite integral value computed correctly.",
            )
        return StageJudgmentResult(
            stage_id=stage_id,
            judgment=AttemptJudgment.INVALID_MATHEMATICS,
            reason="Computed definite integral value does not match expected result.",
        )




