import time
from typing import Optional, Dict, Any
from fastapi import APIRouter
from app.models.schemas import (
    CATNextItemRequest,
    CATItemResponse,
    CATSubmitRequest,
    CATSubmitResponse,
)
from app.api.deps import cat_engine, knowledge_dag

router = APIRouter(tags=["Diagnostic"])


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
    # 1. Yanıt geçmişine son maddeyi ekle (mükerrer ağ isteklerine karşı idempotent)
    updated_history = list(request.administered_history)
    if not any(item[0] == request.item_id for item in updated_history):
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
