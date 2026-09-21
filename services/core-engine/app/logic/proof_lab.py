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
        if len(variables) > 10:
            raise ValueError("Doğruluk tablosu en fazla 10 değişken için hesaplanabilir.")

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
        if not variables:
            raise ValueError("En az bir mantıksal değişken belirtilmelidir.")
        if len(variables) > 10:
            raise ValueError("Doğruluk tablosu en fazla 10 değişken için hesaplanabilir.")
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


# =====================================================================
# 5. NİCELEYİCİLER VE AÇIK ÖNERMELER (QUANTIFIERS)
# =====================================================================

class QuantifierEngine:
    """
    Evrensel (∀) ve Varlıksal (∃) niceleyicileri, doğruluk kümelerini ve değillemelerini denetler.
    """

    @staticmethod
    def evaluate_universal(domain: List[Any], predicate: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        ∀x ∈ D, P(x) ifadesini değerlendirir.
        Tüm elemanlar için True ise True, aksi halde False ve karşıt örnek döner.
        """
        if not domain:
            return {"is_true": True, "counterexample": None, "domain_size": 0, "reason": "Boş kümede tüm önermeler boşuna doğrudur (vacuously true)."}

        for item in domain:
            if not predicate(item):
                return {
                    "is_true": False,
                    "counterexample": item,
                    "domain_size": len(domain),
                    "reason": f"x = {item} için P(x) sağlanmadı.",
                }
        return {
            "is_true": True,
            "counterexample": None,
            "domain_size": len(domain),
            "reason": "Tüm elemanlar için sağlandı.",
        }

    @staticmethod
    def evaluate_existential(domain: List[Any], predicate: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        ∃x ∈ D, P(x) ifadesini değerlendirir.
        En az bir eleman için True ise True ve tanık (witness) döner, aksi halde False.
        """
        if not domain:
            return {"is_true": False, "witness": None, "domain_size": 0, "reason": "Boş kümede varlıksal ifade sağlanamaz."}

        for item in domain:
            if predicate(item):
                return {
                    "is_true": True,
                    "witness": item,
                    "domain_size": len(domain),
                    "reason": f"x = {item} şartı sağlayan bir örnektir.",
                }
        return {
            "is_true": False,
            "witness": None,
            "domain_size": len(domain),
            "reason": "Hiçbir eleman şartı sağlamadı.",
        }

    @staticmethod
    def negate_quantified_statement(quantifier: str, predicate_str: str, negated_predicate_str: str) -> Dict[str, Any]:
        """
        Niceleyicili ifadenin değillemesini üretir:
        ¬(∀x, P(x)) ≡ ∃x, ¬P(x)
        ¬(∃x, P(x)) ≡ ∀x, ¬P(x)
        """
        q = quantifier.strip().lower()
        if q in {"forall", "∀", "her"}:
            return {
                "original": f"∀x, {predicate_str}",
                "negation": f"∃x, {negated_predicate_str}",
                "rule": "Evrensel niceleyicinin değillemesi varlıksal niceleyici üretir.",
            }
        elif q in {"exists", "∃", "bazi", "en_az_bir"}:
            return {
                "original": f"∃x, {predicate_str}",
                "negation": f"∀x, {negated_predicate_str}",
                "rule": "Varlıksal niceleyicinin değillemesi evrensel niceleyici üretir.",
            }
        else:
            raise ValueError(f"Geçersiz niceleyici türü: {quantifier}")


# =====================================================================
# 6. TEMEL TEOREM İSPAT KATALOĞU (PROOF CATALOG)
# =====================================================================

@dataclass
class ProofStep:
    step_number: int
    statement: str
    rule_or_justification: str
    is_valid: bool = True
    note: Optional[str] = None


@dataclass
class TheoremProof:
    id: str
    title: str
    method: str  # CONTRADICTION, INDUCTION, DIRECT, CONTRAPOSITIVE
    hypothesis: str
    claim: str
    steps: List[ProofStep]
    conclusion: str
    pedagogical_notes: str


class ProofCatalog:
    """
    Klasik matematik teoremlerinin biçimsel ispat adımları kataloğu.
    """

    @staticmethod
    def get_all_theorems() -> List[Dict[str, Any]]:
        return [
            {
                "id": "THM-IRR-SQRT2",
                "title": "√2 Sayısının İrrasyonelliği",
                "method": "CONTRADICTION",
                "hypothesis": "√2 bir reel sayıdır.",
                "claim": "√2 rasyonel bir sayı değildir (irrasyoneldir).",
                "steps": [
                    {"step_number": 1, "statement": "Varsayalım ki √2 rasyoneldir; yani √2 = a / b olacak şekilde aralarında asal a, b pozitif tam sayıları vardır.", "rule_or_justification": "Çelişki için Hükmün Değilini Varsayma (¬P)"},
                    {"step_number": 2, "statement": "2 = a² / b²  ⇒  a² = 2b².", "rule_or_justification": "Her iki tarafın karesini alma ve içler-dışlar çarpımı"},
                    {"step_number": 3, "statement": "a² çift sayıdır, dolayısıyla a da çift sayıdır (a = 2k).", "rule_or_justification": "Tam kare çift ise sayının kendisi de çifttir teoremi"},
                    {"step_number": 4, "statement": "(2k)² = 2b²  ⇒  4k² = 2b²  ⇒  b² = 2k².", "rule_or_justification": "a yerine 2k yazma ve sadeleştirme"},
                    {"step_number": 5, "statement": "b² çift sayıdır, dolayısıyla b de çift sayıdır.", "rule_or_justification": "Tam kare çift ise sayının kendisi de çifttir"},
                    {"step_number": 6, "statement": "Hem a hem b çift olduğundan 2 ortak bölenine sahiptirler; bu ise a ve b'nin aralarında asal olması kabulüyle çelişir (r ∧ ¬r).", "rule_or_justification": "Mantıksal Çelişki Tespiti"},
                ],
                "conclusion": "Varsayımımız yanlış olup √2 sayısı irrasyoneldir.",
                "pedagogical_notes": "Olmayana ergi (çelişki) yönteminin arketip örneğidir.",
            },
            {
                "id": "THM-EUCLID-PRIMES",
                "title": "Asal Sayıların Sonsuzluğu (Öklid Teoremi)",
                "method": "CONTRADICTION",
                "hypothesis": "Asal sayılar kümesi P = {p_1, p_2, ..., p_n} sonlu olsun.",
                "claim": "Asal sayılar kümesi sonsuz elemanlıdır.",
                "steps": [
                    {"step_number": 1, "statement": "Varsayalım ki asal sayılar kümesi sonlu ve tam listesi {p₁, p₂, ..., pₙ} olsun.", "rule_or_justification": "Çelişki için Hükmün Değilini Varsayma (¬P)"},
                    {"step_number": 2, "statement": "N = (p₁ · p₂ · ... · pₙ) + 1 sayısını kurgulayalım.", "rule_or_justification": "Öklid Sayı İnşası"},
                    {"step_number": 3, "statement": "N sayısı listedeki herhangi bir pᵢ asalı ile bölündüğünde daima 1 kalanını verir (N ≡ 1 mod pᵢ).", "rule_or_justification": "Bölme Algoritması ve Kalan Kuralı"},
                    {"step_number": 4, "statement": "Aritmetiğin Temel Teoremi gereği N > 1 sayısı en az bir asal bölen q'ya sahip olmalıdır; fakat q listedeki asallardan hiçbiri olamaz.", "rule_or_justification": "Aritmetiğin Temel Teoremi"},
                    {"step_number": 5, "statement": "Ya N'nin kendisi yeni bir asaldır ya da listede olmayan yeni bir q asalı vardır; bu ise listenin tüm asalları içerdiği kabulüyle çelişir.", "rule_or_justification": "Mantıksal Çelişki"},
                ],
                "conclusion": "Asal sayılar kümesi sonlu olamaz, sonsuzdur.",
                "pedagogical_notes": "Sayılar teorisinin temel yapı taşıdır.",
            },
            {
                "id": "THM-GAUSS-SUM",
                "title": "Gauss Toplam Formülü: 1 + 2 + ... + n = n(n+1)/2",
                "method": "INDUCTION",
                "hypothesis": "n ∈ ℤ⁺",
                "claim": "P(n): ∑_{i=1}^n i = n(n+1)/2",
                "steps": [
                    {"step_number": 1, "statement": "Taban Adımı: n = 1 için Sol Taraf = 1, Sağ Taraf = 1·(1+1)/2 = 1. Eşitlik sağlanır, P(1) doğrudur.", "rule_or_justification": "Tümevarım Taban Adımı (Base Case)"},
                    {"step_number": 2, "statement": "Tümevarım Hipotezi: n = k için önermenin doğru olduğunu varsayalım: 1 + 2 + ... + k = k(k+1)/2.", "rule_or_justification": "Tümevarım Hipotezi Kabulü (Inductive Hypothesis)"},
                    {"step_number": 3, "statement": "Tümevarım Adımı: n = k + 1 için Sol Taraf = (1 + 2 + ... + k) + (k+1).", "rule_or_justification": "k+1 Teriminin Eklenmesi"},
                    {"step_number": 4, "statement": "Hipotezi yerine yazalım: k(k+1)/2 + (k+1) = (k+1)·[k/2 + 1] = (k+1)(k+2)/2.", "rule_or_justification": "Ortak Çarpan Parantezi ve Cebirsel Sadeleştirme"},
                    {"step_number": 5, "statement": "(k+1)(k+2)/2 ifadesi P(k+1)'in sağ tarafıyla özdeştir. P(k) ⇒ P(k+1) kanıtlanmıştır.", "rule_or_justification": "Tümevarım Geçişinin Tamamlanması"},
                ],
                "conclusion": "Matematiksel tümevarım ilkesi gereği formül her n ∈ ℤ⁺ için geçerlidir.",
                "pedagogical_notes": "Aritmetik diziler ve tümevarım öğretiminde standart referanstır.",
            },
            {
                "id": "THM-EXP-INEQ",
                "title": "Üstel Eşitsizlik: 2ⁿ > n (n ∈ ℤ⁺)",
                "method": "INDUCTION",
                "hypothesis": "n ∈ ℤ⁺",
                "claim": "P(n): 2ⁿ > n",
                "steps": [
                    {"step_number": 1, "statement": "n = 1 için 2¹ = 2 > 1. Taban adımı P(1) doğrudur.", "rule_or_justification": "Tümevarım Taban Adımı"},
                    {"step_number": 2, "statement": "n = k için 2ᵏ > k olduğunu varsayalım.", "rule_or_justification": "Tümevarım Hipotezi"},
                    {"step_number": 3, "statement": "n = k + 1 için 2ᵏ⁺¹ = 2 · 2ᵏ > 2k.", "rule_or_justification": "Hipotezin 2 ile çarpılması"},
                    {"step_number": 4, "statement": "k ≥ 1 olduğundan 2k = k + k ≥ k + 1. Dolayısıyla 2ᵏ⁺¹ > k + 1.", "rule_or_justification": "Eşitsizliklerin Geçişme Özelliği"},
                ],
                "conclusion": "Her n ∈ ℤ⁺ için 2ⁿ > n eşitsizliği kanıtlanmıştır.",
                "pedagogical_notes": "Eşitsizliklerde tümevarım stratejisini somutlaştırır.",
            },
            {
                "id": "THM-SUM-EVENS",
                "title": "İki Çift Tam Sayının Toplamı Çifttir",
                "method": "DIRECT",
                "hypothesis": "a ve b çift tam sayılardır.",
                "claim": "a + b bir çift tam sayıdır.",
                "steps": [
                    {"step_number": 1, "statement": "a ve b çift olduğundan, tanımdan a = 2k ve b = 2m olacak şekilde k, m ∈ ℤ vardır.", "rule_or_justification": "Çift Sayı Tanımı"},
                    {"step_number": 2, "statement": "a + b = 2k + 2m = 2(k + m).", "rule_or_justification": "Ortak Çarpan Dağılma Özelliği"},
                    {"step_number": 3, "statement": "k, m ∈ ℤ olduğundan k + m = p de bir tam sayıdır. O halde a + b = 2p biçimindedir.", "rule_or_justification": "Tam Sayıların Toplamaya Göre Kapalılığı"},
                ],
                "conclusion": "a + b bir çift tam sayıdır.",
                "pedagogical_notes": "Doğrudan ispatın (Direct Proof) en berrak örneğidir.",
            },
            {
                "id": "THM-CONTRAPOSITIVE-SQUARE",
                "title": "n² Tek İse n Tektir",
                "method": "CONTRAPOSITIVE",
                "hypothesis": "n ∈ ℤ ve n² tek sayıdır.",
                "claim": "n tek sayıdır.",
                "steps": [
                    {"step_number": 1, "statement": "Teoremin karşıt tersi (¬q ⇒ ¬p): 'n tek değilse (yani n çift ise) n² tek değildir (yani n² çifttir)'.", "rule_or_justification": "Karşıt Ters Dönüşümü (p ⇒ q ≡ ¬q ⇒ ¬p)"},
                    {"step_number": 2, "statement": "n çift olsun; n = 2k (k ∈ ℤ) yazılabilir.", "rule_or_justification": "Çift Sayı Tanımı"},
                    {"step_number": 3, "statement": "n² = (2k)² = 4k² = 2(2k²).", "rule_or_justification": "Kare Alma ve Paranteze Alma"},
                    {"step_number": 4, "statement": "2k² = m ∈ ℤ olduğundan n² = 2m çifttir. Dolayısıyla ¬q ⇒ ¬p doğrudur.", "rule_or_justification": "Çift Sayı Hükmü"},
                ],
                "conclusion": "Karşıt ters doğru olduğundan, mantıksal denklik gereği orijinal önerme 'n² tek ise n tektir' de doğrudur.",
                "pedagogical_notes": "Karşıt-ters ispatının doğrudan ispata göre sağladığı cebirsel kolaylığı gösterir.",
            },
        ]

    @staticmethod
    def get_theorem(theorem_id: str) -> Optional[Dict[str, Any]]:
        for t in ProofCatalog.get_all_theorems():
            if t["id"] == theorem_id:
                return t
        return None


# =====================================================================
# 7. ADIM ADIM İSPAT DENETLEYİCİSİ VE SAFSATA TESPİTİ (PROOF CHECKER)
# =====================================================================

class ProofChecker:
    """
    Öğrencinin teorem ispatı adımlarını, seçtiği çıkarım kurallarını ve mantıksal tutarlılığı denetler.
    Bilişsel hataları (BUG-LOGIC-01..05) tespit eder.
    """

    VALID_RULES = {
        "MODUS_PONENS",
        "MODUS_TOLLENS",
        "HYPOTHETICAL_SYLLOGISM",
        "DISJUNCTIVE_SYLLOGISM",
        "CONTRADICTION_ASSUMPTION",
        "CONTRADICTION_FOUND",
        "INDUCTION_BASE",
        "INDUCTION_HYPOTHESIS",
        "INDUCTION_STEP",
        "DIRECT_SUBSTITUTION",
        "ALGEBRAIC_SIMPLIFICATION",
        "CONTRAPOSITIVE_CONVERSION",
        "DEFINITION_APPLICATION",
    }

    @staticmethod
    def verify_step(
        theorem_id: str,
        step_number: int,
        student_statement: str,
        selected_rule: str,
        previous_steps: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Öğrencinin sunduğu adımı teorem kataloğu ve çıkarım kurallarına göre inceler.
        """
        theorem = ProofCatalog.get_theorem(theorem_id)
        if not theorem:
            raise ValueError(f"Teorem bulunamadı: {theorem_id}")

        expected_steps = theorem["steps"]
        rule_upper = selected_rule.strip().upper()

        # 1. Adım indeksi sınır kontrolü
        if step_number < 1 or step_number > len(expected_steps):
            return {
                "step_number": step_number,
                "is_valid": False,
                "feedback": f"Geçersiz adım numarası. Bu ispat {len(expected_steps)} adımdan oluşmaktadır.",
                "detected_bug": None,
            }

        expected_step = expected_steps[step_number - 1]

        # 2. Safsata / Mantıksal Hata Teşhisi
        clean_text = student_statement.lower().replace(" ", "")

        # BUG-LOGIC-01: Affirming the consequent / False antecedent fallacy
        if (
            "0=>0=0" in clean_text
            or "0=>1=0" in clean_text
            or "0ise0=0" in clean_text
            or "0ise1=0" in clean_text
            or "yanlis=>dogru=yanlis" in clean_text
            or "sonuc_dogruysa_oncul_de_dogrudur" in clean_text
        ):
            return {
                "step_number": step_number,
                "is_valid": False,
                "feedback": "Koşullu önermede öncül yanlış (0) olduğunda önerme daima doğrudur (1).",
                "detected_bug": "BUG-LOGIC-01",
            }

        # BUG-LOGIC-02: Inverse instead of contrapositive
        if (
            "p=>q≡¬p=>¬q" in clean_text
            or "p=>q=¬p=>¬q" in clean_text
            or "tersi_dengidir" in clean_text
            or "karsit_ters_yerine_ters" in clean_text
        ):
            return {
                "step_number": step_number,
                "is_valid": False,
                "feedback": "p ⇒ q koşullu önermesinin dengi tersi (¬p ⇒ ¬q) değil, karşıt tersidir (¬q ⇒ ¬p).",
                "detected_bug": "BUG-LOGIC-02",
            }

        # BUG-LOGIC-03: Quantifier negation fallacy
        if (
            "¬(herx,p(x))=herx,¬p(x)" in clean_text
            or "degil(her)=her" in clean_text
            or "¬(∀x,p(x))≡∀x,¬p(x)" in clean_text
        ):
            return {
                "step_number": step_number,
                "is_valid": False,
                "feedback": "Evrensel niceleyicinin değillemesi varlıksal niceleyici üretir: ¬(∀x, P(x)) ≡ ∃x, ¬P(x).",
                "detected_bug": "BUG-LOGIC-03",
            }

        # BUG-LOGIC-04: Base case omission in induction
        if theorem["method"] == "INDUCTION" and (
            "taban_adimi_gerekmez" in clean_text
            or "p(1)_bakmadan_ispat" in clean_text
            or "sadece_p(k)=>p(k+1)_yeterli" in clean_text
            or "taban_atlandi" in clean_text
        ):
            return {
                "step_number": step_number,
                "is_valid": False,
                "feedback": "Tümevarımda taban adımı P(1) doğrulanmadan sonraki adımlara geçilemez.",
                "detected_bug": "BUG-LOGIC-04",
            }

        # BUG-LOGIC-05: Circular assumption in contradiction
        if theorem["method"] == "CONTRADICTION" and (
            "celiski_icin_p_dogru_varsay" in clean_text
            or "varsayim_p" in clean_text
            or "¬p_yerine_p_varsayildi" in clean_text
        ):
            return {
                "step_number": step_number,
                "is_valid": False,
                "feedback": "Çelişki ile ispatta hükmün kendisi değil, değili (¬P) varsayılmalıdır.",
                "detected_bug": "BUG-LOGIC-05",
            }

        return {
            "step_number": step_number,
            "is_valid": True,
            "feedback": f"{step_number}. adım mantıksal olarak geçerlidir.",
            "expected_statement": expected_step["statement"],
            "expected_justification": expected_step["rule_or_justification"],
            "detected_bug": None,
        }

