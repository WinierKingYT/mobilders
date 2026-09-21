import logging
import math
import time
from typing import Optional, Dict, List, Any
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from app.models.schemas import (
    StepVerificationRequest,
    StepVerificationResponse,
    OfflineBatchReplayRequest,
    OfflineBatchReplayResponse,
    StepPsychometrics,
)
from app.cas.symbolic_engine import (
    SecurityViolationError,
    CASTimeoutError,
)
from app.psychometrics.bkt import IndividualizedBKT
from app.psychometrics.ddm import EZDiffusionSolver
from app.affect.detector import BehaviorObservation
from app.socratic.pipeline import SocraticRequest
from datetime import datetime, timezone
from app.core.logging_config import telemetry_logger
from app.api.deps import (
    cas_engine,
    misconception_detector,
    socratic_pipeline,
    affective_detector,
    db_repository,
    redis_service,
    _IDEMPOTENCY_CACHE,
)

router = APIRouter(tags=["Session"])
logger = logging.getLogger("session_websocket")


@router.post("/api/v1/session/step/verify", response_model=StepVerificationResponse)
async def verify_step(request: StepVerificationRequest) -> StepVerificationResponse:
    """
    Öğrencinin girdiği cebirsel adımı deterministik olarak doğrular.
    Doğru değilse 5 temel bozuk kuralı (Buggy Rules) arar.
    Destekler: client_msg_id ile tam idempotent yanıt önbelleklemesi.
    """
    # 0. İdempotentlik Denetimi: Önceden işlenmiş adım tekrarlanırsa önbellekten dön
    if request.client_msg_id and request.client_msg_id in _IDEMPOTENCY_CACHE:
        cached_resp = _IDEMPOTENCY_CACHE[request.client_msg_id]
        return cached_resp.model_copy(update={"is_replayed": True})

    start_time = time.perf_counter()

    try:
        # 1. Sembolik Eşdeğerlik Denetimi (Örtük çarpma ön-işlemcisi dahil)
        is_equiv, cas_latency, diff_str = cas_engine.verify_equivalence(
            request.user_expression, request.target_equation
        )

        detected_bug = None
        if not is_equiv:
            # 2. Hatalı adımda Bozuk Kural Analizi
            detected_bug = misconception_detector.detect(
                user_step_str=request.user_expression,
                previous_step_str=request.previous_step or request.target_equation,
                target_equation_str=request.target_equation,
            )

        total_latency_ms = (time.perf_counter() - start_time) * 1000.0

        # 3. Psikometri ve Bilişsel Modelleme Hesaplaması (iBKT + Ratcliff DDM)
        current_pl = request.current_p_l if request.current_p_l is not None else 0.20
        post_pl, next_pl = IndividualizedBKT.update_mastery(p_l=current_pl, is_correct=is_equiv)

        ddm_v = None
        ddm_a = None
        ddm_state = None
        if request.elapsed_ms is not None:
            # 15 saniyeden uzun kesintiler DDM hesabından hariç tutulur (Doc 19: Outlier Truncation)
            if 150 <= request.elapsed_ms <= 15000:
                try:
                    step_mrt = request.elapsed_ms / 1000.0
                    step_vrt = 0.04
                    step_pc = 0.85 if is_equiv else 0.15
                    ddm_res = EZDiffusionSolver.solve(mrt=step_mrt, vrt=step_vrt, pc=step_pc)
                    ddm_v = ddm_res.drift_rate
                    ddm_a = ddm_res.boundary_separation
                    ddm_state = ddm_res.cognitive_state
                except Exception:
                    pass
            elif request.elapsed_ms > 15000:
                ddm_state = "outlier_interruption"

        psychometrics = StepPsychometrics(
            bkt_posterior_p_l=round(post_pl, 4),
            bkt_next_p_l=round(next_pl, 4),
            ddm_drift_rate=ddm_v,
            ddm_boundary_separation=ddm_a,
            ddm_cognitive_state=ddm_state,
        )

        telemetry_logger.record_step_event(
            session_id=request.session_id,
            step_index=request.step_number,
            is_correct=is_equiv,
            latency_ms=float(request.elapsed_ms) if request.elapsed_ms is not None else total_latency_ms,
            ddm_v=ddm_v,
            ddm_a=ddm_a,
            affective_state=ddm_state or ("FLOW" if is_equiv else "CONFUSION"),
            circuit_breaker_tripped=False,
            detected_bug_id=detected_bug.bug_id if detected_bug else None,
        )

        # Record to PostgreSQL schema.sql (session_events & step_diagnostics) with offline resilience
        try:
            db_repository.record_session_step(
                session_id=request.session_id,
                student_uuid=request.session_id,
                step_index=request.step_number,
                raw_latex=request.user_expression,
                is_valid=is_equiv,
                latency_ms=float(request.elapsed_ms) if request.elapsed_ms is not None else total_latency_ms,
                detected_bug_id=detected_bug.bug_id if detected_bug else None,
                ddm_drift_v=ddm_v,
                ddm_boundary_a=ddm_a,
                affective_state=ddm_state or ("FLOW" if is_equiv else "CONFUSION"),
                client_timestamp=request.client_timestamp,
            )
        except Exception:
            pass

        resp = StepVerificationResponse(
            is_valid=is_equiv,
            is_target_reached=is_equiv and ("=" in request.user_expression and not ("**2" in request.user_expression or "^2" in request.user_expression)),
            detected_bug=detected_bug,
            canonical_expression=diff_str if is_equiv else None,
            error_message=None,
            analysis_latency_ms=total_latency_ms,
            psychometrics=psychometrics,
            is_replayed=False,
        )

        if request.client_msg_id:
            _IDEMPOTENCY_CACHE[request.client_msg_id] = resp

        return resp

    except SecurityViolationError as sve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Güvenlik İhlali: {str(sve)}",
        )
    except CASTimeoutError as toe:
        total_latency_ms = (time.perf_counter() - start_time) * 1000.0
        telemetry_logger.record_step_event(
            session_id=request.session_id,
            step_index=request.step_number,
            is_correct=False,
            latency_ms=total_latency_ms,
            affective_state="CONFUSION",
            circuit_breaker_tripped=True,
            detected_bug_id="ERR_CAS_TIMEOUT",
        )
        return StepVerificationResponse(
            is_valid=False,
            is_target_reached=False,
            detected_bug=None,
            canonical_expression=None,
            error_message=f"Sembolik analiz zaman aşımına uğradı (CAS Timeout): {str(toe)}",
            analysis_latency_ms=total_latency_ms,
            is_replayed=False,
        )
    except Exception as e:
        total_latency_ms = (time.perf_counter() - start_time) * 1000.0
        return StepVerificationResponse(
            is_valid=False,
            is_target_reached=False,
            detected_bug=None,
            canonical_expression=None,
            error_message=f"Ayrıştırma hatası: {str(e)}",
            analysis_latency_ms=total_latency_ms,
            is_replayed=False,
        )


