import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.modeling.models import (
    ModelingStage,
    ScaffoldStepRequest,
    ProblemCategory,
)
from app.modeling.solvers import (
    AgeProblemSolver,
    MotionProblemSolver,
    MixtureProblemSolver,
    WorkProblemSolver,
    PercentageProblemSolver,
    OptimizationProblemSolver,
)
from app.modeling.scaffold_engine import SocraticModelingScaffoldEngine


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def scaffold_engine():
    cas = SymbolicEquivalenceEngine()
    detector = QuadraticMisconceptionDetector(cas)
    return SocraticModelingScaffoldEngine(cas, detector)


# ==========================================
# 1. SOLVERS TESTS
# ==========================================

def test_age_problem_solver():
    # Şimdiki yaş x, 5 yıl sonraki yaş x + 5
    assert AgeProblemSolver.verify_age_relation("x", 5, "x + 5") is True
    assert AgeProblemSolver.verify_age_relation("3*x", 5, "3*x + 5") is True
    assert AgeProblemSolver.verify_age_relation("3*x", 5, "3*x") is False

    valid, msg = AgeProblemSolver.check_age_domain(15.0)
    assert valid is True

    valid_neg, msg_neg = AgeProblemSolver.check_age_domain(-5.0)
    assert valid_neg is False
    assert "pozitif" in msg_neg

    valid_float, msg_float = AgeProblemSolver.check_age_domain(12.7)
    assert valid_float is False
    assert "tamsayı" in msg_float


def test_motion_problem_solver():
    # 400 km, 60 km/h ve 40 km/h -> 4 saat
    t_meet = MotionProblemSolver.solve_meeting_time(400, 60, 40)
    assert abs(t_meet - 4.0) < 1e-5

    # 100 km fark, 90 km/h ve 70 km/h -> 5 saat
    t_catch = MotionProblemSolver.solve_catchup_time(100, 90, 70)
    assert abs(t_catch - 5.0) < 1e-5

    # Gidiş 60 km/h, dönüş 40 km/h -> Harmonik ortalama 48 km/h
    v_harm = MotionProblemSolver.solve_harmonic_average_speed(60, 40)
    assert abs(v_harm - 48.0) < 1e-5

    valid, _ = MotionProblemSolver.check_motion_domain(50.0, 2.5)
    assert valid is True

    invalid, _ = MotionProblemSolver.check_motion_domain(-10.0)
    assert invalid is False


def test_mixture_problem_solver():
    # 40 L %20 ve 60 L %50 -> 100 L %38
    conc = MixtureProblemSolver.calculate_mixture_concentration([40, 60], [20, 50])
    assert abs(conc - 38.0) < 1e-5

    # Saf su ekleme (yüzde 0)
    conc_water = MixtureProblemSolver.calculate_mixture_concentration([50, 50], [40, 0])
    assert abs(conc_water - 20.0) < 1e-5

    valid, _ = MixtureProblemSolver.check_mixture_domain(38.0, 100.0)
    assert valid is True

    invalid_conc, _ = MixtureProblemSolver.check_mixture_domain(120.0)
    assert invalid_conc is False


def test_work_problem_solver():
    # 6 gün ve 12 gün -> 4 gün
    t_comb = WorkProblemSolver.calculate_combined_time([6, 12])
    assert abs(t_comb - 4.0) < 1e-5

    # 3 işçi: 10, 15, 30 gün -> 1/(1/10 + 1/15 + 1/30) = 1/(3/30 + 2/30 + 1/30) = 1/(6/30) = 5 gün
    t_comb3 = WorkProblemSolver.calculate_combined_time([10, 15, 30])
    assert abs(t_comb3 - 5.0) < 1e-5

    valid, _ = WorkProblemSolver.check_work_domain(4.0)
    assert valid is True

    invalid, _ = WorkProblemSolver.check_work_domain(-3.0)
    assert invalid is False


def test_percentage_problem_solver():
    # 100 TL, +%30 zam, -%20 indirim -> 104 TL
    final_p = PercentageProblemSolver.apply_successive_percentages(100.0, [30.0, -20.0])
    assert abs(final_p - 104.0) < 1e-5

    # 100 TL maliyet, 130 TL satış -> %30 kâr
    margin = PercentageProblemSolver.calculate_profit_margin_on_cost(100.0, 130.0)
    assert abs(margin - 30.0) < 1e-5


