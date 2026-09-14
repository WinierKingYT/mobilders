"""
Hedef 5: Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası Test Paketi.
Test Kapsamı:
1. Vision & LaTeX Normalizasyon Pipeline (Kesir, Kök, İntegral, Türev, Üsler).
2. Defter Çözüm Adımı Segmentasyonu ve Knowledge DAG Eşleştirmesi (N01-N135).
3. Anti-Photomath Sokratik Hata Teşhisi (Cevabı Vermeden Adım Bazlı Yanılgı Tespiti).
4. Zero-Leakage Kalkanı Doğrulaması (Kök ve Çözüm Değerlerinin Sızdırılmaması).
5. FastAPI /api/v1/scan/diagnose Endpoint Entegrasyon Testleri.
"""

import pytest
import base64
from fastapi.testclient import TestClient
from app.main import app
from app.graph.knowledge_dag import KnowledgeDAG
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.socratic.guardrail import ZeroLeakageGuardrail
from app.ocr.vision_pipeline import MathVisionPipeline
from app.ocr.socratic_diagnoser import SocraticNotebookDiagnoser
from app.ocr.models import MathScanRequest, MathScanResponse


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def dag():
    return KnowledgeDAG()


@pytest.fixture
def cas():
    return SymbolicEquivalenceEngine()


@pytest.fixture
def detector(cas):
    return QuadraticMisconceptionDetector(cas_engine=cas)


@pytest.fixture
def vision(dag):
    return MathVisionPipeline(dag=dag)


@pytest.fixture
def diagnoser(cas, detector, dag, vision):
    return SocraticNotebookDiagnoser(
        cas=cas,
        detector=detector,
        dag=dag,
        vision_pipeline=vision,
    )


# ==============================================================================
# 1. VISION & LATEX NORMALIZATION PIPELINE
# ==============================================================================

def test_latex_normalization_fractions_and_roots(vision):
    raw = r"\frac{2x + 6}{2} = \sqrt{16}"
    norm = vision.normalize_latex(raw)
    assert norm == "(2x + 6)/(2) = sqrt(16)"


def test_latex_normalization_calculus_symbols(vision):
    raw = r"\int (3x^2 + 1) dx"
    norm = vision.normalize_latex(raw)
    assert "integrate" in norm
    assert "**2" in norm


def test_latex_normalization_trig_and_powers(vision):
    raw = r"\sin^2(x) + \cos^2(x) = 1"
    norm = vision.normalize_latex(raw)
    assert "sin" in norm
    assert "cos" in norm
    assert "**2" in norm


def test_line_segmentation_strips_enumeration(vision):
    raw = """
    1) x^2 - 5*x + 6 = 0
    2) (x - 2)*(x - 3) = 0
    Adım 3: x - 2 = 0
    """
    lines = vision._segment_text_into_lines(raw)
    assert len(lines) == 3
    assert lines[0] == "x^2 - 5*x + 6 = 0"
    assert lines[1] == "(x - 2)*(x - 3) = 0"
    assert lines[2] == "x - 2 = 0"


def test_link_problem_to_dag_quadratics(vision):
    node_id, title = vision.link_problem_to_dag_node("x^2 - 4 = 0")
    assert node_id == "N19"
    assert "Diskriminant" in title or "Kuadratik" in title


def test_link_problem_to_dag_trigonometry(vision):
    node_id, title = vision.link_problem_to_dag_node(r"\sin(2x) = \cos(x)")
    assert node_id == "N52"
    assert "Trigonometrik" in title or "Birim" in title


def test_link_problem_to_dag_calculus_derivative(vision):
    node_id, title = vision.link_problem_to_dag_node("d/dx (x^3 + 2x)")
    assert node_id in {"N89", "N94", "N101"}


def test_link_problem_to_dag_calculus_integral(vision):
    node_id, title = vision.link_problem_to_dag_node(r"\int (2x + 1) dx")
    assert node_id in {"N111", "N117", "N123", "N132"}


# ==============================================================================
# 2. ANTI-PHOTOMATH SOKRATİK ADIM VE HATA TEŞHİSİ
# ==============================================================================

def test_notebook_fully_valid_solution(diagnoser):
    """Tüm adımları doğru olan defter çözümü: Hata yok, cevabı ifşa etmeden üstbilişsel soru sorar."""
    lines = [
        "x^2 - 9 = 0",
        "(x - 3)*(x + 3) = 0",
    ]
    resp = diagnoser.diagnose_notebook_solution(lines)
    assert resp.has_error is False
    assert resp.error_step_index is None
    assert resp.detected_bug_id is None
    assert len(resp.segmented_steps) == 1
    assert resp.segmented_steps[0].is_valid is True
    # Asla kökleri söylememeli (3 ve -3)
    assert "3" not in resp.socratic_hint or "x = 3" not in resp.socratic_hint
    assert "?" in resp.socratic_hint


