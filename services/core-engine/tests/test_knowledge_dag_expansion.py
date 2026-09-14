import pytest
from app.graph.knowledge_dag import KnowledgeDAG, CycleDetectedError


def test_knowledge_dag_26_nodes_expansion():
    dag = KnowledgeDAG()
    all_nodes = dag.get_all_node_ids()

    # 1. Total nodes count must be 26 (20 core + 3 inequalities + 3 parabolas)
    assert len(all_nodes) == 26

    # 2. Verify Group A (Inequalities: N21, N22, N23)
    assert "N21" in all_nodes
    assert "N22" in all_nodes
    assert "N23" in all_nodes
    assert "N10" in dag.get_node("N21").strict_prereqs
    assert "N12" in dag.get_node("N21").strict_prereqs
    assert "N21" in dag.get_node("N22").strict_prereqs
    assert "N22" in dag.get_node("N23").strict_prereqs

    # 3. Verify Group B (Parabolas: N24, N25, N26)
    assert "N24" in all_nodes
    assert "N25" in all_nodes
    assert "N26" in all_nodes
    assert "N10" in dag.get_node("N24").strict_prereqs
    assert "N18" in dag.get_node("N24").strict_prereqs
    assert "N24" in dag.get_node("N25").strict_prereqs
    assert "N24" in dag.get_node("N26").strict_prereqs


def test_topological_sort_and_cycle_free():
    dag = KnowledgeDAG()
    dag.assert_cycle_free()
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == 26

    # Verify order constraint: prerequisites must precede dependent nodes
    idx_map = {n: i for i, n in enumerate(sorted_nodes)}
    for n_id, node in dag.nodes.items():
        for p in node.strict_prereqs:
            assert idx_map[p] < idx_map[n_id], f"Prereq {p} must come before {n_id}"


def test_zpd_candidates_advanced_curriculum():
    dag = KnowledgeDAG()
    # Assume student has mastered core nodes N01 to N20
    mastered = {f"N{i:02d}" for i in range(1, 21)}
    zpd = dag.get_zpd_candidates(mastered)

    # N21 (prereqs: N10, N12) and N24 (prereqs: N10, N18) must be ZPD candidates!
    assert "N21" in zpd
    assert "N24" in zpd

    # Once N21 is mastered, N22 becomes candidate
    mastered.add("N21")
    zpd2 = dag.get_zpd_candidates(mastered)
    assert "N22" in zpd2
