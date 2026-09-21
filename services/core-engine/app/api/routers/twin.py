from fastapi import APIRouter
from app.curriculum_generator.synthetic_twin_generator import (
    SyntheticTwinGenerator,
    TwinGenerateRequest,
    TwinQuestionResponse,
)

router = APIRouter(tags=["Synthetic Twin"])


@router.post("/api/v1/twin/generate", response_model=TwinQuestionResponse)
async def generate_synthetic_twin(req: TwinGenerateRequest) -> TwinQuestionResponse:
    """
    Öğrencinin kavramsal yanılgısına (bug_id) göre pedagojik hedefli,
    tam sayı köklere sahip taze bir izomorfik ikiz denklem üretir.
    """
    return SyntheticTwinGenerator.generate(
        bug_id=req.bug_id,
        original_equation=req.original_equation,
        difficulty_level=req.difficulty_level,
    )