def test_notebook_quadratic_bug_quad_03_detected(diagnoser):
    """1. adımda tam kare açılımında çarpımın iki katı unutulmuş (BUG-QUAD-03)."""
    lines = [
        "(x + 3)^2 = 25",
        "x^2 + 9 = 25",  # 6x unutuldu!
    ]
    resp = diagnoser.diagnose_notebook_solution(lines)
    assert resp.has_error is True
    assert resp.error_step_index == 1
    assert resp.detected_bug_id == "BUG-QUAD-03"
    assert resp.segmented_steps[0].is_valid is False
    assert "tam kare" in resp.socratic_hint or "2ab" in resp.socratic_hint
    assert "?" in resp.socratic_hint


def test_notebook_quadratic_bug_quad_01_detected(diagnoser):
    """Sıfır olmayan sayıya sıfır-çarpım kuralı uygulanmış (BUG-QUAD-01)."""
    lines = [
        "x*(x + 6) = 2",
        "x = 2",
    ]
    resp = diagnoser.diagnose_notebook_solution(lines)
    assert resp.has_error is True
    assert resp.error_step_index == 1
    assert resp.detected_bug_id == "BUG-QUAD-01"
    assert "sıfır-çarpım" in resp.socratic_hint or "sıfır" in resp.socratic_hint


def test_notebook_trig_bug_trig_01_detected(diagnoser):
    """Trigonometride sahte dağılma kuralı (sin(x+y) = sin(x) + sin(y))."""
    lines = [
        "sin(x + y)",
        "sin(x) + sin(y)",
    ]
    resp = diagnoser.diagnose_notebook_solution(lines)
    assert resp.has_error is True
    assert resp.detected_bug_id == "BUG-TRIG-01"
    assert "toplam-fark" in resp.socratic_hint or "dağıt" in resp.socratic_hint


def test_notebook_calculus_chain_rule_error(diagnoser):
    """Zincir kuralında iç türevin unutulması (BUG-CALC-01)."""
    lines = [
        "diff((3*x + 1)**4, x)",
        "4*(3*x + 1)**3",
    ]
    resp = diagnoser.diagnose_notebook_solution(lines)
    assert resp.has_error is True
    assert resp.detected_bug_id == "BUG-CALC-01"
    assert "zincir" in resp.socratic_hint or "iç" in resp.socratic_hint


def test_notebook_calculus_integral_missing_c(diagnoser):
    """Belirsiz integralde +C'nin unutulması (BUG-INT-01)."""
    lines = [
        "integrate(x, x)",
        "x^2/2",
    ]
    resp = diagnoser.diagnose_notebook_solution(lines)
    assert resp.has_error is True
    assert resp.detected_bug_id == "BUG-INT-01"
    assert "sabiti" in resp.socratic_hint or "+ C" in resp.socratic_hint


# ==============================================================================
# 3. ZERO-LEAKAGE KALKANI DOĞRULAMASI
# ==============================================================================

def test_zero_leakage_shield_scrubs_direct_answers():
    guard = ZeroLeakageGuardrail()
    leaked = "Cevap x = 5 ve x = -2 çıkar."
    sanitized, was_intercepted = guard.enforce_zero_leakage(leaked, language="tr")
    assert was_intercepted is True
    assert "x = 5" not in sanitized
    assert "?" in sanitized


def test_zero_leakage_shield_permits_pedagogical_hints():
    guard = ZeroLeakageGuardrail()
    safe_hint = "1. adımda tam kare açılımını yaparken 2ab terimini eklemeyi unuttun mu?"
    sanitized, was_intercepted = guard.enforce_zero_leakage(safe_hint, language="tr")
    assert was_intercepted is False
    assert sanitized == safe_hint


# ==============================================================================
# 4. FASTAPI ENDPOINT ENTEGRASYON TESTLERİ (/api/v1/scan/diagnose)
# ==============================================================================

def test_api_scan_diagnose_text_override(client):
    payload = {
        "raw_text_override": "x*(x + 6) = 2\nx = 2",
        "student_id": "TEST-OCR-STU-01",
    }
    res = client.post("/api/v1/scan/diagnose", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_error"] is True
    assert data["detected_bug_id"] == "BUG-QUAD-01"
    assert data["dag_node_id"] is not None
    assert data["is_zero_leakage_sanitized"] is True
    assert "?" in data["socratic_hint"]


def test_api_scan_diagnose_base64_payload(client):
    encoded = base64.b64encode(b"(x + 3)^2 = 25\nx^2 + 9 = 25").decode("utf-8")
    payload = {
        "image_base64": f"data:image/png;base64,{encoded}",
        "student_id": "TEST-OCR-STU-02",
    }
    res = client.post("/api/v1/scan/diagnose", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_error"] is True
    assert data["detected_bug_id"] == "BUG-QUAD-03"
    assert len(data["segmented_steps"]) >= 1


def test_api_scan_diagnose_valid_calculus_solution(client):
    payload = {
        "raw_text_override": "integrate(2*x, x)\nx**2 + C",
        "student_id": "TEST-OCR-STU-03",
    }
    res = client.post("/api/v1/scan/diagnose", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["has_error"] is False
    assert data["error_step_index"] is None
