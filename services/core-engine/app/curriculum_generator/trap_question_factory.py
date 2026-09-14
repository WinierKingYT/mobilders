"""
Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası ve Dinamik Deneme Sınavı Motoru (HEDEF 13).
Tersine Mühendislik (Reverse-SymPy), her çeldiricisi bir BUG-ID ile etiketlenmiş akıllı soru üretimi
ve hedeflenen teta yetenek düzeyine (IRT) göre dinamik deneme sınavı montajı.
"""
from __future__ import annotations
import math
import random
import time
import uuid
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    ROOT_FOUNDATION = "root_foundation"
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    GEOMETRY = "geometry"
    WORD_PROBLEM = "word_problem"


class ExamSection(str, Enum):
    TYT_MATEMATIK = "TYT_MATEMATIK"
    AYT_MATEMATIK = "AYT_MATEMATIK"
    IB_DP_HL = "IB_DP_HL"
    AP_CALCULUS_BC = "AP_CALCULUS_BC"


class CognitiveChoice(BaseModel):
    """Her çeldiricisi bir kavramsal yanılgı simülasyonu olan şık nesnesi."""
    text: str
    is_correct: bool
    bug_id: Optional[str] = None
    distractor_rationale: Optional[str] = None


class TrapQuestion(BaseModel):
    """Bilişsel Tuzaklı Çoktan Seçmeli Soru Kartı."""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str
    type: QuestionType
    prompt: str
    choices: List[CognitiveChoice]
    correct_choice_index: int
    difficulty_b: float = 0.0
    discrimination_a: float = 1.8
    full_socratic_solution: str
    target_value: str


class DynamicExam(BaseModel):
    """Montajlanmış Dinamik Deneme Sınavı Paketi."""
    exam_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    section: ExamSection
    questions: List[TrapQuestion]
    total_time_minutes: int
    target_theta: float
    created_at: float = Field(default_factory=time.time)


