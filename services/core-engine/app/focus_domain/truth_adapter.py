from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet, Literal, Tuple

from pydantic import BaseModel, Field, model_validator

from .models import KCId


class TruthFactCode(str, Enum):
    SIGN_WRONG = "TF-SIGN-WRONG"
    SIGNED_SUM_WRONG = "TF-SIGNED-SUM-WRONG"
    PARTIAL_DISTRIBUTION = "TF-PARTIAL-DISTRIBUTION"
    DISTRIBUTION_SIGN_COMPOSITION_WRONG = "TF-DISTRIBUTION-SIGN-COMPOSITION-WRONG"
    UNLIKE_TERMS_COMBINED = "TF-UNLIKE-TERMS-COMBINED"
    EQUALITY_ONE_SIDE_CHANGED = "TF-EQUALITY-ONE-SIDE-CHANGED"
    SIMPLE_ROOT_SIGN_WRONG = "TF-SIMPLE-ROOT-SIGN-WRONG"
    BINOMIAL_CROSS_TERM_OMITTED = "TF-BINOMIAL-CROSS-TERM-OMITTED"
    FACTOR_PAIR_PRODUCT_MISMATCH = "TF-FACTOR-PAIR-PRODUCT-MISMATCH"
    FACTOR_PAIR_SUM_MISMATCH = "TF-FACTOR-PAIR-SUM-MISMATCH"
    FACTOR_EXPANSION_MISMATCH = "TF-FACTOR-EXPANSION-MISMATCH"
    ZERO_PRODUCT_MISAPPLIED = "TF-ZERO-PRODUCT-MISAPPLIED"
    COEFFICIENT_SUBTRACTED_INSTEAD_OF_DIVIDED = "TF-COEFFICIENT-SUBTRACTED-INSTEAD-OF-DIVIDED"
    INEQUALITY_DIRECTION_NOT_REVERSED = "TF-INEQUALITY-DIRECTION-NOT-REVERSED"
    VERTEX_ABS_SIGN_INVERTED = "TF-VERTEX-ABS-SIGN-INVERTED"
    VERTEX_ORDINATE_EQUALS_CONSTANT = "TF-VERTEX-ORDINATE-EQUALS-CONSTANT"
    DIVISOR_ROOT_SIGN_INVERTED = "TF-DIVISOR-ROOT-SIGN-INVERTED"
    REMAINDER_CONFUSED_WITH_COEFF_SUM = "TF-REMAINDER-CONFUSED-WITH-COEFF-SUM"
    TRIG_RATIO_WRONG = "TF-TRIG-RATIO-WRONG"
    TRIG_AXIS_CONFUSED = "TF-TRIG-AXIS-CONFUSED"
    TRIG_SECONDARY_ROOT_OMITTED = "TF-TRIG-SECONDARY-ROOT-OMITTED"
    TRIG_COEFF_ABSORBED_INTO_ARG = "TF-TRIG-COEFF-ABSORBED-INTO-ARG"
    LOG_POWER_WRONG = "TF-LOG-POWER-WRONG"
    LOG_EXPONENT_CALCULATION_WRONG = "TF-LOG-EXPONENT-CALCULATION-WRONG"
    LOG_ADDITION_DISTRIBUTED = "TF-LOG-ADDITION-DISTRIBUTED"
    LOG_DOMAIN_CONSTRAINT_VIOLATED = "TF-LOG-DOMAIN-CONSTRAINT-VIOLATED"
    LIMIT_FORM_NOT_INDETERMINATE = "TF-LIMIT-FORM-NOT-INDETERMINATE"
    LIMIT_SIMPLIFICATION_WRONG = "TF-LIMIT-SIMPLIFICATION-WRONG"
    LIMIT_VALUE_WRONG = "TF-LIMIT-VALUE-WRONG"
    DERIVATIVE_POWER_RULE_WRONG = "TF-DERIVATIVE-POWER-RULE-WRONG"
    DERIVATIVE_SLOPE_WRONG = "TF-DERIVATIVE-SLOPE-WRONG"
    TANGENT_LINE_WRONG = "TF-TANGENT-LINE-WRONG"
    INTEGRAL_ANTIDERIVATIVE_WRONG = "TF-INTEGRAL-ANTIDERIVATIVE-WRONG"
    INTEGRAL_LIMITS_EVALUATION_WRONG = "TF-INTEGRAL-LIMITS-EVALUATION-WRONG"
    INTEGRAL_VALUE_WRONG = "TF-INTEGRAL-VALUE-WRONG"


