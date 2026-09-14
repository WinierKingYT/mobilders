import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "core-engine"
    assert data["cas_status"] == "ready"
    assert "BUG-QUAD-01" in data["supported_misconceptions"]


def test_api_verify_step_valid():
    payload = {
        "session_id": "test-session-001",
        "node_id": "N07",
        "step_number": 1,
        "user_expression": "x**2 + 6*x = 2",
        "target_equation": "x**2 + 6*x - 2 = 0",
    }
    response = client.post("/api/v1/session/step/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["analysis_latency_ms"] < 120.0
    assert data["error_message"] is None
    assert data["detected_bug"] is None


def test_api_verify_step_invalid_no_bug():
    payload = {
        "session_id": "test-session-002",
        "node_id": "N07",
        "step_number": 1,
        "user_expression": "x**2 + 6*x = 9",
        "target_equation": "x**2 + 6*x - 2 = 0",
    }
    response = client.post("/api/v1/session/step/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["detected_bug"] is None


def test_api_verify_step_security_violation():
    payload = {
        "session_id": "test-session-003",
        "node_id": "N07",
        "step_number": 1,
        "user_expression": "__import__('os').system('dir')",
        "target_equation": "x = 0",
    }
    response = client.post("/api/v1/session/step/verify", json=payload)
    assert response.status_code == 400
    assert "Güvenlik İhlali" in response.json()["detail"]


def test_api_diagnose_misconception_bug_01():
    payload = {
        "session_id": "test-session-004",
        "node_id": "N08",
        "step_number": 2,
        "previous_step": "x*(x + 6) = 2",
        "user_expression": "x = 2",
        "target_equation": "x**2 + 6*x - 2 = 0",
    }

    response = client.post("/api/v1/session/step/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["detected_bug"] is not None
    assert data["detected_bug"]["bug_id"] == "BUG-QUAD-01"
    assert data["detected_bug"]["severity"] == "CRITICAL"
    assert "A*B=0" in data["detected_bug"]["description"]


def test_api_diagnose_misconception_bug_02():
    payload = {
        "session_id": "test-session-005",
        "node_id": "N05",
        "step_number": 2,
        "previous_step": "x**2 = 16",
        "user_expression": "x = 4",
        "target_equation": "x**2 - 16 = 0",
    }
    response = client.post("/api/v1/session/step/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["detected_bug"] is not None
    assert data["detected_bug"]["bug_id"] == "BUG-QUAD-02"
    assert data["detected_bug"]["severity"] == "CRITICAL"


def test_api_cat_next_item():
    payload = {
        "session_id": "cat-session-001",
        "current_theta": 0.0,
        "administered_item_ids": [],
    }
    response = client.post("/api/v1/diagnostic/next-item", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == "CAT-ITEM-01"
    assert data["target_node_id"] == "N12"


def test_api_cat_submit_progression_and_completion():
    # 1. Adım: İlk soruyu doğru yanıtla
    payload1 = {
        "session_id": "cat-session-002",
        "item_id": "CAT-ITEM-01",
        "is_correct": True,
        "administered_history": [],
    }
    response1 = client.post("/api/v1/diagnostic/submit", json=payload1)
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["theta_hat"] > 0.0
    assert data1["is_complete"] is False
    assert data1["next_item"] is not None

    # 2. Adım: 8 soru tamamlayıp testi bitir
    history = [
        ("CAT-ITEM-01", True),
        ("CAT-ITEM-02", True),
        ("CAT-ITEM-08", True),
        ("CAT-ITEM-07", True),
        ("CAT-ITEM-06", True),
        ("CAT-ITEM-05", True),
        ("CAT-ITEM-03", True),
    ]
    payload_final = {
        "session_id": "cat-session-002",
        "item_id": "CAT-ITEM-04",
        "is_correct": True,
        "administered_history": history,
    }
    response_final = client.post("/api/v1/diagnostic/submit", json=payload_final)
    assert response_final.status_code == 200
    data_final = response_final.json()
    assert data_final["is_complete"] is True
    assert data_final["next_item"] is None
    assert data_final["seeded_mastery"] is not None
    assert len(data_final["seeded_mastery"]) == 80
    assert data_final["zpd_candidates"] is not None


def test_api_socratic_respond():
    payload = {
        "user_input": "x(x+6) = 2 ise x = 2",
        "target_equation": "x**2 + 6*x - 2 = 0",
        "previous_step": "x*(x+6) = 2",
        "solution_roots": [-6.32, 0.32],
        "affective_state": "FLOW",
        "scaffolding_level": 2,
    }
    response = client.post("/api/v1/socratic/respond", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["final_output"] is not None
    assert data["socratic_ratio"] >= 1.0
    assert "?" in data["final_output"]


def test_websocket_session_lifecycle():
    with client.websocket_connect("/ws/v1/session") as ws:
        init_msg = ws.receive_json()
        assert init_msg["type"] == "SESSION_READY"
        assert init_msg["status"] == "CONNECTED"

        # 1. Send valid step
        ws.send_json({
            "type": "STEP_SUBMIT",
            "client_msg_id": "cmsg_001",
            "payload": {
                "raw_latex": "x**2 + 6*x = 2",
                "previous_canonical": "x**2 + 6*x - 2 = 0",
                "target_equation": "x**2 + 6*x - 2 = 0",
                "latency_ms": 3000,
            }
        })
        val_msg = ws.receive_json()
        assert val_msg["type"] == "STEP_VALIDATED"
        assert val_msg["payload"]["is_correct"] is True

        # 2. Send confidence
        ws.send_json({
            "type": "CONFIDENCE_SUBMIT",
            "client_msg_id": "cmsg_002",
            "payload": {"confidence_level": 0.90}
        })
        conf_msg = ws.receive_json()
        assert conf_msg["type"] == "CONFIDENCE_ACK"
        assert conf_msg["payload"]["status"] == "RECORDED"

        # 3. Ping / Pong
        ws.send_json({"type": "PING"})
        pong_msg = ws.receive_json()
        assert pong_msg["type"] == "PONG"


def test_protocol_22_rest_aliases():
    # 1. /api/v1/cat/start
    r1 = client.post("/api/v1/cat/start", json={"session_id": "test_cat_001"})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["cat_session_id"] == "test_cat_001"
    assert d1["first_item"] is not None

    # 2. /api/v1/cat/submit-item
    r2 = client.post("/api/v1/cat/submit-item", json={
        "session_id": "test_cat_001",
        "item_id": "CAT-ITEM-01",
        "is_correct": True,
        "administered_history": [],
    })
    assert r2.status_code == 200
    assert r2.json()["theta_hat"] > 0.0

    # 3. /api/v1/cat/result/{cat_session_id}
    r3 = client.get("/api/v1/cat/result/test_cat_001?theta=1.2")
    assert r3.status_code == 200
    d3 = r3.json()
    assert len(d3["atlas_mastery"]) == 80
    assert "N15" in d3["atlas_mastery"]

    # 4. /api/v1/session/start-daily
    r4 = client.post("/api/v1/session/start-daily")
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["duration_limit_minutes"] == 20
    assert d4["circadian_lock_hours"] == 14

    # 5. /api/v1/atlas/state
    r5 = client.get("/api/v1/atlas/state")
    assert r5.status_code == 200
    d5 = r5.json()
    assert d5["total_nodes"] == 80

    # 6. /api/v1/session/conclude
    r6 = client.post("/api/v1/session/conclude")
    assert r6.status_code == 200
    d6 = r6.json()
    assert d6["status"] == "CONCLUDED"
    assert d6["circadian_lock_active"] is True
    assert d6["lock_duration_seconds"] == 14 * 3600



