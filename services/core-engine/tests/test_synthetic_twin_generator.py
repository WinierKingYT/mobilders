import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.curriculum_generator.synthetic_twin_generator import (
    SyntheticTwinGenerator,
    TwinGenerateRequest,
    TwinQuestionResponse,
)

client = TestClient(app)


def test_twin_generator_bug_quad_01():
    twin = SyntheticTwinGenerator.generate("BUG-QUAD-01", difficulty_level=1)
    assert twin.targeted_bug_id == "BUG-QUAD-01"
    assert "Sıfır-Çarpım" in twin.targeted_bug_title
    assert "=" in twin.target_equation
    assert len(twin.canonical_roots) == 2
    assert "sağ tarafı sıfırdan farklı" in twin.pedagogical_focus


def test_twin_generator_bug_quad_02():
    twin = SyntheticTwinGenerator.generate("BUG-QUAD-02", difficulty_level=1)
    assert twin.targeted_bug_id == "BUG-QUAD-02"
    assert "Negatif İkiz Kök" in twin.targeted_bug_title
    assert len(twin.canonical_roots) == 2
    # Simetrik kökler olmalı (r1 + r2 == 0)
    assert sum(twin.canonical_roots) == 0.0


def test_twin_generator_bug_quad_03():
    twin = SyntheticTwinGenerator.generate("BUG-QUAD-03", difficulty_level=1)
    assert twin.targeted_bug_id == "BUG-QUAD-03"
    assert "Binom Karesi" in twin.targeted_bug_title
    assert len(twin.canonical_roots) == 2


def test_twin_generator_bug_quad_04():
    twin = SyntheticTwinGenerator.generate("BUG-QUAD-04", difficulty_level=1)
    assert twin.targeted_bug_id == "BUG-QUAD-04"
    assert "Tam Kare" in twin.targeted_bug_title
    assert len(twin.canonical_roots) == 2


def test_twin_generator_sign_flip():
    twin = SyntheticTwinGenerator.generate("SIGN_FLIP", difficulty_level=1)
    assert twin.targeted_bug_id == "SIGN_FLIP"
    assert "Eksi İşareti" in twin.targeted_bug_title
    assert len(twin.canonical_roots) >= 1


def test_twin_generator_generic():
    twin = SyntheticTwinGenerator.generate("UNKNOWN_BUG", difficulty_level=1)
    assert twin.targeted_bug_id == "UNKNOWN_BUG"
    assert len(twin.canonical_roots) == 2


def test_twin_generate_api_endpoint():
    payload = {
        "bug_id": "BUG-QUAD-01",
        "difficulty_level": 1,
    }
    response = client.post("/api/v1/twin/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["targeted_bug_id"] == "BUG-QUAD-01"
    assert "target_equation" in data
    assert len(data["canonical_roots"]) == 2
    assert "hint" in data


def test_twin_generator_monic_quadratic_formatting():
    # sum_r = 0 (b = 0) -> no 0x
    eq_zero_b = SyntheticTwinGenerator._format_monic_quadratic(2, -2)
    assert eq_zero_b == "x² - 4 = 0"
    assert "0x" not in eq_zero_b

    # sum_r = 1 (b = -1) -> - x (not - 1x)
    eq_neg_1 = SyntheticTwinGenerator._format_monic_quadratic(2, -1)
    assert eq_neg_1 == "x² - x - 2 = 0"
    assert "1x" not in eq_neg_1

    # sum_r = -1 (b = 1) -> + x (not + 1x)
    eq_pos_1 = SyntheticTwinGenerator._format_monic_quadratic(-2, 1)
    assert eq_pos_1 == "x² + x - 2 = 0"
    assert "1x" not in eq_pos_1

    # Standard positive b and positive c
    eq_std = SyntheticTwinGenerator._format_monic_quadratic(2, 3)
    assert eq_std == "x² - 5x + 6 = 0"

    # Roots 0, 0
    eq_zero = SyntheticTwinGenerator._format_monic_quadratic(0, 0)
    assert eq_zero == "x² = 0"


def test_twin_generator_deduplicates_original_equation():
    # BUG-QUAD-02 has: "x² = 49", "2x² = 72", "x² - 64 = 0"
    for _ in range(15):
        twin = SyntheticTwinGenerator.generate(
            "BUG-QUAD-02",
            original_equation="x² = 49",
            difficulty_level=1,
        )
        assert twin.target_equation != "x² = 49"
        assert twin.target_equation in ["2x² = 72", "x² - 64 = 0"]

    # Also check with different whitespace / syntax (e.g. x^2=49)
    for _ in range(15):
        twin = SyntheticTwinGenerator.generate(
            "BUG-QUAD-02",
            original_equation="x^2=49",
            difficulty_level=1,
        )
        assert twin.target_equation != "x² = 49"


def test_twin_generate_api_endpoint_with_original_equation():
    payload = {
        "bug_id": "BUG-QUAD-02",
        "original_equation": "x² = 49",
        "difficulty_level": 1,
    }
    response = client.post("/api/v1/twin/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_equation"] != "x² = 49"
    assert data["target_equation"] in ["2x² = 72", "x² - 64 = 0"]

