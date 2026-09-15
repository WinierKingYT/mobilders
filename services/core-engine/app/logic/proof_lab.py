"""
Kişisel Öğrenme Motoru (PLE) - Seviye 19: Matematiksel İspat ve Mantık Laboratuvarı (Proof Lab)
Önermeler mantığı, doğruluk tablosu motoru, çıkarım kuralları (Modus Ponens/Tollens),
tümevarım ispat iskeleti ve çelişki ile ispat doğrulayıcısı.
"""

from __future__ import annotations
import itertools
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable


# =====================================================================
# 1. ÖNERMELER MANTIĞI VE DOĞRULUK TABLOSU MOTORU
# =====================================================================

def logic_not(p: bool) -> bool:
    """Değilleme (¬p)."""
    return not p


def logic_and(p: bool, q: bool) -> bool:
    """Ve bağlacı (p ∧ q). Sadece ikisi de doğruysa doğrudur."""
    return p and q


def logic_or(p: bool, q: bool) -> bool:
    """Veya bağlacı (p ∨ q). İkisi de yanlışsa yanlıştır, aksi halde doğru."""
    return p or q


def logic_xor(p: bool, q: bool) -> bool:
    """Ya da bağlacı (p ⊻ q). Değerler farklıysa doğru, aynıysa yanlış."""
    return p != q


def logic_implies(p: bool, q: bool) -> bool:
    """
    Koşullu önerme: İse bağlacı (p ⇒ q).
    Yalnızca p=True ve q=False iken False üretir; aksi halde True (¬p ∨ q).
    """
    return (not p) or q


def logic_iff(p: bool, q: bool) -> bool:
    """
    İki yönlü koşullu önerme: Ancak ve ancak bağlacı (p ⇔ q).
    p ve q aynı doğruluk değerine sahipse True, farklıysa False.
    """
    return p == q


class TruthTableGenerator:
    """
    Verilen önermelerin doğruluk tablosunu (Truth Table) ve Tautoloji/Çelişki durumunu hesaplar.
    """

    @staticmethod
    def generate_table(
        variables: List[str],
        formula_func: Callable[[Dict[str, bool]], bool],
    ) -> Dict[str, Any]:
        """
        Değişkenlerin tüm olası kombinasyonları (2^n) için formülü değerlendirir.
        """
        if not variables:
            raise ValueError("En az bir mantıksal değişken belirtilmelidir.")

        rows: List[Dict[str, Any]] = []
        outcomes: List[bool] = []

        # 2^n olası doğruluk değeri kombinasyonu (True/False)
        combinations = list(itertools.product([True, False], repeat=len(variables)))

        for combo in combinations:
            env = dict(zip(variables, combo))
            result = bool(formula_func(env))
            outcomes.append(result)
            rows.append({
                "assignment": {k: 1 if v else 0 for k, v in env.items()},
                "result": 1 if result else 0,
            })

        is_tautology = all(outcomes)
        is_contradiction = not any(outcomes)
        is_contingency = not is_tautology and not is_contradiction

        return {
            "variables": variables,
            "row_count": len(rows),
            "rows": rows,
            "is_tautology": is_tautology,
            "is_contradiction": is_contradiction,
            "is_contingency": is_contingency,
        }

    @staticmethod
    def verify_equivalence(
        variables: List[str],
        func_a: Callable[[Dict[str, bool]], bool],
        func_b: Callable[[Dict[str, bool]], bool],
    ) -> bool:
        """İki mantıksal formülün tüm durumlarda denk (A ≡ B) olduğunu kanıtlar."""
        combinations = list(itertools.product([True, False], repeat=len(variables)))
        for combo in combinations:
            env = dict(zip(variables, combo))
            if func_a(env) != func_b(env):
                return False
        return True


# =====================================================================
# 2. DÜZGÜN ÇIKARIM KURALLARI (INFERENCE RULES)
# =====================================================================

class InferenceRuleVerifier:
    """
    Dedüktif mantık çıkarım kurallarını doğrular.
    """

    @staticmethod
    def modus_ponens(p: bool, p_implies_q: bool) -> Optional[bool]:
        """
        Modus Ponens (Öncülü Olumlama):
        Öncüller: p, p ⇒ q
        Sonuç: q
        """
        if p is True and p_implies_q is True:
            return True
        return None

    @staticmethod
    def modus_tollens(not_q: bool, p_implies_q: bool) -> Optional[bool]:
        """
        Modus Tollens (Sonucu Yadsıma):
        Öncüller: ¬q, p ⇒ q
        Sonuç: ¬p
        """
        if not_q is True and p_implies_q is True:
            return True  # ¬p is True
        return None

    @staticmethod
    def hypothetical_syllogism(p_implies_q: bool, q_implies_r: bool) -> Optional[bool]:
        """
        Varsayımsal Tasım (Zincirleme Kuralı):
        Öncüller: p ⇒ q, q ⇒ r
        Sonuç: p ⇒ r
        """
        if p_implies_q is True and q_implies_r is True:
            return True
        return None

    @staticmethod
    def disjunctive_syllogism(p_or_q: bool, not_p: bool) -> Optional[bool]:
        """
        Seçenekli Tasım:
        Öncüller: p ∨ q, ¬p
        Sonuç: q
        """
        if p_or_q is True and not_p is True:
            return True  # q is True
        return None


# =====================================================================
# 3. İSPAT YÖNTEMLERİ DOĞRULAYICISI (PROOF METHODS)
# =====================================================================