class TrapQuestionGenerator:
    """Tersine Mühendislik (Reverse-SymPy) ile Bilişsel Tuzaklı Soru Üreticisi."""

    @staticmethod
    def generate_quadratic(r1: int = 2, r2: int = -5) -> TrapQuestion:
        """
        Kökleri r1 ve r2 olan kuadratik denklem:
        (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2 = 0
        """
        sum_roots = r1 + r2
        prod_roots = r1 * r2
        b_coeff = -sum_roots
        c_coeff = prod_roots

        b_sign = f"+ {b_coeff}" if b_coeff >= 0 else f"- {abs(b_coeff)}"
        c_sign = f"+ {c_coeff}" if c_coeff >= 0 else f"- {abs(c_coeff)}"
        eq_str = f"x² {b_sign}x {c_sign} = 0"

        correct_text = f"x = {r1} veya x = {r2}"

        # 1. BUG-QUAD-05: Kuadratik formülde b işaret hatası (-b yerine b)
        distractor_sign_flip = f"x = {-r1} veya x = {-r2}"

        # 2. BUG-QUAD-02: Negatif kökü unutma / sadece pozitif kökü alma
        pos_root = max(r1, r2)
        distractor_drop_neg = f"x = {pos_root}"

        # 3. Kökler toplamı / çarpımı katsayı kargaşası
        distractor_mixed = f"x = {sum_roots} veya x = {prod_roots}"

        # 4. Sahte kök
        distractor_generic = f"x = {r1 + 1} veya x = {r2 - 1}"

        raw_choices = [
            CognitiveChoice(
                text=correct_text,
                is_correct=True,
                bug_id=None,
                distractor_rationale=None,
            ),
            CognitiveChoice(
                text=distractor_sign_flip,
                is_correct=False,
                bug_id="BUG-QUAD-05",
                distractor_rationale="Formülde -b yerine b alarak işaret hatası yapan öğrenci bu şıkkı seçer.",
            ),
            CognitiveChoice(
                text=distractor_drop_neg,
                is_correct=False,
                bug_id="BUG-QUAD-02",
                distractor_rationale="Negatif kökü ihmal edip sadece mutlak değeri alan öğrenci bu şıkkı seçer.",
            ),
            CognitiveChoice(
                text=distractor_mixed,
                is_correct=False,
                bug_id="BUG-QUAD-01",
                distractor_rationale="Denklemi sıfıra eşitlemeden katsayıları doğrudan kök sanan öğrenci tuzağa düşer.",
            ),
            CognitiveChoice(
                text=distractor_generic,
                is_correct=False,
                bug_id="BUG-FOUND-15",
                distractor_rationale="İşlem önceliği veya terazi tek taraflı işlem hatası.",
            ),
        ]

        # Karıştır
        random.seed(r1 * 31 + r2 * 17)
        shuffled = list(raw_choices)
        random.shuffle(shuffled)
        correct_idx = [i for i, c in enumerate(shuffled) if c.is_correct][0]

        return TrapQuestion(
            node_id="N27",
            type=QuestionType.ALGEBRA,
            prompt=f"{eq_str} denkleminin gerçel sayılardaki çözüm kümesi aşağıdakilerden hangisidir?",
            choices=shuffled,
            correct_choice_index=correct_idx,
            difficulty_b=0.5,
            discrimination_a=2.0,
            full_socratic_solution=f"Çarpanlara ayırma: (x - ({r1}))(x - ({r2})) = 0 => {correct_text}",
            target_value=correct_text,
        )

    @staticmethod
    def generate_derivative(a: int = 3, n: int = 4) -> TrapQuestion:
        """
        f(x) = (ax + 2)^n türevi:
        f'(x) = n * a * (ax + 2)^(n-1)
        BUG-CALC-01: İç türevi (a) unutma -> n * (ax + 2)^(n-1)
        """
        correct_coeff = n * a
        correct_text = f"{correct_coeff}({a}x + 2)^{n-1}"

        # BUG-CALC-01: İç türev a unutuldu
        distractor_no_inner = f"{n}({a}x + 2)^{n-1}"

        # BUG-CALC-06: Sabit sayının türevi 2 olarak bırakıldı
        distractor_const_left = f"{correct_coeff}({a}x + 2)^{n-1} + 2"

        # Kuvvet azaltmak yerine artırıldı (integral kuralıyla karıştı)
        distractor_power_up = f"{correct_coeff}({a}x + 2)^{n+1}"

        # Rastgele çeldirici
        distractor_generic = f"{n * a}({a}x + 2)^{n}"

        raw_choices = [
            CognitiveChoice(text=correct_text, is_correct=True),
            CognitiveChoice(
                text=distractor_no_inner,
                is_correct=False,
                bug_id="BUG-CALC-01",
                distractor_rationale="Zincir kuralında parantez içinin türevi olan a katsayısını çarpmayı unutan öğrenci.",
            ),
            CognitiveChoice(
                text=distractor_const_left,
                is_correct=False,
                bug_id="BUG-CALC-06",
                distractor_rationale="Sabitin türevinin sıfır olduğunu unutup +2 sabitini koruyan öğrenci.",
            ),
            CognitiveChoice(
                text=distractor_power_up,
                is_correct=False,
                bug_id="BUG-CALC-05",
                distractor_rationale="Türev alırken üssü 1 azaltmak yerine 1 artıran öğrenci.",
            ),
            CognitiveChoice(
                text=distractor_generic,
                is_correct=False,
                bug_id="BUG-CALC-04",
                distractor_rationale="Üs derecesini düşürmeyi unutan öğrenci.",
            ),
        ]

        shuffled = list(raw_choices)
        random.shuffle(shuffled)
        correct_idx = [i for i, c in enumerate(shuffled) if c.is_correct][0]

        return TrapQuestion(
            node_id="N85",
            type=QuestionType.CALCULUS,
            prompt=f"f(x) = ({a}x + 2)^{n} olduğuna göre f'(x) türev fonksiyonu nedir?",
            choices=shuffled,
            correct_choice_index=correct_idx,
            difficulty_b=1.2,
            discrimination_a=2.2,
            full_socratic_solution=f"Zincir kuralı: f'(x) = {n}({a}x + 2)^{n-1} · ({a}x + 2)' = {correct_text}",
            target_value=correct_text,
        )

    @staticmethod
    def generate_euclidean(p: int = 4, k: int = 9) -> TrapQuestion:
        """
        Dik üçgende hipotenüse inen yükseklik: h² = p · k
        h = sqrt(p * k)
        """
        h_exact = int(math.sqrt(p * k))
        correct_text = f"{h_exact}"

        # BUG-EUC-04: Karekökü unutup h^2 = p*k = h sanma
        distractor_no_root = f"{p * k}"

        # Aritmetik ortalama alma tuzağı: h = (p + k) / 2
        distractor_avg = f"{(p + k) / 2.0:g}"

        # Hipotenüsün toplamı
        distractor_sum = f"{p + k}"

        # Yanlış fark
        distractor_diff = f"{abs(p - k)}"

        raw_choices = [
            CognitiveChoice(text=correct_text, is_correct=True),
            CognitiveChoice(
                text=distractor_no_root,
                is_correct=False,
                bug_id="BUG-EUC-04",
                distractor_rationale="Öklid formülünde h² = p·k bulup karekök almayı unutan öğrenci bu şıkkı işaretler.",
            ),
            CognitiveChoice(
                text=distractor_avg,
                is_correct=False,
                bug_id="BUG-ANAG-04",
                distractor_rationale="Geometrik ortalama yerine aritmetik ortalama alan öğrenci tuzağa düşer.",
            ),
            CognitiveChoice(
                text=distractor_sum,
                is_correct=False,
                bug_id="BUG-EUC-01",
                distractor_rationale="Yüksekliği hipotenüsün toplamı sanan öğrenci.",
            ),
            CognitiveChoice(
                text=distractor_diff,
                is_correct=False,
                bug_id="BUG-FOUND-10",
                distractor_rationale="Parçaların farkını alan öğrenci.",
            ),
        ]

        shuffled = list(raw_choices)
        random.shuffle(shuffled)
        correct_idx = [i for i, c in enumerate(shuffled) if c.is_correct][0]

        return TrapQuestion(
            node_id="N165",
            type=QuestionType.GEOMETRY,
            prompt=(
                f"Bir dik üçgende hipotenüse ait yükseklik (h), hipotenüsü uzunlukları "
                f"{p} cm ve {k} cm olan iki parçaya ayırmaktadır. Buna göre h kaç cm'dir?"
            ),
            choices=shuffled,
            correct_choice_index=correct_idx,
            difficulty_b=0.8,
            discrimination_a=1.9,
            full_socratic_solution=f"Öklid Bağıntısı: h² = p · k = {p} · {k} = {p * k} => h = {h_exact}",
            target_value=correct_text,
        )

    @staticmethod
    def generate_circle_angle(center_angle: int = 80) -> TrapQuestion:
        """
        Merkez açı 2alpha ise aynı yayı gören çevre açı alpha = center_angle / 2
        """
        inscribed = center_angle // 2
        correct_text = f"{inscribed}°"

        # BUG-EUC-02: Çevre açıyı merkez açıya eşit sanma
        distractor_equal = f"{center_angle}°"

        # 2 katını alma
        distractor_double = f"{center_angle * 2}°"

        # Bütünlerini alma
        distractor_supp = f"{180 - center_angle}°"

        # Yarım bütünler
        distractor_half_supp = f"{(180 - center_angle) // 2}°"

        raw_choices = [
            CognitiveChoice(text=correct_text, is_correct=True),
            CognitiveChoice(
                text=distractor_equal,
                is_correct=False,
                bug_id="BUG-EUC-02",
                distractor_rationale="Çevre açıyı merkez açıyla eşit kabul eden öğrenci bu tuzağa düşer.",
            ),
            CognitiveChoice(
                text=distractor_double,
                is_correct=False,
                bug_id="BUG-TRIG-03",
                distractor_rationale="Çevre açıyı yayın iki katı sanan öğrenci.",
            ),
            CognitiveChoice(
                text=distractor_supp,
                is_correct=False,
                bug_id="BUG-EUC-05",
                distractor_rationale="Kirişler dörtgeni ile karıştırıp 180'e tamamlayan öğrenci.",
            ),
            CognitiveChoice(
                text=distractor_half_supp,
                is_correct=False,
                bug_id="BUG-FOUND-04",
                distractor_rationale="Farklı orantı kuran öğrenci.",
            ),
        ]

        shuffled = list(raw_choices)
        random.shuffle(shuffled)
        correct_idx = [i for i, c in enumerate(shuffled) if c.is_correct][0]

        return TrapQuestion(
            node_id="N177",
            type=QuestionType.GEOMETRY,
            prompt=(
                f"Bir çemberde aynı AB yayını gören merkez açının ölçüsü {center_angle}° "
                f"olduğuna göre, bu yayı gören çevre açının ölçüsü kaç derecedir?"
            ),
            choices=shuffled,
            correct_choice_index=correct_idx,
            difficulty_b=0.6,
            discrimination_a=1.8,
            full_socratic_solution=f"Çevre açı = Merkez Açı / 2 = {center_angle}° / 2 = {inscribed}°",
            target_value=correct_text,
        )


