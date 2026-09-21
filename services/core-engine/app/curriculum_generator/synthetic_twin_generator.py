"""
Kişiselleştirilmiş İkiz Alıştırma Jeneratörü (Synthetic Twin Practice Generator).
Öğrencinin kavramsal yanılgılarına (bug_id) göre Tersine Mühendislik (Reverse-SymPy)
kullanarak tam sayı köklere ve pedagojik hedefe sahip izomorfik taze sorular üretir.
"""
from __future__ import annotations
import uuid
import random
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TwinGenerateRequest(BaseModel):
    bug_id: str
    original_equation: Optional[str] = None
    user_id: Optional[str] = None
    difficulty_level: int = 1


class TwinQuestionResponse(BaseModel):
    twin_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_equation: str
    canonical_roots: List[float]
    targeted_bug_id: str
    targeted_bug_title: str
    pedagogical_focus: str
    hint: str
    difficulty_level: int = 1


class SyntheticTwinGenerator:
    """
    Kavramsal yanılgıları hedefe alarak izomorfik ikiz denklemler üreten Reverse-SymPy fabrikası.
    """

    BUG_METADATA: Dict[str, Dict[str, str]] = {
        "BUG-QUAD-01": {
            "title": "Sıfır-Çarpım Kuralı İhlali",
            "focus": "Eşitliğin sağ tarafı sıfırdan farklı iken çarpanları doğrudan sayıya eşitleme tuzağından kaçın.",
        },
        "BUG-QUAD-02": {
            "title": "Negatif İkiz Kök İhmali",
            "focus": "x² = c eşitliğinde negatif simetrik kökü (-√c) unutma.",
        },
        "BUG-QUAD-03": {
            "title": "Binom Karesi Açılım Hatası",
            "focus": "(x ± a)² açılımında orta terim olan 2ax'i unutma.",
        },
        "BUG-QUAD-04": {
            "title": "Tam Kare Denge Hatası",
            "focus": "Eşitliğin bir tarafına eklenen sayıyı diğer tarafa da ekleyerek teraziyi koru.",
        },
        "BUG-QUAD-05": {
            "title": "Kuadratik Formül Payda Hatası",
            "focus": "Formülde paydadaki 2a katsayısına ve -b işaretine dikkat et.",
        },
        "SIGN_FLIP": {
            "title": "Eksi İşareti Dağıtım Yanılgısı",
            "focus": "Parantez önündeki eksi işaretini parantez içindeki tüm terimlere dağıt.",
        },
    }

    @classmethod
    def generate(
        cls,
        bug_id: str,
        original_equation: Optional[str] = None,
        difficulty_level: int = 1,
    ) -> TwinQuestionResponse:
        b = bug_id.upper().strip()

        if b == "BUG-QUAD-01":
            return cls._generate_bug_quad_01(difficulty_level)
        elif b == "BUG-QUAD-02":
            return cls._generate_bug_quad_02(difficulty_level)
        elif b == "BUG-QUAD-03":
            return cls._generate_bug_quad_03(difficulty_level)
        elif b == "BUG-QUAD-04":
            return cls._generate_bug_quad_04(difficulty_level)
        elif b == "BUG-QUAD-05":
            return cls._generate_bug_quad_05(difficulty_level)
        elif "SIGN" in b:
            return cls._generate_sign_flip(difficulty_level)
        else:
            return cls._generate_generic_quadratic(b, difficulty_level)

    @classmethod
    def _generate_bug_quad_01(cls, difficulty: int) -> TwinQuestionResponse:
        """
        Sağ tarafı sıfır OLMAYAN kuadratik denklem:
        (x - a)(x - b) = c  (c != 0)
        Örnek: (x - 3)(x + 2) = 6 => x^2 - x - 12 = 0 => (x - 4)(x + 3) = 0 => kökler: 4, -3
        """
        presets = [
            {
                "eq": "(x - 3)(x + 2) = 6",
                "roots": [4.0, -3.0],
                "hint": "Sol tarafı aç: x² - x - 6 = 6. Sağdaki 6'yı sola at: x² - x - 12 = 0. Şimdi çarpanlarına ayır.",
            },
            {
                "eq": "(x - 1)(x - 6) = 6",
                "roots": [7.0, 0.0],
                "hint": "Sol tarafı aç: x² - 7x + 6 = 6. Her iki taraftan 6 çıkar: x² - 7x = 0. x parantezine al.",
            },
            {
                "eq": "(x + 1)(x - 4) = 6",
                "roots": [5.0, -2.0],
                "hint": "Önce parantezleri çarp: x² - 3x - 4 = 6. 6'yı sola al: x² - 3x - 10 = 0.",
            },
        ]
        choice = random.choice(presets)
        return TwinQuestionResponse(
            target_equation=choice["eq"],
            canonical_roots=choice["roots"],
            targeted_bug_id="BUG-QUAD-01",
            targeted_bug_title="Sıfır-Çarpım Kuralı İhlali",
            pedagogical_focus="Eşitliğin sağ tarafı sıfırdan farklıdır. Doğrudan çarpanları eşitleyemezsin; önce tüm terimleri bir tarafa toplayıp diğer tarafı 0 yapmalısın.",
            hint=choice["hint"],
            difficulty_level=difficulty,
        )

    @classmethod
    def _generate_bug_quad_02(cls, difficulty: int) -> TwinQuestionResponse:
        """
        x² = c veya ax² = b formatında negatif ikiz kökü hatırlatan denklem.
        """
        presets = [
            {
                "eq": "x² = 49",
                "roots": [7.0, -7.0],
                "hint": "Karesi 49 olan sayılar: x = 7 ve x = -7.",
            },
            {
                "eq": "2x² = 72",
                "roots": [6.0, -6.0],
                "hint": "Önce her iki tarafı 2'ye böl: x² = 36. Ardından hem pozitif hem negatif karekökü al.",
            },
            {
                "eq": "x² - 64 = 0",
                "roots": [8.0, -8.0],
                "hint": "x² = 64 eşitliğini yaz. x = 8 veya x = -8 köklerini unutma.",
            },
        ]
        choice = random.choice(presets)
        return TwinQuestionResponse(
            target_equation=choice["eq"],
            canonical_roots=choice["roots"],
            targeted_bug_id="BUG-QUAD-02",
            targeted_bug_title="Negatif İkiz Kök İhmali",
            pedagogical_focus="Karesi pozitif bir sayı olan kuadratik denklemlerde mutlaka simetrik iki kök (±√c) vardır.",
            hint=choice["hint"],
            difficulty_level=difficulty,
        )

    @classmethod
    def _generate_bug_quad_03(cls, difficulty: int) -> TwinQuestionResponse:
        """
        (x ± a)² açılımı gerektiren ve orta terimi sınayan denklem.
        """
        presets = [
            {
                "eq": "(x - 4)² = 25",
                "roots": [9.0, -1.0],
                "hint": "(x - 4)² = x² - 8x + 16 veya x - 4 = ±5 eşitliklerinden birini kullanabilirsin.",
            },
            {
                "eq": "(x + 3)² = 16",
                "roots": [1.0, -7.0],
                "hint": "x + 3 = 4 veya x + 3 = -4. Buradan x = 1 ve x = -7 elde edilir.",
            },
            {
                "eq": "(x - 5)² = 9",
                "roots": [8.0, 2.0],
                "hint": "(x - 5)² açılımında ortadaki -10x terimini hatırla.",
            },
        ]
        choice = random.choice(presets)
        return TwinQuestionResponse(
            target_equation=choice["eq"],
            canonical_roots=choice["roots"],
            targeted_bug_id="BUG-QUAD-03",
            targeted_bug_title="Binom Karesi Açılım Hatası",
            pedagogical_focus="(x ± a)² ifadesi x² ± a² değildir; ortadaki 2ax terimi mutlaka korunmalıdır.",
            hint=choice["hint"],
            difficulty_level=difficulty,
        )

    @classmethod
    def _generate_bug_quad_04(cls, difficulty: int) -> TwinQuestionResponse:
        """
        Tam kareye tamamlama: x² + 2kx = m
        """
        presets = [
            {
                "eq": "x² + 6x = 16",
                "roots": [2.0, -8.0],
                "hint": "(6/2)² = 9. Her iki tarafa 9 ekle: x² + 6x + 9 = 16 + 9 => (x + 3)² = 25.",
            },
            {
                "eq": "x² - 8x = 9",
                "roots": [9.0, -1.0],
                "hint": "(-8/2)² = 16. Her iki tarafa 16 ekle: x² - 8x + 16 = 9 + 16 => (x - 4)² = 25.",
            },
        ]
        choice = random.choice(presets)
        return TwinQuestionResponse(
            target_equation=choice["eq"],
            canonical_roots=choice["roots"],
            targeted_bug_id="BUG-QUAD-04",
            targeted_bug_title="Tam Kare Denge Hatası",
            pedagogical_focus="Eşitliğin sol tarafına tam kare yapmak için eklenen terim, teraziyi korumak için sağ tarafa da eklenmelidir.",
            hint=choice["hint"],
            difficulty_level=difficulty,
        )

    @classmethod
    def _generate_bug_quad_05(cls, difficulty: int) -> TwinQuestionResponse:
        """
        Kuadratik formül: ax² + bx + c = 0 (a > 1)
        """
        presets = [
            {
                "eq": "2x² - 5x + 2 = 0",
                "roots": [2.0, 0.5],
                "hint": "a = 2, b = -5, c = 2. Paydada 2a = 4 olduğuna ve -(-5) = +5 olduğuna dikkat et.",
            },
            {
                "eq": "2x² - 7x + 3 = 0",
                "roots": [3.0, 0.5],
                "hint": "Δ = b² - 4ac = 49 - 24 = 25. Kökler: (7 ± 5) / 4.",
            },
        ]
        choice = random.choice(presets)
        return TwinQuestionResponse(
            target_equation=choice["eq"],
            canonical_roots=choice["roots"],
            targeted_bug_id="BUG-QUAD-05",
            targeted_bug_title="Kuadratik Formül Payda Hatası",
            pedagogical_focus="Kuadratik formülde paydadaki 2a katsayısı ve -b işaretine dikkat et: x = (-b ± √Δ) / (2a).",
            hint=choice["hint"],
            difficulty_level=difficulty,
        )

    @classmethod
    def _generate_sign_flip(cls, difficulty: int) -> TwinQuestionResponse:
        """
        İşaret dağılımı: -(ax - b) içeren denklem.
        """
        presets = [
            {
                "eq": "-(2x - 5) + 3x = 9",
                "roots": [4.0],
                "hint": "Parantezi aç: -2x + 5 + 3x = 9 => x + 5 = 9 => x = 4.",
            },
            {
                "eq": "(3x + 2) - (x - 6) = 14",
                "roots": [3.0],
                "hint": "-(x - 6) açılımı -x + 6 olur. 3x + 2 - x + 6 = 14 => 2x + 8 = 14 => x = 3.",
            },
        ]
        choice = random.choice(presets)
        return TwinQuestionResponse(
            target_equation=choice["eq"],
            canonical_roots=choice["roots"],
            targeted_bug_id="SIGN_FLIP",
            targeted_bug_title="Eksi İşareti Dağıtım Yanılgısı",
            pedagogical_focus="Parantez önündeki eksi işareti içerideki tüm terimlerin işaretini değiştirir: -(a - b) = -a + b.",
            hint=choice["hint"],
            difficulty_level=difficulty,
        )

    @classmethod
    def _generate_generic_quadratic(cls, bug_id: str, difficulty: int) -> TwinQuestionResponse:
        """
        Genel temiz tamsayı köklü kuadratik denklem.
        """
        r1 = random.choice([2, 3, 4, 5])
        r2 = random.choice([-1, -2, 1, 6])
        sum_r = r1 + r2
        prod_r = r1 * r2
        b_sign = f"- {sum_r}" if sum_r >= 0 else f"+ {abs(sum_r)}"
        c_sign = f"+ {prod_r}" if prod_r >= 0 else f"- {abs(prod_r)}"
        eq = f"x² {b_sign}x {c_sign} = 0"

        return TwinQuestionResponse(
            target_equation=eq,
            canonical_roots=[float(r1), float(r2)],
            targeted_bug_id=bug_id,
            targeted_bug_title=f"Kavramsal Pekiştirme ({bug_id})",
            pedagogical_focus="Temel cebirsel kuralları adım adım uygulayarak denklemi çöz.",
            hint=f"Çarpımları {prod_r} ve toplamları {sum_r} olan iki sayı bul.",
            difficulty_level=difficulty,
        )
