"""
Curriculum Phase C: Calculus I (Limit, Continuity, Derivatives) Test Suite (N81 - N110).
Contains 50 exhaustive tests verifying:
1. Knowledge DAG structure, cycle freedom, topological sort, and ZPD progression (N81-N110).
2. Multi-curriculum alignment across MEB, AP Calculus (AB/BC), and IB DP (AA SL/HL).
3. Symbolic CAS Calculus Engine (limits, differentiation, tangent lines, continuity).
4. Misconceptions & Buggy Rules (BUG-CALC-01 to BUG-CALC-10) with ZERO FALSE POSITIVES.
5. Cognitive Atlas & Local Analytics reporting for Calculus groups.
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


# ==============================================================================
# 1. KNOWLEDGE DAG STRUCTURE & PREREQUISITES (N81 - N110)
# ==============================================================================

def test_dag_hedef4_total_nodes_110(dag):
    """Grafın en az 110 düğüm içerdiğini ve N81-N110 aralığının eksiksiz olduğunu doğrular."""
    assert len(dag.nodes) >= 110
    for i in range(81, 111):
        n_id = f"N{i:02d}" if i < 100 else f"N{i}"
        assert n_id in dag.nodes, f"Düğüm {n_id} eksik!"
        node = dag.get_node(n_id)
        assert node.title != ""
        assert node.canonical_code != ""
        assert node.level in {10, 11, 12}
        assert -1.0 <= node.default_difficulty_b <= 3.0
        assert 1.0 <= node.discrimination_a <= 3.0


def test_dag_hedef4_prerequisites_integrity(dag):
    """N81-N110 düğümlerinin tüm önkoşullarının grafta var olduğunu doğrular."""
    for i in range(81, 111):
        n_id = f"N{i:02d}" if i < 100 else f"N{i}"
        node = dag.get_node(n_id)
        for prereq in node.strict_prereqs:
            assert prereq in dag.nodes, f"{n_id} düğümünün önkoşulu {prereq} grafta bulunamadı!"


def test_dag_hedef4_cycle_freedom_and_topological_sort(dag):
    """110 düğümlük grafın döngüsüz olduğunu ve Kahn sıralamasının geçerliliğini doğrular."""
    dag.assert_cycle_free()
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == len(dag.nodes)

    index_map = {n_id: idx for idx, n_id in enumerate(sorted_nodes)}
    for n_id, node in dag.nodes.items():
        for p in node.strict_prereqs:
            assert index_map[p] < index_map[n_id], f"{p} düğümü {n_id} düğümünden önce gelmeli!"


def test_dag_hedef4_seviye10_limit_continuity_nodes(dag):
    """Seviye 10 düğümlerinin (N81-N88: Limit & Süreklilik) hiyerarşisini doğrular."""
    assert dag.get_node("N81").level == 10  # math.calc.limit_intuitive
    assert "N26" in dag.get_node("N81").strict_prereqs
    assert dag.get_node("N82").level == 10  # math.calc.limit_algebraic
    assert "N81" in dag.get_node("N82").strict_prereqs
    assert dag.get_node("N83").level == 10  # math.calc.limit_zero_over_zero
    assert "N47" in dag.get_node("N83").strict_prereqs  # Polinom çarpan teoremi
    assert dag.get_node("N87").level == 10  # math.calc.continuity_definition
    assert "N81" in dag.get_node("N87").strict_prereqs
    assert dag.get_node("N88").level == 10  # math.calc.continuity_theorems (IVT)


def test_dag_hedef4_seviye11_derivative_rules_nodes(dag):
    """Seviye 11 düğümlerinin (N89-N98: Türev Alma Kuralları) hiyerarşisini doğrular."""
    assert dag.get_node("N89").level == 11  # math.calc.derivative_limit_definition
    assert "N83" in dag.get_node("N89").strict_prereqs
    assert dag.get_node("N90").level == 11  # math.calc.power_rule_polynomials
    assert dag.get_node("N91").level == 11  # math.calc.product_rule
    assert dag.get_node("N92").level == 11  # math.calc.quotient_rule
    assert dag.get_node("N94").level == 11  # math.calc.chain_rule
    assert "N92" in dag.get_node("N94").strict_prereqs
    assert dag.get_node("N95").level == 11  # math.calc.derivative_trig
    assert "N53" in dag.get_node("N95").strict_prereqs  # Trigonometri
    assert dag.get_node("N96").level == 11  # math.calc.derivative_exp_log
    assert "N68" in dag.get_node("N96").strict_prereqs  # e^x
    assert dag.get_node("N98").level == 11  # math.calc.lhopital_rule


def test_dag_hedef4_seviye12_derivative_applications_nodes(dag):
    """Seviye 12 düğümlerinin (N99-N110: Türev Uygulamaları & Optimizasyon) hiyerarşisini doğrular."""
    assert dag.get_node("N99").level == 12   # math.calc.mean_value_theorem
    assert dag.get_node("N100").level == 12  # math.calc.increasing_decreasing_intervals
    assert dag.get_node("N101").level == 12  # math.calc.critical_points
    assert dag.get_node("N102").level == 12  # math.calc.first_derivative_test
    assert dag.get_node("N103").level == 12  # math.calc.second_derivative_concavity
    assert dag.get_node("N105").level == 12  # math.calc.optimization_geometric
    assert dag.get_node("N108").level == 12  # math.calc.implicit_differentiation
    assert dag.get_node("N109").level == 12  # math.calc.related_rates
    assert dag.get_node("N110").level == 12  # math.calc.linear_approximation


def test_dag_hedef4_zpd_progression_calculus(dag):
    """Öğrenci Fonksiyonlar ve Cebir tamamladığında N81 (Limit Sezgisi) ZPD'ye girmelidir."""
    mastered = {f"N{i:02d}" for i in range(1, 27)}
    zpd = dag.get_zpd_candidates(mastered)
    assert "N81" in zpd  # N26 önkoşulu sağlandığı için ZPD'de olmalı


