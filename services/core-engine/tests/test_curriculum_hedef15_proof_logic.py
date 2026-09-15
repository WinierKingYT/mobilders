"""
HEDEF 15: Matematiksel İspat ve Mantık Laboratuvarı (Proof Lab & Formal Logic) Testleri.
Asgari 40 test ile önermeler mantığı, doğruluk tabloları, çıkarım kuralları, tümevarım,
çelişki ile ispat, aksine örnek ve mantıksal yanılgı tespitlerini (BUG-LOGIC-01..05) doğrular.
"""

import pytest
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
)
from app.misconceptions.detector import QuadraticMisconceptionDetector as MisconceptionDetector


# =====================================================================
# 1. TEMEL MANTIKSAL BAĞLAÇLAR VE DOĞRULUK DEĞERLERİ
# =====================================================================

def test_logic_not():
    assert logic_not(True) is False
    assert logic_not(False) is True


def test_logic_and():
    assert logic_and(True, True) is True
    assert logic_and(True, False) is False
    assert logic_and(False, True) is False
    assert logic_and(False, False) is False


def test_logic_or():
    assert logic_or(True, True) is True
    assert logic_or(True, False) is True
    assert logic_or(False, True) is True
    assert logic_or(False, False) is False


def test_logic_xor():
    assert logic_xor(True, True) is False
    assert logic_xor(True, False) is True
    assert logic_xor(False, True) is True
    assert logic_xor(False, False) is False


def test_logic_implies_truth_values():
    # p => q: Sadece 1 => 0 iken False, 0 => 0 ve 0 => 1 iken True!
    assert logic_implies(True, True) is True
    assert logic_implies(True, False) is False
    assert logic_implies(False, True) is True
    assert logic_implies(False, False) is True


def test_logic_iff():
    assert logic_iff(True, True) is True
    assert logic_iff(False, False) is True
    assert logic_iff(True, False) is False
    assert logic_iff(False, True) is False


# =====================================================================
# 2. DOĞRULUK TABLOSU, TAUTOLOJİ VE ÇELİŞKİ TESTLERİ
# =====================================================================

def test_truth_table_generator_tautology_excluded_middle():
    # p ∨ ¬p daima 1'dir (Tautoloji)
    res = TruthTableGenerator.generate_table(
        variables=["p"],
        formula_func=lambda env: logic_or(env["p"], logic_not(env["p"])),
    )
    assert res["is_tautology"] is True
    assert res["is_contradiction"] is False
    assert res["row_count"] == 2


def test_truth_table_generator_contradiction():
    # p ∧ ¬p daima 0'dır (Çelişki)
    res = TruthTableGenerator.generate_table(
        variables=["p"],
        formula_func=lambda env: logic_and(env["p"], logic_not(env["p"])),
    )
    assert res["is_contradiction"] is True
    assert res["is_tautology"] is False


def test_truth_table_generator_contingency():
    # p ∧ q bazen doğru bazen yanlış
    res = TruthTableGenerator.generate_table(
        variables=["p", "q"],
        formula_func=lambda env: logic_and(env["p"], env["q"]),
    )
    assert res["is_contingency"] is True
    assert res["is_tautology"] is False
    assert res["is_contradiction"] is False
    assert res["row_count"] == 4


def test_truth_table_empty_variables_raises():
    with pytest.raises(ValueError):
        TruthTableGenerator.generate_table([], lambda env: True)


# =====================================================================
# 3. MANTIKSAL DENKLİK KANITLARI (EQUIVALENCE VERIFICATION)
# =====================================================================

def test_de_morgan_law_1():
    # ¬(p ∧ q) ≡ ¬p ∨ ¬q
    is_equiv = TruthTableGenerator.verify_equivalence(
        variables=["p", "q"],
        func_a=lambda env: logic_not(logic_and(env["p"], env["q"])),
        func_b=lambda env: logic_or(logic_not(env["p"]), logic_not(env["q"])),
    )
    assert is_equiv is True


def test_de_morgan_law_2():
    # ¬(p ∨ q) ≡ ¬p ∧ ¬q
    is_equiv = TruthTableGenerator.verify_equivalence(
        variables=["p", "q"],
        func_a=lambda env: logic_not(logic_or(env["p"], env["q"])),
        func_b=lambda env: logic_and(logic_not(env["p"]), logic_not(env["q"])),
    )
    assert is_equiv is True


def test_implication_equivalence():
    # p ⇒ q ≡ ¬p ∨ q
    is_equiv = TruthTableGenerator.verify_equivalence(
        variables=["p", "q"],
        func_a=lambda env: logic_implies(env["p"], env["q"]),
        func_b=lambda env: logic_or(logic_not(env["p"]), env["q"]),
    )
    assert is_equiv is True