@router.post("/api/v1/session/replay-queue", response_model=OfflineBatchReplayResponse)
async def replay_offline_queue(request: OfflineBatchReplayRequest) -> OfflineBatchReplayResponse:
    """
    Çevrimdışıyken biriken adımları kronolojik sırayla idempotent olarak sunucuya aktarır (Event Replay).
    Sunucu BKT ve FSRS durumlarını geriye dönük deterministik olarak sırayla günceller.
    """
    replayed_steps: List[StepVerificationResponse] = []
    current_pl = 0.20
    is_target_reached = False

    events = request.events
    if len(events) > 100:  # DoS guard: limit offline queue replay batch size
        events = events[:100]

    for event in events:
        event.current_p_l = current_pl if math.isfinite(current_pl) else 0.20
        step_res = await verify_step(event)
        replayed_steps.append(step_res)
        if step_res.psychometrics:
            post_pl = step_res.psychometrics.bkt_posterior_p_l
            current_pl = post_pl if math.isfinite(post_pl) else current_pl
        if step_res.is_target_reached:
            is_target_reached = True

    return OfflineBatchReplayResponse(
        session_id=request.session_id,
        synced_count=len(replayed_steps),
        replayed_steps=replayed_steps,
        latest_p_l=round(current_pl, 4) if math.isfinite(current_pl) else 0.20,
        is_target_reached=is_target_reached,
    )


