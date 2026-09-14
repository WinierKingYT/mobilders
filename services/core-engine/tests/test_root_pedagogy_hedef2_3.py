import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.root_pedagogy.root_dag import RootPrerequisiteDAG
from app.root_pedagogy.diagnostic import ZeroBaselineDiagnostic
from app.root_pedagogy.weakness_ledger import CognitiveWeaknessLedger
from app.root_pedagogy.co_solver import ActiveCoSolverEngine
from app.root_pedagogy.sandbox import InSituRemediationSandbox
from app.root_pedagogy.models import (
    ZeroBaselineEvaluationRequest,
    CoSolveRequest,
    SandboxSessionRequest,
    WeaknessSeverity,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def detector():
    cas = SymbolicEquivalenceEngine()
    return QuadraticMisconceptionDetector(cas)


# ==========================================
# 1. ROOT PREREQUISITE DAG TESTS
# ==========================================

def test_root_dag_structure_and_nodes():
    dag = RootPrerequisiteDAG()
    assert len(dag.nodes) == 16
    for i in range(1, 17):
        node_id = f"N_ROOT_{i:02d}"
        assert node_id in dag.nodes
        assert dag.nodes[node_id].level < 0


def test_root_dag_cycle_free_and_topological_sort():
    dag = RootPrerequisiteDAG()
    # Cycle check
    dag.assert_cycle_free()
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == 16
    assert sorted_nodes[0] in ["N_ROOT_01", "N_ROOT_05"]
    assert "N_ROOT_15" in sorted_nodes[10:]


def test_root_dag_bug_mapping():
    dag = RootPrerequisiteDAG()
    assert dag.map_bug_to_root_node("BUG-FOUND-01") == "N_ROOT_04"
    assert dag.map_bug_to_root_node("BUG-FOUND-02") == "N_ROOT_08"
    assert dag.map_bug_to_root_node("BUG-FOUND-04") == "N_ROOT_07"
    assert dag.map_bug_to_root_node("BUG-FOUND-09") == "N_ROOT_11"
    assert dag.map_bug_to_root_node("BUG-FOUND-15") == "N_ROOT_15"


# ==========================================
# 2. ZERO-BASELINE DIAGNOSTIC TESTS
# ==========================================

def test_zero_baseline_all_correct():
    diag = ZeroBaselineDiagnostic()
    req = ZeroBaselineEvaluationRequest(
        student_id="s1",
        answers={"Q_ROOT_01": 2, "Q_ROOT_02": 1, "Q_ROOT_03": 1},
    )
    resp = diag.evaluate(req)
    assert resp.needs_root_pathway is False
    assert resp.score_ratio == 1.0
    assert resp.recommended_starting_node == "N01"


def test_zero_baseline_missed_q1_debt():
    diag = ZeroBaselineDiagnostic()
    req = ZeroBaselineEvaluationRequest(
        student_id="s2",
        answers={"Q_ROOT_01": 0, "Q_ROOT_02": 1, "Q_ROOT_03": 1},  # Q1 yanlış
    )
    resp = diag.evaluate(req)
    assert resp.needs_root_pathway is True
    assert resp.recommended_starting_node == "N_ROOT_01"


def test_zero_baseline_missed_q2_pemdas():
    diag = ZeroBaselineDiagnostic()
    req = ZeroBaselineEvaluationRequest(
        student_id="s3",
        answers={"Q_ROOT_01": 2, "Q_ROOT_02": 0, "Q_ROOT_03": 1},  # Q2 yanlış (14 dedi)
    )
    resp = diag.evaluate(req)
    assert resp.needs_root_pathway is True
    assert resp.recommended_starting_node == "N_ROOT_08"


def test_zero_baseline_missed_q3_balance():
    diag = ZeroBaselineDiagnostic()
    req = ZeroBaselineEvaluationRequest(
        student_id="s4",
        answers={"Q_ROOT_01": 2, "Q_ROOT_02": 1, "Q_ROOT_03": 0},  # Q3 yanlış
    )
    resp = diag.evaluate(req)
    assert resp.needs_root_pathway is True
    assert resp.recommended_starting_node == "N_ROOT_13"


# ==========================================
# 3. COGNITIVE WEAKNESS LEDGER TESTS
# ==========================================

def test_weakness_ledger_classification():
    ledger = CognitiveWeaknessLedger()

    # Slip
    e1 = ledger.log_error("st1", "N04", "x = 5", None)
    assert e1.severity == WeaknessSeverity.SLIP
    assert e1.p_l_penalty == 0.05

    # Misconception
    e2 = ledger.log_error("st1", "N10", "x(x-2)=5 => x=5", "BUG-QUAD-01")
    assert e2.severity == WeaknessSeverity.MISCONCEPTION
    assert e2.p_l_penalty == 0.15

    # Root deficit
    e3 = ledger.log_error("st1", "N01", "-(-4) = -4", "BUG-FOUND-01")
    assert e3.severity == WeaknessSeverity.ROOT_DEFICIT
    assert e3.p_l_penalty == 0.25

    entries = ledger.get_student_weaknesses("st1")
    assert len(entries) == 3


def test_weakness_ledger_trigger_sandbox():
    ledger = CognitiveWeaknessLedger()
    assert ledger.should_trigger_sandbox("st2", "BUG-FOUND-02") is True
    assert ledger.should_trigger_sandbox("st2", None) is False

    # Tekrarlayan lise hatası
    ledger.log_error("st2", "N10", "step1", "BUG-QUAD-01")
    assert ledger.should_trigger_sandbox("st2", "BUG-QUAD-01") is False
    ledger.log_error("st2", "N10", "step2", "BUG-QUAD-01")
    assert ledger.should_trigger_sandbox("st2", "BUG-QUAD-01") is True


# ==========================================
# 4. ACTIVE CO-SOLVER & HESITATION SENSOR TESTS
# ==========================================

def test_active_cosolver_linear_subgoal_flow():
    cosolver = ActiveCoSolverEngine()

    # Subgoal 1: 6 karşıya geçmeli
    req1 = CoSolveRequest(session_id="cs1", subgoal_id="SG_LIN_01", student_answer="6")
    res1 = cosolver.process_subgoal_step(req1)
    assert res1.is_valid is True
    assert res1.next_subgoal is not None
    assert res1.next_subgoal.subgoal_id == "SG_LIN_02"

    # Subgoal 2: 14 - 6 = 8
    req2 = CoSolveRequest(session_id="cs1", subgoal_id="SG_LIN_02", student_answer="8")
    res2 = cosolver.process_subgoal_step(req2)
    assert res2.is_valid is True
    assert res2.next_subgoal.subgoal_id == "SG_LIN_03"

    # Subgoal 3: 8 / 2 = 4
    req3 = CoSolveRequest(session_id="cs1", subgoal_id="SG_LIN_03", student_answer="x = 4")
    res3 = cosolver.process_subgoal_step(req3)
    assert res3.is_valid is True
    assert res3.all_completed is True


def test_active_cosolver_hesitation_sensor_and_source_unpacker():
    cosolver = ActiveCoSolverEngine()
    # 8 saniyeden uzun hareketsizlik -> fısıltı tetiklenmeli
    req = CoSolveRequest(session_id="cs2", subgoal_id="SG_LIN_01", student_answer="wrong", elapsed_seconds=9.5)
    res = cosolver.process_subgoal_step(req)
    assert res.is_valid is False
    assert res.hesitation_whisper is not None
    assert "Fısıltı" in res.hesitation_whisper
    assert res.source_unpacker_data is not None
    assert res.source_unpacker_data["subgoal_id"] == "SG_LIN_01"


# ==========================================
# 5. IN-SITU REMEDIATION SANDBOX TESTS
# ==========================================

def test_insitu_sandbox_creation_and_resolution():
    sandbox = InSituRemediationSandbox()

    req_nl = SandboxSessionRequest(student_id="st3", root_node_id="N_ROOT_02", trigger_error_step="-6 - 5 = -1")
    res_nl = sandbox.create_sandbox(req_nl)
    assert res_nl.tool_type == "NUMBER_LINE"

    # Action verification
    assert sandbox.verify_action(res_nl.sandbox_id, res_nl.tool_type, -11) is True
    assert sandbox.verify_action(res_nl.sandbox_id, res_nl.tool_type, 0) is False

    req_pie = SandboxSessionRequest(student_id="st3", root_node_id="N_ROOT_05", trigger_error_step="1/2 + 1/3")
    res_pie = sandbox.create_sandbox(req_pie)
    assert res_pie.tool_type == "PIE_FRACTION"

    req_bal = SandboxSessionRequest(student_id="st3", root_node_id="N_ROOT_15", trigger_error_step="2x+3=11")
    res_bal = sandbox.create_sandbox(req_bal)
    assert res_bal.tool_type == "BALANCE_SCALE"


# ==========================================
# 6. BUG-FOUND-01..15 MISCONCEPTION TESTS
# ==========================================

def test_bug_found_01_double_negative(detector):
    bug = detector.detect("-(-4) = -4", "isaret kurali", "-(-4) = 4")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-01"


def test_bug_found_02_pemdas_blindness(detector):
    bug = detector.detect("3 + 4*2 = 14", "islem sirasi", "3 + 8 = 11")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-02"


def test_bug_found_03_exponent_sign(detector):
    bug = detector.detect("-3^2 = 9", "uslu sayi isareti", "-3^2 = -9")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-03"


def test_bug_found_04_fraction_flat_addition(detector):
    bug = detector.detect("1/2 + 1/3 = 2/5", "kesir toplama", "5/6")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-04"


def test_bug_found_05_partial_distribution(detector):
    bug = detector.detect("2(x+3) = 2x+3", "dagilma ozelligi", "2x + 6")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-05"


def test_bug_found_06_addition_multiplication_confusion(detector):
    bug = detector.detect("x + x = x^2", "benzer terim toplama", "2x")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-06"


def test_bug_found_07_coefficient_subtraction(detector):
    bug = detector.detect("x = 9", "3x = 12", "x = 4")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-07"


def test_bug_found_08_unlike_terms_addition(detector):
    bug = detector.detect("2x + 3 = 5x", "terim birlestirme", "2x + 3")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-08"


def test_bug_found_09_exponent_base_multiplication(detector):
    bug = detector.detect("2^3 = 6", "us hesaplama", "8")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-09"


def test_bug_found_10_negative_ordering(detector):
    bug = detector.detect("-8 > -3", "sayi dogrusu siralamasi", "-8 < -3")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-10"


def test_bug_found_11_division_by_zero(detector):
    bug = detector.detect("5/0 = 0", "tanimsizlik", "tanimsiz")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-11"


def test_bug_found_12_negative_parenthesis_distribution(detector):
    bug = detector.detect("-(x - 4) = -x - 4", "eksi parantez", "-x + 4")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-12"


def test_bug_found_13_function_digit_concat(detector):
    bug = detector.detect("f(3) = 23", "f(x) = 2x", "6")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-13"


def test_bug_found_14_inequality_negative_division(detector):
    bug_direct = detector._check_bug_found_14("x < -3", "-2x < 6")
    assert bug_direct is not None
    assert bug_direct.bug_id == "BUG-FOUND-14"

    bug_gen = detector.detect("x < -3", "-2x < 6", "x > -3")
    assert bug_gen is not None
    assert bug_gen.bug_id in ["BUG-FOUND-14", "BUG-QUAD-06"]


def test_bug_found_15_one_sided_balance(detector):
    bug = detector.detect("x + 4 - 4 = 10", "terazi dengesi", "x + 4 - 4 = 10 - 4")
    assert bug is not None
    assert bug.bug_id == "BUG-FOUND-15"


def test_bug_found_zero_false_positive_on_valid(detector):
    valid_steps = [
        "-(-4) = 4",
        "3 + 4*2 = 11",
        "-3^2 = -9",
        "1/2 + 1/3 = 5/6",
        "2(x+3) = 2x + 6",
        "x + x = 2x",
        "x = 4",
        "2x + 3 = 11",
        "2^3 = 8",
        "-8 < -3",
        "-(x - 4) = -x + 4",
        "f(3) = 6",
        "x > -3",
        "x + 4 - 4 = 10 - 4",
    ]
    for s in valid_steps:
        bug = detector.detect(s, "normal adim", s)
        assert bug is None, f"False positive triggered on: {s}"


# ==========================================
# 7. ROOT PEDAGOGY API ENDPOINT TESTS
# ==========================================

def test_api_zero_baseline_diagnostic(client):
    payload = {
        "student_id": "api-st-1",
        "answers": {"Q_ROOT_01": 2, "Q_ROOT_02": 1, "Q_ROOT_03": 1},
    }
    resp = client.post("/api/v1/root/diagnostic/evaluate", json=payload)
    assert resp.status_code == 200
    assert resp.json()["needs_root_pathway"] is False


def test_api_cosolve_subgoal(client):
    payload = {
        "session_id": "api-cs-1",
        "subgoal_id": "SG_LIN_01",
        "student_answer": "6",
        "elapsed_seconds": 2.0,
    }
    resp = client.post("/api/v1/root/cosolve/subgoal", json=payload)
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is True
    assert resp.json()["subgoal_completed"] is True


def test_api_sandbox_session(client):
    payload = {
        "student_id": "api-sb-1",
        "root_node_id": "N_ROOT_02",
        "trigger_error_step": "-6 - 5 = -1",
    }
    resp = client.post("/api/v1/root/sandbox/session", json=payload)
    assert resp.status_code == 200
    assert resp.json()["tool_type"] == "NUMBER_LINE"


def test_api_weakness_ledger(client):
    # First trigger an error via cosolve
    client.post("/api/v1/root/cosolve/subgoal", json={
        "session_id": "student-weak-test",
        "subgoal_id": "SG_LIN_01",
        "student_answer": "wrong-answer",
        "elapsed_seconds": 1.0,
    })
    resp = client.get("/api/v1/root/weaknesses/student-weak-test")
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) >= 1
    assert entries[0]["severity"] == "SLIP"


