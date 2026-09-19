"""
Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru (HEDEF 11)
Üçgen, Dörtgen, Çember kısıt çözücüsü ve Sokratik Ek Çizim Önerici.
"""
from __future__ import annotations
import math
from typing import Optional, Dict, Any, List, Tuple


class Triangle2D:
    """
    Öklid düzleminde sentetik üçgen nesnesi.
    Kenar uzunlukları (a, b, c) ve karşılarındaki açılar (A, B, C derece).
    """

    def __init__(
        self,
        a: Optional[float] = None,
        b: Optional[float] = None,
        c: Optional[float] = None,
        angle_A: Optional[float] = None,
        angle_B: Optional[float] = None,
        angle_C: Optional[float] = None,
    ):
        self.a = float(a) if a is not None else None
        self.b = float(b) if b is not None else None
        self.c = float(c) if c is not None else None
        self.angle_A = float(angle_A) if angle_A is not None else None
        self.angle_B = float(angle_B) if angle_B is not None else None
        self.angle_C = float(angle_C) if angle_C is not None else None

        self._solve_triangle()

    def _solve_triangle(self) -> None:
        """Eksik açı veya kenarları kosinüs ve sinüs teoremleriyle tamamlar."""
        # 1. İki açı verilmişse üçüncüyü tamamla
        angles = [self.angle_A, self.angle_B, self.angle_C]
        known_angles = [ang for ang in angles if ang is not None]
        if len(known_angles) == 2:
            rem = 180.0 - sum(known_angles)
            if rem <= 0:
                raise ValueError("Üçgenin iki açısının toplamı 180° veya daha büyük olamaz!")
            if self.angle_A is None:
                self.angle_A = rem
            elif self.angle_B is None:
                self.angle_B = rem
            elif self.angle_C is None:
                self.angle_C = rem

        # 2. Üç kenar biliniyorsa açıları Kosinüs Teoremiyle hesapla
        if self.a and self.b and self.c:
            if not self.satisfies_triangle_inequality():
                raise ValueError(
                    f"Verilen kenarlar ({self.a}, {self.b}, {self.c}) üçgen eşitsizliğini sağlamıyor!"
                )
            if self.angle_A is None:
                cos_A = (self.b**2 + self.c**2 - self.a**2) / (2.0 * self.b * self.c)
                self.angle_A = math.degrees(math.acos(max(-1.0, min(1.0, cos_A))))
            if self.angle_B is None:
                cos_B = (self.a**2 + self.c**2 - self.b**2) / (2.0 * self.a * self.c)
                self.angle_B = math.degrees(math.acos(max(-1.0, min(1.0, cos_B))))
            if self.angle_C is None:
                self.angle_C = 180.0 - self.angle_A - self.angle_B

    def satisfies_triangle_inequality(self) -> bool:
        """Üçgen eşitsizliği: |b - c| < a < b + c"""
        if not (self.a and self.b and self.c):
            return True
        return (
            (self.a < self.b + self.c)
            and (self.b < self.a + self.c)
            and (self.c < self.a + self.b)
            and (self.a > abs(self.b - self.c))
            and (self.b > abs(self.a - self.c))
            and (self.c > abs(self.a - self.b))
        )

    @property
    def is_right_angled(self) -> bool:
        """Dik üçgen mi (Pisagor kontrolü veya 90° açı)? """
        if self.angle_A and math.isclose(self.angle_A, 90.0, abs_tol=1e-3):
            return True
        if self.angle_B and math.isclose(self.angle_B, 90.0, abs_tol=1e-3):
            return True
        if self.angle_C and math.isclose(self.angle_C, 90.0, abs_tol=1e-3):
            return True
        if self.a and self.b and self.c:
            sides = sorted([self.a, self.b, self.c])
            return math.isclose(sides[0] ** 2 + sides[1] ** 2, sides[2] ** 2, abs_tol=1e-5)
        return False

    @property
    def is_isosceles(self) -> bool:
        """İkizkenar üçgen mi?"""
        if self.a and self.b and math.isclose(self.a, self.b, abs_tol=1e-5):
            return True
        if self.b and self.c and math.isclose(self.b, self.c, abs_tol=1e-5):
            return True
        if self.a and self.c and math.isclose(self.a, self.c, abs_tol=1e-5):
            return True
        if self.angle_A and self.angle_B and math.isclose(self.angle_A, self.angle_B, abs_tol=1e-3):
            return True
        if self.angle_B and self.angle_C and math.isclose(self.angle_B, self.angle_C, abs_tol=1e-3):
            return True
        if self.angle_A and self.angle_C and math.isclose(self.angle_A, self.angle_C, abs_tol=1e-3):
            return True
        return False

    @property
    def is_equilateral(self) -> bool:
        """Eşkenar üçgen mi?"""
        if self.a and self.b and self.c:
            return (
                math.isclose(self.a, self.b, abs_tol=1e-5)
                and math.isclose(self.b, self.c, abs_tol=1e-5)
            )
        if self.angle_A and self.angle_B and self.angle_C:
            return (
                math.isclose(self.angle_A, 60.0, abs_tol=1e-3)
                and math.isclose(self.angle_B, 60.0, abs_tol=1e-3)
            )
        return False

    @property
    def perimeter(self) -> float:
        if not (self.a and self.b and self.c):
            raise ValueError("Tüm kenarlar bilinmeden çevre hesaplanamaz.")
        return self.a + self.b + self.c

    @property
    def area(self) -> float:
        """Heron formülü: Alan = sqrt(s(s-a)(s-b)(s-c))"""
        if self.a and self.b and self.c:
            s = self.perimeter / 2.0
            val = s * (s - self.a) * (s - self.b) * (s - self.c)
            return math.sqrt(max(0.0, val))
        elif self.a and self.b and self.angle_C:
            rad = math.radians(self.angle_C)
            return 0.5 * self.a * self.b * math.sin(rad)
        raise ValueError("Yeterli veri yok.")

    @property
    def inradius(self) -> float:
        """İç teğet çember yarıçapı: r = Alan / s"""
        s = self.perimeter / 2.0
        return self.area / s

    @property
    def circumradius(self) -> float:
        """Çevrel çember yarıçapı: R = abc / (4 * Alan)"""
        if not (self.a and self.b and self.c):
            raise ValueError("Kenarlar eksik.")
        return (self.a * self.b * self.c) / (4.0 * self.area)

    def altitude_to_base(self, side: str = "a") -> float:
        """Seçilen kenara inen yükseklik: h = 2 * Alan / kenar"""
        length = getattr(self, side, None)
        if not length:
            raise ValueError(f"Kenar {side} bilinmiyor.")
        return 2.0 * self.area / length

    def median_to_base(self, side: str = "a") -> float:
        """Kenarortay uzunluğu: 2 * V_a^2 = b^2 + c^2 - a^2 / 2"""
        if not (self.a and self.b and self.c):
            raise ValueError("Tüm kenarlar gereklidir.")
        if side == "a":
            return 0.5 * math.sqrt(2 * self.b**2 + 2 * self.c**2 - self.a**2)
        elif side == "b":
            return 0.5 * math.sqrt(2 * self.a**2 + 2 * self.c**2 - self.b**2)
        elif side == "c":
            return 0.5 * math.sqrt(2 * self.a**2 + 2 * self.b**2 - self.c**2)
        raise ValueError("Geçersiz kenar.")


