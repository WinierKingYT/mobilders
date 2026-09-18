from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple

from pydantic import BaseModel

from .models import AttemptJudgment, KCId
from .truth_adapter import AlphaTruthResult, TruthFactCode


class ErrorObservationCode(str, Enum):
    SIGN_WRONG = "EO-SIGN-WRONG"
    SIGNED_SUM_WRONG = "EO-SIGNED-SUM-WRONG"
    PARTIAL_DISTRIBUTION = "EO-PARTIAL-DISTRIBUTION"
    DISTRIBUTION_SIGN_COMPOSITION_WRONG = "EO-DISTRIBUTION-SIGN-COMPOSITION-WRONG"
    UNLIKE_TERMS_COMBINED = "EO-UNLIKE-TERMS-COMBINED"
    EQUALITY_ONE_SIDE_CHANGED = "EO-EQUALITY-ONE-SIDE-CHANGED"
    SIMPLE_ROOT_SIGN_WRONG = "EO-SIMPLE-ROOT-SIGN-WRONG"
    BINOMIAL_CROSS_TERM_OMITTED = "EO-BINOMIAL-CROSS-TERM-OMITTED"
    FACTOR_PAIR_PRODUCT_MISMATCH = "EO-FACTOR-PAIR-PRODUCT-MISMATCH"
    FACTOR_PAIR_SUM_MISMATCH = "EO-FACTOR-PAIR-SUM-MISMATCH"
    FACTOR_EXPANSION_MISMATCH = "EO-FACTOR-EXPANSION-MISMATCH"
    ZERO_PRODUCT_MISAPPLIED = "EO-ZERO-PRODUCT-MISAPPLIED"
    COEFFICIENT_SUBTRACTED = "EO-COEFFICIENT-SUBTRACTED"
    INEQUALITY_DIRECTION_NOT_REVERSED = "EO-INEQUALITY-DIRECTION-NOT-REVERSED"
    VERTEX_FORMULA_SIGN_INVERTED = "EO-VERTEX-FORMULA-SIGN-INVERTED"
    VERTEX_ORDINATE_CONFUSED_WITH_CONSTANT = "EO-VERTEX-ORDINATE-CONFUSED-WITH-CONSTANT"
    DIVISOR_ROOT_SIGN_INVERTED = "EO-DIVISOR-ROOT-SIGN-INVERTED"
    REMAINDER_CONFUSED_WITH_COEFF_SUM = "EO-REMAINDER-CONFUSED-WITH-COEFF-SUM"
    TRIG_SECONDARY_ROOT_OMITTED = "EO-TRIG-SECONDARY-ROOT-OMITTED"
    TRIG_AXIS_CONFUSED = "EO-TRIG-AXIS-CONFUSED"
    TRIG_COEFF_ABSORBED_INTO_ARG = "EO-TRIG-COEFF-ABSORBED-INTO-ARG"
    LOG_DOMAIN_CONSTRAINT_VIOLATED = "EO-LOG-DOMAIN-CONSTRAINT-VIOLATED"
    LOG_ADDITION_DISTRIBUTED = "EO-LOG-ADDITION-DISTRIBUTED"
    LOG_EXPONENT_CALCULATION_WRONG = "EO-LOG-EXPONENT-CALCULATION-WRONG"
    LIMIT_FORM_WRONG = "EO-CALC-LIMIT-FORM-WRONG"
    LIMIT_SIMPLIFICATION_WRONG = "EO-CALC-SIMPLIFICATION-WRONG"
    LIMIT_VALUE_WRONG = "EO-CALC-LIMIT-VALUE-WRONG"
    DERIVATIVE_POWER_RULE_WRONG = "EO-CALC-DERIVATIVE-POWER-WRONG"
    DERIVATIVE_SLOPE_WRONG = "EO-CALC-SLOPE-WRONG"
    TANGENT_LINE_WRONG = "EO-CALC-TANGENT-WRONG"
    INTEGRAL_ANTIDERIVATIVE_WRONG = "EO-CALC-INTEGRAL-ANTIDERIV-WRONG"
    INTEGRAL_LIMITS_EVALUATION_WRONG = "EO-CALC-INTEGRAL-LIMITS-WRONG"
    INTEGRAL_VALUE_WRONG = "EO-CALC-INTEGRAL-VALUE-WRONG"
    UNKNOWN_INVALID_STEP = "EO-UNKNOWN-INVALID-STEP"


