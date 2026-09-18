from app.focus_domain.attempt_language import (
    NormalizationStatus,
    SupportedAttemptNormalizer,
)
from app.focus_domain.models import AttemptJudgment, CompositeTaskFailureCode, StageId
from app.focus_domain.stage_judgment import CTQF1StageJudgmentService


normalizer = SupportedAttemptNormalizer()
service = CTQF1StageJudgmentService()


def test_solution_set_normalizes_order_and_spelling():
    a = normalizer.normalize_solution_set("{x=-3, x=2}")
    b = normalizer.normalize_solution_set("x=2 veya x=-3")
    assert a.status == NormalizationStatus.SUPPORTED
    assert b.status == NormalizationStatus.SUPPORTED
    assert a.solution_set.values == (-3, 2)
    assert a.solution_set == b.solution_set


def test_solution_set_rejects_zero_root_as_unsupported_domain():
    result = normalizer.normalize_solution_set("x=0, x=2")
    assert result.status == NormalizationStatus.UNSUPPORTED_DOMAIN
    assert result.as_attempt_judgment_if_not_supported() == AttemptJudgment.UNSUPPORTED_DOMAIN


def test_fraction_input_is_domain_boundary_not_math_error():
    result = normalizer.normalize_assignment("x=1/2")
    assert result.status == NormalizationStatus.UNSUPPORTED_DOMAIN
    assert result.as_attempt_judgment_if_not_supported() == AttemptJudgment.UNSUPPORTED_DOMAIN


def test_factor_pair_is_order_insensitive():
    result = normalizer.normalize_factor_pair("-3,2")
    assert result.status == NormalizationStatus.SUPPORTED
    assert result.factor_pair == (-3, 2)


def test_s1_correct_pair_is_valid_expected():
    attempt = normalizer.normalize_factor_pair("-3,2")
    result = service.judge_factor_pair(attempt, expected_pair=(2, -3))
    assert result.judgment == AttemptJudgment.VALID_EXPECTED


def test_s1_wrong_supported_pair_is_invalid_math():
    attempt = normalizer.normalize_factor_pair("-6,1")
    result = service.judge_factor_pair(attempt, expected_pair=(2, -3))
    assert result.judgment == AttemptJudgment.INVALID_MATHEMATICS


def test_s2_one_correct_branch_is_valid_incomplete():
    attempt = normalizer.normalize_branch_decomposition("x-2=0")
    result = service.judge_branch_decomposition(
        attempt,
        expected_branch_equations=frozenset({"x-2=0", "x+3=0"}),
    )
    assert result.judgment == AttemptJudgment.VALID_INCOMPLETE
    assert result.composite_failure == CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE
    assert result.observed_correct_items == frozenset({"x-2=0"})


def test_s2_two_correct_branches_are_valid_expected():
    attempt = normalizer.normalize_branch_decomposition("x+3=0 or x-2=0")
    result = service.judge_branch_decomposition(
        attempt,
        expected_branch_equations=frozenset({"x-2=0", "x+3=0"}),
    )
    assert result.judgment == AttemptJudgment.VALID_EXPECTED


def test_s2_correct_plus_wrong_branch_is_invalid_math_but_preserves_correct_observation():
    attempt = normalizer.normalize_branch_decomposition("x-2=0 or x+4=0")
    result = service.judge_branch_decomposition(
        attempt,
        expected_branch_equations=frozenset({"x-2=0", "x+3=0"}),
    )
    assert result.judgment == AttemptJudgment.INVALID_MATHEMATICS
    assert result.observed_correct_items == frozenset({"x-2=0"})


def test_s4_partial_solution_set_is_valid_incomplete():
    attempt = normalizer.normalize_solution_set("x=-3")
    result = service.judge_solution_set(
        attempt,
        expected_roots=frozenset({-3, 2}),
    )
    assert result.judgment == AttemptJudgment.VALID_INCOMPLETE


def test_s4_complete_solution_set_is_valid_expected():
    attempt = normalizer.normalize_solution_set("x=2, x=-3")
    result = service.judge_solution_set(
        attempt,
        expected_roots=frozenset({-3, 2}),
    )
    assert result.judgment == AttemptJudgment.VALID_EXPECTED
    assert result.bypassed_stage_evidence is False


def test_complete_solution_set_during_s1_is_valid_shortcut():
    attempt = normalizer.normalize_solution_set("x=2, x=-3")
    result = service.judge_solution_set(
        attempt,
        expected_roots=frozenset({-3, 2}),
        current_stage=StageId.S1_FACTOR,
    )
    assert result.judgment == AttemptJudgment.VALID_SHORTCUT
    assert result.bypassed_stage_evidence is True


def test_unsupported_form_never_becomes_invalid_math():
    attempt = normalizer.normalize_branch_decomposition("x^2+x-6=0")
    result = service.judge_branch_decomposition(
        attempt,
        expected_branch_equations=frozenset({"x-2=0", "x+3=0"}),
    )
    assert result.judgment == AttemptJudgment.UNSUPPORTED_STEP_FORM


def test_structured_float_factor_pair_is_not_silently_truncated():
    attempt = normalizer.normalize_factor_pair([2.5, -3])
    assert attempt.status == NormalizationStatus.UNSUPPORTED_STEP_FORM


def test_s3_service_preserves_valid_incomplete_semantics():
    from app.focus_domain.models import BranchAssignmentStatus, BranchWorkItem, BranchWorkSet

    work = BranchWorkSet(
        branch_items=[
            BranchWorkItem(
                branch_id="A",
                source_factor="x-2",
                expected_equation="x-2=0",
                expected_assignment="x=2",
                assignment_status=BranchAssignmentStatus.VALID,
            ),
            BranchWorkItem(
                branch_id="B",
                source_factor="x+3",
                expected_equation="x+3=0",
                expected_assignment="x=-3",
                assignment_status=BranchAssignmentStatus.PENDING,
            ),
        ]
    )
    result = service.judge_branch_work_set(work)
    assert result.judgment == AttemptJudgment.VALID_INCOMPLETE
    assert result.composite_failure == CompositeTaskFailureCode.ROOT_BRANCH_INCOMPLETE
    assert result.observed_correct_items == frozenset({"x=2"})
