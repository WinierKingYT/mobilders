import pytest
from app.cas.preprocessor import ImplicitMultiplicationPreprocessor
from app.cas.symbolic_engine import SymbolicEquivalenceEngine


def test_implicit_multiplication_coefficients():
    # 2x -> 2*x, 15x -> 15*x
    raw = "2x + 15x = 17"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert processed == "2*x + 15*x = 17"


def test_implicit_multiplication_parentheses():
    # (x+1)(x-2) -> (x+1)*(x-2)
    raw = "(x + 1)(x - 2) = 0"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "(x + 1)*(x - 2) = 0" in processed


def test_implicit_multiplication_number_and_parenthesis():
    # 3(x+4) -> 3*(x+4)
    raw = "3(x + 4) = 12"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "3*(x + 4) = 12" in processed


def test_implicit_multiplication_variable_and_parenthesis():
    # x(x+6) -> x*(x+6)
    raw = "x(x + 6) = 2"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "x*(x + 6) = 2" in processed


def test_implicit_multiplication_compact_exponent():
    # x2 -> x**2, b2 -> b**2
    raw = "x2 + 6x - 2 = 0"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "x**2 + 6*x - 2 = 0" in processed


def test_cas_engine_handles_natural_mobile_input():
    cas = SymbolicEquivalenceEngine()

    # Öğrenci telefonda 'x2 + 6x = 2' yazsa bile 'x**2 + 6*x - 2 = 0' ile eşdeğer olmalı
    user_mobile_input = "x2 + 6x = 2"
    canonical_target = "x**2 + 6*x - 2 = 0"

    is_equiv, latency_ms, diff = cas.verify_equivalence(user_mobile_input, canonical_target)
    assert is_equiv is True
    assert latency_ms < 120.0


def test_cas_engine_handles_factored_parentheses_without_stars():
    cas = SymbolicEquivalenceEngine()

    user_mobile_input = "(x - 2)(x - 3) = 0"
    canonical_target = "x**2 - 5*x + 6 = 0"

    is_equiv, latency_ms, diff = cas.verify_equivalence(user_mobile_input, canonical_target)
    assert is_equiv is True


def test_implicit_multiplication_unicode_superscripts():
    # x² + 6x = 2 -> x**2 + 6*x = 2
    raw = "x² + 6x = 2"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "x**2 + 6*x = 2" in processed

    cas = SymbolicEquivalenceEngine()
    is_equiv, _, _ = cas.verify_equivalence("x² + 6x = 2", "x**2 + 6*x - 2 = 0")
    assert is_equiv is True

    # (x + 1)² = 4
    is_equiv, _, _ = cas.verify_equivalence("(x + 1)² = 4", "x**2 + 2*x - 3 = 0")
    assert is_equiv is True


def test_implicit_multiplication_unicode_operators():
    # Unicode minus: −, unicode times: ×, unicode div: ÷
    raw = "x² − 5x + 6 = 0"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "x**2 - 5*x + 6 = 0" in processed

    cas = SymbolicEquivalenceEngine()
    is_equiv, _, _ = cas.verify_equivalence("x² − 5x + 6 = 0", "x**2 - 5*x + 6 = 0")
    assert is_equiv is True

    is_equiv, _, _ = cas.verify_equivalence("2 × 3x = 18", "6*x = 18")
    assert is_equiv is True

    is_equiv, _, _ = cas.verify_equivalence("6 ÷ 2x = 3", "3*x = 3")
    assert is_equiv is True


def test_implicit_multiplication_decimal_comma():
    # 2,5x = 5 -> 2.5*x = 5
    raw = "2,5x = 5"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "2.5*x = 5" in processed

    cas = SymbolicEquivalenceEngine()
    is_equiv, _, _ = cas.verify_equivalence("2,5x = 5", "5*x/2 = 5")
    assert is_equiv is True


def test_implicit_multiplication_latex_fractions_and_roots():
    # \frac{2x + 6}{2} = 4 -> ((2*x + 6)/(2)) = 4
    raw = r"\frac{2x + 6}{2} = 4"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "((2*x + 6)/(2)) = 4" in processed

    cas = SymbolicEquivalenceEngine()
    is_equiv, _, _ = cas.verify_equivalence(r"\frac{2x + 6}{2} = 4", "x + 3 = 4")
    assert is_equiv is True

    # \sqrt{16} = 4
    is_equiv, _, _ = cas.verify_equivalence(r"\sqrt{16} = 4", "4 = 4")
    assert is_equiv is True

    # \left(x + 1\right)\left(x + 2\right) = 0
    is_equiv, _, _ = cas.verify_equivalence(r"\left(x + 1\right)\left(x + 2\right) = 0", "x**2 + 3*x + 2 = 0")
    assert is_equiv is True


def test_implicit_multiplication_fraction_variable_priority():
    # 1/2x should be parsed deterministically as ((1)/(2))*x, distinct from 1/(2*x)
    raw = "1/2x = 3"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "((1)/(2))*x" in processed

    cas = SymbolicEquivalenceEngine()
    is_equiv, _, _ = cas.verify_equivalence("1/2x = 3", "x/2 = 3")
    assert is_equiv is True

    # 1/(2x) is reciprocal
    is_equiv_recip, _, _ = cas.verify_equivalence("1/(2x) = 3", "1/(2*x) = 3")
    assert is_equiv_recip is True


def test_implicit_multiplication_multivariable_product():
    # ab -> a*b, 2ab -> 2*a*b, bc -> b*c
    raw = "2ab + bc = 10"
    processed = ImplicitMultiplicationPreprocessor.preprocess(raw)
    assert "2*a*b + b*c = 10" in processed

    cas = SymbolicEquivalenceEngine()
    is_equiv, _, _ = cas.verify_equivalence("2ab = 6", "2*a*b = 6")
    assert is_equiv is True


def test_implicit_multiplication_fraction_depth_limit():
    # Nested \frac beyond depth limit should not cause infinite loop or stack crash
    nested = r"\frac{1}{" * 25 + "2" + "}" * 25
    res = ImplicitMultiplicationPreprocessor.preprocess(nested)
    assert isinstance(res, str)
    assert r"\frac" not in res

