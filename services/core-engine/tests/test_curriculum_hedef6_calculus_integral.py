"""
Hedef 6: Kalkülüs II — İntegral ve Alan Hesabı Test Paketi (N111 - N135).
50 Kapsamlı Test:
1. Knowledge DAG Yapısı, Önkoşul Bütünlüğü ve Topolojik Sıralama (N111-N135).
2. Uluslararası Müfredat Eşleştirmesi (MEB, AP Calculus, IB DP AA).
3. Sembolik CAS İntegral & Riemann Motoru (Belirsiz, Belirli, Eğriler Arası Alan, Riemann Toplamları).
4. Bilişsel Kavram Yanılgıları (BUG-INT-01'den BUG-INT-10'a) ve SIFIR YANLIŞ POZİTİF (ZERO FALSE POSITIVES).
5. Bilişsel Atlas & Yerel Analitik Raporlama (CALCULUS_INTEGRAL grubu).
"""

import pytest
import sympy as sp
from app.graph.knowledge_dag import KnowledgeDAG, KnowledgeNode
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.analytics.local_reporter import LocalAnalyticsReporter


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
def registry():
    return CurriculumOntologyRegistry()


@pytest.fixture
def reporter(dag):
    return LocalAnalyticsReporter(dag=dag)


# ==============================================================================
# 1. KNOWLEDGE DAG STRUCTURE & PREREQUISITES (N111 - N135)
# ==============================================================================

def test_dag_hedef6_total_nodes_135(dag):
    """Grafın 135 düğüm içerdiğini ve N111-N135 aralığının eksiksiz tanımlandığını doğrular."""
    assert len(dag.nodes) == 135
    for i in range(111, 136):
        n_id = f"N{i}"
        assert n_id in dag.nodes, f"Düğüm {n_id} eksik!"
        node = dag.get_node(n_id)
        assert node.title != ""
        assert node.canonical_code != ""
        assert node.level in {13, 14}
        assert -1.0 <= node.default_difficulty_b <= 3.0
        assert 1.0 <= node.discrimination_a <= 3.0


def test_dag_hedef6_prerequisites_integrity(dag):
    """N111-N135 düğümlerinin tüm önkoşullarının grafta var olduğunu doğrular."""
    for i in range(111, 136):
        n_id = f"N{i}"
        node = dag.get_node(n_id)
        assert len(node.strict_prereqs) > 0, f"{n_id} önkoşulsuz tanımlanamaz!"
        for prereq in node.strict_prereqs:
            assert prereq in dag.nodes, f"{n_id} düğümünün önkoşulu {prereq} grafta bulunamadı!"


def test_dag_hedef6_cycle_freedom_and_topological_sort(dag):
    """135 düğümlük grafın döngüsüz olduğunu ve Kahn sıralamasının geçerliliğini doğrular."""
    dag.assert_cycle_free()
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == len(dag.nodes)

    index_map = {n_id: idx for idx, n_id in enumerate(sorted_nodes)}
    for n_id, node in dag.nodes.items():
        for p in node.strict_prereqs:
            assert index_map[p] < index_map[n_id], f"{p} düğümü {n_id} düğümünden önce gelmeli!"


def test_dag_hedef6_seviye13_indefinite_integral_nodes(dag):
    """Seviye 13 düğümlerinin (N111-N122: Belirsiz İntegral & Yöntemler) hiyerarşisini doğrular."""
    level13_nodes = [dag.get_node(f"N{i}") for i in range(111, 123)]
    assert len(level13_nodes) == 12
    for node in level13_nodes:
        assert node.level == 13
        assert "math.calc" in node.canonical_code


def test_dag_hedef6_seviye14_definite_integral_area_nodes(dag):
    """Seviye 14 düğümlerinin (N123-N135: Belirli İntegral & Alan Hesabı) hiyerarşisini doğrular."""
    level14_nodes = [dag.get_node(f"N{i}") for i in range(123, 136)]
    assert len(level14_nodes) == 13
    for node in level14_nodes:
        assert node.level == 14
        assert "math.calc" in node.canonical_code


