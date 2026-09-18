from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Iterable, List, Mapping, Optional, Protocol
from threading import RLock

from pydantic import BaseModel, ConfigDict, Field

from .decision_pipeline import (
    EpisodePhase,
    FocusDecision,
    FocusDecisionPipeline,
    FocusEpisodeOrchestrator,
    FocusEpisodeState,
    NextActionType,
)
from .models import AttemptJudgment, BarrierState, KCId, KCState


DOMAIN_CONTRACT_VERSION = "0.4+implementation-erratum-0.1"
EVENT_SCHEMA_VERSION = 1
GENESIS_HASH = "GENESIS"


class FocusEventType(str, Enum):
    EPISODE_CREATED = "EPISODE_CREATED"
    ATTEMPT_HANDLED = "ATTEMPT_HANDLED"
    PROBE_RESPONSE_APPLIED = "PROBE_RESPONSE_APPLIED"
    REPAIR_BEGUN = "REPAIR_BEGUN"
    REPAIR_ACTION_SUCCEEDED = "REPAIR_ACTION_SUCCEEDED"
    ORIGINAL_SELF_CORRECTION_SUCCEEDED = "ORIGINAL_SELF_CORRECTION_SUCCEEDED"
    TRANSFER_RECORDED = "TRANSFER_RECORDED"
    RETEST_SCHEDULED = "RETEST_SCHEDULED"
    DELAYED_RETEST_RECORDED = "DELAYED_RETEST_RECORDED"


class FocusEventDraft(BaseModel):
    """Append request before journal sequence/hash assignment.

    ``idempotency_key`` is caller-owned and must be stable across retries.
    Reusing the key for a different logical event is a hard conflict.
    """

    episode_id: str
    idempotency_key: str
    event_type: FocusEventType
    payload: Dict[str, object] = Field(default_factory=dict)
    expected_previous_sequence: int = Field(ge=0)
    domain_contract_version: str = DOMAIN_CONTRACT_VERSION
    schema_version: int = EVENT_SCHEMA_VERSION


class FocusEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    episode_id: str
    idempotency_key: str
    sequence: int = Field(ge=1)
    event_type: FocusEventType
    payload: Dict[str, object] = Field(default_factory=dict)
    occurred_at: datetime
    previous_event_hash: str
    event_hash: str
    domain_contract_version: str = DOMAIN_CONTRACT_VERSION
    schema_version: int = EVENT_SCHEMA_VERSION


class FocusEpisodeSnapshotRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    episode_id: str
    last_sequence: int = Field(ge=0)
    journal_head_hash: str
    state: FocusEpisodeState
    state_hash: str
    created_at: datetime
    domain_contract_version: str = DOMAIN_CONTRACT_VERSION
    schema_version: int = EVENT_SCHEMA_VERSION


class AppendResult(BaseModel):
    event: FocusEvent
    appended: bool


class EventJournalConflict(ValueError):
    pass


class EventJournalCorruption(ValueError):
    pass


class SnapshotConflict(ValueError):
    pass


class EpisodeNotFound(KeyError):
    pass


class FocusEventJournal(Protocol):
    def find_idempotent(self, draft: FocusEventDraft) -> Optional[FocusEvent]: ...
    def get_by_idempotency_key(self, episode_id: str, idempotency_key: str) -> Optional[FocusEvent]: ...
    def append(self, draft: FocusEventDraft) -> AppendResult: ...
    def list_events(self, episode_id: str, *, after_sequence: int = 0) -> List[FocusEvent]: ...
    def last_event(self, episode_id: str) -> Optional[FocusEvent]: ...
    def get_event(self, episode_id: str, sequence: int) -> Optional[FocusEvent]: ...
    def episode_ids(self) -> List[str]: ...


