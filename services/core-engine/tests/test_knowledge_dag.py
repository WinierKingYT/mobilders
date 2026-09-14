import pytest
from app.graph.knowledge_dag import KnowledgeDAG, CycleDetectedError, KnowledgeNode


@pytest.fixture
def dag():
    return KnowledgeDAG()


def test_dag_initialization_20_nodes(dag):
    assert len(dag.nodes) == 26
    assert "N01" in dag.nodes
    assert "N15" in dag.nodes
    assert "N20" in dag.nodes
    assert "N21" in dag.nodes
    assert "N26" in dag.nodes


def test_dag_is_cycle_free(dag):
    # İnşa anında assert_cycle_free çalışır, hata fırlatmamalıdır
    dag.assert_cycle_free()


def test_dag_topological_sort_validity(dag):
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == 26

    # Her düğümün katı önkoşulu listede kendisinden önce gelmelidir
    index_map = {n_id: idx for idx, n_id in enumerate(sorted_nodes)}

    for n_id, node in dag.nodes.items():
        for parent_id in node.strict_prereqs:
            assert index_map[parent_id] < index_map[n_id], (
                f"Önkoşul ihlali: {parent_id} ({index_map[parent_id]}), "
                f"{n_id} ({index_map[n_id]}) düğümünden önce gelmeliydi!"
            )


def test_dag_recursive_prerequisites(dag):
    # N15 (Tam Kare) için derin önkoşullar: N14, N07, N13, N10, N04, N02, N03, N01
    prereqs = dag.get_prerequisites("N15", recursive=True)
    assert "N01" in prereqs
    assert "N02" in prereqs
    assert "N14" in prereqs
    assert "N13" in prereqs
    assert "N15" not in prereqs


def test_dag_zpd_candidates_progression(dag):
    # 1. Başlangıçta hiçbir şey bilinmiyorken tek ZPD düğümü kök N01'dir
    zpd_0 = dag.get_zpd_candidates(set())
    assert zpd_0 == ["N01"]

    # 2. N01 bilindiğinde N02 ve N03 ZPD adayı olur
    zpd_1 = dag.get_zpd_candidates({"N01"})
    assert set(zpd_1) == {"N02", "N03"}

    # 3. N01, N02, N03 bilindiğinde N04, N05 ve N07 açılır
    zpd_2 = dag.get_zpd_candidates({"N01", "N02", "N03"})
    assert "N04" in zpd_2
    assert "N05" in zpd_2
    assert "N07" in zpd_2


def test_dag_cycle_detection_on_invalid_graph():
    bad_dag = KnowledgeDAG()
    # Yapay döngü ekle: N01 -> N02 -> N04 -> N01
    bad_dag.nodes["N01"].strict_prereqs.append("N04")
    with pytest.raises(CycleDetectedError):
        bad_dag.assert_cycle_free()
