import concurrent.futures
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.focus_domain.api import create_focus_router, install_focus_api
from app.focus_domain.application import (
    FocusAttemptInputKind,
    FocusServiceFacade,
)
from app.focus_domain.models import AttemptJudgment, KCId, KCState
from app.focus_domain.persistence import (
    EventJournalConflict,
    FocusEpisodePersistenceService,
)
from app.focus_domain.sql_persistence import (
    SQLiteFocusJournal,
    SQLiteFocusSnapshotStore,
)


def _sql_service():
    journal = SQLiteFocusJournal(":memory:")
    snapshots = SQLiteFocusSnapshotStore(":memory:")
    persistence = FocusEpisodePersistenceService(journal=journal, snapshots=snapshots)
    return FocusServiceFacade(persistence)


def test_sqlite_persistence_adapter_e2e():
    """Verify ACID SQLite persistence journal and snapshots execute identically to in-memory."""
    service = _sql_service()

    # 1. Start episode
    res_start = service.start_ctqf1_episode(
        episode_id="sql-ep-1",
        b=5,
        c=6,
        idempotency_key="sql:start",
    )
    assert res_start.stream_version == 1

    # 2. Attempt step
    res_att = service.submit_attempt(
        episode_id="sql-ep-1",
        input_kind=FocusAttemptInputKind.FACTOR_PAIR,
        raw_input=[2, 3],
        idempotency_key="sql:att1",
        expected_previous_sequence=1,
    )
    assert res_att.judgment == AttemptJudgment.VALID_EXPECTED
    assert res_att.stream_version == 2

    # 3. Checkpoint snapshot
    snapshot = service.persistence.checkpoint("sql-ep-1")
    assert snapshot.last_sequence == 2

    # 4. Reconstruct from SQLite snapshot and journal
    loaded = service.persistence.load("sql-ep-1")
    assert loaded.workspace_kc == KCId.Z1
    assert loaded.current_stage.value == "S2_BRANCH"


def test_concurrency_optimistic_locking_conflict():
    """Verify concurrent requests with the same expected sequence raise EventJournalConflict."""
    service = _sql_service()
    service.start_ctqf1_episode(
        episode_id="race-ep",
        b=5,
        c=6,
        idempotency_key="race:start",
    )

    success_count = 0
    conflict_count = 0

    def submit(worker_id: int):
        try:
            res = service.submit_attempt(
                episode_id="race-ep",
                input_kind=FocusAttemptInputKind.FACTOR_PAIR,
                raw_input=[2, 3],
                idempotency_key=f"race:att:{worker_id}",
                expected_previous_sequence=1,
            )
            return ("SUCCESS", res)
        except EventJournalConflict:
            return ("CONFLICT", None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(submit, i) for i in range(5)]
        for fut in concurrent.futures.as_completed(futures):
            status, _ = fut.result()
            if status == "SUCCESS":
                success_count += 1
            else:
                conflict_count += 1

    # Exactly one writer succeeds at sequence 1 -> 2; all other 4 must detect stale version
    assert success_count == 1
    assert conflict_count == 4


def test_idempotent_retry_under_concurrency():
    """Verify concurrent identical retries (same idempotency key) return identical results safely."""
    service = _sql_service()
    service.start_ctqf1_episode(
        episode_id="idem-ep",
        b=5,
        c=6,
        idempotency_key="idem:start",
    )

    results = []

    def retry():
        return service.submit_attempt(
            episode_id="idem-ep",
            input_kind=FocusAttemptInputKind.FACTOR_PAIR,
            raw_input=[2, 3],
            idempotency_key="idem:same_key",
            expected_previous_sequence=1,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(retry) for _ in range(5)]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())

    # All workers must receive the exact same command result
    for r in results:
        assert r.stream_version == 2
        assert r.judgment == AttemptJudgment.VALID_EXPECTED
        assert r.event_id == results[0].event_id


def test_payload_sanitization_rejects_oversized_payloads():
    """Verify oversized payloads fail fast with HTTP 422 before reaching the domain kernel."""
    app = FastAPI()
    service = _sql_service()
    install_focus_api(app, enabled=True, service=service)
    client = TestClient(app)

    # Start
    client.post(
        "/focus/v1/episodes",
        json={"episode_id": "sec-ep", "b": 5, "c": 6},
        headers={"Idempotency-Key": "sec:start"},
    )

    # Submit huge string payload (> 500 chars)
    giant_string = "x" * 600
    r = client.post(
        "/focus/v1/episodes/sec-ep/attempts",
        json={"input_kind": "BRANCH_DECOMPOSITION", "input": giant_string},
        headers={"Idempotency-Key": "sec:giant", "X-Focus-Expected-Sequence": "1"},
    )
    assert r.status_code == 422


def test_rate_limiting_protects_routes():
    """Verify exceeding request limits produces HTTP 429."""
    app = FastAPI()
    service = _sql_service()
    install_focus_api(app, enabled=True, service=service)
    client = TestClient(app)

    # Exceed 60 requests
    exceeded = False
    for i in range(65):
        r = client.post(
            "/focus/v1/episodes",
            json={"episode_id": f"rate-ep-{i}", "b": 5, "c": 6},
            headers={"Idempotency-Key": f"k-{i}", "Authorization": "Bearer token_alice"},
        )
        if r.status_code == 429:
            exceeded = True
            break

    assert exceeded is True
