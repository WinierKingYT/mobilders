import pytest
import sympy as sp
from app.graph.knowledge_dag import KnowledgeDAG, CycleDetectedError
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.analytics.local_reporter import LocalAnalyticsReporter
from app.retention.fsrs import FSRSEngine


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
def mapper():
    return CurriculumOntologyRegistry()


# ==============================================================================
# 1. KNOWLEDGE GRAPH EXPANSION (N51 - N80)
# ==============================================================================

def test_dag_hedef3_total_nodes_80(dag):
    """Grafın en az 80 düğüm içerdiğini ve N51-N80 aralığının eksiksiz olduğunu doğrular."""
    assert len(dag.nodes) >= 80
    for i in range(51, 81):
        n_id = f"N{i:02d}"
        assert n_id in dag.nodes, f"Düğüm {n_id} eksik!"
        node = dag.get_node(n_id)
        assert node.title != ""
        assert node.canonical_code != ""
        assert node.level in {8, 9}
        assert -1.0 <= node.default_difficulty_b <= 3.0
        assert 1.0 <= node.discrimination_a <= 3.0


def test_dag_hedef3_prerequisites_integrity(dag):
    """N51-N80 düğümlerinin tüm önkoşullarının grafta var olduğunu doğrular."""
    for i in range(51, 81):
        n_id = f"N{i:02d}"
        node = dag.get_node(n_id)
        for prereq in node.strict_prereqs:
            assert prereq in dag.nodes, f"{n_id} düğümünün önkoşulu {prereq} grafta bulunamadı!"


def test_dag_hedef3_cycle_freedom_and_topological_sort(dag):
    """80+ düğümlük genişletilmiş grafın döngüsüz olduğunu ve Kahn sıralamasının geçerliliğini doğrular."""
    dag.assert_cycle_free()
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == len(dag.nodes)

    index_map = {n_id: idx for idx, n_id in enumerate(sorted_nodes)}
    for n_id, node in dag.nodes.items():
        for p in node.strict_prereqs:
            assert index_map[p] < index_map[n_id], f"{p} düğümü {n_id} düğümünden önce gelmeli!"


def test_dag_hedef3_zpd_progression(dag):
    """N01-N50 tamamlandığında N51 ve N66'nın ZPD adayları olduğunu doğrular."""
    mastered_core = {f"N{i:02d}" for i in range(1, 51)}
    zpd = dag.get_zpd_candidates(mastered_core)
    assert "N51" in zpd  # Yönlü Açılar (prereqs: N01, N05)
    assert "N66" in zpd  # Üstel Fonksiyon (prereqs: N08, N26)


# ==============================================================================
# 2. MULTI-CURRICULUM ONTOLOGY MAPPINGS (N51 - N80)
# ==============================================================================

def test_curriculum_mapper_trig_and_log(mapper):
    """MEB, IB DP ve AP Precalculus standartlarının N51-N80 için varlığını doğrular."""
    # MEB
    std_n51 = mapper.get_standard_for_node("N51", "MEB")
    assert std_n51 is not None
    assert std_n51.standard_id == "MEB-11.1.1.1"

    std_n66 = mapper.get_standard_for_node("N66", "MEB")
    assert std_n66 is not None
    assert std_n66.standard_id == "MEB-12.1.1.1"

    std_n69 = mapper.get_standard_for_node("N69", "MEB")
    assert std_n69 is not None
    assert std_n69.standard_id == "MEB-12.1.2.1"

    # IB DP
    std_n52 = mapper.get_standard_for_node("N52", "IB_AA")
    assert std_n52 is not None
    assert std_n52.standard_id == "IB-AA-SL-3.1"

    std_n60 = mapper.get_standard_for_node("N60", "IB_AA")
    assert std_n60 is not None
    assert std_n60.standard_id == "IB-AA-SL-3.5"

    std_n78 = mapper.get_standard_for_node("N78", "IB_AA")
    assert std_n78 is not None
    assert std_n78.standard_id == "IB-AA-SL-1.3"

    # AP Precalculus
    std_n55 = mapper.get_standard_for_node("N55", "AP_PRECALC")
    assert std_n55 is not None
    assert std_n55.standard_id == "AP-PRECALC-3.2"

    std_n72 = mapper.get_standard_for_node("N72", "AP_PRECALC")
    assert std_n72 is not None
    assert std_n72.standard_id == "AP-PRECALC-2.4"


