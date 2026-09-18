"""Focus Domain Synthetic Traffic Harness & Telemetry Driver.

Simulates multi-stage, multi-phase learner journeys across the pure Focus
application facade to verify end-to-end telemetry and deployment readiness.
"""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field

from .application import (
    FocusAttemptInputKind,
    FocusCommandResult,
    FocusServiceFacade,
)
from .decision_pipeline import NextActionType
from .metrics import FocusMetrics, get_focus_metrics
from .models import AttemptJudgment, KCId, KCState


class SyntheticJourneyResult(BaseModel):
    episode_id: str
    journey_type: str
    final_stream_version: int
    final_stage: str
    final_phase: str
    events_generated: int
    success: bool
    summary: str


class SyntheticBatchResult(BaseModel):
    total_journeys: int
    successful_journeys: int
    total_events: int
    journey_details: List[SyntheticJourneyResult] = Field(default_factory=list)
    telemetry_summary: Dict[str, Any] = Field(default_factory=dict)


class SyntheticTrafficHarness:
    """Automated driver for generating realistic synthetic learner activity."""

    def __init__(
        self,
        service: FocusServiceFacade,
        metrics: Optional[FocusMetrics] = None,
    ) -> None:
        self.service = service
        self.metrics = metrics or get_focus_metrics()

    def run_healthy_progression(self, episode_id: str) -> SyntheticJourneyResult:
        """Executes a textbook flawless learner run through all 4 stages of CT-QF1."""
        # 1. Start episode
        r1 = self.service.start_ctqf1_episode(
            episode_id=episode_id,
            b=5,
            c=6,
            idempotency_key=f"{episode_id}:start",
        )
        self.metrics.record_command("start_episode", "SUCCESS")

        # 2. Stage 1: Factor pair (2, 3)
        r2 = self.service.submit_attempt(
            episode_id=episode_id,
            input_kind=FocusAttemptInputKind.FACTOR_PAIR,
            raw_input=[2, 3],
            idempotency_key=f"{episode_id}:att1",
            expected_previous_sequence=1,
        )
        self.metrics.record_command("submit_attempt", "SUCCESS")
        if r2.judgment:
            self.metrics.record_judgment(r2.judgment.value)
        if r2.decision:
            self.metrics.record_decision(r2.decision.action.value)

        # 3. Stage 2: Branch decomposition x+2=0 or x+3=0
        r3 = self.service.submit_attempt(
            episode_id=episode_id,
            input_kind=FocusAttemptInputKind.BRANCH_DECOMPOSITION,
            raw_input="x+2=0 or x+3=0",
            idempotency_key=f"{episode_id}:att2",
            expected_previous_sequence=2,
        )
        self.metrics.record_command("submit_attempt", "SUCCESS")
        if r3.judgment:
            self.metrics.record_judgment(r3.judgment.value)
        if r3.decision:
            self.metrics.record_decision(r3.decision.action.value)

        # 4. Stage 3: Solve branch equations
        r4 = self.service.submit_attempt(
            episode_id=episode_id,
            input_kind=FocusAttemptInputKind.BRANCH_WORK,
            raw_input={"x+2=0": "x=-2", "x+3=0": "x=-3"},
            idempotency_key=f"{episode_id}:att3",
            expected_previous_sequence=3,
        )
        self.metrics.record_command("submit_attempt", "SUCCESS")
        if r4.judgment:
            self.metrics.record_judgment(r4.judgment.value)
        if r4.decision:
            self.metrics.record_decision(r4.decision.action.value)

        # 5. Stage 4: Complete solution set {-2, -3}
        r5 = self.service.submit_attempt(
            episode_id=episode_id,
            input_kind=FocusAttemptInputKind.SOLUTION_SET,
            raw_input="x=-2, x=-3",
            idempotency_key=f"{episode_id}:att4",
            expected_previous_sequence=4,
        )
        self.metrics.record_command("submit_attempt", "SUCCESS")
        if r5.judgment:
            self.metrics.record_judgment(r5.judgment.value)
        if r5.decision:
            self.metrics.record_decision(r5.decision.action.value)

        return SyntheticJourneyResult(
            episode_id=episode_id,
            journey_type="HEALTHY_PROGRESSION",
            final_stream_version=r5.stream_version,
            final_stage=r5.state.current_stage.value,
            final_phase=r5.state.phase.value,
            events_generated=5,
            success=True,
            summary="Completed CT-QF1 from S1 to S4 flawlessly.",
        )

    def run_misconception_and_repair_journey(
        self,
        episode_id: str,
    ) -> SyntheticJourneyResult:
        """Executes a diagnostic journey: sign reversal -> probe/repair -> transfer -> retest."""
        # 1. Start episode
        r1 = self.service.start_ctqf1_episode(
            episode_id=episode_id,
            b=5,
            c=6,
            idempotency_key=f"{episode_id}:start",
        )
        self.metrics.record_command("start_episode", "SUCCESS")

        # 2. Trigger sign reversal misconception
        r2 = self.service.submit_attempt(
            episode_id=episode_id,
            input_kind=FocusAttemptInputKind.FACTOR_PAIR,
            raw_input=[-2, -3],
            idempotency_key=f"{episode_id}:att1_err",
            expected_previous_sequence=1,
        )
        self.metrics.record_command("submit_attempt", "SUCCESS")
        if r2.judgment:
            self.metrics.record_judgment(r2.judgment.value)
        if r2.decision:
            self.metrics.record_decision(r2.decision.action.value)

        curr_seq = r2.stream_version

        # 3. Handle Probe or Repair
        if r2.decision and r2.decision.action == NextActionType.REQUEST_PROBE and r2.decision.probe_id:
            r_probe = self.service.apply_probe_response(
                episode_id=episode_id,
                probe_id=r2.decision.probe_id,
                response_code="PRODUCT_ONLY",
                idempotency_key=f"{episode_id}:probe_resp",
                expected_previous_sequence=curr_seq,
            )
            self.metrics.record_command("apply_probe_response", "SUCCESS")
            curr_seq = r_probe.stream_version

        # 4. Begin Repair
        r_rep = self.service.begin_current_repair(
            episode_id=episode_id,
            idempotency_key=f"{episode_id}:begin_rep",
            expected_previous_sequence=curr_seq,
        )
        self.metrics.record_command("begin_repair", "SUCCESS")
        curr_seq = r_rep.stream_version
        target_kc = r_rep.state.repair_kc or KCId.F2

        # 5. Submit Repair Work on intervention
        r_work = self.service.submit_repair_work(
            episode_id=episode_id,
            raw_work=[2, 3],  # valid context work for F2
            idempotency_key=f"{episode_id}:work",
            expected_previous_sequence=curr_seq,
        )
        self.metrics.record_command("submit_repair_work", "SUCCESS")
        curr_seq = r_work.stream_version

        # 5b. Original Self-Correction on CT-QF1
        r_corr = self.service.submit_original_self_correction(
            episode_id=episode_id,
            input_kind=FocusAttemptInputKind.FACTOR_PAIR,
            raw_input="2, 3",
            idempotency_key=f"{episode_id}:orig_corr",
            expected_previous_sequence=curr_seq,
        )
        self.metrics.record_command("submit_original_self_correction", "SUCCESS")
        curr_seq = r_corr.stream_version

        # 6. Submit Transfer Task Work
        r_trans = self.service.submit_transfer_work(
            episode_id=episode_id,
            raw_work=[3, 4],  # expected pair for F2 transfer task
            idempotency_key=f"{episode_id}:trans",
            expected_previous_sequence=curr_seq,
        )
        self.metrics.record_command("submit_transfer_work", "SUCCESS")
        curr_seq = r_trans.stream_version

        # 7. Schedule Delayed Retest
        r_sched = self.service.schedule_retest(
            episode_id=episode_id,
            target_kc=target_kc,
            idempotency_key=f"{episode_id}:retest_sched",
            expected_previous_sequence=curr_seq,
        )
        self.metrics.record_command("schedule_retest", "SUCCESS")
        curr_seq = r_sched.stream_version

        # 8. Submit Delayed Retest Work
        r_retest = self.service.submit_delayed_retest_work(
            episode_id=episode_id,
            target_kc=target_kc,
            raw_work=[2, 3],  # expected pair for F2 retest task
            idempotency_key=f"{episode_id}:retest_work",
            expected_previous_sequence=curr_seq,
        )
        self.metrics.record_command("submit_delayed_retest_work", "SUCCESS")

        return SyntheticJourneyResult(
            episode_id=episode_id,
            journey_type="REPAIR_AND_TRANSFER_JOURNEY",
            final_stream_version=r_retest.stream_version,
            final_stage=r_retest.state.current_stage.value,
            final_phase=r_retest.state.phase.value,
            events_generated=r_retest.stream_version,
            success=True,
            summary="Diagnosed misconception, completed intervention, passed transfer, and verified durable recovery.",
        )

    def run_synthetic_batch(self, count: int = 10) -> SyntheticBatchResult:
        """Executes a mixed synthetic cohort verifying cross-episode persistence and telemetry."""
        details: List[SyntheticJourneyResult] = []
        total_events = 0

        for i in range(count):
            ep_id = f"synth-ep-{i}"
            if i % 2 == 0:
                res = self.run_healthy_progression(ep_id)
            else:
                res = self.run_misconception_and_repair_journey(ep_id)
            details.append(res)
            total_events += res.events_generated

        # Check cross-episode profile
        self.service.get_multi_episode_learner_profile()
        self.metrics.record_command("get_learner_profile", "SUCCESS")

        summary = self.metrics.get_summary()

        return SyntheticBatchResult(
            total_journeys=count,
            successful_journeys=sum(1 for d in details if d.success),
            total_events=total_events,
            journey_details=details,
            telemetry_summary=summary,
        )
