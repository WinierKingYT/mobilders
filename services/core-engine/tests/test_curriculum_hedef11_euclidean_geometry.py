"""
HEDEF 11: Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru Kapsamlı Test Paketi
N161 - N185 Düğümleri, Üçgen/Dörtgen/Çember Geometrisi, Ek Çizim Önerici ve BUG-EUC-01..05 Testleri.
"""
import pytest
import math
from app.graph.knowledge_dag import KnowledgeDAG
from app.geometry.synthetic_geometry import (
    Triangle2D,
    EuclideanRelations,
    AuxiliaryConstructionAdvisor,
    solve_synthetic_geometry,
)
from app.misconceptions.detector import QuadraticMisconceptionDetector


@pytest.fixture
def dag():
    return KnowledgeDAG()


@pytest.fixture
def detector():
    return QuadraticMisconceptionDetector()


# ==============================================================================
# 1. KNOWLEDGE DAG STRUCTURE & PREREQUISITES (N161 - N185)
# ==============================================================================

def test_dag_hedef11_total_nodes_185(dag):
    """Grafın en az 185 düğüm içerdiğini ve N161-N185 aralığının eksiksiz tanımlandığını doğrular."""
    assert len(dag.nodes) >= 185
    for i in range(161, 186):
        n_id = f"N{i}"
        assert n_id in dag.nodes, f"Düğüm {n_id} eksik!"
        node = dag.get_node(n_id)
        assert node.title != ""
        assert node.canonical_code != ""
        assert node.level == 17
        assert -1.0 <= node.default_difficulty_b <= 3.0
        assert 1.0 <= node.discrimination_a <= 3.0


def test_dag_hedef11_cycle_free(dag):
    """N161-N185 düğümlerinin döngüsüz (DAG) olduğunu doğrular."""
    dag.assert_cycle_free()


def test_dag_hedef11_topological_sort(dag):
    """N161-N185 içeren tüm grafın topolojik sıralanabildiğini doğrular."""
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == len(dag.nodes)
    # Önkoşul sıralamaları kontrolü
    assert sorted_nodes.index("N161") < sorted_nodes.index("N162")
    assert sorted_nodes.index("N161") < sorted_nodes.index("N164")
    assert sorted_nodes.index("N164") < sorted_nodes.index("N165")
    assert sorted_nodes.index("N168") < sorted_nodes.index("N169")
    assert sorted_nodes.index("N177") < sorted_nodes.index("N178")
    assert sorted_nodes.index("N181") < sorted_nodes.index("N182")
    assert sorted_nodes.index("N183") < sorted_nodes.index("N184")


def test_dag_hedef11_prerequisites(dag):
    """Öklid geometrisi düğümlerinin sağlam hiyerarşik önkoşullara bağlandığını doğrular."""
    # N162 (üçgen eşitsizliği) N161'e (üçgende açılar) bağlı
    assert "N161" in dag.get_prerequisites("N162")
    # N165 (öklid bağıntıları) N164'e (pisagor) bağlı
    assert "N164" in dag.get_prerequisites("N165")
    # N169 (alan-benzerlik ilişkisi) N168'e (benzerlik) bağlı
    assert "N168" in dag.get_prerequisites("N169")
    # N182 (daire dilim alanı) N181'e (yay uzunluğu) bağlı
    assert "N181" in dag.get_prerequisites("N182")
    # N185 (küre) N182 ve N183'e bağlı
    prereqs_185 = dag.get_prerequisites("N185")
    assert "N182" in prereqs_185 and "N183" in prereqs_185


# ==============================================================================
# 2. TRIANGLE2D OPERATIONS & PROPERTIES
# ==============================================================================

def test_triangle2d_validity_and_angle_sum():
    # 30-60-90 üçgeni
    t = Triangle2D(angle_A=30.0, angle_B=60.0)
    assert t.angle_C == 90.0
    assert t.is_right_angled


def test_triangle2d_invalid_angle_sum():
    with pytest.raises(ValueError, match="180° veya daha büyük olamaz"):
        Triangle2D(angle_A=100.0, angle_B=85.0)


def test_triangle2d_inequality_violation():
    # 3, 4, 8 üçgen eşitsizliğini sağlamaz (8 >= 3 + 4)
    with pytest.raises(ValueError, match="üçgen eşitsizliğini sağlamıyor"):
        Triangle2D(a=3.0, b=4.0, c=8.0)