class FocusSnapshotStore(Protocol):
    def get(self, episode_id: str) -> Optional[FocusEpisodeSnapshotRecord]: ...
    def put(self, snapshot: FocusEpisodeSnapshotRecord) -> None: ...


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _draft_identity(draft: FocusEventDraft) -> str:
    # Derived results (currently the decision) are journaled for replay/response
    # fidelity but are not part of command identity. This lets a retry check
    # idempotency *before* re-executing a phase-sensitive command.
    identity_payload = {
        key: value for key, value in draft.payload.items() if key != "decision"
    }
    value = {
        "episode_id": draft.episode_id,
        "idempotency_key": draft.idempotency_key,
        "event_type": draft.event_type.value,
        "payload": identity_payload,
        "domain_contract_version": draft.domain_contract_version,
        "schema_version": draft.schema_version,
    }
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _event_hash_payload(event: FocusEvent) -> Mapping[str, object]:
    return {
        "event_id": event.event_id,
        "episode_id": event.episode_id,
        "idempotency_key": event.idempotency_key,
        "sequence": event.sequence,
        "event_type": event.event_type.value,
        "payload": event.payload,
        "occurred_at": event.occurred_at.isoformat(),
        "previous_event_hash": event.previous_event_hash,
        "domain_contract_version": event.domain_contract_version,
        "schema_version": event.schema_version,
    }


def compute_event_hash(event: FocusEvent) -> str:
    return hashlib.sha256(
        _canonical_json(_event_hash_payload(event)).encode("utf-8")
    ).hexdigest()


def compute_state_hash(state: FocusEpisodeState) -> str:
    return hashlib.sha256(
        _canonical_json(state.model_dump(mode="json")).encode("utf-8")
    ).hexdigest()


class InMemoryFocusEventRepository:
    """Reference append-only journal with idempotent retry semantics."""

    def __init__(self) -> None:
        self._events: Dict[str, List[FocusEvent]] = {}
        self._idempotency: Dict[tuple[str, str], tuple[str, FocusEvent]] = {}
        self._lock = RLock()

    def find_idempotent(self, draft: FocusEventDraft) -> Optional[FocusEvent]:
        identity = _draft_identity(draft)
        key = (draft.episode_id, draft.idempotency_key)
        with self._lock:
            existing = self._idempotency.get(key)
            if existing is None:
                return None
            existing_identity, existing_event = existing
            if existing_identity != identity:
                raise EventJournalConflict(
                    "Idempotency key was already used for a different Focus event"
                )
            return existing_event.model_copy(deep=True)

    def get_by_idempotency_key(
        self,
        episode_id: str,
        idempotency_key: str,
    ) -> Optional[FocusEvent]:
        with self._lock:
            existing = self._idempotency.get((episode_id, idempotency_key))
            if existing is None:
                return None
            return existing[1].model_copy(deep=True)

    def append(self, draft: FocusEventDraft) -> AppendResult:
        identity = _draft_identity(draft)
        key = (draft.episode_id, draft.idempotency_key)
        with self._lock:
            existing = self._idempotency.get(key)
            if existing is not None:
                existing_identity, existing_event = existing
                if existing_identity != identity:
                    raise EventJournalConflict(
                        "Idempotency key was already used for a different Focus event"
                    )
                return AppendResult(event=existing_event.model_copy(deep=True), appended=False)

            events = self._events.setdefault(draft.episode_id, [])
            current_sequence = len(events)
            if draft.expected_previous_sequence != current_sequence:
                raise EventJournalConflict(
                    "Stale Focus stream version: "
                    f"expected previous sequence {draft.expected_previous_sequence}, "
                    f"actual {current_sequence}"
                )

            sequence = current_sequence + 1
            previous_hash = events[-1].event_hash if events else GENESIS_HASH
            occurred_at = datetime.now(timezone.utc)
            event_id = f"{draft.episode_id}:{sequence}:{draft.idempotency_key}"

            provisional = FocusEvent(
                event_id=event_id,
                episode_id=draft.episode_id,
                idempotency_key=draft.idempotency_key,
                sequence=sequence,
                event_type=draft.event_type,
                payload=draft.payload,
                occurred_at=occurred_at,
                previous_event_hash=previous_hash,
                event_hash="",
                domain_contract_version=draft.domain_contract_version,
                schema_version=draft.schema_version,
            )
            event = provisional.model_copy(
                update={"event_hash": compute_event_hash(provisional)}
            )
            stored = event.model_copy(deep=True)
            events.append(stored)
            self._idempotency[key] = (identity, stored)
            return AppendResult(event=stored.model_copy(deep=True), appended=True)

    def list_events(
        self,
        episode_id: str,
        *,
        after_sequence: int = 0,
    ) -> List[FocusEvent]:
        with self._lock:
            return [
                event.model_copy(deep=True)
                for event in self._events.get(episode_id, [])
                if event.sequence > after_sequence
            ]

    def last_event(self, episode_id: str) -> Optional[FocusEvent]:
        with self._lock:
            events = self._events.get(episode_id, [])
            return events[-1].model_copy(deep=True) if events else None

    def get_event(self, episode_id: str, sequence: int) -> Optional[FocusEvent]:
        if sequence < 1:
            return None
        with self._lock:
            events = self._events.get(episode_id, [])
            index = sequence - 1
            return events[index].model_copy(deep=True) if index < len(events) else None

    def episode_ids(self) -> List[str]:
        with self._lock:
            return sorted(self._events)


