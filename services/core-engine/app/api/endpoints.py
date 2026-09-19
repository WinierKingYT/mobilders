import time
from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from app.models.schemas import (
    StepVerificationRequest,
    StepVerificationResponse,
    OfflineBatchReplayRequest,
    OfflineBatchReplayResponse,
    StepPsychometrics,
    CATNextItemRequest,
    CATItemResponse,
    CATSubmitRequest,
    CATSubmitResponse,
    StrokeRecognitionRequest,
    StrokeRecognitionResponse,
    MultimodalStepVerificationRequest,
    MultimodalStepVerificationResponse,
    CurriculumStandard,
    CurriculumListResponse,
    ClassroomAnalyticsResponse,
    LTILaunchPayload,
    LTIGradeScoreRequest,
    VoiceSocraticRequest,
    VoiceSocraticResponse,
    CurriculumSynthesizeRequest,
    SynthesizedCurriculumResponse,
    SimulationCohortRequest,
    SimulationCohortResponse,
    DPExportRequest,
    DPExportResponse,
    LeaderboardResponse,
)
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
from app.cas.stroke_parser import StrokeToASTParser
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.graph.knowledge_dag import KnowledgeDAG
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.adaptive.cat_engine import CATEngine
from app.psychometrics.bkt import IndividualizedBKT
from app.psychometrics.ddm import EZDiffusionSolver
from app.affect.detector import AffectiveStateDetector, BehaviorObservation
from app.socratic.pipeline import SocraticPipeline, SocraticRequest, InnerMonologueLog
from app.retention.fsrs import FSRSEngine
from app.analytics.local_reporter import LocalAnalyticsReporter
from app.analytics.classroom_reporter import ClassroomAnalyticsReporter
from app.lti.service import LTI13Service
from app.voice.service import VoiceSocraticEngine
from app.curriculum_generator.dag_synthesizer import AutonomousCurriculumSynthesizer
from app.simulation.cohort_factory import VectorizedCohortSimulationFactory
from app.curriculum_generator.trap_question_factory import (
    TrapQuestionGenerator,
    DynamicExamFactory,
    FormalQuestionVerifier,
    ExamDocumentExporter,
    ExamSection,
    TrapQuestion,
    DynamicExam,
)
from app.research.dp_exporter import DifferentialPrivacyExporter
from app.research.leaderboard import CognitiveModelBenchmark
from app.ocr.models import MathScanRequest, MathScanResponse
from app.ocr.vision_pipeline import MathVisionPipeline
from app.ocr.socratic_diagnoser import SocraticNotebookDiagnoser
from app.modeling.models import (
    ScaffoldStepRequest,
    ScaffoldStepResponse,
    ModelingProblemSpec,
)
from app.modeling.scaffold_engine import SocraticModelingScaffoldEngine
from app.geometry.analytic_geometry import solve_analytic_geometry
from app.geometry.synthetic_geometry import solve_synthetic_geometry
from app.probability.combinatorics_engine import (
    solve_combinatorics_or_probability,
    MonteCarloProbabilitySimulator,
)
from app.root_pedagogy.models import (
    ZeroBaselineEvaluationRequest,
    ZeroBaselineEvaluationResponse,
    CoSolveRequest,
    CoSolveResponse,
    SandboxSessionRequest,
    SandboxSessionResponse,
    WeaknessEntry,
    RootNode,
)
from app.root_pedagogy.root_dag import RootPrerequisiteDAG
from app.root_pedagogy.diagnostic import ZeroBaselineDiagnostic
from app.root_pedagogy.weakness_ledger import CognitiveWeaknessLedger
from app.root_pedagogy.co_solver import ActiveCoSolverEngine
from app.root_pedagogy.sandbox import InSituRemediationSandbox
from app.vault.mistake_vault import (
    CognitiveMistakeVault,
    MistakeRecord,
    MistakeStatus,
    SelfCorrectionStage,
    SelfCorrectionSessionManager,
    BossBattleEngine,
    BossBattleState,
)
from app.core.logging_config import telemetry_logger

router = APIRouter(tags=["Session, Verification, Diagnostic, Multimodal, LTI, Voice, Autonomous Generator & Benchmark, Mistake Vault"])

# Tekil motor örnekleri (Singletons)
cas_engine = SymbolicEquivalenceEngine()
misconception_detector = QuadraticMisconceptionDetector(cas_engine)
knowledge_dag = KnowledgeDAG()
curriculum_registry = CurriculumOntologyRegistry()
cat_engine = CATEngine(dag=knowledge_dag)
fsrs_engine = FSRSEngine()
affective_detector = AffectiveStateDetector()
socratic_pipeline = SocraticPipeline()
local_analytics = LocalAnalyticsReporter(dag=knowledge_dag, fsrs=fsrs_engine)
classroom_reporter = ClassroomAnalyticsReporter(dag=knowledge_dag)
stroke_parser = StrokeToASTParser()
lti_service = LTI13Service()
voice_engine = VoiceSocraticEngine(socratic_pipeline=socratic_pipeline, guardrail=socratic_pipeline.guardrail)
curriculum_synthesizer = AutonomousCurriculumSynthesizer()
simulation_factory = VectorizedCohortSimulationFactory()
dp_exporter = DifferentialPrivacyExporter()
model_benchmark = CognitiveModelBenchmark()
cognitive_mistake_vault = CognitiveMistakeVault(fsrs_engine=fsrs_engine)
self_correction_manager = SelfCorrectionSessionManager(cognitive_mistake_vault)
boss_battle_engine = BossBattleEngine(cognitive_mistake_vault)
math_vision_pipeline = MathVisionPipeline(dag=knowledge_dag)
socratic_diagnoser = SocraticNotebookDiagnoser(
    cas=cas_engine,
    detector=misconception_detector,
    dag=knowledge_dag,
    vision_pipeline=math_vision_pipeline,
    vault=cognitive_mistake_vault,
)
modeling_scaffold_engine = SocraticModelingScaffoldEngine(
    cas_engine=cas_engine,
    detector=misconception_detector,
    vault=cognitive_mistake_vault,
)
root_dag = RootPrerequisiteDAG()
zero_baseline_diagnostic = ZeroBaselineDiagnostic()
weakness_ledger = CognitiveWeaknessLedger(root_dag)
active_cosolver = ActiveCoSolverEngine(cas_engine)
insitu_sandbox = InSituRemediationSandbox()
trap_question_generator = TrapQuestionGenerator()
dynamic_exam_factory = DynamicExamFactory(trap_question_generator)


