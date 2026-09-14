import pytest
from app.graph.knowledge_dag import KnowledgeDAG, CycleDetectedError


def test_knowledge_dag_50_nodes_expansion():
    dag = KnowledgeDAG()
    all_nodes = dag.get_all_node_ids()

    # 1. Total nodes count must be 110 (Phase II Calculus)
    assert len(all_nodes) == 110

    # 2. Verify Group A (Inequalities: N21, N22, N23)
    assert "N21" in all_nodes
    assert "N22" in all_nodes
    assert "N23" in all_nodes
    assert "N10" in dag.get_node("N21").strict_prereqs
    assert "N12" in dag.get_node("N21").strict_prereqs
    assert "N21" in dag.get_node("N22").strict_prereqs
    assert "N22" in dag.get_node("N23").strict_prereqs

    # 3. Verify Group B (Parabolas: N24 - N38)
    for n in range(24, 39):
        assert f"N{n:02d}" in all_nodes
    assert "N24" in dag.get_node("N27").strict_prereqs
    assert "N24" in dag.get_node("N28").strict_prereqs
    assert "N20" in dag.get_node("N33").strict_prereqs
    assert "N33" in dag.get_node("N34").strict_prereqs

    # 4. Verify Group C (Polynomials: N39 - N50)
    for n in range(39, 51):
        assert f"N{n:02d}" in all_nodes
    assert "N03" in dag.get_node("N39").strict_prereqs
    assert "N39" in dag.get_node("N40").strict_prereqs
    assert "N40" in dag.get_node("N41").strict_prereqs
    assert "N41" in dag.get_node("N42").strict_prereqs
    assert "N42" in dag.get_node("N47").strict_prereqs

    # 5. Verify Group D (Trigonometry: N51 - N65)
    for n in range(51, 66):
        assert f"N{n:02d}" in all_nodes
    assert "N51" in dag.get_node("N52").strict_prereqs
    assert "N52" in dag.get_node("N53").strict_prereqs
    assert "N55" in dag.get_node("N60").strict_prereqs
    assert "N60" in dag.get_node("N62").strict_prereqs

    # 6. Verify Group E (Exponential and Logarithmic Functions: N66 - N80)
    for n in range(66, 81):
        assert f"N{n:02d}" in all_nodes
    assert "N66" in dag.get_node("N69").strict_prereqs
    assert "N69" in dag.get_node("N72").strict_prereqs
    assert "N72" in dag.get_node("N73").strict_prereqs
    assert "N71" in dag.get_node("N78").strict_prereqs

    # 7. Verify Group F (Calculus I: Limit, Süreklilik ve Türev: N81 - N110)
    for n in range(81, 111):
        assert f"N{n:02d}" if n < 100 else f"N{n}" in all_nodes


def test_topological_sort_and_cycle_free():
    dag = KnowledgeDAG()
    dag.assert_cycle_free()
    sorted_nodes = dag.topological_sort()
    assert len(sorted_nodes) == len(dag.nodes)

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