def test_triangle2d_3_4_5_right_triangle():
    t = Triangle2D(a=3.0, b=4.0, c=5.0)
    assert t.is_right_angled
    assert not t.is_isosceles
    assert not t.is_equilateral
    assert math.isclose(t.perimeter, 12.0)
    assert math.isclose(t.area, 6.0)
    # İç teğet çember yarıçapı: r = A / s = 6 / 6 = 1.0
    assert math.isclose(t.inradius, 1.0)
    # Çevrel çember yarıçapı: R = abc / (4A) = 60 / 24 = 2.5 (hipotenüsün yarısı)
    assert math.isclose(t.circumradius, 2.5)


def test_triangle2d_equilateral():
    t = Triangle2D(a=6.0, b=6.0, c=6.0)
    assert t.is_equilateral
    assert t.is_isosceles
    assert not t.is_right_angled
    assert math.isclose(t.angle_A, 60.0, abs_tol=1e-3)
    # Alan = a^2 * sqrt(3) / 4 = 36 * sqrt(3) / 4 = 9 * sqrt(3) ~ 15.588
    expected_area = 9.0 * math.sqrt(3.0)
    assert math.isclose(t.area, expected_area, abs_tol=1e-4)
    # Yükseklik = a * sqrt(3) / 2 = 3 * sqrt(3) ~ 5.196
    assert math.isclose(t.altitude_to_base("a"), 3.0 * math.sqrt(3.0), abs_tol=1e-4)


def test_triangle2d_isosceles():
    # Kenarları 5, 5, 6 olan ikizkenar üçgen
    t = Triangle2D(a=5.0, b=5.0, c=6.0)
    assert t.is_isosceles
    assert not t.is_equilateral
    # Yükseklik c kenarına inen: 5^2 - 3^2 = 16 => h = 4
    assert math.isclose(t.altitude_to_base("c"), 4.0, abs_tol=1e-4)
    # Alan = 6 * 4 / 2 = 12
    assert math.isclose(t.area, 12.0, abs_tol=1e-4)


def test_triangle2d_median():
    # 3-4-5 üçgeninde hipotenüse (c=5) inen kenarortay = 2.5 (muhteşem üçlü)
    t = Triangle2D(a=3.0, b=4.0, c=5.0)
    assert math.isclose(t.median_to_base("c"), 2.5, abs_tol=1e-4)


# ==============================================================================
# 3. EUCLIDEAN RELATIONS
# ==============================================================================

def test_euclidean_relations_height():
    # p = 4, k = 9 => h = sqrt(36) = 6
    h = EuclideanRelations.height_from_segments(4.0, 9.0)
    assert math.isclose(h, 6.0)


def test_euclidean_relations_legs():
    # a = 25, k = 9 => b = sqrt(9 * 25) = 15
    # p = 16 => c = sqrt(16 * 25) = 20
    b = EuclideanRelations.leg_from_segment_and_hypotenuse(9.0, 25.0)
    c = EuclideanRelations.leg_from_segment_and_hypotenuse(16.0, 25.0)
    assert math.isclose(b, 15.0)
    assert math.isclose(c, 20.0)
    # b^2 + c^2 = 15^2 + 20^2 = 225 + 400 = 625 = 25^2
    assert math.isclose(b**2 + c**2, 25.0**2)


def test_euclidean_relations_area_product():
    # b = 15, c = 20, a = 25, h = 12 (h = sqrt(9*16) = 12)
    # 15 * 20 = 300, 25 * 12 = 300
    assert EuclideanRelations.verify_area_product(15.0, 20.0, 25.0, 12.0)


# ==============================================================================
# 4. AUXILIARY CONSTRUCTION ADVISOR (AKILLI EK ÇİZİM MOTORU)
# ==============================================================================

def test_advisor_isosceles_drop_altitude():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "triangle",
        "properties": ["ikizkenar"],
        "goal": "kenar_bulma",
    })
    assert hint["action"] == "TABANA_DIKME_INDIR"
    assert "tabana ait yardımcı bir yükseklik indirmeyi dene" in hint["pedagogical_hint"]
    assert "kenarortay" in hint["pedagogical_hint"]


def test_advisor_right_triangle_hypotenuse_median():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "triangle",
        "properties": ["dik_ucgen", "hipotenus_orta"],
        "goal": "uzunluk",
    })
    assert hint["action"] == "MUHTESEM_UCLU_CIZ"
    assert "Muhteşem Üçlü" in hint["pedagogical_hint"]


def test_advisor_midsegment():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "triangle",
        "properties": ["orta_nokta"],
        "goal": "uzunluk_bulma",
    })
    assert hint["action"] == "ORTA_TABAN_BIRLESTIR"
    assert "orta taban" in hint["pedagogical_hint"]