def test_dag_hedef6_zpd_progression_integral(dag):
    """Türev düğümlerini (N81-N110) tamamlayan bir öğrencinin ZPD'sine N111 girmelidir."""
    mastered = {f"N{i:02d}" if i < 100 else f"N{i}" for i in range(1, 111)}
    zpd = dag.get_zpd_candidates(mastered)
    assert "N111" in zpd


# ==============================================================================
# 2. MULTI-CURRICULUM ONTOLOGY MAPPER (MEB, AP CALC, IB AA)
# ==============================================================================

def test_curriculum_meb_integral_standards(registry):
    """MEB 12. Sınıf İntegral kazanımlarının varlığını doğrular."""
    meb_n111 = registry.get_standard_for_node("N111", "MEB")
    assert meb_n111 is not None
    assert meb_n111.standard_id == "MEB-12.7.1.1"
    assert "İntegral" in meb_n111.title_tr

    meb_n123 = registry.get_standard_for_node("N123", "MEB")
    assert meb_n123 is not None
    assert meb_n123.standard_id == "MEB-12.7.3.1"
    assert "Riemann" in meb_n123.title_tr

    meb_n129 = registry.get_standard_for_node("N129", "MEB")
    assert meb_n129 is not None
    assert meb_n129.standard_id == "MEB-12.7.4.1"
    assert "Alan" in meb_n129.title_tr


def test_curriculum_ap_calculus_integral_standards(registry):
    """AP Calculus AB/BC Unit 6, 7, 8 integral standartlarının varlığını doğrular."""
    ap_n111 = registry.get_standard_for_node("N111", "AP_CALC")
    assert ap_n111 is not None
    assert ap_n111.standard_id == "AP-CALC-6.7"

    ap_n123 = registry.get_standard_for_node("N123", "AP_CALC")
    assert ap_n123 is not None
    assert ap_n123.standard_id == "AP-CALC-6.2"

    ap_n129 = registry.get_standard_for_node("N129", "AP_CALC")
    assert ap_n129 is not None
    assert ap_n129.standard_id == "AP-CALC-8.4"


def test_curriculum_ib_aa_integral_standards(registry):
    """IB DP Mathematics Analysis & Approaches Topic 5 integral standartlarını doğrular."""
    ib_n117 = registry.get_standard_for_node("N117", "IB_AA")
    assert ib_n117 is not None
    assert ib_n117.standard_id == "IB-AA-SL-5.12"

    ib_n119 = registry.get_standard_for_node("N119", "IB_AA")
    assert ib_n119 is not None
    assert ib_n119.standard_id == "IB-AA-HL-5.13"

    ib_n126 = registry.get_standard_for_node("N126", "IB_AA")
    assert ib_n126 is not None
    assert ib_n126.standard_id == "IB-AA-SL-5.11"


# ==============================================================================
# 3. CAS SEMBOLİK İNTEGRAL & RIEMANN MOTORU
# ==============================================================================

def test_cas_indefinite_integral_polynomial(cas):
    """Polinom integrali: ∫ (3x^2 + 2x + 1) dx = x^3 + x^2 + x + C."""
    res = cas.compute_indefinite_integral("3*x**2 + 2*x + 1")
    expected = sp.sympify("x**3 + x**2 + x + C", locals=cas.symbols)
    assert sp.simplify(res - expected) == 0


def test_cas_indefinite_integral_trigonometric(cas):
    """Trigonometrik integral: ∫ cos(x) dx = sin(x) + C."""
    res = cas.compute_indefinite_integral("cos(x)")
    expected = sp.sympify("sin(x) + C", locals=cas.symbols)
    assert sp.simplify(res - expected) == 0


def test_cas_indefinite_integral_reciprocal_log(cas):
    """Ters fonksiyon integrali: ∫ 1/x dx = ln|x| + C."""
    res = cas.compute_indefinite_integral("1/x")
    assert "log(x)" in str(res) or "ln(x)" in str(res)


def test_cas_indefinite_integral_exponential(cas):
    """Üstel fonksiyon integrali: ∫ e^x dx = e^x + C."""
    res = cas.compute_indefinite_integral("e**x")
    assert "exp(x)" in str(res) or "e**x" in str(res)