class InMemoryFocusSnapshotRepository:
    """Reference snapshot store; journal remains the source of truth."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, FocusEpisodeSnapshotRecord] = {}

    def get(self, episode_id: str) -> Optional[FocusEpisodeSnapshotRecord]:
        snapshot = self._snapshots.get(episode_id)
        return snapshot.model_copy(deep=True) if snapshot else None

    def put(self, snapshot: FocusEpisodeSnapshotRecord) -> None:
        existing = self._snapshots.get(snapshot.episode_id)
        if existing is not None and snapshot.last_sequence < existing.last_sequence:
            raise SnapshotConflict("Snapshot sequence cannot move backwards")
        if (
            existing is not None
            and snapshot.last_sequence == existing.last_sequence
            and (
                snapshot.journal_head_hash != existing.journal_head_hash
                or snapshot.state_hash != existing.state_hash
            )
        ):
            raise SnapshotConflict("Same-sequence snapshot cannot change content")
        self._snapshots[snapshot.episode_id] = snapshot.model_copy(deep=True)


class FocusEventReducer:
    """Deterministic reducer from one event into one episode state."""

    def __init__(self) -> None:
        self._orch = FocusEpisodeOrchestrator()

    def apply(
        self,
        state: Optional[FocusEpisodeState],
        event: FocusEvent,
    ) -> FocusEpisodeState:
        if event.schema_version != EVENT_SCHEMA_VERSION:
            raise EventJournalCorruption(
                f"Unsupported Focus event schema version: {event.schema_version}"
            )
        if event.domain_contract_version != DOMAIN_CONTRACT_VERSION:
            raise EventJournalCorruption(
                "Domain contract version mismatch during Focus replay"
            )

        if event.event_type == FocusEventType.EPISODE_CREATED:
            if state is not None:
                raise EventJournalCorruption("EPISODE_CREATED must be the first event")
            try:
                return FocusEpisodeState.model_validate(event.payload["state"])
            except Exception as exc:  # pragma: no cover - validation detail
                raise EventJournalCorruption("Invalid EPISODE_CREATED payload") from exc

        if state is None:
            raise EventJournalCorruption("Focus event stream is missing EPISODE_CREATED")

        if event.event_type == FocusEventType.ATTEMPT_HANDLED:
            try:
                judgment = AttemptJudgment(str(event.payload["judgment"]))
                observations = frozenset(str(x) for x in event.payload.get("observations", []))
            except Exception as exc:
                raise EventJournalCorruption("Invalid ATTEMPT_HANDLED payload") from exc
            next_state, _ = self._orch.handle_attempt(
                state,
                judgment=judgment,
                observations=observations,
            )
            return next_state

        if event.event_type == FocusEventType.PROBE_RESPONSE_APPLIED:
            try:
                result = self._orch.apply_probe_response(
                    state,
                    probe_id=str(event.payload["probe_id"]),
                    response_code=str(event.payload["response_code"]),
                )
            except Exception as exc:
                raise EventJournalCorruption("Invalid probe replay") from exc
            return result.state

        if event.event_type == FocusEventType.REPAIR_BEGUN:
            try:
                decision = FocusDecision.model_validate(event.payload["decision"])
                return self._orch.begin_repair(state, decision)
            except Exception as exc:
                raise EventJournalCorruption("Invalid repair-begin replay") from exc

        if event.event_type == FocusEventType.REPAIR_ACTION_SUCCEEDED:
            try:
                next_state = self._orch.record_repair_action_success(state)
                if "transfer_task_context" in event.payload and event.payload["transfer_task_context"]:
                    next_state.transfer_task_context = event.payload["transfer_task_context"]
                return next_state
            except Exception as exc:
                raise EventJournalCorruption("Invalid repair-success replay") from exc

        if event.event_type == FocusEventType.ORIGINAL_SELF_CORRECTION_SUCCEEDED:
            try:
                return self._orch.record_original_self_correction_success(state)
            except Exception as exc:
                raise EventJournalCorruption("Invalid self-correction replay") from exc

        if event.event_type == FocusEventType.TRANSFER_RECORDED:
            try:
                prior_gap = event.payload.get("prior_gap_state")
                prior_barrier = event.payload.get("prior_barrier_state")
                return self._orch.record_transfer_result(
                    state,
                    success=bool(event.payload["success"]),
                    prior_gap_state=KCState(str(prior_gap)) if prior_gap else None,
                    prior_barrier_state=BarrierState(str(prior_barrier)) if prior_barrier else None,
                )
            except Exception as exc:
                raise EventJournalCorruption("Invalid transfer replay") from exc

        if event.event_type == FocusEventType.RETEST_SCHEDULED:
            try:
                target_kc = KCId(str(event.payload["target_kc"]))
                barrier_id = str(event.payload["barrier_id"]) if event.payload.get("barrier_id") else None
                next_state = self._orch.record_retest_scheduled(
                    state,
                    target_kc=target_kc,
                    barrier_id=barrier_id,
                )
                if "retest_task_context" in event.payload and event.payload["retest_task_context"]:
                    next_state.retest_task_context = event.payload["retest_task_context"]
                return next_state
            except Exception as exc:
                raise EventJournalCorruption("Invalid retest-scheduled replay") from exc

        if event.event_type == FocusEventType.DELAYED_RETEST_RECORDED:
            try:
                target_kc = KCId(str(event.payload["target_kc"]))
                success = bool(event.payload["success"])
                barrier_id = str(event.payload["barrier_id"]) if event.payload.get("barrier_id") else None
                return self._orch.record_delayed_retest_result(
                    state,
                    target_kc=target_kc,
                    success=success,
                    barrier_id=barrier_id,
                )
            except Exception as exc:
                raise EventJournalCorruption("Invalid delayed-retest replay") from exc

        raise EventJournalCorruption(f"Unknown event type: {event.event_type}")


class FocusEpisodeReconstructor:
    """Verify a hash chain and reconstruct state from journal (+ optional snapshot)."""

    def __init__(self) -> None:
        self._reducer = FocusEventReducer()

    def verify_chain(
        self,
        events: Iterable[FocusEvent],
        *,
        expected_start_sequence: int = 1,
        expected_previous_hash: str = GENESIS_HASH,
    ) -> None:
        expected_sequence = expected_start_sequence
        previous_hash = expected_previous_hash
        for event in events:
            if event.sequence != expected_sequence:
                raise EventJournalCorruption(
                    f"Non-contiguous sequence: expected {expected_sequence}, got {event.sequence}"
                )
            if event.previous_event_hash != previous_hash:
                raise EventJournalCorruption("Broken previous_event_hash chain")
            if compute_event_hash(event.model_copy(update={"event_hash": ""})) != event.event_hash:
                raise EventJournalCorruption("Focus event hash mismatch")
            previous_hash = event.event_hash
            expected_sequence += 1

    def reconstruct_from_events(self, events: Iterable[FocusEvent]) -> FocusEpisodeState:
        event_list = list(events)
        if not event_list:
            raise EpisodeNotFound("No events found for Focus episode")
        self.verify_chain(event_list)
        state: Optional[FocusEpisodeState] = None
        episode_id = event_list[0].episode_id
        for event in event_list:
            if event.episode_id != episode_id:
                raise EventJournalCorruption("Cross-episode event in one replay stream")
            state = self._reducer.apply(state, event)
        assert state is not None
        return state

    def reconstruct(
        self,
        *,
        episode_id: str,
        journal: FocusEventJournal,
        snapshots: Optional[FocusSnapshotStore] = None,
    ) -> FocusEpisodeState:
        snapshot = snapshots.get(episode_id) if snapshots else None
        if snapshot is None:
            return self.reconstruct_from_events(journal.list_events(episode_id))

        if snapshot.domain_contract_version != DOMAIN_CONTRACT_VERSION:
            raise EventJournalCorruption("Snapshot domain contract version mismatch")
        if snapshot.schema_version != EVENT_SCHEMA_VERSION:
            raise EventJournalCorruption("Snapshot schema version mismatch")
        if compute_state_hash(snapshot.state) != snapshot.state_hash:
            raise EventJournalCorruption("Snapshot state hash mismatch")
        anchor = journal.get_event(episode_id, snapshot.last_sequence)
        if anchor is None or anchor.event_hash != snapshot.journal_head_hash:
            raise EventJournalCorruption("Snapshot is not anchored to the journal head")

        tail = journal.list_events(episode_id, after_sequence=snapshot.last_sequence)
        self.verify_chain(
            tail,
            expected_start_sequence=snapshot.last_sequence + 1,
            expected_previous_hash=snapshot.journal_head_hash,
        )
        state = snapshot.state.model_copy(deep=True)
        for event in tail:
            state = self._reducer.apply(state, event)
        return state


class FocusEpisodePersistenceService:
    """Reference transactional boundary around the pure Focus orchestrator.

    The service computes the next state first. It appends an event only after
    the command is valid. This prevents invalid commands from polluting the
    append-only journal.
    """

    def __init__(
        self,
        *,
        journal: Optional[FocusEventJournal] = None,
        snapshots: Optional[FocusSnapshotStore] = None,
    ) -> None:
        self.journal = journal or InMemoryFocusEventRepository()
        self.snapshots = snapshots or InMemoryFocusSnapshotRepository()
        self._orch = FocusEpisodeOrchestrator()
        self._pipeline = FocusDecisionPipeline()
        self._reconstructor = FocusEpisodeReconstructor()

    def load(self, episode_id: str) -> FocusEpisodeState:
        return self._reconstructor.reconstruct(
            episode_id=episode_id,
            journal=self.journal,
            snapshots=self.snapshots,
        )

    def list_episodes(self) -> List[str]:
        return self.journal.episode_ids()

    def load_at_sequence(
        self,
        episode_id: str,
        sequence: int,
    ) -> FocusEpisodeState:
        if sequence < 1:
            raise EpisodeNotFound(episode_id)
        events = [
            event
            for event in self.journal.list_events(episode_id)
            if event.sequence <= sequence
        ]
        return self._reconstructor.reconstruct_from_events(events)

    def _current_sequence(self, episode_id: str) -> int:
        event = self.journal.last_event(episode_id)
        return event.sequence if event else 0

    def start_episode(
        self,
        *,
        episode_id: str,
        initial_state: FocusEpisodeState,
        idempotency_key: str,
    ) -> tuple[FocusEpisodeState, FocusEvent]:
        draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.EPISODE_CREATED,
            payload={"state": initial_state.model_dump(mode="json")},
            expected_previous_sequence=0,
        )
        existing = self.journal.find_idempotent(draft)
        if existing is not None:
            return self.load_at_sequence(episode_id, existing.sequence), existing
        append = self.journal.append(draft)
        return self.load(episode_id), append.event

    def handle_attempt(
        self,
        *,
        episode_id: str,
        judgment: AttemptJudgment,
        observations: Iterable[str] = (),
        idempotency_key: str,
        expected_previous_sequence: Optional[int] = None,
        command_metadata: Optional[Dict[str, object]] = None,
    ) -> tuple[FocusEpisodeState, FocusDecision, FocusEvent]:
        observation_set = frozenset(observations)
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        base_draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.ATTEMPT_HANDLED,
            expected_previous_sequence=append_expected_sequence,
            payload={
                "judgment": judgment.value,
                "observations": sorted(observation_set),
                **(command_metadata or {}),
            },
        )
        existing = self.journal.find_idempotent(base_draft)
        if existing is not None:
            return (
                self.load_at_sequence(episode_id, existing.sequence),
                FocusDecision.model_validate(existing.payload["decision"]),
                existing,
            )

        current_seq = self._current_sequence(episode_id)
        if (
            expected_previous_sequence is not None
            and 0 < expected_previous_sequence <= current_seq
        ):
            current = self.load_at_sequence(episode_id, expected_previous_sequence)
        else:
            current = self.load(episode_id)
        next_state, decision = self._orch.handle_attempt(
            current,
            judgment=judgment,
            observations=observation_set,
        )
        draft = base_draft.model_copy(
            update={
                "payload": {
                    **base_draft.payload,
                    "decision": decision.model_dump(mode="json"),
                }
            }
        )
        append = self.journal.append(draft)
        if not append.appended:
            return (
                self.load_at_sequence(episode_id, append.event.sequence),
                FocusDecision.model_validate(append.event.payload["decision"]),
                append.event,
            )
        return next_state, decision, append.event

    def apply_probe_response(
        self,
        *,
        episode_id: str,
        probe_id: str,
        response_code: str,
        idempotency_key: str,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusDecision, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        base_draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.PROBE_RESPONSE_APPLIED,
            expected_previous_sequence=append_expected_sequence,
            payload={"probe_id": probe_id, "response_code": response_code},
        )
        existing = self.journal.find_idempotent(base_draft)
        if existing is not None:
            return (
                self.load_at_sequence(episode_id, existing.sequence),
                FocusDecision.model_validate(existing.payload["decision"]),
                existing,
            )

        if 0 < append_expected_sequence <= current_sequence:
            current = self.load_at_sequence(episode_id, append_expected_sequence)
        else:
            current = self.load(episode_id)
        applied = self._orch.apply_probe_response(
            current,
            probe_id=probe_id,
            response_code=response_code,
        )
        draft = base_draft.model_copy(
            update={
                "payload": {
                    **base_draft.payload,
                    "decision": applied.decision.model_dump(mode="json"),
                }
            }
        )
        append = self.journal.append(draft)
        if not append.appended:
            return (
                self.load_at_sequence(episode_id, append.event.sequence),
                FocusDecision.model_validate(append.event.payload["decision"]),
                append.event,
            )
        return applied.state, applied.decision, append.event

    def begin_current_repair(
        self,
        *,
        episode_id: str,
        idempotency_key: str,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusDecision, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        base_draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.REPAIR_BEGUN,
            expected_previous_sequence=append_expected_sequence,
            payload={},
        )
        existing = self.journal.find_idempotent(base_draft)
        if existing is not None:
            return (
                self.load_at_sequence(episode_id, existing.sequence),
                FocusDecision.model_validate(existing.payload["decision"]),
                existing,
            )

        if 0 < append_expected_sequence <= current_sequence:
            current = self.load_at_sequence(episode_id, append_expected_sequence)
        else:
            current = self.load(episode_id)
        if current.last_judgment is None:
            raise ValueError("No prior attempt exists for repair decision")
        decision = self._pipeline.decide_after_attempt(
            current,
            judgment=current.last_judgment,
            observations=current.last_observations,
        )
        if decision.action != NextActionType.START_REPAIR:
            raise ValueError("Current episode state does not authorize START_REPAIR")
        next_state = self._orch.begin_repair(current, decision)
        append = self.journal.append(
            base_draft.model_copy(
                update={"payload": {"decision": decision.model_dump(mode="json")}}
            )
        )
        if not append.appended:
            return (
                self.load_at_sequence(episode_id, append.event.sequence),
                FocusDecision.model_validate(append.event.payload["decision"]),
                append.event,
            )
        return next_state, decision, append.event

    def record_repair_action_success(
        self,
        *,
        episode_id: str,
        idempotency_key: str,
        transfer_task_context: Optional[Dict[str, Any]] = None,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.REPAIR_ACTION_SUCCEEDED,
            expected_previous_sequence=append_expected_sequence,
            payload={"transfer_task_context": transfer_task_context} if transfer_task_context else {},
        )
        existing = self.journal.find_idempotent(draft)
        if existing is not None:
            return self.load_at_sequence(episode_id, existing.sequence), existing
        current = self.load(episode_id)
        next_state = self._orch.record_repair_action_success(current)
        if transfer_task_context:
            next_state.transfer_task_context = transfer_task_context
        append = self.journal.append(draft)
        return next_state, append.event

    def record_original_self_correction_success(
        self,
        *,
        episode_id: str,
        idempotency_key: str,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.ORIGINAL_SELF_CORRECTION_SUCCEEDED,
            expected_previous_sequence=append_expected_sequence,
        )
        existing = self.journal.find_idempotent(draft)
        if existing is not None:
            return self.load_at_sequence(episode_id, existing.sequence), existing
        current = self.load(episode_id)
        next_state = self._orch.record_original_self_correction_success(current)
        append = self.journal.append(draft)
        return next_state, append.event

    def record_transfer_result(
        self,
        *,
        episode_id: str,
        success: bool,
        idempotency_key: str,
        prior_gap_state: Optional[KCState] = None,
        prior_barrier_state: Optional[BarrierState] = None,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.TRANSFER_RECORDED,
            expected_previous_sequence=append_expected_sequence,
            payload={
                "success": success,
                "prior_gap_state": prior_gap_state.value if prior_gap_state else None,
                "prior_barrier_state": (
                    prior_barrier_state.value if prior_barrier_state else None
                ),
            },
        )
        existing = self.journal.find_idempotent(draft)
        if existing is not None:
            return self.load_at_sequence(episode_id, existing.sequence), existing
        current = self.load(episode_id)
        next_state = self._orch.record_transfer_result(
            current,
            success=success,
            prior_gap_state=prior_gap_state,
            prior_barrier_state=prior_barrier_state,
        )
        append = self.journal.append(draft)
        return next_state, append.event

    def record_retest_scheduled(
        self,
        *,
        episode_id: str,
        target_kc: KCId,
        idempotency_key: str,
        barrier_id: Optional[str] = None,
        retest_task_context: Optional[Dict[str, Any]] = None,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.RETEST_SCHEDULED,
            expected_previous_sequence=append_expected_sequence,
            payload={
                "target_kc": target_kc.value,
                "barrier_id": barrier_id,
                "retest_task_context": retest_task_context,
            },
        )
        existing = self.journal.find_idempotent(draft)
        if existing is not None:
            return self.load_at_sequence(episode_id, existing.sequence), existing
        current = self.load(episode_id)
        next_state = self._orch.record_retest_scheduled(
            current,
            target_kc=target_kc,
            barrier_id=barrier_id,
        )
        if retest_task_context:
            next_state.retest_task_context = retest_task_context
        append = self.journal.append(draft)
        return next_state, append.event

    def record_delayed_retest_result(
        self,
        *,
        episode_id: str,
        target_kc: KCId,
        success: bool,
        idempotency_key: str,
        barrier_id: Optional[str] = None,
        expected_previous_sequence: Optional[int] = None,
    ) -> tuple[FocusEpisodeState, FocusEvent]:
        current_sequence = self._current_sequence(episode_id)
        append_expected_sequence = (
            current_sequence
            if expected_previous_sequence is None
            else expected_previous_sequence
        )
        draft = FocusEventDraft(
            episode_id=episode_id,
            idempotency_key=idempotency_key,
            event_type=FocusEventType.DELAYED_RETEST_RECORDED,
            expected_previous_sequence=append_expected_sequence,
            payload={
                "target_kc": target_kc.value,
                "success": success,
                "barrier_id": barrier_id,
            },
        )
        existing = self.journal.find_idempotent(draft)
        if existing is not None:
            return self.load_at_sequence(episode_id, existing.sequence), existing
        current = self.load(episode_id)
        next_state = self._orch.record_delayed_retest_result(
            current,
            target_kc=target_kc,
            success=success,
            barrier_id=barrier_id,
        )
        append = self.journal.append(draft)
        return next_state, append.event

    def checkpoint(self, episode_id: str) -> FocusEpisodeSnapshotRecord:
        state = self.load(episode_id)
        last_event = self.journal.last_event(episode_id)
        if last_event is None:
            raise EpisodeNotFound(episode_id)
        snapshot = FocusEpisodeSnapshotRecord(
            episode_id=episode_id,
            last_sequence=last_event.sequence,
            journal_head_hash=last_event.event_hash,
            state=state.model_copy(deep=True),
            state_hash=compute_state_hash(state),
            created_at=datetime.now(timezone.utc),
        )
        self.snapshots.put(snapshot)
        return snapshot