# ==============================================================================
# 2. MULTI-CURRICULUM ONTOLOGY MAPPER (MEB, AP CALC, IB AA)
# ==============================================================================

def test_curriculum_meb_calculus_standards(registry):
    """MEB 12. Sınıf Türev ve Limit kazanımlarının varlığını doğrular."""
    meb_n81 = registry.get_standard_for_node("N81", "MEB")
    assert meb_n81 is not None
    assert meb_n81.standard_id == "MEB-12.5.1.1"
    assert "Limit" in meb_n81.title_tr

    meb_n89 = registry.get_standard_for_node("N89", "MEB")
    assert meb_n89 is not None
    assert meb_n89.standard_id == "MEB-12.6.1.1"
    assert "Türev" in meb_n89.title_tr

    meb_n94 = registry.get_standard_for_node("N94", "MEB")
    assert meb_n94 is not None
    assert "Zincir" in meb_n94.title_tr


def test_curriculum_ap_calculus_standards(registry):
    """AP Calculus AB/BC standartlarının varlığını doğrular."""
    ap_n81 = registry.get_standard_for_node("N81", "AP_CALC")
    assert ap_n81 is not None
    assert ap_n81.standard_id == "AP-CALC-1.3"

    ap_n90 = registry.get_standard_for_node("N90", "AP_CALC")
    assert ap_n90 is not None
    assert ap_n90.standard_id == "AP-CALC-2.5"

    ap_n105 = registry.get_standard_for_node("N105", "AP_CALC")
    assert ap_n105 is not None
    assert ap_n105.standard_id == "AP-CALC-5.11"

    ap_n108 = registry.get_standard_for_node("N108", "AP_CALC")
    assert ap_n108 is not None
    assert ap_n108.standard_id == "AP-CALC-3.2"


def test_curriculum_ib_aa_calculus_standards(registry):
    """IB DP Mathematics Analysis & Approaches Calculus standartlarını doğrular."""
    ib_n83 = registry.get_standard_for_node("N83", "IB_AA")
    assert ib_n83 is not None
    assert ib_n83.standard_id == "IB-AA-SL-5.2"

    ib_n89 = registry.get_standard_for_node("N89", "IB_AA")
    assert ib_n89 is not None
    assert ib_n89.standard_id == "IB-AA-SL-5.3"

    ib_n102 = registry.get_standard_for_node("N102", "IB_AA")
    assert ib_n102 is not None
    assert ib_n102.standard_id == "IB-AA-SL-5.9"


