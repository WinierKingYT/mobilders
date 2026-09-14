"""
Test Suite: Autonomous Curriculum Synthesizer & Formal SymPy Theorem Prover.
Verifies:
1. SymPyFormalVerifier algebraic identity proofs, limits, and solvable equations.
2. TopicBuggySynthesizer for Logarithms, Trigonometry, and Limits.
3. AutonomousCurriculumSynthesizer 30-node DAG generation, Kahn's cycle-free topological sort.
4. /api/v1/curriculum/synthesize API endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.curriculum_generator.formal_verifier import SymPyFormalVerifier
from app.curriculum_generator.buggy_synthesizer import TopicBuggySynthesizer
from app.curriculum_generator.dag_synthesizer import AutonomousCurriculumSynthesizer
from app.models.schemas import CurriculumSynthesizeRequest

client = TestClient(app)


def test_formal_verifier_identities():
    # Algebraic
    assert SymPyFormalVerifier.verify_identity("x**2 * x**3", "x**5") is True
    assert SymPyFormalVerifier.verify_identity("(x + 2)**2", "x**2 + 4*x + 4") is True
    assert SymPyFormalVerifier.verify_identity("(x + 2)**2", "x**2 + 4") is False

    # Trigonometric
    assert SymPyFormalVerifier.verify_identity("sin(x)**2 + cos(x)**2", "1") is True

    # Logarithmic
    assert SymPyFormalVerifier.verify_identity("log(x) + log(y)", "log(x*y)") is True


def test_formal_verifier_solvable_equations():
    is_solvable, roots = SymPyFormalVerifier.verify_solvable_equation("x**2 - 5*x + 6 = 0")
    assert is_solvable is True
    assert "2" in roots and "3" in roots

    # Inconsistent / unsolvable real equation check
    is_solv, _ = SymPyFormalVerifier.verify_solvable_equation("exp(x) = -5")
    assert is_solv is False


def test_formal_verifier_limits():
    # Indeterminate 0/0 limit: lim_{x -> 2} (x^2 - 4)/(x - 2) = 4
    is_valid = SymPyFormalVerifier.verify_limit_evaluation(
        expr_str="(x**2 - 4)/(x - 2)",
        var_str="x",
        point_val=2,
        expected_limit_str="4",
    )
    assert is_valid is True


def test_buggy_rule_synthesizer_topics():
    # Logarithms
    log_bugs = TopicBuggySynthesizer.get_buggy_rules_for_topic("Logarithms")
    assert len(log_bugs) >= 4
    bug_ids = [b["bug_id"] for b in log_bugs]
    assert "BUG-LOG-01" in bug_ids
    assert "BUG-LOG-02" in bug_ids

    # Trigonometry
    trig_bugs = TopicBuggySynthesizer.get_buggy_rules_for_topic("Trigonometry")
    assert len(trig_bugs) >= 4
    assert any(b["bug_id"] == "BUG-TRIG-01" for b in trig_bugs)

    # Limits
    lim_bugs = TopicBuggySynthesizer.get_buggy_rules_for_topic("Limits")
    assert len(lim_bugs) >= 3
    assert any(b["bug_id"] == "BUG-LIM-01" for b in lim_bugs)


def test_autonomous_curriculum_synthesizer_logarithms():
    synthesizer = AutonomousCurriculumSynthesizer()
    req = CurriculumSynthesizeRequest(topic="Logarithms", target_grade="11", language="tr")
    response = synthesizer.synthesize(req)

    assert response.topic == "Logarithms"
    assert response.total_nodes == 30
    assert response.is_cycle_free is True
    assert len(response.topological_order) == 30
    assert response.formal_verification_passed is True
    assert len(response.buggy_rules) >= 4

    # Verify node structure and levels
    levels = {n.level for n in response.nodes}
    assert 0 in levels and 5 in levels
    # Kahn's topological sort verification: every parent must appear BEFORE child
    node_index = {n_id: idx for idx, n_id in enumerate(response.topological_order)}
    for node in response.nodes:
        for parent_id in node.strict_prereqs:
            assert node_index[parent_id] < node_index[node.id]


def test_curriculum_synthesize_api_endpoint():
    payload = {
        "topic": "Trigonometry",
        "target_grade": "Grade 11-12",
        "language": "tr",
    }
    res = client.post("/api/v1/curriculum/synthesize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_nodes"] == 30
    assert data["is_cycle_free"] is True
    assert data["formal_verification_passed"] is True
    assert len(data["nodes"]) == 30
