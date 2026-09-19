"""
Hedef 15: Matematiksel İspat ve Mantık Laboratuvarı ("Nedenini Anla") Test Paketi.
Önermeler mantığı, doğruluk tabloları, totoloji/çelişki, niceleyiciler, çıkarım kuralları,
olmayana ergi (çelişki), tümevarım, teorem kataloğu, safsata teşhisi (BUG-LOGIC-01..05)
ve FastAPI REST API uç noktalarının doğrulanması.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.logic.proof_lab import (
    logic_not,
    logic_and,
    logic_or,
    logic_xor,
    logic_implies,
    logic_iff,
    TruthTableGenerator,
    InferenceRuleVerifier,
    ProofVerifier,
    MathematicalInductionEngine,
    QuantifierEngine,
    ProofCatalog,
    ProofChecker,
)
from app.misconceptions.detector import QuadraticMisconceptionDetector as MisconceptionDetector


# =====================================================================
# 1. ÖNERMELER MANTIĞI VE BAĞLAÇLAR TESTLERİ
# =====================================================================

def test_logic_connectives_basic_not_and_or_xor():
    # NOT
    assert logic_not(True) is False
    assert logic_not(False) is True

    # AND
    assert logic_and(True, True) is True
    assert logic_and(True, False) is False
    assert logic_and(False, True) is False
    assert logic_and(False, False) is False

    # OR
    assert logic_or(True, True) is True
    assert logic_or(True, False) is True
    assert logic_or(False, True) is True
    assert logic_or(False, False) is False

    # XOR
    assert logic_xor(True, True) is False
    assert logic_xor(True, False) is True
    assert logic_xor(False, True) is True
    assert logic_xor(False, False) is False


def test_logic_implies_table():
    # 1 => 1 = 1, 1 => 0 = 0, 0 => 1 = 1, 0 => 0 = 1
    assert logic_implies(True, True) is True
    assert logic_implies(True, False) is False
    assert logic_implies(False, True) is True
    assert logic_implies(False, False) is True


def test_logic_iff_table():
    # 1 <=> 1 = 1, 1 <=> 0 = 0, 0 <=> 1 = 0, 0 <=> 0 = 1
    assert logic_iff(True, True) is True
    assert logic_iff(True, False) is False
    assert logic_iff(False, True) is False
    assert logic_iff(False, False) is True


# =====================================================================
# 2. DOĞRULUK TABLOSU MOTORU TESTLERİ
# =====================================================================

def test_truth_table_generator_single_variable():
    table = TruthTableGenerator.generate_table(["p"], lambda env: logic_not(env["p"]))
    assert table["row_count"] == 2
    assert table["variables"] == ["p"]
    assert table["is_contingency"] is True


def test_truth_table_generator_two_variables():
    table = TruthTableGenerator.generate_table(
        ["p", "q"], lambda env: logic_and(env["p"], env["q"])
    )
    assert table["row_count"] == 4
    assert table["is_tautology"] is False
    assert table["is_contradiction"] is False
    assert table["is_contingency"] is True


def test_truth_table_generator_tautology():
    # p ∨ ¬p is a tautology
    table = TruthTableGenerator.generate_table(
        ["p"], lambda env: logic_or(env["p"], logic_not(env["p"]))
    )
    assert table["is_tautology"] is True
    assert table["is_contradiction"] is False
    assert table["is_contingency"] is False


def test_truth_table_generator_contradiction():
    # p ∧ ¬p is a contradiction
    table = TruthTableGenerator.generate_table(
        ["p"], lambda env: logic_and(env["p"], logic_not(env["p"]))
    )
    assert table["is_tautology"] is False
    assert table["is_contradiction"] is True
    assert table["is_contingency"] is False


def test_truth_table_empty_variables_raises():
    with pytest.raises(ValueError):
        TruthTableGenerator.generate_table([], lambda env: True)


def test_de_morgan_laws_equivalence():
    # ¬(p ∧ q) ≡ ¬p ∨ ¬q
    equiv_1 = TruthTableGenerator.verify_equivalence(
        ["p", "q"],
        lambda env: logic_not(logic_and(env["p"], env["q"])),
        lambda env: logic_or(logic_not(env["p"]), logic_not(env["q"])),
    )
    assert equiv_1 is True

    # ¬(p ∨ q) ≡ ¬p ∧ ¬q
    equiv_2 = TruthTableGenerator.verify_equivalence(
        ["p", "q"],
        lambda env: logic_not(logic_or(env["p"], env["q"])),
        lambda env: logic_and(logic_not(env["p"]), logic_not(env["q"])),
    )
    assert equiv_2 is True


def test_conditional_contrapositive_equivalence():
    # (p ⇒ q) ≡ (¬q ⇒ ¬p)
    equiv = TruthTableGenerator.verify_equivalence(
        ["p", "q"],
        lambda env: logic_implies(env["p"], env["q"]),
        lambda env: logic_implies(logic_not(env["q"]), logic_not(env["p"])),
    )
    assert equiv is True


def test_conditional_or_equivalence():
    # (p ⇒ q) ≡ (¬p ∨ q)
    equiv = TruthTableGenerator.verify_equivalence(
        ["p", "q"],
        lambda env: logic_implies(env["p"], env["q"]),
        lambda env: logic_or(logic_not(env["p"]), env["q"]),
    )
    assert equiv is True


# =====================================================================
# 3. ÇIKARIM KURALLARI (INFERENCE RULES) TESTLERİ
# =====================================================================

def test_inference_modus_ponens():
    assert InferenceRuleVerifier.modus_ponens(True, True) is True
    assert InferenceRuleVerifier.modus_ponens(False, True) is None
    assert InferenceRuleVerifier.modus_ponens(True, False) is None


def test_inference_modus_tollens():
    assert InferenceRuleVerifier.modus_tollens(True, True) is True
    assert InferenceRuleVerifier.modus_tollens(False, True) is None


def test_inference_hypothetical_syllogism():
    assert InferenceRuleVerifier.hypothetical_syllogism(True, True) is True
    assert InferenceRuleVerifier.hypothetical_syllogism(True, False) is None


def test_inference_disjunctive_syllogism():
    assert InferenceRuleVerifier.disjunctive_syllogism(True, True) is True
    assert InferenceRuleVerifier.disjunctive_syllogism(False, True) is None


# =====================================================================
# 4. İSPAT YÖNTEMLERİ (PROOF METHODS) TESTLERİ
# =====================================================================

def test_proof_verifier_contrapositive():
    valid = ProofVerifier.verify_contrapositive(
        lambda p, q: logic_implies(p, q),
        lambda p, q: logic_implies(logic_not(q), logic_not(p)),
    )
    assert valid is True


def test_proof_verifier_contradiction_flow_valid():
    steps = [
        lambda: True,
        lambda: True,
        lambda: True,
    ]
    res = ProofVerifier.verify_contradiction_flow(
        hypothesis=True,
        negated_claim=True,
        deduction_steps=steps,
        produces_contradiction=True,
    )
    assert res["proof_valid"] is True
    assert "ispatlandı" in res["conclusion"]


def test_proof_verifier_contradiction_flow_invalid():
    steps = [lambda: True, lambda: False]
    res = ProofVerifier.verify_contradiction_flow(
        hypothesis=True,
        negated_claim=True,
        deduction_steps=steps,
        produces_contradiction=True,
    )
    assert res["proof_valid"] is False


def test_proof_verifier_counterexample_found():
    # ∀x ∈ [1, 2, 3, 4], x < 3  -> 3 and 4 are counterexamples
    res = ProofVerifier.find_counterexample([1, 2, 3, 4], lambda x: x < 3)
    assert res["counterexample_found"] is True
    assert res["counterexample_value"] == 3


def test_proof_verifier_counterexample_none():
    res = ProofVerifier.find_counterexample([1, 2, 3], lambda x: x > 0)
    assert res["counterexample_found"] is False
    assert res["counterexample_value"] is None


# =====================================================================
# 5. MATEMATİKSEL TÜMEVARIM TESTLERİ
# =====================================================================

def test_induction_verify_base_case():
    assert MathematicalInductionEngine.verify_base_case(lambda n: n * (n + 1) % 2 == 0, base_n=1) is True
    assert MathematicalInductionEngine.verify_base_case(lambda n: n > 5, base_n=1) is False


def test_induction_simulate_inductive_step_gauss():
    # Gauss: 1 + ... + n = n(n+1)/2
    pred = lambda n: sum(range(1, n + 1)) == (n * (n + 1)) // 2
    res = MathematicalInductionEngine.simulate_inductive_step(pred, start_k=1, test_range=10)
    assert res["all_steps_valid"] is True
    assert len(res["domino_chain"]) == 10


def test_induction_simulate_inductive_step_inequality():
    # 2^n > n for n >= 1
    pred = lambda n: (2 ** n) > n
    res = MathematicalInductionEngine.simulate_inductive_step(pred, start_k=1, test_range=8)
    assert res["all_steps_valid"] is True


def test_induction_scaffold_zero_leakage():
    scaffold = MathematicalInductionEngine.scaffold_induction_proof(
        claim_name="Gauss Toplam Formülü",
        formula_str="1 + ... + n = n(n+1)/2",
        base_n=1,
    )
    assert scaffold["base_n"] == 1
    assert len(scaffold["stages"]) == 3
    assert scaffold["stages"][0]["title"] == "Taban Adımı (Base Case)"
    assert scaffold["stages"][1]["title"] == "Tümevarım Hipotezi (Inductive Hypothesis)"
    assert scaffold["stages"][2]["title"] == "Tümevarım Adımı (Inductive Step)"


# =====================================================================
# 6. NİCELEYİCİLER (QUANTIFIERS) TESTLERİ
# =====================================================================

def test_quantifier_universal_valid_and_counterexample():
    # ∀x ∈ [2, 4, 6], x is even -> True
    res_true = QuantifierEngine.evaluate_universal([2, 4, 6], lambda x: x % 2 == 0)
    assert res_true["is_true"] is True
    assert res_true["counterexample"] is None

    # ∀x ∈ [2, 4, 5, 6], x is even -> False, counterexample=5
    res_false = QuantifierEngine.evaluate_universal([2, 4, 5, 6], lambda x: x % 2 == 0)
    assert res_false["is_true"] is False
    assert res_false["counterexample"] == 5


def test_quantifier_existential_valid_and_witness():
    # ∃x ∈ [1, 3, 4], x is even -> True, witness=4
    res_true = QuantifierEngine.evaluate_existential([1, 3, 4], lambda x: x % 2 == 0)
    assert res_true["is_true"] is True
    assert res_true["witness"] == 4

    # ∃x ∈ [1, 3, 5], x is even -> False
    res_false = QuantifierEngine.evaluate_existential([1, 3, 5], lambda x: x % 2 == 0)
    assert res_false["is_true"] is False
    assert res_false["witness"] is None


def test_quantifier_negation_universal():
    res = QuantifierEngine.negate_quantified_statement("forall", "x > 0", "x <= 0")
    assert "∃x" in res["negation"]
    assert "x <= 0" in res["negation"]


def test_quantifier_negation_existential():
    res = QuantifierEngine.negate_quantified_statement("exists", "x^2 = 2", "x^2 != 2")
    assert "∀x" in res["negation"]
    assert "x^2 != 2" in res["negation"]


# =====================================================================
# 7. TEOREM İSPAT KATALOĞU VE DENETLEYİCİSİ TESTLERİ
# =====================================================================

def test_proof_catalog_contains_theorems():
    theorems = ProofCatalog.get_all_theorems()
    assert len(theorems) >= 6
    ids = [t["id"] for t in theorems]
    assert "THM-IRR-SQRT2" in ids
    assert "THM-EUCLID-PRIMES" in ids
    assert "THM-GAUSS-SUM" in ids
    assert "THM-EXP-INEQ" in ids
    assert "THM-SUM-EVENS" in ids
    assert "THM-CONTRAPOSITIVE-SQUARE" in ids


def test_proof_checker_valid_step():
    res = ProofChecker.verify_step(
        theorem_id="THM-IRR-SQRT2",
        step_number=1,
        student_statement="Varsayalim ki kok 2 rasyoneldir",
        selected_rule="CONTRADICTION_ASSUMPTION",
    )
    assert res["is_valid"] is True
    assert res["detected_bug"] is None


def test_proof_checker_invalid_step_number():
    res = ProofChecker.verify_step(
        theorem_id="THM-IRR-SQRT2",
        step_number=99,
        student_statement="test",
        selected_rule="MODUS_PONENS",
    )
    assert res["is_valid"] is False
    assert "Geçersiz adım numarası" in res["feedback"]


# =====================================================================
# 8. BİLİŞSEL SAFSATA VE HATA DEDEKTÖRLERİ (BUG-LOGIC-01..05)
# =====================================================================

def test_bug_logic_01_false_antecedent_fallacy():
    detector = MisconceptionDetector()
    diag = detector.detect("0 => 0 = 0", "p => q tablosu", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-01"


def test_bug_logic_01_valid_no_false_positive():
    detector = MisconceptionDetector()
    diag = detector.detect("0 => 0 = 1", "p => q tablosu", "")
    assert diag is None


def test_bug_logic_02_inverse_instead_of_contrapositive():
    detector = MisconceptionDetector()
    diag = detector.detect("p => q ≡ ¬p => ¬q", "karsit ters", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-02"


def test_bug_logic_02_valid_no_false_positive():
    detector = MisconceptionDetector()
    diag = detector.detect("p => q ≡ ¬q => ¬p", "karsit ters", "")
    assert diag is None


def test_bug_logic_03_quantifier_negation_scope():
    detector = MisconceptionDetector()
    diag = detector.detect("¬(Her x, P(x)) = Her x, ¬P(x)", "niceleyici degillemesi", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-03"


def test_bug_logic_03_valid_no_false_positive():
    detector = MisconceptionDetector()
    diag = detector.detect("¬(Her x, P(x)) = Bazi x, ¬P(x)", "niceleyici degillemesi", "")
    assert diag is None


def test_bug_logic_04_induction_base_case_omission():
    detector = MisconceptionDetector()
    diag = detector.detect("taban_adimi_gerekmez sadece k k+1", "tumevarim", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-04"


def test_bug_logic_05_contradiction_circular_assumption():
    detector = MisconceptionDetector()
    diag = detector.detect("celiski_icin_p_dogru_varsay", "olmayana ergi", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-05"


# =====================================================================
# 9. FASTAPI REST API UÇ NOKTA TESTLERİ
# =====================================================================

def test_fastapi_proof_truth_table_endpoint():
    client = TestClient(app)
    resp = client.post(
        "/api/v1/proof/truth-table",
        json={"variables": ["p", "q"], "expression_type": "implies"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 4
    assert data["is_tautology"] is False
    assert data["is_contingency"] is True


def test_fastapi_proof_catalog_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/proof/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 6
    assert any(t["id"] == "THM-IRR-SQRT2" for t in data)


def test_fastapi_proof_verify_step_and_vault():
    client = TestClient(app)
    # Trigger BUG-LOGIC-04 with student_id
    resp = client.post(
        "/api/v1/proof/verify-step",
        json={
            "theorem_id": "THM-GAUSS-SUM",
            "step_number": 1,
            "student_statement": "taban_adimi_gerekmez direkt p(k) kabul edelim",
            "selected_rule": "INDUCTION_BASE",
            "student_id": "STU-LOGIC-01",
            "problem_statement": "Gauss Toplam Formülü İspatı",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert data["detected_bug"] == "BUG-LOGIC-04"
    assert data["vault_recorded"] is True


def test_fastapi_proof_induction_simulate_endpoint():
    client = TestClient(app)
    resp = client.post(
        "/api/v1/proof/induction/simulate",
        json={"claim_type": "gauss", "start_k": 1, "test_range": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["all_steps_valid"] is True
    assert len(data["domino_chain"]) == 5
