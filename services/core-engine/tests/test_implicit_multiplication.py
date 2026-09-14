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