class EuclideanRelations:
    """
    Dik üçgende Öklid bağıntıları:
    Hipotenüs: a = p + k
    Yükseklik: h
    Dik kenarlar: b, c (burada b² = k·a, c² = p·a)
    """

    @staticmethod
    def height_from_segments(p: float, k: float) -> float:
        """h² = p · k"""
        if p <= 0 or k <= 0:
            raise ValueError("Ayırdığı parçalar pozitif olmalıdır.")
        return math.sqrt(p * k)

    @staticmethod
    def leg_from_segment_and_hypotenuse(segment: float, hypotenuse: float) -> float:
        """b² = k · a"""
        if segment <= 0 or hypotenuse <= 0 or segment > hypotenuse:
            raise ValueError("Geçersiz parça veya hipotenüs uzunluğu.")
        return math.sqrt(segment * hypotenuse)

    @staticmethod
    def verify_area_product(b: float, c: float, a: float, h: float) -> bool:
        """b · c = a · h (Çift alan bağıntısı)"""
        return math.isclose(b * c, a * h, abs_tol=1e-5)


class AuxiliaryConstructionAdvisor:
    """
    Sokratik Akıllı Ek Çizim Motoru (Smart Auxiliary Line Scaffold).
    Öğrencinin takıldığı geometrik konfigürasyonu analiz edip çözüm yolunu
    açan pedagojik ek çizim stratejisini önerir (Asla nihai cevabı sızdırmaz!).
    """

    @staticmethod
    def suggest_construction(configuration: Dict[str, Any]) -> Dict[str, str]:
        """
        Geometrik yapı taşlarına göre en uygun Sokratik ek çizim hamlesini üretir.
        """
        shape_type = configuration.get("type", "").lower()
        properties = configuration.get("properties", [])
        goal = configuration.get("goal", "")

        # 1. İkizkenar Üçgen Konfigürasyonu
        if "ikizkenar" in properties or shape_type == "isosceles_triangle":
            return {
                "action": "TABANA_DIKME_INDIR",
                "pedagogical_hint": (
                    "İkizkenar üçgende tabana ait yardımcı bir yükseklik indirmeyi dene. "
                    "Bu dikme hem tabanı iki eşit parçaya böler (kenarortay) hem de tepe açısını ortalar (açıortay)."
                ),
                "visual_type": "altitude_to_base",
                "rationale": "İkizkenar üçgende tepe açısından tabana inen dikme simetri eksenidir.",
            }

        # 2. Dik Üçgende Hipotenüs Kenarortayı (Muhteşem Üçlü)
        if "dik_ucgen" in properties and ("kenarortay" in properties or "hipotenus_orta" in properties):
            return {
                "action": "MUHTESEM_UCLU_CIZ",
                "pedagogical_hint": (
                    "Dik köşeden hipotenüsün orta noktasına bir kenarortay çizmeyi dene. "
                    "Dik üçgende hipotenüse inen kenarortay, ayırdığı parçaların uzunluğuna eşittir (Muhteşem Üçlü)."
                ),
                "visual_type": "median_to_hypotenuse",
                "rationale": "V_a = a / 2",
            }

        # 3. İki Kenarın Orta Noktaları (Orta Taban)
        if "orta_nokta" in properties or "midpoints" in properties:
            return {
                "action": "ORTA_TABAN_BIRLESTIR",
                "pedagogical_hint": (
                    "Üçgenin iki kenarının orta noktalarını bir doğru parçası ile birleştir. "
                    "Oluşan orta taban üçüncü kenara paraleldir ve uzunluğu o kenarın tam yarısıdır."
                ),
                "visual_type": "midsegment",
                "rationale": "Thales benzerliği: 1:2 oranı ve paralellik sağlar.",
            }

        # 4. Yamuk Konfigürasyonu
        if shape_type == "yamuk" or "trapezoid" in properties:
            if "alan" in goal or "yukseklik" in goal:
                return {
                    "action": "TABANA_DIKLER_INDIR",
                    "pedagogical_hint": (
                        "Üst köşelerden alt tabana iki dikme indirerek şekli bir dikdörtgen ve iki dik üçgene ayır."
                    ),
                    "visual_type": "trapezoid_altitudes",
                    "rationale": "Yamuğu dikdörtgen ve dik üçgenlere ayrıştırarak Pisagor uygulamayı sağlar.",
                }
            else:
                return {
                    "action": "YAN_KENARA_PARALEL_CIZ",
                    "pedagogical_hint": (
                        "Üst köşelerden birinden karşı yan kenara bir paralel doğru parçası çizerek bir paralelkenar ve bir üçgen oluştur."
                    ),
                    "visual_type": "trapezoid_parallel_leg",
                    "rationale": "Yamuğu paralelkenar ve üçgene dönüştürerek açı ve kenar taşımayı sağlar.",
                }

        # 5. Çemberde Teğet Noktası
        if "cember_teget" in properties or shape_type == "circle_tangent":
            return {
                "action": "MERKEZI_TEGET_NOKTASINA_BIRLESTIR",
                "pedagogical_hint": (
                    "Çemberin merkezini teğet doğrusunun değme noktasına birleştir. "
                    "Yarıçap doğrusu teğete değme noktasında diktir (r ⊥ d)."
                ),
                "visual_type": "radius_to_tangent",
                "rationale": "Teğet noktasında 90° dik açı ve dik üçgen elde edilir.",
            }

        # 6. Çemberde Kiriş
        if "cember_kiris" in properties or shape_type == "circle_chord":
            return {
                "action": "MERKEZDEN_KIRISE_DIKME_INDIR",
                "pedagogical_hint": (
                    "Çemberin merkezinden kirişe bir dikme indir. "
                    "Merkezden indirilen dikme kirişi ve kirişin gördüğü yayı iki eşit parçaya böler."
                ),
                "visual_type": "perpendicular_to_chord",
                "rationale": "Kirişi ortalayarak dik üçgen ve Pisagor bağıntısı kurar.",
            }

        # 7. Çapı Gören Çevre Açı
        if "cap" in properties and "cevre_aci" in properties:
            return {
                "action": "CAPI_GOREN_UCGENI_TAMAMLA",
                "pedagogical_hint": (
                    "Çember üzerindeki noktayı çapın iki ucuna birleştirerek çevre açı oluştur. "
                    "Çapı gören çevre açı daima 90°'dir."
                ),
                "visual_type": "diameter_inscribed_triangle",
                "rationale": "180°'lik yarım çember yayını gören çevre açı 90° dik üçgen üretir.",
            }

        # Genel Varsayılan Öneri
        return {
            "action": "OZEL_ACI_KARSISINA_DIKME_IN",
            "pedagogical_hint": (
                "30°, 45° veya 60° gibi özel bir açı görüyorsan, karşısına bir dikme indirerek özel dik üçgen oluşturmayı dene."
            ),
            "visual_type": "perpendicular_to_special_angle",
            "rationale": "Özel açılarda (30-60-90, 45-45-90) kenar oranlarını doğrudan kullanma imkanı sunar.",
        }


