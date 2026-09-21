from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from app.vault.mistake_vault import (
    MistakeRecord,
    MistakeStatus,
)
from app.api.deps import (
    cognitive_mistake_vault,
    self_correction_manager,
    boss_battle_engine,
)

router = APIRouter(tags=["Mistake Vault"])


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


@router.get("/api/v1/vault/misconception-profile/{user_id}")
async def get_misconception_profile(user_id: str) -> Dict[str, Any]:
    """Öğrencinin kavramsal yanılgı profilini ve görselleştirilmiş hata ağacı verisini döner."""
    return cognitive_mistake_vault.get_misconception_profile(user_id=user_id)


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
