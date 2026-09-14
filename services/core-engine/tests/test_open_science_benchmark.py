"""
Test Suite: Open Academic Science Benchmark & Differential Privacy Exporter.
Verifies:
1. DifferentialPrivacyExporter with bounded Laplace noise mechanism.
2. Zero-PII sanitization and pseudorandom anonymization.
3. CognitiveModelBenchmark standardized model ranking (iBKT, FSRS, DDM, 2PL-IRT, BKT).
4. /api/v1/research/export/dp-dataset & /api/v1/research/leaderboard API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.research.dp_exporter import DifferentialPrivacyExporter
from app.research.leaderboard import CognitiveModelBenchmark
from app.models.schemas import DPExportRequest

client = TestClient(app)


def test_dp_exporter_laplace_scaling():
    req_eps_1 = DPExportRequest(epsilon=1.0, delta=1e-5, max_records=50)
    res_1 = DifferentialPrivacyExporter.export_dataset(req_eps_1)

    req_eps_05 = DPExportRequest(epsilon=0.5, delta=1e-5, max_records=50)
    res_05 = DifferentialPrivacyExporter.export_dataset(req_eps_05)

    assert res_1.records_exported == 50
    assert res_05.records_exported == 50
    assert res_1.zero_pii_verified is True
    assert res_05.zero_pii_verified is True

    # Check Laplace noise scale applied: b = Delta f / eps
    # For RT sensitivity = 0.5:
    # eps=1.0 -> b=0.5; eps=0.5 -> b=1.0
    scale_1 = res_1.dataset[0]["dp_noise_scale_applied"]
    scale_05 = res_05.dataset[0]["dp_noise_scale_applied"]
    assert pytest.approx(scale_1, rel=1e-2) == 0.50
    assert pytest.approx(scale_05, rel=1e-2) == 1.0


def test_dp_exporter_zero_pii_and_bounds():
    req = DPExportRequest(epsilon=1.5, max_records=25)
    res = DifferentialPrivacyExporter.export_dataset(req)

    assert len(res.dataset) == 25
    for record in res.dataset:
        assert record["participant_pseudonym"].startswith("anon_res_")
        assert len(record["participant_pseudonym"]) > 10
        # Check bounded reaction time
        assert record["reaction_time_seconds"] >= 0.2
        # Check bounded confidence
        assert 0.0 <= record["confidence_reported"] <= 1.0
        # Check node format
        assert record["node_id"].startswith("N")


def test_cognitive_model_leaderboard():
    leaderboard_res = CognitiveModelBenchmark.get_leaderboard("Test-Dataset-2026")
    assert leaderboard_res.total_models == 5
    assert leaderboard_res.benchmark_dataset == "Test-Dataset-2026"

    models = leaderboard_res.leaderboard
    # Rank 1 must be iBKT
    assert models[0].rank == 1
    assert "iBKT" in models[0].model_name
    assert models[0].auc_roc > 0.88

    # Rank 2 must be FSRS
    assert models[1].rank == 2
    assert "FSRS" in models[1].model_name

    # Baseline BKT should be lowest rank
    assert models[-1].rank == 5
    assert "Baseline" in models[-1].category or "Standard BKT" in models[-1].model_name


def test_research_api_endpoints():
    # Test DP export endpoint
    dp_payload = {
        "epsilon": 0.8,
        "delta": 1e-5,
        "max_records": 30,
    }
    dp_res = client.post("/api/v1/research/export/dp-dataset", json=dp_payload)
    assert dp_res.status_code == 200
    dp_data = dp_res.json()
    assert dp_data["records_exported"] == 30
    assert dp_data["zero_pii_verified"] is True
    assert len(dp_data["dataset"]) == 30

    # Test Leaderboard endpoint
    lb_res = client.get("/api/v1/research/leaderboard")
    assert lb_res.status_code == 200
    lb_data = lb_res.json()
    assert lb_data["total_models"] == 5
    assert lb_data["leaderboard"][0]["rank"] == 1
