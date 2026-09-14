import pytest
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError


@pytest.fixture
def cas():
    return SymbolicEquivalenceEngine()


def test_symbolic_equivalence_valid_steps(cas):
    # Denklem: x^2 + 6x - 2 = 0
    target = "x**2 + 6*x - 2 = 0"

    # Adım 1: x^2 + 6x = 2
    step1 = "x**2 + 6*x = 2"
    is_equiv, latency_ms, diff = cas.verify_equivalence(step1, target)
    assert is_equiv is True
    assert latency_ms < 120.0

    # Adım 2: x^2 + 6x + 9 = 11
    step2 = "x**2 + 6*x + 9 = 11"
    is_equiv, latency_ms, diff = cas.verify_equivalence(step2, target)
    assert is_equiv is True

    # Adım 3: (x + 3)^2 = 11
    step3 = "(x + 3)**2 = 11"
    is_equiv, latency_ms, diff = cas.verify_equivalence(step3, target)
    assert is_equiv is True


def test_symbolic_factoring_equivalence(cas):
    target = "x**2 - 5*x + 6 = 0"
    step = "(x - 2)*(x - 3) = 0"
    is_equiv, latency_ms, diff = cas.verify_equivalence(step, target)
    assert is_equiv is True


def test_symbolic_invalid_equivalence(cas):
    target = "x**2 + 6*x - 2 = 0"
    wrong_step = "x**2 + 6*x = 9"
    is_equiv, latency_ms, diff = cas.verify_equivalence(wrong_step, target)
    assert is_equiv is False


def test_security_ast_injection_prevention(cas):
    # Python zararlı kod enjeksiyonu denemesi
    malicious_inputs = [
        "__import__('os').system('dir')",
        "eval('1 + 1')",
        "open('secret.txt', 'r')",
        "x + [i for i in range(10)]",
    ]

    for malicious in malicious_inputs:
        with pytest.raises((SecurityViolationError, ValueError)):
            cas.parse_to_sympy(malicious)


def test_security_max_ast_depth(cas):
    # 20 seviye iç içe ikili işlem (MAX_AST_DEPTH = 15)
    deep_expr = " + ".join(["x"] * 20)
    with pytest.raises(SecurityViolationError):
        cas.sanitize_and_validate_ast(deep_expr)