def test_optimization_problem_solver():
    # -x^2 + 30x parabolünün tepe noktası: x = 15, y = 225
    res = OptimizationProblemSolver.find_quadratic_extremum("-x**2 + 30*x", "x")
    assert res["is_valid"] is True
    assert res["type"] == "MAXIMUM"
    assert abs(res["x_opt"] - 15.0) < 1e-5
    assert abs(res["y_opt"] - 225.0) < 1e-5


# ==========================================
# 2. BUGGY RULES TESTS (BUG-PROB-01..10)
# ==========================================

def test_bug_prob_01_age_shift_asymmetry(scaffold_engine):
    bug = scaffold_engine.detector.detect("x + 5 = 2*y", "5 yil sonraki yas problemi", "(x+5)+(3x+5)=50")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-01"


def test_bug_prob_02_speed_time_inverse_ratio(scaffold_engine):
    bug = scaffold_engine.detector.detect("v1/v2 = t1/t2", "hareket problemi", "v1*t1 = v2*t2")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-02"


def test_bug_prob_03_average_speed_arithmetic_mean(scaffold_engine):
    bug = scaffold_engine.detector.detect("vort = (60+40)/2 = 50", "ortalama hiz problemi 60 ve 40", "v_ort=48")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-03"


def test_bug_prob_04_percentage_reversal_fallacy(scaffold_engine):
    bug = scaffold_engine.detector.detect("1.20*0.80 = 1", "yuzde zam ve indirim", "1.30*0.80=1.04")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-04"


def test_bug_prob_05_mixture_solvent_confusion(scaffold_engine):
    bug = scaffold_engine.detector.detect("yuzde = tuz/su", "karisim yuzdesi", "40*20+60*50=100*x")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-05"


def test_bug_prob_06_work_time_linear_addition(scaffold_engine):
    bug = scaffold_engine.detector.detect("6 + 3 = 9 gun", "birlikte calisan isciler 6 ve 3 gun", "1/6+1/3=1/t")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-06"


def test_bug_prob_07_relative_velocity_sign_inversion(scaffold_engine):
    bug = scaffold_engine.detector.detect("karsilasma = (v1-v2)*t", "karsit yonlu hareket", "(v1+v2)*t=x")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-07"


def test_bug_prob_08_profit_base_confusion(scaffold_engine):
    bug = scaffold_engine.detector.detect("kar = satis * yuzde", "maliyet uzerinden kar", "satis = maliyet*(1+kar)")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-08"


def test_bug_prob_09_unit_inconsistency(scaffold_engine):
    bug = scaffold_engine.detector.detect("x = 60 * 20", "20 dakika yolculuk hizi 60 km/h", "x = 60 * (20/60)")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-09"


def test_bug_prob_10_real_world_domain_invalidation(scaffold_engine):
    bug = scaffold_engine.detector.detect("x = -5", "yas problemi sonucu", "10")
    assert bug is not None
    assert bug.bug_id == "BUG-PROB-10"


def test_bug_prob_zero_false_positive_on_valid_equations(scaffold_engine):
    # Geçerli denklemler asla BUG-PROB vermemeli
    valid_eqs = [
        "(x + 5) + (3*x + 5) = 50",
        "(60 + 40) * t = 400",
        "40 * 20 + 60 * 50 = 100 * x",
        "1/6 + 1/12 = 1/t",
        "100 * 1.30 * 0.80 = 100 + k",
    ]
    for eq in valid_eqs:
        bug = scaffold_engine.detector.detect(eq, "problem cozumu", eq)
        assert bug is None, f"False positive detected on valid equation: {eq}"


# ==========================================
# 3. SCAFFOLD ENGINE FLOW TESTS
# ==========================================

