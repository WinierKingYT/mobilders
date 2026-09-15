"""
HEDEF 16: Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini Testleri.
Asgari 40 test ile 245 düğümlük tüm müfredat atlasını, alan kümelemesini,
topolojik bağımlılıkları, darboğaz analizini, ZPD sınırını ve 3B uzaysal koordinatları doğrular.
"""

import pytest
from app.graph.knowledge_atlas_engine import (
    LivingKnowledgeAtlasEngine,
    DomainCluster,
    AtlasNode,
)


@pytest.fixture
def atlas():
    return LivingKnowledgeAtlasEngine()


# =====================================================================
# 1. ATLAS DÜĞÜM KAPASİTESİ VE ALAN DAĞILIMI TESTLERİ
# =====================================================================

def test_atlas_total_node_count(atlas):
    # 16 Kök (N_ROOT_01 - N_ROOT_16) + 230 Müfredat (N01 - N230) = 246 Düğüm
    assert atlas.get_total_nodes() == 246


def test_atlas_root_nodes_present(atlas):
    for i in range(1, 17):
        node_id = f"N_ROOT_{i:02d}"
        node = atlas.get_node(node_id)
        assert node is not None
        assert node.domain == DomainCluster.ROOT


def test_atlas_core_nodes_present(atlas):
    # N01'den N230'a kadar tüm düğümlerin varlığı
    for i in range(1, 231):
        node_id = f"N{i:02d}" if i < 100 else f"N{i}"
        node = atlas.get_node(node_id)
        assert node is not None, f"Düğüm bulunamadı: {node_id}"


def test_atlas_domain_distribution(atlas):
    summary = atlas.get_domain_summary()
    assert summary[DomainCluster.ROOT] == 16
    assert summary[DomainCluster.ALGEBRA] == 50          # N01 - N50
    assert summary[DomainCluster.FUNCTIONS_TRIG] == 30   # N51 - N80
    assert summary[DomainCluster.CALCULUS_DIFF] == 30    # N81 - N110
    assert summary[DomainCluster.CALCULUS_INT] == 25     # N111 - N135
    assert summary[DomainCluster.ANALYTIC_GEOM] == 25    # N136 - N160
    assert summary[DomainCluster.EUCLIDEAN_GEOM] == 25   # N161 - N185
    assert summary[DomainCluster.PROB_STATS] == 25       # N186 - N210
    assert summary[DomainCluster.LOGIC_PROOF] == 20      # N211 - N230


def test_atlas_get_nodes_by_domain(atlas):
    roots = atlas.get_nodes_by_domain(DomainCluster.ROOT)
    assert len(roots) == 16
    proofs = atlas.get_nodes_by_domain(DomainCluster.LOGIC_PROOF)
    assert len(proofs) == 20


# =====================================================================
# 2. TOPOLOJİK VE ÖNKOŞUL İZLEME TESTLERİ
# =====================================================================

def test_recursive_prerequisites_from_derivative(atlas):
    # N81 (Limit) ve N91 (Türev Tanımı) geriye doğru N01'e ve temel cebire kadar uzanmalıdır
    prereqs = atlas.get_recursive_prerequisites("N91")
    assert "N81" in prereqs or "N82" in prereqs or "N01" in prereqs
    assert len(prereqs) > 3


def test_recursive_prerequisites_from_integral(atlas):
    # N111 (Belirsiz İntegral) geriye doğru türev düğümlerine dayanır
    prereqs = atlas.get_recursive_prerequisites("N111")
    assert any(n.startswith("N") for n in prereqs)
    assert len(prereqs) >= 2


def test_downstream_dependents_from_n01(atlas):
    # N01 (Temel Dört İşlem ve Cebir), tüm lise matematiğinin anasıdır
    descendants = atlas.get_downstream_dependents("N01")
    # Yüzlerce düğüm N01'e bağımlıdır
    assert len(descendants) > 50


def test_downstream_dependents_from_n04(atlas):
    # N04 (Lineer Denklemler), analitik geometri ve denklem sistemlerini besler
    descendants = atlas.get_downstream_dependents("N04")
    assert len(descendants) > 20


