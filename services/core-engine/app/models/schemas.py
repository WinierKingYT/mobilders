from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field


class DiagnosticPayload(BaseModel):
    bug_id: Optional[str] = Field(None, description="Benzersiz bozuk kural kodu (örn. BUG-QUAD-01)")
    severity: str = Field("WARNING", description="Hata şiddeti: INFO | WARNING | CRITICAL")
    category: str = Field("ALGEBRAIC", description="Hata kategorisi")
    description: str = Field(..., description="Öğrencinin yaptığı hatanın zihinsel modeli")
    remediation_directive: str = Field(..., description="AI Tutor'a gönderilen pedagojik komut")
    offending_term: Optional[str] = Field(None, description="Hatalı terim veya adım")


class StepPsychometrics(BaseModel):
    bkt_posterior_p_l: float = Field(..., description="Güncellenmiş ustalık olasılığı P(L_t | obs)")
    bkt_next_p_l: float = Field(..., description="Bir sonraki adım için yansıtılan ustalık olasılığı P(L_t+1)")
    ddm_drift_rate: Optional[float] = Field(None, description="Ratcliff DDM sürüklenme hızı (v)")
    ddm_boundary_separation: Optional[float] = Field(None, description="Ratcliff DDM temkinlilik / sınır mesafesi (a)")
    ddm_cognitive_state: Optional[str] = Field(None, description="Bilişsel profil teşhisi (fluent_mastery, cautious_effort, vb.)")


class StepVerificationRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    node_id: str = Field("N15", description="Hedef DAG düğümü (örn: N12, N15, N18)")
    step_number: int = Field(1, ge=1, description="Sorudaki adım sırası")
    user_expression: str = Field(..., description="Öğrencinin girdiği cebirsel denklem veya ifade")
    target_equation: str = Field(..., description="Orijinal veya hedef denklem")
    previous_step: Optional[str] = Field(None, description="Bir önceki doğrulanmış adım")
    elapsed_ms: Optional[int] = Field(None, ge=0, description="Adımı yazarken geçen süre (milisaniye)")
    confidence_rating: Optional[float] = Field(None, ge=0.0, le=1.0, description="Metabilişsel güven beyanı")
    current_p_l: Optional[float] = Field(0.20, ge=0.0, le=1.0, description="Mevcut BKT ustalık düzeyi P(L)")
    client_msg_id: Optional[str] = Field(None, description="Çevrimdışı ve tekrar oynatma idempotentlik anahtarı (UUID)")
    client_timestamp: Optional[str] = Field(None, description="İstemcide adımın atıldığı anlık ISO zaman damgası")


class StepVerificationResponse(BaseModel):
    is_valid: bool = Field(..., description="Adım matematiksel olarak geçerli mi?")
    is_target_reached: bool = Field(..., description="Denklemin nihai çözümüne ulaşıldı mı?")
    detected_bug: Optional[DiagnosticPayload] = Field(None, description="Tespit edilen bozuk kural")
    canonical_expression: Optional[str] = Field(None, description="Sembolik standart form")
    error_message: Optional[str] = Field(None, description="Sözdizimi veya ayrıştırma hatası")
    analysis_latency_ms: float = Field(..., description="CAS analiz süresi")
    psychometrics: Optional[StepPsychometrics] = Field(None, description="Anlık bilişsel ve psikometrik kestirim")
    is_replayed: bool = Field(False, description="Idempotent önbellekten veya çevrimdışı kuyruktan mı döndü?")


class OfflineBatchReplayRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    events: List[StepVerificationRequest] = Field(..., description="Çevrimdışı kaydedilen adımlar listesi")


