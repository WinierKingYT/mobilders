import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.analytics.local_reporter import LocalAnalyticsReporter
from app.graph.knowledge_dag import KnowledgeDAG
from app.retention.fsrs import FSRSEngine


@pytest.fixture
def client():
    return TestClient(app)


def test_local_analytics_reporter():
    dag = KnowledgeDAG()
    fsrs = FSRSEngine()
    reporter = LocalAnalyticsReporter(dag=dag, fsrs=fsrs)

    report = reporter.generate_student_report("EXP-STU-99")
    assert report["student_id"] == "EXP-STU-99"

    # 1. Metacognitive checks
    meta = report["metacognitive"]
    assert "ece" in meta
    assert "brier_score" in meta
    assert "overconfidence_rate" in meta
    assert "imposter_rate" in meta

    # 2. Cognitive efficiency checks
    eff = report["cognitive_efficiency"]
    assert "paas_e_index" in eff
    assert "interpretation" in eff

    # 3. Memory retention projection
    ret = report["memory_retention_14d"]
    assert len(ret["projection"]) == 14
    assert ret["projection"][0]["day"] == 1
    assert ret["projection"][-1]["day"] == 14
    assert ret["projection"][0]["retention_probability"] >= ret["projection"][-1]["retention_probability"]

    # 4. Algebra Atlas
    atlas = report["algebra_atlas"]
    assert atlas["total_nodes"] == 80
    assert len(atlas["nodes"]) == 80


def test_analytics_api_endpoint(client):
    response = client.get("/api/v1/analytics/student/EXP-STU-01")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "EXP-STU-01"
    assert "metacognitive" in data
    assert "cognitive_efficiency" in data
    assert "memory_retention_14d" in data
    assert "algebra_atlas" in data
    assert data["algebra_atlas"]["total_nodes"] == 80