def test_advisor_trapezoid_parallel_leg():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "yamuk",
        "properties": ["trapezoid"],
        "goal": "kenar_iliskisi",
    })
    assert hint["action"] == "YAN_KENARA_PARALEL_CIZ"
    assert "paralel doğru parçası çizerek" in hint["pedagogical_hint"]


def test_advisor_trapezoid_altitudes_for_area():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "yamuk",
        "properties": ["trapezoid"],
        "goal": "alan_hesabi",
    })
    assert hint["action"] == "TABANA_DIKLER_INDIR"
    assert "dikme indirerek" in hint["pedagogical_hint"]


def test_advisor_circle_tangent():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "circle",
        "properties": ["cember_teget"],
        "goal": "yaricap",
    })
    assert hint["action"] == "MERKEZI_TEGET_NOKTASINA_BIRLESTIR"
    assert "r ⊥ d" in hint["pedagogical_hint"] or "diktir" in hint["pedagogical_hint"]


def test_advisor_circle_chord():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "circle",
        "properties": ["cember_kiris"],
        "goal": "kiris_uzunlugu",
    })
    assert hint["action"] == "MERKEZDEN_KIRISE_DIKME_INDIR"
    assert "kirişi ve kirişin gördüğü yayı iki eşit parçaya böler" in hint["pedagogical_hint"]


def test_advisor_diameter_inscribed():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "circle",
        "properties": ["cap", "cevre_aci"],
        "goal": "aci_bulma",
    })
    assert hint["action"] == "CAPI_GOREN_UCGENI_TAMAMLA"
    assert "90°" in hint["pedagogical_hint"]


# ==============================================================================
# 5. MISCONCEPTION RULES (BUG-EUC-01 .. BUG-EUC-05)
# ==============================================================================

def test_bug_euc_01_triangle_inequality(detector):
    """BUG-EUC-01: Üçgen eşitsizliği ihlali (3, 4, 8 kenarlarıyla üçgen çizmeye kalkma)."""
    diag1 = detector.detect("kenarlar = 3, 4, 8", "Üçgen oluşturma", "")
    assert diag1 is not None
    assert diag1.bug_id == "BUG-EUC-01"
    assert "EUCLIDEAN_TRIANGLE_INEQUALITY_VIOLATION" in diag1.category

    diag2 = detector.detect("a=8,b=3,c=4 => ucgen", "Üçgen çizimi", "")
    assert diag2 is not None
    assert diag2.bug_id == "BUG-EUC-01"


