from __future__ import annotations

from enum import Enum
from typing import Dict, FrozenSet, List, Literal, Optional, Set

from pydantic import BaseModel, Field, model_validator


class AttemptJudgment(str, Enum):
    """Mutually distinct Alpha attempt outcomes.

    IMPORTANT:
    - VALID_INCOMPLETE is mathematically valid but task-incomplete.
    - VALID_SHORTCUT may complete a task but cannot launder evidence for
      bypassed knowledge components.
    """

    VALID_EXPECTED = "VALID_EXPECTED"
    VALID_INCOMPLETE = "VALID_INCOMPLETE"
    VALID_SHORTCUT = "VALID_SHORTCUT"
    INVALID_MATHEMATICS = "INVALID_MATHEMATICS"
    AMBIGUOUS_INPUT = "AMBIGUOUS_INPUT"
    UNSUPPORTED_STEP_FORM = "UNSUPPORTED_STEP_FORM"
    UNSUPPORTED_DOMAIN = "UNSUPPORTED_DOMAIN"


class AttemptActionType(str, Enum):
    ARITHMETIC_RESULT = "ARITHMETIC_RESULT"
    EXPRESSION_REWRITE = "EXPRESSION_REWRITE"
    EQUATION_REWRITE = "EQUATION_REWRITE"
    INEQUALITY_REWRITE = "INEQUALITY_REWRITE"
    COORDINATE_ASSIGNMENT = "COORDINATE_ASSIGNMENT"
    CLASSIFICATION = "CLASSIFICATION"
    FACTOR_PAIR_SELECTION = "FACTOR_PAIR_SELECTION"
    BRANCH_DECOMPOSITION = "BRANCH_DECOMPOSITION"
    SOLUTION_ASSIGNMENT = "SOLUTION_ASSIGNMENT"
    SOLUTION_SET = "SOLUTION_SET"
    CHOICE_RESPONSE = "CHOICE_RESPONSE"


class KCId(str, Enum):
    N1 = "KC-N1"
    N2 = "KC-N2"
    N3 = "KC-N3"
    E1 = "KC-E1"
    E2 = "KC-E2"
    Q0 = "KC-Q0"
    Q1 = "KC-Q1"
    F1 = "KC-F1"
    F2 = "KC-F2"
    Z1 = "KC-Z1"
    L1 = "KC-L1"
    L2 = "KC-L2"
    I1 = "KC-I1"
    P1 = "KC-P1"
    P2 = "KC-P2"
    PL1 = "KC-PL1"
    PL2 = "KC-PL2"
    TR1 = "KC-TR1"
    TR2 = "KC-TR2"
    LG1 = "KC-LG1"
    LG2 = "KC-LG2"
    LM1 = "KC-LM1"
    LM2 = "KC-LM2"
    DV1 = "KC-DV1"
    DV2 = "KC-DV2"
    IN1 = "KC-IN1"
    IN2 = "KC-IN2"


