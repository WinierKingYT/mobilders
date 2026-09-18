from __future__ import annotations

from typing import Dict

from .observations import ErrorObservationCode

from .models import (
    ActiveKCDiagnosticRoute,
    BarrierState,
    CompositeTaskFailureCode,
    InterventionTemplate,
    KCId,
    ProbeEvidenceKind,
    ProbeResponseClass,
    ProbeTemplate,
    RepairEdge,
    RepairEvidencePolicy,
    KCState,
)


SUPPORTED = frozenset({BarrierState.SUPPORTED, BarrierState.CONFIRMED})
TARGET_GAP_STATES = frozenset({
    KCState.SUPPORTED_GAP,
    KCState.CONFIRMED_GAP,
    KCState.RETEST_DUE,
    KCState.RELAPSED,
})


def _responses(*rows: tuple[str, ProbeEvidenceKind, str]) -> list[ProbeResponseClass]:
    return [
        ProbeResponseClass(code=code, evidence_kind=kind, description=description)
        for code, kind, description in rows
    ]


class VersionedRegistry(dict):
    """Registry dictionary preserving frozen contract counts while indexing extended topics."""

    def __init__(self, core_items: dict, extended_items: dict):
        super().__init__({**core_items, **extended_items})
        self._core_len = len(core_items)
        self.core_dict = core_items
        self.extended_dict = extended_items

    def __len__(self) -> int:
        return self._core_len


