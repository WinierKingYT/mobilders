from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from app.models.schemas import DiagnosticPayload


class WeaknessSeverity(str, Enum):
    SLIP = "SLIP"                       # Basit işlem/aritmetik dikkatsizliği
    MISCONCEPTION = "MISCONCEPTION"     # Lise müfredatı kavram yanılgısı (örn: BUG-QUAD-01)
    ROOT_DEFICIT = "ROOT_DEFICIT"       # Seviye -3..-1 kök önkoşul eksikliği (örn: BUG-FOUND-01..15)


class RootNode(BaseModel):
    id: str = Field(..., description="Kök düğüm kodu (örn: N_ROOT_01)")
    canonical_code: str
    title: str
    level: float = Field(..., description="Negatif seviye (-3.0 .. -1.0)")
    strict_prereqs: List[str] = Field(default_factory=list)
    description: str


class ZeroBaselineDiagnosticQuestion(BaseModel):
    question_id: str
    node_id: str
    question_text: str
    options: List[str]
    correct_index: int
    concept_tested: str


class ZeroBaselineEvaluationRequest(BaseModel):
    student_id: str
    answers: Dict[str, int] = Field(..., description="question_id -> seçilen seçenek indeksi")


class ZeroBaselineEvaluationResponse(BaseModel):
    student_id: str
    needs_root_pathway: bool
    recommended_starting_node: str
    score_ratio: float
    diagnoses: List[str]


class WeaknessEntry(BaseModel):
    id: str
    student_id: str
    node_id: str
    bug_id: Optional[str] = None
    severity: WeaknessSeverity
    context_step: str
    timestamp: str
    p_l_penalty: float = 0.15


class SubgoalStep(BaseModel):
    subgoal_id: str
    order: int
    title: str
    prompt: str
    expected_answer_str: str
    socratic_hint: str
    explanation: str


class CoSolveRequest(BaseModel):
    session_id: str
    subgoal_id: str
    student_answer: str
    elapsed_seconds: float = 0.0


class CoSolveResponse(BaseModel):
    session_id: str
    subgoal_id: str
    is_valid: bool
    subgoal_completed: bool
    feedback: str
    next_subgoal: Optional[SubgoalStep] = None
    all_completed: bool = False
    hesitation_whisper: Optional[str] = None
    source_unpacker_data: Optional[Dict[str, Any]] = None


class SandboxSessionRequest(BaseModel):
    student_id: str
    root_node_id: str
    trigger_error_step: str


class SandboxSessionResponse(BaseModel):
    sandbox_id: str
    root_node_id: str
    tool_type: str  # 'NUMBER_LINE' | 'PIE_FRACTION' | 'BALANCE_SCALE'
    instruction: str
    expected_action: Dict[str, Any]
    is_resolved: bool = False
    is_quarantined: bool = True
    frozen_p_l: Optional[float] = None
    frozen_theta: Optional[float] = None
