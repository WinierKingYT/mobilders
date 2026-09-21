import time
from fastapi import APIRouter
from app.models.schemas import (
    StrokeRecognitionRequest,
    StrokeRecognitionResponse,
    MultimodalStepVerificationRequest,
    MultimodalStepVerificationResponse,
    StepPsychometrics,
)
from app.cas.symbolic_engine import SecurityViolationError
from app.psychometrics.bkt import IndividualizedBKT
from app.ocr.models import MathScanRequest, MathScanResponse
from app.api.deps import (
    stroke_parser,
    cas_engine,
    misconception_detector,
    math_vision_pipeline,
    socratic_diagnoser,
)

router = APIRouter(tags=["Multimodal"])


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
