from typing import Dict, List, Optional, Set
from app.root_pedagogy.models import RootNode


class RootPrerequisiteDAG:
    """
    Seviye -3..-1 Kök Matematik Ontolojisi ve Önkoşul Grafı (DAG N_ROOT_01 - N_ROOT_16).
    Hiçbir matematik temeli olmayan veya geçmişte kopmuş bir öğrencinin
    kök kavram eksikliklerini haritalandırır.
    """

    def __init__(self):
        self.nodes: Dict[str, RootNode] = {}
        self._build_root_nodes()
        self.assert_cycle_free()

    def _build_root_nodes(self) -> None:
        raw_nodes = [
            # SEVİYE -3: Sayı Hissi, Yön ve İşaret Sezgisi
            RootNode(
                id="N_ROOT_01",
                canonical_code="math.root.number_line_direction",
                title="Sayı Doğrusu ve Yön Sezgisi",
                level=-3.0,
                strict_prereqs=[],
                description="Sıfırın sağı pozitif/kazanç, solu negatif/kayıptır. Sayı doğrusunda sola gidildikçe değer küçülür.",
            ),
            RootNode(
                id="N_ROOT_02",
                canonical_code="math.root.debt_credit_model",
                title="Borç / Alacak ve Sıcaklık Modeli",
                level=-3.0,
                strict_prereqs=["N_ROOT_01"],
                description="-6 - 5 = -11; borcun büyümesi sezgisi ve termometre sıcaklık düşüşü.",
            ),
            RootNode(
                id="N_ROOT_03",
                canonical_code="math.root.opposite_signs_addition",
                title="Zıt İşaretlerin Toplanması",
                level=-3.0,
                strict_prereqs=["N_ROOT_01", "N_ROOT_02"],
                description="-8 + 5 = -3; mutlak değeri büyük olanın işaretinin baskın gelmesi.",
            ),
            RootNode(
                id="N_ROOT_04",
                canonical_code="math.root.sign_rules_mul_div",
                title="Çarpma ve Bölmede İşaret Kuralları",
                level=-3.0,
                strict_prereqs=["N_ROOT_03"],
                description="(+)·(-) = (-), (-)·(-) = (+); tersin tersi pozitiftir yön kuralı.",
            ),

            # SEVİYE -2.5: Kesirler ve Rasyonel Sezgi
            RootNode(
                id="N_ROOT_05",
                canonical_code="math.root.fraction_division_model",
                title="Kesir Bir Bölmedir (Dilim Modeli)",
                level=-2.5,
                strict_prereqs=["N_ROOT_01"],
                description="Pasta/pizza dilimi; 1/4'ün 1 bütünün 4 eşit parçaya bölünmesi olduğu.",
            ),
            RootNode(
                id="N_ROOT_06",
                canonical_code="math.root.equivalent_fractions",
                title="Denk Kesirler ve Sadeleştirme",
                level=-2.5,
                strict_prereqs=["N_ROOT_05"],
                description="2/4 = 1/2; pay ve paydayı aynı sayıyla çarpıp bölerek ölçekleme.",
            ),
            RootNode(
                id="N_ROOT_07",
                canonical_code="math.root.common_denominator",
                title="Ortak Payda Mantığı",
                level=-2.5,
                strict_prereqs=["N_ROOT_06"],
                description="Farklı büyüklükteki dilimler doğrudan toplanamaz: 1/2 + 1/3 için dilimleri eşitleme.",
            ),

            # SEVİYE -2: İşlem Önceliği ve Parantez Sezgisi
            RootNode(
                id="N_ROOT_08",
                canonical_code="math.root.order_of_operations",
                title="Çarpmanın Önceliği Sezgisi (PEMDAS)",
                level=-2.0,
                strict_prereqs=["N_ROOT_04"],
                description="3 + 2 · 4 = 11; çarpma işlem paketidir, önce paket hesaplanır.",
            ),
            RootNode(
                id="N_ROOT_09",
                canonical_code="math.root.parenthesis_shield",
                title="Parantezin Koruyucu Kalkanı",
                level=-2.0,
                strict_prereqs=["N_ROOT_08"],
                description="Parantez içi tek bir sayı gibi işlem görür; önce parantez içi çözülür.",
            ),
            RootNode(
                id="N_ROOT_10",
                canonical_code="math.root.distributive_gift_pack",
                title="Hediye Paketi Dağılma Özelliği",
                level=-2.0,
                strict_prereqs=["N_ROOT_09"],
                description="2(x + 4) = 2x + 8; hediye paketindeki her nesneye dıştaki çarpan uygulanır.",
            ),

            # SEVİYE -1.5: Üslü ve Köklü Sayı Tohumları
            RootNode(
                id="N_ROOT_11",
                canonical_code="math.root.exponent_counter",
                title="Üs Bir Çarpma Sayacıdır",
                level=-1.5,
                strict_prereqs=["N_ROOT_08"],
                description="2³ = 2·2·2 = 8; asla taban ile üs çarpılmaz (2·3 = 6 DEĞİLDİR).",
            ),
            RootNode(
                id="N_ROOT_12",
                canonical_code="math.root.square_root_area",
                title="Karekök Alan Sezgisi",
                level=-1.5,
                strict_prereqs=["N_ROOT_11"],
                description="√25 = 5; 'Alanı 25 olan karenin bir kenar uzunluğu kaçtır?' sezgisi.",
            ),

            # SEVİYE -1: Değişken, Eşitlik ve Terazi Sezgisi
            RootNode(
                id="N_ROOT_13",
                canonical_code="math.root.variable_mystery_box",
                title="x Bir Harf Değil 'Gizli Sayı Kutusu'dur",
                level=-1.0,
                strict_prereqs=["N_ROOT_09"],
                description="x bilinmeyen tek bir sayıdır; içine bakılmayı bekleyen bir hediye kutusudur.",
            ),
            RootNode(
                id="N_ROOT_14",
                canonical_code="math.root.implicit_multiplication",
                title="Örtük Çarpma Sezgisi",
                level=-1.0,
                strict_prereqs=["N_ROOT_13"],
                description="3x ifadesi '3 tane x' ya da 3 · x demektir, basamak değeri değildir.",
            ),
            RootNode(
                id="N_ROOT_15",
                canonical_code="math.root.balance_scale_equation",
                title="Terazi Modeli ile Denklem Çözme",
                level=-1.0,
                strict_prereqs=["N_ROOT_10", "N_ROOT_14"],
                description="Sol kefeden ne alırsan sağ kefeden de aynısını almalısın; denge bozulamaz.",
            ),
            RootNode(
                id="N_ROOT_16",
                canonical_code="math.root.function_machine",
                title="Fonksiyon Fabrikası Sezgisi",
                level=-1.0,
                strict_prereqs=["N_ROOT_14"],
                description="Girdi (x) -> Kural Fabrikası (f) -> Çıktı (y); her girdiye tek bir çıktı.",
            ),
        ]

        for n in raw_nodes:
            self.nodes[n.id] = n

    def assert_cycle_free(self) -> None:
        """Döngüsüz olduğunu DFS ile doğrular."""
        visited: Dict[str, int] = {}

        def dfs(curr_id: str):
            visited[curr_id] = 0
            curr = self.nodes[curr_id]
            for p_id in curr.strict_prereqs:
                if p_id not in self.nodes:
                    raise KeyError(f"Geçersiz önkoşul: {p_id}")
                if visited.get(p_id) == 0:
                    raise ValueError(f"Döngü tespit edildi: {curr_id} -> {p_id}")
                if p_id not in visited:
                    dfs(p_id)
            visited[curr_id] = 1

        for n_id in self.nodes:
            if n_id not in visited:
                dfs(n_id)

    def topological_sort(self) -> List[str]:
        in_degree = {n_id: len(node.strict_prereqs) for n_id, node in self.nodes.items()}
        queue = [n_id for n_id, deg in in_degree.items() if deg == 0]
        sorted_nodes = []

        children_map: Dict[str, List[str]] = {n_id: [] for n_id in self.nodes}
        for n_id, node in self.nodes.items():
            for p in node.strict_prereqs:
                children_map[p].append(n_id)

        while queue:
            queue.sort()
            curr = queue.pop(0)
            sorted_nodes.append(curr)
            for child in children_map[curr]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return sorted_nodes

    def map_bug_to_root_node(self, bug_id: str) -> Optional[str]:
        """Bozuk kuralı Seviye -3..-1 ontolojisindeki ilgili kök düğümle eşleştirir."""
        mapping = {
            "BUG-FOUND-01": "N_ROOT_04",   # -(-4) = -4
            "BUG-FOUND-02": "N_ROOT_08",   # 3 + 4*2 = 14
            "BUG-FOUND-03": "N_ROOT_11",   # -3^2 = 9
            "BUG-FOUND-04": "N_ROOT_07",   # 1/2 + 1/3 = 2/5
            "BUG-FOUND-05": "N_ROOT_10",   # 2(x+3) = 2x+3
            "BUG-FOUND-06": "N_ROOT_14",   # x + x = x^2
            "BUG-FOUND-07": "N_ROOT_14",   # 3x = 12 => x = 12 - 3
            "BUG-FOUND-08": "N_ROOT_14",   # 2x + 3 = 5x
            "BUG-FOUND-09": "N_ROOT_11",   # 2^3 = 6
            "BUG-FOUND-10": "N_ROOT_01",   # -8 > -3
            "BUG-FOUND-11": "N_ROOT_05",   # 5/0 = 0
            "BUG-FOUND-12": "N_ROOT_10",   # -(x - 4) = -x - 4
            "BUG-FOUND-13": "N_ROOT_16",   # f(x)=2x => f(3)=23
            "BUG-FOUND-14": "N_ROOT_04",   # -2x < 6 => x < -3 (yön unutma)
            "BUG-FOUND-15": "N_ROOT_15",   # tek taraflı terazi
        }
        return mapping.get(bug_id)
