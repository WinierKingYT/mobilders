"""SQLite-backed persistent event journal and snapshot store for Focus V1 Alpha.

Implements the pure `FocusEventJournal` and `FocusSnapshotStore` protocols
using transactional, ACID-compliant SQLite with optimistic concurrency checks.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .persistence import (
    AppendResult,
    DOMAIN_CONTRACT_VERSION,
    EVENT_SCHEMA_VERSION,
    EventJournalConflict,
    EventJournalCorruption,
    FocusEpisodeSnapshotRecord,
    FocusEvent,
    FocusEventDraft,
    FocusEventType,
    GENESIS_HASH,
    SnapshotConflict,
    _canonical_json,
    _draft_identity,
    compute_event_hash,
)


class SQLiteFocusJournal:
    """ACID-compliant SQLite append-only journal for Focus events."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            isolation_level=None,  # autocommit mode, transactions handled explicitly
        )
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS focus_events (
                        episode_id TEXT NOT NULL,
                        sequence INTEGER NOT NULL,
                        event_id TEXT NOT NULL UNIQUE,
                        idempotency_key TEXT NOT NULL,
                        idempotency_identity TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        occurred_at TEXT NOT NULL,
                        previous_event_hash TEXT NOT NULL,
                        event_hash TEXT NOT NULL,
                        domain_contract_version TEXT NOT NULL,
                        schema_version INTEGER NOT NULL,
                        PRIMARY KEY (episode_id, sequence),
                        UNIQUE (episode_id, idempotency_key)
                    )
                    """
                )
                self._conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_focus_events_episode_seq 
                    ON focus_events (episode_id, sequence)
                    """
                )

    def find_idempotent(self, draft: FocusEventDraft) -> Optional[FocusEvent]:
        identity = _draft_identity(draft)
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT event_id, episode_id, idempotency_key, sequence, event_type,
                       payload_json, occurred_at, previous_event_hash, event_hash,
                       domain_contract_version, schema_version, idempotency_identity
                FROM focus_events
                WHERE episode_id = ? AND idempotency_key = ?
                """,
                (draft.episode_id, draft.idempotency_key),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            stored_identity = row[11]
            if stored_identity != identity:
                raise EventJournalConflict(
                    "Idempotency key was already used for a different Focus event"
                )
            return self._row_to_event(row)

    def get_by_idempotency_key(
        self,
        episode_id: str,
        idempotency_key: str,
    ) -> Optional[FocusEvent]:
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT event_id, episode_id, idempotency_key, sequence, event_type,
                       payload_json, occurred_at, previous_event_hash, event_hash,
                       domain_contract_version, schema_version, idempotency_identity
                FROM focus_events
                WHERE episode_id = ? AND idempotency_key = ?
                """,
                (episode_id, idempotency_key),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_event(row)

    def append(self, draft: FocusEventDraft) -> AppendResult:
        identity = _draft_identity(draft)
        with self._lock:
            with self._conn:
                cursor = self._conn.cursor()
                # 1. Check idempotency
                cursor.execute(
                    """
                    SELECT event_id, episode_id, idempotency_key, sequence, event_type,
                           payload_json, occurred_at, previous_event_hash, event_hash,
                           domain_contract_version, schema_version, idempotency_identity
                    FROM focus_events
                    WHERE episode_id = ? AND idempotency_key = ?
                    """,
                    (draft.episode_id, draft.idempotency_key),
                )
                row = cursor.fetchone()
                if row is not None:
                    stored_identity = row[11]
                    if stored_identity != identity:
                        raise EventJournalConflict(
                            "Idempotency key was already used for a different Focus event"
                        )
                    return AppendResult(event=self._row_to_event(row), appended=False)

                # 2. Get current sequence and last hash
                cursor.execute(
                    """
                    SELECT sequence, event_hash
                    FROM focus_events
                    WHERE episode_id = ?
                    ORDER BY sequence DESC
                    LIMIT 1
                    """,
                    (draft.episode_id,),
                )
                last_row = cursor.fetchone()
                current_sequence = last_row[0] if last_row else 0
                previous_hash = last_row[1] if last_row else GENESIS_HASH

                # 3. Concurrency sequence check
                if draft.expected_previous_sequence != current_sequence:
                    raise EventJournalConflict(
                        f"Stale Focus stream version: expected previous sequence {draft.expected_previous_sequence}, actual {current_sequence}"
                    )

                sequence = current_sequence + 1
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
                event_hash = compute_event_hash(provisional)
                event = provisional.model_copy(update={"event_hash": event_hash})

                cursor.execute(
                    """
                    INSERT INTO focus_events (
                        episode_id, sequence, event_id, idempotency_key,
                        idempotency_identity, event_type, payload_json,
                        occurred_at, previous_event_hash, event_hash,
                        domain_contract_version, schema_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.episode_id,
                        event.sequence,
                        event.event_id,
                        event.idempotency_key,
                        identity,
                        event.event_type.value,
                        json.dumps(event.payload),
                        event.occurred_at.isoformat(),
                        event.previous_event_hash,
                        event.event_hash,
                        event.domain_contract_version,
                        event.schema_version,
                    ),
                )
                return AppendResult(event=event, appended=True)

    def list_events(self, episode_id: str, *, after_sequence: int = 0) -> List[FocusEvent]:
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT event_id, episode_id, idempotency_key, sequence, event_type,
                       payload_json, occurred_at, previous_event_hash, event_hash,
                       domain_contract_version, schema_version, idempotency_identity
                FROM focus_events
                WHERE episode_id = ? AND sequence > ?
                ORDER BY sequence ASC
                """,
                (episode_id, after_sequence),
            )
            return [self._row_to_event(row) for row in cursor.fetchall()]

    def last_event(self, episode_id: str) -> Optional[FocusEvent]:
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT event_id, episode_id, idempotency_key, sequence, event_type,
                       payload_json, occurred_at, previous_event_hash, event_hash,
                       domain_contract_version, schema_version, idempotency_identity
                FROM focus_events
                WHERE episode_id = ?
                ORDER BY sequence DESC
                LIMIT 1
                """,
                (episode_id,),
            )
            row = cursor.fetchone()
            return self._row_to_event(row) if row else None

    def get_event(self, episode_id: str, sequence: int) -> Optional[FocusEvent]:
        if sequence < 1:
            return None
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT event_id, episode_id, idempotency_key, sequence, event_type,
                       payload_json, occurred_at, previous_event_hash, event_hash,
                       domain_contract_version, schema_version, idempotency_identity
                FROM focus_events
                WHERE episode_id = ? AND sequence = ?
                """,
                (episode_id, sequence),
            )
            row = cursor.fetchone()
            return self._row_to_event(row) if row else None

    def episode_ids(self) -> List[str]:
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute("SELECT DISTINCT episode_id FROM focus_events ORDER BY episode_id ASC")
            return [row[0] for row in cursor.fetchall()]

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    @staticmethod
    def _row_to_event(row: tuple) -> FocusEvent:
        return FocusEvent(
            event_id=row[0],
            episode_id=row[1],
            idempotency_key=row[2],
            sequence=row[3],
            event_type=FocusEventType(row[4]),
            payload=json.loads(row[5]),
            occurred_at=datetime.fromisoformat(row[6]),
            previous_event_hash=row[7],
            event_hash=row[8],
            domain_contract_version=row[9],
            schema_version=row[10],
        )