def test_contrapositive_equivalence():
    # p ⇒ q ≡ ¬q ⇒ ¬p
    is_equiv = TruthTableGenerator.verify_equivalence(
        variables=["p", "q"],
        func_a=lambda env: logic_implies(env["p"], env["q"]),
        func_b=lambda env: logic_implies(logic_not(env["q"]), logic_not(env["p"])),
    )
    assert is_equiv is True


def test_inverse_not_equivalent_to_implication():
    # p ⇒ q İLE TERSİ (¬p ⇒ ¬q) DENK DEĞİLDİR! (BUG-LOGIC-02 Mantıksal Kanıtı)
    is_equiv = TruthTableGenerator.verify_equivalence(
        variables=["p", "q"],
        func_a=lambda env: logic_implies(env["p"], env["q"]),
        func_b=lambda env: logic_implies(logic_not(env["p"]), logic_not(env["q"])),
    )
    assert is_equiv is False


def test_double_negation():
    # ¬(¬p) ≡ p
    is_equiv = TruthTableGenerator.verify_equivalence(
        variables=["p"],
        func_a=lambda env: logic_not(logic_not(env["p"])),
        func_b=lambda env: env["p"],
    )
    assert is_equiv is True


# =====================================================================
# 4. ÇIKARIM KURALLARI (INFERENCE RULES) TESTLERİ
# =====================================================================

def test_modus_ponens_valid():
    # p=True, (p => q)=True -> q=True
    assert InferenceRuleVerifier.modus_ponens(p=True, p_implies_q=True) is True


def test_modus_ponens_invalid_antecedent():
    assert InferenceRuleVerifier.modus_ponens(p=False, p_implies_q=True) is None


def test_modus_tollens_valid():
    # ¬q=True, (p => q)=True -> ¬p=True
    assert InferenceRuleVerifier.modus_tollens(not_q=True, p_implies_q=True) is True


def test_hypothetical_syllogism_valid():
    # p => q ve q => r -> p => r
    assert InferenceRuleVerifier.hypothetical_syllogism(p_implies_q=True, q_implies_r=True) is True


def test_disjunctive_syllogism_valid():
    # p ∨ q ve ¬p -> q
    assert InferenceRuleVerifier.disjunctive_syllogism(p_or_q=True, not_p=True) is True


# =====================================================================
# 5. İSPAT YÖNTEMLERİ (ÇELİŞKİ, KARŞIT TERS, AKSİNE ÖRNEK) TESTLERİ
# =====================================================================

def test_proof_by_contradiction_flow():
    # İspat: "√2 irrasyoneldir"
    # Hipotez: Sayı ekseni tanımlı
    # Değil: "√2 rasyoneldir (p/q aralarında asal)"
    # Dedüktif adımlar: 2 = p^2 / q^2 -> p çift -> q çift -> p ve q aralarında asal değil!
    # Çelişki: (aralarında asal) ∧ (aralarında asal değil)
    res = ProofVerifier.verify_contradiction_flow(
        hypothesis=True,
        negated_claim=True,
        deduction_steps=[
            lambda: True,  # 2q^2 = p^2
            lambda: True,  # p çift olmalı
            lambda: True,  # q çift olmalı
        ],
        produces_contradiction=True,
    )
    assert res["proof_valid"] is True
    assert "matematiksel olarak ispatlandı" in res["conclusion"]


def test_proof_by_contrapositive_flow():
    # İspat: "n^2 tek ise n tektir"
    # Karşıt Ters: "n çift ise n^2 çifttir"
    is_valid = ProofVerifier.verify_contrapositive(
        p_implies_q_func=lambda p, q: logic_implies(p, q),
        contrapositive_func=lambda p, q: logic_implies(logic_not(q), logic_not(p)),
    )
    assert is_valid is True


def test_counterexample_refutation_found():
    # İddia: "Tüm asal sayılar tektir: ∀p ∈ Asallar, Tek(p)"
    primes = [2, 3, 5, 7, 11, 13]
    res = ProofVerifier.find_counterexample(primes, predicate=lambda p: p % 2 != 0)
    assert res["counterexample_found"] is True
    assert res["counterexample_value"] == 2


def test_counterexample_refutation_none():
    # İddia: "x^2 >= 0 her x ∈ Reel sayılar için"
    reals = [-5.0, -1.0, 0.0, 2.5, 10.0]
    res = ProofVerifier.find_counterexample(reals, predicate=lambda x: x ** 2 >= 0)
    assert res["counterexample_found"] is False


# =====================================================================
# 6. MATEMATİKSEL TÜMEVARIM (MATHEMATICAL INDUCTION) TESTLERİ
# =====================================================================

def test_induction_sum_of_integers():
    # P(n): 1 + 2 + ... + n = n*(n+1)/2
    def predicate(n: int) -> bool:
        lhs = sum(range(1, n + 1))
        rhs = (n * (n + 1)) // 2
        return lhs == rhs

    # Taban adımı P(1)
    assert MathematicalInductionEngine.verify_base_case(predicate, base_n=1) is True

    # Tümevarım geçiş simülasyonu
    sim = MathematicalInductionEngine.simulate_inductive_step(predicate, start_k=1, test_range=20)
    assert sim["all_steps_valid"] is True