# ==============================================================================
# 3. SYMBOLIC CAS CALCULUS ENGINE
# ==============================================================================

def test_cas_compute_limit_polynomial(cas):
    """Polinom fonksiyonunda doğrudan yerine koyma limitini doğrular."""
    lim_val, is_fin = cas.compute_limit("x**2 - 3*x + 2", var="x", target_val=2)
    assert is_fin is True
    assert lim_val == 0


def test_cas_compute_limit_zero_over_zero(cas):
    """0/0 belirsizliğindeki rasyonel limitin doğru hesaplandığını doğrular."""
    lim_val, is_fin = cas.compute_limit("(x**2 - 4) / (x - 2)", var="x", target_val=2)
    assert is_fin is True
    assert lim_val == 4


def test_cas_compute_limit_trigonometric(cas):
    """lim(x->0) sin(x)/x = 1 trigonometrik limitini doğrular."""
    lim_val, is_fin = cas.compute_limit("sin(x) / x", var="x", target_val=0)
    assert is_fin is True
    assert lim_val == 1


def test_cas_compute_limit_infinity(cas):
    """Sonsuzdaki rasyonel limit hesabını doğrular: (3x^2 + 1)/(x^2 - 5) -> 3."""
    lim_val, is_fin = cas.compute_limit("(3*x**2 + 1) / (x**2 - 5)", var="x", target_val="oo")
    assert is_fin is True
    assert lim_val == 3


def test_cas_compute_derivative_power_rule(cas):
    """Polinom türevini kuvvet kuralı ile doğrular: d/dx(x^3 - 4x^2 + 5x - 7) = 3x^2 - 8x + 5."""
    deriv = cas.compute_derivative("x**3 - 4*x**2 + 5*x - 7", var="x")
    expected = cas.parse_to_sympy("3*x**2 - 8*x + 5")
    assert sp.simplify(deriv - expected) == 0


def test_cas_compute_derivative_trigonometric(cas):
    """Trigonometrik fonksiyonların türevlerini doğrular."""
    d_sin = cas.compute_derivative("sin(x)", var="x")
    assert sp.simplify(d_sin - cas.parse_to_sympy("cos(x)")) == 0

    d_cos = cas.compute_derivative("cos(x)", var="x")
    assert sp.simplify(d_cos - cas.parse_to_sympy("-sin(x)")) == 0


def test_cas_compute_derivative_chain_rule(cas):
    """Zincir kuralı türevini doğrular: d/dx(sin(3x)) = 3*cos(3x)."""
    deriv = cas.compute_derivative("sin(3*x)", var="x")
    expected = cas.parse_to_sympy("3*cos(3*x)")
    assert sp.simplify(deriv - expected) == 0


def test_cas_compute_derivative_exponential_log(cas):
    """Üstel ve logaritmik fonksiyonların türevlerini doğrular."""
    d_exp = cas.compute_derivative("exp(x)", var="x")
    assert sp.simplify(d_exp - cas.parse_to_sympy("exp(x)")) == 0

    d_ln = cas.compute_derivative("ln(x)", var="x")
    assert sp.simplify(d_ln - cas.parse_to_sympy("1/x")) == 0


def test_cas_verify_derivative_valid(cas):
    """Öğrencinin doğru türev adımını teyit eder."""
    assert cas.verify_derivative("x**4 + 2*x**2", "4*x**3 + 4*x", var="x") is True
    assert cas.verify_derivative("cos(2*x)", "-2*sin(2*x)", var="x") is True


def test_cas_verify_derivative_invalid(cas):
    """Öğrencinin hatalı türev adımını reddeder."""
    assert cas.verify_derivative("x**4 + 2*x**2", "4*x**3 + 2*x", var="x") is False
    assert cas.verify_derivative("cos(2*x)", "2*sin(2*x)", var="x") is False


