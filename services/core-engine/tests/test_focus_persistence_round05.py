import pytest

from app.focus_domain.decision_pipeline import EpisodePhase, FocusEpisodeState, NextActionType
from app.focus_domain.models import AttemptJudgment, BarrierState, KCId, KCState
from app.focus_domain.persistence import (
    EventJournalConflict,
    EventJournalCorruption,
    FocusEpisodePersistenceService,
    FocusEpisodeReconstructor,
    FocusEventDraft,
    FocusEventType,
    InMemoryFocusEventRepository,
    InMemoryFocusSnapshotRepository,
)


def _service():
    return FocusEpisodePersistenceService(
        journal=InMemoryFocusEventRepository(),
        snapshots=InMemoryFocusSnapshotRepository(),
    )


def _start_f2(service, episode_id="ep-1"):
    state, event = service.start_episode(
        episode_id=episode_id,
        initial_state=FocusEpisodeState(workspace_kc=KCId.F2),
        idempotency_key=f"{episode_id}:start",
    )
    assert event.sequence == 1
    return state


def test_event_journal_is_contiguous_and_hash_chained():
    service = _service()
    _start_f2(service)
    service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )

    events = service.journal.list_events("ep-1")
    assert [event.sequence for event in events] == [1, 2]
    assert events[0].previous_event_hash == "GENESIS"
    assert events[1].previous_event_hash == events[0].event_hash
    FocusEpisodeReconstructor().verify_chain(events)


def test_same_idempotency_key_same_command_returns_same_event_without_duplicate():
    service = _service()
    _start_f2(service)

    state1, decision1, event1 = service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )
    state2, decision2, event2 = service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )

    assert event2.event_id == event1.event_id
    assert len(service.journal.list_events("ep-1")) == 2
    assert decision2 == decision1
    assert state2 == state1


def test_same_idempotency_key_different_command_is_hard_conflict():
    service = _service()
    _start_f2(service)
    service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )

    with pytest.raises(EventJournalConflict):
        service.handle_attempt(
            episode_id="ep-1",
            judgment=AttemptJudgment.VALID_EXPECTED,
            observations=set(),
            idempotency_key="ep-1:a1",
        )


def test_probe_retry_is_idempotent_even_after_phase_changed():
    service = _service()
    _start_f2(service)
    state, decision, _ = service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )
    assert state.phase == EpisodePhase.PROBING
    assert decision.probe_id == "PR-F2-01"

    first_state, first_decision, first_event = service.apply_probe_response(
        episode_id="ep-1",
        probe_id="PR-F2-01",
        response_code="PRODUCT_ONLY",
        idempotency_key="ep-1:p1",
    )
    assert first_state.phase == EpisodePhase.WORKSPACE
    assert first_decision.action == NextActionType.START_REPAIR

    retry_state, retry_decision, retry_event = service.apply_probe_response(
        episode_id="ep-1",
        probe_id="PR-F2-01",
        response_code="PRODUCT_ONLY",
        idempotency_key="ep-1:p1",
    )
    assert retry_event.event_id == first_event.event_id
    assert retry_state == first_state
    assert retry_decision == first_decision
    assert len(service.journal.list_events("ep-1")) == 3


def test_full_repair_episode_survives_crash_and_replay():
    service = _service()
    _start_f2(service)
    service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )
    service.apply_probe_response(
        episode_id="ep-1",
        probe_id="PR-F2-01",
        response_code="PRODUCT_ONLY",
        idempotency_key="ep-1:p1",
    )
    repairing, decision, _ = service.begin_current_repair(
        episode_id="ep-1",
        idempotency_key="ep-1:r0",
    )
    assert decision.intervention_id == "IT-F2-01"
    assert repairing.phase == EpisodePhase.REPAIRING

    service.record_repair_action_success(
        episode_id="ep-1", idempotency_key="ep-1:r1"
    )
    service.record_original_self_correction_success(
        episode_id="ep-1", idempotency_key="ep-1:r2"
    )
    final_state, _ = service.record_transfer_result(
        episode_id="ep-1",
        success=True,
        idempotency_key="ep-1:r3",
    )

    # Simulate process loss: reconstruct using a brand new reconstructor from journal only.
    replayed = FocusEpisodeReconstructor().reconstruct_from_events(
        service.journal.list_events("ep-1")
    )
    assert replayed == final_state
    assert replayed.phase == EpisodePhase.WORKSPACE
    assert replayed.learner.kc_states[KCId.F2] == KCState.TEMPORARILY_RECOVERED
    assert replayed.learner.barrier_states["BH-F2-01"] == BarrierState.TEMPORARILY_RECOVERED


def test_snapshot_plus_tail_reconstruction_matches_full_replay():
    service = _service()
    _start_f2(service)
    service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )
    service.checkpoint("ep-1")

    state, _, _ = service.apply_probe_response(
        episode_id="ep-1",
        probe_id="PR-F2-01",
        response_code="PRODUCT_ONLY",
        idempotency_key="ep-1:p1",
    )
    via_snapshot = service.load("ep-1")
    full = FocusEpisodeReconstructor().reconstruct_from_events(
        service.journal.list_events("ep-1")
    )
    assert via_snapshot == full == state