def test_scaffold_flow_age_problem(scaffold_engine):
    # Stage 1: Variable Definition
    req1 = ScaffoldStepRequest(
        session_id="s1",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="x = oğlun yaşı",
    )
    res1 = scaffold_engine.evaluate_step(req1)
    assert res1.is_valid is True
    assert res1.stage_completed is True
    assert res1.next_stage == ModelingStage.STAGE_2_EQUATION

    # Stage 2: Equation Formulation
    req2 = ScaffoldStepRequest(
        session_id="s1",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="(x + 5) + (3*x + 5) = 50",
    )
    res2 = scaffold_engine.evaluate_step(req2)
    assert res2.is_valid is True
    assert res2.stage_completed is True
    assert res2.next_stage == ModelingStage.STAGE_3_SOLVE

    # Stage 3: Solve Step
    req3 = ScaffoldStepRequest(
        session_id="s1",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="x = 10",
    )
    res3 = scaffold_engine.evaluate_step(req3)
    assert res3.is_valid is True
    assert res3.stage_completed is True
    assert res3.domain_valid is True


def test_scaffold_flow_motion_problem(scaffold_engine):
    # Stage 1
    req1 = ScaffoldStepRequest(
        session_id="s2",
        problem_id="PROB_MOTION_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="t",
    )
    res1 = scaffold_engine.evaluate_step(req1)
    assert res1.is_valid is True

    # Stage 2
    req2 = ScaffoldStepRequest(
        session_id="s2",
        problem_id="PROB_MOTION_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="(60 + 40) * t = 400",
    )
    res2 = scaffold_engine.evaluate_step(req2)
    assert res2.is_valid is True

    # Stage 3
    req3 = ScaffoldStepRequest(
        session_id="s2",
        problem_id="PROB_MOTION_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="4",
    )
    res3 = scaffold_engine.evaluate_step(req3)
    assert res3.is_valid is True
    assert res3.domain_valid is True


def test_scaffold_flow_mixture_problem(scaffold_engine):
    # Stage 1
    req1 = ScaffoldStepRequest(
        session_id="s3",
        problem_id="PROB_MIXTURE_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="x",
    )
    res1 = scaffold_engine.evaluate_step(req1)
    assert res1.is_valid is True

    # Stage 2
    req2 = ScaffoldStepRequest(
        session_id="s3",
        problem_id="PROB_MIXTURE_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="40 * 20 + 60 * 50 = 100 * x",
    )
    res2 = scaffold_engine.evaluate_step(req2)
    assert res2.is_valid is True

    # Stage 3
    req3 = ScaffoldStepRequest(
        session_id="s3",
        problem_id="PROB_MIXTURE_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="x = 38",
    )
    res3 = scaffold_engine.evaluate_step(req3)
    assert res3.is_valid is True
    assert res3.domain_valid is True


def test_scaffold_flow_work_problem(scaffold_engine):
    # Stage 1
    req1 = ScaffoldStepRequest(
        session_id="s4",
        problem_id="PROB_WORK_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="t",
    )
    res1 = scaffold_engine.evaluate_step(req1)
    assert res1.is_valid is True

    # Stage 2
    req2 = ScaffoldStepRequest(
        session_id="s4",
        problem_id="PROB_WORK_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="1/6 + 1/12 = 1/t",
    )
    res2 = scaffold_engine.evaluate_step(req2)
    assert res2.is_valid is True

    # Stage 3
    req3 = ScaffoldStepRequest(
        session_id="s4",
        problem_id="PROB_WORK_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="4",
    )
    res3 = scaffold_engine.evaluate_step(req3)
    assert res3.is_valid is True


def test_scaffold_flow_percent_problem(scaffold_engine):
    # Stage 1
    req1 = ScaffoldStepRequest(
        session_id="s5",
        problem_id="PROB_PERCENT_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="k",
    )
    res1 = scaffold_engine.evaluate_step(req1)
    assert res1.is_valid is True

    # Stage 2
    req2 = ScaffoldStepRequest(
        session_id="s5",
        problem_id="PROB_PERCENT_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="100 * 1.30 * 0.80 = 100 + k",
    )
    res2 = scaffold_engine.evaluate_step(req2)
    assert res2.is_valid is True

    # Stage 3
    req3 = ScaffoldStepRequest(
        session_id="s5",
        problem_id="PROB_PERCENT_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="4",
    )
    res3 = scaffold_engine.evaluate_step(req3)
    assert res3.is_valid is True