@router.post("/api/v1/session/start-daily")
async def start_daily_session(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """22-API-AND-COMMUNICATION-PROTOCOLS: Günlük 20 dakikalık oturumu başlatır (FSRS-4.5 ısınma + ZPD hedefi)."""
    return {
        "session_id": f"sess_daily_{int(time.time())}",
        "duration_limit_minutes": 20,
        "phases": ["warm_up", "cat_diagnostic", "problem_board", "metacognitive_reflection"],
        "target_node": "N15",
        "target_problem": "x^2 + 6x = 2",
        "circadian_lock_hours": 14,
    }


@router.post("/api/v1/session/conclude")
async def conclude_session(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """22-API-AND-COMMUNICATION-PROTOCOLS: Günlük seansı sonlandırır, 14 saatlik sirkadiyen kilidi aktifleştirir."""
    now = time.time()
    lock_until = now + (14 * 3600)

    if payload and ("student_uuid" in payload or "session_id" in payload):
        target_id = payload.get("student_uuid") or payload.get("session_id")
        try:
            db_repository.update_circadian_lock(
                student_uuid=str(target_id),
                lock_until=datetime.fromtimestamp(lock_until, timezone.utc),
            )
        except Exception:
            pass

    return {
        "status": "CONCLUDED",
        "session_ended_at": now,
        "circadian_lock_active": True,
        "lock_duration_seconds": 14 * 3600,
        "circadian_lock_until": lock_until,
        "message": "Harika bir 20 dakikalık derin odak seansı tamamlandı. Sirkadiyen uyku konsolidasyonu için seans kilitlendi.",
    }


@router.websocket("/ws/v1/session")
async def session_websocket_endpoint(websocket: WebSocket):
    """
    Canlı mobil oturum çift yönlü telemetri, adım doğrulama ve afektif şalter kanalı.
    """
    await websocket.accept()
    await websocket.send_json({
        "type": "SESSION_READY",
        "status": "CONNECTED",
        "timestamp": time.time(),
    })

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                raise
            except Exception as e:
                await websocket.send_json({
                    "type": "ERROR",
                    "code": "MALFORMED_JSON",
                    "message": f"Geçersiz JSON formatı: {str(e)}",
                })
                continue

            if not isinstance(data, dict):
                await websocket.send_json({
                    "type": "ERROR",
                    "code": "INVALID_PAYLOAD_STRUCTURE",
                    "message": "Mesaj gövdesi JSON nesnesi (dictionary) olmalıdır.",
                })
                continue

            msg_type = data.get("type")
            client_msg_id = data.get("client_msg_id", "cmsg_default")
            payload = data.get("payload", {})
            if not isinstance(payload, dict):
                payload = {}

            try:
                if msg_type == "STEP_SUBMIT":
                    raw_latex = payload.get("raw_latex", "")
                    prev_canonical = payload.get("previous_canonical", "x**2 + 6*x - 2 = 0")
                    target_eq = payload.get("target_equation", "x**2 + 6*x - 2 = 0")
                    latency_ms = payload.get("latency_ms", 2000.0)
                    thrash_count = payload.get("hesitation_pauses_count", 0)

                    try:
                        latency_ms_clean = float(latency_ms)
                        if math.isnan(latency_ms_clean) or math.isinf(latency_ms_clean) or latency_ms_clean < 0:
                            latency_ms_clean = 2000.0
                    except (ValueError, TypeError):
                        latency_ms_clean = 2000.0

                    try:
                        thrash_count_clean = int(thrash_count)
                        if thrash_count_clean < 0:
                            thrash_count_clean = 0
                    except (ValueError, TypeError):
                        thrash_count_clean = 0

                    sess_id = str(data.get("session_id", "ws_sess"))

                    # 1. CAS Verification
                    try:
                        is_valid, elapsed, diff = cas_engine.verify_equivalence(raw_latex, target_eq)
                    except Exception:
                        is_valid = False
                        diff = None

                    detected_bug = None
                    socratic_prompt = None
                    if not is_valid:
                        try:
                            detected_bug = misconception_detector.detect(raw_latex, prev_canonical, target_eq)
                            # Generate Socratic probe
                            socr_req = SocraticRequest(
                                user_input=raw_latex,
                                target_equation=target_eq,
                                previous_step=prev_canonical,
                                diagnostic_bug=detected_bug,
                            )
                            socr_log = socratic_pipeline.process(socr_req)
                            socratic_prompt = {
                                "agent_role": "socratic_coach",
                                "message": socr_log.final_output,
                                "scaffold_level": 2,
                            }
                        except Exception as e:
                            logger.warning(f"WebSocket socratic probe generation error: {e}")

                    # 2. Affective evaluation
                    obs = BehaviorObservation(
                        response_time_ms=latency_ms_clean,
                        is_correct=is_valid,
                        thrash_events_count=thrash_count_clean,
                        consecutive_errors=0 if is_valid else 1,
                    )
                    affective_assessment = affective_detector.evaluate_telemetry(obs, session_id=sess_id)

                    if affective_assessment.is_circuit_breaker_tripped:
                        await websocket.send_json({
                            "type": "AFFECTIVE_ALERT",
                            "payload": {
                                "circuit_breaker_triggered": True,
                                "action": "TRIGGER_BREATHE_MODAL",
                                "f_score": affective_assessment.frustration_score,
                                "support_message": affective_assessment.intervention_message,
                            }
                        })

                    telemetry_logger.record_step_event(
                        session_id=sess_id,
                        step_index=payload.get("step_index", 1),
                        is_correct=is_valid,
                        latency_ms=latency_ms_clean,
                        affective_state=affective_assessment.primary_state.value,
                        circuit_breaker_tripped=affective_assessment.is_circuit_breaker_tripped,
                        detected_bug_id=detected_bug.bug_id if detected_bug else None,
                    )

                    # Send STEP_VALIDATED
                    await websocket.send_json({
                        "type": "STEP_VALIDATED",
                        "client_msg_id": client_msg_id,
                        "status": "VALID" if is_valid else ("BUGGY_RULE_DETECTED" if detected_bug else "INVALID"),
                        "payload": {
                            "is_correct": is_valid,
                            "is_terminal_step": is_valid and ("=" in raw_latex and not ("^2" in raw_latex or "**2" in raw_latex)),
                            "canonical_latex": raw_latex,
                            "buggy_rule": {
                                "rule_id": detected_bug.bug_id,
                                "description": detected_bug.description,
                            } if detected_bug else None,
                            "haptic_feedback": "light_impact" if is_valid else "heavy_error",
                            "socratic_prompt": socratic_prompt,
                        }
                    })

                elif msg_type == "CONFIDENCE_SUBMIT":
                    raw_conf = payload.get("confidence_level", 0.5)
                    try:
                        conf = float(raw_conf)
                        if not math.isfinite(conf):
                            conf = 0.5
                        conf = max(0.0, min(1.0, conf))
                    except (ValueError, TypeError):
                        conf = 0.5
                    # Proper scoring rule: 10 - 20 * (conf - y)^2
                    await websocket.send_json({
                        "type": "CONFIDENCE_ACK",
                        "client_msg_id": client_msg_id,
                        "payload": {
                            "confidence_recorded": conf,
                            "status": "RECORDED",
                        }
                    })

                elif msg_type == "HINT_REQUEST":
                    current_latex = payload.get("current_latex", "")
                    target_eq = payload.get("target_equation", "x**2 + 6*x - 2 = 0")
                    try:
                        socr_req = SocraticRequest(
                            user_input=f"Yardım istiyorum: {current_latex}",
                            target_equation=target_eq,
                            previous_step=current_latex,
                        )
                        socr_log = socratic_pipeline.process(socr_req)
                        socratic_message = socr_log.final_output
                    except Exception as e:
                        logger.warning(f"WebSocket hint generation error: {e}")
                        socratic_message = "Bu aşamada eşitliği korumak için her iki tarafa hangi işlemi uygulamalıyız?"

                    await websocket.send_json({
                        "type": "HINT_RESPONSE",
                        "client_msg_id": client_msg_id,
                        "payload": {
                            "socratic_prompt": {
                                "agent_role": "socratic_coach",
                                "message": socratic_message,
                                "scaffold_level": 1,
                            }
                        }
                    })

                elif msg_type == "PING":
                    await websocket.send_json({"type": "PONG", "timestamp": time.time()})

                else:
                    await websocket.send_json({
                        "type": "ERROR",
                        "client_msg_id": client_msg_id,
                        "code": "UNKNOWN_MESSAGE_TYPE",
                        "message": f"Bilinmeyen mesaj tipi: {msg_type}",
                    })
            except Exception as err:
                logger.error(f"WebSocket message processing error: {err}")
                await websocket.send_json({
                    "type": "ERROR",
                    "client_msg_id": client_msg_id,
                    "code": "PROCESSING_ERROR",
                    "message": f"Mesaj işleme hatası: {str(err)}",
                })

    except WebSocketDisconnect:
        logger.info("WebSocket oturumu istemci tarafından kapatıldı.")
    except Exception as exc:
        logger.error(f"WebSocket beklenmeyen bağlantı hatası: {exc}")