class AlphaTruthResult(BaseModel):
    target_kc: KCId
    is_valid: bool
    facts: FrozenSet[TruthFactCode] = frozenset()
    expected: Dict[str, int | str | bool] = Field(default_factory=dict)
    observed: Dict[str, int | str | bool] = Field(default_factory=dict)
    reason: str

    @model_validator(mode="after")
    def valid_results_do_not_carry_error_facts(self) -> "AlphaTruthResult":
        if self.is_valid and self.facts:
            raise ValueError("Valid truth results cannot carry error facts")
        return self


class AlphaQuadraticTaskSpec(BaseModel):
    """Deterministic CT-QF1 generated-task truth specification.

    ``factor_abs_max`` is a generation bound, not a cognitive definition.
    """

    m: int
    n: int
    factor_abs_max: int = 6

    @model_validator(mode="after")
    def validate_generation_profile(self) -> "AlphaQuadraticTaskSpec":
        if self.m == 0 or self.n == 0:
            raise ValueError("Alpha CT-QF1 excludes zero-root generation")
        if self.m == self.n:
            raise ValueError("Alpha CT-QF1 excludes repeated-root generation")
        if abs(self.m) > self.factor_abs_max or abs(self.n) > self.factor_abs_max:
            raise ValueError("Factors exceed GenerationProfile.alpha.factor_abs_max")
        return self

    @property
    def b(self) -> int:
        return self.m + self.n

    @property
    def c(self) -> int:
        return self.m * self.n

    @property
    def factor_pair(self) -> Tuple[int, int]:
        return tuple(sorted((self.m, self.n)))

    @property
    def branch_equations(self) -> FrozenSet[str]:
        def eq(k: int) -> str:
            sign = "+" if k > 0 else "-"
            return f"x{sign}{abs(k)}=0"

        return frozenset({eq(self.m), eq(self.n)})

    @property
    def roots(self) -> FrozenSet[int]:
        return frozenset({-self.m, -self.n})

    @property
    def polynomial(self) -> str:
        b_part = f"+{self.b}x" if self.b > 0 else (f"{self.b}x" if self.b < 0 else "")
        c_part = f"+{self.c}" if self.c > 0 else str(self.c)
        return f"x^2{b_part}{c_part}=0"