def test_cas_compute_tangent_line(cas):
    """f(x) = x^2 eğrisine x0=3 noktasındaki teğet doğrusu y = 6(x-3) + 9 = 6x - 9 olmalıdır."""
    tangent_expr, slope, y0 = cas.compute_tangent_line("x**2", x0=3.0)
    assert slope == 6.0
    assert y0 == 9.0
    expected = cas.parse_to_sympy("6*x - 9")
    assert sp.simplify(tangent_expr - expected) == 0


def test_cas_check_continuity_continuous_point(cas):
    """f(x) = x^2 + 1 fonksiyonunun x=2'de sürekli olduğunu doğrular."""
    is_cont, lim_val, func_val = cas.check_continuity("x**2 + 1", var="x", pt=2.0)
    assert is_cont is True
    assert lim_val == 5.0
    assert func_val == 5.0


def test_cas_check_continuity_discontinuous_point(cas):
    """f(x) = 1/x fonksiyonunun x=0'da sürekli olmadığını doğrular."""
    is_cont, lim_val, func_val = cas.check_continuity("1/x", var="x", pt=0.0)
    assert is_cont is False


# ==============================================================================
# 4. CALCULUS MISCONCEPTIONS & BUGGY RULES (BUG-CALC-01 to BUG-CALC-10)
# ==============================================================================

