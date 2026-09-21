from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from app.geometry.analytic_geometry import solve_analytic_geometry
from app.geometry.synthetic_geometry import solve_synthetic_geometry
from app.api.deps import (
    misconception_detector,
    cognitive_mistake_vault,
)

router = APIRouter(tags=["Geometry"])


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