def test_cas_definite_integral_polynomial(cas):
    """Belirli integral: ∫_0^3 x^2 dx = 9."""
    exact, val = cas.compute_definite_integral("x**2", var="x", a=0, b=3)
    assert exact == 9
    assert val == 9.0


def test_cas_definite_integral_trigonometric(cas):
    """Belirli integral: ∫_0^pi sin(x) dx = 2."""
    exact, val = cas.compute_definite_integral("sin(x)", var="x", a=0, b="pi")
    assert exact == 2
    assert val == 2.0


def test_cas_definite_integral_reversed_limits(cas):
    """Sınırların ters çevrilmesi: ∫_3^0 x^2 dx = -9."""
    exact, val = cas.compute_definite_integral("x**2", var="x", a=3, b=0)
    assert exact == -9
    assert val == -9.0


def test_cas_area_between_curves_standard(cas):
    """y = x ve y = x^2 arasında [0, 1] alan: 1/6."""
    area = cas.compute_area_between_curves("x", "x**2", 0, 1)
    assert abs(area - 1/6) < 1e-6


def test_cas_area_between_curves_order_invariant(cas):
    """Eğrilerin sırası ters verilse bile alan mutlak farktır ve pozitif kalır."""
    area = cas.compute_area_between_curves("x**2", "x", 0, 1)
    assert area > 0
    assert abs(area - 1/6) < 1e-6


def test_cas_verify_integral_correct(cas):
    """Ters türev doğrulaması: (x^3 + C)' = 3x^2."""
    assert cas.verify_integral("3*x**2", "x**3 + C") is True


def test_cas_verify_integral_incorrect(cas):
    """Yanlış ters türev doğrulaması."""
    assert cas.verify_integral("3*x**2", "x**2 + C") is False


def test_cas_riemann_sum_left_convergence(cas):
    """Sol Riemann toplamı n=4 ve n=100 yakınsaması: ∫_0^1 x^2 dx = 1/3."""
    r4 = cas.compute_riemann_sum("x**2", 0, 1, 4, method="left")
    r100 = cas.compute_riemann_sum("x**2", 0, 1, 100, method="left")
    exact = 1.0 / 3.0
    assert abs(r100 - exact) < abs(r4 - exact)
    assert abs(r100 - exact) < 0.01


def test_cas_riemann_sum_right_overestimate(cas):
    """Artan fonksiyon f(x)=x^2 için sağ Riemann toplamı üstten tahmin verir."""
    r_right = cas.compute_riemann_sum("x**2", 0, 1, 10, method="right")
    assert r_right > (1.0 / 3.0)


def test_cas_riemann_sum_midpoint_exactness(cas):
    """Doğrusal fonksiyonda orta nokta Riemann toplamı tam integrali verir."""
    r_mid = cas.compute_riemann_sum("x", 0, 2, 4, method="midpoint")
    assert abs(r_mid - 2.0) < 1e-9


# ==============================================================================
# 4. BİLİŞSEL KAVRAM YANILGILARI (BUG-INT-01..10) & ZERO FALSE POSITIVES
# ==============================================================================