def test_api_list_root_dag_nodes(client):
    resp = client.get("/api/v1/root/dag/nodes")
    assert resp.status_code == 200
    nodes = resp.json()
    assert len(nodes) == 16
    ids = [n["id"] for n in nodes]
    assert "N_ROOT_01" in ids
    assert "N_ROOT_16" in ids


def test_root_dag_prerequisites_chain():
    dag = RootPrerequisiteDAG()
    # N_ROOT_15 depends on N_ROOT_10 and N_ROOT_14
    n15 = dag.nodes["N_ROOT_15"]
    assert "N_ROOT_10" in n15.strict_prereqs
    assert "N_ROOT_14" in n15.strict_prereqs


def test_root_dag_levels_monotonicity():
    dag = RootPrerequisiteDAG()
    for n_id, node in dag.nodes.items():
        assert -3.0 <= node.level <= -1.0
        for p_id in node.strict_prereqs:
            parent = dag.nodes[p_id]
            assert parent.level <= node.level


def test_zero_baseline_mixed_answers():
    diag = ZeroBaselineDiagnostic()
    req = ZeroBaselineEvaluationRequest(
        student_id="st-mixed",
        answers={"Q_ROOT_01": 2, "Q_ROOT_02": 0, "Q_ROOT_03": 0},
    )
    res = diag.evaluate(req)
    assert res.needs_root_pathway is True
    assert abs(res.score_ratio - (1 / 3)) < 1e-4