def test_bug_calc_01_chain_rule_inner_derivative_missing(detector):
    """BUG-CALC-01: Zincir kuralında iç türevin unutulmasını tespit eder."""
    res = detector.detect(
        user_step_str="d/dx(sin(2x)) = cos(2x)",
        previous_step_str="d/dx(sin(2x))",
        target_equation_str="d/dx(sin(2x)) = 2*cos(2x)",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-01"
    assert "CALCULUS_CHAIN_RULE" in res.category


def test_bug_calc_01_polynomial_power_inner_derivative_missing(detector):
    """BUG-CALC-01: Polinom kuvvetinde iç türevin unutulmasını tespit eder."""
    res = detector.detect(
        user_step_str="4*(3*x + 1)**3",
        previous_step_str="(3*x + 1)**4",
        target_equation_str="12*(3*x + 1)**3",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-01"


def test_bug_calc_01_zero_false_positive_on_correct_chain_rule(detector):
    """Doğru zincir kuralı uygulandığında BUG-CALC-01 tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="2*cos(2*x)",
        previous_step_str="d/dx(sin(2*x))",
        target_equation_str="2*cos(2*x)",
    )
    assert res is None


def test_bug_calc_02_quotient_rule_sign_error(detector):
    """BUG-CALC-02: Bölüm türevinde pay kısmındaki artı işareti hatasını yakalar."""
    res = detector.detect(
        user_step_str="(f'*g + f*g') / g^2",
        previous_step_str="(f/g)'",
        target_equation_str="(f'*g - f*g') / g^2",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-02"
    assert "QUOTIENT_RULE_SIGN" in res.category


def test_bug_calc_02_zero_false_positive_on_correct_quotient(detector):
    """Doğru bölüm türevinde BUG-CALC-02 tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="(f'*g - f*g') / g^2",
        previous_step_str="(f/g)'",
        target_equation_str="(f'*g - f*g') / g^2",
    )
    assert res is None


def test_bug_calc_03_indeterminate_zero_over_zero_fallacy(detector):
    """BUG-CALC-03: 0/0 belirsizliğini 0 veya tanımsız sanma yanılgısını yakalar."""
    res = detector.detect(
        user_step_str="0/0 = 0",
        previous_step_str="lim_{x->2} (x^2 - 4)/(x - 2) = 0/0",
        target_equation_str="4",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-03"
    assert "INDETERMINATE_FORM" in res.category


def test_bug_calc_03_indeterminate_undefined_fallacy(detector):
    """BUG-CALC-03: 0/0 için doğrudan tanımsız iddiasını yakalar."""
    res = detector.detect(
        user_step_str="0/0 = tanimsiz",
        previous_step_str="lim (x**2-4)/(x-2)",
        target_equation_str="4",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-03"


def test_bug_calc_03_zero_false_positive_on_factoring(detector):
    """0/0 belirsizliğinde çarpanlara ayırma adımında hata tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="(x - 2)*(x + 2) / (x - 2)",
        previous_step_str="(x**2 - 4) / (x - 2)",
        target_equation_str="4",
    )
    assert res is None


def test_bug_calc_04_critical_point_false_extrema(detector):
    """BUG-CALC-04: f'(x)=0 olan noktayı kesin yerel ekstremum sanma yanılgısını yakalar."""
    res = detector.detect(
        user_step_str="f'(0)=0 oldugundan x=0 yerel maksimumdur",
        previous_step_str="f(x) = x^3, f'(x) = 3*x^2",
        target_equation_str="x=0 büküm noktasıdır",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-04"
    assert "CRITICAL_POINT" in res.category


def test_bug_calc_04_zero_false_positive_on_valid_test(detector):
    """Türevin işaret değişimini inceleyen geçerli ifadede hata tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="f'(x) işareti tablosunda (+)'dan (-)'ye geçtiğinden x=2 yerel maksimumdur",
        previous_step_str="f'(x) = -2x + 4",
        target_equation_str="x=2 yerel maksimum",
    )
    assert res is None


def test_bug_calc_05_product_rule_false_linearity(detector):
    """BUG-CALC-05: Çarpımın türevinde sahte doğrusallık ((uv)' = u'v') yanılgısını yakalar."""
    res = detector.detect(
        user_step_str="(u*v)' = u'*v'",
        previous_step_str="(u*v)'",
        target_equation_str="u'*v + u*v'",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-05"
    assert "PRODUCT_RULE" in res.category


def test_bug_calc_05_product_rule_applied_false_linearity(detector):
    """BUG-CALC-05: x*sin(x) türevini 1*cos(x) sanma hatasını yakalar."""
    res = detector.detect(
        user_step_str="(x * sin(x))' = 1*cos(x) = cos(x)",
        previous_step_str="(x * sin(x))'",
        target_equation_str="sin(x) + x*cos(x)",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-05"


def test_bug_calc_05_zero_false_positive_on_correct_product(detector):
    """Doğru çarpım türevinde BUG-CALC-05 tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="sin(x) + x*cos(x)",
        previous_step_str="(x * sin(x))'",
        target_equation_str="sin(x) + x*cos(x)",
    )
    assert res is None


def test_bug_calc_06_constant_derivative_error(detector):
    """BUG-CALC-06: Sabit sayının türevini sıfır yerine kendisi bırakma hatasını yakalar."""
    res = detector.detect(
        user_step_str="(x^2 + 5)' = 2x + 5",
        previous_step_str="x^2 + 5",
        target_equation_str="2x",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-06"
    assert "CONSTANT_DERIVATIVE" in res.category


def test_bug_calc_06_zero_false_positive_on_correct_constant_deriv(detector):
    """Sabit sayının türevi 0 olarak alındığında hata tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="2*x + 0 = 2*x",
        previous_step_str="x**2 + 5",
        target_equation_str="2*x",
    )
    assert res is None


def test_bug_calc_07_limit_equals_function_value_fallacy(detector):
    """BUG-CALC-07: Fonksiyon tanımsız olduğunda limitin de olmadığını sanma yanılgısını yakalar."""
    res = detector.detect(
        user_step_str="f(a) tanimsiz oldugu icin limit yoktur",
        previous_step_str="f(x) = (x^2 - 4)/(x - 2)",
        target_equation_str="lim = 4",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-07"
    assert "LIMIT_EQUALS_FUNCTION_VALUE" in res.category


def test_bug_calc_07_zero_false_positive_on_proper_limit(detector):
    """Doğru limit yaklaşımında hata tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="Sagdan ve soldan yaklasildiginda limit degeri 4'tur",
        previous_step_str="lim (x**2-4)/(x-2)",
        target_equation_str="4",
    )
    assert res is None


def test_bug_calc_08_cosine_derivative_sign_error(detector):
    """BUG-CALC-08: d/dx(cos x) = sin x işaret hatasını yakalar."""
    res = detector.detect(
        user_step_str="(cos(x))' = sin(x)",
        previous_step_str="cos(x)",
        target_equation_str="-sin(x)",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-08"
    assert "COSINE_DERIVATIVE_SIGN" in res.category


def test_bug_calc_08_zero_false_positive_on_correct_cosine_deriv(detector):
    """d/dx(cos x) = -sin(x) doğru adımında hata tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="-sin(x)",
        previous_step_str="cos(x)",
        target_equation_str="-sin(x)",
    )
    assert res is None


def test_bug_calc_09_lhopital_quotient_confusion(detector):
    """BUG-CALC-09: Bölüm türevi yerine L'Hôpital f'/g' uygulamasını yakalar."""
    res = detector.detect(
        user_step_str="(f/g)' = f'/g'",
        previous_step_str="(f/g)'",
        target_equation_str="(f'*g - f*g')/g^2",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-09"
    assert "LHOPITAL_QUOTIENT" in res.category


def test_bug_calc_09_zero_false_positive_on_correct_derivative(detector):
    """Doğru bölüm türevinde BUG-CALC-09 tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="(f'*g - f*g')/g**2",
        previous_step_str="(f/g)'",
        target_equation_str="(f'*g - f*g')/g**2",
    )
    assert res is None


def test_bug_calc_10_tangent_slope_function_value_confusion(detector):
    """BUG-CALC-10: Teğet eğimini türev yerine doğrudan f(x_0) değerine eşitlemeyi yakalar."""
    res = detector.detect(
        user_step_str="m = f(x_0)",
        previous_step_str="f(x), x_0",
        target_equation_str="m = f'(x_0)",
    )
    assert res is not None
    assert res.bug_id == "BUG-CALC-10"
    assert "TANGENT_SLOPE" in res.category


def test_bug_calc_10_zero_false_positive_on_correct_tangent_slope(detector):
    """m = f'(x_0) doğru eğim formülünde hata tetiklenmemelidir."""
    res = detector.detect(
        user_step_str="m = f'(x_0)",
        previous_step_str="f(x), x_0",
        target_equation_str="m = f'(x_0)",
    )
    assert res is None


# ==============================================================================
# 5. COGNITIVE ATLAS & LOCAL ANALYTICS INTEGRATION
# ==============================================================================

def test_analytics_reporter_calculus_groups(dag):
    """LocalAnalyticsReporter'ın CALCULUS_LIMIT ve CALCULUS_DERIVATIVE gruplarını doğru ürettiğini teyit eder."""
    reporter = LocalAnalyticsReporter(dag=dag)
    report = reporter.generate_student_report("CALC-STUDENT-01")

    atlas = report["algebra_atlas"]
    assert atlas["total_nodes"] == len(dag.nodes)

    node_groups = {n["node_id"]: n["curriculum_group"] for n in atlas["nodes"]}
    assert node_groups["N81"] == "CALCULUS_LIMIT"
    assert node_groups["N88"] == "CALCULUS_LIMIT"
    assert node_groups["N89"] == "CALCULUS_DERIVATIVE"
    assert node_groups["N110"] == "CALCULUS_DERIVATIVE"


def test_cas_security_violation_in_calculus(cas):
    """Kalkülüs girdilerinde güvenlik ihlali oluşturabilecek yetkisiz çağrıları engeller."""
    with pytest.raises((SecurityViolationError, ValueError)):
        cas.compute_derivative("__import__('os').system('ls')", var="x")


def test_cas_higher_order_derivative(cas):
    """Yüksek mertebeden türevlerin doğru hesaplandığını doğrular (f''(x), f'''(x))."""
    d2 = cas.compute_derivative("x**4", var="x", order=2)
    assert sp.simplify(d2 - cas.parse_to_sympy("12*x**2")) == 0

    d3 = cas.compute_derivative("sin(x)", var="x", order=3)
    assert sp.simplify(d3 - cas.parse_to_sympy("-cos(x)")) == 0


def test_curriculum_registry_standards_count_and_unique_ids(registry):
    """Müfredat standartlarının benzersiz kimliklere sahip olduğunu doğrular."""
    standards = registry.get_all_standards()
    assert len(standards) >= 40
    ids = [s.standard_id for s in standards]
    assert len(ids) == len(set(ids)), "Standart ID'leri benzersiz olmalıdır!"