# ==============================================================================
# 3. SYMPY CAS EXPANSION & DOMAIN CONSTRAINTS
# ==============================================================================

def test_cas_trig_identities(cas):
    """Trigonometrik temel özdeşliklerin CAS motoru tarafından doğrulandığını test eder."""
    assert cas.verify_trig_identity("sin(x)**2 + cos(x)**2", "1") is True
    assert cas.verify_trig_identity("sin(2*x)", "2*sin(x)*cos(x)") is True
    assert cas.verify_trig_identity("cos(2*x)", "cos(x)**2 - sin(x)**2") is True
    assert cas.verify_trig_identity("tan(x)", "sin(x)/cos(x)") is True
    assert cas.verify_trig_identity("sin(x)**2", "cos(x)**2") is False


def test_cas_log_equalities(cas):
    """Logaritma temel özelliklerinin CAS motoru tarafından doğrulandığını test eder."""
    assert cas.verify_log_equality("log(a) + log(b)", "log(a*b)") is True
    assert cas.verify_log_equality("log(a) - log(b)", "log(a/b)") is True
    assert cas.verify_log_equality("log(x**2)", "2*log(x)") is True
    assert cas.verify_log_equality("log(a) + log(b)", "log(a+b)") is False


def test_cas_domain_constraints_log_argument(cas):
    """Logaritma argümanının pozitiflik şartını evaluate_domain_constraints ile doğrular."""
    # x = 1 için log(x - 2) argümanı -1 <= 0 olduğu için reddedilmeli
    valid, reason = cas.evaluate_domain_constraints("log(x - 2)", "x", 1.0)
    assert valid is False
    assert "pozitif" in reason.lower()

    # x = 2 için log(x - 2) argümanı 0 olduğu için reddedilmeli
    valid, reason = cas.evaluate_domain_constraints("log(x - 2)", "x", 2.0)
    assert valid is False

    # x = 5 için log(x - 2) argümanı 3 > 0 olduğu için onaylanmalı
    valid, reason = cas.evaluate_domain_constraints("log(x - 2)", "x", 5.0)
    assert valid is True
    assert reason is None


def test_cas_domain_constraints_division_by_zero(cas):
    """Sıfıra bölme ve tanımsızlık durumlarının evaluate_domain_constraints ile yakalandığını doğrular."""
    valid, reason = cas.evaluate_domain_constraints("1 / (x - 3)", "x", 3.0)
    assert valid is False
    assert "tanımsız" in reason.lower()


# ==============================================================================
# 4. 10 NEW COGNITIVE BUGGY RULES (BUG-TRIG-01..05 & BUG-LOG-01..05)
# ==============================================================================

