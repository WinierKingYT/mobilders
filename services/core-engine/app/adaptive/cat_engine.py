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
        ]
        for it in items:
            self.item_pool[it.item_id] = it

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
            first_deriv = -theta * prior_weight
            second_deriv = -prior_weight

            for item_id, is_correct in administered_responses:
                item = self.item_pool[item_id]
                p = self.probability_correct(theta, item.discrimination_a, item.difficulty_b)
                y = 1.0 if is_correct else 0.0

                first_deriv += self.D * item.discrimination_a * (y - p)
                info = self.fisher_information(theta, item.discrimination_a, item.difficulty_b)
                second_deriv -= info

            if abs(second_deriv) < 1e-9:
                break

            step = first_deriv / second_deriv
            theta = theta - step

            # Uç değer kırpma (-3.5 ile +3.5 aralığı)
            theta = max(-3.5, min(3.5, theta))

            if abs(step) < 1e-4:
                break

        # Standart Hata (SE)
        total_info = prior_weight
        for item_id, _ in administered_responses:
            item = self.item_pool[item_id]
            total_info += self.fisher_information(theta, item.discrimination_a, item.difficulty_b)

        standard_error = 1.0 / math.sqrt(total_info)
        return theta, standard_error

    def select_next_item(
        self, current_theta: float, administered_item_ids: Set[str]
    ) -> Optional[CATItem]:
        """Kullanılmamış maddeler arasında Fisher bilgisini maksimize eden maddeyi seçer."""
        available_items = [
            it for it_id, it in self.item_pool.items() if it_id not in administered_item_ids
        ]

        if not available_items:
            return None

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
