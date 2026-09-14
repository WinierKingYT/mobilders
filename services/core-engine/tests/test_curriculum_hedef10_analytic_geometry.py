"""
HEDEF 10: Analitik Geometri ve 2B Vektörler Kapsamlı Test Paketi
N136 - N160 Düğümleri, Nokta/Doğru/Çember/Vektör Motoru ve BUG-ANAG-01..05 Testleri.
"""
import pytest
import math
from app.graph.knowledge_dag import KnowledgeDAG
from app.geometry.analytic_geometry import (
    Point2D,
    Line2D,
    Circle2D,
    Vector2D,
    triangle_centroid,
    triangle_area,
    solve_analytic_geometry,
)
from app.misconceptions.detector import QuadraticMisconceptionDetector


@pytest.fixture
def dag():
    return KnowledgeDAG()


@pytest.fixture
def detector():
    return QuadraticMisconceptionDetector()


# ==============================================================================
# 1. KNOWLEDGE DAG STRUCTURE & PREREQUISITES (N136 - N160)
# ==============================================================================

def test_dag_hedef10_total_nodes_160(dag):
    """Grafın 160 düğüm içerdiğini ve N136-N160 aralığının eksiksiz tanımlandığını doğrular."""
    assert len(dag.nodes) >= 160
    for i in range(136, 161):
        n_id = f"N{i}"
        assert n_id in dag.nodes, f"Düğüm {n_id} eksik!"
        node = dag.get_node(n_id)
        assert node.title != ""
        assert node.canonical_code != ""
        assert node.level in {15, 16}
        assert -1.0 <= node.default_difficulty_b <= 3.0
        assert 1.0 <= node.discrimination_a <= 3.0


def test_dag_hedef10_cycle_free(dag):
    """N136-N160 düğümlerinin döngüsüz (DAG) olduğunu doğrular."""
    dag.assert_cycle_free()


def test_dag_hedef10_topological_sort(dag):
    """N136-N160 içeren tüm grafın topolojik sıralanabildiğini doğrular."""
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == len(dag.nodes)
    # Önkoşul sırası testi: N136 -> N137, N141 -> N142, N152 -> N153, N156 -> N158
    assert sorted_nodes.index("N136") < sorted_nodes.index("N137")
    assert sorted_nodes.index("N141") < sorted_nodes.index("N142")
    assert sorted_nodes.index("N152") < sorted_nodes.index("N153")
    assert sorted_nodes.index("N156") < sorted_nodes.index("N158")


def test_dag_hedef10_prerequisites(dag):
    """Analitik geometri ve vektör düğümlerinin mantıklı önkoşullara bağlandığını doğrular."""
    # N137 (iki nokta arası uzaklık) N136'ya bağlı
    assert "N136" in dag.get_prerequisites("N137")
    # N147 (dik doğruların eğimi) N141'e (eğim) bağlı
    assert "N141" in dag.get_prerequisites("N147")
    # N150 (noktanın doğruya uzaklığı) N137 ve N145'e bağlı
    prereqs_150 = dag.get_prerequisites("N150")
    assert "N137" in prereqs_150 and "N145" in prereqs_150
    # N158 (iç çarpım) N157'ye bağlı
    assert "N157" in dag.get_prerequisites("N158")
    # N160 (dik izdüşüm) N159'a bağlı
    assert "N159" in dag.get_prerequisites("N160")


# ==============================================================================
# 2. POINT2D OPERATIONS
# ==============================================================================

def test_point2d_distance():
    p1 = Point2D(0, 0)
    p2 = Point2D(3, 4)
    assert math.isclose(p1.distance_to(p2), 5.0)
    p3 = Point2D(-1, -2)
    p4 = Point2D(2, 2)
    assert math.isclose(p3.distance_to(p4), 5.0)


def test_point2d_midpoint():
    p1 = Point2D(2, 8)
    p2 = Point2D(6, 2)
    mid = p1.midpoint_with(p2)
    assert mid == Point2D(4, 5)


