from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from app.models.schemas import DiagnosticPayload


class ProblemCategory(str, Enum):
    AGE = "AGE"
    MOTION = "MOTION"
    MIXTURE = "MIXTURE"
    WORK = "WORK"
    PERCENTAGE = "PERCENTAGE"
    OPTIMIZATION = "OPTIMIZATION"


class ModelingStage(str, Enum):
    STAGE_1_VARIABLE = "STAGE_1_VARIABLE"
    STAGE_2_EQUATION = "STAGE_2_EQUATION"
    STAGE_3_SOLVE = "STAGE_3_SOLVE"


class SchematicType(str, Enum):
    MOTION_TIMELINE = "MOTION_TIMELINE"
    MIXTURE_VESSEL = "MIXTURE_VESSEL"
    WORK_PROGRESS = "WORK_PROGRESS"
    PERCENTAGE_BAR = "PERCENTAGE_BAR"


class SchematicDiagramSpec(BaseModel):
    diagram_type: SchematicType
    title: str
    data: Dict[str, Any] = Field(default_factory=dict)


class ModelingProblemSpec(BaseModel):
    id: str = Field(..., description="Problem ID (örn: PROB_AGE_01)")
    category: ProblemCategory
    node_id: str = Field(..., description="Bağlı olduğu DAG düğümü (örn: N04, N10, N38)")
    title: str
    story_text: str = Field(..., description="Hikayeli problem metni")
    target_unknown_description: str = Field(..., description="Bulunması istenen ana büyüklüğün sözel tanımı")
    canonical_variable: str = Field("x", description="Önerilen ana değişken sembolü")
    acceptable_variables: List[str] = Field(default_factory=lambda: ["x", "y", "t", "v", "a", "k"])
    canonical_equation_str: str = Field(..., description="Kurulması gereken standart matematiksel eşitlik")
    alternative_equations: List[str] = Field(default_factory=list, description="Denk alternatif denklem kalıpları")
    canonical_solution_str: str = Field(..., description="x için çözülmüş sembolik/sayısal sonuç")
    domain_constraints: Dict[str, Any] = Field(
        default_factory=lambda: {"positive": True, "integer_only": False, "min_val": 0, "max_val": None},
        description="Gerçek dünya kısıtları (yaş pozitif ve tam sayı olmalı, hız pozitif vb.)"
    )
    socratic_hints: Dict[str, str] = Field(
        default_factory=dict,
        description="Aşamalara özgü Sokratik ipuçları"
    )
    schematic: Optional[SchematicDiagramSpec] = None


class ScaffoldStepRequest(BaseModel):
    session_id: str
    problem_id: str
    stage: ModelingStage
    student_input: str = Field(..., description="Öğrencinin ilgili aşamada girdiği yanıt (değişken, denklem veya çözüm adımı)")
    variable_name: Optional[str] = Field("x", description="Öğrencinin seçtiği değişken adı")
    previous_steps: List[str] = Field(default_factory=list)
    student_id: Optional[str] = Field("student_default", description="Öğrenci kimliği (Bilişsel Hata Kasası kaydı için)")
    client_timestamp: Optional[str] = None


class ScaffoldStepResponse(BaseModel):
    problem_id: str
    stage: ModelingStage
    is_valid: bool
    stage_completed: bool
    detected_bug: Optional[DiagnosticPayload] = None
    socratic_feedback: str
    next_stage: Optional[ModelingStage] = None
    domain_valid: Optional[bool] = None
    analysis_latency_ms: float = 0.0
    schematic_state_update: Optional[Dict[str, Any]] = None
