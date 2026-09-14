import pytest
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.misconceptions.clustering import UnsupervisedErrorClusterer


@pytest.fixture
def detector():
    return QuadraticMisconceptionDetector()


def test_bug_quad_06_inequality_sign_reversal(detector):
    # Student divided by -2 but kept < instead of flipping to >
    res = detector.detect(
        user_step_str="x < -3",
        previous_step_str="-2x < 6",
        target_equation_str="-2x < 6",
    )
    assert res is not None
    assert res.bug_id == "BUG-QUAD-06"
    assert "yön" in res.description.lower() or "negatif" in res.description.lower()


def test_bug_quad_07_sign_table_double_root(detector):
    # Student writes x <= 2 for (x - 2)^2 <= 0
    res = detector.detect(
        user_step_str="x <= 2",
        previous_step_str="(x - 2)**2 <= 0",
        target_equation_str="(x - 2)**2 <= 0",
    )
    assert res is not None
    assert res.bug_id == "BUG-QUAD-07"
    assert "çift katlı" in res.description.lower()


def test_bug_quad_08_parabola_vertex_sign(detector):
    # For x^2 - 6x + 5 = 0, true r = -(-6)/2 = 3. Student computes r = -6/2 = -3.
    res = detector.detect(
        user_step_str="r = -3",
        previous_step_str="x**2 - 6*x + 5 = 0",
        target_equation_str="x**2 - 6*x + 5 = 0",
    )
    assert res is not None
    assert res.bug_id == "BUG-QUAD-08"
    assert "tepe noktası" in res.description.lower()


def test_bug_quad_09_horizontal_transformation_direction(detector):
    # Student states that f(x - 3) means shifting left (sola)
    res = detector.detect(
        user_step_str="grafik sola 3 birim ötelenir",
        previous_step_str="f(x) = (x - 3)**2",
        target_equation_str="f(x) = (x - 3)**2",
    )
    assert res is not None
    assert res.bug_id == "BUG-QUAD-09"
    assert "sağa" in res.description.lower()


def test_bug_quad_10_inequality_region_inversion(detector):
    # For (x - 1)(x - 3) > 0, roots are 1 and 3. Outside roots is correct, but student chooses (1, 3).
    res = detector.detect(
        user_step_str="(1, 3)",
        previous_step_str="(x - 1)*(x - 3) > 0",
        target_equation_str="x**2 - 4*x + 3 > 0",
    )
    assert res is not None
    assert res.bug_id == "BUG-QUAD-10"
    assert "köklerin" in res.description.lower() or "bölge" in res.description.lower()


def test_negative_controls_no_false_positive(detector):
    # Correct flipping: -2x < 6 => x > -3 (should NOT trigger bug6)
    res_correct_flip = detector.detect(
        user_step_str="x > -3",
        previous_step_str="-2x < 6",
        target_equation_str="-2x < 6",
    )
    assert res_correct_flip is None or res_correct_flip.bug_id != "BUG-QUAD-06"

    # Correct vertex: x^2 - 6x + 5 => r = 3 (should NOT trigger bug8)
    res_correct_vertex = detector.detect(
        user_step_str="r = 3",
        previous_step_str="x**2 - 6*x + 5 = 0",
        target_equation_str="x**2 - 6*x + 5 = 0",
    )
    assert res_correct_vertex is None


def test_unsupervised_error_clustering():
    clusterer = UnsupervisedErrorClusterer(n_clusters=3)
    sample_errors = [
        {"user_step": "x < -3", "previous_step": "-2x < 6", "student_id": "S1"},
        {"user_step": "x <= -5", "previous_step": "-x <= 5", "student_id": "S2"},
        {"user_step": "r = -3", "previous_step": "x**2 - 6*x + 5 = 0", "student_id": "S3"},
        {"user_step": "r = -2", "previous_step": "x**2 - 4*x + 1 = 0", "student_id": "S4"},
        {"user_step": "(1, 3)", "previous_step": "(x - 1)*(x - 3) > 0", "student_id": "S5"},
        {"user_step": "(-2, 4)", "previous_step": "(x + 2)*(x - 4) > 0", "student_id": "S6"},
    ]
    clusters = clusterer.cluster_errors(sample_errors)
    assert len(clusters) == 3
    for c_id, c_data in clusters.items():
        assert "candidate_rule" in c_data
        assert c_data["count"] > 0
        assert len(c_data["exemplars"]) > 0