def test_point2d_internal_division():
    # A(1, 2) ve B(7, 8), k = 1 => orta nokta (4, 5)
    p1 = Point2D(1, 2)
    p2 = Point2D(7, 8)
    p = p1.internal_division(p2, 1.0)
    assert p == Point2D(4, 5)
    # k = 2 => AP/PB = 2 => x = (1 + 2*7)/3 = 5, y = (2 + 2*8)/3 = 6
    p_div2 = p1.internal_division(p2, 2.0)
    assert p_div2 == Point2D(5, 6)


def test_point2d_quadrant():
    assert Point2D(3, 5).quadrant() == 1
    assert Point2D(-2, 4).quadrant() == 2
    assert Point2D(-3, -7).quadrant() == 3
    assert Point2D(4, -1).quadrant() == 4
    assert Point2D(0, 5).quadrant() == 0
    assert Point2D(3, 0).quadrant() == 0


# ==============================================================================
# 3. LINE2D OPERATIONS
# ==============================================================================

def test_line2d_from_two_points_and_slope():
    p1 = Point2D(1, 2)
    p2 = Point2D(4, 8)
    line = Line2D.from_two_points(p1, p2)
    # Eğim m = (8 - 2) / (4 - 1) = 6 / 3 = 2
    assert line.slope is not None
    assert math.isclose(line.slope, 2.0, abs_tol=1e-5)
    # y-kesimi: y = 2x + 0 => 0
    assert math.isclose(line.y_intercept, 0.0, abs_tol=1e-5)


def test_line2d_from_point_and_slope():
    p = Point2D(2, 3)
    line = Line2D.from_point_and_slope(p, -1.0)
    assert math.isclose(line.slope, -1.0, abs_tol=1e-5)
    # y - 3 = -1(x - 2) => y = -x + 5
    assert math.isclose(line.y_intercept, 5.0, abs_tol=1e-5)
    assert math.isclose(line.x_intercept, 5.0, abs_tol=1e-5)


def test_line2d_from_intercepts():
    # x/3 + y/4 = 1 => 4x + 3y - 12 = 0
    line = Line2D.from_intercepts(3.0, 4.0)
    assert math.isclose(line.x_intercept, 3.0, abs_tol=1e-5)
    assert math.isclose(line.y_intercept, 4.0, abs_tol=1e-5)
    assert math.isclose(line.slope, -4.0 / 3.0, abs_tol=1e-5)


def test_line2d_horizontal_and_vertical():
    # Yatay doğru y = 4 (0x + 1y - 4 = 0)
    horiz = Line2D(0, 1, -4)
    assert horiz.is_horizontal
    assert not horiz.is_vertical
    assert math.isclose(horiz.slope, 0.0, abs_tol=1e-5)
    assert math.isclose(horiz.angle_deg, 0.0, abs_tol=1e-5)

    # Düşey doğru x = 3 (1x + 0y - 3 = 0)
    vert = Line2D(1, 0, -3)
    assert vert.is_vertical
    assert not vert.is_horizontal
    assert vert.slope is None
    assert math.isclose(vert.angle_deg, 90.0, abs_tol=1e-5)


def test_line2d_angle_deg():
    # Eğim = 1 => theta = 45°
    l45 = Line2D.from_point_and_slope(Point2D(0, 0), 1.0)
    assert math.isclose(l45.angle_deg, 45.0, abs_tol=1e-4)

    # Eğim = -1 => theta = 135°
    l135 = Line2D.from_point_and_slope(Point2D(0, 0), -1.0)
    assert math.isclose(l135.angle_deg, 135.0, abs_tol=1e-4)


def test_line2d_point_distance():
    # 3x + 4y - 12 = 0 doğrusuna O(0,0) uzaklığı = 12 / 5 = 2.4
    line = Line2D(3, 4, -12)
    d = line.distance_from_point(Point2D(0, 0))
    assert math.isclose(d, 2.4, abs_tol=1e-5)


