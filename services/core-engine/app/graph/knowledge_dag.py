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