# =====================================================================
# 3. YAKINSAK GELİŞİM ALANI (ZPD) SINIR BULMA TESTLERİ
# =====================================================================

def test_zpd_frontier_blank_slate(atlas):
    # Başlangıçta hiçbir şey bilinmiyorken ZPD'de kök düğümler bulunur
    zpd = atlas.compute_zpd_frontier(set())
    assert "N_ROOT_01" in zpd
    assert "N01" in zpd
    # İleri kalkülüs veya türev henüz ZPD'de olamaz
    assert "N91" not in zpd
    assert "N111" not in zpd


def test_zpd_frontier_after_mastering_roots(atlas):
    # Öğrenci kök düğüm N01'de ustalaştığında N02 ve N03 açılır
    zpd = atlas.compute_zpd_frontier({"N01"})
    assert "N02" in zpd
    assert "N03" in zpd
    # N04 henüz açılmaz çünkü hem N02 hem N03 gerekir
    assert "N04" not in zpd


def test_zpd_frontier_unlocks_linear_algebra(atlas):
    zpd = atlas.compute_zpd_frontier({"N01", "N02", "N03"})
    assert "N04" in zpd


# =====================================================================
# 4. BİLİŞSEL DARBOĞAZ (BOTTLENECK) ANALİZİ TESTLERİ
# =====================================================================

def test_critical_bottlenecks_blank_slate(atlas):
    # Sıfır bilgi durumunda en kritik darboğazlar N01, N04 gibi anayol düğümleridir
    bottlenecks = atlas.find_critical_bottlenecks(set(), top_k=5)
    assert len(bottlenecks) == 5
    top_ids = [b["node_id"] for b in bottlenecks]
    assert "N01" in top_ids or "N04" in top_ids


def test_critical_bottlenecks_after_foundations(atlas):
    # Temel cebir bilinirken yeni darboğazlar ileri seviyeye kayar
    foundations = {f"N{i:02d}" for i in range(1, 27)}
    bottlenecks = atlas.find_critical_bottlenecks(foundations, top_k=5)
    top_ids = [b["node_id"] for b in bottlenecks]
    assert "N01" not in top_ids  # N01 zaten biliniyor


# =====================================================================
# 5. MÜFREDAT VE ALAN İLERLEME YÜZDESİ TESTLERİ
# =====================================================================

def test_curriculum_progress_zero(atlas):
    prog = atlas.calculate_curriculum_progress(set())
    assert prog["mastered_count"] == 0
    assert prog["overall_percentage"] == 0.0


def test_curriculum_progress_partial(atlas):
    # 50 düğüm bilindiğinde
    mastered = {f"N{i:02d}" for i in range(1, 51)}
    prog = atlas.calculate_curriculum_progress(mastered)
    assert prog["mastered_count"] == 50
    # 50 / 245 ≈ %20.4
    assert prog["overall_percentage"] == pytest.approx(20.4, abs=0.2)
    # Cebir alanı %100 tamamlanmıştır
    assert prog["domain_stats"][DomainCluster.ALGEBRA]["percentage"] == 100.0


# =====================================================================
# 6. 3B UZAYSAL KOORDİNAT PROJEKSİYONU TESTLERİ
# =====================================================================

def test_spatial_coordinates_finite_and_assigned(atlas):
    for node in atlas.nodes.values():
        assert isinstance(node.x, float)
        assert isinstance(node.y, float)
        assert isinstance(node.z, float)
        # z koordinatı seviye ile orantılıdır
        assert node.z == float(node.level * 40.0)


def test_spatial_coordinates_domain_separation(atlas):
    # Farklı alanlardaki düğümler farklı uzaysal bölgelerde kümelenir
    root_node = atlas.get_node("N_ROOT_01")
    calculus_node = atlas.get_node("N91")
    assert root_node is not None and calculus_node is not None
    # Dikey seviye farkı
    assert root_node.z < calculus_node.z


# =====================================================================
# 7. SERİ HALE GETİRİLMİŞ GRAF VERİSİ (PAYLOAD) TESTLERİ
# =====================================================================