def test_line2d_parallel_and_perpendicular():
    l1 = Line2D.from_point_and_slope(Point2D(0, 0), 3.0)
    l2 = Line2D.from_point_and_slope(Point2D(1, 2), 3.0)
    l3 = Line2D.from_point_and_slope(Point2D(0, 0), -1.0 / 3.0)

    assert l1.is_parallel_to(l2)
    assert not l1.is_parallel_to(l3)
    assert l1.is_perpendicular_to(l3)
    assert not l1.is_perpendicular_to(l2)


def test_line2d_distance_between_parallel():
    # 3x + 4y - 10 = 0 ve 3x + 4y + 15 = 0 arası uzaklık |15 - (-10)| / 5 = 25 / 5 = 5.0
    l1 = Line2D(3, 4, -10)
    l2 = Line2D(3, 4, 15)
    d = l1.distance_to_parallel_line(l2)
    assert d is not None
    assert math.isclose(d, 5.0, abs_tol=1e-5)


def test_line2d_intersection():
    # y = x ve y = -x + 4 => kesişim (2, 2)
    l1 = Line2D.from_point_and_slope(Point2D(0, 0), 1.0)
    l2 = Line2D.from_point_and_slope(Point2D(0, 4), -1.0)
    p = l1.intersection_with(l2)
    assert p is not None
    assert p == Point2D(2, 2)


# ==============================================================================
# 4. CIRCLE2D OPERATIONS
# ==============================================================================

def test_circle2d_basic():
    c = Circle2D(Point2D(3, 4), 5.0)
    assert math.isclose(c.area, 25.0 * math.pi)
    assert math.isclose(c.circumference, 10.0 * math.pi)
    assert c.contains_point(Point2D(3, 4)) == "inside"
    assert c.contains_point(Point2D(0, 0)) == "on_circle"
    assert c.contains_point(Point2D(10, 10)) == "outside"


def test_circle2d_from_general_form():
    # (x - 2)^2 + (y + 3)^2 = 16 => x^2 + y^2 - 4x + 6y - 3 = 0
    # D = -4, E = 6, F = -3
    c = Circle2D.from_general_form(-4, 6, -3)
    assert c.center == Point2D(2, -3)
    assert math.isclose(c.radius, 4.0, abs_tol=1e-5)


def test_circle2d_line_relative_position():
    # Merkez (0,0), r = 5
    c = Circle2D(Point2D(0, 0), 5.0)
    secant_line = Line2D(0, 1, -3)     # y = 3 (uzaklık 3 < 5)
    tangent_line = Line2D(0, 1, -5)    # y = 5 (uzaklık 5 == 5)
    disjoint_line = Line2D(0, 1, -8)   # y = 8 (uzaklık 8 > 5)

    assert c.relative_position_with_line(secant_line) == "secant"
    assert c.relative_position_with_line(tangent_line) == "tangent"
    assert c.relative_position_with_line(disjoint_line) == "disjoint"


def test_circle2d_tangent_at_point():
    # Merkez (0,0), r = 5, nokta (3, 4)
    c = Circle2D(Point2D(0, 0), 5.0)
    tangent = c.tangent_at_point(Point2D(3, 4))
    # Yarıçap eğimi 4/3 => teğet eğimi -3/4
    assert math.isclose(tangent.slope, -3.0 / 4.0, abs_tol=1e-5)


# ==============================================================================
# 5. VECTOR2D OPERATIONS
# ==============================================================================

def test_vector2d_norm_and_ops():
    u = Vector2D(3, 4)
    assert math.isclose(u.norm, 5.0)
    v = Vector2D(1, -2)
    # Toplama
    assert u.add(v) == Vector2D(4, 2)
    # Çıkarma
    assert u.subtract(v) == Vector2D(2, 6)
    # Skaler çarpım
    assert u.scale(2.0) == Vector2D(6, 8)


