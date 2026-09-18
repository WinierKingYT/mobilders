from __future__ import annotations

import hashlib
import os
import threading
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from .application import (
    FocusApplicationError,
    FocusAttemptInputKind,
    FocusCommandResult,
    FocusEpisodeView,
    FocusServiceFacade,
)
from .learner_profile import MultiEpisodeLearnerProfile, ReEntryDiagnostic
from .metrics import TimedOperation, get_focus_metrics
from .persistence import (
    EpisodeNotFound,
    EventJournalConflict,
    EventJournalCorruption,
    SnapshotConflict,
)


class StartFocusEpisodeRequest(BaseModel):
    episode_id: str = Field(min_length=1, max_length=128)
    topic_id: str = Field(default="CT-QF1", min_length=1, max_length=32)
    a: Optional[int] = None
    b: int = 5
    c: int = 6
    comparator: Optional[str] = "<="
    divisor_root: Optional[int] = None


# Backwards compatibility alias
StartCTQF1EpisodeRequest = StartFocusEpisodeRequest


class SubmitFocusAttemptRequest(BaseModel):
    input_kind: FocusAttemptInputKind
    input: Any

    @field_validator("input")
    @classmethod
    def validate_input_size(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Input string exceeds maximum allowable length of 500 characters")
        if isinstance(v, (list, tuple)) and len(v) > 20:
            raise ValueError("Input sequence exceeds maximum allowable length of 20 items")
        if isinstance(v, dict) and len(v) > 20:
            raise ValueError("Input dictionary exceeds maximum allowable size of 20 entries")
        return v


class SubmitProbeResponseRequest(BaseModel):
    probe_id: str = Field(min_length=1, max_length=64)
    response_code: str = Field(min_length=1, max_length=128)


class SubmitRepairWorkRequest(BaseModel):
    raw_work: Any

    @field_validator("raw_work")
    @classmethod
    def validate_work_size(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Raw work string exceeds maximum allowable length of 500 characters")
        if isinstance(v, (list, tuple)) and len(v) > 20:
            raise ValueError("Raw work sequence exceeds maximum allowable length of 20 items")
        return v


class SubmitSelfCorrectionRequest(BaseModel):
    input_kind: FocusAttemptInputKind
    input: Any

    @field_validator("input")
    @classmethod
    def validate_input_size(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Input string exceeds maximum allowable length of 500 characters")
        if isinstance(v, (list, tuple)) and len(v) > 20:
            raise ValueError("Input sequence exceeds maximum allowable length of 20 items")
        if isinstance(v, dict) and len(v) > 20:
            raise ValueError("Input dictionary exceeds maximum allowable size of 20 entries")
        return v


class SubmitTransferWorkRequest(BaseModel):
    raw_work: Any

    @field_validator("raw_work")
    @classmethod
    def validate_work_size(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Raw work string exceeds maximum allowable length of 500 characters")
        if isinstance(v, (list, tuple)) and len(v) > 20:
            raise ValueError("Raw work sequence exceeds maximum allowable length of 20 items")
        return v


class ScheduleRetestRequest(BaseModel):
    target_kc: str = Field(min_length=1, max_length=16)
    barrier_id: Optional[str] = None


class SubmitDelayedRetestWorkRequest(BaseModel):
    target_kc: str = Field(min_length=1, max_length=16)
    raw_work: Any
    barrier_id: Optional[str] = None

    @field_validator("raw_work")
    @classmethod
    def validate_work_size(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Raw work string exceeds maximum allowable length of 500 characters")
        if isinstance(v, (list, tuple)) and len(v) > 20:
            raise ValueError("Raw work sequence exceeds maximum allowable length of 20 items")
        return v


def _http_error(exc: Exception) -> HTTPException:
    metrics = get_focus_metrics()
    if isinstance(exc, FocusApplicationError):
        return HTTPException(
            status_code=422,
            detail={"code": "FOCUS_UNSUPPORTED_TASK", "message": str(exc)},
        )
    if isinstance(exc, EpisodeNotFound):
        return HTTPException(
            status_code=404,
            detail={"code": "FOCUS_EPISODE_NOT_FOUND", "message": str(exc)},
        )
    if isinstance(exc, EventJournalConflict):
        metrics.record_conflict()
        metrics.record_audit_event("STALE_SEQUENCE_CONFLICT", {"message": str(exc)})
        return HTTPException(
            status_code=409,
            detail={"code": "FOCUS_STREAM_CONFLICT", "message": str(exc)},
        )
    if isinstance(exc, (EventJournalCorruption, SnapshotConflict)):
        metrics.record_audit_event("JOURNAL_CORRUPTION", {"message": str(exc)}, severity="CRITICAL")
        return HTTPException(
            status_code=500,
            detail={"code": "FOCUS_PERSISTENCE_INTEGRITY_ERROR", "message": str(exc)},
        )
    if isinstance(exc, ValueError):
        return HTTPException(
            status_code=409,
            detail={"code": "FOCUS_INVALID_TRANSITION", "message": str(exc)},
        )
    return HTTPException(
        status_code=500,
        detail={"code": "FOCUS_INTERNAL_ERROR", "message": "Unexpected Focus error"},
    )


def is_canary_admitted(key: str, percentage: int) -> bool:
    if percentage <= 0:
        return False
    if percentage >= 100:
        return True
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return (int(digest[:8], 16) % 100) < percentage


def _record_result_metrics(result: FocusCommandResult) -> None:
    metrics = get_focus_metrics()
    if result.judgment:
        metrics.record_judgment(result.judgment.value)
    if result.decision:
        metrics.record_decision(result.decision.action.value)


def create_focus_router(
    *,
    service: Optional[FocusServiceFacade] = None,
    enabled: bool = True,
    canary_percentage: int = 100,
    kill_switch: bool = False,
) -> APIRouter:
    facade = service or FocusServiceFacade()
    metrics = get_focus_metrics()

    # Rate limiting: maximum 60 requests per minute per client IP / token
    client_request_history: Dict[str, List[float]] = {}
    rate_limit_lock = threading.Lock()

    def _verify_gate(
        request: Request,
        authorization: Optional[str] = Header(None, alias="Authorization"),
        idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    ) -> None:
        # Telemetry & metrics endpoints are always accessible for system observability
        if request.url.path.endswith("/metrics"):
            return

        if kill_switch:
            metrics.record_audit_event("KILL_SWITCH_ACTIVE", {"action": "rejected"})
            raise HTTPException(
                status_code=503,
                detail={"code": "FOCUS_KILL_SWITCH_ACTIVE", "message": "Focus kernel is disabled via emergency kill switch"},
            )
        if not enabled and canary_percentage <= 0:
            raise HTTPException(
                status_code=503,
                detail={"code": "FOCUS_DISABLED", "message": "Focus feature is currently disabled"},
            )
        raw_key = authorization or idempotency_key or "anonymous_client"
        key = raw_key[7:].strip() if raw_key.startswith("Bearer ") else raw_key.strip()
        if canary_percentage < 100:
            if not is_canary_admitted(key, canary_percentage):
                raise HTTPException(
                    status_code=503,
                    detail={"code": "FOCUS_CANARY_EXCLUDED", "message": "Request not allocated to Focus v1 canary cohort"},
                )
        # Check rate limit
        now = time.time()
        client_key = key
        with rate_limit_lock:
            history = client_request_history.setdefault(client_key, [])
            # Filter out entries older than 60s
            history = [t for t in history if now - t < 60.0]
            client_request_history[client_key] = history
            if len(history) >= 60:
                metrics.record_audit_event("RATE_LIMIT_EXCEEDED", {"client": client_key})
                raise HTTPException(
                    status_code=429,
                    detail={"code": "FOCUS_RATE_LIMIT_EXCEEDED", "message": "Rate limit of 60 requests/minute exceeded"},
                )
            history.append(now)

    router = APIRouter(
        prefix="/focus/v1",
        tags=["Focus V1 Alpha"],
        dependencies=[Depends(_verify_gate)],
    )

    @router.get("/metrics")
    def get_metrics_summary() -> Dict[str, Any]:
        return metrics.get_summary()

    @router.post("/episodes", response_model=FocusCommandResult, status_code=201)
    def start_episode(
        body: StartFocusEpisodeRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
    ) -> FocusCommandResult:
        with TimedOperation(metrics, "start_episode"):
            try:
                res = facade.start_episode(
                    episode_id=body.episode_id,
                    topic_id=body.topic_id,
                    a=body.a,
                    b=body.b,
                    c=body.c,
                    divisor_root=body.divisor_root,
                    comparator=body.comparator or "<=",
                    idempotency_key=idempotency_key,
                )
                _record_result_metrics(res)
                return res
            except Exception as exc:
                raise _http_error(exc) from exc

    @router.get("/episodes/{episode_id}", response_model=FocusEpisodeView)
    def get_episode(episode_id: str) -> FocusEpisodeView:
        with TimedOperation(metrics, "get_episode"):
            try:
                return facade.get_episode(episode_id)
            except Exception as exc:
                raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/attempts",
        response_model=FocusCommandResult,
    )
    def submit_attempt(
        episode_id: str,
        body: SubmitFocusAttemptRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        with TimedOperation(metrics, "submit_attempt"):
            try:
                res = facade.submit_attempt(
                    episode_id=episode_id,
                    input_kind=body.input_kind,
                    raw_input=body.input,
                    idempotency_key=idempotency_key,
                    expected_previous_sequence=expected_sequence,
                )
                _record_result_metrics(res)
                return res
            except Exception as exc:
                raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/probe-responses",
        response_model=FocusCommandResult,
    )
    def submit_probe_response(
        episode_id: str,
        body: SubmitProbeResponseRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            return facade.apply_probe_response(
                episode_id=episode_id,
                probe_id=body.probe_id,
                response_code=body.response_code,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/repair/begin",
        response_model=FocusCommandResult,
    )
    def begin_repair(
        episode_id: str,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            return facade.begin_current_repair(
                episode_id=episode_id,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/repair/work",
        response_model=FocusCommandResult,
    )
    def submit_repair_work(
        episode_id: str,
        body: SubmitRepairWorkRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            return facade.submit_repair_work(
                episode_id=episode_id,
                raw_work=body.raw_work,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/repair/self-correction",
        response_model=FocusCommandResult,
    )
    def submit_self_correction(
        episode_id: str,
        body: SubmitSelfCorrectionRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            return facade.submit_original_self_correction(
                episode_id=episode_id,
                input_kind=body.input_kind,
                raw_input=body.input,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/repair/transfer",
        response_model=FocusCommandResult,
    )
    def submit_transfer_work(
        episode_id: str,
        body: SubmitTransferWorkRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            return facade.submit_transfer_work(
                episode_id=episode_id,
                raw_work=body.raw_work,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/retest/schedule",
        response_model=FocusCommandResult,
    )
    def schedule_retest(
        episode_id: str,
        body: ScheduleRetestRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            from .models import KCId
            target_kc = KCId(body.target_kc)
            return facade.schedule_retest(
                episode_id=episode_id,
                target_kc=target_kc,
                barrier_id=body.barrier_id,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.post(
        "/episodes/{episode_id}/retest/submit",
        response_model=FocusCommandResult,
    )
    def submit_delayed_retest_work(
        episode_id: str,
        body: SubmitDelayedRetestWorkRequest,
        idempotency_key: str = Header(..., alias="Idempotency-Key"),
        expected_sequence: int = Header(
            ...,
            ge=1,
            alias="X-Focus-Expected-Sequence",
        ),
    ) -> FocusCommandResult:
        try:
            from .models import KCId
            target_kc = KCId(body.target_kc)
            return facade.submit_delayed_retest_work(
                episode_id=episode_id,
                target_kc=target_kc,
                raw_work=body.raw_work,
                barrier_id=body.barrier_id,
                idempotency_key=idempotency_key,
                expected_previous_sequence=expected_sequence,
            )
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.get("/profile", response_model=MultiEpisodeLearnerProfile)
    def get_learner_profile() -> MultiEpisodeLearnerProfile:
        try:
            return facade.get_multi_episode_learner_profile()
        except Exception as exc:
            raise _http_error(exc) from exc

    @router.get("/diagnostics/re-entry/{target_kc}", response_model=ReEntryDiagnostic)
    def diagnose_re_entry(target_kc: str) -> ReEntryDiagnostic:
        try:
            from .models import KCId
            kc = KCId(target_kc)
            return facade.diagnose_session_re_entry(target_kc=kc)
        except Exception as exc:
            raise _http_error(exc) from exc

    return router


def focus_v1_enabled_from_env() -> bool:
    return os.getenv("FOCUS_V1_ENABLED", "false").strip().lower() == "true"


def install_focus_api(
    app: FastAPI,
    *,
    enabled: bool,
    canary_percentage: Optional[int] = None,
    kill_switch: bool = False,
    service: Optional[FocusServiceFacade] = None,
) -> None:
    """Feature-flagged and canary-aware integration point.

    When disabled and canary is 0, no Focus routes are registered at all.
    """
    pct = (100 if enabled else 0) if canary_percentage is None else canary_percentage
    if not enabled and pct <= 0:
        return
    app.include_router(
        create_focus_router(
            service=service,
            enabled=enabled,
            canary_percentage=pct,
            kill_switch=kill_switch,
        )
    )
