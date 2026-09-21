from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from fastapi import APIRouter
from app.models.schemas import (
    CurriculumListResponse,
    LTILaunchPayload,
    LTIGradeScoreRequest,
    ClassroomAnalyticsResponse,
    CurriculumSynthesizeRequest,
    SynthesizedCurriculumResponse,
)
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.api.deps import (
    curriculum_registry,
    lti_service,
    classroom_reporter,
    local_analytics,
    curriculum_synthesizer,
    knowledge_dag,
    atlas_engine,
)

router = APIRouter(tags=["Curriculum, Analytics, LTI & Atlas"])


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


@router.post("/api/v1/curriculum/synthesize", response_model=SynthesizedCurriculumResponse)
async def synthesize_curriculum(request: CurriculumSynthesizeRequest) -> SynthesizedCurriculumResponse:
    """
    İleri matematik konusunu girdi alarak 30 düğümlü döngüsüz Bilgi Grafı (DAG),
    kavram yanılgısı kataloğu ve SymPy ile formel olarak kanıtlanmış öğrenme adımları sentezler.
    """
    return curriculum_synthesizer.synthesize(request)


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


@router.get("/api/v1/classroom/analytics", response_model=ClassroomAnalyticsResponse)
async def get_classroom_analytics(
    cohort_id: str = "CLASS-10A", students: int = 28
) -> ClassroomAnalyticsResponse:
    """
    Öğretmenler için öğrencilerin ZPD dağılımını, yaygın bozuk kuralları ve Paas bilişsel
    yük indeksini kişisel veri içermeksizin (Zero-PII) raporlar.
    """
    safe_students = max(5, min(1000, students))
    safe_cohort_id = str(cohort_id)[:50]
    return classroom_reporter.generate_classroom_report(cohort_id=safe_cohort_id, student_count=safe_students)


@router.get("/api/v1/analytics/student/{student_id}")
async def get_student_analytics(student_id: str) -> Dict[str, Any]:
    """
    Öğrencinin metabilişsel kalibrasyon, Paas bilişsel verimlilik (E),
    14 günlük FSRS kalıcılık projeksiyonu ve 26 düğümlü Cebir Atlası analitiği.
    """
    return local_analytics.generate_student_report(student_id)


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


class AtlasPayloadRequest(BaseModel):
    mastered_ids: List[str] = []


class AtlasBottlenecksRequest(BaseModel):
    mastered_ids: List[str] = []
    top_k: int = 5


@router.get("/api/v1/atlas/summary")
async def get_atlas_summary_endpoint() -> Dict[str, Any]:
    """
    Hedef 16: 246 Düğümlü Bütünleşik Zihin Ağı alan özeti ve toplam düğüm sayısı.
    """
    return {
        "total_nodes": atlas_engine.get_total_nodes(),
        "domains": atlas_engine.get_domain_summary(),
    }


@router.post("/api/v1/atlas/payload")
async def get_atlas_payload_endpoint(req: AtlasPayloadRequest) -> Dict[str, Any]:
    """
    Hedef 16: Öğrencinin posterior ustalığına göre ZPD, Mastered ve Locked durumlu tam graf payload'u.
    """
    safe_mastered = set(req.mastered_ids[:500])
    return atlas_engine.generate_atlas_payload(safe_mastered)


@router.post("/api/v1/atlas/bottlenecks")
async def get_atlas_bottlenecks_endpoint(req: AtlasBottlenecksRequest) -> List[Dict[str, Any]]:
    """
    Hedef 16: Öğrencinin ilerlemesini tıkayan kritik darboğaz (bottleneck) düğümleri tespiti.
    """
    safe_mastered = set(req.mastered_ids[:500])
    safe_top_k = max(1, min(50, req.top_k))
    return atlas_engine.find_critical_bottlenecks(safe_mastered, top_k=safe_top_k)


@router.post("/api/v1/atlas/zpd")
async def get_atlas_zpd_endpoint(req: AtlasPayloadRequest) -> List[str]:
    """
    Hedef 16: Öğrencinin Yakınsak Gelişim Alanı (ZPD) sınırındaki hazır düğümler.
    """
    safe_mastered = set(req.mastered_ids[:500])
    return atlas_engine.compute_zpd_frontier(safe_mastered)


@router.post("/api/v1/atlas/progress")
async def get_atlas_progress_endpoint(req: AtlasPayloadRequest) -> Dict[str, Any]:
    """
    Hedef 16: Müfredatın genel ve alan bazlı yüzde tamamlama oranları.
    """
    safe_mastered = set(req.mastered_ids[:500])
    return atlas_engine.calculate_curriculum_progress(safe_mastered)