def test_induction_sum_of_odds():
    # P(n): 1 + 3 + 5 + ... + (2n-1) = n^2
    def predicate(n: int) -> bool:
        lhs = sum(2 * i - 1 for i in range(1, n + 1))
        rhs = n ** 2
        return lhs == rhs

    assert MathematicalInductionEngine.verify_base_case(predicate, base_n=1) is True
    sim = MathematicalInductionEngine.simulate_inductive_step(predicate, start_k=1, test_range=15)
    assert sim["all_steps_valid"] is True


def test_induction_divisibility_by_three():
    # P(n): 4^n - 1 sayısı 3 ile tam bölünür
    def predicate(n: int) -> bool:
        return ((4 ** n) - 1) % 3 == 0

    assert MathematicalInductionEngine.verify_base_case(predicate, base_n=1) is True
    sim = MathematicalInductionEngine.simulate_inductive_step(predicate, start_k=1, test_range=15)
    assert sim["all_steps_valid"] is True


def test_induction_inequality_power_of_two():
    # P(n): 2^n > n her n >= 1 için
    def predicate(n: int) -> bool:
        return (2 ** n) > n

    assert MathematicalInductionEngine.verify_base_case(predicate, base_n=1) is True
    sim = MathematicalInductionEngine.simulate_inductive_step(predicate, start_k=1, test_range=25)
    assert sim["all_steps_valid"] is True


def test_induction_scaffolding_structure():
    scaffold = MathematicalInductionEngine.scaffold_induction_proof(
        claim_name="Doğal Sayılar Toplamı",
        formula_str="1 + 2 + ... + n = n(n+1)/2",
        base_n=1,
    )
    assert len(scaffold["stages"]) == 3
    assert scaffold["stages"][0]["title"].startswith("Taban Adımı")
    assert scaffold["stages"][1]["title"].startswith("Tümevarım Hipotezi")
    assert scaffold["stages"][2]["title"].startswith("Tümevarım Adımı")


# =====================================================================
# 7. BİLİŞSEL YANILGI TESPİTLERİ (BUG-LOGIC-01..05) VE ZERO FALSE POSITIVES
# =====================================================================

@pytest.fixture
def detector():
    return MisconceptionDetector()


def test_bug_logic_01_false_antecedent(detector):
    diag = detector.detect("0 => 0 = 0", "Koşullu önermenin doğruluk değeri?", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-01"
    assert "öncül" in diag.description.lower() or "yanlış" in diag.description.lower()


def test_bug_logic_01_valid_step_no_false_positive(detector):
    diag = detector.detect("0 => 0 = 1", "Koşullu önerme doğruluk tablosu", "")
    assert diag is None


def test_bug_logic_02_inverse_instead_of_contrapositive(detector):
    diag = detector.detect("p => q ≡ ¬p => ¬q", "Koşullu önermenin dengi nedir?", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-02"
    assert "karşıt ters" in diag.description.lower()


def test_bug_logic_02_valid_step_no_false_positive(detector):
    diag = detector.detect("p => q ≡ ¬q => ¬p", "Karşıt ters denkliği", "")
    assert diag is None


def test_bug_logic_03_quantifier_negation_scope_fallacy(detector):
    diag = detector.detect("¬(Her x, P(x)) = Her x, ¬P(x)", "Niceleyicinin değillemesi", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-03"
    assert "evrensel" in diag.description.lower() or "varlıksal" in diag.description.lower()


def test_bug_logic_03_valid_step_no_false_positive(detector):
    diag = detector.detect("¬(Her x, P(x)) = Bazı x, ¬P(x)", "De Morgan niceleyici", "")
    assert diag is None


def test_bug_logic_04_induction_base_case_omission(detector):
    diag = detector.detect("taban_adimi_gerekmez", "Tümevarım ile ispat adımları", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-04"
    assert "domino" in diag.description.lower() or "taban" in diag.description.lower()


def test_bug_logic_04_valid_step_no_false_positive(detector):
    diag = detector.detect("n=1 için P(1) doğrulanmalıdır", "Tümevarım adımları", "")
    assert diag is None


def test_bug_logic_05_contradiction_circular_assumption(detector):
    diag = detector.detect("celiski_icin_p_dogru_varsay", "Olmayana ergi yöntemiyle ispat", "")
    assert diag is not None
    assert diag.bug_id == "BUG-LOGIC-05"
    assert "değil" in diag.description.lower() or "çelişki" in diag.description.lower()


def test_bug_logic_05_valid_step_no_false_positive(detector):
    diag = detector.detect("Hükmün değilini (¬p) doğru varsayalım", "Çelişki ile ispat", "")
    assert diag is None