class StageId(str, Enum):
    S1_FACTOR = "S1_FACTOR"
    S2_BRANCH = "S2_BRANCH"
    S3_SOLVE_FACTOR_EQUATIONS = "S3_SOLVE_FACTOR_EQUATIONS"
    S4_COMPLETE_SOLUTION_SET = "S4_COMPLETE_SOLUTION_SET"
    S1_ISOLATE_TERM = "S1_ISOLATE_TERM"
    S2_ISOLATE_VARIABLE = "S2_ISOLATE_VARIABLE"
    S3_VERIFY_SOLUTION = "S3_VERIFY_SOLUTION"
    S2_DIRECTION_AWARE_DIVISION = "S2_DIRECTION_AWARE_DIVISION"
    S1_CALCULATE_R = "S1_CALCULATE_R"
    S2_CALCULATE_K = "S2_CALCULATE_K"
    S3_EXTREMUM_CLASSIFICATION = "S3_EXTREMUM_CLASSIFICATION"
    S1_ROOT_OF_DIVISOR = "S1_ROOT_OF_DIVISOR"
    S2_EVALUATE_REMAINDER = "S2_EVALUATE_REMAINDER"
    S1_ISOLATE_TRIG_VALUE = "S1_ISOLATE_TRIG_VALUE"
    S2_DETERMINE_PRINCIPAL_ANGLE = "S2_DETERMINE_PRINCIPAL_ANGLE"
    S3_DETERMINE_SECONDARY_ROOT = "S3_DETERMINE_SECONDARY_ROOT"
    S1_EXPONENTIAL_CONVERSION = "S1_EXPONENTIAL_CONVERSION"
    S3_VERIFY_DOMAIN_CONSTRAINT = "S3_VERIFY_DOMAIN_CONSTRAINT"
    S1_EVALUATE_LIMIT_FORM = "S1_EVALUATE_LIMIT_FORM"
    S2_SIMPLIFY_EXPRESSION = "S2_SIMPLIFY_EXPRESSION"
    S3_COMPUTE_FINAL_LIMIT = "S3_COMPUTE_FINAL_LIMIT"
    S1_COMPUTE_DERIVATIVE = "S1_COMPUTE_DERIVATIVE"
    S2_EVALUATE_SLOPE = "S2_EVALUATE_SLOPE"
    S3_DETERMINE_TANGENT_LINE = "S3_DETERMINE_TANGENT_LINE"
    S1_FIND_ANTIDERIVATIVE = "S1_FIND_ANTIDERIVATIVE"
    S2_APPLY_LIMITS = "S2_APPLY_LIMITS"
    S3_COMPUTE_DEFINITE_INTEGRAL = "S3_COMPUTE_DEFINITE_INTEGRAL"


class KCState(str, Enum):
    UNKNOWN = "UNKNOWN"
    EVIDENCE_SPARSE = "EVIDENCE_SPARSE"
    LOOKS_STABLE = "LOOKS_STABLE"
    SUSPECTED_GAP = "SUSPECTED_GAP"
    SUPPORTED_GAP = "SUPPORTED_GAP"
    CONFIRMED_GAP = "CONFIRMED_GAP"
    REPAIRING = "REPAIRING"
    TEMPORARILY_RECOVERED = "TEMPORARILY_RECOVERED"
    RETEST_DUE = "RETEST_DUE"
    RELAPSED = "RELAPSED"
    DURABLE_EVIDENCE = "DURABLE_EVIDENCE"


class BarrierState(str, Enum):
    UNSEEN = "UNSEEN"
    OBSERVED = "OBSERVED"
    SUSPECTED = "SUSPECTED"
    PROBED = "PROBED"
    SUPPORTED = "SUPPORTED"
    CONFIRMED = "CONFIRMED"
    DISCONFIRMED = "DISCONFIRMED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REPAIRING = "REPAIRING"
    TEMPORARILY_RECOVERED = "TEMPORARILY_RECOVERED"
    RETEST_DUE = "RETEST_DUE"
    RELAPSED = "RELAPSED"
    DURABLE_EVIDENCE = "DURABLE_EVIDENCE"


