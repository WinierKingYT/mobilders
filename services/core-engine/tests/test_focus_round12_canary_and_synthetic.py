import pytest

from app.focus_domain.application import FocusServiceFacade
from app.focus_domain.canary import (
    CanaryHealthPolicy,
    CanaryHealthStatus,
    CanaryOrchestrator,
    CanaryStage,
)
from app.focus_domain.metrics import FocusMetrics
from app.focus_domain.models import KCId, KCState
from app.focus_domain.persistence import (
    FocusEpisodePersistenceService,
    FocusEpisodeReconstructor,
)
from app.focus_domain.sql_persistence import (
    SQLiteFocusJournal,
    SQLiteFocusSnapshotStore,
)
from app.focus_domain.synthetic_traffic import SyntheticTrafficHarness


def _create_sqlite_service() -> FocusServiceFacade:
    journal = SQLiteFocusJournal(":memory:")
    snapshots = SQLiteFocusSnapshotStore(":memory:")
    persistence = FocusEpisodePersistenceService(journal=journal, snapshots=snapshots)
    return FocusServiceFacade(persistence)


def test_canary_orchestrator_stage_advancement():
    """Verify progressive promotion through canary stages (0% -> 5% -> 25% -> 100%)."""
    metrics = FocusMetrics()
    orch = CanaryOrchestrator(initial_stage=CanaryStage.STAGE_0_DISABLED, metrics=metrics)

    assert orch.stage == CanaryStage.STAGE_0_DISABLED
    assert orch.percentage == 0
    assert orch.is_request_admitted("any_user") is False

    # Promote to Stage 1 (5%)
    s1 = orch.advance_stage()
    assert s1 == CanaryStage.STAGE_1_INITIAL
    assert orch.percentage == 5

    # Promote to Stage 2 (25%)
    s2 = orch.advance_stage()
    assert s2 == CanaryStage.STAGE_2_EXPANDED
    assert orch.percentage == 25

    # Promote to Stage 3 (100%)
    s3 = orch.advance_stage()
    assert s3 == CanaryStage.STAGE_3_FULL
    assert orch.percentage == 100
    assert orch.is_request_admitted("any_user") is True

    # Terminal stage promotion remains at Stage 3
    s_term = orch.advance_stage()
    assert s_term == CanaryStage.STAGE_3_FULL


def test_canary_health_policy_breach_and_automated_rollback():
    """Verify health policy halts promotion on high conflict/error rate and supports rollback."""
    metrics = FocusMetrics()
    policy = CanaryHealthPolicy(max_conflict_rate=0.05, min_commands_for_evaluation=5)
    orch = CanaryOrchestrator(
        initial_stage=CanaryStage.STAGE_1_INITIAL,
        policy=policy,
        metrics=metrics,
    )

    # Simulate 10 commands with 3 conflicts (30% conflict rate > 5% allowed)
    for _ in range(7):
        metrics.record_command("submit_attempt", "SUCCESS", duration_ms=10.0)
    for _ in range(3):
        metrics.record_conflict()
        metrics.record_command("submit_attempt", "EventJournalConflict", duration_ms=10.0)

    report = orch.evaluate_health()
    assert report.status == CanaryHealthStatus.BREACHED
    assert len(report.violations) > 0
    assert "Conflict rate" in report.violations[0]

    # Attempting to advance stage MUST fail
    with pytest.raises(ValueError, match="health policy breached"):
        orch.advance_stage()

    # Trigger rollback
    orch.rollback("Elevated conflict rate detected in canary observation")
    assert orch.stage == CanaryStage.STAGE_0_DISABLED
    assert orch.kill_switch is True
    assert orch.percentage == 0
    assert orch.is_request_admitted("user") is False

    summary = metrics.get_summary()
    assert any(e["event_type"] == "CANARY_ROLLBACK_TRIGGERED" for e in summary["recent_audit_events"])


def test_synthetic_healthy_progression_journey():
    """Verify deterministic simulation of an end-to-end healthy run (S1 through S4) on SQLite."""
    service = _create_sqlite_service()
    metrics = FocusMetrics()
    harness = SyntheticTrafficHarness(service=service, metrics=metrics)

    res = harness.run_healthy_progression(episode_id="healthy-ep-1")
    assert res.success is True
    assert res.final_stream_version == 5
    assert res.final_stage == "S4_COMPLETE_SOLUTION_SET"
    assert res.final_phase == "COMPLETED"

    # Verify event stream in SQLite
    events = service.persistence.journal.list_events("healthy-ep-1")
    assert len(events) == 5
    # Verify hash chain integrity
    FocusEpisodeReconstructor().verify_chain(events)


def test_synthetic_misconception_and_repair_journey():
    """Verify diagnosis, intervention, transfer task, and delayed retest on SQLite."""
    service = _create_sqlite_service()
    metrics = FocusMetrics()
    harness = SyntheticTrafficHarness(service=service, metrics=metrics)

    res = harness.run_misconception_and_repair_journey(episode_id="repair-ep-1")
    assert res.success is True
    assert res.final_stream_version >= 6

    # Verify KC status after successful transfer and retest
    final_state = service.persistence.load("repair-ep-1")
    # KC should be in DURABLE_EVIDENCE or TEMPORARILY_RECOVERED
    target_kc = final_state.repair_kc or KCId.F2
    kc_status = final_state.learner.kc_states.get(target_kc)
    assert kc_status in {KCState.DURABLE_EVIDENCE, KCState.TEMPORARILY_RECOVERED}


def test_synthetic_batch_cohort_and_telemetry_aggregation():
    """Verify multi-episode cohort execution aggregates accurate telemetry without corruption."""
    service = _create_sqlite_service()
    metrics = FocusMetrics()
    harness = SyntheticTrafficHarness(service=service, metrics=metrics)

    batch = harness.run_synthetic_batch(count=6)
    assert batch.total_journeys == 6
    assert batch.successful_journeys == 6
    assert batch.total_events >= 30

    # Inspect telemetry summary
    telemetry = batch.telemetry_summary
    assert "start_episode:SUCCESS" in telemetry["commands"]
    assert "submit_attempt:SUCCESS" in telemetry["commands"]
    assert "VALID_EXPECTED" in telemetry["judgments"]
    assert "ADVANCE" in telemetry["decisions"]
    assert telemetry["optimistic_conflicts"] == 0
    assert telemetry["dead_letter_audit_count"] == 0  # Zero unexpected anomalies