def test_weakness_ledger_multi_student_isolation():
    ledger = CognitiveWeaknessLedger()
    ledger.log_error("alice", "N01", "-(-4)=-4", "BUG-FOUND-01")
    ledger.log_error("bob", "N02", "3+4*2=14", "BUG-FOUND-02")
    assert len(ledger.get_student_weaknesses("alice")) == 1
    assert len(ledger.get_student_weaknesses("bob")) == 1


def test_active_cosolver_distributive_flow():
    cosolver = ActiveCoSolverEngine()
    req1 = CoSolveRequest(session_id="cs-d", subgoal_id="SG_DIST_01", student_answer="3")
    res1 = cosolver.process_subgoal_step(req1)
    assert res1.is_valid is True
    assert res1.next_subgoal.subgoal_id == "SG_DIST_02"

    req2 = CoSolveRequest(session_id="cs-d", subgoal_id="SG_DIST_02", student_answer="3x")
    res2 = cosolver.process_subgoal_step(req2)
    assert res2.is_valid is True

    req3 = CoSolveRequest(session_id="cs-d", subgoal_id="SG_DIST_03", student_answer="12")
    res3 = cosolver.process_subgoal_step(req3)
    assert res3.is_valid is True
    assert res3.all_completed is True


def test_insitu_sandbox_fraction_verification():
    sandbox = InSituRemediationSandbox()
    assert sandbox.verify_action("sb1", "PIE_FRACTION", "5/6") is True
    assert sandbox.verify_action("sb1", "PIE_FRACTION", "2/5") is False


def test_insitu_sandbox_balance_verification():
    sandbox = InSituRemediationSandbox()
    assert sandbox.verify_action("sb2", "BALANCE_SCALE", 3) is True
    assert sandbox.verify_action("sb2", "BALANCE_SCALE", 99) is False


def test_api_cosolve_invalid_step(client):
    payload = {
        "session_id": "api-cs-invalid",
        "subgoal_id": "SG_LIN_01",
        "student_answer": "999",
        "elapsed_seconds": 1.0,
    }
    resp = client.post("/api/v1/root/cosolve/subgoal", json=payload)
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is False
    assert "Tekrar düşün" in resp.json()["feedback"]

