import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import create_focus_router, install_focus_api, is_canary_admitted
from app.focus_domain.application import FocusAttemptInputKind, FocusServiceFacade
from app.focus_domain.metrics import get_focus_metrics


def test_canary_admitted_hashing():
    # 0% percentage admits nothing
    assert is_canary_admitted("user-1", 0) is False
    assert is_canary_admitted("user-2", 0) is False

    # 100% percentage admits everything
    assert is_canary_admitted("user-1", 100) is True
    assert is_canary_admitted("user-2", 100) is True

    # 50% percentage divides deterministically
    admitted = sum(1 for i in range(200) if is_canary_admitted(f"user-test-{i}", 50))
    assert 80 <= admitted <= 120  # Roughly 50% of 200 is 100


def test_kill_switch_immediately_blocks_all_routes():
    app = FastAPI()
    router = create_focus_router(enabled=True, canary_percentage=100, kill_switch=True)
    app.include_router(router)
    client = TestClient(app)

    res = client.post(
        "/focus/v1/episodes",
        json={"episode_id": "ep-kill", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-kill"},
    )
    assert res.status_code == 503
    data = res.json()
    assert data["detail"]["code"] == "FOCUS_KILL_SWITCH_ACTIVE"

    metrics = get_focus_metrics()
    summary = metrics.get_summary()
    assert any(e["event_type"] == "KILL_SWITCH_ACTIVE" for e in summary["recent_audit_events"])


def test_canary_cohort_routing_and_exclusion():
    app = FastAPI()
    # Find one key that is admitted at 20% and one that is excluded
    admitted_key = None
    excluded_key = None
    for i in range(100):
        k = f"token-canary-{i}"
        if is_canary_admitted(k, 20) and admitted_key is None:
            admitted_key = k
        elif not is_canary_admitted(k, 20) and excluded_key is None:
            excluded_key = k
        if admitted_key and excluded_key:
            break

    router = create_focus_router(enabled=False, canary_percentage=20, kill_switch=False)
    app.include_router(router)
    client = TestClient(app)

    # Excluded caller receives 503 FOCUS_CANARY_EXCLUDED
    res_ex = client.post(
        "/focus/v1/episodes",
        json={"episode_id": "ep-canary-1", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-ex", "Authorization": excluded_key},
    )
    assert res_ex.status_code == 503
    assert res_ex.json()["detail"]["code"] == "FOCUS_CANARY_EXCLUDED"

    # Admitted caller succeeds
    res_ad = client.post(
        "/focus/v1/episodes",
        json={"episode_id": "ep-canary-2", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-ad", "Authorization": admitted_key},
    )
    assert res_ad.status_code == 201
    assert res_ad.json()["episode_id"] == "ep-canary-2"


def test_install_focus_api_when_disabled_mounts_no_routes():
    app = FastAPI()
    install_focus_api(app, enabled=False, canary_percentage=0)
    client = TestClient(app)

    res = client.post(
        "/focus/v1/episodes",
        json={"episode_id": "ep-none", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-none"},
    )
    assert res.status_code == 404


def test_metrics_collection_and_telemetry_endpoint():
    metrics = get_focus_metrics()
    metrics.reset()

    app = FastAPI()
    router = create_focus_router(enabled=True, canary_percentage=100)
    app.include_router(router)
    client = TestClient(app)

    # 1. Start episode
    r1 = client.post(
        "/focus/v1/episodes",
        json={"episode_id": "ep-metric", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-metric-start"},
    )
    assert r1.status_code == 201

    # 2. Submit attempt
    r2 = client.post(
        "/focus/v1/episodes/ep-metric/attempts",
        json={"input_kind": "FACTOR_PAIR", "input": [2, 3]},
        headers={"Idempotency-Key": "k-metric-att", "X-Focus-Expected-Sequence": "1"},
    )
    assert r2.status_code == 200

    # 3. Retrieve telemetry via GET /focus/v1/metrics
    r_metrics = client.get("/focus/v1/metrics")
    assert r_metrics.status_code == 200
    m_data = r_metrics.json()

    assert "start_episode:SUCCESS" in m_data["commands"]
    assert "submit_attempt:SUCCESS" in m_data["commands"]
    assert "VALID_EXPECTED" in m_data["judgments"]
    assert "ADVANCE" in m_data["decisions"]
    assert m_data["average_latency_ms"]["start_episode"] >= 0.0
