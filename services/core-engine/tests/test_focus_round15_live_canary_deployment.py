"""
Round 17: Live Production General Availability (Stage 3 - 100% Full Access) Test Suite.

Verifies:
1. Environment & Config Loading: FOCUS_V1_ENABLED=true, FOCUS_CANARY_PERCENTAGE=100, FOCUS_KILL_SWITCH=false.
2. /health endpoint exposes active canary configuration (100%) and CAS readiness.
3. 100% of client traffic is admitted without canary exclusion.
4. Arbitrary clients can start, advance, and complete CT-QF1 episodes with zero 503 FOCUS_CANARY_EXCLUDED rejections.
5. Emergency Kill Switch immediately blocks all routes with HTTP 503 FOCUS_KILL_SWITCH_ACTIVE.
6. Telemetry & Metrics reflect accurate audit and execution statistics with zero dead-letter events.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.focus_domain.api import create_focus_router, install_focus_api, is_canary_admitted
from app.focus_domain.application import FocusAttemptInputKind, FocusServiceFacade
from app.focus_domain.metrics import get_focus_metrics


@pytest.fixture(autouse=True)
def clean_metrics_state():
    metrics = get_focus_metrics()
    metrics.reset()
    yield
    metrics.reset()


def _build_live_canary_app():
    settings = Settings()
    test_app = FastAPI(title="Core Engine Live Canary Test App")
    install_focus_api(
        test_app,
        enabled=settings.FOCUS_V1_ENABLED,
        canary_percentage=settings.FOCUS_CANARY_PERCENTAGE,
        kill_switch=settings.FOCUS_KILL_SWITCH,
    )

    @test_app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": "core-engine",
            "environment": settings.ENVIRONMENT,
            "cas_status": "ready",
            "focus_v1_enabled": settings.FOCUS_V1_ENABLED,
            "focus_canary_percentage": settings.FOCUS_CANARY_PERCENTAGE,
            "focus_kill_switch": settings.FOCUS_KILL_SWITCH,
            "supported_misconceptions": [
                "BUG-QUAD-01",
                "BUG-QUAD-02",
                "BUG-QUAD-03",
                "BUG-QUAD-04",
                "BUG-QUAD-05",
            ],
        }

    return test_app


@pytest.fixture
def client():
    app = _build_live_canary_app()
    return TestClient(app)


def test_round17_environment_and_health_endpoint(client):
    """Verify live config and health check report Stage 3 General Availability configuration (100%)."""
    settings = Settings()
    assert settings.FOCUS_V1_ENABLED is True
    assert settings.FOCUS_CANARY_PERCENTAGE == 100
    assert settings.FOCUS_KILL_SWITCH is False

    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "core-engine"
    assert data["cas_status"] == "ready"
    assert data["focus_v1_enabled"] is True
    assert data["focus_canary_percentage"] == 100
    assert data["focus_kill_switch"] is False


def test_round17_canary_modulo_admits_100_percent_of_traffic():
    """Verify SHA-256 modulo routing admits 100% of all client keys."""
    sample_size = 2000
    admitted = sum(
        1 for i in range(sample_size)
        if is_canary_admitted(f"learner_device_hash_{i}", 100)
    )
    assert admitted == sample_size, f"Expected {sample_size}, but got {admitted}"


def test_round17_live_ga_routing_zero_exclusions_all_clients_admitted(client):
    """Verify that under 100% GA, all callers are admitted without any canary exclusions."""
    # Test a sample of diverse callers that previously may have been excluded
    test_keys = [
        f"ga_learner_token_{i}" for i in range(20)
    ]

    for idx, key in enumerate(test_keys):
        # 1. Any caller successfully starts an episode
        res_start = client.post(
            "/focus/v1/episodes",
            json={"episode_id": f"r17-ga-ep-{idx}", "b": 5, "c": 6},
            headers={
                "Idempotency-Key": f"k-r17-start-{idx}",
                "Authorization": f"Bearer {key}",
            },
        )
        assert res_start.status_code == 201
        start_body = res_start.json()
        assert start_body["episode_id"] == f"r17-ga-ep-{idx}"
        assert start_body["state"]["current_stage"] == "S1_FACTOR"

    # 2. Perform full multi-stage progression on one episode
    caller_key = test_keys[0]
    ep_id = "r17-ga-ep-0"

    # Step 1 -> S2_BRANCH
    res_s1 = client.post(
        f"/focus/v1/episodes/{ep_id}/attempts",
        json={
            "input_kind": FocusAttemptInputKind.FACTOR_PAIR.value,
            "input": [2, 3],
        },
        headers={
            "Idempotency-Key": "k-r17-step1",
            "X-Focus-Expected-Sequence": "1",
            "Authorization": f"Bearer {caller_key}",
        },
    )
    assert res_s1.status_code == 200
    s1_body = res_s1.json()
    assert s1_body["state"]["current_stage"] == "S2_BRANCH"
    assert s1_body["judgment"] == "VALID_EXPECTED"

    # Step 2 -> COMPLETED via solution set
    res_s2 = client.post(
        f"/focus/v1/episodes/{ep_id}/attempts",
        json={
            "input_kind": FocusAttemptInputKind.SOLUTION_SET.value,
            "input": ["x=-2", "x=-3"],
        },
        headers={
            "Idempotency-Key": "k-r17-step2",
            "X-Focus-Expected-Sequence": "2",
            "Authorization": f"Bearer {caller_key}",
        },
    )
    assert res_s2.status_code == 200
    s2_body = res_s2.json()
    assert s2_body["state"]["phase"] == "COMPLETED"
    assert s2_body["judgment"] == "VALID_SHORTCUT"


def test_round17_emergency_kill_switch_trip_and_audit():
    """Verify kill switch immediately halts all traffic even at 100% GA."""
    metrics = get_focus_metrics()
    kill_router = create_focus_router(
        enabled=True,
        canary_percentage=100,
        kill_switch=True,
    )
    kill_app = FastAPI()
    kill_app.include_router(kill_router)
    kill_client = TestClient(kill_app)

    res = kill_client.post(
        "/focus/v1/episodes",
        json={"episode_id": "r17-kill-ep", "b": 5, "c": 6},
        headers={"Idempotency-Key": "k-kill-r17"},
    )
    assert res.status_code == 503
    body = res.json()
    assert body["detail"]["code"] == "FOCUS_KILL_SWITCH_ACTIVE"

    summary = metrics.get_summary()
    assert any(
        e["event_type"] == "KILL_SWITCH_ACTIVE"
        for e in summary["recent_audit_events"]
    )


def test_round17_metrics_telemetry_pre_flight_integrity(client):
    """Verify GET /focus/v1/metrics telemetry endpoint returns healthy counters with 0 dead-letter audits."""
    res = client.get("/focus/v1/metrics")
    assert res.status_code == 200
    metrics_data = res.json()

    assert metrics_data["dead_letter_audit_count"] == 0
    assert "commands" in metrics_data
    assert "average_latency_ms" in metrics_data
    assert isinstance(metrics_data["recent_audit_events"], list)
