"""
Test Suite: Offline State Replay & Idempotent Event Queue Synchronization.
Verifies:
1. client_msg_id idempotency cache prevents duplicate BKT state updates.
2. Chronological event replay over POST /api/v1/session/replay-queue.
3. Batch processing of offline steps preserving BKT mastery progression and Buggy Rule detection.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_idempotent_step_verification():
    msg_id = "test-msg-uuid-999"
    payload = {
        "session_id": "session-idemp-01",
        "node_id": "N15",
        "step_number": 1,
        "user_expression": "(x - 2)(x - 3) = 0",
        "target_equation": "x^2 - 5*x + 6 = 0",
        "current_p_l": 0.20,
        "client_msg_id": msg_id,
        "client_timestamp": "2026-09-14T20:30:00Z",
    }

    # First attempt: Fresh computation
    res1 = client.post("/api/v1/session/step/verify", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["is_valid"] is True
    assert data1["is_replayed"] is False

    # Second attempt with IDENTICAL client_msg_id: Must return from idempotency cache
    res2 = client.post("/api/v1/session/step/verify", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["is_valid"] is True
    assert data2["is_replayed"] is True
    assert data2["canonical_expression"] == data1["canonical_expression"]


def test_offline_batch_replay_queue():
    session_id = "session-offline-replay-02"
    events = [
        {
            "session_id": session_id,
            "node_id": "N15",
            "step_number": 1,
            "user_expression": "(x - 2)(x - 3) = 0",
            "target_equation": "x^2 - 5*x + 6 = 0",
            "client_msg_id": "offline-step-101",
            "client_timestamp": "2026-09-14T20:31:00Z",
            "elapsed_ms": 1200,
        },
        {
            "session_id": session_id,
            "node_id": "N15",
            "step_number": 2,
            "user_expression": "x = 2",
            "target_equation": "x^2 + 6*x - 2 = 0",
            "previous_step": "x*(x + 6) = 2",
            "client_msg_id": "offline-step-102",
            "client_timestamp": "2026-09-14T20:31:30Z",
            "elapsed_ms": 2500,
        },
        {
            "session_id": session_id,
            "node_id": "N15",
            "step_number": 3,
            "user_expression": "x**2 - 5*x = -6",
            "target_equation": "x^2 - 5*x + 6 = 0",
            "client_msg_id": "offline-step-103",
            "client_timestamp": "2026-09-14T20:32:00Z",
            "elapsed_ms": 800,
        },
    ]

    replay_payload = {
        "session_id": session_id,
        "events": events,
    }

    res = client.post("/api/v1/session/replay-queue", json=replay_payload)
    assert res.status_code == 200
    data = res.json()

    assert data["session_id"] == session_id
    assert data["synced_count"] == 3
    assert len(data["replayed_steps"]) == 3

    # Step 1 was valid
    assert data["replayed_steps"][0]["is_valid"] is True
    # Step 2 had BUG-QUAD-01
    assert data["replayed_steps"][1]["is_valid"] is False
    assert data["replayed_steps"][1]["detected_bug"] is not None
    assert data["replayed_steps"][1]["detected_bug"]["bug_id"] == "BUG-QUAD-01"
    # Step 3 reached target equation
    assert data["replayed_steps"][2]["is_valid"] is True
    assert data["is_target_reached"] is True
    assert data["latest_p_l"] > 0.20