class AlphaTruthAdapter:
    """Narrow deterministic truth authority for frozen Focus Alpha.

    It intentionally exposes only the operations needed by the 10 frozen
    Repairable KCs and CT-QF1. It does not accept arbitrary symbolic programs.
    """

    def check_signed_sum(self, a: int, b: int, observed: int) -> AlphaTruthResult:
        expected = a + b
        valid = observed == expected
        return AlphaTruthResult(
            target_kc=KCId.N1,
            is_valid=valid,
            facts=frozenset() if valid else frozenset({TruthFactCode.SIGNED_SUM_WRONG}),
            expected={"result": expected},
            observed={"result": observed},
            reason="Signed addition/subtraction is deterministic over Alpha integers.",
        )

    def check_signed_multiplication(self, a: int, b: int, observed: int) -> AlphaTruthResult:
        expected = a * b
        if observed == expected:
            facts: FrozenSet[TruthFactCode] = frozenset()
            valid = True
        else:
            valid = False
            facts = (
                frozenset({TruthFactCode.SIGN_WRONG})
                if abs(observed) == abs(expected) and observed == -expected
                else frozenset()
            )
        return AlphaTruthResult(
            target_kc=KCId.N2,
            is_valid=valid,
            facts=facts,
            expected={"result": expected},
            observed={"result": observed},
            reason="Signed multiplication is deterministic over Alpha integers.",
        )

    def check_unary_negation(self, inner: int, observed: int) -> AlphaTruthResult:
        expected = -inner
        facts = frozenset()
        if observed != expected and observed == inner:
            facts = frozenset({TruthFactCode.SIGN_WRONG})
        return AlphaTruthResult(
            target_kc=KCId.N3,
            is_valid=observed == expected,
            facts=facts,
            expected={"result": expected},
            observed={"result": observed},
            reason="Unary negation changes the sign of the represented integer.",
        )

    def check_distribution(
        self,
        *,
        outside: int,
        inner_constant: int,
        observed_x_coefficient: int,
        observed_constant: int,
    ) -> AlphaTruthResult:
        expected_x = outside
        expected_constant = outside * inner_constant
        valid = observed_x_coefficient == expected_x and observed_constant == expected_constant
        facts: set[TruthFactCode] = set()

        if not valid:
            # Canonical partial distribution: a(x+b) -> ax+b.
            if observed_x_coefficient == expected_x and observed_constant == inner_constant and outside != 1:
                facts.add(TruthFactCode.PARTIAL_DISTRIBUTION)

            if (
                observed_x_coefficient == expected_x
                and abs(observed_constant) == abs(expected_constant)
                and observed_constant == -expected_constant
            ):
                facts.add(TruthFactCode.DISTRIBUTION_SIGN_COMPOSITION_WRONG)
                facts.add(TruthFactCode.SIGN_WRONG)

        return AlphaTruthResult(
            target_kc=KCId.E1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"x_coefficient": expected_x, "constant": expected_constant},
            observed={"x_coefficient": observed_x_coefficient, "constant": observed_constant},
            reason="Distribution must preserve both term coverage and signed multiplication.",
        )

    def check_like_term_action(
        self,
        *,
        same_variable_structure: bool,
        learner_combined: bool,
    ) -> AlphaTruthResult:
        valid = same_variable_structure or not learner_combined
        facts = (
            frozenset()
            if valid
            else frozenset({TruthFactCode.UNLIKE_TERMS_COMBINED})
        )
        return AlphaTruthResult(
            target_kc=KCId.E2,
            is_valid=valid,
            facts=facts,
            expected={"may_combine": same_variable_structure},
            observed={"learner_combined": learner_combined},
            reason="Only terms with the same variable/power structure may be combined.",
        )

    def check_equality_additive_transform(
        self,
        *,
        left_delta: int,
        right_delta: int,
    ) -> AlphaTruthResult:
        valid = left_delta == right_delta
        facts = (
            frozenset()
            if valid
            else frozenset({TruthFactCode.EQUALITY_ONE_SIDE_CHANGED})
        )
        return AlphaTruthResult(
            target_kc=KCId.Q0,
            is_valid=valid,
            facts=facts,
            expected={"same_additive_delta": True},
            observed={"left_delta": left_delta, "right_delta": right_delta},
            reason="Alpha KC-Q0 preserves equality by the same additive change on both sides.",
        )

    def check_simple_factor_root(self, *, constant: int, observed_root: int) -> AlphaTruthResult:
        expected = -constant
        facts: set[TruthFactCode] = set()
        if observed_root != expected:
            if observed_root == constant and constant != 0:
                facts.add(TruthFactCode.SIMPLE_ROOT_SIGN_WRONG)
            else:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.Q1,
            is_valid=observed_root == expected,
            facts=frozenset(facts),
            expected={"root": expected},
            observed={"root": observed_root},
            reason="For x+c=0, the Alpha root is x=-c.",
        )

    def check_binomial_expansion(
        self,
        *,
        m: int,
        n: int,
        observed_middle_coefficient: int,
        observed_constant: int,
        cross_term_present: bool = True,
    ) -> AlphaTruthResult:
        expected_middle = m + n
        expected_constant = m * n
        valid = (
            cross_term_present
            and observed_middle_coefficient == expected_middle
            and observed_constant == expected_constant
        )
        facts: set[TruthFactCode] = set()
        if not valid:
            if not cross_term_present:
                facts.add(TruthFactCode.BINOMIAL_CROSS_TERM_OMITTED)
            if observed_middle_coefficient != expected_middle:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
            if observed_constant != expected_constant:
                facts.add(TruthFactCode.FACTOR_PAIR_PRODUCT_MISMATCH)
            facts.add(TruthFactCode.FACTOR_EXPANSION_MISMATCH)
        return AlphaTruthResult(
            target_kc=KCId.F1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"middle_coefficient": expected_middle, "constant": expected_constant},
            observed={
                "middle_coefficient": observed_middle_coefficient,
                "constant": observed_constant,
                "cross_term_present": cross_term_present,
            },
            reason="Monic binomial expansion must preserve cross-term sum and constant product.",
        )

    def check_factor_pair(
        self,
        *,
        b: int,
        c: int,
        pair: Tuple[int, int],
    ) -> AlphaTruthResult:
        m, n = int(pair[0]), int(pair[1])
        observed_sum = m + n
        observed_product = m * n
        facts: set[TruthFactCode] = set()
        if observed_sum != b:
            facts.add(TruthFactCode.FACTOR_PAIR_SUM_MISMATCH)
        if observed_product != c:
            facts.add(TruthFactCode.FACTOR_PAIR_PRODUCT_MISMATCH)
        valid = not facts
        return AlphaTruthResult(
            target_kc=KCId.F2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"sum": b, "product": c},
            observed={"sum": observed_sum, "product": observed_product},
            reason="A monic factor pair must satisfy both sum and product constraints.",
        )

    def check_zero_product_application(
        self,
        *,
        source_operator: Literal["MULTIPLY", "ADD"],
        learner_split_into_zero_branches: bool,
    ) -> AlphaTruthResult:
        valid = source_operator == "MULTIPLY" or not learner_split_into_zero_branches
        facts = (
            frozenset()
            if valid
            else frozenset({TruthFactCode.ZERO_PRODUCT_MISAPPLIED})
        )
        return AlphaTruthResult(
            target_kc=KCId.Z1,
            is_valid=valid,
            facts=facts,
            expected={"zero_branching_allowed": source_operator == "MULTIPLY"},
            observed={"learner_split": learner_split_into_zero_branches},
            reason="Zero-product branching applies to a product equal to zero, not a sum.",
        )

    def check_linear_term_isolation(
        self,
        *,
        a: int,
        b: int,
        c: int,
        observed_rhs: int,
    ) -> AlphaTruthResult:
        expected = c - b
        valid = observed_rhs == expected
        facts: set[TruthFactCode] = set()
        if not valid:
            if observed_rhs in (c + b, c):
                facts.add(TruthFactCode.EQUALITY_ONE_SIDE_CHANGED)
            else:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.Q0,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"rhs": expected},
            observed={"rhs": observed_rhs},
            reason="Isolating the linear term requires applying the opposite additive delta to both sides.",
        )

    def check_linear_coefficient_division(
        self,
        *,
        a: int,
        d: int,
        observed_x: int,
    ) -> AlphaTruthResult:
        expected = d // a
        valid = observed_x == expected
        facts: set[TruthFactCode] = set()
        if not valid:
            if observed_x == d - a:
                facts.add(TruthFactCode.COEFFICIENT_SUBTRACTED_INSTEAD_OF_DIVIDED)
            elif abs(observed_x) == abs(expected) and observed_x == -expected:
                facts.add(TruthFactCode.SIGN_WRONG)
            else:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.L1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"x": expected},
            observed={"x": observed_x},
            reason="Isolating x from ax = d requires dividing both sides by the coefficient a.",
        )

    def check_inequality_division(
        self,
        *,
        a: int,
        d: int,
        original_comparator: str,
        observed_comparator: str,
        observed_x: int,
    ) -> AlphaTruthResult:
        flip_map = {"<=": ">=", "<": ">", ">=": "<=", ">": "<"}
        expected_op = flip_map[original_comparator] if a < 0 else original_comparator
        expected_x = d // a
        valid_op = observed_comparator == expected_op
        valid_x = observed_x == expected_x
        valid = valid_op and valid_x
        facts: set[TruthFactCode] = set()
        if not valid:
            if a < 0 and observed_comparator == original_comparator:
                facts.add(TruthFactCode.INEQUALITY_DIRECTION_NOT_REVERSED)
            if not valid_x:
                if abs(observed_x) == abs(expected_x) and observed_x == -expected_x:
                    facts.add(TruthFactCode.SIGN_WRONG)
                else:
                    facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.I1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"comparator": expected_op, "x": expected_x},
            observed={"comparator": observed_comparator, "x": observed_x},
            reason="Dividing an inequality by a negative number reverses the inequality direction.",
        )

    def check_parabola_vertex_r(
        self,
        *,
        a: int,
        b: int,
        observed_r: float,
    ) -> AlphaTruthResult:
        expected = -b / (2.0 * a)
        valid = abs(observed_r - expected) < 1e-4
        facts: set[TruthFactCode] = set()
        if not valid:
            buggy_r_no_minus = b / (2.0 * a)
            if abs(observed_r - buggy_r_no_minus) < 1e-4:
                facts.add(TruthFactCode.VERTEX_ABS_SIGN_INVERTED)
            else:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.P1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"r": expected},
            observed={"r": observed_r},
            reason="Parabola vertex abscissa is calculated using r = -b / (2a).",
        )

    def check_parabola_vertex_k(
        self,
        *,
        a: int,
        b: int,
        c: int,
        r: float,
        observed_k: float,
    ) -> AlphaTruthResult:
        expected = a * (r ** 2) + b * r + c
        valid = abs(observed_k - expected) < 1e-4
        facts: set[TruthFactCode] = set()
        if not valid:
            if abs(observed_k - float(c)) < 1e-4 and abs(float(c) - expected) > 1e-4:
                facts.add(TruthFactCode.VERTEX_ORDINATE_EQUALS_CONSTANT)
            else:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.P1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"k": expected},
            observed={"k": observed_k},
            reason="Parabola vertex ordinate is calculated by evaluating k = f(r).",
        )

    def check_parabola_extremum(
        self,
        *,
        a: int,
        observed_is_min: bool,
    ) -> AlphaTruthResult:
        expected_is_min = (a > 0)
        valid = (observed_is_min == expected_is_min)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.SIGN_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.P2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"is_minimum": expected_is_min},
            observed={"is_minimum": observed_is_min},
            reason="If a > 0 the parabola opens upwards (minimum); if a < 0 it opens downwards (maximum).",
        )

    def check_polynomial_divisor_root(
        self,
        *,
        divisor_root: int,
        observed_root: int,
    ) -> AlphaTruthResult:
        expected = divisor_root
        valid = (observed_root == expected)
        facts: set[TruthFactCode] = set()
        if not valid:
            if observed_root == -expected:
                facts.add(TruthFactCode.DIVISOR_ROOT_SIGN_INVERTED)
            else:
                facts.add(TruthFactCode.SIGN_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.PL2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"root": expected},
            observed={"root": observed_root},
            reason="The root of divisor (x - d) is found by setting x - d = 0, which gives x = d.",
        )

    def check_polynomial_remainder(
        self,
        *,
        a: int,
        b: int,
        c: int,
        divisor_root: int,
        observed_rem: int,
    ) -> AlphaTruthResult:
        d = divisor_root
        expected = a * (d ** 2) + b * d + c
        valid = (observed_rem == expected)
        facts: set[TruthFactCode] = set()
        if not valid:
            coeff_sum = a + b + c
            const_term = c
            if (observed_rem == coeff_sum or observed_rem == const_term) and observed_rem != expected:
                facts.add(TruthFactCode.REMAINDER_CONFUSED_WITH_COEFF_SUM)
            else:
                facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.PL1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"remainder": expected},
            observed={"remainder": observed_rem},
            reason="By the Remainder Theorem, the remainder of P(x) divided by (x - d) is P(d).",
        )

    def check_trig_ratio(
        self,
        *,
        expected_ratio: float,
        observed_ratio: float,
    ) -> AlphaTruthResult:
        valid = abs(observed_ratio - expected_ratio) < 1e-4
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.TRIG_RATIO_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.TR1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"ratio": str(expected_ratio)},
            observed={"ratio": str(observed_ratio)},
            reason="Trigonometric ratio must be isolated correctly (sin(x) = c/a).",
        )

    def check_trig_principal_angle(
        self,
        *,
        expected_principal_deg: int,
        observed_deg: int,
    ) -> AlphaTruthResult:
        valid = (observed_deg == expected_principal_deg)
        facts: set[TruthFactCode] = set()
        if not valid:
            if observed_deg in (90 - expected_principal_deg, 60 if expected_principal_deg == 30 else 30):
                facts.add(TruthFactCode.TRIG_AXIS_CONFUSED)
            else:
                facts.add(TruthFactCode.SIGN_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.TR1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"principal_deg": expected_principal_deg},
            observed={"principal_deg": observed_deg},
            reason="Principal angle must match the reference angle on the unit circle in [0, 90].",
        )

    def check_trig_secondary_root(
        self,
        *,
        expected_secondary_deg: int,
        observed_deg: int,
        principal_deg: int = 30,
    ) -> AlphaTruthResult:
        valid = (observed_deg == expected_secondary_deg)
        facts: set[TruthFactCode] = set()
        if not valid:
            if observed_deg == principal_deg:
                facts.add(TruthFactCode.TRIG_SECONDARY_ROOT_OMITTED)
            else:
                facts.add(TruthFactCode.SIGN_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.TR2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"secondary_deg": expected_secondary_deg},
            observed={"secondary_deg": observed_deg},
            reason="Secondary root in [0, 360) satisfies sin(180 - x) = sin(x).",
        )

    def check_log_power(
        self,
        *,
        base: int,
        k: int,
        expected_power: int,
        observed_power: int,
    ) -> AlphaTruthResult:
        valid = (observed_power == expected_power)
        facts: set[TruthFactCode] = set()
        if not valid:
            if observed_power == base * k:
                facts.add(TruthFactCode.LOG_EXPONENT_CALCULATION_WRONG)
            else:
                facts.add(TruthFactCode.LOG_POWER_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.LG1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"power": expected_power},
            observed={"power": observed_power},
            reason="log_b(y) = k converts to exponential form y = b^k.",
        )

    def check_log_solution(
        self,
        *,
        expected_x: int,
        observed_x: int,
    ) -> AlphaTruthResult:
        valid = (observed_x == expected_x)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.SIGNED_SUM_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.LG1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"x": expected_x},
            observed={"x": observed_x},
            reason="Variable x is isolated from x - c = b^k as x = b^k + c.",
        )

    def check_log_domain_constraint(
        self,
        *,
        is_domain_valid: bool,
        observed_valid: bool,
    ) -> AlphaTruthResult:
        valid = (observed_valid == is_domain_valid)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.LOG_DOMAIN_CONSTRAINT_VIOLATED)
        return AlphaTruthResult(
            target_kc=KCId.LG2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"domain_valid": is_domain_valid},
            observed={"domain_valid": observed_valid},
            reason="Logarithmic arguments must strictly satisfy the positivity condition (argument > 0).",
        )

    def check_limit_form(
        self,
        *,
        expected_form: str = "0/0",
        observed_form: str,
    ) -> AlphaTruthResult:
        norm_exp = expected_form.strip().lower()
        norm_obs = observed_form.strip().lower()
        valid = (norm_obs == norm_exp)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.LIMIT_FORM_NOT_INDETERMINATE)
        return AlphaTruthResult(
            target_kc=KCId.LM1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"form": expected_form},
            observed={"form": observed_form},
            reason="Direct evaluation of the quotient at x = a yields 0/0 indeterminate form.",
        )

    def check_limit_simplification(
        self,
        *,
        expected_expr: str,
        observed_expr: str,
    ) -> AlphaTruthResult:
        def _clean(s: str) -> str:
            return s.replace(" ", "").replace("*", "").lower()
        norm_exp = _clean(expected_expr)
        norm_obs = _clean(observed_expr)
        valid = (norm_obs == norm_exp)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.LIMIT_SIMPLIFICATION_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.LM1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"simplified_expr": expected_expr},
            observed={"simplified_expr": observed_expr},
            reason="Factoring the numerator (x - a)(x + a) and cancelling (x - a) leaves (x + a).",
        )

    def check_limit_value(
        self,
        *,
        expected_limit: float,
        observed_limit: float,
    ) -> AlphaTruthResult:
        valid = abs(observed_limit - expected_limit) < 1e-4
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.LIMIT_VALUE_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.LM1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"limit_val": expected_limit},
            observed={"limit_val": observed_limit},
            reason="Evaluating the simplified expression at x = a yields the finite limit value.",
        )

    def check_derivative_function(
        self,
        *,
        expected_deriv: str,
        observed_deriv: str,
    ) -> AlphaTruthResult:
        def _clean(s: str) -> str:
            c = s.replace(" ", "").replace("*", "").lower()
            if "=" in c:
                c = c.split("=")[-1]
            return c
        norm_exp = _clean(expected_deriv)
        norm_obs = _clean(observed_deriv)
        valid = (norm_obs == norm_exp)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.DERIVATIVE_POWER_RULE_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.DV1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"derivative": expected_deriv},
            observed={"derivative": observed_deriv},
            reason="Power rule d/dx(ax^2 + bx + c) yields 2ax + b.",
        )

    def check_tangent_slope(
        self,
        *,
        expected_slope: float,
        observed_slope: float,
    ) -> AlphaTruthResult:
        valid = abs(observed_slope - expected_slope) < 1e-4
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.DERIVATIVE_SLOPE_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.DV1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"slope": expected_slope},
            observed={"slope": observed_slope},
            reason="Evaluating the derivative function at x0 yields tangent slope m = f'(x0).",
        )

    def check_tangent_line(
        self,
        *,
        expected_line: str,
        observed_line: str,
    ) -> AlphaTruthResult:
        def _clean_line(s: str) -> str:
            c = s.replace(" ", "").replace("*", "").lower()
            return c.replace("=1x", "=x").replace("+1x", "+x").replace("-1x", "-x")

        norm_exp = _clean_line(expected_line)
        norm_obs = _clean_line(observed_line)
        valid = (norm_obs == norm_exp)
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.TANGENT_LINE_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.DV2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"tangent_line": expected_line},
            observed={"tangent_line": observed_line},
            reason="Tangent line equation is given by point-slope form y - y0 = m(x - x0).",
        )

    def check_antiderivative(
        self,
        *,
        expected_antideriv: str,
        observed_antideriv: str,
    ) -> AlphaTruthResult:
        def _clean(s: str) -> str:
            c = s.replace(" ", "").replace("*", "").lower()
            if "=" in c:
                c = c.split("=")[-1]
            if c.endswith("+c"):
                c = c[:-2]
            return c.replace("+1x", "+x").replace("-1x", "-x").replace("=1x", "=x")

        norm_exp = _clean(expected_antideriv)
        norm_obs = _clean(observed_antideriv)
        valid = (norm_obs == norm_exp)
        # Check commutativity of terms (e.g. x^2+x vs x+x^2)
        if not valid:
            exp_parts = set(norm_exp.replace("-", "+-").split("+"))
            obs_parts = set(norm_obs.replace("-", "+-").split("+"))
            if exp_parts and exp_parts == obs_parts:
                valid = True

        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.INTEGRAL_ANTIDERIVATIVE_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.IN1,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"antiderivative": expected_antideriv},
            observed={"antiderivative": observed_antideriv},
            reason="Antiderivative F(x) = int f(x) dx is computed using the power rule for integration.",
        )

    def check_integral_limits_evaluation(
        self,
        *,
        expected_diff_str: str,
        observed_diff_str: str,
        expected_diff_val: float,
    ) -> AlphaTruthResult:
        def _clean(s: str) -> str:
            return s.replace(" ", "").lower()

        norm_exp = _clean(expected_diff_str)
        norm_obs = _clean(observed_diff_str)
        valid = (norm_obs == norm_exp)
        if not valid:
            # Check numeric evaluation
            try:
                # Handle "6 - 0" or "6"
                if "-" in norm_obs:
                    parts = norm_obs.split("-")
                    val = float(parts[0]) - float(parts[1])
                else:
                    val = float(norm_obs)
                valid = abs(val - expected_diff_val) < 1e-4
            except (ValueError, IndexError):
                valid = False

        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.INTEGRAL_LIMITS_EVALUATION_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.IN2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"limits_difference": expected_diff_str},
            observed={"limits_difference": observed_diff_str},
            reason="Evaluating limits requires computing the fundamental theorem difference F(b) - F(a).",
        )

    def check_definite_integral_value(
        self,
        *,
        expected_val: float,
        observed_val: float,
    ) -> AlphaTruthResult:
        valid = abs(observed_val - expected_val) < 1e-4
        facts: set[TruthFactCode] = set()
        if not valid:
            facts.add(TruthFactCode.INTEGRAL_VALUE_WRONG)
        return AlphaTruthResult(
            target_kc=KCId.IN2,
            is_valid=valid,
            facts=frozenset(facts),
            expected={"definite_integral": expected_val},
            observed={"definite_integral": observed_val},
            reason="Final definite integral value corresponds to net signed area under the curve.",
        )



