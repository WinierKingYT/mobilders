import pytest
import sympy as sp
from app.graph.knowledge_dag import KnowledgeDAG, CycleDetectedError
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
from app.misconceptions.detector import QuadraticMisconceptionDetector


@pytest.fixture
def dag():
    return KnowledgeDAG()


@pytest.fixture
def cas():
    return SymbolicEquivalenceEngine()


@pytest.fixture
def detector():
    return QuadraticMisconceptionDetector()


@pytest.fixture
def mapper():
    return CurriculumOntologyRegistry()


# ==============================================================================
# 1. KNOWLEDGE DAG 50-NODE RIGOROUS TESTS
# ==============================================================================

def test_dag_total_nodes_is_fifty(dag):
    assert len(dag.nodes) == 50


def test_dag_kahn_topological_sort_full_coverage(dag):
    dag.assert_cycle_free()
    order = dag.topological_sort()
    assert len(order) == 50
    # Every strict prerequisite must appear before the dependent node
    pos = {n_id: i for i, n_id in enumerate(order)}
    for n_id, node in dag.nodes.items():
        for prereq in node.strict_prereqs:
            assert pos[prereq] < pos[n_id], f"Prerequisite {prereq} must precede {n_id}"


def test_dag_parabola_subgraph_nodes_integrity(dag):
    # N27 to N38 must all exist with appropriate levels (5 or 6)
    for i in range(27, 39):
        node_id = f"N{i:02d}"
        node = dag.get_node(node_id)
        assert node is not None
        assert node.level in {5, 6}
        assert node.default_difficulty_b >= 0.5
        assert len(node.strict_prereqs) >= 1


def test_dag_polynomial_subgraph_nodes_integrity(dag):
    # N39 to N50 must all exist with appropriate levels (6 or 7)
    for i in range(39, 51):
        node_id = f"N{i:02d}"
        node = dag.get_node(node_id)
        assert node is not None
        assert node.level in {6, 7}
        assert len(node.strict_prereqs) >= 1


def test_dag_zpd_progression_into_parabolas(dag):
    # Student mastering N01-N24 should have N27 and N31 available in ZPD
    mastered = {f"N{i:02d}" for i in range(1, 25)}
    zpd = set(dag.get_zpd_candidates(mastered))
    assert "N27" in zpd
    assert "N31" in zpd


def test_dag_zpd_progression_into_polynomials(dag):
    # Student with N01, N02, N03 mastered can start N39 (polynomial definition)
    mastered = {"N01", "N02", "N03"}
    zpd = set(dag.get_zpd_candidates(mastered))
    assert "N39" in zpd


# ==============================================================================
# 2. CURRICULUM STANDARDS MAPPING TESTS
# ==============================================================================

def test_curriculum_mapper_parabola_standards(mapper):
    meb_n32 = mapper.get_standard_for_node("N32", "MEB")
    assert meb_n32 is not None
    assert "Ekstremum" in meb_n32.title_tr
    assert meb_n32.grade_level == "11"

    ib_n33 = mapper.get_standard_for_node("N33", "IB_AA")
    assert ib_n33 is not None
    assert "Intersections" in ib_n33.title_en


def test_curriculum_mapper_polynomial_standards(mapper):
    meb_n39 = mapper.get_standard_for_node("N39", "MEB")
    assert meb_n39 is not None
    assert "Polinom" in meb_n39.title_tr
    assert meb_n39.grade_level == "10"

    meb_n42 = mapper.get_standard_for_node("N42", "MEB")
    assert meb_n42 is not None
    assert "Kalan Teoremi" in meb_n42.title_tr

    ib_n47 = mapper.get_standard_for_node("N47", "IB_AA")
    assert ib_n47 is not None
    assert "Factor Theorem" in ib_n47.title_en


# ==============================================================================
# 3. CAS SYMBOLIC ENGINE POLYNOMIAL & PARABOLA CAPABILITIES
# ==============================================================================

def test_cas_polynomial_division_exact(cas):
    quo, rem = cas.polynomial_divide("x**2 - 1", "x - 1")
    x = cas.symbols["x"]
    assert sp.simplify(quo - (x + 1)) == 0
    assert rem == 0


def test_cas_polynomial_division_with_remainder(cas):
    quo, rem = cas.polynomial_divide("x**3 - 2*x**2 + 3*x + 5", "x - 1")
    x = cas.symbols["x"]
    assert sp.simplify(quo - (x**2 - x + 2)) == 0
    assert rem == 7


def test_cas_polynomial_remainder_function(cas):
    rem = cas.polynomial_remainder("x**2 + 5*x + 6", "x + 2")
    assert rem == 0


