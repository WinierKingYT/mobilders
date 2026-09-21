import time
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.api.endpoints import IdempotencyCache, _IDEMPOTENCY_CACHE
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, CASTimeoutError
from app.models.schemas import StepVerificationResponse

client = TestClient(app)


def test_idempotency_cache_max_size_eviction():
    cache = IdempotencyCache(max_size=3, ttl_seconds=3600.0)
    
    resp1 = StepVerificationResponse(is_valid=True, is_target_reached=False, analysis_latency_ms=10.0)
    resp2 = StepVerificationResponse(is_valid=True, is_target_reached=False, analysis_latency_ms=20.0)
    resp3 = StepVerificationResponse(is_valid=True, is_target_reached=False, analysis_latency_ms=30.0)
    resp4 = StepVerificationResponse(is_valid=True, is_target_reached=False, analysis_latency_ms=40.0)

    cache["msg1"] = resp1
    cache["msg2"] = resp2
    cache["msg3"] = resp3
    assert len(cache) == 3

    # Adding 4th item without touching msg1 must evict "msg1" (the least recently used)
    cache["msg4"] = resp4
    assert len(cache) == 3
    assert "msg1" not in cache
    assert "msg2" in cache
    assert "msg3" in cache
    assert "msg4" in cache


def test_idempotency_cache_lru_access_promotion():
    cache = IdempotencyCache(max_size=3, ttl_seconds=3600.0)
    resp = StepVerificationResponse(is_valid=True, is_target_reached=False, analysis_latency_ms=10.0)

    cache["msg1"] = resp
    cache["msg2"] = resp
    cache["msg3"] = resp

    # Accessing msg1 promotes it to most recently used
    _ = cache.get("msg1")

    # Adding 4th item should evict msg2 (the oldest untouched item), NOT msg1
    cache["msg4"] = resp
    assert len(cache) == 3
    assert "msg2" not in cache
    assert "msg1" in cache
    assert "msg3" in cache
    assert "msg4" in cache


def test_idempotency_cache_ttl_expiration():
    cache = IdempotencyCache(max_size=10, ttl_seconds=0.05)
    resp = StepVerificationResponse(is_valid=True, is_target_reached=False, analysis_latency_ms=10.0)

    cache["msg_temp"] = resp
    assert "msg_temp" in cache
    assert cache.get("msg_temp") is not None

    # Wait for TTL to expire
    time.sleep(0.08)
    assert cache.get("msg_temp") is None
    assert "msg_temp" not in cache


def test_api_idempotent_replay_with_cache():
    client_msg_id = f"test_idemp_{int(time.time() * 1000)}"
    payload = {
        "session_id": "sess_idemp_test",
        "node_id": "N15",
        "step_number": 1,
        "user_expression": "x + 2 = 5",
        "target_equation": "x = 3",
        "client_msg_id": client_msg_id,
    }

    # First request
    res1 = client.post("/api/v1/session/step/verify", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["is_valid"] is True
    assert data1["is_replayed"] is False

    # Second request with same client_msg_id must be served from cache as replayed
    res2 = client.post("/api/v1/session/step/verify", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["is_valid"] is True
    assert data2["is_replayed"] is True


def test_symbolic_engine_lru_cache_bounded():
    engine = SymbolicEquivalenceEngine()
    engine.MAX_CACHE_SIZE = 5  # Test with small cache size

    # Fill cache
    for i in range(7):
        is_eq, _, _ = engine.verify_equivalence(f"x + {i} = {i}", "x = 0")
        assert is_eq is True

    # Cache should never exceed MAX_CACHE_SIZE
    assert len(engine._cache) == 5
    # Earliest keys should have been evicted
    assert ("x + 0 = 0", "x = 0") not in engine._cache
    assert ("x + 1 = 1", "x = 0") not in engine._cache
    assert ("x + 6 = 6", "x = 0") in engine._cache


def test_symbolic_engine_timeout_enforcement():
    engine = SymbolicEquivalenceEngine(timeout_ms=10)

    # Mock _compute_equivalence to simulate an expensive computation exceeding timeout
    def slow_compute(user_str, target_str):
        time.sleep(0.05)
        return True, "0"

    with patch.object(engine, "_compute_equivalence", side_effect=slow_compute):
        with pytest.raises(CASTimeoutError) as exc_info:
            engine.verify_equivalence("x = 1", "x = 1", timeout_ms=10)
        assert "zaman aşımına uğradı" in str(exc_info.value)


def test_api_handles_cas_timeout():
    # Test that verify_step API endpoint handles CASTimeoutError gracefully
    with patch("app.api.endpoints.cas_engine.verify_equivalence", side_effect=CASTimeoutError("Test timeout")):
        payload = {
            "session_id": "test_timeout_sess",
            "node_id": "N15",
            "step_number": 1,
            "user_expression": "x^2 + 6x = 2",
            "target_equation": "x^2 + 6x - 2 = 0",
        }
        res = client.post("/api/v1/session/step/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["is_valid"] is False
        assert "CAS Timeout" in data["error_message"]
