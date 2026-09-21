from fastapi import APIRouter
from app.models.schemas import (
    VoiceSocraticRequest,
    VoiceSocraticResponse,
)
from app.socratic.pipeline import SocraticRequest, InnerMonologueLog
from app.api.deps import socratic_pipeline, voice_engine

router = APIRouter(tags=["Socratic"])


@router.post("/api/v1/socratic/respond", response_model=InnerMonologueLog)
async def get_socratic_response(request: SocraticRequest) -> InnerMonologueLog:
    """
    4-Katmanlı İç Monolog hattı ve Zero-Leakage sübabı ile
    öğrenciye doğrudan cevabı vermeyen Sokratik rehberlik üretir.
    """
    return socratic_pipeline.process(request)


@router.post("/api/v1/voice/socratic-turn", response_model=VoiceSocraticResponse)
async def voice_socratic_turn(request: VoiceSocraticRequest) -> VoiceSocraticResponse:
    """
    Yazma güçlüğü çeken öğrenciler için konuşmadan-metne ve metinden-konuşmaya destekli,
    Zero-Leakage filtresiyle güvence altına alınmış Sokratik rehberlik sunar.
    """
    return voice_engine.process_voice_turn(request)