class OfflineBatchReplayResponse(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    synced_count: int = Field(..., description="Başarıyla işlenen ve senkronize edilen adım sayısı")
    replayed_steps: List[StepVerificationResponse] = Field(..., description="Doğrulanan adımların yanıtları")
    latest_p_l: float = Field(..., description="Tüm adımlardan sonra güncellenen BKT ustalık düzeyi")
    is_target_reached: bool = Field(..., description="Hedef denklemin nihai çözümüne ulaşıldı mı?")


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
    curriculum: Optional[str] = Field("DEFAULT", description="Müfredat filtresi (DEFAULT, MEB, IB, CCSS, AP)")


class CATSubmitRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    item_id: str = Field(..., description="Cevaplanan madde")
    is_correct: bool = Field(..., description="Cevap doğruluğu")
    administered_history: List[Tuple[str, bool]] = Field(
        default_factory=list, description="Önceki madde yanıt geçmişi [(item_id, is_correct), ...]"
    )
    curriculum: Optional[str] = Field("DEFAULT", description="Müfredat filtresi")


class CATSubmitResponse(BaseModel):
    theta_hat: float = Field(..., description="Güncellenmiş yetenek puanı")
    standard_error: float = Field(..., description="Kestirimin standart hatası SE(theta)")
    is_complete: bool = Field(..., description="Teşhis testi tamamlandı mı?")
    next_item: Optional[CATItemResponse] = Field(None, description="Test bitmediyse sıradaki en bilgilendirici madde")
    seeded_mastery: Optional[Dict[str, float]] = Field(None, description="Test bittiğinde 20 düğümün başlangıç olasılıkları")
    zpd_candidates: Optional[List[str]] = Field(None, description="Öğrencinin çalışmaya başlaması gereken ZPD düğümleri")


# ==========================================
# MULTIMODAL INKING SCHEMAS
# ==========================================

class StrokePoint(BaseModel):
    x: float = Field(..., description="X koordinatı")
    y: float = Field(..., description="Y koordinatı")
    t: Optional[int] = Field(None, description="Zaman damgası (ms)")
    p: Optional[float] = Field(1.0, description="Kalem basıncı (0.0 - 1.0)")


class InkingStroke(BaseModel):
    id: Optional[str] = Field(None, description="Çizgi ID")
    points: List[StrokePoint] = Field(..., description="Çizgiyi oluşturan noktalar dizisi")


class StrokeRecognitionRequest(BaseModel):
    strokes: List[InkingStroke] = Field(..., description="Kullanıcının çizdiği serbest el yazısı çizgileri")
    session_id: Optional[str] = Field(None, description="Oturum ID")


class StrokeRecognitionResponse(BaseModel):
    raw_latex: str = Field(..., description="Tanınan ham LaTeX ifadesi")
    sympy_expression: str = Field(..., description="SymPy uyumlu cebirsel ifade")
    confidence: float = Field(..., description="Nöro-sembolik tanıma güven skoru (0.0 - 1.0)")
    segmented_tokens: List[str] = Field(default_factory=list, description="Ayrıştırılan token listesi")
    parsing_latency_ms: float = Field(..., description="Ayrıştırma gecikmesi (ms)")


class MultimodalStepVerificationRequest(BaseModel):
    strokes: List[InkingStroke] = Field(..., description="Çizilen el yazısı çizgileri")
    session_id: str = Field(..., description="Oturum UUID")
    node_id: str = Field("N15", description="Hedef DAG düğümü")
    step_number: int = Field(1, ge=1, description="Adım numarası")
    target_equation: str = Field(..., description="Orijinal veya hedef denklem")
    previous_step: Optional[str] = Field(None, description="Önceki geçerli adım")
    elapsed_ms: Optional[int] = Field(None, ge=0, description="Çizim süresi (ms)")
    confidence_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    current_p_l: Optional[float] = Field(0.20, ge=0.0, le=1.0)


class MultimodalStepVerificationResponse(BaseModel):
    recognized_latex: str = Field(..., description="Çizimden tanınan LaTeX")
    recognized_sympy: str = Field(..., description="SymPy uyumlu ifade")
    is_valid: bool = Field(..., description="Cebirsel eşdeğerlik geçerli mi?")
    is_target_reached: bool = Field(..., description="Hedefe ulaşıldı mı?")
    detected_bug: Optional[DiagnosticPayload] = Field(None, description="Tespit edilen bozuk kural")
    canonical_expression: Optional[str] = Field(None, description="Sembolik standart biçim")
    error_message: Optional[str] = Field(None, description="Hata mesajı")
    recognition_confidence: float = Field(..., description="Çizgi tanıma güven skoru")
    total_latency_ms: float = Field(..., description="Toplam işlem süresi")
    psychometrics: Optional[StepPsychometrics] = Field(None, description="Bilişsel model çıktısı")


# ==========================================
# CURRICULUM & LOCALIZATION SCHEMAS
# ==========================================

class CurriculumStandard(BaseModel):
    standard_id: str = Field(..., description="Standart kazanım kodu (örn: MEB-10.4.1.1, CCSS-HSA-REI.B.4)")
    curriculum: str = Field(..., description="Müfredat adı (MEB, IB_AA, IB_AI, CCSS, AP_PRECALC)")
    node_id: str = Field(..., description="Eşleştiği Bilgi Grafı Düğüm ID'si")
    title_tr: str = Field(..., description="Türkçe kazanım başlığı")
    title_en: str = Field(..., description="İngilizce standard başlığı")
    description_tr: str = Field(..., description="Türkçe açıklama")
    description_en: str = Field(..., description="İngilizce açıklama")
    grade_level: str = Field(..., description="Hedef sınıf/seviye (örn: 10, DP1, High School)")


class CurriculumListResponse(BaseModel):
    curricula: List[str] = Field(..., description="Desteklenen müfredatlar listesi")
    total_standards: int = Field(..., description="Toplam standart sayısı")
    standards: List[CurriculumStandard] = Field(..., description="Kazanım standartları listesi")


# ==========================================
# CLASSROOM ANALYTICS & LTI 1.3 SCHEMAS
# ==========================================

class BuggyRuleOccurrence(BaseModel):
    bug_id: str
    count: int
    percentage: float
    description: str
    recommended_scaffolding: str


class ClassroomAnalyticsResponse(BaseModel):
    cohort_id: str = Field(..., description="Sınıf / Grup ID")
    total_students: int = Field(..., description="Gruptaki anonim öğrenci sayısı")
    zpd_distribution: Dict[str, int] = Field(..., description="Düğümlere göre ZPD'de olan öğrenci sayıları")
    active_buggy_rules: List[BuggyRuleOccurrence] = Field(..., description="En sık rastlanan kavram yanılgıları")
    paas_cognitive_efficiency: Dict[str, float] = Field(..., description="Ortalama Paas E indeksi ve bileşenleri")
    curriculum_coverage_pct: float = Field(..., description="Sınıfın müfredat kapsama / yetkinlik yüzdesi")
    zero_pii_compliant: bool = Field(True, description="Kişisel veri içermez güvencesi")


class LTILaunchPayload(BaseModel):
    iss: str = Field(..., description="LMS Issuer URL")
    login_hint: str = Field(..., description="LMS login hint")
    target_link_uri: str = Field(..., description="Hedef LTI başlatma URL'i")
    client_id: Optional[str] = Field(None, description="LMS Client ID")
    lti_message_hint: Optional[str] = Field(None, description="LMS LTI message hint")


class LTIGradeScoreRequest(BaseModel):
    line_item_id: str = Field(..., description="LMS Not hanesi / LineItem ID")
    student_pseudonym_id: str = Field(..., description="Anonim öğrenci takma adı (Zero-PII)")
    score_given: float = Field(..., ge=0.0, description="Verilen puan")
    score_maximum: float = Field(100.0, gt=0.0, description="Maksimum puan")
    activity_progress: str = Field("Completed", description="Initialized, Started, InProgress, Submitted, Completed")
    grading_progress: str = Field("FullyGraded", description="FullyGraded, Pending, Failed")
    comment: Optional[str] = Field(None, description="Öğretmen/sistem notu")


# ==========================================
# VOICE SOKRATIC SCHEMAS
# ==========================================

class VoiceSocraticRequest(BaseModel):
    session_id: str = Field(..., description="Oturum UUID")
    audio_transcript: str = Field(..., description="Öğrencinin konuştuğu cümlenin metni (STT çıktısı)")
    target_equation: str = Field(..., description="Çalışılan denklem")
    previous_step: Optional[str] = Field(None, description="Önceki doğrulanmış adım")
    solution_roots: List[float] = Field(default_factory=list, description="Kökler (Zero-Leak filtresi için)")
    language: str = Field("tr", description="Dil kodu: tr veya en")


class VoiceSocraticResponse(BaseModel):
    socratic_guidance_text: str = Field(..., description="Sokratik rehber metni")
    audio_stream_url: Optional[str] = Field(None, description="Sentezlenen ses dosyasının veya akışının URL'i")
    zero_leakage_enforced: bool = Field(True, description="Cevap kaçırma filtresi devrede miydi?")
    socratic_ratio: float = Field(..., description="Soru / açıklama oranı")
    latency_ms: float = Field(..., description="İşlem süresi (ms)")
    normalized_transcript: Optional[str] = Field(None, description="VAD ve matematik normalizasyonundan geçmiş girdi")
    vad_filtered: bool = Field(False, description="Gürültü veya nefes sesi filtrelendi mi?")


# ==========================================
# AUTONOMOUS CURRICULUM GENERATOR SCHEMAS
# ==========================================

class CurriculumSynthesizeRequest(BaseModel):
    topic: str = Field(..., description="İleri matematik konusu (örn: Logarithms, Trigonometry, Limits)")
    target_grade: str = Field("Grade 11-12", description="Hedef seviye")
    language: str = Field("tr", description="Müfredat dili ('tr' veya 'en')")


class SynthesizedNodeSchema(BaseModel):
    id: str
    canonical_code: str
    title: str
    level: int
    strict_prereqs: List[str]
    default_difficulty_b: float
    discrimination_a: float
    description: str
    formal_proof_verified: bool


class SynthesizedCurriculumResponse(BaseModel):
    topic: str = Field(..., description="Sentezlenen matematik konusu")
    total_nodes: int = Field(..., description="Üretilen toplam düğüm sayısı")
    is_cycle_free: bool = Field(True, description="Kahn algoritması döngüsüzlük teyidi")
    topological_order: List[str] = Field(..., description="Topolojik önkoşul sırası")
    formal_verification_passed: bool = Field(..., description="SymPy teorem kanıtı teyidi")
    nodes: List[SynthesizedNodeSchema] = Field(..., description="30 düğümlü Bilgi Grafı")
    buggy_rules: List[Dict[str, Any]] = Field(..., description="Konuya özel kavram yanılgısı kataloğu")


# ==========================================
# SYNTHETIC TWIN COHORT SIMULATION SCHEMAS
# ==========================================

class SimulationCohortRequest(BaseModel):
    cohort_size: int = Field(100000, ge=100, le=500000, description="Sentetik öğrenci sayısı (varsayılan: 100.000)")
    virtual_days: int = Field(30, ge=1, le=180, description="Hızlandırılmış sanal gün sayısı")
    topic: str = Field("QUADRATICS", description="Simüle edilecek müfredat konusu")
    personas_distribution: Optional[Dict[str, float]] = Field(
        None, description="Persona oranları: fast_forgetter, overconfident, imposter, slip_prone, fluent_master"
    )


class PersonaOutcomeMetrics(BaseModel):
    persona_name: str
    count: int
    mean_mastery_pct: float
    mean_retention_30d: float
    mean_ece_calibration: float
    mean_rt_seconds: float
    dropout_or_quarantine_pct: float


class SimulationCohortResponse(BaseModel):
    cohort_size: int = Field(..., description="Simüle edilen toplam sentetik öğrenci sayısı")
    virtual_days: int = Field(..., description="Sanal gün süresi")
    total_learning_trials: int = Field(..., description="Toplam yürütülen öğrenme adımı sayısı")
    overall_completion_rate: float = Field(..., description="Müfredat tamamlama oranı")
    persona_outcomes: List[PersonaOutcomeMetrics] = Field(..., description="Persona bazlı çıktılar")
    bottleneck_nodes: List[Dict[str, Any]] = Field(..., description="Empirik olarak elenen dar boğaz düğümleri")
    runtime_seconds: float = Field(..., description="Simülasyon yürütme süresi (saniye)")


# ==========================================
# OPEN SCIENCE BENCHMARK & DP SCHEMAS
# ==========================================

class DPExportRequest(BaseModel):
    epsilon: float = Field(1.0, gt=0.0, le=10.0, description="Diferansiyel gizlilik bütçesi (epsilon)")
    delta: float = Field(1e-5, ge=0.0, le=1e-3, description="Diferansiyel gizlilik delta parametresi")
    max_records: int = Field(1000, ge=10, le=50000, description="Dışa aktarılacak maksimum anonim kayıt")


class DPExportResponse(BaseModel):
    epsilon: float = Field(..., description="Uygulanan diferansiyel gizlilik epsilon değeri")
    delta: float = Field(..., description="Uygulanan delta değeri")
    records_exported: int = Field(..., description="Dışa aktarılan anonim kayıt sayısı")
    zero_pii_verified: bool = Field(True, description="Sıfır-PII güvencesi")
    dataset: List[Dict[str, Any]] = Field(..., description="Laplace gürültüsü eklenmiş araştırma veri seti")


class CognitiveModelScore(BaseModel):
    model_name: str
    category: str
    auc_roc: float
    rmse: float
    brier_score: float
    log_likelihood: float
    latency_per_step_ms: float
    rank: int


class LeaderboardResponse(BaseModel):
    benchmark_dataset: str = Field(..., description="Değerlendirmede kullanılan kıyas veri seti")
    evaluated_at: str = Field(..., description="Değerlendirme zaman damgası")
    total_models: int = Field(..., description="Sıralanan model sayısı")
    leaderboard: List[CognitiveModelScore] = Field(..., description="Psikometri ve Bilişsel Bilim Liderlik Tablosu")