def test_vector2d_dot_product():
    u = Vector2D(2, 3)
    v = Vector2D(4, -1)
    # u · v = 2*4 + 3*(-1) = 8 - 3 = 5
    assert math.isclose(u.dot_product(v), 5.0)


def test_vector2d_angle_and_orthogonality():
    u = Vector2D(1, 0)
    v = Vector2D(0, 1)
    assert u.is_orthogonal_to(v)
    assert math.isclose(u.angle_deg_with(v), 90.0)

    w = Vector2D(1, 1)
    assert math.isclose(u.angle_deg_with(w), 45.0, abs_tol=1e-4)


def test_vector2d_orthogonal_projection():
    # u = (3, 4), v = (1, 0) => proj_v(u) = (3, 0)
    u = Vector2D(3, 4)
    v = Vector2D(1, 0)
    proj = u.orthogonal_projection_onto(v)
    assert proj == Vector2D(3, 0)
    assert math.isclose(u.orthogonal_projection_length(v), 3.0)


# ==============================================================================
# 6. ANALYTICAL UTILITIES
# ==============================================================================

def test_triangle_centroid_and_area():
    p1 = Point2D(0, 0)
    p2 = Point2D(6, 0)
    p3 = Point2D(0, 8)
    g = triangle_centroid(p1, p2, p3)
    assert g == Point2D(2, 8.0 / 3.0)
    area = triangle_area(p1, p2, p3)
    assert math.isclose(area, 24.0)


def test_solve_analytic_geometry_pipeline():
    res_dist = solve_analytic_geometry("distance", x1=0, y1=0, x2=3, y2=4)
    assert res_dist["result"] == 5.0

    res_dot = solve_analytic_geometry("vector_dot", u1=1, u2=0, v1=0, v2=5)
    assert res_dot["dot_product"] == 0.0
    assert res_dot["is_orthogonal"] is True


# ==============================================================================
# 7. MISCONCEPTION RULES (BUG-ANAG-01 .. BUG-ANAG-05)
# ==============================================================================

def test_bug_anag_01_perpendicular_slope(detector):
    """BUG-ANAG-01: Dik doğrularda m1 = m2 veya m1*m2 = 1 yanılgısı."""
    diag1 = detector.detect("m1*m2 = 1", "d1 ile d2 birbirine dik", "")
    assert diag1 is not None
    assert diag1.bug_id == "BUG-ANAG-01"

    diag2 = detector.detect("m2 = m1", "d1 ve d2 doğruları dik kesişiyor", "")
    assert diag2 is not None
    assert diag2.bug_id == "BUG-ANAG-01"


def test_bug_anag_02_obtuse_slope_sign(detector):
    """BUG-ANAG-02: Geniş eğim açısında pozitif eğim alma hatası."""
    diag = detector.detect("tan(135) = 1", "Doğrunun eğim açısı 135 derecedir", "")
    assert diag is not None
    assert diag.bug_id == "BUG-ANAG-02"
    assert "GEOMETRY_OBTUSE_SLOPE_SIGN_ERROR" in diag.category


def test_bug_anag_03_circle_center_sign(detector):
    """BUG-ANAG-03: Çember merkez koordinatında işaret tersliği."""
    diag = detector.detect("M(-2, -3)", "(x - 2)^2 + (y - 3)^2 = 16", "")
    assert diag is not None
    assert diag.bug_id == "BUG-ANAG-03"
    assert "GEOMETRY_CIRCLE_CENTER_SIGN_REVERSAL" in diag.category


def test_bug_anag_04_omitted_square_root(detector):
    """BUG-ANAG-04: Uzaklık formülünde karekökü unutma."""
    diag = detector.detect("d = (x2 - x1)^2 + (y2 - y1)^2", "A(1,2) ve B(4,6) arası uzaklık", "")
    assert diag is not None
    assert diag.bug_id == "BUG-ANAG-04"
    assert "GEOMETRY_DISTANCE_OMITTED_SQUARE_ROOT" in diag.category