def test_cas_polynomial_coeffs_sum(cas):
    sum_val = cas.polynomial_coeffs_sum("4*x**3 - 5*x + 7")
    # P(1) = 4 - 5 + 7 = 6
    assert sum_val == 6


def test_cas_polynomial_constant_term(cas):
    const_val = cas.polynomial_constant_term("4*x**3 - 5*x + 7")
    # P(0) = 7
    assert const_val == 7


def test_cas_parabola_vertex_calculation_positive_a(cas):
    # f(x) = x^2 - 4x + 3 => r = 2, k = -1
    r, k = cas.verify_parabola_vertex(1, -4, 3)
    assert r == 2.0
    assert k == -1.0


def test_cas_parabola_vertex_calculation_negative_a(cas):
    # f(x) = -2x^2 + 8x - 5 => r = -8/(2*-2) = 2, k = -5 - (64/(4*-2)) = -5 - (-8) = 3
    r, k = cas.verify_parabola_vertex(-2, 8, -5)
    assert r == 2.0
    assert k == 3.0


def test_cas_sandbox_security_with_poly_symbols(cas):
    # Allowed symbols P, Q, r, Delta must be parsed cleanly
    e1 = cas.parse_to_sympy("r = 3")
    assert e1 is not None
    # Forbidden operations must raise SecurityViolationError
    with pytest.raises(SecurityViolationError):
        cas.parse_to_sympy("__import__('os').system('ls')")


# ==============================================================================
# 4. 10 BUGGY RULES — POSITIVE DETECTION (TRUE POSITIVES)
# ==============================================================================