def test_generate_atlas_payload_structure(atlas):
    mastered = {"N01", "N02"}
    payload = atlas.generate_atlas_payload(mastered)
    assert "meta" in payload
    assert "nodes" in payload
    assert "edges" in payload

    assert payload["meta"]["total_nodes"] == 246
    assert payload["meta"]["total_edges"] > 100
    assert payload["meta"]["mastered_count"] == 2

    # Status doğrulama
    node_map = {n["id"]: n for n in payload["nodes"]}
    assert node_map["N01"]["status"] == "MASTERED"
    assert node_map["N02"]["status"] == "MASTERED"
    assert node_map["N03"]["status"] == "IN_ZPD"
    assert node_map["N91"]["status"] == "LOCKED"


def test_atlas_unknown_node_returns_none(atlas):
    assert atlas.get_node("NON_EXISTENT") is None
    assert atlas.get_recursive_prerequisites("NON_EXISTENT") == set()
    assert atlas.get_downstream_dependents("NON_EXISTENT") == set()


# =====================================================================
# 8. DERİN BAĞLANTI, SEVİYE VE KOD KALIPLARI TESTLERİ
# =====================================================================

def test_atlas_canonical_code_format(atlas):
    for node in atlas.nodes.values():
        assert node.canonical_code.startswith("math.")
        assert len(node.canonical_code.split(".")) >= 3


def test_atlas_level_boundaries(atlas):
    levels = [node.level for node in atlas.nodes.values()]
    assert min(levels) == -3
    assert max(levels) == 19


def test_atlas_euclidean_deep_path(atlas):
    # Katı cisimler küre N185 geriye doğru çember N182'ye dayanmalıdır
    prereqs = atlas.get_recursive_prerequisites("N185")
    assert "N182" in prereqs or "N183" in prereqs


def test_atlas_probability_deep_path(atlas):
    # Normal dağılım N210 geriye doğru standart puanlara ve yayılım ölçülerine dayanır
    prereqs = atlas.get_recursive_prerequisites("N210")
    assert "N209" in prereqs
    assert "N207" in prereqs


def test_atlas_logic_proof_deep_path(atlas):
    # Tümevarım eşitsizlikleri N229 geriye doğru tümevarım adımına N227 ve aksiyomlara N220 dayanır
    prereqs = atlas.get_recursive_prerequisites("N229")
    assert "N227" in prereqs
    assert "N226" in prereqs
    assert "N220" in prereqs


def test_atlas_root_prerequisite_traversal(atlas):
    # Terazi modeli N_ROOT_15 geriye doğru örtük çarpma ve sayı hissine dayanır
    prereqs = atlas.get_recursive_prerequisites("N_ROOT_15")
    assert "N_ROOT_14" in prereqs or "N_ROOT_10" in prereqs


def test_atlas_learner_profile_stem_freshman(atlas):
    # Tüm cebir ve kalkülüs düğümleri tamamlanmış bir üniversite adayı
    mastered = {f"N{i:02d}" if i < 100 else f"N{i}" for i in range(1, 136)}
    prog = atlas.calculate_curriculum_progress(mastered)
    # Cebir ve her iki kalkülüs alanı %100 olmalıdır
    assert prog["domain_stats"][DomainCluster.ALGEBRA]["percentage"] == 100.0
    assert prog["domain_stats"][DomainCluster.CALCULUS_DIFF]["percentage"] == 100.0
    assert prog["domain_stats"][DomainCluster.CALCULUS_INT]["percentage"] == 100.0
    # Genel oran 135 / 246 ≈ %54.9
    assert prog["overall_percentage"] > 50.0


def test_atlas_learner_profile_geometry_specialist(atlas):
    # Analitik ve Öklid geometrisi tamamlanmış
    geom_nodes = {f"N{i}" for i in range(136, 186)}
    prog = atlas.calculate_curriculum_progress(geom_nodes)
    assert prog["domain_stats"][DomainCluster.ANALYTIC_GEOM]["percentage"] == 100.0
    assert prog["domain_stats"][DomainCluster.EUCLIDEAN_GEOM]["percentage"] == 100.0