def test_scaffold_flow_optimization_problem(scaffold_engine):
    req1 = ScaffoldStepRequest(
        session_id="s6",
        problem_id="PROB_OPTIMIZATION_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="x",
    )
    res1 = scaffold_engine.evaluate_step(req1)
    assert res1.is_valid is True

    req2 = ScaffoldStepRequest(
        session_id="s6",
        problem_id="PROB_OPTIMIZATION_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="x * (30 - x) = 225",
    )
    res2 = scaffold_engine.evaluate_step(req2)
    assert res2.is_valid is True

    req3 = ScaffoldStepRequest(
        session_id="s6",
        problem_id="PROB_OPTIMIZATION_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="15",
    )
    res3 = scaffold_engine.evaluate_step(req3)
    assert res3.is_valid is True


def test_scaffold_stage_1_invalid_variable(scaffold_engine):
    req = ScaffoldStepRequest(
        session_id="s7",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_1_VARIABLE,
        student_input="bilinmeyen sayı zzzz",
    )
    res = scaffold_engine.evaluate_step(req)
    assert res.is_valid is False
    assert res.stage_completed is False
    assert "Seçtiğin değişken" in res.socratic_feedback


def test_scaffold_stage_2_buggy_rule_feedback(scaffold_engine):
    # Öğrenci zaman kayması hatası yaptı
    req = ScaffoldStepRequest(
        session_id="s8",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="x + 5 = 2y",
    )
    res = scaffold_engine.evaluate_step(req)
    assert res.is_valid is False
    assert res.detected_bug is not None
    assert res.detected_bug.bug_id == "BUG-PROB-01"
    assert "t yıl sonra" in res.socratic_feedback


def test_scaffold_stage_3_zero_leakage_shield(scaffold_engine):
    # Yanlış cevap verildiğinde doğru cevap asla sızdırılmamalı
    req = ScaffoldStepRequest(
        session_id="s9",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="x = 18",
    )
    res = scaffold_engine.evaluate_step(req)
    assert res.is_valid is False
    assert "10" not in res.socratic_feedback, "Shield failure: Correct root leaked in Socratic feedback!"


def test_scaffold_stage_3_negative_domain_rejection(scaffold_engine):
    # Negatif yaş girişi
    req = ScaffoldStepRequest(
        session_id="s10",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="x = -5",
    )
    res = scaffold_engine.evaluate_step(req)
    assert res.is_valid is False
    assert res.domain_valid is False
    assert "pozitif" in res.socratic_feedback or res.detected_bug is not None


# ==========================================
# 4. FASTAPI ENDPOINT TESTS
# ==========================================

def test_api_list_modeling_problems(client):
    response = client.get("/api/v1/modeling/problems")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 6
    ids = [p["id"] for p in data]
    assert "PROB_AGE_01" in ids
    assert "PROB_MOTION_01" in ids
    assert "PROB_MIXTURE_01" in ids


def test_api_get_modeling_problem_found(client):
    response = client.get("/api/v1/modeling/problem/PROB_MOTION_01")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "PROB_MOTION_01"
    assert data["category"] == "MOTION"
    assert data["schematic"] is not None
    assert data["schematic"]["diagram_type"] == "MOTION_TIMELINE"


def test_api_get_modeling_problem_not_found(client):
    response = client.get("/api/v1/modeling/problem/PROB_UNKNOWN_99")
    assert response.status_code == 404