def test_bug_trig_01_linearity_trap(detector):
    """BUG-TRIG-01: sin(a+b) = sin a + sin b lineerlik tuzağını test eder."""
    res = detector.detect("sin(a+b) = sin(a) + sin(b)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-01"
    assert res.category == "TRIG_LINEARITY_TRAP"

    res_cos = detector.detect("cos(x+y) = cos(x) + cos(y)", "", "")
    assert res_cos is not None
    assert res_cos.bug_id == "BUG-TRIG-01"

    # Negatif test (Doğru açılım hata vermemeli)
    assert detector.detect("sin(a+b) = sin(a)*cos(b) + cos(a)*sin(b)", "", "") is None


def test_bug_trig_02_argument_cancellation(detector):
    """BUG-TRIG-02: sin(2x) = 2sin(x) veya sin(2x)/sin(x) = 2 argüman hatasını test eder."""
    res1 = detector.detect("sin(2x) = 2sin(x)", "", "")
    assert res1 is not None
    assert res1.bug_id == "BUG-TRIG-02"

    res2 = detector.detect("sin(2x)/sin(x) = 2", "", "")
    assert res2 is not None
    assert res2.bug_id == "BUG-TRIG-02"

    # Negatif test: Doğru yarım açı açılımı
    assert detector.detect("sin(2*x) = 2*sin(x)*cos(x)", "", "") is None


def test_bug_trig_03_axis_confusion(detector):
    """BUG-TRIG-03: Birim çemberde eksen kargaşası (tan = cos/sin veya apsis=sin)."""
    res1 = detector.detect("tan(x) = cos(x)/sin(x)", "", "")
    assert res1 is not None
    assert res1.bug_id == "BUG-TRIG-03"

    res2 = detector.detect("x = sin ve y = cos", "", "")
    assert res2 is not None
    assert res2.bug_id == "BUG-TRIG-03"

    # Negatif test
    assert detector.detect("tan(x) = sin(x)/cos(x)", "", "") is None


def test_bug_trig_04_root_and_period_loss(detector):
    """BUG-TRIG-04: Trigonometrik denklemde sadeleştirme ile kök kaybı veya tek açı yazma."""
    # Sadeleştirirken sin(x) = 0 köklerini silme
    res = detector.detect("cos(x) = 1", "sin(x)*cos(x) = sin(x)", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-04"

    # Tek açı verip diğer bölgeyi unutma
    res_angle = detector.detect("x = 30", "sin(x) = 1/2", "")
    assert res_angle is not None
    assert res_angle.bug_id == "BUG-TRIG-04"

    # Negatif test: İki kök veya çarpan ayrımı
    assert detector.detect("sin(x)*(cos(x) - 1) = 0", "sin(x)*cos(x) = sin(x)", "") is None


def test_bug_trig_05_parity_and_negative_angle(detector):
    """BUG-TRIG-05: cos(-x) = -cos(x) parite kargaşasını test eder."""
    res1 = detector.detect("cos(-x) = -cos(x)", "", "")
    assert res1 is not None
    assert res1.bug_id == "BUG-TRIG-05"

    res2 = detector.detect("sin(-x) = sin(x)", "", "")
    assert res2 is not None
    assert res2.bug_id == "BUG-TRIG-05"

    # Negatif test
    assert detector.detect("cos(-x) = cos(x)", "", "") is None
    assert detector.detect("sin(-x) = -sin(x)", "", "") is None


def test_bug_log_01_addition_distribution(detector):
    """BUG-LOG-01: log(a+b) = log(a) + log(b) dağılma tuzağını test eder."""
    res1 = detector.detect("log(a+b) = log(a) + log(b)", "", "")
    assert res1 is not None
    assert res1.bug_id == "BUG-LOG-01"

    res2 = detector.detect("log(a-b) = log(a)/log(b)", "", "")
    assert res2 is not None
    assert res2.bug_id == "BUG-LOG-01"

    # Negatif test
    assert detector.detect("log(a*b) = log(a) + log(b)", "", "") is None


def test_bug_log_02_multiplication_power_confusion(detector):
    """BUG-LOG-02: log(ab) = log a * log b veya (log x)^2 = 2log x yanılgısını test eder."""
    res1 = detector.detect("log(a*b) = log(a)*log(b)", "", "")
    assert res1 is not None
    assert res1.bug_id == "BUG-LOG-02"

    res2 = detector.detect("(log(x))^2 = 2*log(x)", "", "")
    assert res2 is not None
    assert res2.bug_id == "BUG-LOG-02"

    # Negatif test
    assert detector.detect("log(x**2) = 2*log(x)", "", "") is None


def test_bug_log_03_extraneous_root_negative_domain(detector):
    """BUG-LOG-03: Logaritmik denklemde tanım kümesini ihlal eden kökü kabul etme."""
    # log(x - 2) = 0 denkleminde öğrenci x = 1 bulursa (1 - 2 = -1 <= 0)
    res = detector.detect("x = 1", "log(x - 2) = 0", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-03"
    assert "argüman" in res.description.lower() or "negatif" in res.description.lower()

    # Negatif test: Geçerli kök (x = 3 => 3 - 2 = 1 > 0)
    assert detector.detect("x = 3", "log(x - 2) = 0", "") is None


def test_bug_log_04_change_of_base_division(detector):
    """BUG-LOG-04: log(a)/log(b) = log(a/b) taban değiştirme bölme hatasını test eder."""
    res = detector.detect("log(a)/log(b) = log(a/b)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-04"

    # Negatif test
    assert detector.detect("log(a) - log(b) = log(a/b)", "", "") is None


def test_bug_log_05_base_exponent_inversion(detector):
    """BUG-LOG-05: log_a(b) = c => b = c^a taban-üs tersliği hatasını test eder."""
    res = detector.detect("8 = 3^2", "log_2(8) = 3", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-05"

    res_symbolic = detector.detect("b = c^a", "log_a(b) = c", "")
    assert res_symbolic is not None
    assert res_symbolic.bug_id == "BUG-LOG-05"

    # Negatif test
    assert detector.detect("b = a**c", "log_a(b) = c", "") is None


# ==============================================================================
# 5. LOCAL ANALYTICS TOPOLOGY AND CURRICULUM GROUPS
# ==============================================================================

def test_local_reporter_trig_log_curriculum_groups(dag):
    """LocalAnalyticsReporter'ın N51-N65'i TRIGONOMETRY, N66-N80'i EXPONENTIAL_LOGARITHMIC olarak grupladığını teyit eder."""
    fsrs = FSRSEngine()
    reporter = LocalAnalyticsReporter(dag=dag, fsrs=fsrs)
    report = reporter.generate_student_report("EXP-TEST-STUDENT")

    atlas_nodes = {n["node_id"]: n for n in report["algebra_atlas"]["nodes"]}

    # Trigonometri düğümleri kontrolü
    for i in range(51, 66):
        n_id = f"N{i:02d}"
        assert n_id in atlas_nodes
        assert atlas_nodes[n_id]["curriculum_group"] == "TRIGONOMETRY"

    # Üstel ve Logaritma düğümleri kontrolü
    for i in range(66, 81):
        n_id = f"N{i:02d}"
        assert n_id in atlas_nodes
        assert atlas_nodes[n_id]["curriculum_group"] == "EXPONENTIAL_LOGARITHMIC"


# ==============================================================================
# 6. AST SECURITY AND PERMITTED SYMBOLS
# ==============================================================================

def test_ast_security_allowed_trig_symbols(cas):
    """Trigonometrik sembollerin güvenli AST içinde geçerli olduğunu doğrular."""
    assert cas.parse_to_sympy("sin(theta) + cos(alpha)") is not None
    assert cas.parse_to_sympy("tan(beta)") is not None
    assert cas.parse_to_sympy("exp(x)") is not None
    assert cas.parse_to_sympy("ln(x)") is not None


def test_ast_security_rejects_malicious_calls(cas):
    """AST'nin zararlı veya izinsiz çağrıları engellediğini doğrular."""
    with pytest.raises(SecurityViolationError):
        cas.sanitize_and_validate_ast("__import__('os').system('dir')")

    with pytest.raises(SecurityViolationError):
        cas.sanitize_and_validate_ast("open('/etc/passwd')")


def test_cas_compound_angles(cas):
    """Toplam ve fark formüllerinin CAS doğrulamalarını test eder."""
    assert cas.verify_trig_identity("sin(x - y)", "sin(x)*cos(y) - cos(x)*sin(y)") is True
    assert cas.verify_trig_identity("cos(x + y)", "cos(x)*cos(y) - sin(x)*sin(y)") is True
    assert cas.verify_trig_identity("cos(x - y)", "cos(x)*cos(y) + sin(x)*sin(y)") is True


def test_cas_reduction_identities(cas):
    """İndirgeme formüllerinin simetrisini test eder."""
    assert cas.verify_trig_identity("sin(pi - x)", "sin(x)") is True
    assert cas.verify_trig_identity("cos(pi - x)", "-cos(x)") is True
    assert cas.verify_trig_identity("sin(pi/2 - x)", "cos(x)") is True
    assert cas.verify_trig_identity("cos(pi/2 - x)", "sin(x)") is True


def test_cas_log_change_of_base(cas):
    """Taban değiştirme kuralı eşitliğini test eder."""
    # log(b)/log(a) eşitliğini verify_log_equality ile sına
    assert cas.verify_log_equality("log(x) / log(2)", "log(x) / log(2)") is True
    assert cas.verify_log_equality("ln(x) / ln(10)", "ln(x) / ln(10)") is True


def test_cas_domain_constraints_various_cases(cas):
    """Farklı tanım kümesi durumlarını test eder."""
    # Negatif taban
    ok, reason = cas.evaluate_domain_constraints("log(x)", "x", -3.0)
    assert ok is False
    assert "pozitif" in reason.lower()

    # Sıfır taban/argüman
    ok, reason = cas.evaluate_domain_constraints("log(x)", "x", 0.0)
    assert ok is False

    # Karekök içi negatif
    ok, reason = cas.evaluate_domain_constraints("sqrt(x - 5)", "x", 2.0)
    assert ok is False
    assert "karekök" in reason.lower()

    # Karekök içi geçerli
    ok, reason = cas.evaluate_domain_constraints("sqrt(x - 5)", "x", 6.0)
    assert ok is True


def test_bug_trig_01_tan_sum_distribution(detector):
    """BUG-TRIG-01 tan(a+b) dağılma tuzağını test eder."""
    res = detector.detect("tan(a+b) = tan(a) + tan(b)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-01"


def test_bug_trig_02_cos_argument_cancellation(detector):
    """BUG-TRIG-02 cos(2x) = 2cos(x) argüman hatasını test eder."""
    res = detector.detect("cos(2x) = 2cos(x)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-02"


def test_bug_trig_03_cotangent_axis_confusion(detector):
    """BUG-TRIG-03 cot(x) = sin(x)/cos(x) kargaşasını test eder."""
    res = detector.detect("cot(x) = sin(x)/cos(x)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-03"


def test_bug_trig_04_cancellation_root_loss_tan(detector):
    """BUG-TRIG-04 tan(x)*sin(x) = sin(x) ifadesinde sin(x)'e bölüp sin(x)=0 kökünü silme."""
    res = detector.detect("tan(x) = 1", "tan(x)*sin(x) = sin(x)", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-04"


def test_bug_trig_05_negative_theta_parity(detector):
    """BUG-TRIG-05 cos(-theta) = -cos(theta) parite hatasını test eder."""
    res = detector.detect("cos(-theta) = -cos(theta)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-TRIG-05"


def test_bug_log_01_natural_log_distribution(detector):
    """BUG-LOG-01 ln(x+y) = ln(x) + ln(y) hatasını test eder."""
    res = detector.detect("ln(x+y) = ln(x) + ln(y)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-01"


def test_bug_log_02_natural_log_multiplication(detector):
    """BUG-LOG-02 ln(ab) = ln(a)*ln(b) hatasını test eder."""
    res = detector.detect("ln(ab) = ln(a)*ln(b)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-02"


def test_bug_log_03_multiple_extraneous_roots(detector):
    """BUG-LOG-03 Birden fazla kök içinde negatif argüman yaratanı yakalama."""
    # Denklem: log(x - 5) = 0, Öğrenci: Ç = {1, 6} -> x = 1 tanımsız yapar
    res = detector.detect("Ç = {1, 6}", "log(x - 5) = 0", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-03"


def test_bug_log_04_natural_log_change_of_base(detector):
    """BUG-LOG-04 ln(a)/ln(b) = ln(a/b) hatasını test eder."""
    res = detector.detect("ln(a)/ln(b) = ln(a/b)", "", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-04"


def test_bug_log_05_symbolic_base_exponent(detector):
    """BUG-LOG-05 a = b^c taban-kuvvet tersliği test eder."""
    res = detector.detect("a = b^c", "log_a(b) = c", "")
    assert res is not None
    assert res.bug_id == "BUG-LOG-05"


def test_zero_false_positives_advanced_battery(detector):
    """Geniş bir geçerli cebirsel adımlar bataryasında sıfır False Positive doğrulaması."""
    valid_steps = [
        ("cos(2*x) = 2*cos(x)**2 - 1", ""),
        ("cos(2*x) = 1 - 2*sin(x)**2", ""),
        ("tan(x) = sin(x)/cos(x)", ""),
        ("cot(x) = cos(x)/sin(x)", ""),
        ("cos(-x) = cos(x)", ""),
        ("sin(-x) = -sin(x)", ""),
        ("log(a*b) = log(a) + log(b)", ""),
        ("log(a/b) = log(a) - log(b)", ""),
        ("log(x**3) = 3*log(x)", ""),
        ("b = a**c", "log_a(b) = c"),
        ("x = 7", "log(x - 2) = 0"),
        ("sin(x)*(cos(x) - 1) = 0", "sin(x)*cos(x) = sin(x)"),
    ]
    for user_step, prev_step in valid_steps:
        diag = detector.detect(user_step, prev_step, "")
        assert diag is None, f"Geçerli adım '{user_step}' için yanlış hata tespit edildi: {diag.bug_id}"


def test_law_of_cosines_cas_computation(cas):
    """Kosinüs teoremi ile kenar hesaplama adımlarını doğrular: c^2 = a^2 + b^2 - 2ab*cos(C)."""
    # a = 3, b = 5, C = 60 derece (pi/3) -> c^2 = 9 + 25 - 30*0.5 = 19
    c_squared_expr = "3**2 + 5**2 - 2*3*5*cos(pi/3)"
    res = cas.parse_to_sympy(c_squared_expr)
    assert sp.simplify(res) == 19


def test_law_of_sines_area_cas_computation(cas):
    """Sinüslü alan formülü adımlarını doğrular: Alan = (1/2)*a*b*sin(C)."""
    # a = 4, b = 6, C = 30 derece (pi/6) -> Alan = 0.5 * 24 * 0.5 = 6
    area_expr = "(1/2) * 4 * 6 * sin(pi/6)"
    res = cas.parse_to_sympy(area_expr)
    assert sp.simplify(res) == 6


def test_exponential_growth_decay_cas(cas):
    """Üstel büyüme modelini doğrular."""
    # 100 * 2^3 = 800
    res = cas.parse_to_sympy("100 * 2**3")
    assert sp.simplify(res) == 800


def test_domain_constraints_log_base_one(cas):
    """Logaritma tabanının 1 olamayacağını evaluate_domain_constraints ile doğrular."""
    # log_1(5) geçersizdir
    valid, reason = cas.evaluate_domain_constraints("log(5, x)", "x", 1.0)
    assert valid is False
    assert "taban" in reason.lower() or "tanımsız" in reason.lower()


def test_domain_constraints_log_base_negative(cas):
    """Logaritma tabanının negatif olamayacağını evaluate_domain_constraints ile doğrular."""
    valid, reason = cas.evaluate_domain_constraints("log(5, x)", "x", -2.0)
    assert valid is False


def test_tan_singularity_domain_constraints(cas):
    """tan(pi/2) gibi tanımsızlıkların evaluate_domain_constraints ile yakalandığını doğrular."""
    valid, reason = cas.evaluate_domain_constraints("tan(x)", "x", float(sp.pi / 2))
    assert valid is False


def test_double_angle_tan_identity(cas):
    """Tanjant yarım açı formülünün doğruluğunu test eder."""
    assert cas.verify_trig_identity("tan(2*x)", "(2*tan(x)) / (1 - tan(x)**2)") is True


def test_natural_log_e_identity(cas):
    """Doğal logaritma e özelliklerini test eder: ln(e) = 1."""
    res = cas.parse_to_sympy("ln(e)")
    assert sp.simplify(res) == 1


