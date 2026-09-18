"""Focus Domain Canary Orchestration, Rollout State Machine, and Health Guard.

Implements staged canary rollout (0% -> 5% -> 25% -> 100%), automated health evaluation,
and safety rollback triggers for production deployment readiness.
"""

from __future__ import annotations

from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .metrics import FocusMetrics, get_focus_metrics


class CanaryStage(str, Enum):
    STAGE_0_DISABLED = "STAGE_0_DISABLED"      # 0% traffic admitted
    STAGE_1_INITIAL = "STAGE_1_INITIAL"        # 5% initial cohort observation
    STAGE_2_EXPANDED = "STAGE_2_EXPANDED"      # 25% expanded cohort observation
    STAGE_3_FULL = "STAGE_3_FULL"              # 100% full production traffic

    @property
    def percentage(self) -> int:
        mapping = {
            CanaryStage.STAGE_0_DISABLED: 0,
            CanaryStage.STAGE_1_INITIAL: 5,
            CanaryStage.STAGE_2_EXPANDED: 25,
            CanaryStage.STAGE_3_FULL: 100,
        }
        return mapping[self]

    def next_stage(self) -> Optional[CanaryStage]:
        order = [
            CanaryStage.STAGE_0_DISABLED,
            CanaryStage.STAGE_1_INITIAL,
            CanaryStage.STAGE_2_EXPANDED,
            CanaryStage.STAGE_3_FULL,
        ]
        idx = order.index(self)
        if idx + 1 < len(order):
            return order[idx + 1]
        return None


class CanaryHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    BREACHED = "BREACHED"


class CanaryHealthReport(BaseModel):
    status: CanaryHealthStatus
    total_commands: int
    conflict_rate: float
    error_rate: float
    max_average_latency_ms: float
    violations: List[str] = Field(default_factory=list)


class CanaryHealthPolicy(BaseModel):
    max_conflict_rate: float = 0.05           # Max 5% optimistic locking conflicts
    max_error_rate: float = 0.001            # Max 0.1% unexpected system errors
    max_average_latency_ms: float = 100.0     # Max 100ms average execution latency
    min_commands_for_evaluation: int = 5      # Minimum sample size before evaluating breaches

    def evaluate(self, metrics_summary: Dict[str, Any]) -> CanaryHealthReport:
        commands = metrics_summary.get("commands", {})
        total_commands = sum(commands.values())
        conflicts = metrics_summary.get("optimistic_conflicts", 0)

        # Count errors (outcomes other than SUCCESS)
        error_commands = sum(
            count for key, count in commands.items() if not key.endswith(":SUCCESS")
        )

        conflict_rate = (conflicts / total_commands) if total_commands > 0 else 0.0
        error_rate = (error_commands / total_commands) if total_commands > 0 else 0.0

        latencies = metrics_summary.get("average_latency_ms", {})
        max_lat = max(latencies.values()) if latencies else 0.0

        violations: List[str] = []

        if total_commands >= self.min_commands_for_evaluation:
            if conflict_rate > self.max_conflict_rate:
                violations.append(
                    f"Conflict rate {conflict_rate:.2%} exceeds threshold {self.max_conflict_rate:.2%}"
                )
            if error_rate > self.max_error_rate:
                violations.append(
                    f"Error rate {error_rate:.2%} exceeds threshold {self.max_error_rate:.2%}"
                )
            if max_lat > self.max_average_latency_ms:
                violations.append(
                    f"Max latency {max_lat:.1f}ms exceeds threshold {self.max_average_latency_ms:.1f}ms"
                )

        if violations:
            status = CanaryHealthStatus.BREACHED
        elif total_commands < self.min_commands_for_evaluation:
            status = CanaryHealthStatus.HEALTHY
        else:
            status = CanaryHealthStatus.HEALTHY

        return CanaryHealthReport(
            status=status,
            total_commands=total_commands,
            conflict_rate=round(conflict_rate, 4),
            error_rate=round(error_rate, 4),
            max_average_latency_ms=round(max_lat, 2),
            violations=violations,
        )


class CanaryOrchestrator:
    """Manages canary rollout progression with automated health gating and rollback."""

    def __init__(
        self,
        initial_stage: CanaryStage = CanaryStage.STAGE_0_DISABLED,
        policy: Optional[CanaryHealthPolicy] = None,
        metrics: Optional[FocusMetrics] = None,
    ) -> None:
        self.stage = initial_stage
        self.policy = policy or CanaryHealthPolicy()
        self.metrics = metrics or get_focus_metrics()
        self.kill_switch: bool = False
        self.rollback_history: List[Dict[str, Any]] = []

    @property
    def percentage(self) -> int:
        if self.kill_switch:
            return 0
        return self.stage.percentage

    def is_request_admitted(self, client_key: str) -> bool:
        if self.kill_switch or self.percentage <= 0:
            return False
        if self.percentage >= 100:
            return True
        digest = hashlib.sha256(client_key.encode("utf-8")).hexdigest()
        return (int(digest[:8], 16) % 100) < self.percentage

    def evaluate_health(self) -> CanaryHealthReport:
        summary = self.metrics.get_summary()
        return self.policy.evaluate(summary)

    def advance_stage(self) -> CanaryStage:
        """Promote canary to the next stage if and only if health policy is satisfied."""
        if self.kill_switch:
            raise ValueError("Cannot advance canary stage while kill switch is active")

        report = self.evaluate_health()
        if report.status == CanaryHealthStatus.BREACHED:
            raise ValueError(
                f"Cannot advance canary stage: health policy breached ({', '.join(report.violations)})"
            )

        next_st = self.stage.next_stage()
        if next_st is not None:
            self.stage = next_st
            self.metrics.record_audit_event(
                "CANARY_STAGE_PROMOTED",
                {"new_stage": self.stage.value, "percentage": self.percentage},
                severity="INFO",
            )
        return self.stage

    def rollback(self, reason: str) -> None:
        """Trigger an emergency rollback to STAGE_0_DISABLED and engage safety kill switch."""
        old_stage = self.stage
        self.stage = CanaryStage.STAGE_0_DISABLED
        self.kill_switch = True
        record = {
            "reason": reason,
            "previous_stage": old_stage.value,
            "action": "ROLLBACK_AND_KILL_SWITCH",
        }
        self.rollback_history.append(record)
        self.metrics.record_audit_event(
            "CANARY_ROLLBACK_TRIGGERED",
            record,
            severity="CRITICAL",
        )