# Idempotency Cache for offline event replay and network duplicate protection
_IDEMPOTENCY_CACHE: Dict[str, StepVerificationResponse] = {}


# ==========================================
# 1. ADIM BAZLI ÇÖZÜM TAHTASI DOĞRULAMA API
# ==========================================

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

    for event in request.events:
        event.current_p_l = current_pl
        step_res = await verify_step(event)
        replayed_steps.append(step_res)
        if step_res.psychometrics:
            current_pl = step_res.psychometrics.bkt_posterior_p_l
        if step_res.is_target_reached:
            is_target_reached = True

    return OfflineBatchReplayResponse(
        session_id=request.session_id,
        synced_count=len(replayed_steps),
        replayed_steps=replayed_steps,
        latest_p_l=round(current_pl, 4),
        is_target_reached=is_target_reached,
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
        curriculum=request.curriculum,
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
        next_item = cat_engine.select_next_item(
            theta_hat, administered_ids, curriculum=request.curriculum
        )
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


# ==========================================
# 5. MULTIMODAL INKING & STROKE-TO-AST API
# ==========================================

@router.post("/api/v1/multimodal/stroke-to-ast", response_model=StrokeRecognitionResponse)
async def recognize_ink_strokes(request: StrokeRecognitionRequest) -> StrokeRecognitionResponse:
    """
    Kullanıcının çizdiği serbest el yazısı çizgilerini ayrıştırıp aday LaTeX ve SymPy üretir.
    """
    return stroke_parser.parse_strokes(request.strokes)


@router.post("/api/v1/multimodal/ink/verify", response_model=MultimodalStepVerificationResponse)
async def verify_ink_step(request: MultimodalStepVerificationRequest) -> MultimodalStepVerificationResponse:
    """
    Çizilen el yazısı matematik adımlarını ayrıştırır ve Nöro-Sembolik Güvenlik Sınırı dahilinde
    %100 deterministik SymPy CAS motoru ve bozuk kural teşhisiyle doğrular.
    """
    start_time = time.perf_counter()

    # 1. Çizgi Ayrıştırma (Stroke-to-AST)
    recognition = stroke_parser.parse_strokes(request.strokes)
    candidate_expr = recognition.sympy_expression

    # 2. Deterministik CAS Doğrulama (Tanıma sonucu asla kendi kendini doğrulayamaz)
    is_equiv, cas_latency, diff_str = False, 0.0, None
    detected_bug = None
    error_msg = None

    if candidate_expr:
        try:
            is_equiv, cas_latency, diff_str = cas_engine.verify_equivalence(
                candidate_expr, request.target_equation
            )
            if not is_equiv:
                detected_bug = misconception_detector.detect(
                    user_step_str=candidate_expr,
                    previous_step_str=request.previous_step or request.target_equation,
                    target_equation_str=request.target_equation,
                )
        except SecurityViolationError as e:
            error_msg = f"Güvenlik ihlali: {str(e)}"
        except Exception as e:
            error_msg = f"Cebirsel ayrıştırma uyarısı: {str(e)}"
    else:
        error_msg = "Çizimden geçerli bir matematiksel ifade çıkarılamadı."

    total_latency_ms = (time.perf_counter() - start_time) * 1000.0

    # 3. Psikometri ve Bilişsel Modelleme (iBKT)
    current_pl = request.current_p_l if request.current_p_l is not None else 0.20
    post_pl, next_pl = IndividualizedBKT.update_mastery(p_l=current_pl, is_correct=is_equiv)
    psychometrics = StepPsychometrics(
        bkt_posterior_p_l=round(post_pl, 4),
        bkt_next_p_l=round(next_pl, 4),
        ddm_drift_rate=None,
        ddm_boundary_separation=None,
        ddm_cognitive_state="fluent_inking_mastery" if is_equiv else "inking_exploration",
    )

    is_target_reached = is_equiv and any(kw in candidate_expr for kw in ["x=", "x =", "x1=", "x2="])

    return MultimodalStepVerificationResponse(
        recognized_latex=recognition.raw_latex,
        recognized_sympy=recognition.sympy_expression,
        is_valid=is_equiv,
        is_target_reached=is_target_reached,
        detected_bug=detected_bug,
        canonical_expression=candidate_expr,
        error_message=error_msg,
        recognition_confidence=recognition.confidence,
        total_latency_ms=round(total_latency_ms, 2),
        psychometrics=psychometrics,
    )


# ==========================================
# 6. ULUSLARARASI MÜFREDAT ONTOLOJİ API
# ==========================================

@router.get("/api/v1/curriculum/standards", response_model=CurriculumListResponse)
async def get_curriculum_standards(curriculum: Optional[str] = None) -> CurriculumListResponse:
    """
    MEB, IB DP, US Common Core ve AP Precalculus ontoloji kazanım standartlarını listeler.
    """
    if curriculum and curriculum.upper() not in ["ALL", "DEFAULT"]:
        standards = curriculum_registry.get_standards_for_curriculum(curriculum)
    else:
        standards = curriculum_registry.get_all_standards()

    return CurriculumListResponse(
        curricula=CurriculumOntologyRegistry.CURRICULA,
        total_standards=len(standards),
        standards=standards,
    )


# ==========================================
# 7. OKUL VE LMS ENTEGRASYONU (LTI 1.3 & AGS)
# ==========================================

@router.post("/api/v1/lti/login")
async def lti_oidc_login(payload: LTILaunchPayload):
    """
    LMS (Canvas, Moodle, Google Classroom) 3. taraf OIDC oturum açma başlangıcı.
    """
    return lti_service.initiate_login(payload)


@router.post("/api/v1/lti/launch")
async def lti_resource_launch(id_token: str, state: Optional[str] = None):
    """
    LTI 1.3 Kaynak Bağlantısı Başlatma ve Sıfır-PII anonim kullanıcı doğrulama.
    """
    return lti_service.handle_launch(id_token, state)


@router.get("/api/v1/lti/jwks")
async def lti_jwks():
    """
    Öğrenme Motoru'nun LMS doğrulama açık anahtar kümesi (JWKS / RS256).
    """
    return lti_service.get_jwks()


@router.post("/api/v1/lti/ags/scores")
async def lti_sync_grade(request: LTIGradeScoreRequest):
    """
    LTI 1.3 AGS Not Defteri ile çift yönlü puan ve yetkinlik senkronizasyonu.
    """
    return lti_service.sync_grade_to_lms(request)


# ==========================================
# 8. SIFIR-PII SINIF VE ÖĞRETMEN ANALİTİK API
# ==========================================

@router.get("/api/v1/classroom/analytics", response_model=ClassroomAnalyticsResponse)
async def get_classroom_analytics(
    cohort_id: str = "CLASS-10A", students: int = 28
) -> ClassroomAnalyticsResponse:
    """
    Öğretmenler için öğrencilerin ZPD dağılımını, yaygın bozuk kuralları ve Paas bilişsel
    yük indeksini kişisel veri içermeksizin (Zero-PII) raporlar.
    """
    return classroom_reporter.generate_classroom_report(cohort_id=cohort_id, student_count=students)


# ==========================================
# 9. BİLİŞSEL SESLİ SOKRATİK REHBERLİK API
# ==========================================

@router.post("/api/v1/voice/socratic-turn", response_model=VoiceSocraticResponse)
async def voice_socratic_turn(request: VoiceSocraticRequest) -> VoiceSocraticResponse:
    """
    Yazma güçlüğü çeken öğrenciler için konuşmadan-metne ve metinden-konuşmaya destekli,
    Zero-Leakage filtresiyle güvence altına alınmış Sokratik rehberlik sunar.
    """
    return voice_engine.process_voice_turn(request)


# ==========================================
# 10. OTONOM MÜFREDAT VE FORMEL KANIT API
# ==========================================

@router.post("/api/v1/curriculum/synthesize", response_model=SynthesizedCurriculumResponse)
async def synthesize_curriculum(request: CurriculumSynthesizeRequest) -> SynthesizedCurriculumResponse:
    """
    İleri matematik konusunu girdi alarak 30 düğümlü döngüsüz Bilgi Grafı (DAG),
    kavram yanılgısı kataloğu ve SymPy ile formel olarak kanıtlanmış öğrenme adımları sentezler.
    """
    return curriculum_synthesizer.synthesize(request)


# ==========================================
# 11. 100.000 SENTETİK ÖĞRENCİ İKİZİ SİMÜLASYON API
# ==========================================

@router.post("/api/v1/simulation/run-cohort", response_model=SimulationCohortResponse)
async def run_cohort_simulation(request: SimulationCohortRequest) -> SimulationCohortResponse:
    """
    Farklı bilişsel profillere sahip 100.000 sentetik öğrenci ikizi üzerinde
    30 günlük sanal zaman hızlandırmasıyla Monte Carlo simülasyonu yürütür ve dar boğazları eler.
    """
    return simulation_factory.run_simulation(request)


# ==========================================
# 12. AÇIK AKADEMİK ARAŞTIRMA VE LİDERLİK TABLOSU API
# ==========================================

@router.post("/api/v1/research/export/dp-dataset", response_model=DPExportResponse)
async def export_dp_research_dataset(request: DPExportRequest) -> DPExportResponse:
    """
    Bilişsel bilim araştırmacıları için tamamen anonimleştirilmiş (sıfır-PII),
    diferansiyel gizlilik (epsilon-DP) korumalı açık veri seti üretir.
    """
    return dp_exporter.export_dataset(request)


@router.get("/api/v1/research/leaderboard", response_model=LeaderboardResponse)
async def get_cognitive_models_leaderboard() -> LeaderboardResponse:
    """
    iBKT, DDM, FSRS ve IRT modellerinin kestirimsel başarılarını karşılaştıran
    küresel Öğrenme Bilimleri Liderlik Tablosunu döner.
    """
    return model_benchmark.get_leaderboard()


# ==========================================
# 13. DEFTERDEN / KİTAPTAN SORU FOTOĞRAFLAMA VE SOKRATİK HATA TEŞHİS KAMERASI API
# ==========================================

@router.post("/api/v1/scan/diagnose", response_model=MathScanResponse)
async def scan_and_diagnose_notebook(request: MathScanRequest) -> MathScanResponse:
    """
    Hedef 5: Defterden/Kitaptan Soru Fotoğraflama ve Sokratik Hata Teşhis Kamerası API'si.
    Anti-Photomath felsefesi: Doğrudan cevabı vermek KESİNLİKLE YASAKTIR.
    Görüntüden veya metinden adımları ayırır, CAS ile doğrular, Buggy Rule tespit eder
    ve Zero-Leakage kalkanıyla Sokratik geri bildirim üretir.
    """
    lines = math_vision_pipeline.process_image_or_text(
        image_base64=request.image_base64,
        raw_text_override=request.raw_text_override,
    )
    response = socratic_diagnoser.diagnose_notebook_solution(
        segmented_lines=lines,
        target_problem=request.target_problem,
        user_id=request.student_id or "default_student",
    )
    return response


# ==========================================
# 14. HİKAYELİ PROBLEMLER VE SOKRATİK MODELLEME İSKELESİ API
# ==========================================

@router.post("/api/v1/modeling/scaffold/step", response_model=ScaffoldStepResponse)
async def evaluate_modeling_scaffold_step(request: ScaffoldStepRequest) -> ScaffoldStepResponse:
    """
    Hedef 8: Yeni Nesil Hikayeli Problemler ve Modelleme Motoru (Word Problems & Modeling).
    3 Aşamalı Modelleme İskelesi:
    1. Değişken Tanımla (Variable Identification)
    2. Eşitliği Kur (Equation Formulation & Buggy Rule Check)
    3. Adım Adım Çöz & Gerçek Dünya Kısıtları (CAS Solution & Domain Guard)
    """
    return modeling_scaffold_engine.evaluate_step(request)


@router.get("/api/v1/modeling/problems", response_model=List[ModelingProblemSpec])
async def list_modeling_problems() -> List[ModelingProblemSpec]:
    """Sistemdeki tüm standart modelleme problemlerini listeler."""
    return list(modeling_scaffold_engine.problem_bank.values())


@router.get("/api/v1/modeling/problem/{problem_id}", response_model=ModelingProblemSpec)
async def get_modeling_problem(problem_id: str) -> ModelingProblemSpec:
    """Belirli bir modelleme probleminin tanımını ve şematik verilerini döner."""
    prob = modeling_scaffold_engine.problem_bank.get(problem_id)
    if not prob:
        raise HTTPException(status_code=404, detail=f"Problem {problem_id} bulunamadı.")
    return prob


# ==========================================
# 15. KÖK PEDAGOJİ VE AKTİF BİRLİKTE ÇÖZME API (HEDEF 2 & HEDEF 3)
# ==========================================

@router.post("/api/v1/root/diagnostic/evaluate", response_model=ZeroBaselineEvaluationResponse)
async def evaluate_zero_baseline(request: ZeroBaselineEvaluationRequest) -> ZeroBaselineEvaluationResponse:
    """
    Hedef 2: Sıfır Tabanlı Bilişsel Sezgi Testi Değerlendirme API'si.
    Öğrencinin 3 temel soruya verdiği cevaplara göre kök patika gereksinimini tespit eder.
    """
    return zero_baseline_diagnostic.evaluate(request)


@router.post("/api/v1/root/cosolve/subgoal", response_model=CoSolveResponse)
async def process_cosolve_subgoal(request: CoSolveRequest) -> CoSolveResponse:
    """
    Hedef 3: Aktif Birlikte Çözme Motoru (Faded Worked Examples & Subgoal Labeling).
    Öğrencinin mikro alt hedefteki cevabını denetler, 8s üzerinde hareketsizlikte fısıltı ve kaynak açıcı sunar.
    """
    resp = active_cosolver.process_subgoal_step(request)
    # Hatalıysa zaaf defterine kaydet
    if not resp.is_valid:
        weakness_ledger.log_error(
            student_id=request.session_id,
            node_id="N_ROOT_SUBGOAL",
            user_step=request.student_answer,
            elapsed_seconds=request.elapsed_seconds,
        )
    return resp


@router.post("/api/v1/root/sandbox/session", response_model=SandboxSessionResponse)
async def create_sandbox_session(request: SandboxSessionRequest) -> SandboxSessionResponse:
    """
    Hedef 3: In-Situ Mikro-Kum Havuzu Başlatma API'si.
    Lise sorusunda kök hata yapıldığında ana soruyu dondurur ve 45 saniyelik görsel aracı açar.
    """
    return insitu_sandbox.create_sandbox(request)


@router.get("/api/v1/root/weaknesses/{student_id}", response_model=List[WeaknessEntry])
async def get_student_weaknesses(student_id: str) -> List[WeaknessEntry]:
    """Hedef 3: Bilişsel Zaaf Defteri kayıtlarını döndürür."""
    return weakness_ledger.get_student_weaknesses(student_id)


@router.get("/api/v1/root/dag/nodes", response_model=List[RootNode])
async def list_root_dag_nodes() -> List[RootNode]:
    """Hedef 2: Kök Bilgi Grafı'ndaki (N_ROOT_01 - N_ROOT_16) tüm düğümleri döner."""
    return list(root_dag.nodes.values())


# ==========================================
# 16. KİŞİSEL HATA OTOPSİSİ VE ZAAF AVCISI API (HEDEF 12)
# ==========================================

class VaultRecordRequest(BaseModel):
    user_id: str
    node_id: str
    bug_id: str
    problem_statement: str
    offending_step: str
    correct_principle: str
    remediation_directive: str
    timestamp: Optional[float] = None


class SelfCorrectionStartRequest(BaseModel):
    mistake_id: str


class SelfCorrectionDiagnoseRequest(BaseModel):
    mistake_id: str
    is_identified: bool


class SelfCorrectionExplainRequest(BaseModel):
    mistake_id: str
    is_principle_correct: bool


class SelfCorrectionResolveRequest(BaseModel):
    mistake_id: str
    is_correct: bool
    current_time: Optional[float] = None


class BossBattleSpawnRequest(BaseModel):
    user_id: str
    current_time: Optional[float] = None


class BossBattleTurnRequest(BaseModel):
    battle_id: str
    is_clean_solve: bool
    current_time: Optional[float] = None


@router.post("/api/v1/vault/record", response_model=MistakeRecord)
async def record_vault_mistake(req: VaultRecordRequest) -> MistakeRecord:
    """Kavramsal bir hatayı Bilişsel Hata Kasasına SQLite üzerine kaydeder."""
    return cognitive_mistake_vault.record_mistake(
        user_id=req.user_id,
        node_id=req.node_id,
        bug_id=req.bug_id,
        problem_statement=req.problem_statement,
        offending_step=req.offending_step,
        correct_principle=req.correct_principle,
        remediation_directive=req.remediation_directive,
        timestamp=req.timestamp,
    )


@router.get("/api/v1/vault/list/{user_id}", response_model=List[MistakeRecord])
async def list_vault_mistakes(user_id: str, status: Optional[MistakeStatus] = None) -> List[MistakeRecord]:
    """Kullanıcının kasasındaki hataları listeler."""
    return cognitive_mistake_vault.list_mistakes(user_id=user_id, status=status)


@router.get("/api/v1/vault/due/{user_id}", response_model=List[MistakeRecord])
async def get_due_vault_mistakes(user_id: str) -> List[MistakeRecord]:
    """FSRS-4.5 tekrar zamanı gelmiş açık veya telafideki hataları getirir."""
    return cognitive_mistake_vault.get_due_mistakes(user_id=user_id)


@router.get("/api/v1/vault/analytics/{user_id}")
async def get_vault_analytics(user_id: str) -> Dict[str, Any]:
    """Kullanıcının hata ve zaaf analitiğini (kür oranı, en sık yapılan hatalar) döner."""
    return cognitive_mistake_vault.get_vault_analytics(user_id=user_id)


@router.post("/api/v1/vault/self-correction/start")
async def start_self_correction(req: SelfCorrectionStartRequest) -> Dict[str, Any]:
    """3 Aşamalı Kendi Hatasını Düzeltme seansı başlatır."""
    try:
        return self_correction_manager.start_session(req.mistake_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/v1/vault/self-correction/diagnose")
async def submit_self_correction_diagnosis(req: SelfCorrectionDiagnoseRequest) -> Dict[str, Any]:
    """Aşama 1: Hatalı terim/bozuk kural teşhisi."""
    try:
        return self_correction_manager.submit_step_diagnosis(req.mistake_id, req.is_identified)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/v1/vault/self-correction/explain")
async def submit_self_correction_explanation(req: SelfCorrectionExplainRequest) -> Dict[str, Any]:
    """Aşama 2: Doğru matematiksel ilkeyi ifade etme."""
    try:
        return self_correction_manager.submit_principle_explanation(req.mistake_id, req.is_principle_correct)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/v1/vault/self-correction/resolve")
async def submit_self_correction_clean_resolution(req: SelfCorrectionResolveRequest) -> Dict[str, Any]:
    """Aşama 3: Eşyapılı soruyu temiz çözme ve FSRS güncellemesi."""
    try:
        return self_correction_manager.submit_clean_resolution(
            req.mistake_id,
            req.is_correct,
            current_time=req.current_time,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/v1/vault/boss-battle/spawn")
async def spawn_boss_battle(req: BossBattleSpawnRequest) -> Dict[str, Any]:
    """FSRS Boss Battle oturumu başlatır (en az 3 due hata gerekir)."""
    battle = boss_battle_engine.spawn_boss_battle(req.user_id, current_time=req.current_time)
    if not battle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Boss Battle başlatılamadı: En az 3 adet tekrarı gelmiş (due) hata kaydı bulunmalıdır.",
        )
    return battle.model_dump()


@router.post("/api/v1/vault/boss-battle/turn")
async def submit_boss_battle_turn(req: BossBattleTurnRequest) -> Dict[str, Any]:
    """Boss Battle tur hamlesi gönderir."""
    try:
        return boss_battle_engine.submit_boss_turn(
            battle_id=req.battle_id,
            is_clean_solve=req.is_clean_solve,
            current_time=req.current_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# 17. ANALİTİK GEOMETRİ VE VEKTÖRLER APİ (HEDEF 10)
# ==========================================

class AnalyticGeometrySolveRequest(BaseModel):
    task: str  # "distance", "line_from_points", "vector_dot", "circle_line"
    params: Dict[str, Any]
    student_id: Optional[str] = None
    problem_statement: Optional[str] = None
    student_step: Optional[str] = None


class AnalyticGeometrySolveResponse(BaseModel):
    task: str
    result_data: Dict[str, Any]
    detected_bug: Optional[Dict[str, Any]] = None
    vault_recorded: bool = False


@router.post("/api/v1/geometry/analytic/solve", response_model=AnalyticGeometrySolveResponse)
async def solve_analytic_geometry_endpoint(req: AnalyticGeometrySolveRequest) -> AnalyticGeometrySolveResponse:
    """
    Hedef 10: Analitik Geometri ve Vektörler Motoru API'si.
    Nokta, doğru, çember ve vektör problemlerini çözer; varsa öğrenci yanılgılarını (BUG-ANAG-01..05)
    tespit edip Bilişsel Hata Kasası'na kaydeder.
    """
    try:
        res = solve_analytic_geometry(req.task, **req.params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    detected_diag = None
    vault_recorded = False

    if req.student_step:
        diag = misconception_detector.detect(req.student_step, req.problem_statement or "", "")
        if diag:
            detected_diag = diag.model_dump()
            if req.student_id:
                node_map = {
                    "BUG-ANAG-01": "N147",
                    "BUG-ANAG-02": "N141",
                    "BUG-ANAG-03": "N152",
                    "BUG-ANAG-04": "N137",
                    "BUG-ANAG-05": "N158",
                }
                node_id = node_map.get(diag.bug_id, "N136")
                cognitive_mistake_vault.record_mistake(
                    user_id=req.student_id,
                    node_id=node_id,
                    bug_id=diag.bug_id,
                    problem_statement=req.problem_statement or f"Analitik Geometri: {req.task}",
                    offending_step=req.student_step,
                    correct_principle=diag.description,
                    remediation_directive=diag.remediation_directive,
                )
                vault_recorded = True

    return AnalyticGeometrySolveResponse(
        task=req.task,
        result_data=res,
        detected_bug=detected_diag,
        vault_recorded=vault_recorded,
    )


# ==========================================
# 18. SENTETİK ÖKLİD GEOMETRİSİ VE AKILLI EK ÇİZİM API (HEDEF 11)
# ==========================================

class SyntheticGeometrySolveRequest(BaseModel):
    task: str  # "triangle_solve", "euclidean_height", "euclidean_leg", "auxiliary_advisor"
    params: Dict[str, Any]
    student_id: Optional[str] = None
    problem_statement: Optional[str] = None
    student_step: Optional[str] = None


class SyntheticGeometrySolveResponse(BaseModel):
    task: str
    result_data: Dict[str, Any]
    detected_bug: Optional[Dict[str, Any]] = None
    vault_recorded: bool = False


@router.post("/api/v1/geometry/synthetic/solve", response_model=SyntheticGeometrySolveResponse)
async def solve_synthetic_geometry_endpoint(req: SyntheticGeometrySolveRequest) -> SyntheticGeometrySolveResponse:
    """
    Hedef 11: Sentetik Öklid Geometrisi ve Akıllı Ek Çizim Motoru API'si.
    Üçgen, Öklid bağıntıları ve Sokratik ek çizim önerilerini çözer;
    varsa öğrenci yanılgılarını (BUG-EUC-01..05) tespit edip Bilişsel Hata Kasası'na kaydeder.
    """
    try:
        res = solve_synthetic_geometry(req.task, **req.params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    detected_diag = None
    vault_recorded = False

    if req.student_step:
        diag = misconception_detector.detect(req.student_step, req.problem_statement or "", "")
        if diag:
            detected_diag = diag.model_dump()
            if req.student_id:
                node_map = {
                    "BUG-EUC-01": "N162",
                    "BUG-EUC-02": "N178",
                    "BUG-EUC-03": "N169",
                    "BUG-EUC-04": "N165",
                    "BUG-EUC-05": "N167",
                }
                node_id = node_map.get(diag.bug_id, "N161")
                cognitive_mistake_vault.record_mistake(
                    user_id=req.student_id,
                    node_id=node_id,
                    bug_id=diag.bug_id,
                    problem_statement=req.problem_statement or f"Sentetik Geometri: {req.task}",
                    offending_step=req.student_step,
                    correct_principle=diag.description,
                    remediation_directive=diag.remediation_directive,
                )
                vault_recorded = True

    return SyntheticGeometrySolveResponse(
        task=req.task,
        result_data=res,
        detected_bug=detected_diag,
        vault_recorded=vault_recorded,
    )


# ==============================================================================
# HEDEF 13: Bilişsel Tuzaklı Sonsuz Soru Üretim Fabrikası & Dinamik Deneme Sınavı
# ==============================================================================

class ExamGenerateRequest(BaseModel):
    section: ExamSection = ExamSection.TYT_MATEMATIK
    question_count: int = 10
    target_theta: float = 0.0


class ExamGradeRequest(BaseModel):
    exam: DynamicExam
    answers: Dict[int, int]


class ExamExportRequest(BaseModel):
    exam: DynamicExam
    format: str = "html"  # "html" veya "latex"
    include_solutions: bool = True


class TargetedQuestionRequest(BaseModel):
    bug_id: str
    seed: Optional[int] = None


class QuestionVerifyRequest(BaseModel):
    question: TrapQuestion


@router.post("/api/v1/exam/generate", response_model=DynamicExam)
async def generate_dynamic_exam(req: ExamGenerateRequest) -> DynamicExam:
    """Belirtilen sınav tipine, soru adedine ve hedef teta düzeyine göre bilişsel tuzaklı deneme sınavı üretir."""
    return dynamic_exam_factory.assemble_exam(
        section=req.section,
        question_count=req.question_count,
        target_theta=req.target_theta,
    )


@router.post("/api/v1/exam/grade")
async def grade_dynamic_exam(req: ExamGradeRequest) -> Dict[str, Any]:
    """Dinamik deneme sınavını puanlar ve tetiklenen bilişsel tuzakları (BUG-ID) raporlar."""
    return dynamic_exam_factory.grade_exam(
        exam=req.exam,
        answers=req.answers,
    )


@router.post("/api/v1/exam/export")
async def export_dynamic_exam(req: ExamExportRequest) -> Dict[str, Any]:
    """Deneme sınavını derlenebilir LaTeX veya yazdırılabilir HTML / PDF formatında dışa aktarır."""
    if req.format.lower() == "latex":
        content = ExamDocumentExporter.export_to_latex(req.exam, include_solutions=req.include_solutions)
    else:
        content = ExamDocumentExporter.export_to_html_printable(req.exam, include_solutions=req.include_solutions)
    return {
        "format": req.format.lower(),
        "content": content,
    }


@router.post("/api/v1/exam/question/targeted", response_model=TrapQuestion)
async def generate_targeted_trap_question(req: TargetedQuestionRequest) -> TrapQuestion:
    """Öğrencinin geçmiş zaafında yer alan belirli bir BUG-ID'yi hedefleyen çeldiricili soru sentezler."""
    return trap_question_generator.generate_targeted_bug(bug_id=req.bug_id, seed=req.seed)


@router.post("/api/v1/exam/question/verify")
async def verify_trap_question_formally(req: QuestionVerifyRequest) -> Dict[str, Any]:
    """SymPy ile sorunun köklerini, analitik türev/çözüm geçerliliğini ve çeldirici tutarlılığını formel olarak ispatlar."""
    return FormalQuestionVerifier.verify_formally(req.question)


# ==============================================================================
# HEDEF 14: Olasılık, Kombinatorik ve İstatistik Motoru (Monte Carlo)
# ==============================================================================

class ProbabilitySolveRequest(BaseModel):
    problem_type: str  # "combination_selection", "linear_permutation", "conditional_probability", vb.
    params: Dict[str, Any]
    student_id: Optional[str] = None
    problem_statement: Optional[str] = None
    student_step: Optional[str] = None


class ProbabilitySolveResponse(BaseModel):
    problem_type: str
    result_data: Dict[str, Any]
    detected_bug: Optional[Dict[str, Any]] = None
    vault_recorded: bool = False


class MonteCarloSimulateRequest(BaseModel):
    experiment_type: str = "coin_flip"  # "coin_flip", "urn_draw"
    params: Dict[str, Any] = {}
    num_trials: int = 100_000


@router.post("/api/v1/probability/solve", response_model=ProbabilitySolveResponse)
async def solve_probability_endpoint(req: ProbabilitySolveRequest) -> ProbabilitySolveResponse:
    """
    Hedef 14: Olasılık ve Kombinatorik Sokratik Çözücü API'si.
    Permütasyon, kombinasyon veya koşullu olasılık problemlerini sıfır sızıntı ile iskeletlendirir;
    varsa öğrenci yanılgılarını (BUG-COMB-01..05) tespit edip Bilişsel Hata Kasası'na kaydeder.
    """
    try:
        res = solve_combinatorics_or_probability(req.problem_type, req.params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    detected_diag = None
    vault_recorded = False

    if req.student_step:
        diag = misconception_detector.detect(req.student_step, req.problem_statement or "", "")
        if diag:
            detected_diag = diag.model_dump()
            if req.student_id:
                node_map = {
                    "BUG-COMB-01": "N191",
                    "BUG-COMB-02": "N200",
                    "BUG-COMB-03": "N202",
                    "BUG-COMB-04": "N189",
                    "BUG-COMB-05": "N199",
                }
                node_id = node_map.get(diag.bug_id, "N186")
                cognitive_mistake_vault.record_mistake(
                    user_id=req.student_id,
                    node_id=node_id,
                    bug_id=diag.bug_id,
                    problem_statement=req.problem_statement or f"Olasılık/Kombinatorik: {req.problem_type}",
                    offending_step=req.student_step,
                    correct_principle=diag.description,
                    remediation_directive=diag.remediation_directive,
                )
                vault_recorded = True

    return ProbabilitySolveResponse(
        problem_type=req.problem_type,
        result_data=res,
        detected_bug=detected_diag,
        vault_recorded=vault_recorded,
    )


@router.post("/api/v1/probability/monte-carlo")
async def simulate_monte_carlo_endpoint(req: MonteCarloSimulateRequest) -> Dict[str, Any]:
    """
    Canlı Monte Carlo Olasılık Simülatörü API'si.
    100.000 sanal deney ile büyük sayılar yasasını deneysel olarak doğrular.
    """
    sim = MonteCarloProbabilitySimulator(seed=req.params.get("seed", 42))

    if req.experiment_type == "urn_draw":
        return sim.simulate_urn_draw(
            red_count=req.params.get("red_count", 4),
            blue_count=req.params.get("blue_count", 6),
            draw_count=req.params.get("draw_count", 2),
            target_reds=req.params.get("target_reds", 2),
            with_replacement=req.params.get("with_replacement", False),
            num_trials=req.num_trials,
        )
    else:
        # Default: coin_flip / Bernoulli event
        prob = req.params.get("prob", 0.5)
        return sim.simulate_event(
            trial_func=lambda rng: rng.random() < prob,
            num_trials=req.num_trials,
            theoretical_prob=prob,
        )


# =====================================================================
# HEDEF 15: MATEMATİKSEL İSPAT VE MANTIK LABORATUVARI ENDPOINTS
# =====================================================================

from app.logic.proof_lab import (
    TruthTableGenerator,
    ProofCatalog,
    ProofChecker,
    MathematicalInductionEngine,
    QuantifierEngine,
    logic_and,
    logic_or,
    logic_not,
    logic_implies,
    logic_iff,
    logic_xor,
)


class ProofTruthTableRequest(BaseModel):
    variables: List[str] = ["p", "q"]
    expression_type: str = "implies"  # "implies", "iff", "and", "or", "xor", "de_morgan_and", "contrapositive"


class ProofVerifyStepRequest(BaseModel):
    theorem_id: str
    step_number: int
    student_statement: str
    selected_rule: str
    student_id: Optional[str] = None
    problem_statement: Optional[str] = None


class ProofVerifyStepResponse(BaseModel):
    step_number: int
    is_valid: bool
    feedback: str
    expected_statement: Optional[str] = None
    expected_justification: Optional[str] = None
    detected_bug: Optional[str] = None
    vault_recorded: bool = False


class InductionSimulateRequest(BaseModel):
    claim_type: str = "gauss"  # "gauss", "exp_ineq"
    start_k: int = 1
    test_range: int = 10


@router.post("/api/v1/proof/truth-table")
async def generate_truth_table_endpoint(req: ProofTruthTableRequest) -> Dict[str, Any]:
    """
    Hedef 15: Mantıksal önermeler için 2^n satırlı doğruluk tablosu ve totoloji/çelişki analizi.
    """
    expr_type = req.expression_type.lower()
    if expr_type == "implies":
        formula = lambda env: logic_implies(env.get("p", False), env.get("q", False))
    elif expr_type == "iff":
        formula = lambda env: logic_iff(env.get("p", False), env.get("q", False))
    elif expr_type == "and":
        formula = lambda env: logic_and(env.get("p", False), env.get("q", False))
    elif expr_type == "or":
        formula = lambda env: logic_or(env.get("p", False), env.get("q", False))
    elif expr_type == "xor":
        formula = lambda env: logic_xor(env.get("p", False), env.get("q", False))
    elif expr_type == "de_morgan_and":
        # ¬(p ∧ q) ⇔ (¬p ∨ ¬q) -> Tautology test
        formula = lambda env: logic_iff(
            logic_not(logic_and(env.get("p", False), env.get("q", False))),
            logic_or(logic_not(env.get("p", False)), logic_not(env.get("q", False))),
        )
    elif expr_type == "contrapositive":
        # (p ⇒ q) ⇔ (¬q ⇒ ¬p) -> Tautology test
        formula = lambda env: logic_iff(
            logic_implies(env.get("p", False), env.get("q", False)),
            logic_implies(logic_not(env.get("q", False)), logic_not(env.get("p", False))),
        )
    else:
        formula = lambda env: env.get("p", False)

    return TruthTableGenerator.generate_table(req.variables, formula)


@router.get("/api/v1/proof/catalog")
async def get_proof_catalog_endpoint() -> List[Dict[str, Any]]:
    """
    Hedef 15: Temel teorem ispat kataloğu (√2 irrasyonelliği, asal sayıların sonsuzluğu, Gauss vb.).
    """
    return ProofCatalog.get_all_theorems()


@router.post("/api/v1/proof/verify-step", response_model=ProofVerifyStepResponse)
async def verify_proof_step_endpoint(req: ProofVerifyStepRequest) -> ProofVerifyStepResponse:
    """
    Hedef 15: Öğrencinin teorem ispat adımını denetler; safsata ve bilişsel hataları tespit eder.
    """
    try:
        res = ProofChecker.verify_step(
            theorem_id=req.theorem_id,
            step_number=req.step_number,
            student_statement=req.student_statement,
            selected_rule=req.selected_rule,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    vault_recorded = False
    detected_bug = res.get("detected_bug")

    # If no bug from ProofChecker, also test via misconception_detector
    if not detected_bug:
        diag = misconception_detector.detect(req.student_statement, req.problem_statement or "", "")
        if diag and diag.bug_id.startswith("BUG-LOGIC"):
            detected_bug = diag.bug_id
            res["is_valid"] = False
            res["feedback"] = diag.description

    if detected_bug and req.student_id:
        node_map = {
            "BUG-LOGIC-01": "N214",
            "BUG-LOGIC-02": "N217",
            "BUG-LOGIC-03": "N219",
            "BUG-LOGIC-04": "N226",
            "BUG-LOGIC-05": "N223",
        }
        node_id = node_map.get(detected_bug, "N211")
        cognitive_mistake_vault.record_mistake(
            user_id=req.student_id,
            node_id=node_id,
            bug_id=detected_bug,
            problem_statement=req.problem_statement or f"İspat Denetimi: {req.theorem_id} Adım {req.step_number}",
            offending_step=req.student_statement,
            correct_principle=res.get("feedback", "Mantıksal çıkarım kuralına uyulmalıdır."),
            remediation_directive="Çıkarım kurallarını ve ters varsayım/taban adımı ilkelerini gözden geçir.",
        )
        vault_recorded = True

    return ProofVerifyStepResponse(
        step_number=res["step_number"],
        is_valid=res["is_valid"],
        feedback=res["feedback"],
        expected_statement=res.get("expected_statement"),
        expected_justification=res.get("expected_justification"),
        detected_bug=detected_bug,
        vault_recorded=vault_recorded,
    )


@router.post("/api/v1/proof/induction/simulate")
async def simulate_induction_endpoint(req: InductionSimulateRequest) -> Dict[str, Any]:
    """
    Hedef 15: Matematiksel tümevarım domino zinciri simülasyonu.
    """
    if req.claim_type == "exp_ineq":
        # 2^n > n
        pred = lambda n: (2 ** n) > n
    else:
        # Gauss sum: sum(1..n) == n*(n+1)//2
        pred = lambda n: sum(range(1, n + 1)) == (n * (n + 1)) // 2

    return MathematicalInductionEngine.simulate_inductive_step(
        predicate=pred,
        start_k=req.start_k,
        test_range=req.test_range,
    )