def test_snapshot_tampering_is_detected():
    service = _service()
    _start_f2(service)
    snapshot = service.checkpoint("ep-1")
    tampered_state = snapshot.state.model_copy(update={"probe_budget_remaining": 0})
    service.snapshots._snapshots["ep-1"] = snapshot.model_copy(
        update={"state": tampered_state}
    )

    with pytest.raises(EventJournalCorruption, match="Snapshot state hash mismatch"):
        service.load("ep-1")


def test_event_payload_tampering_breaks_hash_verification():
    service = _service()
    _start_f2(service)
    service.handle_attempt(
        episode_id="ep-1",
        judgment=AttemptJudgment.INVALID_MATHEMATICS,
        observations={"EO-FACTOR-PAIR-SUM-MISMATCH"},
        idempotency_key="ep-1:a1",
    )
    events = service.journal.list_events("ep-1")
    tampered = list(events)
    tampered[1] = tampered[1].model_copy(
        update={"payload": {**tampered[1].payload, "observations": []}}
    )

    with pytest.raises(EventJournalCorruption, match="hash mismatch"):
        FocusEpisodeReconstructor().reconstruct_from_events(tampered)


def test_invalid_phase_command_does_not_pollute_journal():
    service = _service()
    _start_f2(service)
    before = len(service.journal.list_events("ep-1"))

    with pytest.raises(ValueError):
        service.record_transfer_result(
            episode_id="ep-1",
            success=True,
            idempotency_key="ep-1:illegal-transfer",
        )

    assert len(service.journal.list_events("ep-1")) == before


def test_reference_repository_rejects_same_episode_idempotency_collision():
    journal = InMemoryFocusEventRepository()
    journal.append(
        FocusEventDraft(
            episode_id="ep-a",
            idempotency_key="same-key",
            event_type=FocusEventType.EPISODE_CREATED,
            expected_previous_sequence=0,
            payload={"state": FocusEpisodeState(workspace_kc=KCId.N1).model_dump(mode="json")},
        )
    )
    with pytest.raises(EventJournalConflict):
        journal.append(
            FocusEventDraft(
                episode_id="ep-a",
                idempotency_key="same-key",
                event_type=FocusEventType.ATTEMPT_HANDLED,
                expected_previous_sequence=1,
                payload={"judgment": AttemptJudgment.VALID_EXPECTED.value, "observations": []},
            )
        )


def test_idempotency_key_is_scoped_per_episode():
    journal = InMemoryFocusEventRepository()
    for episode_id, kc in [("ep-a", KCId.N1), ("ep-b", KCId.N2)]:
        result = journal.append(
            FocusEventDraft(
                episode_id=episode_id,
                idempotency_key="start",
                event_type=FocusEventType.EPISODE_CREATED,
                expected_previous_sequence=0,
                payload={"state": FocusEpisodeState(workspace_kc=kc).model_dump(mode="json")},
            )
        )
        assert result.appended is True


def test_optimistic_stream_version_blocks_stale_concurrent_append():
    journal = InMemoryFocusEventRepository()
    journal.append(
        FocusEventDraft(
            episode_id="ep-a",
            idempotency_key="start",
            event_type=FocusEventType.EPISODE_CREATED,
            expected_previous_sequence=0,
            payload={"state": FocusEpisodeState(workspace_kc=KCId.F2).model_dump(mode="json")},
        )
    )

    # Two hypothetical writers both read sequence 1.
    first = FocusEventDraft(
        episode_id="ep-a",
        idempotency_key="writer-1",
        event_type=FocusEventType.ATTEMPT_HANDLED,
        expected_previous_sequence=1,
        payload={"judgment": AttemptJudgment.VALID_EXPECTED.value, "observations": []},
    )
    stale_second = FocusEventDraft(
        episode_id="ep-a",
        idempotency_key="writer-2",
        event_type=FocusEventType.ATTEMPT_HANDLED,
        expected_previous_sequence=1,
        payload={"judgment": AttemptJudgment.VALID_EXPECTED.value, "observations": []},
    )
    journal.append(first)
    with pytest.raises(EventJournalConflict, match="Stale Focus stream version"):
        journal.append(stale_second)


def test_repository_returns_deep_copies_not_mutable_internal_events():
    journal = InMemoryFocusEventRepository()
    appended = journal.append(
        FocusEventDraft(
            episode_id="ep-a",
            idempotency_key="start",
            event_type=FocusEventType.EPISODE_CREATED,
            expected_previous_sequence=0,
            payload={"state": FocusEpisodeState(workspace_kc=KCId.N1).model_dump(mode="json")},
        )
    ).event
    appended.payload["external_mutation"] = True

    stored = journal.list_events("ep-a")[0]
    assert "external_mutation" not in stored.payload
    FocusEpisodeReconstructor().verify_chain([stored])
