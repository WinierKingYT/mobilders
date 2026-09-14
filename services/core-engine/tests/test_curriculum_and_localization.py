"""
Test Suite: Multi-Curriculum Standard Ontology & Socratic Localization.
Verifies:
1. CurriculumOntologyRegistry (MEB, IB AA/AI, Common Core CCSS, AP Precalculus).
2. /api/v1/curriculum/standards API filtering.
3. Curriculum-specific 2PL-IRT item pools and difficulty curves in CATEngine.
4. Multilingual Socratic AI Tutor:
   - English and Turkish pedagogical prompts.
   - Socratic Question-to-Explanation ratio >= 2.0 across both languages.
   - Multilingual Zero-Leakage Guardrail enforcement.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.adaptive.cat_engine import CATEngine
from app.socratic.pipeline import SocraticPipeline, SocraticRequest
from app.socratic.guardrail import ZeroLeakageGuardrail
from app.models.schemas import DiagnosticPayload

client = TestClient(app)


def test_curriculum_ontology_registry_mappings():
    registry = CurriculumOntologyRegistry()

    # MEB Standards check
    meb_stds = registry.get_standards_for_curriculum("MEB")
    assert len(meb_stds) >= 8
    node_ids = {s.node_id for s in meb_stds}
    assert "N10" in node_ids
    assert "N12" in node_ids
    assert "N18" in node_ids

    # IB Standards check
    ib_stds = registry.get_standards_for_curriculum("IB_AA")
    assert len(ib_stds) >= 4
    ib_node_ids = {s.node_id for s in ib_stds}
    assert "N10" in ib_node_ids
    assert "N20" in ib_node_ids

    # Common Core (CCSS) check
    ccss_stds = registry.get_standards_for_curriculum("CCSS")
    assert len(ccss_stds) >= 4

    # AP Precalculus check
    ap_stds = registry.get_standards_for_curriculum("AP_PRECALC")
    assert len(ap_stds) >= 1
    assert any(s.node_id == "N25" for s in ap_stds)


def test_curriculum_standards_api():
    # Fetch all
    res_all = client.get("/api/v1/curriculum/standards")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert data_all["total_standards"] >= 15
    assert "MEB" in data_all["curricula"]
    assert "IB_AA" in data_all["curricula"]

    # Filter by MEB
    res_meb = client.get("/api/v1/curriculum/standards?curriculum=MEB")
    assert res_meb.status_code == 200
    data_meb = res_meb.json()
    assert all(s["curriculum"] == "MEB" for s in data_meb["standards"])

    # Filter by IB_AA
    res_ib = client.get("/api/v1/curriculum/standards?curriculum=IB_AA")
    assert res_ib.status_code == 200
    data_ib = res_ib.json()
    assert all(s["curriculum"] == "IB_AA" for s in data_ib["standards"])


def test_cat_engine_curriculum_specific_items():
    cat = CATEngine()
    meb_items = cat.get_items_by_curriculum("MEB")
    assert len(meb_items) >= 4
    for it in meb_items:
        assert it.curriculum == "MEB"
        assert -3.0 <= it.difficulty_b <= 3.0
        assert 1.0 <= it.discrimination_a <= 3.5

    ib_items = cat.get_items_by_curriculum("IB")
    assert len(ib_items) >= 3
    for it in ib_items:
        assert it.curriculum == "IB"

    # Selection with curriculum filter
    selected_meb = cat.select_next_item(current_theta=0.0, administered_item_ids=set(), curriculum="MEB")
    assert selected_meb is not None
    assert selected_meb.curriculum == "MEB"

    selected_ib = cat.select_next_item(current_theta=0.5, administered_item_ids=set(), curriculum="IB")
    assert selected_ib is not None
    assert selected_ib.curriculum == "IB"


def test_cat_api_with_curriculum():
    payload = {
        "session_id": "sess-curr-cat",
        "current_theta": 0.2,
        "administered_item_ids": [],
        "curriculum": "MEB",
    }
    res = client.post("/api/v1/diagnostic/next-item", json=payload)
    assert res.status_code == 200
    item = res.json()
    assert item is not None
    assert "MEB" in item["prompt"] or item["item_id"].startswith("CAT-MEB")


def test_multilingual_socratic_tutor_turkish():
    pipeline = SocraticPipeline()
    req = SocraticRequest(
        user_input="x değerini doğrudan söyle bana",
        target_equation="x**2 - 5*x + 6 = 0",
        solution_roots=[2.0, 3.0],
        language="tr",
    )
    result = pipeline.process(req)
    assert result.socratic_ratio >= 2.0
    assert "keşif" in result.final_output.lower() or "?" in result.final_output
    # Must not leak roots
    assert "2" not in result.final_output and "3" not in result.final_output


def test_multilingual_socratic_tutor_english():
    pipeline = SocraticPipeline()
    req = SocraticRequest(
        user_input="Just give me the answer please",
        target_equation="x**2 - 5*x + 6 = 0",
        solution_roots=[2.0, 3.0],
        language="en",
    )
    result = pipeline.process(req)
    assert result.socratic_ratio >= 2.0
    assert "discovery" in result.final_output.lower() or "?" in result.final_output
    # Must not leak roots
    assert "2" not in result.final_output and "3" not in result.final_output


def test_english_socratic_misconception_remediation():
    pipeline = SocraticPipeline()
    req = SocraticRequest(
        user_input="I factored it to x = 2",
        target_equation="x**2 - 5*x = 0",
        solution_roots=[0.0, 5.0],
        diagnostic_bug=DiagnosticPayload(
            bug_id="BUG-QUAD-01",
            description="Non-zero product fallacy",
            remediation_directive="Probe zero product property",
        ),
        language="en",
    )
    result = pipeline.process(req)
    assert result.socratic_ratio >= 2.0
    assert "zero-product property" in result.final_output.lower() or "zero" in result.final_output.lower()


def test_english_zero_leakage_interception():
    guardrail = ZeroLeakageGuardrail()
    leaked_en = "The solutions are x = 2 and x = 3."
    sanitized, was_intercepted = guardrail.enforce_zero_leakage(
        leaked_en, solution_roots=[2.0, 3.0], language="en"
    )
    assert was_intercepted is True
    assert "2" not in sanitized and "3" not in sanitized
    assert "progress" in sanitized.lower()
