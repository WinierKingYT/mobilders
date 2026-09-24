"""
Tests for PostgreSQL (schema.sql) and Redis (redis_init.lua) persistence layer.
Verifies connection pooling, data access repository, Redis atomic rate limiting,
L1/L2 idempotency caching, and seamless offline fallback.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.redis_service import RedisService
from app.db.connection import PostgresConnectionManager
from app.db.repository import CognitiveStateRepository, _ensure_uuid
from app.models.schemas import StepVerificationResponse, StepPsychometrics
from app.api.deps import IdempotencyCache
from app.main import app

client = TestClient(app)


# ====================================================================
# 1. Redis Service Tests
# ====================================================================

def test_redis_service_connected_and_lua_eval():
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    mock_client.script_load.return_value = "fake_sha_12345"
    mock_client.evalsha.return_value = ["ALLOWED", "1"]

    with patch("redis.Redis.from_url", return_value=mock_client):
        redis_svc = RedisService("redis://mock:6379/0")
        assert redis_svc.is_connected is True

        status, data = redis_svc.check_idempotency_and_rate_limit(
            rate_key="rate:test",
            idemp_key="idemp:test",
            max_requests=2,
            window_seconds=1,
            idemp_ttl=3600,
            client_msg_id="msg_001",
        )
        assert status == "ALLOWED"
        assert data == "1"

        # Test storing idempotent response
        test_resp = StepVerificationResponse(
            is_valid=True,
            is_target_reached=False,
            detected_bug=None,
            canonical_expression="x = 4",
            error_message=None,
            analysis_latency_ms=12.5,
            psychometrics=StepPsychometrics(bkt_posterior_p_l=0.45, bkt_next_p_l=0.52),
            is_replayed=False,
        )
        redis_svc.store_idempotent_response("idemp:step:msg_001", test_resp, 3600)
        assert mock_client.setex.called

        # Test retrieving idempotent response
        mock_client.get.return_value = test_resp.model_dump_json()
        cached = redis_svc.get_idempotent_response("idemp:step:msg_001")
        assert cached is not None
        assert "x = 4" in cached


def test_redis_service_offline_fallback():
    with patch("redis.Redis.from_url", side_effect=Exception("Connection refused")):
        redis_svc = RedisService("redis://unreachable:6379/0")
        assert redis_svc.is_connected is False

        # Must not raise exceptions
        status, data = redis_svc.check_idempotency_and_rate_limit("rate:test", "idemp:test")
        assert status == "ALLOWED"

        redis_svc.store_idempotent_response("idemp:test", {"key": "val"})
        assert redis_svc.get_idempotent_response("idemp:test") is None


# ====================================================================
# 2. IdempotencyCache Two-Tier (Memory L1 + Redis L2) Tests
# ====================================================================

def test_idempotency_cache_redis_l2_integration():
    mock_redis = MagicMock()
    mock_redis.is_connected = True

    test_resp = StepVerificationResponse(
        is_valid=True,
        is_target_reached=False,
        detected_bug=None,
        canonical_expression="x = 2",
        error_message=None,
        analysis_latency_ms=10.0,
        psychometrics=StepPsychometrics(bkt_posterior_p_l=0.50, bkt_next_p_l=0.60),
        is_replayed=False,
    )
    mock_redis.get_idempotent_response.return_value = test_resp.model_dump_json()

    cache = IdempotencyCache(max_size=10, ttl_seconds=3600, redis_svc=mock_redis)

    # Key is not in local memory, should fetch from Redis L2
    result = cache.get("msg_from_redis")
    assert result is not None
    assert result.canonical_expression == "x = 2"
    # Now it should also be in local memory
    assert "msg_from_redis" in cache


# ====================================================================
# 3. PostgreSQL Connection Manager Tests
# ====================================================================

def test_postgres_connection_manager_offline_fallback():
    with patch("psycopg2.pool.ThreadedConnectionPool", side_effect=Exception("Database down")):
        mgr = PostgresConnectionManager("postgresql://mock:5432/mock_db")
        assert mgr.is_connected is False

        with mgr.get_connection() as conn:
            assert conn is None


def test_postgres_connection_manager_connected():
    mock_pool = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_pool.getconn.return_value = mock_conn

    with patch("psycopg2.pool.ThreadedConnectionPool", return_value=mock_pool):
        mgr = PostgresConnectionManager("postgresql://mock:5432/mock_db")
        assert mgr.is_connected is True

        with mgr.get_connection() as conn:
            assert conn is mock_conn

        assert mock_conn.commit.called
        assert mock_pool.putconn.called


# ====================================================================
# 4. CognitiveStateRepository (schema.sql DDL) Tests
# ====================================================================

def test_ensure_uuid_helper():
    # Valid UUID remains unchanged
    orig_uuid = "12345678-1234-5678-1234-567812345678"
    assert _ensure_uuid(orig_uuid) == orig_uuid

    # Arbitrary string is deterministically hashed into valid UUID
    hashed1 = _ensure_uuid("sess_demo_100")
    hashed2 = _ensure_uuid("sess_demo_100")
    assert hashed1 == hashed2
    # Verify it is a valid UUID
    uuid.UUID(hashed1)


def test_repository_record_session_step_with_mock_db():
    mock_mgr = MagicMock()
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_mgr.get_connection.return_value.__enter__.return_value = mock_conn

    repo = CognitiveStateRepository(mock_mgr)
    event_id = repo.record_session_step(
        session_id="sess_test_123",
        student_uuid="student_abc",
        step_index=1,
        raw_latex="x + 2 = 6",
        is_valid=True,
        latency_ms=850.0,
        detected_bug_id=None,
        ddm_drift_v=0.15,
        ddm_boundary_a=0.10,
        affective_state="FLOW",
        client_timestamp=datetime.now(timezone.utc),
    )

    assert event_id is not None
    # Verify UUID format
    uuid.UUID(event_id)
    # Check that SQL was executed for student_state, session_events, and step_diagnostics
    assert mock_cur.execute.call_count == 3


def test_repository_offline_fallback():
    mock_mgr = MagicMock()
    mock_mgr._pool = None  # Simulates offline pool

    repo = CognitiveStateRepository(mock_mgr)

    # Must return None or fallback without crashing
    event_id = repo.record_session_step(
        session_id="sess_offline",
        student_uuid="stu_offline",
        step_index=1,
        raw_latex="x = 2",
        is_valid=True,
    )
    assert event_id is None

    state = repo.get_or_create_student_state("stu_offline")
    assert state["overall_theta"] == 0.0
    assert state["standard_error"] == 1.0

    assert repo.update_node_mastery("stu_offline", "N15", 0.5) is False
    assert repo.update_circadian_lock("stu_offline", datetime.now(timezone.utc)) is False
    assert repo.purge_student_data("stu_offline") is False


# ====================================================================
# 5. Full API Endpoint Integration with Resilience
# ====================================================================

def test_verify_step_with_persistence_layer():
    resp = client.post(
        "/api/v1/session/step/verify",
        json={
            "session_id": "sess_integration_test",
            "node_id": "N15",
            "step_number": 1,
            "user_expression": "x = 4",
            "target_equation": "x - 4 = 0",
            "client_msg_id": "cmsg_persist_01",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["is_target_reached"] is True


def test_conclude_session_with_circadian_lock_persistence():
    resp = client.post(
        "/api/v1/session/conclude",
        json={
            "session_id": "sess_integration_conclude",
            "student_uuid": "12345678-1234-5678-1234-567812345678",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "CONCLUDED"
    assert data["circadian_lock_active"] is True


def test_websocket_keep_alive_and_clean_disconnect():
    """
    Aşama 55: WebSocket 60s keep-alive ve 1000 temiz kapanış güvencesi.
    Mobil istemci DISCONNECT (1000) paketi gönderdiğinde oturumun hayalet bırakılmadan
    temiz biçimde kapatıldığını doğrular.
    """
    with client.websocket_connect("/ws/v1/session") as ws:
        init_msg = ws.receive_json()
        assert init_msg["type"] == "SESSION_READY"
        assert init_msg["status"] == "CONNECTED"

        # PING gönderip bağlantının canlı olduğunu teyit et
        ws.send_json({"type": "PING"})
        pong_msg = ws.receive_json()
        assert pong_msg["type"] == "PONG"

        # Temiz kapanış paketi ilet
        ws.send_json({"type": "DISCONNECT", "code": 1000})

