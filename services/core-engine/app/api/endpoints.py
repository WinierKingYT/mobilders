import time
from typing import Optional, Dict, List, Any
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from app.models.schemas import (
    StepVerificationRequest,
    StepVerificationResponse,
    StepPsychometrics,
    CATNextItemRequest,
    CATItemResponse,
    CATSubmitRequest,
    CATSubmitResponse,
)
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.graph.knowledge_dag import KnowledgeDAG
from app.adaptive.cat_engine import CATEngine
from app.psychometrics.bkt import IndividualizedBKT
from app.psychometrics.ddm import EZDiffusionSolver
from app.affect.detector import AffectiveStateDetector, BehaviorObservation
from app.socratic.pipeline import SocraticPipeline, SocraticRequest, InnerMonologueLog
from app.retention.fsrs import FSRSEngine
from app.analytics.local_reporter import LocalAnalyticsReporter
from app.core.logging_config import telemetry_logger

router = APIRouter(tags=["Session, Verification, Diagnostic & WebSocket"])

# Tekil motor örnekleri (Singletons)
cas_engine = SymbolicEquivalenceEngine()
misconception_detector = QuadraticMisconceptionDetector(cas_engine)
knowledge_dag = KnowledgeDAG()
cat_engine = CATEngine(dag=knowledge_dag)
fsrs_engine = FSRSEngine()
affective_detector = AffectiveStateDetector()
socratic_pipeline = SocraticPipeline()
local_analytics = LocalAnalyticsReporter(dag=knowledge_dag, fsrs=fsrs_engine)


# ==========================================
# 1. ADIM BAZLI ÇÖZÜM TAHTASI DOĞRULAMA API
# ==========================================

@router.post("/api/v1/session/step/verify", response_model=StepVerificationResponse)
async def verify_step(request: StepVerificationRequest) -> StepVerificationResponse:
    """
    Öğrencinin girdiği cebirsel adımı deterministik olarak doğrular.
    Doğru değilse 5 temel bozuk kuralı (Buggy Rules) arar.
    """
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

        return StepVerificationResponse(
            is_valid=is_equiv,
            is_target_reached=is_equiv and ("=" in request.user_expression and not ("**2" in request.user_expression or "^2" in request.user_expression)),
            detected_bug=detected_bug,
            canonical_expression=diff_str if is_equiv else None,
            error_message=None,
            analysis_latency_ms=total_latency_ms,
            psychometrics=psychometrics,
        )

    except SecurityViolationError as sve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Güvenlik İhlali: {str(sve)}",
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
        )


# ==========================================
# 2. 2PL-IRT UYARLAMALI DİNAMİK TEŞHİS API
# ==========================================

@router.post("/api/v1/diagnostic/next-item", response_model=Optional[CATItemResponse])
async def get_next_cat_item(request: CATNextItemRequest) -> Optional[CATItemResponse]:
    """
    Mevcut latent yetenek düzeyine göre Fisher bilgisini maksimize eden
    bir sonraki teşhis sorusunu getirir.
    """
    item = cat_engine.select_next_item(
        current_theta=request.current_theta,
        administered_item_ids=set(request.administered_item_ids),
    )
    if not item:
        return None

    return CATItemResponse(
        item_id=item.item_id,
        target_node_id=item.target_node_id,
        prompt=item.prompt,
        difficulty_b=item.difficulty_b,
        discrimination_a=item.discrimination_a,
    )