def test_bug_euc_02_inscribed_equals_central(detector):
    """BUG-EUC-02: Çevre açıyı merkez açıya eşit sayma hatası."""
    diag = detector.detect("cevre_aci = merkez_aci", "Çemberde açılar", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-02"
    assert "EUCLIDEAN_INSCRIBED_ANGLE_EQUALS_CENTRAL_ANGLE" in diag.category


def test_bug_euc_03_similarity_area_linear_ratio(detector):
    """BUG-EUC-03: Benzerlik oranını k iken alan oranını k² yerine k kabul etme yanılgısı."""
    diag = detector.detect("k = 2 => alan_orani = 2", "Benzer üçgenlerde alan", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-03"
    assert "EUCLIDEAN_SIMILARITY_AREA_RATIO_LINEAR_FALLACY" in diag.category


def test_bug_euc_04_euclidean_height_error(detector):
    """BUG-EUC-04: Öklid bağıntısında h² = p·k yerine dik kenarların çarpımını alma hatası."""
    diag = detector.detect("h^2 = b * c", "Öklid bağıntıları", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-04"
    assert "EUCLIDEAN_RIGHT_TRIANGLE_HEIGHT_RELATION_ERROR" in diag.category


def test_bug_euc_05_angle_bisector_equal_split(detector):
    """BUG-EUC-05: Genel üçgende iç açıortayın tabanı eşit ikiye böldüğü yanılgısı."""
    diag = detector.detect("aciortay => taban_esit", "Açıortay teoremi", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-05"
    assert "EUCLIDEAN_ANGLE_BISECTOR_RATIO_FALLACY" in diag.category


# ==============================================================================
# 6. ZERO FALSE POSITIVES & ZERO LEAKAGE
# ==============================================================================

def test_zero_false_positives_valid_euclidean(detector):
    """Geçerli Öklid geometri adımlarının yanlışlıkla hata sayılmadığını doğrular."""
    valid_steps = [
        ("h^2 = p * k", "Öklid teoremi"),
        ("cevre_aci = merkez_aci / 2", "Çemberde açılar"),
        ("k = 2 => alan_orani = 4", "Benzerlikte alan"),
        ("c / b = m / n", "İç açıortay teoremi"),
        ("a < b + c ve a > |b - c|", "Üçgen eşitsizliği"),
    ]
    for step, prev in valid_steps:
        diag = detector.detect(step, prev, "")
        assert diag is None, f"Geçerli adım '{step}' hatalı teşhis edildi: {diag.bug_id if diag else None}"


def test_zero_leakage_euclidean_advisor():
    """Akıllı ek çizim motorunun doğrudan sayısal sonucu sızdırmadığını doğrular."""
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "triangle",
        "properties": ["ikizkenar"],
        "goal": "kenar_uzunlugu_5",
    })
    # İpucu pedagojik bir yönlendirme olmalı, doğrudan bir sayısal yanıt veya kök vermemelidir.
    assert "5" not in hint["pedagogical_hint"]
    assert "yardımcı bir yükseklik" in hint["pedagogical_hint"]


# ==============================================================================
# 7. BOUNDARY & ERROR HANDLING
# ==============================================================================

def test_euclidean_relations_invalid_segments():
    with pytest.raises(ValueError, match="pozitif olmalıdır"):
        EuclideanRelations.height_from_segments(-2.0, 8.0)

    with pytest.raises(ValueError, match="Geçersiz parça"):
        EuclideanRelations.leg_from_segment_and_hypotenuse(30.0, 20.0)


def test_triangle2d_insufficient_data():
    t = Triangle2D(a=5.0)
    with pytest.raises(ValueError, match="Tüm kenarlar bilinmeden"):
        _ = t.perimeter
    with pytest.raises(ValueError, match="Yeterli veri yok"):
        _ = t.area


def test_triangle2d_invalid_altitude_side():
    t = Triangle2D(a=3.0, b=4.0, c=5.0)
    with pytest.raises(ValueError, match="bilinmiyor"):
        t.altitude_to_base("d")


def test_triangle2d_invalid_median_side():
    t = Triangle2D(a=3.0, b=4.0, c=5.0)
    with pytest.raises(ValueError, match="Geçersiz kenar"):
        t.median_to_base("x")


def test_advisor_default_fallback():
    hint = AuxiliaryConstructionAdvisor.suggest_construction({
        "type": "arbitrary_polygon",
        "properties": [],
    })
    assert hint["action"] == "OZEL_ACI_KARSISINA_DIKME_IN"
    assert "özel dik üçgen oluşturmayı dene" in hint["pedagogical_hint"]


def test_bug_euc_01_variant(detector):
    diag = detector.detect("3+4<8 => ucgen", "Üçgen oluşturma", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-01"


def test_bug_euc_03_variant(detector):
    diag = detector.detect("alanlar_orani = k", "Benzerlik", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-03"


def test_bug_euc_04_missing_square(detector):
    diag = detector.detect("h = p * k", "Öklid teoremi", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-04"


def test_bug_euc_05_inverted_ratio(detector):
    diag = detector.detect("c/b = n/m", "Açıortay bağıntısı", "")
    assert diag is not None
    assert diag.bug_id == "BUG-EUC-05"


def test_circle_cyclic_quadrilateral_sum():
    # Kirişler dörtgeninde karşılıklı açılar toplamı 180°
    angle_A = 75.0
    angle_C = 180.0 - angle_A
    assert angle_C == 105.0


def test_circle_inscribed_right_triangle_on_diameter():
    # Çapı gören çevre açı 90°'dir
    center_angle = 180.0
    inscribed_angle = center_angle / 2.0
    assert inscribed_angle == 90.0


# ==============================================================================
# 8. SOLVE PIPELINE, COGNITIVE MISTAKE VAULT & API ENDPOINTS
# ==============================================================================

def test_solve_synthetic_geometry_pipeline():
    """solve_synthetic_geometry fonksiyonunun tüm görevleri başarıyla çalıştırdığını doğrular."""
    # 1. triangle_solve
    res_tri = solve_synthetic_geometry("triangle_solve", a=3.0, b=4.0, c=5.0)
    assert res_tri["is_right_angled"] is True
    assert math.isclose(res_tri["area"], 6.0)
    assert math.isclose(res_tri["perimeter"], 12.0)

    # 2. euclidean_height
    res_h = solve_synthetic_geometry("euclidean_height", p=4.0, k=9.0)
    assert math.isclose(res_h["height"], 6.0)

    # 3. euclidean_leg
    res_leg = solve_synthetic_geometry("euclidean_leg", segment=9.0, hypotenuse=25.0)
    assert math.isclose(res_leg["leg"], 15.0)

    # 4. auxiliary_advisor
    res_adv = solve_synthetic_geometry(
        "auxiliary_advisor",
        configuration={"type": "triangle", "properties": ["ikizkenar"]},
    )
    assert res_adv["action"] == "TABANA_DIKME_INDIR"


def test_cognitive_mistake_vault_records_bug_euc_01_to_05(detector):
    """BUG-EUC-01..05 tespit edildiğinde Bilişsel Hata Kasası'na (N161-N185) kaydedildiğini doğrular."""
    from app.vault.mistake_vault import CognitiveMistakeVault, MistakeStatus

    vault = CognitiveMistakeVault(db_path=":memory:")
    student_id = "stu_euc_vault_01"

    test_cases = [
        ("BUG-EUC-01", "kenarlar = 3, 4, 8", "Üçgen oluşturma", "N162"),
        ("BUG-EUC-02", "cevre_aci = merkez_aci", "Çemberde açılar", "N178"),
        ("BUG-EUC-03", "k = 2 => alan_orani = 2", "Benzer üçgenlerde alan", "N169"),
        ("BUG-EUC-04", "h^2 = b * c", "Öklid bağıntıları", "N165"),
        ("BUG-EUC-05", "aciortay => taban_esit", "Açıortay teoremi", "N167"),
    ]

    for bug_id, step, context, expected_node in test_cases:
        diag = detector.detect(step, context, "")
        assert diag is not None
        assert diag.bug_id == bug_id

        record = vault.record_mistake(
            user_id=student_id,
            node_id=expected_node,
            bug_id=diag.bug_id,
            problem_statement=context,
            offending_step=step,
            correct_principle=diag.description,
            remediation_directive=diag.remediation_directive,
        )
        assert record.user_id == student_id
        assert record.node_id == expected_node
        assert record.bug_id == bug_id
        assert record.status == MistakeStatus.OPEN
        assert record.remediation_directive != ""

    records = vault.list_mistakes(student_id)
    assert len(records) == 5
    bug_ids = {r.bug_id for r in records}
    assert bug_ids == {"BUG-EUC-01", "BUG-EUC-02", "BUG-EUC-03", "BUG-EUC-04", "BUG-EUC-05"}


def test_api_solve_synthetic_geometry_valid_triangle():
    """POST /api/v1/geometry/synthetic/solve geçerli üçgen çözümü."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp = client.post(
        "/api/v1/geometry/synthetic/solve",
        json={
            "task": "triangle_solve",
            "params": {"a": 3.0, "b": 4.0, "c": 5.0},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["task"] == "triangle_solve"
    assert data["result_data"]["is_right_angled"] is True
    assert math.isclose(data["result_data"]["area"], 6.0)
    assert data["detected_bug"] is None
    assert data["vault_recorded"] is False


def test_api_solve_synthetic_geometry_with_misconception_and_vault():
    """POST /api/v1/geometry/synthetic/solve hata tespiti ve kasaya kayıt."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    student_id = "stu_euc_api_001"

    resp = client.post(
        "/api/v1/geometry/synthetic/solve",
        json={
            "task": "euclidean_height",
            "params": {"p": 4.0, "k": 9.0},
            "student_id": student_id,
            "problem_statement": "Öklid bağıntıları",
            "student_step": "h^2 = b * c",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["task"] == "euclidean_height"
    assert math.isclose(data["result_data"]["height"], 6.0)
    assert data["detected_bug"] is not None
    assert data["detected_bug"]["bug_id"] == "BUG-EUC-04"
    assert data["vault_recorded"] is True

    # Kasadan kontrol et
    vault_resp = client.get(f"/api/v1/vault/list/{student_id}")
    assert vault_resp.status_code == 200
    vault_records = vault_resp.json()
    assert len(vault_records) >= 1
    assert any(r["bug_id"] == "BUG-EUC-04" for r in vault_records)


def test_api_solve_synthetic_geometry_invalid_task():
    """POST /api/v1/geometry/synthetic/solve bilinmeyen görev için 400."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp = client.post(
        "/api/v1/geometry/synthetic/solve",
        json={
            "task": "unknown_parabola_task",
            "params": {},
        },
    )
    assert resp.status_code == 400
    assert "Bilinmeyen sentetik geometri görevi" in resp.json()["detail"]


