"""
Multi-Curriculum Standard Ontology Mapper.
Maps the 26-node Algebra/Quadratic Knowledge DAG to international curriculum standards:
- Türkiye MEB (Milli Eğitim Bakanlığı)
- IB DP Mathematics (Analysis & Approaches AA, Applications & Interpretation AI)
- US Common Core State Standards (CCSS Math)
- AP Precalculus (College Board)
"""

from __future__ import annotations
from typing import Dict, List, Optional
from app.models.schemas import CurriculumStandard


class CurriculumOntologyRegistry:
    """Registry maintaining cross-curriculum alignment across all 26 DAG nodes."""

    CURRICULA = ["MEB", "IB_AA", "IB_AI", "CCSS", "AP_PRECALC"]

    def __init__(self):
        self._standards: Dict[str, List[CurriculumStandard]] = {}
        self._build_standards()

    def _build_standards(self) -> None:
        raw_standards = [
            # N01: Negatif Sayılarla İşlemler
            CurriculumStandard(
                standard_id="MEB-7.1.1.1",
                curriculum="MEB",
                node_id="N01",
                title_tr="Tam Sayılarla Çarpma ve Bölme İşlemleri",
                title_en="Operations with Integers and Signed Numbers",
                description_tr="Tam sayılarla çarpma ve bölme işlemlerini yapar, işaret kurallarını kavrar.",
                description_en="Multiply and divide integers; understand signs and absolute value.",
                grade_level="7",
            ),
            CurriculumStandard(
                standard_id="CCSS-7.NS.A.1",
                curriculum="CCSS",
                node_id="N01",
                title_tr="Rasyonel Sayılarla Toplama ve Çıkarma",
                title_en="Operations with Negative Integers and Rational Numbers",
                description_tr="Negatif sayılar ve rasyonel işlemler kuralları.",
                description_en="Apply and extend previous understandings of addition and subtraction to add and subtract rational numbers.",
                grade_level="Grade 7",
            ),

            # N04: Lineer Denklem Çözme
            CurriculumStandard(
                standard_id="MEB-8.2.2.1",
                curriculum="MEB",
                node_id="N04",
                title_tr="Birinci Dereceden Bir Bilinmeyenli Denklemler",
                title_en="Linear Equations in One Variable",
                description_tr="Birinci dereceden bir bilinmeyenli denklemleri çözer.",
                description_en="Solve linear equations in one variable with rational number coefficients.",
                grade_level="8",
            ),
            CurriculumStandard(
                standard_id="CCSS-HSA-REI.B.3",
                curriculum="CCSS",
                node_id="N04",
                title_tr="Birinci Dereceden Denklemleri Çözme",
                title_en="Solve Linear Equations and Inequalities",
                description_tr="Tek değişkenli doğrusal denklemleri çözer.",
                description_en="Solve linear equations and inequalities in one variable, including equations with coefficients represented by letters.",
                grade_level="High School",
            ),

            # N06: İki Kare Farkı
            CurriculumStandard(
                standard_id="MEB-8.2.1.3",
                curriculum="MEB",
                node_id="N06",
                title_tr="Özdeşlikler ve İki Kare Farkı",
                title_en="Difference of Two Squares Identity",
                description_tr="a² - b² = (a - b)(a + b) özdeşliğini modeller ve cebirsel olarak uygular.",
                description_en="Factor algebraic expressions using the difference of two squares pattern.",
                grade_level="8",
            ),
            CurriculumStandard(
                standard_id="IB-AA-SL-1.2",
                curriculum="IB_AA",
                node_id="N06",
                title_tr="Cebirsel İfadelerin Çarpanlara Ayrılması",
                title_en="Algebraic Manipulation and Factorization",
                description_tr="Özdeşlikler ve çarpanlara ayırma.",
                description_en="Algebraic manipulation of quadratic and polynomial forms.",
                grade_level="DP1",
            ),

            # N08: Monik Üçterimlileri Çarpanlara Ayırma
            CurriculumStandard(
                standard_id="MEB-10.3.2.1",
                curriculum="MEB",
                node_id="N08",
                title_tr="Polinom ve Üçterimlilerin Çarpanlara Ayrılması",
                title_en="Factoring Monic Quadratic Trinomials",
                description_tr="x² + bx + c biçimindeki ifadeleri çarpanlarına ayırır.",
                description_en="Factor trinomials of the form x^2 + bx + c.",
                grade_level="10",
            ),
            CurriculumStandard(
                standard_id="CCSS-HSA-SSE.B.3.A",
                curriculum="CCSS",
                node_id="N08",
                title_tr="Kökleri Belirlemek İçin Çarpanlara Ayırma",
                title_en="Factor Quadratic Expression to Reveal Zeros",
                description_tr="Kökleri ortaya çıkarmak için ikinci dereceden ifadeleri çarpanlarına ayırır.",
                description_en="Factor a quadratic expression to reveal the zeros of the function it defines.",
                grade_level="High School",
            ),

            # N10: İkinci Dereceden Denklem Standart Formu
            CurriculumStandard(
                standard_id="MEB-10.4.1.1",
                curriculum="MEB",
                node_id="N10",
                title_tr="İkinci Dereceden Denklem Tanımı ve Standart Form",
                title_en="Quadratic Equations in Standard Form",
                description_tr="ax² + bx + c = 0 formundaki denklemleri tanır ve temel kavramlarını açıklar.",
                description_en="Recognize and manipulate quadratic equations in standard form ax^2 + bx + c = 0.",
                grade_level="10",
            ),
            CurriculumStandard(
                standard_id="IB-AA-SL-2.1",
                curriculum="IB_AA",
                node_id="N10",
                title_tr="Kuadratik Fonksiyonlar ve Denklemler",
                title_en="Quadratic Models and Equations",
                description_tr="Kuadratik fonksiyon ve denklemlerin temel özellikleri.",
                description_en="The quadratic function and forms: standard form, factorized form, vertex form.",
                grade_level="DP1",
            ),

            # N12: Çarpanlara Ayırma ile Çözüm
            CurriculumStandard(
                standard_id="MEB-10.4.1.1.A",
                curriculum="MEB",
                node_id="N12",
                title_tr="Çarpanlara Ayırma Yöntemi ile Denklem Çözme",
                title_en="Solving Quadratics by Factoring",
                description_tr="İkinci dereceden bir bilinmeyenli denklemleri çarpanlara ayırma ile çözer.",
                description_en="Solve quadratic equations by applying the zero-product property to factored forms.",
                grade_level="10",
            ),
            CurriculumStandard(
                standard_id="CCSS-HSA-REI.B.4.B",
                curriculum="CCSS",
                node_id="N12",
                title_tr="İkinci Dereceden Denklemleri Çözme",
                title_en="Solve Quadratic Equations by Inspection and Factoring",
                description_tr="Gözlem ve çarpanlara ayırma ile ikinci dereceden denklemleri çözer.",
                description_en="Solve quadratic equations by inspection, taking square roots, and factoring.",
                grade_level="High School",
            ),

            # N15: Cebirsel Tam Kareye Tamamlama
            CurriculumStandard(
                standard_id="MEB-10.4.1.1.B",
                curriculum="MEB",
                node_id="N15",
                title_tr="Tam Kareye Tamamlama Yöntemi",
                title_en="Completing the Square Method",
                description_tr="İkinci dereceden denklemleri tam kareye tamamlayarak çözer.",
                description_en="Solve quadratic equations by completing the square.",
                grade_level="10",
            ),
            CurriculumStandard(
                standard_id="CCSS-HSA-REI.B.4.A",
                curriculum="CCSS",
                node_id="N15",
                title_tr="Tam Kareye Tamamlama",
                title_en="Use Completing the Square to Solve Quadratics",
                description_tr="ax² + bx + c = 0 formunu (x - p)² = q formuna dönüştürür.",
                description_en="Use the method of completing the square to transform any quadratic equation into an equation of the form (x - p)^2 = q.",
                grade_level="High School",
            ),
            CurriculumStandard(
                standard_id="IB-AI-SL-2.4",
                curriculum="IB_AI",
                node_id="N15",
                title_tr="Kuadratik Modeller ve Dönüşümler",
                title_en="Quadratic Models and Vertex Transformations",
                description_tr="Tam kare formuna getirerek modelleme.",
                description_en="Quadratic models, vertex form by completing the square.",
                grade_level="DP1",
            ),

            # N18: Kuadratik Formülün Standart Uygulanışı
            CurriculumStandard(
                standard_id="MEB-10.4.1.1.C",
                curriculum="MEB",
                node_id="N18",
                title_tr="Kuadratik Formül ile Kök Bulma",
                title_en="Quadratic Formula Solution",
                description_tr="Kuadratik formülü kullanarak denklemin köklerini bulur.",
                description_en="Apply the quadratic formula x = (-b +- sqrt(b^2 - 4ac)) / (2a).",
                grade_level="10",
            ),
            CurriculumStandard(
                standard_id="IB-AA-SL-2.1.B",
                curriculum="IB_AA",
                node_id="N18",
                title_tr="Kuadratik Formül ve Kökler",
                title_en="The Quadratic Formula and Exact Roots",
                description_tr="Kuadratik formül ve rasyonel/irrasyonel kökler.",
                description_en="Use of the quadratic formula to find exact roots.",
                grade_level="DP1",
            ),

            # N20: Diskriminant ve Kök Türü İlişkisi
            CurriculumStandard(
                standard_id="MEB-10.4.1.1.D",
                curriculum="MEB",
                node_id="N20",
                title_tr="Diskriminantın Kök Varlığı ile İlişkisi",
                title_en="Nature of Roots via Discriminant",
                description_tr="Δ = b² - 4ac değerine göre reel ve karmaşık kök durumlarını inceler.",
                description_en="Determine the number and nature of roots using the discriminant Delta = b^2 - 4ac.",
                grade_level="10",
            ),
            CurriculumStandard(
                standard_id="IB-AA-SL-2.1.C",
                curriculum="IB_AA",
                node_id="N20",
                title_tr="Diskriminant Analizi (Δ)",
                title_en="The Discriminant Delta and Nature of Roots",
                description_tr="Δ > 0, Δ = 0 ve Δ < 0 durumları.",
                description_en="The discriminant Delta = b^2 - 4ac and the nature of the roots: two distinct real roots, two equal real roots, no real roots.",
                grade_level="DP1",
            ),

            # N21-N23: İkinci Dereceden Eşitsizlikler
            CurriculumStandard(
                standard_id="MEB-11.3.2.1",
                curriculum="MEB",
                node_id="N21",
                title_tr="İkinci Dereceden Eşitsizlikler ve Çözüm Kümeleri",
                title_en="Quadratic Inequalities and Sign Tables",
                description_tr="ax² + bx + c ≶ 0 eşitsizliklerinin işaret tablosu ile çözümünü yapar.",
                description_en="Solve quadratic inequalities in one variable using sign charts.",
                grade_level="11",
            ),
            CurriculumStandard(
                standard_id="IB-AA-HL-2.1",
                curriculum="IB_AA",
                node_id="N22",
                title_tr="Eşitsizliklerin Analitik Çözümü",
                title_en="Analytical and Graphical Solution of Inequalities",
                description_tr="Kuadratik eşitsizliklerin analitik ve grafiksel çözümü.",
                description_en="Solving quadratic inequalities analytically and graphically.",
                grade_level="DP2",
            ),

            # N24-N26: Parabol ve Fonksiyon Dönüşümleri
            CurriculumStandard(
                standard_id="MEB-11.3.1.2",
                curriculum="MEB",
                node_id="N24",
                title_tr="İkinci Dereceden Fonksiyon Grafiği (Parabol)",
                title_en="Quadratic Functions and Parabola Graphs",
                description_tr="Parabolün tepe noktası, simetri ekseni ve eksen kesimlerini belirler.",
                description_en="Determine vertex, axis of symmetry, and intercepts of parabolas.",
                grade_level="11",
            ),
            CurriculumStandard(
                standard_id="AP-PRECALC-1.2",
                curriculum="AP_PRECALC",
                node_id="N25",
                title_tr="Polinom ve Kuadratik Fonksiyonlarda Değişim",
                title_en="Rates of Change in Quadratic and Polynomial Functions",
                description_tr="Kuadratik modellerde ortalama değişim hızı ve tepe noktası dönüşümleri.",
                description_en="Examine vertex transformations f(x) = a(x-h)^2 + k and rates of change in quadratic models.",
                grade_level="Grade 11-12",
            ),
        ]

        for s in raw_standards:
            if s.curriculum not in self._standards:
                self._standards[s.curriculum] = []
            self._standards[s.curriculum].append(s)

    def get_standards_for_curriculum(self, curriculum: str) -> List[CurriculumStandard]:
        return self._standards.get(curriculum.upper(), [])

    def get_standard_for_node(self, node_id: str, curriculum: str) -> Optional[CurriculumStandard]:
        standards = self.get_standards_for_curriculum(curriculum)
        for s in standards:
            if s.node_id == node_id:
                return s
        return None

    def get_all_standards(self) -> List[CurriculumStandard]:
        all_std = []
        for std_list in self._standards.values():
            all_std.extend(std_list)
        return all_std