@router.post("/api/v1/diagnostic/submit", response_model=CATSubmitResponse)
async def submit_cat_response(request: CATSubmitRequest) -> CATSubmitResponse:
    """
    Öğrencinin teşhis sorusuna verdiği cevabı işler, MAP yetenek kestirimini günceller.
    Test bittiyse 20 düğümlü Cebir Atlası başlangıç olasılıklarını döner.
    """
    # 1. Yanıt geçmişine son maddeyi ekle
    updated_history = list(request.administered_history)
    updated_history.append((request.item_id, request.is_correct))

    # 2. Yetenek (theta) ve Standart Hata (SE) güncelle
    theta_hat, se = cat_engine.estimate_theta(updated_history)

    # 3. Durdurma kuralı kontrolü
    is_done = cat_engine.is_test_complete(updated_history, current_se=se)

    next_item_resp = None
    seeded_mastery = None
    zpd_candidates = None

    if is_done:
        # Test bitti: 20 düğümlü grafı tohumla (DAG Seeding)
        seeded_mastery = cat_engine.seed_knowledge_dag(theta_hat)
        mastered_set = {n_id for n_id, p in seeded_mastery.items() if p >= 0.85}
        zpd_candidates = knowledge_dag.get_zpd_candidates(mastered_set)
    else:
        # Test devam ediyor: Sıradaki maddeyi seç
        administered_ids = {it_id for it_id, _ in updated_history}
        next_item = cat_engine.select_next_item(theta_hat, administered_ids)
        if next_item:
            next_item_resp = CATItemResponse(
                item_id=next_item.item_id,
                target_node_id=next_item.target_node_id,
                prompt=next_item.prompt,
                difficulty_b=next_item.difficulty_b,
                discrimination_a=next_item.discrimination_a,
            )

    return CATSubmitResponse(
        theta_hat=round(theta_hat, 4),
        standard_error=round(se, 4),
        is_complete=is_done,
        next_item=next_item_resp,
        seeded_mastery=seeded_mastery,
        zpd_candidates=zpd_candidates,
    )


# -----------------------------------------------------------
# 22-API-AND-COMMUNICATION-PROTOCOLS.md REST Alias Endpoints
# -----------------------------------------------------------