def test_bug_parab_01_vertex_formula_sign(detector):
    # f(x) = x^2 - 6x + 5. True r = -(-6)/2 = 3. Student computes r = -3 (forgot minus)
    res = detector.detect(
        user_step_str="r = -3",
        previous_step_str="f(x) = x**2 - 6*x + 5",
        target_equation_str="f(x) = x**2 - 6*x + 5",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-01"
    assert "eksi işareti" in res.description.lower()


def test_bug_parab_01_vertex_formula_sign_with_coeff(detector):
    # f(x) = 2x^2 + 8x + 3. True r = -8/4 = -2. Student computes r = 8/4 = 2 (forgot minus)
    res = detector.detect(
        user_step_str="r = 2",
        previous_step_str="f(x) = 2*x**2 + 8*x + 3",
        target_equation_str="f(x) = 2*x**2 + 8*x + 3",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-01"


def test_bug_parab_02_axis_horizontal_line(detector):
    # Student states axis of symmetry is y = 3
    res = detector.detect(
        user_step_str="simetri ekseni: y = 3",
        previous_step_str="f(x) = x**2 - 6*x + 5",
        target_equation_str="f(x) = x**2 - 6*x + 5",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-02"
    assert "düşey" in res.description.lower()


def test_bug_parab_02_ordinate_equals_c(detector):
    # f(x) = x^2 - 4x + 7. True r = 2, k = 3. Student writes k = 7 (constant term)
    res = detector.detect(
        user_step_str="k = 7",
        previous_step_str="f(x) = x**2 - 4*x + 7",
        target_equation_str="f(x) = x**2 - 4*x + 7",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-02"
    assert "sabit terim" in res.description.lower()


def test_bug_parab_03_vertex_equals_sum_of_roots(detector):
    # f(x) = x^2 - 6x + 8. Roots: 2, 4. True r = 3. Student writes r = 6 (sum of roots)
    res = detector.detect(
        user_step_str="r = 6",
        previous_step_str="f(x) = x**2 - 6*x + 8",
        target_equation_str="f(x) = x**2 - 6*x + 8",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-03"
    assert "aritmetik ortalama" in res.description.lower() or "yarısı" in res.description.lower()


def test_bug_parab_04_y_intercept_confused_with_root(detector):
    # f(x) = x^2 - 5x + 6. Constant c = 6 (roots are 2 and 3). Student says root is 6.
    res = detector.detect(
        user_step_str="parabolün kökü c'dir",
        previous_step_str="f(x) = x**2 - 5*x + 6",
        target_equation_str="f(x) = x**2 - 5*x + 6",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-04"


def test_bug_parab_05_extrema_orientation_inversion(detector):
    # f(x) = x^2 - 4x + 3 (a = 1 > 0 => minimum). Student says tepe noktası maksimumdur.
    res = detector.detect(
        user_step_str="tepe noktası maksimumdur",
        previous_step_str="f(x) = x**2 - 4*x + 3",
        target_equation_str="f(x) = x**2 - 4*x + 3",
    )
    assert res is not None
    assert res.bug_id == "BUG-PARAB-05"
    assert "minimum" in res.description.lower()


def test_bug_poly_01_remainder_sign_error(detector):
    # Dividing by (x - 4), student evaluates P(-4) instead of P(4)
    res = detector.detect(
        user_step_str="kalan = P(-4)",
        previous_step_str="P(x) / (x - 4)",
        target_equation_str="P(x) / (x - 4)",
    )
    assert res is not None
    assert res.bug_id == "BUG-POLY-01"
    assert "kalan teoreminde" in res.description.lower()


def test_bug_poly_02_coeffs_sum_zero(detector):
    # Student states katsayılar toplamı için x = 0
    res = detector.detect(
        user_step_str="katsayılar toplamı için x = 0 yazılır",
        previous_step_str="P(x) = 3*x**2 + 5*x - 2",
        target_equation_str="P(x) = 3*x**2 + 5*x - 2",
    )
    assert res is not None
    assert res.bug_id == "BUG-POLY-02"
    assert "x = 1" in res.description.lower()


def test_bug_poly_03_remainder_degree_violation(detector):
    # Divisor degree is 2, student claims remainder degree is 2
    res = detector.detect(
        user_step_str="der(Kalan) = 2",
        previous_step_str="der(Bölen) = 2",
        target_equation_str="der(Bölen) = 2",
    )
    assert res is not None
    assert res.bug_id == "BUG-POLY-03"
    assert "küçük olmalıdır" in res.description.lower()


def test_bug_poly_04_multiply_degrees_arithmetic(detector):
    # deg(P) = 3, deg(Q) = 2. Student writes deg(P*Q) = 6
    res = detector.detect(
        user_step_str="der(P*Q) = 6",
        previous_step_str="der(P) = 3, der(Q) = 2",
        target_equation_str="der(P) = 3, der(Q) = 2",
    )
    assert res is not None
    assert res.bug_id == "BUG-POLY-04"
    assert "toplamıdır" in res.description.lower()


def test_bug_poly_05_remainder_equated_to_root(detector):
    # P(x) / (x - 5). Student writes kalan = 5
    res = detector.detect(
        user_step_str="kalan = 5",
        previous_step_str="P(x) / (x - 5)",
        target_equation_str="P(x) / (x - 5)",
    )
    assert res is not None
    assert res.bug_id == "BUG-POLY-05"
    assert "kökü" in res.description.lower()


# ==============================================================================
# 5. 10 BUGGY RULES — ZERO FALSE POSITIVES (NEGATIVE DETECTION)
# ==============================================================================

def test_clean_parab_01_correct_vertex(detector):
    # f(x) = x^2 - 6x + 5. True r = 3. Student correctly writes r = 3
    res = detector.detect(
        user_step_str="r = 3",
        previous_step_str="f(x) = x**2 - 6*x + 5",
        target_equation_str="f(x) = x**2 - 6*x + 5",
    )
    assert res is None


def test_clean_parab_02_correct_axis_and_ordinate(detector):
    # Student correctly writes vertical axis x = 3
    res = detector.detect(
        user_step_str="simetri ekseni: x = 3",
        previous_step_str="f(x) = x**2 - 6*x + 5",
        target_equation_str="f(x) = x**2 - 6*x + 5",
    )
    assert res is None

    # f(x) = x^2 - 4x + 7. True k = 3. Student correctly writes k = 3
    res_k = detector.detect(
        user_step_str="k = 3",
        previous_step_str="f(x) = x**2 - 4*x + 7",
        target_equation_str="f(x) = x**2 - 4*x + 7",
    )
    assert res_k is None


def test_clean_parab_03_correct_average_of_roots(detector):
    res = detector.detect(
        user_step_str="r = (x1 + x2)/2",
        previous_step_str="f(x) = x**2 - 6*x + 8",
        target_equation_str="f(x) = x**2 - 6*x + 8",
    )
    assert res is None


def test_clean_parab_04_correct_roots(detector):
    res = detector.detect(
        user_step_str="x = 2 veya x = 3",
        previous_step_str="f(x) = x**2 - 5*x + 6",
        target_equation_str="f(x) = x**2 - 5*x + 6",
    )
    assert res is None


def test_clean_parab_05_correct_min_and_max(detector):
    # Positive a correctly identified as minimum
    res_pos = detector.detect(
        user_step_str="tepe noktası minimumdur",
        previous_step_str="f(x) = x**2 - 4*x + 3",
        target_equation_str="f(x) = x**2 - 4*x + 3",
    )
    assert res_pos is None

    # Negative a correctly identified as maximum
    res_neg = detector.detect(
        user_step_str="tepe noktası maksimumdur",
        previous_step_str="f(x) = -x**2 + 4*x - 3",
        target_equation_str="f(x) = -x**2 + 4*x - 3",
    )
    assert res_neg is None


def test_clean_poly_01_correct_remainder_evaluation(detector):
    # Dividing by (x - 4), student evaluates P(4)
    res = detector.detect(
        user_step_str="kalan = P(4)",
        previous_step_str="P(x) / (x - 4)",
        target_equation_str="P(x) / (x - 4)",
    )
    assert res is None


def test_clean_poly_02_correct_coeffs_and_constant(detector):
    res_sum = detector.detect(
        user_step_str="katsayılar toplamı için x = 1 yazılır",
        previous_step_str="P(x) = 3*x**2 + 5*x - 2",
        target_equation_str="P(x) = 3*x**2 + 5*x - 2",
    )
    assert res_sum is None

    res_const = detector.detect(
        user_step_str="sabit terim için x = 0 yazılır",
        previous_step_str="P(x) = 3*x**2 + 5*x - 2",
        target_equation_str="P(x) = 3*x**2 + 5*x - 2",
    )
    assert res_const is None


def test_clean_poly_03_correct_remainder_degree(detector):
    # Divisor degree 2, remainder degree 1
    res = detector.detect(
        user_step_str="der(Kalan) = 1",
        previous_step_str="der(Bölen) = 2",
        target_equation_str="der(Bölen) = 2",
    )
    assert res is None


def test_clean_poly_04_correct_degree_addition(detector):
    # der(P) = 3, der(Q) = 2 => der(P*Q) = 5
    res = detector.detect(
        user_step_str="der(P*Q) = 5",
        previous_step_str="der(P) = 3, der(Q) = 2",
        target_equation_str="der(P) = 3, der(Q) = 2",
    )
    assert res is None


def test_clean_poly_05_correct_remainder_expression(detector):
    res = detector.detect(
        user_step_str="kalan = P(5)",
        previous_step_str="P(x) / (x - 5)",
        target_equation_str="P(x) / (x - 5)",
    )
    assert res is None


# ==============================================================================
# 6. INTEGRATION, ANALYTICS & DEEP SUBGRAPH CONNECTIVITY
# ==============================================================================

def test_local_reporter_parabolas_and_poly_groups(dag):
    from app.analytics.local_reporter import LocalAnalyticsReporter
    reporter = LocalAnalyticsReporter(dag=dag)
    report = reporter.generate_student_report("student_test_h2")
    atlas = report["algebra_atlas"]["nodes"]
    assert len(atlas) == 50

    groups = {n["node_id"]: n["curriculum_group"] for n in atlas}
    assert groups["N24"] == "PARABOLAS"
    assert groups["N32"] == "PARABOLAS"
    assert groups["N38"] == "PARABOLAS"
    assert groups["N39"] == "POLYNOMIALS"
    assert groups["N45"] == "POLYNOMIALS"
    assert groups["N50"] == "POLYNOMIALS"
    assert groups["N21"] == "INEQUALITIES"
    assert groups["N01"] == "QUADRATICS_CORE"


def test_cas_polynomial_factor_theorem(cas):
    # P(x) = x^3 - 4x^2 + x + 6. Roots: -1, 2, 3.
    # P(2) = 8 - 16 + 2 + 6 = 0
    rem = cas.polynomial_remainder("x**3 - 4*x**2 + x + 6", "x - 2")
    assert rem == 0


def test_cas_parabola_line_intersection_discriminant(cas):
    # Parabola: y = x^2 - 2x + 1. Line: y = 2x - 3.
    # Intersection equation: x^2 - 2x + 1 - (2x - 3) = x^2 - 4x + 4 = 0.
    # Delta = (-4)^2 - 4*1*4 = 0 (line is tangent to parabola at x = 2).
    x = cas.symbols["x"]
    diff_expr = cas.parse_to_sympy("(x**2 - 2*x + 1) - (2*x - 3)")
    poly = sp.Poly(diff_expr, x)
    coeffs = poly.all_coeffs()
    a, b, c = coeffs[0], coeffs[1], coeffs[2]
    delta = b**2 - 4*a*c
    assert delta == 0
    roots = sp.solve(diff_expr, x)
    assert roots == [2]


def test_dag_deep_subgraph_connectivity(dag):
    # Verify path from root N01 to terminal polynomial inequality node N50
    prereqs_n50 = dag.get_prerequisites("N50", recursive=True)
    assert "N01" in prereqs_n50
    assert "N03" in prereqs_n50
    assert "N20" in prereqs_n50
    assert "N39" in prereqs_n50
    assert "N47" in prereqs_n50