def solve_synthetic_geometry(task: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Sentetik Öklid geometrisi ve akıllı ek çizim problemlerini çözen motor arayüzü.
    """
    if task == "triangle_solve":
        t = Triangle2D(
            a=kwargs.get("a"),
            b=kwargs.get("b"),
            c=kwargs.get("c"),
            angle_A=kwargs.get("angle_A"),
            angle_B=kwargs.get("angle_B"),
            angle_C=kwargs.get("angle_C"),
        )
        return {
            "a": t.a,
            "b": t.b,
            "c": t.c,
            "angle_A": t.angle_A,
            "angle_B": t.angle_B,
            "angle_C": t.angle_C,
            "is_right_angled": t.is_right_angled,
            "is_isosceles": t.is_isosceles,
            "is_equilateral": t.is_equilateral,
            "perimeter": t.perimeter if (t.a and t.b and t.c) else None,
            "area": t.area if (t.a and t.b and (t.c or t.angle_C)) else None,
        }
    elif task == "euclidean_height":
        h = EuclideanRelations.height_from_segments(kwargs["p"], kwargs["k"])
        return {
            "height": h,
            "formula": "h^2 = p * k",
        }
    elif task == "euclidean_leg":
        leg = EuclideanRelations.leg_from_segment_and_hypotenuse(kwargs["segment"], kwargs["hypotenuse"])
        return {
            "leg": leg,
            "formula": "leg^2 = segment * hypotenuse",
        }
    elif task == "auxiliary_advisor":
        config = kwargs.get("configuration", kwargs)
        return AuxiliaryConstructionAdvisor.suggest_construction(config)
    raise ValueError(f"Bilinmeyen sentetik geometri görevi: {task}")