def test_bug_anag_05_vector_dot_vectorial_result(detector):
    """BUG-ANAG-05: Nokta çarpımında bileşenleri çarparak vektör yazma yanılgısı."""
    diag = detector.detect("u.v = (u1*v1, u2*v2)", "u = (2, 3) ve v = (4, 1) vektörlerinin iç çarpımı", "")
    assert diag is not None
    assert diag.bug_id == "BUG-ANAG-05"
    assert "GEOMETRY_VECTOR_DOT_PRODUCT_VECTORIAL_FALLACY" in diag.category


# ==============================================================================
# 8. ZERO FALSE POSITIVES & ZERO LEAKAGE
# ==============================================================================

def test_zero_false_positives_valid_geometry(detector):
    """Geçerli analitik geometri adımlarının yanlışlıkla hata olarak yakalanmadığını doğrular."""
    valid_steps = [
        ("m1 * m2 = -1", "Dik doğrular"),
        ("tan(135) = -1", "Eğim açısı"),
        ("M(2, 3)", "(x - 2)^2 + (y - 3)^2 = 16"),
        ("d = sqrt((x2 - x1)^2 + (y2 - y1)^2)", "Uzaklık hesabı"),
        ("u.v = 2*4 + 3*1 = 11", "İç çarpım"),
    ]
    for step, prev in valid_steps:
        diag = detector.detect(step, prev, "")
        assert diag is None, f"Geçerli adım '{step}' hatalı teşhis edildi: {diag.bug_id if diag else None}"


def test_zero_leakage_remediation_guardrail(detector):
    """Pedagojik hata yönlendirmelerinde cevabın ifşa edilmediğini doğrular."""
    diag = detector.detect("tan(135) = 1", "Eğim", "")
    assert diag is not None
    # Sokratik yönlendirme sadece kuralı hatırlatmalı, doğrudan nihai cevabı ifşa etmemelidir.
    assert "tan(180° - x)" in diag.remediation_directive
    assert diag.severity == "CRITICAL"


# ==============================================================================
# 9. BOUNDARY & ERROR HANDLING EDGE CASES
# ==============================================================================

def test_point2d_internal_division_invalid_ratio():
    p1 = Point2D(0, 0)
    p2 = Point2D(2, 2)
    with pytest.raises(ValueError, match="k != -1"):
        p1.internal_division(p2, -1.0)


def test_line2d_invalid_coeffs():
    with pytest.raises(ValueError, match="A ve B aynı anda sıfır olamaz"):
        Line2D(0, 0, 5)


def test_line2d_from_identical_points():
    with pytest.raises(ValueError, match="İki nokta birbirinden farklı olmalıdır"):
        Line2D.from_two_points(Point2D(1, 1), Point2D(1, 1))


def test_line2d_from_zero_intercepts():
    with pytest.raises(ValueError, match="Eksen kesimleri sıfır olamaz"):
        Line2D.from_intercepts(0, 5)


def test_circle2d_invalid_radius():
    with pytest.raises(ValueError, match="pozitif olmalıdır"):
        Circle2D(Point2D(0, 0), -2.0)


def test_circle2d_from_invalid_general_form():
    # D=2, E=2, F=10 => D^2 + E^2 - 4F = 4 + 4 - 40 = -32 < 0
    with pytest.raises(ValueError, match="reel çember belirtmez"):
        Circle2D.from_general_form(2, 2, 10)


def test_circle2d_tangent_at_external_point():
    c = Circle2D(Point2D(0, 0), 5.0)
    with pytest.raises(ValueError, match="çember üzerinde değildir"):
        c.tangent_at_point(Point2D(10, 10))


def test_vector2d_zero_vector_exceptions():
    u = Vector2D(0, 0)
    v = Vector2D(3, 4)
    with pytest.raises(ValueError, match="Sıfır vektörün açısı tanımsızdır"):
        u.angle_with(v)

    with pytest.raises(ValueError, match="Sıfır vektör üzerine izdüşüm yapılamaz"):
        v.orthogonal_projection_onto(u)