class ProofVerifier:
    """
    Doğrudan ispat, karşıt ters, çelişki (olmayana ergi) ve aksine örnek yöntemlerini test eder.
    """

    @staticmethod
    def verify_contrapositive(
        p_implies_q_func: Callable[[bool, bool], bool],
        contrapositive_func: Callable[[bool, bool], bool],
    ) -> bool:
        """
        p ⇒ q önermesi ile ¬q ⇒ ¬p önermesinin denkliğini tüm durumlarda teyit eder.
        """
        for p, q in itertools.product([True, False], repeat=2):
            lhs = p_implies_q_func(p, q)
            rhs = contrapositive_func(p, q)
            if lhs != rhs:
                return False
        return True

    @staticmethod
    def verify_contradiction_flow(
        hypothesis: bool,
        negated_claim: bool,
        deduction_steps: List[Callable[[], bool]],
        produces_contradiction: bool,
    ) -> Dict[str, Any]:
        """
        Olmayana ergi (çelişki ile ispat) akışını denetler:
        1. Hipotez doğru kabul edilir.
        2. Hükmün değili (¬q) varsayılır.
        3. Dedüktif adımlar mantıksal bir imkansızlığa / çelişkiye (r ∧ ¬r) varır.
        4. Dolayısıyla ¬q yanlış, yani q doğrudur.
        """
        steps_valid = all(step() for step in deduction_steps)
        proof_valid = steps_valid and produces_contradiction

        return {
            "hypothesis": hypothesis,
            "negated_claim": negated_claim,
            "steps_count": len(deduction_steps),
            "steps_valid": steps_valid,
            "produces_contradiction": produces_contradiction,
            "proof_valid": proof_valid,
            "conclusion": "Orijinal hüküm Q matematiksel olarak ispatlandı." if proof_valid else "İspat geçersiz.",
        }

    @staticmethod
    def find_counterexample(
        domain: List[Any],
        predicate: Callable[[Any], bool],
    ) -> Optional[Dict[str, Any]]:
        """
        ∀x, P(x) biçimindeki bir genellemeyi çürüten bir karşıt örnek arar.
        """
        for item in domain:
            if not predicate(item):
                return {
                    "counterexample_found": True,
                    "counterexample_value": item,
                    "reason": f"P({item}) önermesi False değerini üretti, genelleme çürütüldü.",
                }
        return {
            "counterexample_found": False,
            "counterexample_value": None,
            "reason": "Test edilen kümede çürüten bir karşıt örnek bulunamadı.",
        }


# =====================================================================
# 4. MATEMATİKSEL TÜMEVARIM MOTORU (MATHEMATICAL INDUCTION)
# =====================================================================

class MathematicalInductionEngine:
    """
    Doğal sayılar üzerinde tanımlı P(n) önermelerini tümevarım (taban adımı + hipotez + geçiş)
    yöntemiyle denetler ve adım adım iskele oluşturur.
    """

    @staticmethod
    def verify_base_case(
        predicate: Callable[[int], bool],
        base_n: int = 1,
    ) -> bool:
        """Taban adımı: P(base_n) doğruluğunu kontrol eder."""
        return predicate(base_n)

    @staticmethod
    def simulate_inductive_step(
        predicate: Callable[[int], bool],
        start_k: int = 1,
        test_range: int = 10,
    ) -> Dict[str, Any]:
        """
        Tümevarım geçişini (P(k) ⇒ P(k+1)) belirli bir tam sayı aralığında deneysel olarak doğrular.
        """
        domino_chain: List[Dict[str, Any]] = []
        all_passed = True

        for k in range(start_k, start_k + test_range):
            p_k = predicate(k)
            p_k1 = predicate(k + 1)
            # P(k) True iken P(k+1) de True olmalıdır
            step_valid = (not p_k) or p_k1
            if not step_valid:
                all_passed = False
            domino_chain.append({
                "k": k,
                "P(k)": p_k,
                "P(k+1)": p_k1,
                "implication_holds": step_valid,
            })

        return {
            "start_k": start_k,
            "test_range": test_range,
            "all_steps_valid": all_passed,
            "domino_chain": domino_chain,
        }

    @staticmethod
    def scaffold_induction_proof(
        claim_name: str,
        formula_str: str,
        base_n: int = 1,
    ) -> Dict[str, Any]:
        """
        Tümevarım ispatı için 3 aşamalı pedagojik Sokratik iskele üretir.
        ZERO-LEAKAGE: Öğrencinin cebirsel geçişini yapacağı adımlarda hazır sonuç verilmez.
        """
        return {
            "claim_name": claim_name,
            "formula_str": formula_str,
            "base_n": base_n,
            "stages": [
                {
                    "stage_index": 1,
                    "title": "Taban Adımı (Base Case)",
                    "prompt": f"n = {base_n} için önermenin doğruluğunu kontrol et: Sol taraf ile sağ taraf birbirine eşit midir?",
                    "expected_action": f"P({base_n}) doğrula",
                },
                {
                    "stage_index": 2,
                    "title": "Tümevarım Hipotezi (Inductive Hypothesis)",
                    "prompt": "n = k için önermenin doğru olduğunu varsay: P(k) ifadesini açıkça yaz.",
                    "expected_action": "P(k) kabulü yap",
                },
                {
                    "stage_index": 3,
                    "title": "Tümevarım Adımı (Inductive Step)",
                    "prompt": "P(k) hipotezini kullanarak n = k + 1 için önermenin doğruluğunu cebirsel olarak türet.",
                    "expected_action": "P(k) + (k+1). terim = P(k+1) göster",
                },
            ],
        }