_FACT_TO_OBSERVATION = {
    TruthFactCode.SIGN_WRONG: ErrorObservationCode.SIGN_WRONG,
    TruthFactCode.SIGNED_SUM_WRONG: ErrorObservationCode.SIGNED_SUM_WRONG,
    TruthFactCode.PARTIAL_DISTRIBUTION: ErrorObservationCode.PARTIAL_DISTRIBUTION,
    TruthFactCode.DISTRIBUTION_SIGN_COMPOSITION_WRONG: ErrorObservationCode.DISTRIBUTION_SIGN_COMPOSITION_WRONG,
    TruthFactCode.UNLIKE_TERMS_COMBINED: ErrorObservationCode.UNLIKE_TERMS_COMBINED,
    TruthFactCode.EQUALITY_ONE_SIDE_CHANGED: ErrorObservationCode.EQUALITY_ONE_SIDE_CHANGED,
    TruthFactCode.SIMPLE_ROOT_SIGN_WRONG: ErrorObservationCode.SIMPLE_ROOT_SIGN_WRONG,
    TruthFactCode.BINOMIAL_CROSS_TERM_OMITTED: ErrorObservationCode.BINOMIAL_CROSS_TERM_OMITTED,
    TruthFactCode.FACTOR_PAIR_PRODUCT_MISMATCH: ErrorObservationCode.FACTOR_PAIR_PRODUCT_MISMATCH,
    TruthFactCode.FACTOR_PAIR_SUM_MISMATCH: ErrorObservationCode.FACTOR_PAIR_SUM_MISMATCH,
    TruthFactCode.FACTOR_EXPANSION_MISMATCH: ErrorObservationCode.FACTOR_EXPANSION_MISMATCH,
    TruthFactCode.ZERO_PRODUCT_MISAPPLIED: ErrorObservationCode.ZERO_PRODUCT_MISAPPLIED,
    TruthFactCode.COEFFICIENT_SUBTRACTED_INSTEAD_OF_DIVIDED: ErrorObservationCode.COEFFICIENT_SUBTRACTED,
    TruthFactCode.INEQUALITY_DIRECTION_NOT_REVERSED: ErrorObservationCode.INEQUALITY_DIRECTION_NOT_REVERSED,
    TruthFactCode.VERTEX_ABS_SIGN_INVERTED: ErrorObservationCode.VERTEX_FORMULA_SIGN_INVERTED,
    TruthFactCode.VERTEX_ORDINATE_EQUALS_CONSTANT: ErrorObservationCode.VERTEX_ORDINATE_CONFUSED_WITH_CONSTANT,
    TruthFactCode.DIVISOR_ROOT_SIGN_INVERTED: ErrorObservationCode.DIVISOR_ROOT_SIGN_INVERTED,
    TruthFactCode.REMAINDER_CONFUSED_WITH_COEFF_SUM: ErrorObservationCode.REMAINDER_CONFUSED_WITH_COEFF_SUM,
    TruthFactCode.TRIG_SECONDARY_ROOT_OMITTED: ErrorObservationCode.TRIG_SECONDARY_ROOT_OMITTED,
    TruthFactCode.TRIG_AXIS_CONFUSED: ErrorObservationCode.TRIG_AXIS_CONFUSED,
    TruthFactCode.TRIG_COEFF_ABSORBED_INTO_ARG: ErrorObservationCode.TRIG_COEFF_ABSORBED_INTO_ARG,
    TruthFactCode.LOG_DOMAIN_CONSTRAINT_VIOLATED: ErrorObservationCode.LOG_DOMAIN_CONSTRAINT_VIOLATED,
    TruthFactCode.LOG_ADDITION_DISTRIBUTED: ErrorObservationCode.LOG_ADDITION_DISTRIBUTED,
    TruthFactCode.LOG_EXPONENT_CALCULATION_WRONG: ErrorObservationCode.LOG_EXPONENT_CALCULATION_WRONG,
    TruthFactCode.LIMIT_FORM_NOT_INDETERMINATE: ErrorObservationCode.LIMIT_FORM_WRONG,
    TruthFactCode.LIMIT_SIMPLIFICATION_WRONG: ErrorObservationCode.LIMIT_SIMPLIFICATION_WRONG,
    TruthFactCode.LIMIT_VALUE_WRONG: ErrorObservationCode.LIMIT_VALUE_WRONG,
    TruthFactCode.DERIVATIVE_POWER_RULE_WRONG: ErrorObservationCode.DERIVATIVE_POWER_RULE_WRONG,
    TruthFactCode.DERIVATIVE_SLOPE_WRONG: ErrorObservationCode.DERIVATIVE_SLOPE_WRONG,
    TruthFactCode.TANGENT_LINE_WRONG: ErrorObservationCode.TANGENT_LINE_WRONG,
    TruthFactCode.INTEGRAL_ANTIDERIVATIVE_WRONG: ErrorObservationCode.INTEGRAL_ANTIDERIVATIVE_WRONG,
    TruthFactCode.INTEGRAL_LIMITS_EVALUATION_WRONG: ErrorObservationCode.INTEGRAL_LIMITS_EVALUATION_WRONG,
    TruthFactCode.INTEGRAL_VALUE_WRONG: ErrorObservationCode.INTEGRAL_VALUE_WRONG,
}


class ErrorObservation(BaseModel):
    code: ErrorObservationCode
    target_kc: KCId
    source_attempt_id: Optional[str] = None
    source_fact: Optional[TruthFactCode] = None


class ErrorObservationProducer:
    """Creates mathematical evidence without inventing cognitive diagnosis."""

    def produce(
        self,
        *,
        attempt_judgment: AttemptJudgment,
        truth_result: AlphaTruthResult,
        attempt_id: Optional[str] = None,
    ) -> Tuple[ErrorObservation, ...]:
        # Frozen Domain invariant: only unambiguous supported mathematical
        # invalidity may produce ordinary ErrorObservation records.
        if attempt_judgment != AttemptJudgment.INVALID_MATHEMATICS:
            return ()
        if truth_result.is_valid:
            return ()

        result = []
        for fact in truth_result.facts:
            code = _FACT_TO_OBSERVATION.get(fact)
            if code is None:
                continue
            result.append(
                ErrorObservation(
                    code=code,
                    target_kc=truth_result.target_kc,
                    source_attempt_id=attempt_id,
                    source_fact=fact,
                )
            )
        if not result:
            # Deterministic invalidity may be real even when it does not match a
            # bounded Alpha error pattern. Preserve mathematical evidence without
            # inventing a specific cognitive explanation.
            result.append(
                ErrorObservation(
                    code=ErrorObservationCode.UNKNOWN_INVALID_STEP,
                    target_kc=truth_result.target_kc,
                    source_attempt_id=attempt_id,
                    source_fact=None,
                )
            )
        return tuple(result)