@router.post("/api/v1/cat/start")
async def start_cat_session(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """22-API-AND-COMMUNICATION-PROTOCOLS: Yeni uyarlamalı CAT teşhis oturumu başlatır."""
    sess_id = payload.get("session_id", f"cat_{int(time.time())}") if payload else f"cat_{int(time.time())}"
    first_item = cat_engine.select_next_item(current_theta=0.0, administered_item_ids=set())
    return {
        "cat_session_id": sess_id,
        "first_item": {
            "item_id": first_item.item_id,
            "target_node_id": first_item.target_node_id,
            "prompt": first_item.prompt,
            "difficulty_b": first_item.difficulty_b,
            "discrimination_a": first_item.discrimination_a,
        } if first_item else None,
        "initial_theta": 0.0,
        "initial_se": 1.0,
    }


@router.post("/api/v1/cat/submit-item")
async def submit_cat_item_alias(request: CATSubmitRequest) -> CATSubmitResponse:
    """22-API-AND-COMMUNICATION-PROTOCOLS: Çözülen CAT maddesini iletir."""
    return await submit_cat_response(request)


@router.get("/api/v1/cat/result/{cat_session_id}")
async def get_cat_result(cat_session_id: str, theta: float = 0.0) -> Dict[str, Any]:
    """22-API-AND-COMMUNICATION-PROTOCOLS: CAT sonucunda oluşan 20 düğümlü Cebir Atlası Bayesian başlangıç olasılık dağılımı."""
    seeded = cat_engine.seed_knowledge_dag(theta)
    mastered = {n for n, p in seeded.items() if p >= 0.85}
    zpd = knowledge_dag.get_zpd_candidates(mastered)
    return {
        "cat_session_id": cat_session_id,
        "theta_estimate": theta,
        "atlas_mastery": seeded,
        "zpd_candidates": zpd,
    }


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


@router.get("/api/v1/atlas/state")
async def get_atlas_state() -> Dict[str, Any]:
    """22-API-AND-COMMUNICATION-PROTOCOLS: Öğrencinin güncel 20 düğümlü Cebir Atlası durumu."""
    return {
        "total_nodes": len(knowledge_dag.nodes),
        "nodes": [
            {
                "node_id": node.id,
                "title": node.title,
                "layer": node.level,
                "prerequisites": node.strict_prereqs,
            }
            for node in knowledge_dag.nodes.values()
        ],
    }


@router.post("/api/v1/session/conclude")
async def conclude_session(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """22-API-AND-COMMUNICATION-PROTOCOLS: Günlük seansı sonlandırır, 14 saatlik sirkadiyen kilidi aktifleştirir."""
    now = time.time()
    lock_until = now + (14 * 3600)
    return {
        "status": "CONCLUDED",
        "session_ended_at": now,
        "circadian_lock_active": True,
        "lock_duration_seconds": 14 * 3600,
        "circadian_lock_until": lock_until,
        "message": "Harika bir 20 dakikalık derin odak seansı tamamlandı. Sirkadiyen uyku konsolidasyonu için seans kilitlendi.",
    }


@router.get("/api/v1/analytics/student/{student_id}")
async def get_student_analytics(student_id: str) -> Dict[str, Any]:
    """
    Öğrencinin metabilişsel kalibrasyon, Paas bilişsel verimlilik (E),
    14 günlük FSRS kalıcılık projeksiyonu ve 26 düğümlü Cebir Atlası analitiği.
    """
    return local_analytics.generate_student_report(student_id)


# ==========================================
# 3. SOKRATİK AI DİYALOG VE GÜVENLİK API
# ==========================================

@router.post("/api/v1/socratic/respond", response_model=InnerMonologueLog)
async def get_socratic_response(request: SocraticRequest) -> InnerMonologueLog:
    """
    4-Katmanlı İç Monolog hattı ve Zero-Leakage sübabı ile
    öğrenciye doğrudan cevabı vermeyen Sokratik rehberlik üretir.
    """
    return socratic_pipeline.process(request)


# ==========================================
# 4. WEBSOCKET CANLI OTURUM KANALI (/ws/v1/session)
# ==========================================

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
            data = await websocket.receive_json()
            msg_type = data.get("type")
            client_msg_id = data.get("client_msg_id", "cmsg_default")
            payload = data.get("payload", {})

            if msg_type == "STEP_SUBMIT":
                raw_latex = payload.get("raw_latex", "")
                prev_canonical = payload.get("previous_canonical", "x**2 + 6*x - 2 = 0")
                target_eq = payload.get("target_equation", "x**2 + 6*x - 2 = 0")
                latency_ms = payload.get("latency_ms", 2000.0)
                thrash_count = payload.get("hesitation_pauses_count", 0)

                # 1. CAS Verification
                try:
                    is_valid, elapsed, diff = cas_engine.verify_equivalence(raw_latex, target_eq)
                except Exception:
                    is_valid = False
                    diff = None

                detected_bug = None
                socratic_prompt = None
                if not is_valid:
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

                # 2. Affective evaluation
                obs = BehaviorObservation(
                    response_time_ms=float(latency_ms),
                    is_correct=is_valid,
                    thrash_events_count=thrash_count,
                    consecutive_errors=0 if is_valid else 1,
                )
                affective_assessment = affective_detector.evaluate_telemetry(obs)

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
                    session_id=data.get("session_id", "ws_sess"),
                    step_index=payload.get("step_index", 1),
                    is_correct=is_valid,
                    latency_ms=float(latency_ms),
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
                conf = float(payload.get("confidence_level", 0.5))
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
                socr_req = SocraticRequest(
                    user_input=f"Yardım istiyorum: {current_latex}",
                    target_equation="x**2 + 6*x - 2 = 0",
                    previous_step=current_latex,
                )
                socr_log = socratic_pipeline.process(socr_req)
                await websocket.send_json({
                    "type": "HINT_RESPONSE",
                    "client_msg_id": client_msg_id,
                    "payload": {
                        "socratic_prompt": {
                            "agent_role": "socratic_coach",
                            "message": socr_log.final_output,
                            "scaffold_level": 1,
                        }
                    }
                })

            elif msg_type == "PING":
                await websocket.send_json({"type": "PONG", "timestamp": time.time()})

    except WebSocketDisconnect:
        pass

