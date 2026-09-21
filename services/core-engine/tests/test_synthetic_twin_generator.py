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
