from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field


class DiagnosticPayload(BaseModel):
    bug_id: Optional[str] = Field(None, description="Benzersiz bozuk kural kodu (örn. BUG-QUAD-01)")
    severity: str = Field("WARNING", description="Hata şiddeti: INFO | WARNING | CRITICAL")
    category: str = Field("ALGEBRAIC", description="Hata kategorisi")
    description: str = Field(..., description="Öğrencinin yaptığı hatanın zihinsel modeli")
    remediation_directive: str = Field(..., description="AI Tutor'a gönderilen pedagojik komut")
    offending_term: Optional[str] = Field(None, description="Hatalı terim veya adım")


class StepVerificationRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    node_id: str = Field("N15", description="Hedef DAG düğümü (örn: N12, N15, N18)")
    step_number: int = Field(1, ge=1, description="Sorudaki adım sırası")
    user_expression: str = Field(..., description="Öğrencinin girdiği cebirsel denklem veya ifade")
    target_equation: str = Field(..., description="Orijinal veya hedef denklem")
    previous_step: Optional[str] = Field(None, description="Bir önceki doğrulanmış adım")
    elapsed_ms: Optional[int] = Field(None, ge=0, description="Adımı yazarken geçen süre (milisaniye)")
    confidence_rating: Optional[float] = Field(None, ge=0.0, le=1.0, description="Metabilişsel güven beyanı")


class StepVerificationResponse(BaseModel):
    is_valid: bool = Field(..., description="Adım matematiksel olarak geçerli mi?")
    is_target_reached: bool = Field(..., description="Denklemin nihai çözümüne ulaşıldı mı?")
    detected_bug: Optional[DiagnosticPayload] = Field(None, description="Tespit edilen bozuk kural")
    canonical_expression: Optional[str] = Field(None, description="Sembolik standart form")
    error_message: Optional[str] = Field(None, description="Sözdizimi veya ayrıştırma hatası")
    analysis_latency_ms: float = Field(..., description="CAS analiz süresi")


class CATItemResponse(BaseModel):
    item_id: str = Field(..., description="Madde ID'si (örn: CAT-ITEM-01)")
    target_node_id: str = Field(..., description="Hedef bilgi grafı düğümü (örn: N12)")
    prompt: str = Field(..., description="Öğrenciye sunulan soru metni")
    difficulty_b: float = Field(..., description="2PL-IRT zorluk parametresi")
    discrimination_a: float = Field(..., description="2PL-IRT ayırt edicilik parametresi")


class CATNextItemRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    current_theta: float = Field(0.0, description="Anlık kestirilen latent yetenek")
    administered_item_ids: List[str] = Field(default_factory=list, description="Daha önce çözülmüş maddeler")


class CATSubmitRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    item_id: str = Field(..., description="Cevaplanan madde")
    is_correct: bool = Field(..., description="Cevap doğruluğu")
    administered_history: List[Tuple[str, bool]] = Field(
        default_factory=list, description="Önceki madde yanıt geçmişi [(item_id, is_correct), ...]"
    )


class CATSubmitResponse(BaseModel):
    theta_hat: float = Field(..., description="Güncellenmiş yetenek puanı")
    standard_error: float = Field(..., description="Kestirimin standart hatası SE(theta)")
    is_complete: bool = Field(..., description="Teşhis testi tamamlandı mı?")
    next_item: Optional[CATItemResponse] = Field(None, description="Test bitmediyse sıradaki en bilgilendirici madde")
    seeded_mastery: Optional[Dict[str, float]] = Field(None, description="Test bittiğinde 20 düğümün başlangıç olasılıkları")
    zpd_candidates: Optional[List[str]] = Field(None, description="Öğrencinin çalışmaya başlaması gereken ZPD düğümleri")
