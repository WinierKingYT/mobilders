"""Focus Domain Telemetry, Metrics, and Dead-Letter Audit Logging.

Provides Prometheus/OpenTelemetry-compatible counters, latency timers,
and dead-letter audit loggers for the event-sourced Focus kernel.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import threading
import time
from typing import Any, Dict, List, Mapping, Optional


class FocusMetrics:
    """Thread-safe metrics registry and dead-letter security audit store."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._commands: Dict[str, int] = defaultdict(int)
            self._judgments: Dict[str, int] = defaultdict(int)
            self._decisions: Dict[str, int] = defaultdict(int)
            self._idempotency_hits: int = 0
            self._optimistic_conflicts: int = 0
            self._latency_sum_ms: Dict[str, float] = defaultdict(float)
            self._latency_count: Dict[str, int] = defaultdict(int)
            self._dead_letter_log: List[Dict[str, Any]] = []

    def record_command(self, command: str, outcome: str, duration_ms: float = 0.0) -> None:
        with self._lock:
            key = f"{command}:{outcome}"
            self._commands[key] += 1
            self._latency_sum_ms[command] += duration_ms
            self._latency_count[command] += 1

    def record_judgment(self, judgment: str) -> None:
        with self._lock:
            self._judgments[str(judgment)] += 1

    def record_decision(self, action: str) -> None:
        with self._lock:
            self._decisions[str(action)] += 1

    def record_idempotency_hit(self) -> None:
        with self._lock:
            self._idempotency_hits += 1

    def record_conflict(self) -> None:
        with self._lock:
            self._optimistic_conflicts += 1

    def record_audit_event(
        self,
        event_type: str,
        details: Mapping[str, Any],
        *,
        severity: str = "WARNING",
    ) -> None:
        """Record an immutable audit event for dead-letter analysis (e.g. sequence conflict, rate limit)."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": dict(details),
        }
        with self._lock:
            self._dead_letter_log.append(entry)
            # Bound audit log to last 1000 events to prevent unbounded growth
            if len(self._dead_letter_log) > 1000:
                self._dead_letter_log = self._dead_letter_log[-1000:]

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            avg_latency = {}
            for cmd, count in self._latency_count.items():
                avg_latency[cmd] = round(self._latency_sum_ms[cmd] / count, 2) if count > 0 else 0.0

            return {
                "commands": dict(self._commands),
                "judgments": dict(self._judgments),
                "decisions": dict(self._decisions),
                "idempotency_hits": self._idempotency_hits,
                "optimistic_conflicts": self._optimistic_conflicts,
                "average_latency_ms": avg_latency,
                "dead_letter_audit_count": len(self._dead_letter_log),
                "recent_audit_events": list(self._dead_letter_log[-10:]),
            }


class TimedOperation:
    """Context manager for measuring operation duration in milliseconds."""

    def __init__(self, metrics: FocusMetrics, command: str) -> None:
        self.metrics = metrics
        self.command = command
        self.outcome = "SUCCESS"
        self._start = 0.0

    def __enter__(self) -> TimedOperation:
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration_ms = (time.perf_counter() - self._start) * 1000.0
        if exc_type is not None:
            self.outcome = exc_type.__name__
        self.metrics.record_command(self.command, self.outcome, duration_ms)


_global_metrics = FocusMetrics()


def get_focus_metrics() -> FocusMetrics:
    return _global_metrics
