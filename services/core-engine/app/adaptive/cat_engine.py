import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from app.graph.knowledge_dag import KnowledgeDAG


@dataclass
class CATItem:
    item_id: str
    target_node_id: str
    difficulty_b: float
    discrimination_a: float
    prompt: str
    canonical_answer: str
    curriculum: str = "DEFAULT"


class CATEngine:
    """
    2-Parametreli Lojistik Madde Tepki Kuramı (2PL-IRT) tabanlı
    Bilgisayarlı Uyarlamalı Teşhis Testi (Computerized Adaptive Testing - CAT) motoru.
    """

    D = 1.7  # Normal ogive ölçek sabiti
    PRIOR_VARIANCE = 1.0  # N(0, 1) Gauss öncül varyansı

    def __init__(self, dag: Optional[KnowledgeDAG] = None):
        self.dag = dag or KnowledgeDAG()
        self.item_pool: Dict[str, CATItem] = {}
        self._load_calibrated_item_pool()

    def _load_calibrated_item_pool(self) -> None:
        items = [
            CATItem(
                item_id="CAT-ITEM-01",
                target_node_id="N12",
                difficulty_b=0.00,
                discrimination_a=2.85,
                prompt="x² - 5x + 6 = 0 denkleminin köklerini bulunuz.",
                canonical_answer="x=2 veya x=3",
            ),
            CATItem(
                item_id="CAT-ITEM-02",
                target_node_id="N20",
                difficulty_b=1.40,
                discrimination_a=2.80,
                prompt="2x² + 4x - 7 = 0 denkleminde diskriminant ile kök türünü belirleyiniz.",
                canonical_answer="Δ > 0 (iki farklı reel kök)",
            ),
            CATItem(
                item_id="CAT-ITEM-03",
                target_node_id="N06",
                difficulty_b=-1.10,
                discrimination_a=2.85,
                prompt="x² - 9 ifadesini çarpanlarına ayırınız.",
                canonical_answer="(x - 3)(x + 3)",
            ),
            CATItem(
                item_id="CAT-ITEM-04",
                target_node_id="N02",
                difficulty_b=-2.10,
                discrimination_a=2.75,
                prompt="-3(2x - 4) ifadesini açıp sadeleştiriniz.",
                canonical_answer="-6x + 12",
            ),
            CATItem(
                item_id="CAT-ITEM-05",
                target_node_id="N08",
                difficulty_b=-0.40,
                discrimination_a=2.90,
                prompt="x² + 7x + 12 ifadesini çarpanlarına ayırınız.",
                canonical_answer="(x + 3)(x + 4)",
            ),
            CATItem(
                item_id="CAT-ITEM-06",
                target_node_id="N15",
                difficulty_b=0.70,
                discrimination_a=2.85,
                prompt="x² + 6x ifadesini tam kare yapmak için eklenecek sabit nedir?",
                canonical_answer="9",
            ),
            CATItem(
                item_id="CAT-ITEM-07",
                target_node_id="N18",
                difficulty_b=1.05,
                discrimination_a=2.80,
                prompt="x² - 3x + 1 = 0 denklemini kuadratik formülle çözünüz.",
                canonical_answer="(3 ± √5) / 2",
            ),
            CATItem(
                item_id="CAT-ITEM-08",
                target_node_id="N20",
                difficulty_b=2.10,
                discrimination_a=2.70,
                prompt="h(t) = -5t² + 20t modelinde roketin yere düştüğü anı bulunuz.",
                canonical_answer="t = 4",
            ),
            CATItem(
                item_id="CAT-ITEM-09",
                target_node_id="N03",
                difficulty_b=-1.75,
                discrimination_a=2.80,
                prompt="5x - 15 = 0 denkleminin çözümünü bulunuz.",
                canonical_answer="x = 3",
            ),
            CATItem(
                item_id="CAT-ITEM-10",
                target_node_id="N10",
                difficulty_b=-0.75,
                discrimination_a=2.85,
                prompt="x² - 4x = 0 denklemini ortak paranteze alarak çözünüz.",
                canonical_answer="x = 0 veya x = 4",
            ),
            CATItem(
                item_id="CAT-ITEM-11",
                target_node_id="N16",
                difficulty_b=0.35,
                discrimination_a=2.90,
                prompt="x² + 4x + 1 = 0 denklemini tam kareye tamamlama yöntemiyle yazınız.",
                canonical_answer="(x + 2)² = 3",
            ),
            CATItem(
                item_id="CAT-ITEM-12",
                target_node_id="N19",
                difficulty_b=1.75,
                discrimination_a=2.75,
                prompt="3x² - 5x + 1 = 0 denkleminde diskriminant değerini (Δ) hesaplayınız.",
                canonical_answer="Δ = 13",
            ),
            CATItem(
                item_id="CAT-ITEM-13",
                target_node_id="N01",
                difficulty_b=-2.45,
                discrimination_a=2.70,
                prompt="2x + 6 = 0 denklemini sağlayan x değerini bulunuz.",
                canonical_answer="x = -3",
            ),
            CATItem(
                item_id="CAT-ITEM-14",
                target_node_id="N05",
                difficulty_b=-1.45,
                discrimination_a=2.85,
                prompt="(x + 2)(x - 2) ifadesini iki kare farkı olarak açınız.",
                canonical_answer="x² - 4",
            ),
            CATItem(
                item_id="CAT-ITEM-15",
                target_node_id="N14",
                difficulty_b=-0.10,
                discrimination_a=2.90,
                prompt="x² - x - 6 = 0 denklemini çarpanlarına ayırınız.",
                canonical_answer="(x - 3)(x + 2) = 0",
            ),
            CATItem(
                item_id="CAT-ITEM-16",
                target_node_id="N20",
                difficulty_b=2.45,
                discrimination_a=2.70,
                prompt="ax² + bx + c = 0 denkleminde b² - 4ac < 0 durumunda reel kök sayısını yazınız.",
                canonical_answer="0",
            ),
            CATItem(
                item_id="CAT-ITEM-17",
                target_node_id="N21",
                difficulty_b=1.00,
                discrimination_a=2.85,
                prompt="x² - 4x + 3 > 0 eşitsizliğini çarpanlarına ayırarak standart formda yazınız.",
                canonical_answer="(x - 1)(x - 3) > 0",
            ),
            CATItem(
                item_id="CAT-ITEM-18",
                target_node_id="N22",
                difficulty_b=1.30,
                discrimination_a=2.90,
                prompt="x² - 9 ≤ 0 eşitsizliğinin işaret tablosunda negatif olan bölgeyi aralık olarak yazınız.",
                canonical_answer="[-3, 3]",
            ),
            CATItem(
                item_id="CAT-ITEM-19",
                target_node_id="N23",
                difficulty_b=1.55,
                discrimination_a=2.80,
                prompt="(x - 2)(x + 5) < 0 eşitsizliğinin çözüm kümesini açık aralık olarak yazınız.",
                canonical_answer="(-5, 2)",
            ),
            CATItem(
                item_id="CAT-ITEM-20",
                target_node_id="N24",
                difficulty_b=1.15,
                discrimination_a=2.75,
                prompt="f(x) = x² - 6x + 5 parabolünün tepe noktasının apsisini (r = -b/(2a)) bulunuz.",
                canonical_answer="3",
            ),
            CATItem(
                item_id="CAT-ITEM-21",
                target_node_id="N25",
                difficulty_b=1.45,
                discrimination_a=2.85,
                prompt="f(x) = (x - 4)² + 2 parabolünün tepe noktası koordinatını (r, k) biçiminde yazınız.",
                canonical_answer="(4, 2)",
            ),
            CATItem(
                item_id="CAT-ITEM-22",
                target_node_id="N26",
                difficulty_b=1.65,
                discrimination_a=2.70,
                prompt="f(x) = x² - 4x parabolünün x eksenini kestiği pozitif apsis değerini bulunuz.",
                canonical_answer="4",
            ),
            # MEB Curriculum Calibrated Items
            CATItem(
                item_id="CAT-MEB-01",
                target_node_id="N10",
                difficulty_b=-0.60,
                discrimination_a=2.60,
                prompt="MEB: 2x² - 8x = 0 denkleminin çözüm kümesini bulunuz.",
                canonical_answer="{0, 4}",
                curriculum="MEB",
            ),
            CATItem(
                item_id="CAT-MEB-02",
                target_node_id="N12",
                difficulty_b=0.10,
                discrimination_a=2.90,
                prompt="MEB: x² - 7x + 10 = 0 denklemini çarpanlarına ayırarak çözünüz.",
                canonical_answer="{2, 5}",
                curriculum="MEB",
            ),
            CATItem(
                item_id="CAT-MEB-03",
                target_node_id="N18",
                difficulty_b=1.10,
                discrimination_a=2.80,
                prompt="MEB: x² - 4x + 1 = 0 denklemini kuadratik formül ile çözünüz.",
                canonical_answer="2 ± √3",
                curriculum="MEB",
            ),
            CATItem(
                item_id="CAT-MEB-04",
                target_node_id="N20",
                difficulty_b=1.35,
                discrimination_a=2.85,
                prompt="MEB: x² + 2x + 5 = 0 denkleminin reel sayılardaki çözüm kümesini diskriminant ile inceleyiniz.",
                canonical_answer="Boş küme (Reel kök yok)",
                curriculum="MEB",
            ),
            # IB Curriculum Calibrated Items
            CATItem(
                item_id="CAT-IB-01",
                target_node_id="N10",
                difficulty_b=-0.40,
                discrimination_a=2.75,
                prompt="IB: Express the quadratic function f(x) = 2x² - 12x + 10 in standard form.",
                canonical_answer="2(x - 1)(x - 5)",
                curriculum="IB",
            ),
            CATItem(
                item_id="CAT-IB-02",
                target_node_id="N15",
                difficulty_b=0.75,
                discrimination_a=2.85,
                prompt="IB: Write f(x) = x² + 8x + 11 in vertex form a(x-h)² + k by completing the square.",
                canonical_answer="(x + 4)² - 5",
                curriculum="IB",
            ),
            CATItem(
                item_id="CAT-IB-03",
                target_node_id="N22",
                difficulty_b=1.40,
                discrimination_a=2.90,
                prompt="IB: Solve the quadratic inequality x² - 5x - 14 ≤ 0.",
                canonical_answer="[-2, 7]",
                curriculum="IB",
            ),
            # US Common Core (CCSS) Calibrated Items
            CATItem(
                item_id="CAT-CCSS-01",
                target_node_id="N08",
                difficulty_b=-0.30,
                discrimination_a=2.80,
                prompt="CCSS: Factor the quadratic trinomial x² + 9x + 20.",
                canonical_answer="(x + 4)(x + 5)",
                curriculum="CCSS",
            ),
            CATItem(
                item_id="CAT-CCSS-02",
                target_node_id="N12",
                difficulty_b=0.20,
                discrimination_a=2.85,
                prompt="CCSS: Solve (x - 4)(x + 7) = 0 by applying the zero product property.",
                canonical_answer="x = 4, x = -7",
                curriculum="CCSS",
            ),
            # AP Precalculus Calibrated Items
            CATItem(
                item_id="CAT-AP-01",
                target_node_id="N24",
                difficulty_b=1.20,
                discrimination_a=2.80,
                prompt="AP: Find the axis of symmetry and vertex for the function f(x) = -2(x - 3)² + 8.",
                canonical_answer="x = 3, (3, 8)",
                curriculum="AP",
            ),
            CATItem(
                item_id="CAT-AP-02",
                target_node_id="N25",
                difficulty_b=1.60,
                discrimination_a=2.90,
                prompt="AP: Describe the transformation of y = x² to obtain g(x) = 0.5(x + 2)² - 4.",
                canonical_answer="Horizontal shift left 2, vertical compression by 0.5, vertical shift down 4",
                curriculum="AP",
            ),
        ]
        for it in items:
            self.item_pool[it.item_id] = it

    def get_items_by_curriculum(self, curriculum: str) -> List[CATItem]:
        """Returns all items tagged with a specific curriculum."""
        curr = curriculum.upper()
        return [it for it in self.item_pool.values() if it.curriculum.upper() == curr]

    def update_item_pool(self, calibrated_params: Dict[str, Tuple[float, float]]) -> None:
        """MMLE-EM veya harici kalibrasyondan gelen (a_i, b_i) parametrelerini madde havuzuna uygular."""
        for item_id, (cal_a, cal_b) in calibrated_params.items():
            if item_id in self.item_pool:
                self.item_pool[item_id].discrimination_a = cal_a
                self.item_pool[item_id].difficulty_b = cal_b

    def probability_correct(self, theta: float, a: float, b: float) -> float:
        """2PL-IRT başarı olasılığı: P(Y=1|theta) = 1 / (1 + exp(-1.7*a*(theta - b)))."""
        logit = self.D * a * (theta - b)
        # Sayısal kararlılık (overflow koruması)
        if logit > 35.0:
            return 1.0
        elif logit < -35.0:
            return 0.0
        return 1.0 / (1.0 + math.exp(-logit))

    def fisher_information(self, theta: float, a: float, b: float) -> float:
        """Fisher Bilgi Fonksiyonu: I(theta) = D^2 * a^2 * P * Q."""
        p = self.probability_correct(theta, a, b)
        q = 1.0 - p
        return (self.D ** 2) * (a ** 2) * p * q

    def estimate_theta(
        self, administered_responses: List[Tuple[str, bool]], initial_theta: float = 0.0
    ) -> Tuple[float, float]:
        """
        Bayesyen Maksimum Sonsal (Maximum A Posteriori - MAP) kestirimi.
        N(0, 1) Gauss öncülü ile sıfıra bölme ve ıraksama engellenir.
        Returns: (theta_hat, standard_error)
        """
        if not administered_responses:
            # Henüz yanıt yokken öncül dağılım
            return 0.0, 1.0 / math.sqrt(1.0 / self.PRIOR_VARIANCE)

        # Newton-Raphson iterasyonu
        theta = initial_theta
        prior_weight = 1.0 / self.PRIOR_VARIANCE

        for _ in range(25):
            f_prime = - (theta / self.PRIOR_VARIANCE)
            f_double_prime = - (1.0 / self.PRIOR_VARIANCE)

            for item_id, is_correct in administered_responses:
                if item_id not in self.item_pool:
                    continue
                item = self.item_pool[item_id]
                a = item.discrimination_a
                b = item.difficulty_b
                p = self.probability_correct(theta, a, b)
                y = 1.0 if is_correct else 0.0

                f_prime += self.D * a * (y - p)
                f_double_prime -= (self.D ** 2) * (a ** 2) * p * (1.0 - p)

            if abs(f_double_prime) < 1e-9:
                break

            delta = f_prime / f_double_prime
            theta -= delta

            if abs(delta) < 1e-4:
                break

        # Standard Error: SE(theta) = 1 / sqrt(I(theta) + 1/sigma^2)
        total_info = prior_weight
        for item_id, _ in administered_responses:
            if item_id not in self.item_pool:
                continue
            item = self.item_pool[item_id]
            total_info += self.fisher_information(theta, item.discrimination_a, item.difficulty_b)

        standard_error = 1.0 / math.sqrt(total_info)
        return theta, standard_error

    def select_next_item(
        self,
        current_theta: float,
        administered_item_ids: Set[str],
        curriculum: Optional[str] = None,
    ) -> Optional[CATItem]:
        """Kullanılmamış maddeler arasında Fisher bilgisini maksimize eden maddeyi seçer."""
        available_items = [
            it for it_id, it in self.item_pool.items() if it_id not in administered_item_ids
        ]

        if not available_items:
            return None

        # Filter by curriculum if specified and non-default
        if curriculum and curriculum.upper() not in ["DEFAULT", "ALL"]:
            curr_target = curriculum.upper()
            curr_filtered = [it for it in available_items if it.curriculum.upper() == curr_target]
            if curr_filtered:
                available_items = curr_filtered

        # Fisher bilgisini en yüksek yapan maddeyi bul
        best_item = max(
            available_items,
            key=lambda it: self.fisher_information(current_theta, it.discrimination_a, it.difficulty_b),
        )
        return best_item

    def is_test_complete(
        self, administered_responses: List[Tuple[str, bool]], current_se: float, max_items: int = 8, target_se: float = 0.35
    ) -> bool:
        """Durdurma kuralı: SE <= 0.35 veya maksimum soru sayısına ulaşıldı."""
        if len(administered_responses) >= max_items:
            return True
        if len(administered_responses) >= 3 and current_se <= target_se:
            return True
        return False

    def seed_knowledge_dag(self, theta_hat: float) -> Dict[str, float]:
        """
        Kestirilen theta yeteneğini 20 düğümlü Bilgi Grafı üzerindeki
        başlangıç ustalık olasılıklarına P(L_0) dönüştürür.
        """
        node_mastery: Dict[str, float] = {}

        for n_id, node in self.dag.nodes.items():
            p_mastery = self.probability_correct(
                theta=theta_hat,
                a=node.discrimination_a,
                b=node.default_difficulty_b,
            )
            node_mastery[n_id] = round(p_mastery, 4)

        return node_mastery