def test_api_scaffold_step_endpoint(client):
    payload = {
        "session_id": "test-session-101",
        "problem_id": "PROB_AGE_01",
        "stage": "STAGE_1_VARIABLE",
        "student_input": "x",
    }
    response = client.post("/api/v1/modeling/scaffold/step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["stage_completed"] is True
    assert data["next_stage"] == "STAGE_2_EQUATION"


def test_work_solver_negative_time_raises():
    with pytest.raises(ValueError):
        WorkProblemSolver.calculate_combined_time([6, -2])


def test_motion_solver_invalid_direction_raises():
    with pytest.raises(ValueError):
        MotionProblemSolver.solve_catchup_time(100, 60, 80)


def test_mixture_pure_solute_addition():
    # 80 L %10 karışımına 20 L saf tuz (%100) ekleme
    conc = MixtureProblemSolver.calculate_mixture_concentration([80, 20], [10, 100])
    assert abs(conc - 28.0) < 1e-5


def test_percentage_loss_application():
    # 200 TL maliyet, 160 TL satış -> %20 zarar (-20%)
    margin = PercentageProblemSolver.calculate_profit_margin_on_cost(200.0, 160.0)
    assert abs(margin - (-20.0)) < 1e-5


def test_optimization_invalid_poly():
    res = OptimizationProblemSolver.find_quadratic_extremum("sin(x) + 5", "x")
    assert res["is_valid"] is False


def test_api_scaffold_stage_2_via_api(client):
    payload = {
        "session_id": "api-sess-2",
        "problem_id": "PROB_AGE_01",
        "stage": "STAGE_2_EQUATION",
        "student_input": "4*x + 10 = 50",
    }
    resp = client.post("/api/v1/modeling/scaffold/step", json=payload)
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is True
    assert resp.json()["next_stage"] == "STAGE_3_SOLVE"


def test_api_scaffold_stage_3_via_api(client):
    payload = {
        "session_id": "api-sess-3",
        "problem_id": "PROB_AGE_01",
        "stage": "STAGE_3_SOLVE",
        "student_input": "10",
    }
    resp = client.post("/api/v1/modeling/scaffold/step", json=payload)
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is True
    assert resp.json()["stage_completed"] is True


def test_api_scaffold_invalid_problem_id(client):
    payload = {
        "session_id": "api-sess-4",
        "problem_id": "PROB_NOT_EXIST",
        "stage": "STAGE_1_VARIABLE",
        "student_input": "x",
    }
    resp = client.post("/api/v1/modeling/scaffold/step", json=payload)
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is False
    assert "bulunamadı" in resp.json()["socratic_feedback"]


def test_alternative_equation_acceptance_stage_2(scaffold_engine):
    req = ScaffoldStepRequest(
        session_id="alt-eq-test",
        problem_id="PROB_MOTION_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="60*t + 40*t = 400",
    )
    res = scaffold_engine.evaluate_step(req)
    assert res.is_valid is True
    assert res.stage_completed is True


def test_upper_domain_bound_violation(scaffold_engine):
    # Yaşın 120 üst sınırını aşması
    req = ScaffoldStepRequest(
        session_id="bound-test",
        problem_id="PROB_AGE_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="x = 145",
    )
    res = scaffold_engine.evaluate_step(req)
    assert res.is_valid is False
    assert res.domain_valid is False
    assert "maksimum" in res.socratic_feedback


def test_modeling_scaffold_persists_to_cognitive_mistake_vault():
    """Modelleme aşamasında oluşan BUG-PROB hataları Bilişsel Hata Kasasına otomatik kaydedilmelidir."""
    from app.vault.mistake_vault import CognitiveMistakeVault
    cas = SymbolicEquivalenceEngine()
    detector = QuadraticMisconceptionDetector(cas)
    vault = CognitiveMistakeVault()
    engine = SocraticModelingScaffoldEngine(cas_engine=cas, detector=detector, vault=vault)

    # Aşama 2: İşçi probleminde düz toplama hatası (BUG-PROB-06)
    req = ScaffoldStepRequest(
        session_id="vault-test-sess",
        problem_id="PROB_WORK_01",
        stage=ModelingStage.STAGE_2_EQUATION,
        student_input="6 + 12 = 18 gun",
        student_id="student_model_vault_99",
    )
    res = engine.evaluate_step(req)
    assert res.is_valid is False
    assert res.detected_bug is not None
    assert res.detected_bug.bug_id == "BUG-PROB-06"

    mistakes = vault.list_mistakes(user_id="student_model_vault_99")
    assert len(mistakes) == 1
    assert mistakes[0].bug_id == "BUG-PROB-06"
    assert mistakes[0].node_id == "N04"
    assert "1/t" in mistakes[0].remediation_directive or "kapasite" in mistakes[0].remediation_directive


def test_modeling_scaffold_stage3_domain_violation_vault_record():
    """Aşama 3'te gerçek dünya kısıtı ihlali (BUG-PROB-10) olduğunda kasaya kaydedilmelidir."""
    from app.vault.mistake_vault import CognitiveMistakeVault
    cas = SymbolicEquivalenceEngine()
    detector = QuadraticMisconceptionDetector(cas)
    vault = CognitiveMistakeVault()
    engine = SocraticModelingScaffoldEngine(cas_engine=cas, detector=detector, vault=vault)

    req = ScaffoldStepRequest(
        session_id="vault-test-sess-dom",
        problem_id="PROB_MOTION_01",
        stage=ModelingStage.STAGE_3_SOLVE,
        student_input="t = -4 saat",
        student_id="student_domain_vault_01",
    )
    res = engine.evaluate_step(req)
    assert res.is_valid is False
    assert res.domain_valid is False

    mistakes = vault.list_mistakes(user_id="student_domain_vault_01")
    assert len(mistakes) == 1
    assert mistakes[0].bug_id == "BUG-PROB-10"
    assert "pozitif" in mistakes[0].remediation_directive.lower() or "negatif" in mistakes[0].remediation_directive.lower()


def test_api_scaffold_step_with_student_id_vault_integration(client):
    """API endpoint üzerinden gönderilen modelleme adımında oluşan hata kasaya işlenmelidir."""
    from app.api.endpoints import cognitive_mistake_vault
    payload = {
        "session_id": "api-sess-vault-02",
        "problem_id": "PROB_PERCENT_01",
        "stage": "STAGE_2_EQUATION",
        "student_input": "1.20*0.80 = 1",
        "student_id": "STU_API_PERCENT_01",
    }
    resp = client.post("/api/v1/modeling/scaffold/step", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert data["detected_bug"]["bug_id"] == "BUG-PROB-04"

    # Vault kontrolü
    user_mistakes = cognitive_mistake_vault.list_mistakes(user_id="STU_API_PERCENT_01")
    matching = [m for m in user_mistakes if m.bug_id == "BUG-PROB-04"]
    assert len(matching) >= 1
    assert "çarpan" in matching[0].remediation_directive or "nötrlemez" in matching[0].correct_principle


def test_scaffold_all_ten_bug_prob_remediations(scaffold_engine):
    """Tüm 10 modelleme yanılgısı (BUG-PROB-01..10) için Sokratik rehberlik ve kural doğrulaması."""
    test_cases = [
        ("BUG-PROB-01", "x + 5 = 2y", "5 yil sonra", "(x+5)+(3x+5)=50", "eşit akar"),
        ("BUG-PROB-02", "v1/v2 = t1/t2", "hareket", "v1*t1 = v2*t2", "ters orantılı"),
        ("BUG-PROB-03", "vort = (60+40)/2 = 50", "ortalama hiz", "v_ort=48", "harmonik"),
        ("BUG-PROB-04", "1.20*0.80 = 1", "yuzde", "1.30*0.80=1.04", "nötrlemez"),
        ("BUG-PROB-05", "yuzde = tuz/su", "karisim", "40*20+60*50=100*x", "toplam"),
        ("BUG-PROB-06", "6 + 3 = 9 gun", "isciler", "1/6+1/3=1/t", "toplanamaz"),
        ("BUG-PROB-07", "karsilasma = (v1-v2)*t", "karsit yonlu", "(v1+v2)*t=x", "topla"),
        ("BUG-PROB-08", "kar = satis * yuzde", "maliyet", "satis = maliyet*(1+kar)", "maliyet"),
        ("BUG-PROB-09", "x = 60 * 20", "20 dakika 60 km/h", "x = 60 * (20/60)", "dakika"),
        ("BUG-PROB-10", "x = -5", "yas", "10", "negatif"),
    ]
    for bug_id, student_in, prev_step, target_eq, keyword in test_cases:
        bug = scaffold_engine.detector.detect(student_in, prev_step, target_eq)
        assert bug is not None, f"Failed to detect {bug_id} for input '{student_in}'"
        assert bug.bug_id == bug_id
        combined = (bug.remediation_directive + " " + bug.description).lower()
        assert keyword in combined, f"Keyword '{keyword}' not in combined text: {combined}"