class CompositeTaskState(str, Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED_WITH_SUPPORT = "COMPLETED_WITH_SUPPORT"
    COMPLETED_INDEPENDENTLY = "COMPLETED_INDEPENDENTLY"


class CompositeTaskFailureCode(str, Enum):
    ROOT_BRANCH_INCOMPLETE = "CTF-QF1-01_ROOT_BRANCH_INCOMPLETE"


class BranchAssignmentStatus(str, Enum):
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"
    UNSUPPORTED = "UNSUPPORTED"


class ProbeEvidenceKind(str, Enum):
    POSITIVE = "POSITIVE"
    GAP = "GAP"
    BARRIER_SUPPORT = "BARRIER_SUPPORT"
    BARRIER_WEAKEN = "BARRIER_WEAKEN"
    INCONCLUSIVE = "INCONCLUSIVE"


class CTQF1TaskContext(BaseModel):
    """Server-owned deterministic CT-QF1 problem context.

    The client supplies only b and c at episode creation. The server derives
    the unique Alpha factor pair and roots inside the frozen generation profile.
    """

    b: int
    c: int
    factor_pair: tuple[int, int]
    expected_roots: tuple[int, int]
    factor_abs_max: int = 6

    @classmethod
    def from_coefficients(
        cls,
        *,
        b: int,
        c: int,
        factor_abs_max: int = 6,
    ) -> "CTQF1TaskContext":
        allowed = [
            value
            for value in range(-factor_abs_max, factor_abs_max + 1)
            if value != 0
        ]
        pairs: set[tuple[int, int]] = set()
        for m in allowed:
            for n in allowed:
                if m == n:
                    continue
                if m + n == b and m * n == c:
                    pairs.add(tuple(sorted((m, n))))

        if len(pairs) != 1:
            raise ValueError(
                "CT-QF1 Alpha requires exactly one non-zero, non-repeated "
                "integer factor pair inside the generation profile"
            )

        pair = next(iter(pairs))
        roots = tuple(sorted((-pair[0], -pair[1])))
        return cls(
            b=b,
            c=c,
            factor_pair=pair,
            expected_roots=roots,
            factor_abs_max=factor_abs_max,
        )

    @property
    def expected_branch_equations(self) -> frozenset[str]:
        result = []
        for constant in self.factor_pair:
            if constant > 0:
                result.append(f"x+{constant}=0")
            else:
                result.append(f"x-{abs(constant)}=0")
        return frozenset(result)


class CTLIN1TaskContext(BaseModel):
    """Server-owned deterministic CT-LIN1 linear equation task context: ax + b = c."""

    a: int
    b: int
    c: int
    expected_intermediate_rhs: int
    expected_root: int
    target_equation: str

    @classmethod
    def from_coefficients(cls, *, a: int, b: int, c: int) -> "CTLIN1TaskContext":
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero in linear equation ax + b = c")
        if (c - b) % a != 0:
            raise ValueError(f"Coefficients ({a}, {b}, {c}) do not yield an integer solution")
        d = c - b
        root = d // a
        b_part = f"+{b}" if b > 0 else (f"{b}" if b < 0 else "")
        return cls(
            a=a,
            b=b,
            c=c,
            expected_intermediate_rhs=d,
            expected_root=root,
            target_equation=f"{a}x{b_part}={c}",
        )


class CTINEQ1TaskContext(BaseModel):
    """Server-owned deterministic CT-INEQ1 linear inequality task context: ax + b <= c."""

    a: int
    b: int
    c: int
    comparator: str = "<="
    expected_intermediate_rhs: int
    expected_root: int
    expected_comparator: str
    target_inequality: str

    @classmethod
    def from_coefficients(
        cls, *, a: int, b: int, c: int, comparator: str = "<="
    ) -> "CTINEQ1TaskContext":
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero in linear inequality")
        if (c - b) % a != 0:
            raise ValueError(f"Coefficients ({a}, {b}, {c}) do not yield an integer boundary")
        d = c - b
        root = d // a
        flip_map = {"<=": ">=", "<": ">", ">=": "<=", ">": "<"}
        expected_comp = flip_map[comparator] if a < 0 else comparator
        b_part = f"+{b}" if b > 0 else (f"{b}" if b < 0 else "")
        return cls(
            a=a,
            b=b,
            c=c,
            comparator=comparator,
            expected_intermediate_rhs=d,
            expected_root=root,
            expected_comparator=expected_comp,
            target_inequality=f"{a}x{b_part}{comparator}{c}",
        )


class CTPAR1TaskContext(BaseModel):
    """Server-owned deterministic CT-PAR1 parabola vertex task context: f(x) = ax^2 + bx + c."""

    a: int
    b: int
    c: int
    expected_r: float
    expected_k: float
    is_minimum: bool
    target_function: str

    @classmethod
    def from_coefficients(cls, *, a: int, b: int, c: int) -> "CTPAR1TaskContext":
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero in quadratic function ax^2 + bx + c")
        r = -b / (2.0 * a)
        k = a * (r ** 2) + b * r + c
        is_min = (a > 0)
        b_part = f"+{b}x" if b > 0 else (f"{b}x" if b < 0 else "")
        c_part = f"+{c}" if c > 0 else (f"{c}" if c < 0 else "")
        return cls(
            a=a,
            b=b,
            c=c,
            expected_r=r,
            expected_k=k,
            is_minimum=is_min,
            target_function=f"{a}x^2{b_part}{c_part}",
        )


class CTPOLY1TaskContext(BaseModel):
    """Server-owned deterministic CT-POLY1 polynomial remainder task context: P(x) = ax^2 + bx + c, divisor x - d."""

    a: int
    b: int
    c: int
    divisor_root: int
    expected_remainder: int
    target_polynomial: str
    target_divisor: str

    @classmethod
    def from_coefficients(
        cls, *, a: int, b: int, c: int, divisor_root: int
    ) -> "CTPOLY1TaskContext":
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero in polynomial P(x) = ax^2 + bx + c")
        d = divisor_root
        rem = a * (d ** 2) + b * d + c
        b_part = f"+{b}x" if b > 0 else (f"{b}x" if b < 0 else "")
        c_part = f"+{c}" if c > 0 else (f"{c}" if c < 0 else "")
        div_part = f"x-{d}" if d > 0 else (f"x+{-d}" if d < 0 else "x")
        return cls(
            a=a,
            b=b,
            c=c,
            divisor_root=d,
            expected_remainder=rem,
            target_polynomial=f"{a}x^2{b_part}{c_part}",
            target_divisor=div_part,
        )


class CTTRIG1TaskContext(BaseModel):
    """Server-owned deterministic CT-TRIG1 trigonometric equation task context: a*sin(x) - c = 0."""

    a: int = 2
    c: int = 1
    expected_ratio: float = 0.5
    expected_principal_deg: int = 30
    expected_secondary_deg: int = 150
    target_equation: str = "2sin(x) - 1 = 0"

    @classmethod
    def from_coefficients(cls, *, a: int = 2, c: int = 1) -> "CTTRIG1TaskContext":
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero in a*sin(x) - c = 0")
        ratio = float(c) / float(a)
        if abs(ratio - 0.5) < 1e-4:
            p_deg = 30
            s_deg = 150
        elif abs(ratio - 1.0) < 1e-4:
            p_deg = 90
            s_deg = 90
        elif abs(ratio - 0.0) < 1e-4:
            p_deg = 0
            s_deg = 180
        elif abs(ratio - (-0.5)) < 1e-4:
            p_deg = 210
            s_deg = 330
        elif abs(ratio - (-1.0)) < 1e-4:
            p_deg = 270
            s_deg = 270
        else:
            p_deg = 30
            s_deg = 150

        c_part = f"- {c}" if c > 0 else (f"+ {-c}" if c < 0 else "")
        return cls(
            a=a,
            c=c,
            expected_ratio=ratio,
            expected_principal_deg=p_deg,
            expected_secondary_deg=s_deg,
            target_equation=f"{a}sin(x) {c_part} = 0".strip(),
        )


class CTLOG1TaskContext(BaseModel):
    """Server-owned deterministic CT-LOG1 logarithmic equation task context: log_b(x - c) = k."""

    base: int = 2
    c: int = 3
    k: int = 3
    expected_power: int = 8
    expected_x: int = 11
    is_domain_valid: bool = True
    target_equation: str = "log_2(x - 3) = 3"

    @classmethod
    def from_parameters(
        cls, *, base: int = 2, c: int = 3, k: int = 3
    ) -> "CTLOG1TaskContext":
        if base <= 0 or base == 1:
            raise ValueError("Logarithm base must be positive and not equal to 1")
        power = base ** k
        x_val = power + c
        domain_valid = (x_val - c) > 0
        c_part = f"- {c}" if c > 0 else (f"+ {-c}" if c < 0 else "")
        return cls(
            base=base,
            c=c,
            k=k,
            expected_power=power,
            expected_x=x_val,
            is_domain_valid=domain_valid,
            target_equation=f"log_{base}(x {c_part}) = {k}".strip(),
        )


class CTLIM1TaskContext(BaseModel):
    """Server-owned deterministic CT-LIM1 limit & 0/0 indeterminate task context: lim_{x -> a} (x^2 - a^2)/(x - a)."""

    a: int = 2
    target_x: int = 2
    expected_indeterminate_form: str = "0/0"
    expected_simplified_expr: str = "x + 2"
    expected_limit_val: float = 4.0
    target_expression: str = "lim_{x -> 2} (x^2 - 4)/(x - 2)"

    @classmethod
    def from_parameters(cls, *, a: int = 2) -> "CTLIM1TaskContext":
        if a == 0:
            raise ValueError("Parameter 'a' cannot be zero in lim_{x -> a} (x^2 - a^2)/(x - a)")
        a_sq = a * a
        simp = f"x + {a}" if a > 0 else (f"x - {-a}" if a < 0 else "x")
        lim_val = float(2 * a)
        return cls(
            a=a,
            target_x=a,
            expected_indeterminate_form="0/0",
            expected_simplified_expr=simp,
            expected_limit_val=lim_val,
            target_expression=f"lim_{{x -> {a}}} (x^2 - {a_sq})/(x - {a})",
        )


class CTDERIV1TaskContext(BaseModel):
    """Server-owned deterministic CT-DERIV1 polynomial derivative & tangent line task context: f(x) = ax^2 + bx + c at x0."""

    a: int = 1
    b: int = -3
    c: int = 2
    x0: int = 2
    expected_derivative_str: str = "2x - 3"
    expected_slope: float = 1.0
    expected_y0: float = 0.0
    expected_tangent_line: str = "y = x - 2"
    target_function: str = "f(x) = x^2 - 3x + 2"

    @classmethod
    def from_coefficients(
        cls, *, a: int = 1, b: int = -3, c: int = 2, x0: int = 2
    ) -> "CTDERIV1TaskContext":
        if a == 0:
            raise ValueError("Leading coefficient 'a' cannot be zero in CT-DERIV1")
        slope = float(2 * a * x0 + b)
        y0 = float(a * x0 * x0 + b * x0 + c)
        two_a = 2 * a
        deriv_b = f"+ {b}" if b > 0 else (f"- {-b}" if b < 0 else "")
        deriv_str = f"{two_a}x {deriv_b}".strip()

        # Tangent line: y - y0 = m(x - x0) => y = m*x + (y0 - m*x0)
        c_line = y0 - slope * x0
        m_str = f"{int(slope)}" if slope.is_integer() else f"{slope}"
        c_str = f"+ {int(c_line)}" if c_line > 0 and c_line.is_integer() else (
            f"- {int(-c_line)}" if c_line < 0 and c_line.is_integer() else (
                f"+ {c_line}" if c_line > 0 else (f"- {-c_line}" if c_line < 0 else "")
            )
        )
        tangent_str = f"y = {m_str}x {c_str}".strip() if c_line != 0 else f"y = {m_str}x"

        b_func = f"+ {b}x" if b > 0 else (f"- {-b}x" if b < 0 else "")
        c_func = f"+ {c}" if c > 0 else (f"- {-c}" if c < 0 else "")
        func_str = f"f(x) = {a}x^2 {b_func} {c_func}".strip()

        return cls(
            a=a,
            b=b,
            c=c,
            x0=x0,
            expected_derivative_str=deriv_str,
            expected_slope=slope,
            expected_y0=y0,
            expected_tangent_line=tangent_str,
            target_function=func_str,
        )


class CTINT1TaskContext(BaseModel):
    """Server-owned deterministic CT-INT1 definite integral & area task context: int_a^b (m*x + n) dx."""

    a: int = 0
    b: int = 2
    poly_m: int = 2
    poly_n: int = 1
    expected_antiderivative_str: str = "x^2 + x"
    expected_f_b: float = 6.0
    expected_f_a: float = 0.0
    expected_definite_integral: float = 6.0
    target_integral: str = "int_0^2 (2x + 1) dx"

    @property
    def expected_fb(self) -> float:
        return self.expected_f_b

    @property
    def expected_fa(self) -> float:
        return self.expected_f_a

    @property
    def expected_definite_value(self) -> float:
        return self.expected_definite_integral

    @classmethod
    def from_parameters(
        cls,
        *,
        a: int = 0,
        b: int = 2,
        poly_m: Optional[int] = None,
        poly_n: Optional[int] = None,
        m: Optional[int] = None,
        n: Optional[int] = None,
    ) -> "CTINT1TaskContext":
        if a == b:
            raise ValueError("Integration limits 'a' and 'b' cannot be equal in CT-INT1")
        resolved_m = poly_m if poly_m is not None else (m if m is not None else 2)
        resolved_n = poly_n if poly_n is not None else (n if n is not None else 1)
        # f(x) = m*x + n => F(x) = (m/2)*x^2 + n*x
        m_half = resolved_m / 2.0
        m_half_str = f"{int(m_half)}" if m_half.is_integer() else f"{m_half}"
        if m_half == 1.0:
            m_part = "x^2"
        elif m_half == -1.0:
            m_part = "-x^2"
        elif m_half != 0:
            m_part = f"{m_half_str}x^2"
        else:
            m_part = ""

        if resolved_n == 1:
            n_part = "+ x" if m_part else "x"
        elif resolved_n == -1:
            n_part = "- x" if m_part else "-x"
        elif resolved_n > 0:
            n_part = f"+ {resolved_n}x" if m_part else f"{resolved_n}x"
        elif resolved_n < 0:
            n_part = f"- {-resolved_n}x" if m_part else f"-{-resolved_n}x"
        else:
            n_part = ""

        antideriv = f"{m_part} {n_part}".strip()
        if not antideriv:
            antideriv = "0"

        fb = float(m_half * b * b + resolved_n * b)
        fa = float(m_half * a * a + resolved_n * a)
        def_int = float(fb - fa)

        m_term = f"{resolved_m}x" if resolved_m != 0 else ""
        n_term = f"+ {resolved_n}" if resolved_n > 0 else (f"- {-resolved_n}" if resolved_n < 0 else "")
        integrand = f"{m_term} {n_term}".strip() if (m_term or n_term) else "0"

        return cls(
            a=a,
            b=b,
            poly_m=resolved_m,
            poly_n=resolved_n,
            expected_antiderivative_str=antideriv,
            expected_f_b=fb,
            expected_f_a=fa,
            expected_definite_integral=def_int,
            target_integral=f"int_{a}^{b} ({integrand}) dx",
        )


class AttemptEnvelope(BaseModel):
    attempt_id: str
    problem_family_id: str
    composite_task_id: Optional[str] = None
    stage_id: Optional[StageId] = None
    action_type: AttemptActionType
    payload_ast: Dict[str, object]
    raw_input: Optional[str] = None
    parser_status: str = "PARSED"


class BranchWorkItem(BaseModel):
    """One factor branch in CT-QF1 S3.

    v0.4 Alpha excludes repeated roots, so CT-QF1 normally owns exactly two
    distinct BranchWorkItems.
    """

    branch_id: str
    source_factor: str
    expected_equation: str
    expected_assignment: str
    assignment_status: BranchAssignmentStatus = BranchAssignmentStatus.PENDING
    observed_attempt_id: Optional[str] = None


class BranchWorkSet(BaseModel):
    composite_task_id: Literal["CT-QF1"] = "CT-QF1"
    stage_id: Literal[StageId.S3_SOLVE_FACTOR_EQUATIONS] = (
        StageId.S3_SOLVE_FACTOR_EQUATIONS
    )
    branch_items: List[BranchWorkItem] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def validate_distinct_branches(self) -> "BranchWorkSet":
        branch_ids = [item.branch_id for item in self.branch_items]
        if len(set(branch_ids)) != 2:
            raise ValueError("CT-QF1 Alpha requires two distinct branch IDs")

        equations = [item.expected_equation for item in self.branch_items]
        if len(set(equations)) != 2:
            raise ValueError(
                "Repeated-root/equal-factor branch sets are outside Alpha"
            )
        return self

    @property
    def is_complete(self) -> bool:
        return all(
            item.assignment_status == BranchAssignmentStatus.VALID
            for item in self.branch_items
        )


class ProbeResponseClass(BaseModel):
    code: str
    evidence_kind: ProbeEvidenceKind
    description: str


class ProbeTemplate(BaseModel):
    probe_id: str
    target_kc: KCId
    candidate_barriers: FrozenSet[str] = frozenset()
    prompt_schema: str
    parameter_constraints: str
    truth_rule: str
    response_classes: List[ProbeResponseClass]
    new_prerequisites: FrozenSet[str] = frozenset()
    max_steps: int = Field(default=1, ge=1, le=1)


class InterventionTemplate(BaseModel):
    intervention_id: str
    target_kc: Optional[KCId] = None
    target_task: Optional[str] = None
    eligible_barriers: FrozenSet[str] = frozenset()
    eligible_failures: FrozenSet[CompositeTaskFailureCode] = frozenset()
    allowed_barrier_states: FrozenSet[BarrierState] = frozenset()
    allowed_kc_states: FrozenSet[KCState] = frozenset()
    neutral_support_allowed: bool = False
    student_action: str
    prompt_schema: str
    truth_rule: str
    success_condition: str
    failure_condition: str
    max_attempts: int = Field(default=1, ge=1, le=1)
    next_action_on_success: str
    next_action_on_failure: str
    prohibited_scaffolds: FrozenSet[str] = frozenset()

    @model_validator(mode="after")
    def validate_target(self) -> "InterventionTemplate":
        if bool(self.target_kc) == bool(self.target_task):
            raise ValueError(
                "Intervention must target exactly one of target_kc or target_task"
            )
        return self


class RepairEvidencePolicy(BaseModel):
    """Machine-evaluable evidence guard for one RepairEdge.

    Human-readable ``required_evidence`` remains documentation only; routing
    authority comes from this structured policy.
    """

    accepted_probe_evidence: Dict[str, FrozenSet[ProbeEvidenceKind]] = Field(
        default_factory=dict
    )
    allowed_target_kc_states: FrozenSet[KCState] = frozenset()
    state_support_required_flags: FrozenSet[str] = frozenset()
    required_flags: FrozenSet[str] = frozenset()
    disqualifying_flags: FrozenSet[str] = frozenset()


class RepairEdge(BaseModel):
    edge_id: str
    from_kc: KCId
    to_kc: KCId
    eligible_observations: FrozenSet[str]
    required_evidence: str
    evidence_policy: RepairEvidencePolicy
    preferred_probe_id: Optional[str] = None
    disqualifying_evidence: FrozenSet[str] = frozenset()
    entry_intervention_ids: FrozenSet[str] = frozenset()
    fallback_action: str


class ActiveKCDiagnosticRoute(BaseModel):
    route_id: str
    active_kc: KCId
    eligible_observations: FrozenSet[str]
    probe_id: str
    intervention_id: str
    barrier_id: Optional[str] = None


class ShortcutEvidenceResult(BaseModel):
    task_state: CompositeTaskState
    kc_states: Dict[KCId, KCState]
    barrier_states: Dict[str, BarrierState]
    retest_due: Set[KCId] = Field(default_factory=set)
    preserved_existing_evidence: bool = True


class TransferTaskContext(BaseModel):
    """Server-owned transfer problem context for testing post-repair recovery."""
    target_kc: KCId
    prompt: str
    expected_answer: str
    parameter_context: Dict[str, int] = Field(default_factory=dict)

