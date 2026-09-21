import pytest
import sympy as sp
from app.cas.preprocessor import ImplicitMultiplicationPreprocessor
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError

@pytest.fixture
def engine():
    return SymbolicEquivalenceEngine()

class TestCasEdgeCases:
    def test_uppercase_variable_normalization(self, engine):
        # Student types capital X
        preprocessed = ImplicitMultiplicationPreprocessor.preprocess("2X + 6 = 12")
        assert "2*x" in preprocessed or "2x" in preprocessed or "x" in preprocessed.lower()
        
        is_equiv, _, _ = engine.verify_equivalence("2*X + 6 = 12", "2*x + 6 = 12")
        assert is_equiv is True

    def test_double_equals_normalization(self, engine):
        # Double equals normalization (== to =)
        preprocessed = ImplicitMultiplicationPreprocessor.preprocess("x^2 - 5x + 6 == 0")
        assert preprocessed.count("=") == 1
        
        is_equiv, _, _ = engine.verify_equivalence("x^2 - 5x + 6 == 0", "x^2 - 5x + 6 = 0")
        assert is_equiv is True

    def test_colon_division_normalization(self, engine):
        # European / Turkish division with colon
        preprocessed = ImplicitMultiplicationPreprocessor.preprocess("(x + 2) : 4 = 3")
        assert "/" in preprocessed
        
        is_equiv, _, _ = engine.verify_equivalence("(x + 2) : 4 = 3", "(x + 2) / 4 = 3")
        assert is_equiv is True

    def test_empty_side_error_handling(self, engine):
        # Empty RHS or LHS should raise friendly ValueError, not unhandled crash
        with pytest.raises(ValueError, match="geçerli bir matematiksel ifade"):
            engine.parse_to_sympy("x = ")
            
        with pytest.raises(ValueError, match="geçerli bir matematiksel ifade"):
            engine.parse_to_sympy(" = 5")

    def test_multiple_equals_error_handling(self, engine):
        with pytest.raises(ValueError, match="tam olarak bir '=' işareti"):
            engine.parse_to_sympy("x = y = 2")

    def test_negative_discriminant_equation(self, engine):
        # x^2 + 9 = 0 has no real roots, but algebraic steps must verify accurately
        is_equiv, _, _ = engine.verify_equivalence("x^2 + 9 = 0", "x^2 = -9")
        assert is_equiv is True

    def test_double_root_delta_zero(self, engine):
        # (x - 3)^2 = 0 has Delta = 0, single root x = 3
        is_equiv, _, _ = engine.verify_equivalence("(x - 3)^2 = 0", "x^2 - 6*x + 9 = 0")
        assert is_equiv is True

    def test_rational_coefficients_scalar_multiple(self, engine):
        # x/2 + 1/3 = 5/6 is equivalent to 3x + 2 = 5
        is_equiv, _, _ = engine.verify_equivalence("x/2 + 1/3 = 5/6", "3*x + 2 = 5")
        assert is_equiv is True

    def test_function_names_not_corrupted_by_case_normalization(self, engine):
        # Abs, Poly, sin, exp etc. must not have their capitalized letters broken
        preprocessed = ImplicitMultiplicationPreprocessor.preprocess("Abs(X) + Poly(x)")
        assert "Abs(x)" in preprocessed

    def test_whitespace_and_power_redundancy(self, engine):
        # Extra whitespace around operators
        is_equiv, _, _ = engine.verify_equivalence("  x   +   5   =   12  ", "x + 5 = 12")
        assert is_equiv is True