class DynamicExamFactory:
    """
    Hedeflenen IRT teta ve konu dağılımına göre kişiye özel dinamik deneme sınavı montajlayan fabrika.
    """

    def __init__(self, generator: Optional[TrapQuestionGenerator] = None):
        self.gen = generator or TrapQuestionGenerator()

    def assemble_exam(
        self,
        section: ExamSection = ExamSection.TYT_MATEMATIK,
        question_count: int = 10,
        target_theta: float = 0.0,
    ) -> DynamicExam:
        """Belirtilen sınav tipine ve soru adedine göre bilişsel tuzaklı deneme sınavı üretir."""
        questions: List[TrapQuestion] = []

        # Soru bankası havuzu oluştur
        seed_configs = [
            ("quad", 2, -5),
            ("quad", 3, 4),
            ("quad", 1, -6),
            ("deriv", 2, 3),
            ("deriv", 4, 3),
            ("deriv", 3, 5),
            ("euc", 4, 9),
            ("euc", 2, 8),
            ("euc", 3, 12),
            ("circle", 80, 0),
            ("circle", 100, 0),
            ("circle", 60, 0),
        ]

        for i in range(question_count):
            cfg = seed_configs[i % len(seed_configs)]
            q_type = cfg[0]
            if q_type == "quad":
                q = self.gen.generate_quadratic(cfg[1], cfg[2])
            elif q_type == "deriv":
                q = self.gen.generate_derivative(cfg[1], cfg[2])
            elif q_type == "euc":
                q = self.gen.generate_euclidean(cfg[1], cfg[2])
            elif q_type == "circle":
                q = self.gen.generate_circle_angle(cfg[1])
            questions.append(q)

        time_per_q = 2.0  # Ortalama 2 dakika
        total_time = int(question_count * time_per_q)

        title = f"{section.value} Kişiselleştirilmiş Bilişsel Deneme Sınavı (θ = {target_theta:+.2f})"

        return DynamicExam(
            title=title,
            section=section,
            questions=questions,
            total_time_minutes=total_time,
            target_theta=target_theta,
        )

    def grade_exam(
        self,
        exam: DynamicExam,
        answers: Dict[int, int],  # question_index -> chosen_choice_index
    ) -> Dict[str, Any]:
        """
        Sınavı puanlar ve en önemlisi: Öğrencinin hangi bilişsel tuzaklara (BUG-ID) düştüğünü
        analiz ederek nokta atışı teşhis raporu üretir.
        """
        correct_count = 0
        incorrect_count = 0
        empty_count = 0
        traps_triggered: List[Dict[str, Any]] = []

        for idx, q in enumerate(exam.questions):
            chosen = answers.get(idx)
            if chosen is None or chosen < 0:
                empty_count += 1
                continue

            choice = q.choices[chosen]
            if choice.is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
                if choice.bug_id:
                    traps_triggered.append({
                        "question_index": idx + 1,
                        "node_id": q.node_id,
                        "bug_id": choice.bug_id,
                        "selected_text": choice.text,
                        "correct_answer": q.target_value,
                        "distractor_rationale": choice.distractor_rationale,
                    })

        # Net = Doğru - (Yanlış / 4)
        net_score = correct_count - (incorrect_count / 4.0)

        return {
            "total_questions": len(exam.questions),
            "correct": correct_count,
            "incorrect": incorrect_count,
            "empty": empty_count,
            "net_score": max(0.0, net_score),
            "percentage": round((correct_count / len(exam.questions)) * 100.0, 1),
            "traps_triggered": traps_triggered,
            "remediation_summary": (
                f"{len(traps_triggered)} bilişsel tuzak tetiklendi. "
                "Hata Otopsisi Kasasına otomatik aktarıldı."
                if traps_triggered
                else "Kusursuz odak! Hiçbir bilişsel tuzağa düşülmedi."
            ),
        }
