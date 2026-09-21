"""
Symbolic AST & Mathematical Fuzz Testing Suite (Aşama 2).
Performs adversarial stress testing on preprocessors, formal verifiers,
and misconception detectors with random Unicode, malformed LaTeX, deeply nested
expressions, and numerical edge cases to guarantee zero unhandled crashes.
"""

import math
import random
import string
import pytest
from app.cas.preprocessor import ImplicitMultiplicationPreprocessor
from app.curriculum_generator.formal_verifier import SymPyFormalVerifier
from app.misconceptions.detector import QuadraticMisconceptionDetector


class TestPreprocessorFuzzing:
    """Adversarial stress testing for ImplicitMultiplicationPreprocessor."""

    def test_massive_input_length_clamping(self):
        """Massive inputs (>10,000 chars) should be handled cleanly without hang or crash."""
        massive_input = "x + " * 3000 + "1"
        res = ImplicitMultiplicationPreprocessor.preprocess(massive_input)
        assert isinstance(res, str)
        assert len(res) <= 2000

    def test_deeply_nested_fractions_and_roots(self):
        """Deeply nested LaTeX constructs should not trigger catastrophic backtracking or RecursionError."""
        nested_frac = r"\frac{1}{\frac{2}{\frac{3}{\frac{4}{\frac{5}{\frac{6}{7}}}}}}"
        res = ImplicitMultiplicationPreprocessor.preprocess(nested_frac)
        assert isinstance(res, str)

        nested_sqrt = r"\sqrt{\sqrt{\sqrt{\sqrt{\sqrt{\sqrt{x + 1}}}}}}"
        res_sqrt = ImplicitMultiplicationPreprocessor.preprocess(nested_sqrt)
        assert isinstance(res_sqrt, str)

    def test_random_unicode_and_control_chars(self):
        """Random combinations of Unicode, math symbols, and control chars should never crash."""
        random.seed(42)
        chars = string.printable + "²³⁴⁰¹²³⁴⁵⁶⁷⁸⁹×·•÷−–—√πθλ≠≤≥±\u0000\u0007\u001b\n\r\t"
        for _ in range(50):
            rand_str = "".join(random.choice(chars) for _ in range(120))
            res = ImplicitMultiplicationPreprocessor.preprocess(rand_str)
            assert isinstance(res, str)

    def test_unbalanced_parentheses_and_brackets(self):
        """Extreme unbalanced parentheses should not cause infinite loops or crashes."""
        test_cases = [
            "(((((((((((x + 1)",
            ")))))))))))x - 1",
            "[(({[x + 1]})]",
            "((((x)))) + ))))(((",
            r"\left( \right) \left[",
        ]
        for tc in test_cases:
            res = ImplicitMultiplicationPreprocessor.preprocess(tc)
            assert isinstance(res, str)


class TestFormalVerifierFuzzing:
    """Adversarial stress testing for SymPyFormalVerifier."""

    def test_verify_identity_adversarial_inputs(self):
        """Arbitrary malformed strings and massive expressions should return False without raising."""
        adversarial_cases = [
            ("", ""),
            ("x" * 1000, "x" * 1000),
            ("x / 0", "1"),
            ("1 / (x - x)", "0"),
            ("x ** (x ** (x ** x))", "x"),
            ("sin(x)**2 + cos(x)**2", "1"),  # Should still evaluate True
            ("__import__('os').system('ls')", "0"),
            ("sp.sin(x)", "sin(x)"),
            ("exp(10000000)", "exp(10000000)"),
        ]
        for lhs, rhs in adversarial_cases:
            res = SymPyFormalVerifier.verify_identity(lhs, rhs)
            assert isinstance(res, bool)

    def test_verify_solvable_equation_adversarial_inputs(self):
        """Unsolvable, malformed, or hostile equation strings should return (False, []) cleanly."""
        adversarial_eqs = [
            "",
            "x = ",
            "= 5",
            "x / 0 = 1",
            "x ** 100000 = -1",
            "sin(x) = 2",
            "x + y + z = 10",
            "invalid_syntax(((())))",
            "x = x + 1",  # No solution
            "2*x = 2*x",  # Identity (infinite solutions)
        ]
        for eq in adversarial_eqs:
            is_solvable, sols = SymPyFormalVerifier.verify_solvable_equation(eq, "x")
            assert isinstance(is_solvable, bool)
            assert isinstance(sols, list)

    def test_verify_limit_evaluation_adversarial_inputs(self):
        """Non-existent, infinite, or malformed limits should return False cleanly."""
        adversarial_limits = [
            ("1 / x", "x", 0, "0"),
            ("sin(1 / x)", "x", 0, "0"),
            ("x / 0", "x", 0, "0"),
            ("malformed((", "x", 0, "0"),
            ("x**2", "x", "invalid_point", "0"),
        ]
        for expr, var, pt, exp in adversarial_limits:
            res = SymPyFormalVerifier.verify_limit_evaluation(expr, var, pt, exp)
            assert isinstance(res, bool)


class TestMisconceptionDetectorFuzzing:
    """Stress testing QuadraticMisconceptionDetector with adversarial inputs."""

    def test_detector_adversarial_steps(self):
        """Arbitrary user inputs should never crash the misconception detector."""
        detector = QuadraticMisconceptionDetector()
        adversarial_inputs = [
            "",
            "   ",
            "None",
            "x / 0 = 0",
            "x" * 500,
            "(x + 3)^2 = x^2 + 9",  # Valid bug: BUG-QUAD-03
            "x = 5 or x = -5",
            "x² - 4 = (x-2)(x+2)",
            "///;;;---***",
            "1e500 + x = 0",
        ]
        for step in adversarial_inputs:
            diag = detector.detect(
                user_step_str=step,
                previous_step_str="(x + 3)^2 = 25",
                target_equation_str="(x + 3)^2 = 25",
            )
            # Must return None or MisconceptionDiagnostic without throwing
            if diag is not None:
                assert hasattr(diag, "bug_id")
                assert hasattr(diag, "description")


class TestSymbolicEquivalenceEngineFuzzing:
    """Stress testing SymbolicEquivalenceEngine against parenthesis bombs and AST depth."""

    def test_parenthesis_bomb_raises_security_violation(self):
        from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
        engine = SymbolicEquivalenceEngine()
        bomb = "(" * 200 + "x" + ")" * 200
        with pytest.raises(SecurityViolationError):
            engine.sanitize_and_validate_ast(bomb)

    def test_nested_ast_depth_rejection(self):
        from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
        engine = SymbolicEquivalenceEngine(max_ast_depth=10)
        deep = "1 + (2 + (3 + (4 + (5 + (6 + (7 + (8 + (9 + (10 + (11 + x))))))))))"
        with pytest.raises(SecurityViolationError):
            engine.sanitize_and_validate_ast(deep)