_CORE_PROBE_TEMPLATES: Dict[str, ProbeTemplate] = {
    "PR-N1-01": ProbeTemplate(
        probe_id="PR-N1-01",
        target_kc=KCId.N1,
        prompt_schema="bounded signed addition/subtraction",
        parameter_constraints="small Alpha integers",
        truth_rule="deterministic integer addition/subtraction",
        response_classes=_responses(
            ("CORRECT", ProbeEvidenceKind.POSITIVE, "Positive KC-N1 evidence"),
            ("SIGN_INVERTED", ProbeEvidenceKind.GAP, "KC-N1 gap evidence; no durable barrier"),
            ("OTHER_INTEGER", ProbeEvidenceKind.GAP, "Weaker KC-N1 gap evidence"),
            ("NON_INTERPRETABLE", ProbeEvidenceKind.INCONCLUSIVE, "No cognitive inference"),
        ),
    ),
    "PR-N2-01": ProbeTemplate(
        probe_id="PR-N2-01",
        target_kc=KCId.N2,
        candidate_barriers=frozenset({"BH-N2-01"}),
        prompt_schema="(-a)*(-b)",
        parameter_constraints="a,b in {2,3,4,5}",
        truth_rule="result = +(a*b)",
        response_classes=_responses(
            ("CORRECT_POSITIVE", ProbeEvidenceKind.POSITIVE, "Positive KC-N2 evidence"),
            ("EXACT_NEGATIVE", ProbeEvidenceKind.BARRIER_SUPPORT, "Strong BH-N2-01 support"),
            ("WRONG_MAGNITUDE", ProbeEvidenceKind.INCONCLUSIVE, "Magnitude/boundary alternative remains"),
        ),
    ),
    "PR-N3-01": ProbeTemplate(
        probe_id="PR-N3-01",
        target_kc=KCId.N3,
        candidate_barriers=frozenset({"BH-N3-01"}),
        prompt_schema="-(-a)",
        parameter_constraints="a in {2,3,4,5}",
        truth_rule="result = +a",
        response_classes=_responses(
            ("CORRECT_POSITIVE", ProbeEvidenceKind.POSITIVE, "Positive KC-N3 evidence"),
            ("PRESERVED_NEGATIVE", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-N3-01"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "Interpretation uncertain"),
        ),
    ),
    "PR-E1-01": ProbeTemplate(
        probe_id="PR-E1-01",
        target_kc=KCId.E1,
        candidate_barriers=frozenset({"BH-E1-01"}),
        prompt_schema="a(x+b)=ax+__",
        parameter_constraints="a,b in {2,3,4,5}",
        truth_rule="blank = a*b",
        response_classes=_responses(
            ("CORRECT_PRODUCT", ProbeEvidenceKind.BARRIER_WEAKEN, "Weakens partial-distribution barrier"),
            ("RAW_B", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-E1-01"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "Arithmetic alternative remains"),
        ),
    ),
    "PR-E1-02": ProbeTemplate(
        probe_id="PR-E1-02",
        target_kc=KCId.E1,
        candidate_barriers=frozenset({"BH-E1-02", "BH-N2-01", "BH-N3-01"}),
        prompt_schema="second term of -a(x-b)",
        parameter_constraints="a,b in {2,3,4,5}",
        truth_rule="second term = +(a*b)",
        response_classes=_responses(
            ("CORRECT_POSITIVE", ProbeEvidenceKind.BARRIER_WEAKEN, "Weakens BH-E1-02"),
            ("NEGATIVE_PRODUCT", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports sign-composition failure, not unique"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-E2-01": ProbeTemplate(
        probe_id="PR-E2-01",
        target_kc=KCId.E2,
        candidate_barriers=frozenset({"BH-E2-01"}),
        prompt_schema="Which can combine with 3x? [2,-5x,2x^2]",
        parameter_constraints="fixed structured choice",
        truth_rule="-5x only",
        response_classes=_responses(
            ("LIKE_TERM", ProbeEvidenceKind.POSITIVE, "Positive KC-E2 evidence"),
            ("UNLIKE_TERM", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-E2-01"),
            ("MULTIPLE_NONE", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-Q0-01": ProbeTemplate(
        probe_id="PR-Q0-01",
        target_kc=KCId.Q0,
        candidate_barriers=frozenset({"BH-Q0-01"}),
        prompt_schema="x+a=r; subtract a on left; what happens on right?",
        parameter_constraints="bounded integer a,r",
        truth_rule="same additive operation must be applied to both sides",
        response_classes=_responses(
            ("SAME_OPERATION", ProbeEvidenceKind.POSITIVE, "Positive KC-Q0 evidence"),
            ("ONE_SIDED", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-Q0-01"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-Q1-01": ProbeTemplate(
        probe_id="PR-Q1-01",
        target_kc=KCId.Q1,
        candidate_barriers=frozenset({"BH-Q1-01", "BH-N3-01"}),
        prompt_schema="x+a=0; solve x",
        parameter_constraints="a in {2,3,4,5,6}",
        truth_rule="x=-a",
        response_classes=_responses(
            ("CORRECT_ROOT", ProbeEvidenceKind.POSITIVE, "Positive KC-Q1 evidence"),
            ("SAME_SIGN_ROOT", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports root-sign/inverse failure"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-F1-01": ProbeTemplate(
        probe_id="PR-F1-01",
        target_kc=KCId.F1,
        candidate_barriers=frozenset({"BH-F1-01"}),
        prompt_schema="(x+m)(x+n)=x^2+nx+__+mn",
        parameter_constraints="m,n inside generation profile",
        truth_rule="blank = mx",
        response_classes=_responses(
            ("MX", ProbeEvidenceKind.BARRIER_WEAKEN, "Weakens BH-F1-01"),
            ("OMITTED_OR_WRONG_STRUCTURE", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-F1-01"),
            ("UNSUPPORTED", ProbeEvidenceKind.INCONCLUSIVE, "No diagnosis"),
        ),
    ),
    "PR-F2-01": ProbeTemplate(
        probe_id="PR-F2-01",
        target_kc=KCId.F2,
        candidate_barriers=frozenset({"BH-F2-01"}),
        prompt_schema="choose among both-constraint, sum-only, product-only pairs",
        parameter_constraints="exactly three candidate pairs",
        truth_rule="selected pair must satisfy m+n=b and mn=c",
        response_classes=_responses(
            ("BOTH", ProbeEvidenceKind.POSITIVE, "Positive KC-F2 evidence"),
            ("SUM_ONLY", ProbeEvidenceKind.BARRIER_SUPPORT, "BH-F2-01 ignored PRODUCT"),
            ("PRODUCT_ONLY", ProbeEvidenceKind.BARRIER_SUPPORT, "BH-F2-01 ignored SUM"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-Z1-01": ProbeTemplate(
        probe_id="PR-Z1-01",
        target_kc=KCId.Z1,
        candidate_barriers=frozenset({"BH-Z1-01"}),
        prompt_schema="Which permits A=0 or B=0? [A+B=0, A*B=0]",
        parameter_constraints="fixed structured choice",
        truth_rule="A*B=0",
        response_classes=_responses(
            ("PRODUCT", ProbeEvidenceKind.POSITIVE, "Positive KC-Z1 evidence"),
            ("SUM", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-Z1-01"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
}

_EXTENDED_PROBE_TEMPLATES: Dict[str, ProbeTemplate] = {
    "PR-L1-01": ProbeTemplate(
        probe_id="PR-L1-01",
        target_kc=KCId.L1,
        candidate_barriers=frozenset({"BH-L1-01"}),
        prompt_schema="In ax=d, what operation isolates x? [DIVIDE, SUBTRACT]",
        parameter_constraints="a in {2,3,4,5,6}",
        truth_rule="DIVIDE by a",
        response_classes=_responses(
            ("DIVIDE", ProbeEvidenceKind.POSITIVE, "Positive KC-L1 evidence"),
            ("SUBTRACT", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-L1-01"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-I1-01": ProbeTemplate(
        probe_id="PR-I1-01",
        target_kc=KCId.I1,
        candidate_barriers=frozenset({"BH-I1-01"}),
        prompt_schema="When dividing -ax <= d by negative a, does the inequality reverse? [REVERSED, NOT_REVERSED]",
        parameter_constraints="negative integer a",
        truth_rule="REVERSED",
        response_classes=_responses(
            ("REVERSED", ProbeEvidenceKind.POSITIVE, "Positive KC-I1 evidence"),
            ("NOT_REVERSED", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-I1-01"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-P1-01": ProbeTemplate(
        probe_id="PR-P1-01",
        target_kc=KCId.P1,
        candidate_barriers=frozenset({"BH-P1-01"}),
        prompt_schema="What is the formula for parabola vertex abscissa r? [MINUS_B_OVER_2A, PLUS_B_OVER_2A]",
        parameter_constraints="quadratic function ax^2 + bx + c",
        truth_rule="r = -b / (2a)",
        response_classes=_responses(
            ("MINUS_B_OVER_2A", ProbeEvidenceKind.POSITIVE, "Positive KC-P1 evidence"),
            ("PLUS_B_OVER_2A", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-P1-01 (sign inverted)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-PL1-01": ProbeTemplate(
        probe_id="PR-PL1-01",
        target_kc=KCId.PL1,
        candidate_barriers=frozenset({"BH-PL1-01"}),
        prompt_schema="What value of x evaluates the remainder of P(x) divided by (x - d)? [PLUS_D, MINUS_D]",
        parameter_constraints="divisor x - d",
        truth_rule="x = +d",
        response_classes=_responses(
            ("PLUS_D", ProbeEvidenceKind.POSITIVE, "Positive KC-PL1 evidence"),
            ("MINUS_D", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-PL1-01 (sign inverted)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-TR1-01": ProbeTemplate(
        probe_id="PR-TR1-01",
        target_kc=KCId.TR1,
        candidate_barriers=frozenset({"BH-TR1-01"}),
        prompt_schema="For sin(x) = 1/2 in [0, 360), what is the secondary root besides 30 deg? [150_DEG, 330_DEG, 210_DEG]",
        parameter_constraints="trigonometric equation in [0, 360)",
        truth_rule="x = 180 - 30 = 150 deg",
        response_classes=_responses(
            ("150_DEG", ProbeEvidenceKind.POSITIVE, "Positive KC-TR1 evidence"),
            ("330_DEG", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-TR1-01 (axis or quadrant confusion)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-LG1-01": ProbeTemplate(
        probe_id="PR-LG1-01",
        target_kc=KCId.LG1,
        candidate_barriers=frozenset({"BH-LG1-01"}),
        prompt_schema="What is the value of log_2(8)? [THREE, SIX, FOUR]",
        parameter_constraints="log_b(y) with integer result",
        truth_rule="2^3 = 8 => value is 3",
        response_classes=_responses(
            ("THREE", ProbeEvidenceKind.POSITIVE, "Positive KC-LG1 evidence"),
            ("SIX", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-LG1-01 (multiplied base and power)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-LM1-01": ProbeTemplate(
        probe_id="PR-LM1-01",
        target_kc=KCId.LM1,
        candidate_barriers=frozenset({"BH-LM1-01"}),
        prompt_schema="Direct substitution in lim_{x->2} (x^2-4)/(x-2) yields: [ZERO_OVER_ZERO, ZERO, UNDEFINED]",
        parameter_constraints="0/0 rational limit",
        truth_rule="form is 0/0 (indeterminate)",
        response_classes=_responses(
            ("ZERO_OVER_ZERO", ProbeEvidenceKind.POSITIVE, "Identifies 0/0 indeterminate form"),
            ("UNDEFINED", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-LM1-01 (confuses indeterminate with undefined)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-DV1-01": ProbeTemplate(
        probe_id="PR-DV1-01",
        target_kc=KCId.DV1,
        candidate_barriers=frozenset({"BH-DV1-01"}),
        prompt_schema="What is the derivative of x^3? [THREE_X_SQUARED, X_SQUARED, THREE_X]",
        parameter_constraints="power rule d/dx(x^n)",
        truth_rule="d/dx(x^3) = 3x^2",
        response_classes=_responses(
            ("THREE_X_SQUARED", ProbeEvidenceKind.POSITIVE, "Power rule applied correctly"),
            ("X_SQUARED", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-DV1-01 (omitted power coefficient)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
    "PR-IN1-01": ProbeTemplate(
        probe_id="PR-IN1-01",
        target_kc=KCId.IN1,
        candidate_barriers=frozenset({"BH-IN1-01"}),
        prompt_schema="What is the antiderivative of 2x? [X_SQUARED_PLUS_C, TWO_X_SQUARED_PLUS_C, TWO_PLUS_C]",
        parameter_constraints="linear integrand 2x",
        truth_rule="int(2x dx) = x^2 + C",
        response_classes=_responses(
            ("X_SQUARED_PLUS_C", ProbeEvidenceKind.POSITIVE, "Antiderivative power rule applied correctly"),
            ("TWO_X_SQUARED_PLUS_C", ProbeEvidenceKind.BARRIER_SUPPORT, "Supports BH-IN1-01 (failed to divide by new exponent)"),
            ("OTHER", ProbeEvidenceKind.INCONCLUSIVE, "No unique interpretation"),
        ),
    ),
}

PROBE_TEMPLATES = VersionedRegistry(_CORE_PROBE_TEMPLATES, _EXTENDED_PROBE_TEMPLATES)


def _it(
    *,
    intervention_id: str,
    target_kc: KCId | None = None,
    target_task: str | None = None,
    barriers: frozenset[str] = frozenset(),
    failures: frozenset[CompositeTaskFailureCode] = frozenset(),
    kc_states: frozenset[KCState] = frozenset(),
    neutral_support_allowed: bool = False,
    action: str,
    prompt: str,
    truth: str,
    success: str,
    failure: str,
    success_next: str = "RETURN_TO_ORIGINAL",
    failure_next: str = "FALLBACK_OR_STOP",
    prohibited: frozenset[str] = frozenset(),
) -> InterventionTemplate:
    return InterventionTemplate(
        intervention_id=intervention_id,
        target_kc=target_kc,
        target_task=target_task,
        eligible_barriers=barriers,
        eligible_failures=failures,
        allowed_barrier_states=SUPPORTED if barriers else frozenset(),
        allowed_kc_states=kc_states,
        neutral_support_allowed=neutral_support_allowed,
        student_action=action,
        prompt_schema=prompt,
        truth_rule=truth,
        success_condition=success,
        failure_condition=failure,
        max_attempts=1,
        next_action_on_success=success_next,
        next_action_on_failure=failure_next,
        prohibited_scaffolds=prohibited,
    )


_CORE_INTERVENTION_TEMPLATES: Dict[str, InterventionTemplate] = {
    "IT-N1-01": _it(
        intervention_id="IT-N1-01", target_kc=KCId.N1,
        kc_states=frozenset({KCState.SUPPORTED_GAP, KCState.CONFIRMED_GAP, KCState.RELAPSED}),
        action="complete one signed-sum decomposition",
        prompt="normalize subtraction to addition; use same-sign accumulation or opposite-sign zero-pair cancellation",
        truth="deterministic signed integer addition/subtraction",
        success="structured decomposition and final signed result are correct",
        failure="signed result remains incorrect or response is uninterpretable",
        prohibited=frozenset({"reveal parent-task answer", "invent durable N1 misconception identity"}),
    ),
    "IT-N2-01": _it(
        intervention_id="IT-N2-01", target_kc=KCId.N2, barriers=frozenset({"BH-N2-01"}),
        neutral_support_allowed=True,
        action="compute two contrastive signed products",
        prompt="(-a)*(+b), then (-a)*(-b)",
        truth="deterministic signed multiplication",
        success="both products correct", failure="either product incorrect",
        prohibited=frozenset({"reveal parent answer", "mnemonic-only completion"}),
    ),
    "IT-N3-01": _it(
        intervention_id="IT-N3-01", target_kc=KCId.N3, barriers=frozenset({"BH-N3-01"}),
        action="evaluate unary negation grouping", prompt="-(-a)",
        truth="-(-a)=a", success="returns +a", failure="preserves negative or uninterpretable",
        prohibited=frozenset({"treat ordinary subtraction as unary negation"}),
    ),
    "IT-E1-01": _it(
        intervention_id="IT-E1-01", target_kc=KCId.E1, barriers=frozenset({"BH-E1-01"}),
        neutral_support_allowed=True,
        action="fill missing distributed product", prompt="a(x+b)=ax+a*__",
        truth="outside factor applies to both additive terms",
        success="missing term structurally correct", failure="factor omitted from second term",
        prohibited=frozenset({"prefill both distributed terms"}),
    ),
    "IT-E1-02": _it(
        intervention_id="IT-E1-02", target_kc=KCId.E1, barriers=frozenset({"BH-E1-02"}),
        action="compute distributed products separately", prompt="-a(x-b): [-a*x, -a*(-b)]",
        truth="distribution plus signed multiplication",
        success="both product signs/magnitudes correct", failure="sign composition remains wrong",
        failure_next="GUARDED_REPAIR_EDGE_OR_STOP",
        prohibited=frozenset({"claim BH-E1-02 when N2/N3 alternatives remain"}),
    ),
    "IT-E2-01": _it(
        intervention_id="IT-E2-01", target_kc=KCId.E2, barriers=frozenset({"BH-E2-01"}),
        action="group terms by variable structure", prompt="[ax,b,cx,d]",
        truth="only identical variable/power structures combine",
        success="x terms and constants grouped correctly", failure="unlike terms grouped",
        prohibited=frozenset({"supply final combined expression"}),
    ),
    "IT-Q0-01": _it(
        intervention_id="IT-Q0-01", target_kc=KCId.Q0, barriers=frozenset({"BH-Q0-01"}),
        action="apply same additive operation to both equality sides", prompt="x+a=r; subtract a on both sides",
        truth="L=R implies L+k=R+k", success="same additive operation on both sides",
        failure="one-sided or arbitrary sign change", failure_next="CLEAN_STOP_OR_FALLBACK",
        prohibited=frozenset({"variables-on-both-sides lesson", "multiplicative equation lesson"}),
    ),
    "IT-Q1-01": _it(
        intervention_id="IT-Q1-01", target_kc=KCId.Q1, barriers=frozenset({"BH-Q1-01"}),
        action="solve one factor equation", prompt="x+a=0 or x-a=0",
        truth="TI-02 solution-set preservation", success="correct signed assignment",
        failure="wrong root sign or unsupported response", failure_next="GUARDED_REPAIR_EDGE_OR_STOP",
        prohibited=frozenset({"general equation-solving lesson"}),
    ),
    "IT-F1-01": _it(
        intervention_id="IT-F1-01", target_kc=KCId.F1, barriers=frozenset({"BH-F1-01"}),
        action="produce four multiplicative contributions", prompt="x*x, x*n, m*x, m*n",
        truth="TI-01 expression equivalence", success="all four contributions correct",
        failure="cross term omitted/malformed", failure_next="GUARDED_REPAIR_EDGE_OR_STOP",
        prohibited=frozenset({"supply final expanded trinomial"}),
    ),
    "IT-F2-01": _it(
        intervention_id="IT-F2-01", target_kc=KCId.F2, barriers=frozenset({"BH-F2-01"}),
        action="check pair against sum and product", prompt="pair | sum | product",
        truth="m+n=b and mn=c", success="both constraints satisfied",
        failure="one/no constraint satisfied", failure_next="GUARDED_REPAIR_EDGE_OR_STOP",
        prohibited=frozenset({"supply correct pair before learner choice"}),
    ),
    "IT-Z1-01": _it(
        intervention_id="IT-Z1-01", target_kc=KCId.Z1, barriers=frozenset({"BH-Z1-01"}),
        action="distinguish zero sum from zero product", prompt="compare A+B=0 and A*B=0",
        truth="zero-product property", success="identifies product relation",
        failure="applies branch rule to sum", failure_next="CLEAN_STOP_OR_FALLBACK",
        prohibited=frozenset({"teach unrelated factoring strategy"}),
    ),
    "IT-QF1-01": _it(
        intervention_id="IT-QF1-01", target_task="CT-QF1",
        failures=frozenset({CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE}),
        action="fill unresolved branch/root slot",
        prompt="preserve completed branch; expose unresolved branch slot",
        truth="complete solution set for factored equation",
        success="missing branch/root resolved", failure="branch remains empty/invalid",
        success_next="RESUME_COMPOSITE_STAGE", failure_next="SAVE_OR_CLEAN_STOP",
        prohibited=frozenset({"auto-fill missing branch", "create durable barrier from one omission"}),
    ),
}

_EXTENDED_INTERVENTION_TEMPLATES: Dict[str, InterventionTemplate] = {
    "IT-L1-01": _it(
        intervention_id="IT-L1-01", target_kc=KCId.L1, barriers=frozenset({"BH-L1-01"}),
        action="distinguish coefficient division from subtraction",
        prompt="Since a multiplies x in ax=d, divide both sides by a to isolate x",
        truth="multiplicative inverse rule",
        success="divides both sides by coefficient",
        failure="continues subtracting coefficient",
        prohibited=frozenset({"reveal variable value"}),
    ),
    "IT-I1-01": _it(
        intervention_id="IT-I1-01", target_kc=KCId.I1, barriers=frozenset({"BH-I1-01"}),
        action="reverse inequality direction upon negative division",
        prompt="Dividing both sides of an inequality by a negative number inverts the order",
        truth="negative multiplication/division reverses inequality",
        success="inverts inequality direction",
        failure="preserves original inequality direction",
        prohibited=frozenset({"omit number line explanation"}),
    ),
    "IT-P1-01": _it(
        intervention_id="IT-P1-01", target_kc=KCId.P1, barriers=frozenset({"BH-P1-01"}),
        action="calculate vertex abscissa using minus b over 2a",
        prompt="The vertex abscissa of y = ax^2 + bx + c is r = -b / (2a)",
        truth="derivative zero condition or axis of symmetry",
        success="applies correct sign in vertex abscissa formula",
        failure="omits negative sign in vertex formula",
        prohibited=frozenset({"reveal vertex without calculation"}),
    ),
    "IT-PL1-01": _it(
        intervention_id="IT-PL1-01", target_kc=KCId.PL1, barriers=frozenset({"BH-PL1-01"}),
        action="evaluate polynomial at positive divisor root d",
        prompt="To find the remainder of P(x) divided by (x - d), substitute x = d into P(x)",
        truth="polynomial division algorithm P(x) = (x - d)Q(x) + R",
        success="substitutes correct sign root into polynomial",
        failure="inverts root sign during remainder evaluation",
        prohibited=frozenset({"compute long division without remainder theorem"}),
    ),
    "IT-TR1-01": _it(
        intervention_id="IT-TR1-01", target_kc=KCId.TR1, barriers=frozenset({"BH-TR1-01"}),
        action="find secondary symmetric root on unit circle",
        prompt="On the unit circle, sin(x) represents the vertical coordinate. The secondary root in [0, 360) is 180 - principal angle.",
        truth="sin(180 - theta) = sin(theta)",
        success="identifies second quadrant symmetric angle correctly",
        failure="omits secondary root or confuses quadrants",
        prohibited=frozenset({"give answer without unit circle symmetry"}),
    ),
    "IT-LG1-01": _it(
        intervention_id="IT-LG1-01", target_kc=KCId.LG1, barriers=frozenset({"BH-LG1-01"}),
        action="convert logarithmic statement to power form",
        prompt="log_b(y) = k means b^k = y. The base b is raised to the power k, not multiplied by k.",
        truth="exponential definition of logarithm",
        success="computes b^k correctly without multiplication trap",
        failure="multiplies base by exponent",
        prohibited=frozenset({"compute logarithm without exponential equivalence"}),
    ),
    "IT-LM1-01": _it(
        intervention_id="IT-LM1-01", target_kc=KCId.LM1, barriers=frozenset({"BH-LM1-01"}),
        action="recognize 0/0 indeterminate form and cancel common factor",
        prompt="When direct substitution yields 0/0, factor the numerator as (x-a)(x+a) and cancel the common (x-a) term.",
        truth="algebraic limit evaluation by factoring",
        success="cancels common root factor correctly",
        failure="claims limit is undefined without factoring",
        prohibited=frozenset({"reveal limit without cancellation"}),
    ),
    "IT-DV1-01": _it(
        intervention_id="IT-DV1-01", target_kc=KCId.DV1, barriers=frozenset({"BH-DV1-01"}),
        action="apply power rule d/dx(x^n) = n*x^(n-1)",
        prompt="Bring the power n to the front as a multiplier, then reduce the power by 1: d/dx(x^n) = n*x^(n-1).",
        truth="derivative power rule",
        success="multiplies by exponent and reduces power by 1",
        failure="omits multiplier or fails to decrement power",
        prohibited=frozenset({"reveal derivative without power rule"}),
    ),
    "IT-IN1-01": _it(
        intervention_id="IT-IN1-01", target_kc=KCId.IN1, barriers=frozenset({"BH-IN1-01"}),
        action="apply integration power rule int(x^n dx) = x^(n+1)/(n+1) + C",
        prompt="Increase the power by 1 and divide by the new power: int(x^n dx) = x^(n+1)/(n+1) + C.",
        truth="integration power rule",
        success="increases exponent by 1 and divides by new power",
        failure="fails to divide by new power or applies derivative power rule",
        prohibited=frozenset({"reveal integral without power rule"}),
    ),
}

INTERVENTION_TEMPLATES = VersionedRegistry(_CORE_INTERVENTION_TEMPLATES, _EXTENDED_INTERVENTION_TEMPLATES)


ACTIVE_DIAGNOSTIC_ROUTES: Dict[str, ActiveKCDiagnosticRoute] = {
    "DR-N1-01": ActiveKCDiagnosticRoute(
        route_id="DR-N1-01", active_kc=KCId.N1,
        eligible_observations=frozenset({"EO-SIGNED-SUM-WRONG"}),
        probe_id="PR-N1-01", intervention_id="IT-N1-01",
    ),
    "DR-N2-01": ActiveKCDiagnosticRoute(
        route_id="DR-N2-01", active_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        probe_id="PR-N2-01", intervention_id="IT-N2-01", barrier_id="BH-N2-01",
    ),
    "DR-N3-01": ActiveKCDiagnosticRoute(
        route_id="DR-N3-01", active_kc=KCId.N3,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        probe_id="PR-N3-01", intervention_id="IT-N3-01", barrier_id="BH-N3-01",
    ),
    "DR-E1-01": ActiveKCDiagnosticRoute(
        route_id="DR-E1-01", active_kc=KCId.E1,
        eligible_observations=frozenset({"EO-PARTIAL-DISTRIBUTION"}),
        probe_id="PR-E1-01", intervention_id="IT-E1-01", barrier_id="BH-E1-01",
    ),
    "DR-E1-02": ActiveKCDiagnosticRoute(
        route_id="DR-E1-02", active_kc=KCId.E1,
        eligible_observations=frozenset({"EO-DISTRIBUTION-SIGN-COMPOSITION-WRONG"}),
        probe_id="PR-E1-02", intervention_id="IT-E1-02", barrier_id="BH-E1-02",
    ),
    "DR-E2-01": ActiveKCDiagnosticRoute(
        route_id="DR-E2-01", active_kc=KCId.E2,
        eligible_observations=frozenset({"EO-UNLIKE-TERMS-COMBINED"}),
        probe_id="PR-E2-01", intervention_id="IT-E2-01", barrier_id="BH-E2-01",
    ),
    "DR-Q0-01": ActiveKCDiagnosticRoute(
        route_id="DR-Q0-01", active_kc=KCId.Q0,
        eligible_observations=frozenset({"EO-EQUALITY-ONE-SIDE-CHANGED"}),
        probe_id="PR-Q0-01", intervention_id="IT-Q0-01", barrier_id="BH-Q0-01",
    ),
    "DR-Q1-01": ActiveKCDiagnosticRoute(
        route_id="DR-Q1-01", active_kc=KCId.Q1,
        eligible_observations=frozenset({"EO-SIMPLE-ROOT-SIGN-WRONG"}),
        probe_id="PR-Q1-01", intervention_id="IT-Q1-01", barrier_id="BH-Q1-01",
    ),
    "DR-F1-01": ActiveKCDiagnosticRoute(
        route_id="DR-F1-01", active_kc=KCId.F1,
        eligible_observations=frozenset({"EO-BINOMIAL-CROSS-TERM-OMITTED"}),
        probe_id="PR-F1-01", intervention_id="IT-F1-01", barrier_id="BH-F1-01",
    ),
    "DR-F2-01": ActiveKCDiagnosticRoute(
        route_id="DR-F2-01", active_kc=KCId.F2,
        eligible_observations=frozenset({
            "EO-FACTOR-PAIR-SUM-MISMATCH",
            "EO-FACTOR-PAIR-PRODUCT-MISMATCH",
        }),
        probe_id="PR-F2-01", intervention_id="IT-F2-01", barrier_id="BH-F2-01",
    ),
    "DR-Z1-01": ActiveKCDiagnosticRoute(
        route_id="DR-Z1-01", active_kc=KCId.Z1,
        eligible_observations=frozenset({"EO-ZERO-PRODUCT-MISAPPLIED"}),
        probe_id="PR-Z1-01", intervention_id="IT-Z1-01", barrier_id="BH-Z1-01",
    ),
    "DR-L1-01": ActiveKCDiagnosticRoute(
        route_id="DR-L1-01", active_kc=KCId.L1,
        eligible_observations=frozenset({"EO-COEFFICIENT-SUBTRACTED"}),
        probe_id="PR-L1-01", intervention_id="IT-L1-01", barrier_id="BH-L1-01",
    ),
    "DR-I1-01": ActiveKCDiagnosticRoute(
        route_id="DR-I1-01", active_kc=KCId.I1,
        eligible_observations=frozenset({"EO-INEQUALITY-DIRECTION-NOT-REVERSED"}),
        probe_id="PR-I1-01", intervention_id="IT-I1-01", barrier_id="BH-I1-01",
    ),
    "DR-P1-01": ActiveKCDiagnosticRoute(
        route_id="DR-P1-01", active_kc=KCId.P1,
        eligible_observations=frozenset({
            "EO-VERTEX-FORMULA-SIGN-INVERTED",
            "EO-VERTEX-ORDINATE-CONFUSED-WITH-CONSTANT",
        }),
        probe_id="PR-P1-01", intervention_id="IT-P1-01", barrier_id="BH-P1-01",
    ),
    "DR-PL1-01": ActiveKCDiagnosticRoute(
        route_id="DR-PL1-01", active_kc=KCId.PL1,
        eligible_observations=frozenset({
            "EO-DIVISOR-ROOT-SIGN-INVERTED",
            "EO-REMAINDER-CONFUSED-WITH-COEFF-SUM",
        }),
        probe_id="PR-PL1-01", intervention_id="IT-PL1-01", barrier_id="BH-PL1-01",
    ),
    "DR-TR1-01": ActiveKCDiagnosticRoute(
        route_id="DR-TR1-01", active_kc=KCId.TR1,
        eligible_observations=frozenset({
            "EO-TRIG-SECONDARY-ROOT-OMITTED",
            "EO-TRIG-AXIS-CONFUSED",
            "EO-TRIG-COEFF-ABSORBED-INTO-ARG",
        }),
        probe_id="PR-TR1-01", intervention_id="IT-TR1-01", barrier_id="BH-TR1-01",
    ),
    "DR-LG1-01": ActiveKCDiagnosticRoute(
        route_id="DR-LG1-01", active_kc=KCId.LG1,
        eligible_observations=frozenset({
            "EO-LOG-DOMAIN-CONSTRAINT-VIOLATED",
            "EO-LOG-ADDITION-DISTRIBUTED",
            "EO-LOG-EXPONENT-CALCULATION-WRONG",
        }),
        probe_id="PR-LG1-01", intervention_id="IT-LG1-01", barrier_id="BH-LG1-01",
    ),
    "DR-LM1-01": ActiveKCDiagnosticRoute(
        route_id="DR-LM1-01", active_kc=KCId.LM1,
        eligible_observations=frozenset({
            "EO-CALC-LIMIT-FORM-WRONG",
            "EO-CALC-SIMPLIFICATION-WRONG",
            "EO-CALC-LIMIT-VALUE-WRONG",
        }),
        probe_id="PR-LM1-01", intervention_id="IT-LM1-01", barrier_id="BH-LM1-01",
    ),
    "DR-DV1-01": ActiveKCDiagnosticRoute(
        route_id="DR-DV1-01", active_kc=KCId.DV1,
        eligible_observations=frozenset({
            "EO-CALC-DERIVATIVE-POWER-WRONG",
            "EO-CALC-SLOPE-WRONG",
            "EO-CALC-TANGENT-WRONG",
        }),
        probe_id="PR-DV1-01", intervention_id="IT-DV1-01", barrier_id="BH-DV1-01",
    ),
    "DR-IN1-01": ActiveKCDiagnosticRoute(
        route_id="DR-IN1-01", active_kc=KCId.IN1,
        eligible_observations=frozenset({
            "EO-CALC-INTEGRAL-ANTIDERIV-WRONG",
            "EO-CALC-INTEGRAL-LIMITS-WRONG",
            "EO-CALC-INTEGRAL-VALUE-WRONG",
        }),
        probe_id="PR-IN1-01", intervention_id="IT-IN1-01", barrier_id="BH-IN1-01",
    ),
}


REPAIR_EDGES: Dict[str, RepairEdge] = {
    "RE-E1-N2": RepairEdge(
        edge_id="RE-E1-N2", from_kc=KCId.E1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-DISTRIBUTION-SIGN-COMPOSITION-WRONG", "EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence OR strong recent KC-N2 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
            allowed_target_kc_states=TARGET_GAP_STATES,
            state_support_required_flags=frozenset({"FRESH_TARGET_GAP_EVIDENCE"}),
            disqualifying_flags=frozenset({"RECENT_KC_N2_TRANSFER_SUCCESS"}),
        ),
        preferred_probe_id="PR-N2-01",
        disqualifying_evidence=frozenset({"RECENT_KC_N2_TRANSFER_SUCCESS"}),
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="NEUTRAL_SUPPORT_KC_E1",
    ),
    "RE-E1-N3": RepairEdge(
        edge_id="RE-E1-N3", from_kc=KCId.E1, to_kc=KCId.N3,
        eligible_observations=frozenset({"EO-DISTRIBUTION-SIGN-COMPOSITION-WRONG"}),
        required_evidence="PR-N3-01 supports N3 AND N2 insufficient",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N3-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
            required_flags=frozenset({"N2_ALTERNATIVE_INSUFFICIENT"}),
        ),
        preferred_probe_id="PR-N3-01",
        entry_intervention_ids=frozenset({"IT-N3-01"}),
        fallback_action="NEUTRAL_SUPPORT_KC_E1",
    ),
    "RE-F1-E1": RepairEdge(
        edge_id="RE-F1-E1", from_kc=KCId.F1, to_kc=KCId.E1,
        eligible_observations=frozenset({"EO-BINOMIAL-CROSS-TERM-OMITTED"}),
        required_evidence="PR-E1-01 or observed distribution evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-E1-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
            allowed_target_kc_states=TARGET_GAP_STATES,
            state_support_required_flags=frozenset({"FRESH_TARGET_GAP_EVIDENCE"}),
        ),
        preferred_probe_id="PR-E1-01",
        entry_intervention_ids=frozenset({"IT-E1-01"}),
        fallback_action="IT-F1-01",
    ),
    "RE-F1-E2": RepairEdge(
        edge_id="RE-F1-E2", from_kc=KCId.F1, to_kc=KCId.E2,
        eligible_observations=frozenset({"EO-UNLIKE-TERMS-COMBINED"}),
        required_evidence="PR-E2-01 supports KC-E2 gap",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-E2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-E2-01",
        entry_intervention_ids=frozenset({"IT-E2-01"}),
        fallback_action="IT-F1-01",
    ),
    "RE-F1-N1": RepairEdge(
        edge_id="RE-F1-N1", from_kc=KCId.F1, to_kc=KCId.N1,
        eligible_observations=frozenset({"EO-SIGNED-SUM-WRONG"}),
        required_evidence="PR-N1-01 gap evidence OR strong recent KC-N1 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N1-01": frozenset({ProbeEvidenceKind.GAP})},
            allowed_target_kc_states=TARGET_GAP_STATES,
            state_support_required_flags=frozenset({"FRESH_TARGET_GAP_EVIDENCE"}),
            disqualifying_flags=frozenset({"RECENT_KC_N1_TRANSFER_SUCCESS"}),
        ),
        preferred_probe_id="PR-N1-01",
        disqualifying_evidence=frozenset({"RECENT_KC_N1_TRANSFER_SUCCESS"}),
        entry_intervention_ids=frozenset({"IT-N1-01"}),
        fallback_action="NEUTRAL_SUPPORT_KC_F1",
    ),
    "RE-F1-N2": RepairEdge(
        edge_id="RE-F1-N2", from_kc=KCId.F1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="NEUTRAL_SUPPORT_KC_F1",
    ),
    "RE-F2-N1": RepairEdge(
        edge_id="RE-F2-N1", from_kc=KCId.F2, to_kc=KCId.N1,
        eligible_observations=frozenset({"EO-FACTOR-PAIR-SUM-MISMATCH"}),
        required_evidence="PR-N1-01 gap evidence OR strong recent KC-N1 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N1-01": frozenset({ProbeEvidenceKind.GAP})},
            allowed_target_kc_states=TARGET_GAP_STATES,
            state_support_required_flags=frozenset({"FRESH_TARGET_GAP_EVIDENCE"}),
            disqualifying_flags=frozenset({"RECENT_KC_N1_TRANSFER_SUCCESS"}),
        ),
        preferred_probe_id="PR-N1-01",
        disqualifying_evidence=frozenset({"RECENT_KC_N1_TRANSFER_SUCCESS"}),
        entry_intervention_ids=frozenset({"IT-N1-01"}),
        fallback_action="IT-F2-01",
    ),
    "RE-F2-N2": RepairEdge(
        edge_id="RE-F2-N2", from_kc=KCId.F2, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-FACTOR-PAIR-PRODUCT-MISMATCH"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-F2-01",
    ),
    "RE-F2-F1": RepairEdge(
        edge_id="RE-F2-F1", from_kc=KCId.F2, to_kc=KCId.F1,
        eligible_observations=frozenset({"EO-FACTOR-EXPANSION-MISMATCH"}),
        required_evidence="PR-F1-01 supports structure gap",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-F1-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-F1-01",
        entry_intervention_ids=frozenset({"IT-F1-01"}),
        fallback_action="IT-F2-01",
    ),
    "RE-Q1-Q0": RepairEdge(
        edge_id="RE-Q1-Q0", from_kc=KCId.Q1, to_kc=KCId.Q0,
        eligible_observations=frozenset({"EO-EQUALITY-ONE-SIDE-CHANGED"}),
        required_evidence="PR-Q0-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-Q0-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-Q0-01",
        entry_intervention_ids=frozenset({"IT-Q0-01"}),
        fallback_action="IT-Q1-01",
    ),
    "RE-Q1-N3": RepairEdge(
        edge_id="RE-Q1-N3", from_kc=KCId.Q1, to_kc=KCId.N3,
        eligible_observations=frozenset({"EO-SIMPLE-ROOT-SIGN-WRONG"}),
        required_evidence="PR-Q0-01 passes AND PR-N3-01 supports N3",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N3-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
            required_flags=frozenset({"Q0_PASSED"}),
        ),
        preferred_probe_id="PR-N3-01",
        entry_intervention_ids=frozenset({"IT-N3-01"}),
        fallback_action="IT-Q1-01",
    ),
    "RE-Q1-N1": RepairEdge(
        edge_id="RE-Q1-N1", from_kc=KCId.Q1, to_kc=KCId.N1,
        eligible_observations=frozenset({"EO-SIGNED-SUM-WRONG"}),
        required_evidence="PR-N1-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N1-01": frozenset({ProbeEvidenceKind.GAP})},
        ),
        preferred_probe_id="PR-N1-01",
        entry_intervention_ids=frozenset({"IT-N1-01"}),
        fallback_action="IT-Q1-01",
    ),
    "RE-L1-Q0": RepairEdge(
        edge_id="RE-L1-Q0", from_kc=KCId.L1, to_kc=KCId.Q0,
        eligible_observations=frozenset({"EO-EQUALITY-ONE-SIDE-CHANGED"}),
        required_evidence="PR-Q0-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-Q0-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-Q0-01",
        entry_intervention_ids=frozenset({"IT-Q0-01"}),
        fallback_action="IT-L1-01",
    ),
    "RE-L1-N2": RepairEdge(
        edge_id="RE-L1-N2", from_kc=KCId.L1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-L1-01",
    ),
    "RE-P1-N2": RepairEdge(
        edge_id="RE-P1-N2", from_kc=KCId.P1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-P1-01",
    ),
    "RE-PL1-N2": RepairEdge(
        edge_id="RE-PL1-N2", from_kc=KCId.PL1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-PL1-01",
    ),
    "RE-TR1-N2": RepairEdge(
        edge_id="RE-TR1-N2", from_kc=KCId.TR1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-TR1-01",
    ),
    "RE-LG1-N2": RepairEdge(
        edge_id="RE-LG1-N2", from_kc=KCId.LG1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-LG1-01",
    ),
    "RE-LM1-N2": RepairEdge(
        edge_id="RE-LM1-N2", from_kc=KCId.LM1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-LM1-01",
    ),
    "RE-DV1-N2": RepairEdge(
        edge_id="RE-DV1-N2", from_kc=KCId.DV1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-DV1-01",
    ),
    "RE-IN1-N2": RepairEdge(
        edge_id="RE-IN1-N2", from_kc=KCId.IN1, to_kc=KCId.N2,
        eligible_observations=frozenset({"EO-SIGN-WRONG"}),
        required_evidence="PR-N2-01 gap evidence",
        evidence_policy=RepairEvidencePolicy(
            accepted_probe_evidence={"PR-N2-01": frozenset({ProbeEvidenceKind.BARRIER_SUPPORT})},
        ),
        preferred_probe_id="PR-N2-01",
        entry_intervention_ids=frozenset({"IT-N2-01"}),
        fallback_action="IT-IN1-01",
    ),
}


def validate_focus_registry() -> None:
    """Fail fast if executable Focus authority drifts from frozen v0.4 + erratum."""

    assert len(PROBE_TEMPLATES) == 11, "v0.4 requires exactly 11 primary probes"
    assert len(INTERVENTION_TEMPLATES) == 12, "v0.4.1 erratum requires exactly 12 interventions"

    known_observations = {code.value for code in ErrorObservationCode}

    for route in ACTIVE_DIAGNOSTIC_ROUTES.values():
        assert route.eligible_observations.issubset(known_observations), (
            f"{route.route_id} references unknown ErrorObservation code"
        )
        assert route.probe_id in PROBE_TEMPLATES, (
            f"{route.route_id} references missing probe {route.probe_id}"
        )
        assert route.intervention_id in INTERVENTION_TEMPLATES, (
            f"{route.route_id} references missing intervention {route.intervention_id}"
        )
        assert PROBE_TEMPLATES[route.probe_id].target_kc == route.active_kc, (
            f"{route.route_id} probe target does not match active KC"
        )
        assert INTERVENTION_TEMPLATES[route.intervention_id].target_kc == route.active_kc, (
            f"{route.route_id} intervention target does not match active KC"
        )
        if route.barrier_id:
            assert route.barrier_id in PROBE_TEMPLATES[route.probe_id].candidate_barriers, (
                f"{route.route_id} barrier missing from probe candidates"
            )
            assert route.barrier_id in INTERVENTION_TEMPLATES[route.intervention_id].eligible_barriers, (
                f"{route.route_id} barrier missing from intervention authority"
            )

    for edge in REPAIR_EDGES.values():
        assert edge.eligible_observations.issubset(known_observations), (
            f"{edge.edge_id} references unknown ErrorObservation code"
        )
        assert edge.entry_intervention_ids, (
            f"{edge.edge_id} has no executable intervention target"
        )
        if edge.disqualifying_evidence:
            assert edge.disqualifying_evidence == edge.evidence_policy.disqualifying_flags, (
                f"{edge.edge_id} human/machine disqualifying evidence drifted"
            )
        if edge.preferred_probe_id:
            assert edge.preferred_probe_id in PROBE_TEMPLATES, (
                f"{edge.edge_id} references missing probe {edge.preferred_probe_id}"
            )
        for probe_id in edge.evidence_policy.accepted_probe_evidence:
            assert probe_id in PROBE_TEMPLATES, (
                f"{edge.edge_id} evidence policy references missing probe {probe_id}"
            )
        for intervention_id in edge.entry_intervention_ids:
            assert intervention_id in INTERVENTION_TEMPLATES, (
                f"{edge.edge_id} references missing intervention {intervention_id}"
            )

    # Freeze-review blocker B2: every N1 route must use PR-N1-01.
    n1_edges = [edge for edge in REPAIR_EDGES.values() if edge.to_kc == KCId.N1]
    assert n1_edges, "Expected active N1 RepairEdges"
    assert all(edge.preferred_probe_id == "PR-N1-01" for edge in n1_edges)


validate_focus_registry()