# --- BUG-INT-01: +C Unutulması ---
def test_bug_int_01_detected_explicit(detector):
    diag = detector.detect(
        user_step_str="+C ye gerek yok",
        previous_step_str="integrate(x**2, x)",
        target_equation_str="x**3/3 + C",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-01"


def test_bug_int_01_detected_missing_c_antiderivative(detector):
    diag = detector.detect(
        user_step_str="x^2/2",
        previous_step_str="integrate(x, x)",
        target_equation_str="x^2/2 + C",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-01"


def test_bug_int_01_zero_false_positive_with_c(detector):
    diag = detector.detect(
        user_step_str="x^2/2 + C",
        previous_step_str="integrate(x, x)",
        target_equation_str="x^2/2 + C",
    )
    assert diag is None or diag.bug_id != "BUG-INT-01"


def test_bug_int_01_zero_false_positive_definite_integral(detector):
    diag = detector.detect(
        user_step_str="1/2",
        previous_step_str="integrate(x, (x, 0, 1))",
        target_equation_str="1/2",
    )
    assert diag is None or diag.bug_id != "BUG-INT-01"


# --- BUG-INT-02: u-ikamesinde diferansiyel ihmali ---
def test_bug_int_02_detected_direct(detector):
    diag = detector.detect(
        user_step_str="(2x+1)^4/4",
        previous_step_str="integrate((2x+1)^3, x)",
        target_equation_str="(2x+1)^4/8 + C",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-02"


def test_bug_int_02_detected_du_dx(detector):
    diag = detector.detect(
        user_step_str="u = 2x+1 ve du = dx",
        previous_step_str="integrate(2x+1, x)",
        target_equation_str="u^2/4 + C",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-02"


def test_bug_int_02_zero_false_positive_correct_factor(detector):
    diag = detector.detect(
        user_step_str="(2x+1)^4/8 + C",
        previous_step_str="integrate((2x+1)^3, x)",
        target_equation_str="(2x+1)^4/8 + C",
    )
    assert diag is None or diag.bug_id != "BUG-INT-02"


# --- BUG-INT-03: Belirli integral sınır sırasını ters çıkarma ---
def test_bug_int_03_detected_f_a_minus_f_b(detector):
    diag = detector.detect(
        user_step_str="F(a) - F(b)",
        previous_step_str="integrate(f(x), (x, a, b))",
        target_equation_str="F(b) - F(a)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-03"


def test_bug_int_03_detected_alt_eksi_ust(detector):
    diag = detector.detect(
        user_step_str="altsinir - ustsinir",
        previous_step_str="integrate(f(x), (x, 0, 1))",
        target_equation_str="F(1) - F(0)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-03"


def test_bug_int_03_zero_false_positive_correct_order(detector):
    diag = detector.detect(
        user_step_str="F(b) - F(a)",
        previous_step_str="integrate(f(x), (x, a, b))",
        target_equation_str="F(b) - F(a)",
    )
    assert diag is None or diag.bug_id != "BUG-INT-03"


# --- BUG-INT-04: Negatif belirli integrali doğrudan alan kabul etme ---
def test_bug_int_04_detected(detector):
    diag = detector.detect(
        user_step_str="Alan = -4 br^2",
        previous_step_str="Eğri x-ekseninin altında kalıyor",
        target_equation_str="Alan = 4 br^2",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-04"


def test_bug_int_04_detected_negative_value(detector):
    diag = detector.detect(
        user_step_str="alan=-6",
        previous_step_str="integrate(x-3, (x, 0, 2))",
        target_equation_str="alan=6",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-04"


def test_bug_int_04_zero_false_positive_positive_area(detector):
    diag = detector.detect(
        user_step_str="Alan = 4 br^2",
        previous_step_str="integrate(x, (x, 0, 2))",
        target_equation_str="Alan = 4 br^2",
    )
    assert diag is None or diag.bug_id != "BUG-INT-04"


# --- BUG-INT-05: Kısmi integrasyon işaret hatası ---
def test_bug_int_05_detected(detector):
    diag = detector.detect(
        user_step_str="uv + int(vdu)",
        previous_step_str="integrate(u*dv)",
        target_equation_str="uv - int(vdu)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-05"


def test_bug_int_05_zero_false_positive_correct_formula(detector):
    diag = detector.detect(
        user_step_str="u*v - int(v*du)",
        previous_step_str="integrate(u*dv)",
        target_equation_str="u*v - int(v*du)",
    )
    assert diag is None or diag.bug_id != "BUG-INT-05"


# --- BUG-INT-06: 1/x integralinde kuvvet kuralı uygulama ---
def test_bug_int_06_detected(detector):
    diag = detector.detect(
        user_step_str="int(1/x) = x^0/0 + C",
        previous_step_str="integrate(1/x, x)",
        target_equation_str="ln|x| + C",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-06"


def test_bug_int_06_zero_false_positive_log(detector):
    diag = detector.detect(
        user_step_str="ln|x| + C",
        previous_step_str="integrate(1/x, x)",
        target_equation_str="ln|x| + C",
    )
    assert diag is None or diag.bug_id != "BUG-INT-06"


# --- BUG-INT-07: Belirli integral u-ikamesinde sınırları güncellememe ---
def test_bug_int_07_detected(detector):
    diag = detector.detect(
        user_step_str="u degiskenine gecildi ama sinirlar ayni",
        previous_step_str="integrate(2x*(x^2+1), (x, 0, 1))",
        target_equation_str="integrate(u, (u, 1, 2))",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-07"


def test_bug_int_07_detected_sinirlar_degismez(detector):
    diag = detector.detect(
        user_step_str="sinirlardegismez",
        previous_step_str="u-ikamesi",
        target_equation_str="sinirlar guncellenir",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-07"


# --- BUG-INT-08: İki eğri arası alanda alt - üst çıkarma ---
def test_bug_int_08_detected(detector):
    diag = detector.detect(
        user_step_str="alan = int(alt - ust)",
        previous_step_str="f(x) üstte, g(x) altta",
        target_equation_str="alan = int(ust - alt)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-08"


def test_bug_int_08_detected_reversed_function_order(detector):
    diag = detector.detect(
        user_step_str="alan = int(g - f)",
        previous_step_str="f > g olduğu biliniyor",
        target_equation_str="alan = int(f - g)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-08"


# --- BUG-INT-09: İntegralin çarpma üzerine dağılması ---
def test_bug_int_09_detected(detector):
    diag = detector.detect(
        user_step_str="int(f*g) = int(f) * int(g)",
        previous_step_str="integrate(f*g, x)",
        target_equation_str="by parts veya substitution",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-09"


def test_bug_int_09_detected_polynomial_exponential(detector):
    diag = detector.detect(
        user_step_str="(x^2/2) * e^x",
        previous_step_str="integrate(x * e^x, x)",
        target_equation_str="x*e^x - e^x + C",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-09"


def test_bug_int_09_zero_false_positive_by_parts(detector):
    diag = detector.detect(
        user_step_str="x*e^x - e^x + C",
        previous_step_str="integrate(x * e^x, x)",
        target_equation_str="x*e^x - e^x + C",
    )
    assert diag is None or diag.bug_id != "BUG-INT-09"


# --- BUG-INT-10: FTC 1 Zincir kuralı ihmali ---
def test_bug_int_10_detected(detector):
    diag = detector.detect(
        user_step_str="d/dx int_a^g(x) = f(g(x))",
        previous_step_str="FTC 1 kuralı",
        target_equation_str="f(g(x)) * g'(x)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-10"


def test_bug_int_10_detected_upper_limit_x2(detector):
    diag = detector.detect(
        user_step_str="d/dx(int_0^(x^2)) = sin(x^2)",
        previous_step_str="d/dx int_0^(x^2) sin(t) dt",
        target_equation_str="2*x * sin(x^2)",
    )
    assert diag is not None
    assert diag.bug_id == "BUG-INT-10"


def test_bug_int_10_zero_false_positive_with_derivative(detector):
    diag = detector.detect(
        user_step_str="2*x * sin(x^2)",
        previous_step_str="d/dx int_0^(x^2) sin(t) dt",
        target_equation_str="2*x * sin(x^2)",
    )
    assert diag is None or diag.bug_id != "BUG-INT-10"


# ==============================================================================
# 5. COGNITIVE ATLAS & LOCAL ANALYTICS INTEGRATION
# ==============================================================================

def test_analytics_reporter_calculus_integral_group(dag):
    """LocalAnalyticsReporter CALCULUS_INTEGRAL grubunun N111-N135 düğümlerini içerdiğini doğrular."""
    reporter = LocalAnalyticsReporter(dag=dag)
    report = reporter.generate_student_report("INT-STUDENT-01")

    atlas = report["algebra_atlas"]
    assert atlas["total_nodes"] == len(dag.nodes)

    node_groups = {n["node_id"]: n["curriculum_group"] for n in atlas["nodes"]}
    assert node_groups["N111"] == "CALCULUS_INTEGRAL"
    assert node_groups["N122"] == "CALCULUS_INTEGRAL"
    assert node_groups["N123"] == "CALCULUS_INTEGRAL"
    assert node_groups["N135"] == "CALCULUS_INTEGRAL"
