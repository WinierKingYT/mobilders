import time
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    StepVerificationRequest,
    StepVerificationResponse,
    CATNextItemRequest,
    CATItemResponse,
    CATSubmitRequest,
    CATSubmitResponse,
)
from app.cas.symbolic_engine import SymbolicEquivalenceEngine, SecurityViolationError
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.graph.knowledge_dag import KnowledgeDAG
from app.adaptive.cat_engine import CATEngine

router = APIRouter(tags=["Session, Verification & Diagnostic"])

# Tekil motor örnekleri (Singletons)
cas_engine = SymbolicEquivalenceEngine()
misconception_detector = QuadraticMisconceptionDetector(cas_engine)
knowledge_dag = KnowledgeDAG()
cat_engine = CATEngine(dag=knowledge_dag)


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

        return StepVerificationResponse(
            is_valid=is_equiv,
            is_target_reached=is_equiv and ("=" in request.user_expression and not ("**2" in request.user_expression or "^2" in request.user_expression)),
            detected_bug=detected_bug,
            canonical_expression=diff_str if is_equiv else None,
            error_message=None,
            analysis_latency_ms=total_latency_ms,
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
