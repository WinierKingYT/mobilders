import pytest
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector


@pytest.fixture
def detector():
    cas = SymbolicEquivalenceEngine()
    return QuadraticMisconceptionDetector(cas)


def test_detect_bug_quad_01_non_zero_product(detector):
    prev_step = "x*(x + 6) = 2"
    user_step = "x = 2"
    target = "x**2 + 6*x - 2 = 0"

    diag = detector.detect(user_step, prev_step, target)
    assert diag is not None
    assert diag.bug_id == "BUG-QUAD-01"
    assert "Sıfır-çarpım kuralı" in diag.description


def test_detect_bug_quad_02_missing_negative_root(detector):
    prev_step = "x**2 = 25"
    user_step = "x = 5"
    target = "x**2 - 25 = 0"

    diag = detector.detect(user_step, prev_step, target)
    assert diag is not None
    assert diag.bug_id == "BUG-QUAD-02"
    assert "negatif kök unutuldu" in diag.description


def test_detect_bug_quad_03_exponent_distribution(detector):
    prev_step = "(x + 3)**2 = 11"
    user_step = "x**2 + 9 = 11"
    target = "x**2 + 6*x - 2 = 0"

    diag = detector.detect(user_step, prev_step, target)
    assert diag is not None
    assert diag.bug_id == "BUG-QUAD-03"
    assert "2ab" in diag.description


def test_detect_bug_quad_04_root_cancelling(detector):
    prev_step = "x**2 = 6*x"
    user_step = "x = 6"
    target = "x**2 - 6*x = 0"

    diag = detector.detect(user_step, prev_step, target)
    assert diag is not None
    assert diag.bug_id == "BUG-QUAD-04"
    assert "x=0 kökü yok edildi" in diag.description


def test_detect_bug_quad_05_formula_sign_error(detector):
    prev_step = "x**2 - 5*x + 6 = 0"
    user_step = "x = (-5 + 1)/2"  # b = -5 iken -b yerine -5 yazılmış
    target = "x**2 - 5*x + 6 = 0"

    diag = detector.detect(user_step, prev_step, target)
    assert diag is not None
    assert diag.bug_id == "BUG-QUAD-05"
    assert "(-b) terimi" in diag.description


def test_valid_step_produces_no_bug(detector):
    prev_step = "x*(x + 6) = 2"
    user_step = "x**2 + 6*x = 2"
    target = "x**2 + 6*x - 2 = 0"

    diag = detector.detect(user_step, prev_step, target)
    assert diag is None
