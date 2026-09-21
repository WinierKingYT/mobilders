import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.vault.mistake_vault import CognitiveMistakeVault, MistakeStatus
from app.api.deps import cognitive_mistake_vault


@pytest.fixture
def fresh_vault():
    vault = CognitiveMistakeVault(db_path=":memory:")
    return vault


def test_misconception_profile_empty(fresh_vault):
    profile = fresh_vault.get_misconception_profile("student_clean")
    assert profile["user_id"] == "student_clean"
    assert profile["total_recorded_mistakes"] == 0
    assert profile["total_cured"] == 0
    assert profile["overall_cure_rate"] == 0.0
    assert profile["top_recurring_traps"] == []
    assert len(profile["categories"]) >= 5
    for cat in profile["categories"]:
        assert cat["total_mistakes"] == 0
        assert cat["nodes"] == []


def test_misconception_profile_categories_and_critical_status(fresh_vault):
    user_id = "student_profile_1"

    # 1. Kayıt: BUG-QUAD-01 (Kuadratik)
    rec1 = fresh_vault.record_mistake(
        user_id=user_id,
        node_id="NODE-QUAD-01",
        bug_id="BUG-QUAD-01",
        problem_statement="(x - 2)(x - 3) = 6",
        offending_step="x - 2 = 6 veya x - 3 = 6",
        correct_principle="Eşitliğin sağ tarafı sıfır olmalıdır.",
        remediation_directive="Denklemi önce ax^2 + bx + c = 0 formuna getir.",
    )

    # 2. Kayıt: Tekrar eden BUG-QUAD-01 -> Kritik zaaf olmalı
    rec2 = fresh_vault.record_mistake(
        user_id=user_id,
        node_id="NODE-QUAD-01",
        bug_id="BUG-QUAD-01",
        problem_statement="(x + 1)(x - 4) = 10",
        offending_step="x + 1 = 10",
        correct_principle="Eşitliğin sağ tarafı sıfır olmalıdır.",
        remediation_directive="Parantezleri aç ve terimleri sola topla.",
    )

    # 3. Kayıt: SIGN_FLIP (İşaret & Dağılma)
    rec3 = fresh_vault.record_mistake(
        user_id=user_id,
        node_id="NODE-FOUND-01",
        bug_id="SIGN_FLIP",
        problem_statement="-(2x - 5) = 3",
        offending_step="-2x - 5 = 3",
        correct_principle="Eksi her iki terime de dağıtılmalıdır.",
        remediation_directive="Eksi ile eksinin çarpımı artıdır.",
    )

    profile = fresh_vault.get_misconception_profile(user_id)
    assert profile["total_recorded_mistakes"] == 3
    assert profile["total_cured"] == 0
    assert profile["overall_cure_rate"] == 0.0

    # Top recurring traps olmalı
    assert len(profile["top_recurring_traps"]) == 2
    top1 = profile["top_recurring_traps"][0]
    assert top1["bug_id"] == "BUG-QUAD-01"
    assert top1["frequency"] == 2
    assert top1["open_count"] == 2
    assert top1["status"] == "critical"
    assert top1["category_id"] == "KUADRATIK_DENKLEMLER"

    top2 = profile["top_recurring_traps"][1]
    assert top2["bug_id"] == "SIGN_FLIP"
    assert top2["frequency"] == 1
    assert top2["status"] == "warning"
    assert top2["category_id"] == "ISARET_VE_DAGILMA"

    # Kategoriler kontrolü
    quad_cat = next(c for c in profile["categories"] if c["category_id"] == "KUADRATIK_DENKLEMLER")
    assert quad_cat["total_mistakes"] == 2
    assert quad_cat["active_mistakes"] == 2
    assert len(quad_cat["nodes"]) == 1
    assert quad_cat["nodes"][0]["status"] == "critical"

    sign_cat = next(c for c in profile["categories"] if c["category_id"] == "ISARET_VE_DAGILMA")
    assert sign_cat["total_mistakes"] == 1
    assert sign_cat["active_mistakes"] == 1
    assert len(sign_cat["nodes"]) == 1
    assert sign_cat["nodes"][0]["status"] == "warning"


def test_misconception_profile_cured_lifecycle(fresh_vault):
    user_id = "student_cured_flow"

    rec = fresh_vault.record_mistake(
        user_id=user_id,
        node_id="NODE-QUAD-02",
        bug_id="BUG-QUAD-02",
        problem_statement="x^2 = 25",
        offending_step="x = 5",
        correct_principle="x^2 = 25 için hem x=5 hem x=-5 köktür.",
        remediation_directive="Negatif simetrik kökü unutma.",
    )

    # Önce warning
    p1 = fresh_vault.get_misconception_profile(user_id)
    assert p1["top_recurring_traps"][0]["status"] == "warning"

    # Durumu CURED yap
    rec.status = MistakeStatus.CURED
    fresh_vault.update_record(rec)

    p2 = fresh_vault.get_misconception_profile(user_id)
    assert p2["total_cured"] == 1
    assert p2["overall_cure_rate"] == 1.0
    assert p2["top_recurring_traps"][0]["status"] == "cured"


def test_vault_misconception_profile_endpoint():
    client = TestClient(app)
    user_id = "test_api_profile_user"

    cognitive_mistake_vault.record_mistake(
        user_id=user_id,
        node_id="NODE-QUAD-03",
        bug_id="BUG-QUAD-03",
        problem_statement="(x + 3)^2",
        offending_step="x^2 + 9",
        correct_principle="(x+a)^2 = x^2 + 2ax + a^2",
        remediation_directive="Ortadaki 2ax terimini unutma.",
    )

    response = client.get(f"/api/v1/vault/misconception-profile/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["total_recorded_mistakes"] >= 1
    assert any(c["category_id"] == "ISARET_VE_DAGILMA" for c in data["categories"])
