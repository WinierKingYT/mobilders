from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


class CycleDetectedError(Exception):
    """Graf içinde döngüsel bağımlılık (circular dependency) tespit edildiğinde fırlatılır."""
    pass


@dataclass
class KnowledgeNode:
    id: str
    canonical_code: str
    title: str
    level: int
    strict_prereqs: List[str] = field(default_factory=list)
    soft_prereqs: List[str] = field(default_factory=list)
    description: str = ""
    default_difficulty_b: float = 0.0  # 2PL-IRT b parametresi (-3.0 ile +3.0 arası)
    discrimination_a: float = 1.5      # 2PL-IRT a parametresi


class KnowledgeDAG:
    """
    İkinci Dereceden Denklemler 20 Çekirdek MVP Düğümünü barındıran
    Yönlü Döngüsüz Graf (Directed Acyclic Graph - DAG) motoru.
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self._build_mvp_quadratic_graph()
        self.assert_cycle_free()

    def _build_mvp_quadratic_graph(self) -> None:
        """20 MVP kuadratik düğüm ve önkoşul bağımlılıklarını kurar."""
        raw_nodes = [
            # SEVİYE 0: Temel Aritmetik ve Cebirsel Önkoşullar
            KnowledgeNode(
                id="N01",
                canonical_code="math.arith.signed_ops",
                title="Negatif Sayılarla İşlemler",
                level=0,
                strict_prereqs=[],
                default_difficulty_b=-2.5,
                discrimination_a=1.4,
                description="Pozitif ve negatif tam sayılarla dört işlem kuralları.",
            ),
            KnowledgeNode(
                id="N02",
                canonical_code="math.alg.distributive",
                title="Dağılma Özelliği",
                level=0,
                strict_prereqs=["N01"],
                default_difficulty_b=-2.0,
                discrimination_a=1.6,
                description="Çarpmanın toplama/çıkarma üzerine dağılması: a(b+c) = ab + ac.",
            ),
            KnowledgeNode(
                id="N03",
                canonical_code="math.alg.like_terms",
                title="Benzer Terimleri Birleştirme",
                level=0,
                strict_prereqs=["N01"],
                soft_prereqs=["N02"],
                default_difficulty_b=-1.8,
                discrimination_a=1.5,
                description="Aynı dereceli terimlerin katsayılarını toplama veya çıkarma.",
            ),
            KnowledgeNode(
                id="N04",
                canonical_code="math.alg.linear_solve",
                title="Birinci Dereceden Lineer Denklem Çözme",
                level=0,
                strict_prereqs=["N02", "N03"],
                default_difficulty_b=-1.5,
                discrimination_a=1.8,
                description="Tek bilinmeyenli ax + b = c denklemlerinde x'i yalnız bırakma.",
            ),

            # SEVİYE 1: Çarpanlara Ayırma ve Özdeşlikler
            KnowledgeNode(
                id="N05",
                canonical_code="math.alg.factoring.gcf",
                title="Ortak Çarpan Parantezine Alma",
                level=1,
                strict_prereqs=["N02"],
                default_difficulty_b=-1.2,
                discrimination_a=1.7,
                description="Terimlerdeki en büyük ortak çarpanı dışarı çıkarma.",
            ),
            KnowledgeNode(
                id="N06",
                canonical_code="math.alg.factoring.diff_squares",
                title="İki Kare Farkı Özdeşliği",
                level=1,
                strict_prereqs=["N01", "N05"],
                default_difficulty_b=-1.0,
                discrimination_a=1.9,
                description="a² - b² = (a - b)(a + b) çarpanlara ayırma özdeşliği.",
            ),
            KnowledgeNode(
                id="N07",
                canonical_code="math.alg.factoring.perfect_square",
                title="Tam Kare Özdeşliği",
                level=1,
                strict_prereqs=["N02", "N03"],
                default_difficulty_b=-0.7,
                discrimination_a=1.8,
                description="(a ± b)² = a² ± 2ab + b² açılımı ve geriye çarpanlara ayırma.",
            ),
            KnowledgeNode(
                id="N08",
                canonical_code="math.alg.factoring.monic_trinomials",
                title="Monik Üçterimlileri Çarpanlara Ayırma (x² + bx + c)",
                level=1,
                strict_prereqs=["N01", "N05"],
                soft_prereqs=["N07"],
                default_difficulty_b=-0.4,
                discrimination_a=2.0,
                description="Çarpımları c, toplamları b eden sayı çiftini bularak (x+p)(x+q) yazma.",
            ),
            KnowledgeNode(
                id="N09",
                canonical_code="math.alg.factoring.non_monic_trinomials",
                title="Genel Üçterimlileri Çarpanlara Ayırma (ax² + bx + c)",
                level=1,
                strict_prereqs=["N08"],
                default_difficulty_b=0.2,
                discrimination_a=1.9,
                description="a ≠ 1 durumunda gruplandırma (ac metodu) ile çarpanlara ayırma.",
            ),

            # SEVİYE 2: İkinci Dereceden Denklem Temelleri
            KnowledgeNode(
                id="N10",
                canonical_code="math.alg.quadratics.standard_form",
                title="İkinci Dereceden Denklem Standart Formu",
                level=2,
                strict_prereqs=["N04"],
                default_difficulty_b=-0.8,
                discrimination_a=1.6,
                description="ax² + bx + c = 0 (a ≠ 0) standart biçimi ve a, b, c katsayıları.",
            ),
            KnowledgeNode(
                id="N11",
                canonical_code="math.alg.quadratics.zero_product_property",
                title="Sıfır Çarpım İlkesi",
                level=2,
                strict_prereqs=["N04", "N10"],
                default_difficulty_b=-0.5,
                discrimination_a=2.2,
                description="A * B = 0 ise A = 0 veya B = 0 temel çözüm mantığı.",
            ),
            KnowledgeNode(
                id="N12",
                canonical_code="math.alg.quadratics.solve_by_factoring",
                title="Çarpanlara Ayırma Yoluyla Denklem Çözme",
                level=2,
                strict_prereqs=["N08", "N11"],
                default_difficulty_b=0.0,
                discrimination_a=2.1,
                description="Denklemi çarpanlarına ayırıp sıfır çarpım kuralıyla kökleri bulma.",
            ),
            KnowledgeNode(
                id="N13",
                canonical_code="math.alg.quadratics.solve_pure_square_root",
                title="Karekök Alma Yoluyla Çözüm (ax² = c)",
                level=2,
                strict_prereqs=["N04", "N10"],
                default_difficulty_b=-0.2,
                discrimination_a=1.9,
                description="x² = k denkleminde her iki tarafın karekökünü alıp x = ±√k bulma.",
            ),

            # SEVİYE 3: Tam Kareye Tamamlama ve Geometrik Model
            KnowledgeNode(
                id="N14",
                canonical_code="math.alg.quadratics.geometric_completing_square",
                title="Geometrik Alan Modeli ile Tam Kare",
                level=3,
                strict_prereqs=["N07", "N10"],
                default_difficulty_b=0.3,
                discrimination_a=1.7,
                description="Al-Harezmi x² ve x karolarıyla eksik köşeyi (b/2)² görselleştirme.",
            ),
            KnowledgeNode(
                id="N15",
                canonical_code="math.alg.quadratics.algebraic_completing_square",
                title="Cebirsel Tam Kareye Tamamlama",
                level=3,
                strict_prereqs=["N14", "N13"],
                default_difficulty_b=0.6,
                discrimination_a=2.0,
                description="Eşitliğin her iki tarafına (b/2)² terimi ekleyerek tam kare oluşturma.",
            ),
            KnowledgeNode(
                id="N16",
                canonical_code="math.alg.quadratics.solve_by_completing_square",
                title="Tam Kare Metodu ile Kök Bulma",
                level=3,
                strict_prereqs=["N15", "N13"],
                default_difficulty_b=0.8,
                discrimination_a=2.0,
                description="(x + d)² = k formundan kökleri x = -d ± √k olarak çıkarma.",
            ),

            # SEVİYE 4: Kuadratik Formül ve Diskriminant
            KnowledgeNode(
                id="N17",
                canonical_code="math.alg.quadratics.formula_derivation",
                title="Kuadratik Formülün İspatı",
                level=4,
                strict_prereqs=["N16"],
                default_difficulty_b=1.2,
                discrimination_a=1.8,
                description="ax² + bx + c = 0 genel formunu tam kareye tamamlayarak formülü elde etme.",
            ),
            KnowledgeNode(
                id="N18",
                canonical_code="math.alg.quadratics.formula_application",
                title="Kuadratik Formülün Standart Uygulanışı",
                level=4,
                strict_prereqs=["N10", "N13"],
                default_difficulty_b=0.5,
                discrimination_a=1.9,
                description="x = (-b ± √(b² - 4ac)) / (2a) formülünde katsayıları yerine koyup çözme.",
            ),
            KnowledgeNode(
                id="N19",
                canonical_code="math.alg.quadratics.discriminant_calc",
                title="Diskriminant Tanımı ve Hesaplanışı",
                level=4,
                strict_prereqs=["N01", "N18"],
                default_difficulty_b=0.4,
                discrimination_a=1.8,
                description="Δ = b² - 4ac teriminin doğru işaret ve parantezle hesaplanması.",
            ),
            KnowledgeNode(
                id="N20",
                canonical_code="math.alg.quadratics.discriminant_nature_of_roots",
                title="Diskriminant ve Kök Sayısı/Türü İlişkisi",
                level=4,
                strict_prereqs=["N19"],
                default_difficulty_b=0.9,
                discrimination_a=2.2,
                description="Δ > 0 (iki farklı reel kök), Δ = 0 (çakışık tek kök), Δ < 0 (reel kök yok).",
            ),

            # SEVİYE 5 - DÜĞÜM GRUBU A: İkinci Dereceden Eşitsizlikler
            KnowledgeNode(
                id="N21",
                canonical_code="math.alg.inequalities.standard_form",
                title="İkinci Dereceden Eşitsizlik Standart Formu",
                level=5,
                strict_prereqs=["N10", "N12"],
                default_difficulty_b=1.0,
                discrimination_a=2.0,
                description="ax² + bx + c ≶ 0 eşitsizliklerinin standart çarpan formunda incelenmesi.",
            ),
            KnowledgeNode(
                id="N22",
                canonical_code="math.alg.inequalities.sign_table",
                title="İkinci Dereceden İşaret Tablosu",
                level=5,
                strict_prereqs=["N20", "N21"],
                default_difficulty_b=1.3,
                discrimination_a=2.2,
                description="Köklerin sıralanması, başkatsayı a'nın işareti ile başlama ve tek/çift katlı kök kuralı.",
            ),
            KnowledgeNode(
                id="N23",
                canonical_code="math.alg.inequalities.solution_sets",
                title="Eşitsizlik Çözüm Kümeleri ve Aralıklar",
                level=5,
                strict_prereqs=["N22"],
                default_difficulty_b=1.5,
                discrimination_a=2.1,
                description="İşaret tablosuna göre çözüm kümesini açık/kapalı aralık veya birleşim olarak ifade etme.",
            ),

            # SEVİYE 5 - DÜĞÜM GRUBU B: Parabol ve Fonksiyon Dönüşümleri
            KnowledgeNode(
                id="N24",
                canonical_code="math.fun.parabola.vertex_and_axis",
                title="Parabol Tepe Noktası ve Simetri Ekseni",
                level=5,
                strict_prereqs=["N10", "N18"],
                default_difficulty_b=1.1,
                discrimination_a=2.1,
                description="T(r, k) tepe noktası apsisi r = -b/(2a), ordinatı k = f(r) ve simetri ekseni x = r.",
            ),
            KnowledgeNode(
                id="N25",
                canonical_code="math.fun.parabola.transformations",
                title="Tepe Noktası Formu ve Fonksiyon Ötelemeleri",
                level=5,
                strict_prereqs=["N16", "N24"],
                default_difficulty_b=1.4,
                discrimination_a=2.3,
                description="f(x) = a(x - r)² + k formunda düşey ve yatay ötelemelerin geometrik dinamikleri.",
            ),
            KnowledgeNode(
                id="N26",
                canonical_code="math.fun.parabola.intercepts_and_geometry",
                title="Parabol Eksen Kesimleri ve Diskriminant Geometrisi",
                level=5,
                strict_prereqs=["N20", "N24"],
                default_difficulty_b=1.6,
                discrimination_a=2.2,
                description="Parabolün x ve y eksenlerini kestiği noktalar ile diskriminantın geometrik görselleşmesi.",
            ),

            # SEVİYE 5 & 6: Paraboller ve İkinci Dereceden Fonksiyonlar İleri Müfredatı (N27 - N38)
            KnowledgeNode(
                id="N27",
                canonical_code="math.fun.parabola.vertex_k_formula",
                title="Tepe Noktası Ordinatı ve Formülü",
                level=5,
                strict_prereqs=["N24"],
                default_difficulty_b=1.2,
                discrimination_a=2.0,
                description="Tepe noktası T(r, k) koordinatlarında k = f(r) = (4ac - b²)/(4a) hesabı ve geometrik anlamı.",
            ),
            KnowledgeNode(
                id="N28",
                canonical_code="math.fun.parabola.symmetry_geometry",
                title="Simetri Ekseni ve Kökler Geometrisi",
                level=5,
                strict_prereqs=["N24", "N26"],
                default_difficulty_b=1.3,
                discrimination_a=2.1,
                description="x = r doğrusunun simetri ekseni olması, köklerin simetri eksenine eşit uzaklığı: |x1 - r| = |x2 - r|.",
            ),
            KnowledgeNode(
                id="N29",
                canonical_code="math.fun.parabola.discriminant_tangency",
                title="Parabol ve X-Ekseni Teğetlik Durumu",
                level=5,
                strict_prereqs=["N20", "N26"],
                default_difficulty_b=1.4,
                discrimination_a=2.2,
                description="Δ = 0 durumunda parabolün x-eksenine teğet olması ve tam kare kuralı (çakışık çift katlı kök).",
            ),
            KnowledgeNode(
                id="N30",
                canonical_code="math.fun.parabola.vertex_form_conversion",
                title="Standart Form ile Tepe Noktası Formu Dönüşümü",
                level=5,
                strict_prereqs=["N25", "N27"],
                default_difficulty_b=1.5,
                discrimination_a=2.2,
                description="f(x) = ax² + bx + c ifadesini tam kareye tamamlayarak a(x - r)² + k tepe formuna dönüştürme.",
            ),
            KnowledgeNode(
                id="N31",
                canonical_code="math.fun.parabola.leading_coeff_orientation",
                title="Başkatsayı ve Kolların Açıklığı/Yönü",
                level=5,
                strict_prereqs=["N24"],
                default_difficulty_b=0.8,
                discrimination_a=1.8,
                description="a > 0 iken kollar yukarı, a < 0 iken kollar aşağı; |a| büyüdükçe kolların y-eksenine yaklaşması (daralması).",
            ),
            KnowledgeNode(
                id="N32",
                canonical_code="math.fun.parabola.extrema_and_interval_optimization",
                title="Parabolde Maksimum/Minimum Değer ve Sınırlı Aralık Analizi",
                level=5,
                strict_prereqs=["N27", "N31"],
                default_difficulty_b=1.6,
                discrimination_a=2.3,
                description="Parabolün alabileceği en büyük/en küçük değer; [p, q] kapalı aralığında uç noktalar ve tepe noktası incelemesi.",
            ),
            KnowledgeNode(
                id="N33",
                canonical_code="math.fun.parabola.line_intersection",
                title="Parabol ile Doğrunun Birbirine Göre Durumları",
                level=6,
                strict_prereqs=["N20", "N26"],
                default_difficulty_b=1.7,
                discrimination_a=2.3,
                description="y = ax² + bx + c ile y = mx + n ortak çözümü: Δ > 0 (iki kesişim), Δ = 0 (teğet), Δ < 0 (kesişmez).",
            ),
            KnowledgeNode(
                id="N34",
                canonical_code="math.fun.parabola.parabola_intersection",
                title="İki Parabolün Birbirine Göre Durumları",
                level=6,
                strict_prereqs=["N33"],
                default_difficulty_b=1.8,
                discrimination_a=2.2,
                description="İki parabolün ortak çözüm denkleminin kökleri üzerinden kesişim noktalarının tespiti.",
            ),
            KnowledgeNode(
                id="N35",
                canonical_code="math.fun.parabola.equation_from_roots_and_point",
                title="Kökleri ve Bir Noktası Verilen Parabol Denklemi",
                level=6,
                strict_prereqs=["N12", "N26"],
                default_difficulty_b=1.3,
                discrimination_a=2.0,
                description="y = a(x - x1)(x - x2) formülünde verilen noktayı yerine koyarak a katsayısını ve denklemi bulma.",
            ),
            KnowledgeNode(
                id="N36",
                canonical_code="math.fun.parabola.equation_from_vertex_and_point",
                title="Tepe Noktası ve Bir Noktası Verilen Parabol Denklemi",
                level=6,
                strict_prereqs=["N25", "N27"],
                default_difficulty_b=1.4,
                discrimination_a=2.1,
                description="y = a(x - r)² + k formülünde tepe noktasını ve bilinen noktayı yerine koyarak a katsayısını çıkarma.",
            ),
            KnowledgeNode(
                id="N37",
                canonical_code="math.fun.parabola.equation_from_three_points",
                title="Üç Noktası Verilen Parabolün Denklemi",
                level=6,
                strict_prereqs=["N04", "N35"],
                default_difficulty_b=1.6,
                discrimination_a=2.1,
                description="Üç noktanın ax² + bx + c denklemini sağlamasından 3 bilinmeyenli 1. dereceden denklem sistemi kurup çözme.",
            ),
            KnowledgeNode(
                id="N38",
                canonical_code="math.fun.parabola.real_world_optimization",
                title="Parabolik Gerçek Hayat Modellemesi ve Optimizasyon",
                level=6,
                strict_prereqs=["N32", "N36"],
                default_difficulty_b=1.9,
                discrimination_a=2.4,
                description="Maksimum kâr, alan, atış yörüngesi gibi problemlerde fonksiyonu kuadratik modelleyip tepe noktasını yorumlama.",
            ),

            # SEVİYE 6 & 7: Polinomlar ve Polinom Cebiri (N39 - N50)
            KnowledgeNode(
                id="N39",
                canonical_code="math.poly.definition_and_degree",
                title="Polinom Tanımı, Derece, Katsayı ve Sabit Terim",
                level=6,
                strict_prereqs=["N03"],
                default_difficulty_b=0.7,
                discrimination_a=1.7,
                description="Doğal sayı dereceli terimler P(x) = an xⁿ + ... + a0; başkatsayı, derece ve sabit terim kavramları.",
            ),
            KnowledgeNode(
                id="N40",
                canonical_code="math.poly.arithmetic_and_degree_rules",
                title="Polinomlarda İşlemler ve Derece Aritmetiği",
                level=6,
                strict_prereqs=["N39"],
                default_difficulty_b=1.1,
                discrimination_a=1.9,
                description="Toplama, çıkarma, çarpma; deg(P ± Q) <= max, deg(P * Q) = deg(P) + deg(Q), deg(P(x^k)) = k * deg(P).",
            ),
            KnowledgeNode(
                id="N41",
                canonical_code="math.poly.division_algorithm",
                title="Polinom Bölmesi ve Bölme Bağıntısı",
                level=6,
                strict_prereqs=["N40"],
                default_difficulty_b=1.3,
                discrimination_a=2.0,
                description="P(x) = B(x) * Q(x) + K(x) bölme algoritması; bölünen, bölen, bölüm ve kalanın derecesi deg(K) < deg(B).",
            ),
            KnowledgeNode(
                id="N42",
                canonical_code="math.poly.remainder_theorem_linear",
                title="Kalan Teoremi ve (x - a) ile Bölüm",
                level=6,
                strict_prereqs=["N41"],
                default_difficulty_b=1.2,
                discrimination_a=2.1,
                description="Bölen x - a = 0 => x = a için P(a) değerinin doğrudan kalanı vermesi kuralı.",
            ),
            KnowledgeNode(
                id="N43",
                canonical_code="math.poly.remainder_theorem_linear_general",
                title="(ax + b) ile Bölümünden Kalan",
                level=6,
                strict_prereqs=["N42"],
                default_difficulty_b=1.4,
                discrimination_a=2.1,
                description="ax + b = 0 => x = -b/a kökünün P(-b/a) olarak kalanı vermesi.",
            ),
            KnowledgeNode(
                id="N44",
                canonical_code="math.poly.coeffs_sum_and_constant_term",
                title="Katsayılar Toplamı ve Sabit Terim Hesabı",
                level=6,
                strict_prereqs=["N39"],
                default_difficulty_b=0.9,
                discrimination_a=1.9,
                description="P(x) için katsayılar toplamı P(1), sabit terim P(0); P(mx + n) polinomlarında x yerine 1 ve 0 yazılması.",
            ),
            KnowledgeNode(
                id="N45",
                canonical_code="math.poly.even_odd_degree_coeffs",
                title="Çift ve Tek Dereceli Terim Katsayıları Toplamı",
                level=6,
                strict_prereqs=["N44"],
                default_difficulty_b=1.3,
                discrimination_a=2.0,
                description="Çift dereceli terimler toplamı (P(1) + P(-1))/2, tek dereceli terimler toplamı (P(1) - P(-1))/2.",
            ),
            KnowledgeNode(
                id="N46",
                canonical_code="math.poly.quadratic_divisor_remainder",
                title="İkinci Dereceden Bölen ile Kalan Bulma",
                level=7,
                strict_prereqs=["N41", "N43"],
                default_difficulty_b=1.7,
                discrimination_a=2.3,
                description="Bölen 2. dereceden ise kalanın K(x) = mx + n formunda aranması ve kökler yardımıyla m, n katsayılarının bulunması.",
            ),
            KnowledgeNode(
                id="N47",
                canonical_code="math.poly.factor_theorem",
                title="Çarpan Teoremi ve Polinom Kökleri",
                level=7,
                strict_prereqs=["N42"],
                default_difficulty_b=1.4,
                discrimination_a=2.2,
                description="P(a) = 0 olması ile (x - a)'nın P(x)'in bir çarpanı olması denkliği ve kök kavramı.",
            ),
            KnowledgeNode(
                id="N48",
                canonical_code="math.poly.viete_relations",
                title="Polinomlarda Kök-Katsayı Bağıntıları (Viète)",
                level=7,
                strict_prereqs=["N18", "N47"],
                default_difficulty_b=1.8,
                discrimination_a=2.3,
                description="2. ve 3. derece polinomlarda kökler toplamı, kökler çarpımı ve ikişerli çarpımlar toplamı bağıntıları.",
            ),
            KnowledgeNode(
                id="N49",
                canonical_code="math.poly.graph_and_multiplicity",
                title="Polinom Grafikleri ve Kök Katlılığı (Multiplicity)",
                level=7,
                strict_prereqs=["N26", "N47"],
                default_difficulty_b=1.9,
                discrimination_a=2.4,
                description="Tek katlı köklerde ekseni kesme, çift katlı köklerde teğet olma ve uç davranışları (end behavior).",
            ),
            KnowledgeNode(
                id="N50",
                canonical_code="math.poly.higher_degree_inequalities",
                title="Yüksek Dereceli Polinom Eşitsizlikleri ve İşaret Tablosu",
                level=7,
                strict_prereqs=["N22", "N49"],
                default_difficulty_b=2.0,
                discrimination_a=2.4,
                description="P(x) ≶ 0 eşitsizliklerinde tüm köklerin bulunup işaret tablosuna yerleştirilmesi ve çözüm aralığı tayini.",
            ),
            # SEVİYE 8: Trigonometri & Birim Çember (N51 - N65)
            KnowledgeNode(
                id="N51",
                canonical_code="math.trig.angle_measures",
                title="Yönlü Açılar ve Esas Ölçü",
                level=8,
                strict_prereqs=["N01", "N05"],
                default_difficulty_b=0.4,
                discrimination_a=1.7,
                description="Pozitif/negatif yönlü açılar, derece-radya dönüşümü (D/180 = R/pi) ve [0, 2pi) esas ölçü hesabı.",
            ),
            KnowledgeNode(
                id="N52",
                canonical_code="math.trig.unit_circle_coords",
                title="Birim Çember ve Trigonometrik Koordinatlar",
                level=8,
                strict_prereqs=["N51", "N27"],
                default_difficulty_b=0.6,
                discrimination_a=1.8,
                description="Birim çember üzerindeki P(theta) noktasının koordinatları olarak cos(theta) ve sin(theta) tanımları.",
            ),
            KnowledgeNode(
                id="N53",
                canonical_code="math.trig.pythagorean_identity",
                title="Temel Trigonometrik Özdeşlikler",
                level=8,
                strict_prereqs=["N52", "N09"],
                default_difficulty_b=0.8,
                discrimination_a=1.9,
                description="sin^2(x) + cos^2(x) = 1, tan(x) = sin(x)/cos(x), cot(x) = cos(x)/sin(x), tan(x)cot(x) = 1.",
            ),
            KnowledgeNode(
                id="N54",
                canonical_code="math.trig.special_angles",
                title="Dik Üçgende Oranlar ve Özel Açılar",
                level=8,
                strict_prereqs=["N53"],
                default_difficulty_b=0.7,
                discrimination_a=1.8,
                description="30, 45, 60 derecelik özel açıların sin, cos, tan, cot değerleri ve dik üçgen geometrisi.",
            ),
            KnowledgeNode(
                id="N55",
                canonical_code="math.trig.reduction_formulas",
                title="Trigonometrik İndirgeme Formülleri ve Bölgeler",
                level=8,
                strict_prereqs=["N52", "N54"],
                default_difficulty_b=1.2,
                discrimination_a=2.1,
                description="Dört bölgede işaret analizi, pi ± x ve pi/2 ± x dönüşümlerinde isim ve işaret değişimi kuralları.",
            ),
            KnowledgeNode(
                id="N56",
                canonical_code="math.trig.period_and_graphs",
                title="Trigonometrik Fonksiyonların Periyotları ve Grafikleri",
                level=8,
                strict_prereqs=["N26", "N55"],
                default_difficulty_b=1.3,
                discrimination_a=2.0,
                description="sin, cos ve tan fonksiyonlarının periyotları, genlikleri ve dalga grafiklerinin çizimi.",
            ),
            KnowledgeNode(
                id="N57",
                canonical_code="math.trig.inverse_functions",
                title="Ters Trigonometrik Fonksiyonlar (Ark Fonksiyonlar)",
                level=8,
                strict_prereqs=["N56"],
                default_difficulty_b=1.5,
                discrimination_a=2.2,
                description="arcsin, arccos ve arctan fonksiyonlarının tanım ve değer aralıkları ile bileşke hesapları.",
            ),
            KnowledgeNode(
                id="N58",
                canonical_code="math.trig.law_of_cosines",
                title="Kosinüs Teoremi",
                level=8,
                strict_prereqs=["N53", "N54"],
                default_difficulty_b=1.1,
                discrimination_a=2.0,
                description="Herhangi bir üçgende a^2 = b^2 + c^2 - 2bc*cos(A) bağıntısı ile kenar ve açı hesaplama.",
            ),
            KnowledgeNode(
                id="N59",
                canonical_code="math.trig.law_of_sines_area",
                title="Sinüs Teoremi ve Üçgende Trigonometrik Alan",
                level=8,
                strict_prereqs=["N54", "N58"],
                default_difficulty_b=1.3,
                discrimination_a=2.1,
                description="a/sin(A) = b/sin(B) = c/sin(C) = 2R ve Alan = (1/2)*ab*sin(C) bağıntıları.",
            ),
            KnowledgeNode(
                id="N60",
                canonical_code="math.trig.sum_difference",
                title="Sinüs ve Kosinüs Toplam-Fark Formülleri",
                level=8,
                strict_prereqs=["N55", "N58"],
                default_difficulty_b=1.6,
                discrimination_a=2.3,
                description="sin(a ± b) = sin(a)cos(b) ± cos(a)sin(b) ve cos(a ± b) = cos(a)cos(b) ∓ sin(a)sin(b).",
            ),
            KnowledgeNode(
                id="N61",
                canonical_code="math.trig.tan_sum_difference",
                title="Tanjant Toplam-Fark Formülleri",
                level=8,
                strict_prereqs=["N53", "N60"],
                default_difficulty_b=1.7,
                discrimination_a=2.2,
                description="tan(a ± b) = (tan a ± tan b) / (1 ∓ tan a tan b) bağıntısı ve doğrular arası eğim açıları.",
            ),
            KnowledgeNode(
                id="N62",
                canonical_code="math.trig.double_angle",
                title="Yarım Açı (İki Kat Açı) Formülleri",
                level=8,
                strict_prereqs=["N60"],
                default_difficulty_b=1.5,
                discrimination_a=2.3,
                description="sin(2x) = 2sin(x)cos(x), cos(2x) = cos^2(x) - sin^2(x) = 2cos^2(x) - 1 = 1 - 2sin^2(x).",
            ),
            KnowledgeNode(
                id="N63",
                canonical_code="math.trig.half_angle_applications",
                title="Yarım Açı Tanjant ve İleri İndirgemeler",
                level=8,
                strict_prereqs=["N61", "N62"],
                default_difficulty_b=1.8,
                discrimination_a=2.3,
                description="tan(2x) = 2tan(x)/(1 - tan^2(x)) ve trigonometrik sadeleştirmelerde yarım açı uygulamaları.",
            ),
            KnowledgeNode(
                id="N64",
                canonical_code="math.trig.basic_equations",
                title="Temel Trigonometrik Denklemler",
                level=8,
                strict_prereqs=["N55", "N62"],
                default_difficulty_b=1.8,
                discrimination_a=2.4,
                description="sin(x) = a, cos(x) = b, tan(x) = c denklemlerinin kök aileleri (x = alpha + 2k*pi, vb.).",
            ),
            KnowledgeNode(
                id="N65",
                canonical_code="math.trig.quadratic_trig_equations",
                title="İkinci Dereceden ve Homojen Trigonometrik Denklemler",
                level=8,
                strict_prereqs=["N11", "N64"],
                default_difficulty_b=2.1,
                discrimination_a=2.5,
                description="a*sin^2(x) + b*sin(x) + c = 0 veya a*sin(x) + b*cos(x) = c tipli denklemlerin çözümü.",
            ),
            # SEVİYE 9: Üstel ve Logaritmik Fonksiyonlar (N66 - N80)
            KnowledgeNode(
                id="N66",
                canonical_code="math.exp.definition_properties",
                title="Üstel Fonksiyon Tanımı ve Temel Özellikleri",
                level=9,
                strict_prereqs=["N08", "N26"],
                default_difficulty_b=0.8,
                discrimination_a=1.8,
                description="f(x) = a^x (a > 0, a != 1) üstel fonksiyonu, tanım/değer kümesi ve monotonluğu.",
            ),
            KnowledgeNode(
                id="N67",
                canonical_code="math.exp.growth_decay_models",
                title="Üstel Büyüme ve Bozulma Modelleri",
                level=9,
                strict_prereqs=["N66"],
                default_difficulty_b=1.1,
                discrimination_a=1.9,
                description="N(t) = N_0 * a^(kt) modeli, bakteri popülasyonu, yarı ömür ve bileşik faiz hesabı.",
            ),
            KnowledgeNode(
                id="N68",
                canonical_code="math.exp.natural_exponential",
                title="Doğal Üstel Fonksiyon (e^x) ve Euler Sabiti",
                level=9,
                strict_prereqs=["N66"],
                default_difficulty_b=1.0,
                discrimination_a=1.9,
                description="e tabanlı doğal üstel fonksiyon f(x) = e^x, sürekli bileşik büyüme ve asimptot davranışı.",
            ),
            KnowledgeNode(
                id="N69",
                canonical_code="math.log.definition_inverse",
                title="Logaritma Tanımı ve Üstel Fonksiyon ile Terslik",
                level=9,
                strict_prereqs=["N66"],
                default_difficulty_b=1.2,
                discrimination_a=2.0,
                description="log_a(x) = y <=> a^y = x (a > 0, a != 1, x > 0) tanımı ve y = x doğrusuna göre simetri.",
            ),
            KnowledgeNode(
                id="N70",
                canonical_code="math.log.natural_common",
                title="Doğal Logaritma (ln) ve Onluk Logaritma (log)",
                level=9,
                strict_prereqs=["N68", "N69"],
                default_difficulty_b=1.1,
                discrimination_a=1.9,
                description="10 tabanında log(x) ve e tabanında ln(x) gösterimi, ln(e) = 1, log(10) = 1 özellikleri.",
            ),
            KnowledgeNode(
                id="N71",
                canonical_code="math.log.domain_constraints",
                title="Logaritma Fonksiyonunun En Geniş Tanım Kümesi",
                level=9,
                strict_prereqs=["N22", "N69"],
                default_difficulty_b=1.4,
                discrimination_a=2.2,
                description="log_{g(x)}(f(x)) için f(x) > 0, g(x) > 0 ve g(x) != 1 eşitsizlik sisteminin çözümü.",
            ),
            KnowledgeNode(
                id="N72",
                canonical_code="math.log.product_quotient_rules",
                title="Logaritma Çarpım ve Bölüm Özellikleri",
                level=9,
                strict_prereqs=["N69"],
                default_difficulty_b=1.3,
                discrimination_a=2.1,
                description="log_a(x * y) = log_a(x) + log_a(y) ve log_a(x / y) = log_a(x) - log_a(y) kuralları.",
            ),
            KnowledgeNode(
                id="N73",
                canonical_code="math.log.power_root_rules",
                title="Logaritma Kuvvet ve Kök Özellikleri",
                level=9,
                strict_prereqs=["N72"],
                default_difficulty_b=1.3,
                discrimination_a=2.1,
                description="log_a(x^k) = k * log_a(x) ve log_{a^n}(x^m) = (m/n) * log_a(x) özellikleri.",
            ),
            KnowledgeNode(
                id="N74",
                canonical_code="math.log.change_of_base",
                title="Logaritmada Taban Değiştirme Kuralı",
                level=9,
                strict_prereqs=["N70", "N73"],
                default_difficulty_b=1.6,
                discrimination_a=2.3,
                description="log_a(b) = log_c(b) / log_c(a) = ln(b) / ln(a) bağıntısı ve 1/log_b(a) simetrisi.",
            ),
            KnowledgeNode(
                id="N75",
                canonical_code="math.log.chain_and_exponent_identity",
                title="Logaritma Zincir Kuralı ve a^(log_a b) Özdeşliği",
                level=9,
                strict_prereqs=["N74"],
                default_difficulty_b=1.7,
                discrimination_a=2.3,
                description="log_a(b) * log_b(c) = log_a(c) zinciri ve a^(log_b c) = c^(log_b a), a^(log_a b) = b kuralları.",
            ),
            KnowledgeNode(
                id="N76",
                canonical_code="math.exp.equations_base_and_log",
                title="Üstel Denklemler ve Çözüm Yöntemleri",
                level=9,
                strict_prereqs=["N69", "N73"],
                default_difficulty_b=1.5,
                discrimination_a=2.2,
                description="Taban eşitleme veya her iki tarafın logaritmasını alarak x'i yalnız bırakma.",
            ),
            KnowledgeNode(
                id="N77",
                canonical_code="math.exp.substitution_quadratics",
                title="Değişken Değiştirme ile İkinci Dereceden Üstel Denklemler",
                level=9,
                strict_prereqs=["N11", "N76"],
                default_difficulty_b=1.8,
                discrimination_a=2.3,
                description="a^(2x) + b*a^x + c = 0 tipli denklemlerde u = a^x dönüşümü ve kök taraması.",
            ),
            KnowledgeNode(
                id="N78",
                canonical_code="math.log.equations_and_extraneous_roots",
                title="Logaritmik Denklemler ve Sahte Kök Kontrolü",
                level=9,
                strict_prereqs=["N71", "N72", "N76"],
                default_difficulty_b=1.9,
                discrimination_a=2.4,
                description="Logaritma özellikleriyle denklem çözme ve bulunan köklerin tanım kümesine uygunluğunun teyidi.",
            ),
            KnowledgeNode(
                id="N79",
                canonical_code="math.log.inequalities_base_cases",
                title="Logaritmik Eşitsizlikler ve Taban Analizi",
                level=9,
                strict_prereqs=["N22", "N71", "N78"],
                default_difficulty_b=2.1,
                discrimination_a=2.4,
                description="a > 1 iken eşitsizlik yönünün korunması, 0 < a < 1 iken yönün tersine dönmesi ve tanım aralığı kesişimi.",
            ),
            KnowledgeNode(
                id="N80",
                canonical_code="math.log.modeling_applications",
                title="Logaritmik Modelleme ve Gerçek Hayat Problemleri",
                level=9,
                strict_prereqs=["N70", "N78"],
                default_difficulty_b=1.7,
                discrimination_a=2.1,
                description="Richter deprem ölçeği (R = log(I/I_0)), pH asitlik skalası (-log[H+]) ve desibel ses düzeyi hesapları.",
            ),
        ]

        for node in raw_nodes:
            self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self.nodes.get(node_id)

    def get_all_node_ids(self) -> List[str]:
        return list(self.nodes.keys())

    def get_prerequisites(self, node_id: str, recursive: bool = False) -> Set[str]:
        """Bir düğümün katı önkoşullarını döndürür."""
        node = self.nodes.get(node_id)
        if not node:
            return set()

        direct = set(node.strict_prereqs)
        if not recursive:
            return direct

        all_prereqs = set(direct)
        for parent_id in direct:
            all_prereqs.update(self.get_prerequisites(parent_id, recursive=True))
        return all_prereqs

    def assert_cycle_free(self) -> None:
        """Kahn algoritması veya derinlik öncelikli arama ile grafın döngüsüz (DAG) olduğunu doğrular."""
        visited: Dict[str, int] = {}  # 0: visiting, 1: visited

        def dfs(curr_id: str):
            visited[curr_id] = 0  # visiting
            curr_node = self.nodes[curr_id]
            for parent_id in curr_node.strict_prereqs:
                if parent_id not in self.nodes:
                    raise KeyError(f"Düğüm {curr_id}, tanımlanmamış önkoşula ({parent_id}) sahip!")
                state = visited.get(parent_id)
                if state == 0:
                    raise CycleDetectedError(f"Döngüsel bağımlılık tespit edildi: {curr_id} -> {parent_id}")
                if state is None:
                    dfs(parent_id)
            visited[curr_id] = 1

        for n_id in self.nodes:
            if n_id not in visited:
                dfs(n_id)

    def topological_sort(self) -> List[str]:
        """Önkoşullara göre topolojik sıralanmış düğüm ID listesini döndürür."""
        in_degree = {n_id: len(node.strict_prereqs) for n_id, node in self.nodes.items()}
        # Sıfır önkoşula sahip kök düğümleri bul
        queue = [n_id for n_id, deg in in_degree.items() if deg == 0]
        sorted_nodes = []

        # Ters komşuluk: parent -> children
        children_map: Dict[str, List[str]] = {n_id: [] for n_id in self.nodes}
        for n_id, node in self.nodes.items():
            for p_id in node.strict_prereqs:
                children_map[p_id].append(n_id)

        while queue:
            # Belirlenebilir sıralama için sırala
            queue.sort()
            curr = queue.pop(0)
            sorted_nodes.append(curr)

            for child in children_map[curr]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(sorted_nodes) != len(self.nodes):
            raise CycleDetectedError("Graf içinde döngü var; topolojik sıralama tamamlanamadı!")

        return sorted_nodes

    def get_zpd_candidates(self, mastered_nodes: Set[str]) -> List[str]:
        """
        Öğrencinin Yakınsak Gelişim Alanındaki (ZPD) aday düğümleri bulur.
        Bir düğüm ZPD adayıdır ancak ve ancak:
        1. Öğrenci bu düğümde henüz ustalaşmamışsa.
        2. Bu düğümün TÜM katı önkoşullarında (strict prereqs) öğrenci ustalaşmışsa.
        """
        candidates = []
        for n_id, node in self.nodes.items():
            if n_id in mastered_nodes:
                continue
            # Tüm katı önkoşullar sağlandı mı?
            if all(p in mastered_nodes for p in node.strict_prereqs):
                candidates.append(n_id)
        return candidates

    def calculate_depth(self, node_id: str) -> int:
        """Düğümün köklerden olan azami uzaklığını (derinliğini) hesaplar."""
        node = self.nodes.get(node_id)
        if not node or not node.strict_prereqs:
            return 0
        return 1 + max(self.calculate_depth(p) for p in node.strict_prereqs)