class SQLiteFocusSnapshotStore:
    """ACID-compliant SQLite snapshot store."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            isolation_level=None,
        )
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS focus_snapshots (
                        episode_id TEXT PRIMARY KEY,
                        last_sequence INTEGER NOT NULL,
                        journal_head_hash TEXT NOT NULL,
                        state_json TEXT NOT NULL,
                        state_hash TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )

    def get(self, episode_id: str) -> Optional[FocusEpisodeSnapshotRecord]:
        with self._lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                SELECT episode_id, last_sequence, journal_head_hash, state_json, state_hash, created_at
                FROM focus_snapshots
                WHERE episode_id = ?
                """,
                (episode_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            from .decision_pipeline import FocusEpisodeState
            return FocusEpisodeSnapshotRecord(
                episode_id=row[0],
                last_sequence=row[1],
                journal_head_hash=row[2],
                state=FocusEpisodeState.model_validate_json(row[3]),
                state_hash=row[4],
                created_at=datetime.fromisoformat(row[5]),
            )

    def put(self, snapshot: FocusEpisodeSnapshotRecord) -> None:
        with self._lock:
            with self._conn:
                cursor = self._conn.cursor()
                cursor.execute(
                    """
                    SELECT last_sequence, journal_head_hash, state_hash
                    FROM focus_snapshots
                    WHERE episode_id = ?
                    """,
                    (snapshot.episode_id,),
                )
                existing = cursor.fetchone()
                if existing is not None:
                    ex_seq, ex_head, ex_state = existing
                    if snapshot.last_sequence < ex_seq:
                        raise SnapshotConflict("Snapshot sequence cannot move backwards")
                    if snapshot.last_sequence == ex_seq and (
                        snapshot.journal_head_hash != ex_head or snapshot.state_hash != ex_state
                    ):
                        raise SnapshotConflict("Same-sequence snapshot cannot change content")

                cursor.execute(
                    """
                    INSERT INTO focus_snapshots (
                        episode_id, last_sequence, journal_head_hash, state_json, state_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(episode_id) DO UPDATE SET
                        last_sequence=excluded.last_sequence,
                        journal_head_hash=excluded.journal_head_hash,
                        state_json=excluded.state_json,
                        state_hash=excluded.state_hash,
                        created_at=excluded.created_at
                    """,
                    (
                        snapshot.episode_id,
                        snapshot.last_sequence,
                        snapshot.journal_head_hash,
                        snapshot.state.model_dump_json(),
                        snapshot.state_hash,
                        snapshot.created_at.isoformat(),
                    ),
                )

    def close(self) -> None:
        with self._lock:
            self._conn.close()