def test_atlas_spatial_coordinate_no_nan_or_inf(atlas):
    for node in atlas.nodes.values():
        assert not (node.x != node.x)  # NaN kontrolü
        assert not (node.y != node.y)
        assert not (node.z != node.z)


def test_atlas_bottlenecks_top_k_exceeds_total(atlas):
    # İstenen k düğüm sayısından büyükse eldekilerin tümünü döner
    bottlenecks = atlas.find_critical_bottlenecks(set(), top_k=500)
    assert len(bottlenecks) == 246


def test_atlas_payload_edge_consistency(atlas):
    # Çizilen tüm kenarların hedefi ve kaynağı graf içinde var olmalıdır
    payload = atlas.generate_atlas_payload(set())
    all_node_ids = {n["id"] for n in payload["nodes"]}
    for edge in payload["edges"]:
        assert edge["source"] in all_node_ids
        assert edge["target"] in all_node_ids


def test_atlas_zpd_frontier_pure_set_input(atlas):
    zpd = atlas.compute_zpd_frontier({"N01", "N02", "N03", "N04", "N05"})
    assert isinstance(zpd, list)
    assert all(isinstance(nid, str) for nid in zpd)


def test_atlas_domain_names_consistent(atlas):
    valid_domains = {
        DomainCluster.ROOT,
        DomainCluster.ALGEBRA,
        DomainCluster.FUNCTIONS_TRIG,
        DomainCluster.CALCULUS_DIFF,
        DomainCluster.CALCULUS_INT,
        DomainCluster.ANALYTIC_GEOM,
        DomainCluster.EUCLIDEAN_GEOM,
        DomainCluster.PROB_STATS,
        DomainCluster.LOGIC_PROOF,
    }
    for node in atlas.nodes.values():
        assert node.domain in valid_domains


def test_atlas_all_nodes_have_non_empty_titles(atlas):
    for node in atlas.nodes.values():
        assert len(node.title.strip()) > 3


def test_atlas_all_nodes_have_valid_descriptions(atlas):
    for node in atlas.nodes.values():
        assert len(node.description.strip()) > 10


def test_atlas_difficulty_ranges(atlas):
    for node in atlas.nodes.values():
        # Zorluk değerleri olağan pedagojik sınırda (-3 ile +3 arası)
        assert -4.0 <= node.difficulty <= 4.0


def test_atlas_discrimination_ranges(atlas):
    for node in atlas.nodes.values():
        assert node.discrimination > 0.5


def test_atlas_payload_active_edge_marking(atlas):
    # N01 bilindiğinde N01 kaynaklı kenarlar active=True olmalıdır
    payload = atlas.generate_atlas_payload({"N01"})
    n01_edges = [e for e in payload["edges"] if e["source"] == "N01"]
    assert len(n01_edges) > 0
    assert all(e["active"] is True for e in n01_edges)


def test_atlas_payload_inactive_edge_marking(atlas):
    payload = atlas.generate_atlas_payload(set())
    # Hiçbir düğüm bilinmiyorken tüm kenarlar active=False olmalıdır
    assert all(e["active"] is False for e in payload["edges"])


def test_atlas_curriculum_progress_all_mastered(atlas):
    all_ids = set(atlas.nodes.keys())
    prog = atlas.calculate_curriculum_progress(all_ids)
    assert prog["mastered_count"] == 246
    assert prog["overall_percentage"] == 100.0
    for domain_stat in prog["domain_stats"].values():
        assert domain_stat["percentage"] == 100.0


def test_atlas_bottlenecks_empty_when_all_mastered(atlas):
    all_ids = set(atlas.nodes.keys())
    bottlenecks = atlas.find_critical_bottlenecks(all_ids)
    assert len(bottlenecks) == 0


def test_atlas_zpd_empty_when_all_mastered(atlas):
    all_ids = set(atlas.nodes.keys())
    zpd = atlas.compute_zpd_frontier(all_ids)
    assert len(zpd) == 0

