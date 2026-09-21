"""
Cognitive State Repository for Personal Learning Engine.
Implements data access layer matching schema.sql (PostgreSQL 15 DDL)
with Zero-PII compliance and graceful offline fallback.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.connection import PostgresConnectionManager

logger = logging.getLogger("db.repository")


def _ensure_uuid(val: Optional[str]) -> str:
    """Ensures input is a valid UUID string, deterministically converting arbitrary strings via uuid5."""
    if not val:
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(str(val)))
    except (ValueError, AttributeError):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(val)))


class CognitiveStateRepository:
    """
    Repository for student cognitive state, knowledge node mastery,
    session events, and step diagnostics according to schema.sql.
    """

    def __init__(self, connection_manager: PostgresConnectionManager):
        self.connection_manager = connection_manager

    def record_session_step(
        self,
        session_id: str,
        student_uuid: str,
        step_index: int,
        raw_latex: str,
        is_valid: bool,
        latency_ms: float = 0.0,
        detected_bug_id: Optional[str] = None,
        ddm_drift_v: Optional[float] = None,
        ddm_boundary_a: Optional[float] = None,
        affective_state: Optional[str] = "FLOW",
        client_timestamp: Optional[datetime] = None,
        event_type: str = "STEP_SUBMIT",
    ) -> Optional[str]:
        """
        Atomically records a session event and its corresponding step diagnostic
        into session_events and step_diagnostics tables.
        Returns event_id (UUID str) on success, or None if offline/error.
        """
        if not self.connection_manager._pool:
            return None

        event_id = str(uuid.uuid4())
        sid = _ensure_uuid(student_uuid)
        ts = client_timestamp or datetime.now(timezone.utc)

        try:
            with self.connection_manager.get_connection() as conn:
                if conn is None:
                    return None

                with conn.cursor() as cur:
                    # 1. Ensure student state exists first (FK requirement)
                    cur.execute(
                        """
                        INSERT INTO student_cognitive_state (student_uuid)
                        VALUES (%s)
                        ON CONFLICT (student_uuid) DO NOTHING;
                        """,
                        (sid,),
                    )

                    # 2. Insert into session_events
                    cur.execute(
                        """
                        INSERT INTO session_events (
                            event_id, session_id, student_uuid, event_type,
                            step_index, raw_latex, latency_ms, client_timestamp
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """,
                        (
                            event_id,
                            session_id,
                            sid,
                            event_type,
                            step_index,
                            raw_latex,
                            latency_ms,
                            ts,
                        ),
                    )

                    # 3. Insert into step_diagnostics
                    cur.execute(
                        """
                        INSERT INTO step_diagnostics (
                            event_id, is_valid, detected_bug_id,
                            ddm_drift_v, ddm_boundary_a, affective_state
                        ) VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (
                            event_id,
                            is_valid,
                            detected_bug_id,
                            ddm_drift_v,
                            ddm_boundary_a,
                            affective_state,
                        ),
                    )

                return event_id
        except Exception as e:
            logger.warning(f"Failed to record session step to PostgreSQL: {e}")
            return None

    def get_or_create_student_state(
        self,
        student_uuid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves or creates a student's cognitive state row.
        """
        sid = student_uuid or str(uuid.uuid4())
        if not self.connection_manager._pool:
            return {
                "student_uuid": sid,
                "overall_theta": 0.0,
                "standard_error": 1.0,
                "circadian_lock_until": None,
            }

        try:
            with self.connection_manager.get_connection() as conn:
                if conn is None:
                    return {
                        "student_uuid": sid,
                        "overall_theta": 0.0,
                        "standard_error": 1.0,
                        "circadian_lock_until": None,
                    }

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO student_cognitive_state (student_uuid)
                        VALUES (%s)
                        ON CONFLICT (student_uuid) DO UPDATE
                        SET updated_at = CURRENT_TIMESTAMP
                        RETURNING student_uuid, overall_theta, standard_error, circadian_lock_until;
                        """,
                        (sid,),
                    )
                    row = cur.fetchone()
                    if row:
                        return {
                            "student_uuid": str(row[0]),
                            "overall_theta": float(row[1]),
                            "standard_error": float(row[2]),
                            "circadian_lock_until": row[3].isoformat() if row[3] else None,
                        }
        except Exception as e:
            logger.warning(f"Database error in get_or_create_student_state: {e}")

        return {
            "student_uuid": sid,
            "overall_theta": 0.0,
            "standard_error": 1.0,
            "circadian_lock_until": None,
        }

    def update_node_mastery(
        self,
        student_uuid: str,
        node_id: str,
        p_mastery: float,
        fsrs_stability: float = 1.0,
        fsrs_difficulty: float = 5.0,
        next_review_date: Optional[datetime] = None,
    ) -> bool:
        """
        Upserts node mastery with BKT p_mastery and FSRS-4.5 parameters.
        """
        if not self.connection_manager._pool:
            return False

        review_date = next_review_date or datetime.now(timezone.utc)
        sid = _ensure_uuid(student_uuid)
        try:
            with self.connection_manager.get_connection() as conn:
                if conn is None:
                    return False

                with conn.cursor() as cur:
                    # Ensure student exists
                    cur.execute(
                        """
                        INSERT INTO student_cognitive_state (student_uuid)
                        VALUES (%s)
                        ON CONFLICT (student_uuid) DO NOTHING;
                        """,
                        (sid,),
                    )
                    # Upsert node mastery
                    cur.execute(
                        """
                        INSERT INTO node_mastery (
                            student_uuid, node_id, p_mastery,
                            fsrs_stability, fsrs_difficulty, next_review_date
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (student_uuid, node_id) DO UPDATE SET
                            p_mastery = EXCLUDED.p_mastery,
                            fsrs_stability = EXCLUDED.fsrs_stability,
                            fsrs_difficulty = EXCLUDED.fsrs_difficulty,
                            next_review_date = EXCLUDED.next_review_date,
                            updated_at = CURRENT_TIMESTAMP;
                        """,
                        (
                            sid,
                            node_id,
                            p_mastery,
                            fsrs_stability,
                            fsrs_difficulty,
                            review_date,
                        ),
                    )
                return True
        except Exception as e:
            logger.warning(f"Failed to update node mastery in PostgreSQL: {e}")
            return False

    def update_circadian_lock(
        self,
        student_uuid: str,
        lock_until: datetime,
    ) -> bool:
        """
        Sets circadian sleep lock until timestamp on student_cognitive_state.
        """
        if not self.connection_manager._pool:
            return False

        sid = _ensure_uuid(student_uuid)
        try:
            with self.connection_manager.get_connection() as conn:
                if conn is None:
                    return False

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE student_cognitive_state
                        SET circadian_lock_until = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE student_uuid = %s;
                        """,
                        (lock_until, sid),
                    )
                return True
        except Exception as e:
            logger.warning(f"Failed to update circadian lock in PostgreSQL: {e}")
            return False

    def purge_student_data(self, student_uuid: str) -> bool:
        """
        Executes right-to-be-forgotten purge procedure from schema.sql.
        """
        if not self.connection_manager._pool:
            return False

        sid = _ensure_uuid(student_uuid)
        try:
            with self.connection_manager.get_connection() as conn:
                if conn is None:
                    return False

                with conn.cursor() as cur:
                    cur.execute("SELECT purge_student_data(%s);", (sid,))
                return True
        except Exception as e:
            logger.warning(f"Failed to purge student data in PostgreSQL: {e}")
            return False
