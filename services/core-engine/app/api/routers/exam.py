from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    SimulationCohortRequest,
    SimulationCohortResponse,
    DPExportRequest,
    DPExportResponse,
    LeaderboardResponse,
)
from app.modeling.models import (
    ScaffoldStepRequest,
    ScaffoldStepResponse,
    ModelingProblemSpec,
)
from app.root_pedagogy.models import (
    ZeroBaselineEvaluationRequest,
    ZeroBaselineEvaluationResponse,
    CoSolveRequest,
    CoSolveResponse,
    SandboxSessionRequest,
    SandboxSessionResponse,
    WeaknessEntry,
    RootNode,
)
from app.curriculum_generator.trap_question_factory import (
    ExamSection,
    TrapQuestion,
    DynamicExam,
    ExamDocumentExporter,
    FormalQuestionVerifier,
)
from app.probability.combinatorics_engine import (
    solve_combinatorics_or_probability,
    MonteCarloProbabilitySimulator,
)
from app.logic.proof_lab import (
    TruthTableGenerator,
    ProofCatalog,
    ProofChecker,
    MathematicalInductionEngine,
    logic_and,
    logic_or,
    logic_not,
    logic_implies,
    logic_iff,
    logic_xor,
)
from app.api.deps import (
    simulation_factory,
    dp_exporter,
    model_benchmark,
    modeling_scaffold_engine,
    zero_baseline_diagnostic,
    active_cosolver,
    weakness_ledger,
    insitu_sandbox,
    root_dag,
    dynamic_exam_factory,
    trap_question_generator,
    misconception_detector,
    cognitive_mistake_vault,
)

router = APIRouter(tags=["Exam, Research, Modeling, Probability & Proof"])


# --- Simulation & Research ---

@router.post("/api/v1/simulation/run-cohort", response_model=SimulationCohortResponse)
async def run_cohort_simulation(request: SimulationCohortRequest) -> SimulationCohortResponse:
    """
    Farklı bilişsel profillere sahip 100.000 sentetik öğrenci ikizi üzerinde
    30 günlük sanal zaman hızlandırmasıyla Monte Carlo simülasyonu yürütür ve dar boğazları eler.
    """
    return simulation_factory.run_simulation(request)


@router.post("/api/v1/research/export/dp-dataset", response_model=DPExportResponse)
async def export_dp_research_dataset(request: DPExportRequest) -> DPExportResponse:
    """
    Bilişsel bilim araştırmacıları için tamamen anonimleştirilmiş (sıfır-PII),
    diferansiyel gizlilik (epsilon-DP) korumalı açık veri seti üretir.
    """
    return dp_exporter.export_dataset(request)


@router.get("/api/v1/research/leaderboard", response_model=LeaderboardResponse)
async def get_cognitive_models_leaderboard() -> LeaderboardResponse:
    """
    iBKT, DDM, FSRS ve IRT modellerinin kestirimsel başarılarını karşılaştıran
    küresel Öğrenme Bilimleri Liderlik Tablosunu döner.
    """
    return model_benchmark.get_leaderboard()


# --- Modeling ---

@router.post("/api/v1/modeling/scaffold/step", response_model=ScaffoldStepResponse)
async def evaluate_modeling_scaffold_step(request: ScaffoldStepRequest) -> ScaffoldStepResponse:
    """
    Hedef 8: Yeni Nesil Hikayeli Problemler ve Modelleme Motoru (Word Problems & Modeling).
    3 Aşamalı Modelleme İskelesi:
    1. Değişken Tanımla (Variable Identification)
    2. Eşitliği Kur (Equation Formulation & Buggy Rule Check)
    3. Adım Adım Çöz & Gerçek Dünya Kısıtları (CAS Solution & Domain Guard)
    """
    return modeling_scaffold_engine.evaluate_step(request)


@router.get("/api/v1/modeling/problems", response_model=List[ModelingProblemSpec])
async def list_modeling_problems() -> List[ModelingProblemSpec]:
    """Sistemdeki tüm standart modelleme problemlerini listeler."""
    return list(modeling_scaffold_engine.problem_bank.values())


@router.get("/api/v1/modeling/problem/{problem_id}", response_model=ModelingProblemSpec)
async def get_modeling_problem(problem_id: str) -> ModelingProblemSpec:
    """Belirli bir modelleme probleminin tanımını ve şematik verilerini döner."""
    prob = modeling_scaffold_engine.problem_bank.get(problem_id)
    if not prob:
        raise HTTPException(status_code=404, detail=f"Problem {problem_id} bulunamadı.")
    return prob


# --- Root Pedagogy ---

@router.post("/api/v1/root/diagnostic/evaluate", response_model=ZeroBaselineEvaluationResponse)
async def evaluate_zero_baseline(request: ZeroBaselineEvaluationRequest) -> ZeroBaselineEvaluationResponse:
    """
    Hedef 2: Sıfır Tabanlı Bilişsel Sezgi Testi Değerlendirme API'si.
    Öğrencinin 3 temel soruya verdiği cevaplara göre kök patika gereksinimini tespit eder.
    """
    return zero_baseline_diagnostic.evaluate(request)


@router.post("/api/v1/root/cosolve/subgoal", response_model=CoSolveResponse)
async def process_cosolve_subgoal(request: CoSolveRequest) -> CoSolveResponse:
    """
    Hedef 3: Aktif Birlikte Çözme Motoru (Faded Worked Examples & Subgoal Labeling).
    Öğrencinin mikro alt hedefteki cevabını denetler, 8s üzerinde hareketsizlikte fısıltı ve kaynak açıcı sunar.
    """
    resp = active_cosolver.process_subgoal_step(request)
    if not resp.is_valid:
        weakness_ledger.log_error(
            student_id=request.session_id,
            node_id="N_ROOT_SUBGOAL",
            user_step=request.student_answer,
            elapsed_seconds=request.elapsed_seconds,
        )
    return resp


@router.post("/api/v1/root/sandbox/session", response_model=SandboxSessionResponse)
async def create_sandbox_session(request: SandboxSessionRequest) -> SandboxSessionResponse:
    """
    Hedef 3: In-Situ Mikro-Kum Havuzu Başlatma API'si.
    Lise sorusunda kök hata yapıldığında ana soruyu dondurur ve 45 saniyelik görsel aracı açar.
    """
    return insitu_sandbox.create_sandbox(request)


@router.get("/api/v1/root/weaknesses/{student_id}", response_model=List[WeaknessEntry])
async def get_student_weaknesses(student_id: str) -> List[WeaknessEntry]:
    """Hedef 3: Bilişsel Zaaf Defteri kayıtlarını döndürür."""
    return weakness_ledger.get_student_weaknesses(student_id)


@router.get("/api/v1/root/dag/nodes", response_model=List[RootNode])
async def list_root_dag_nodes() -> List[RootNode]:
    """Hedef 2: Kök Bilgi Grafı'ndaki (N_ROOT_01 - N_ROOT_16) tüm düğümleri döner."""
    return list(root_dag.nodes.values())


# --- Dynamic Exam & Trap Questions ---

class ExamGenerateRequest(BaseModel):
    section: ExamSection = ExamSection.TYT_MATEMATIK
    question_count: int = 10
    target_theta: float = 0.0


class ExamGradeRequest(BaseModel):
    exam: DynamicExam
    answers: Dict[int, int]


class ExamExportRequest(BaseModel):
    exam: DynamicExam
    format: str = "html"  # "html" veya "latex"
    include_solutions: bool = True


class TargetedQuestionRequest(BaseModel):
    bug_id: str
    seed: Optional[int] = None


class QuestionVerifyRequest(BaseModel):
    question: TrapQuestion


@router.post("/api/v1/exam/generate", response_model=DynamicExam)
async def generate_dynamic_exam(req: ExamGenerateRequest) -> DynamicExam:
    """Belirtilen sınav tipine, soru adedine ve hedef teta düzeyine göre bilişsel tuzaklı deneme sınavı üretir."""
    import math
    safe_count = max(1, min(200, req.question_count))
    safe_theta = req.target_theta if math.isfinite(req.target_theta) else 0.0
    safe_theta = max(-4.0, min(4.0, safe_theta))
    return dynamic_exam_factory.assemble_exam(
        section=req.section,
        question_count=safe_count,
        target_theta=safe_theta,
    )


@router.post("/api/v1/exam/grade")
async def grade_dynamic_exam(req: ExamGradeRequest) -> Dict[str, Any]:
    """Dinamik deneme sınavını puanlar ve tetiklenen bilişsel tuzakları (BUG-ID) raporlar."""
    return dynamic_exam_factory.grade_exam(
        exam=req.exam,
        answers=req.answers,
    )


@router.post("/api/v1/exam/export")
async def export_dynamic_exam(req: ExamExportRequest) -> Dict[str, Any]:
    """Deneme sınavını derlenebilir LaTeX veya yazdırılabilir HTML / PDF formatında dışa aktarır."""
    if req.format.lower() == "latex":
        content = ExamDocumentExporter.export_to_latex(req.exam, include_solutions=req.include_solutions)
    else:
        content = ExamDocumentExporter.export_to_html_printable(req.exam, include_solutions=req.include_solutions)
    return {
        "format": req.format.lower(),
        "content": content,
    }


@router.post("/api/v1/exam/question/targeted", response_model=TrapQuestion)
async def generate_targeted_trap_question(req: TargetedQuestionRequest) -> TrapQuestion:
    """Öğrencinin geçmiş zaafında yer alan belirli bir BUG-ID'yi hedefleyen çeldiricili soru sentezler."""
    return trap_question_generator.generate_targeted_bug(bug_id=req.bug_id, seed=req.seed)


@router.post("/api/v1/exam/question/verify")
async def verify_trap_question_formally(req: QuestionVerifyRequest) -> Dict[str, Any]:
    """SymPy ile sorunun köklerini, analitik türev/çözüm geçerliliğini ve çeldirici tutarlılığını formel olarak ispatlar."""
    return FormalQuestionVerifier.verify_formally(req.question)


# --- Probability & Combinatorics ---

class ProbabilitySolveRequest(BaseModel):
    problem_type: str
    params: Dict[str, Any]
    student_id: Optional[str] = None
    problem_statement: Optional[str] = None
    student_step: Optional[str] = None


class ProbabilitySolveResponse(BaseModel):
    problem_type: str
    result_data: Dict[str, Any]
    detected_bug: Optional[Dict[str, Any]] = None
    vault_recorded: bool = False


class MonteCarloSimulateRequest(BaseModel):
    experiment_type: str = "coin_flip"
    params: Dict[str, Any] = {}
    num_trials: int = 100_000


@router.post("/api/v1/probability/solve", response_model=ProbabilitySolveResponse)
async def solve_probability_endpoint(req: ProbabilitySolveRequest) -> ProbabilitySolveResponse:
    """
    Hedef 14: Olasılık ve Kombinatorik Sokratik Çözücü API'si.
    Permütasyon, kombinasyon veya koşullu olasılık problemlerini sıfır sızıntı ile iskeletlendirir;
    varsa öğrenci yanılgılarını (BUG-COMB-01..05) tespit edip Bilişsel Hata Kasası'na kaydeder.
    """
    try:
        res = solve_combinatorics_or_probability(req.problem_type, req.params)
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
                    "BUG-COMB-01": "N191",
                    "BUG-COMB-02": "N200",
                    "BUG-COMB-03": "N202",
                    "BUG-COMB-04": "N189",
                    "BUG-COMB-05": "N199",
                }
                node_id = node_map.get(diag.bug_id, "N186")
                cognitive_mistake_vault.record_mistake(
                    user_id=req.student_id,
                    node_id=node_id,
                    bug_id=diag.bug_id,
                    problem_statement=req.problem_statement or f"Olasılık/Kombinatorik: {req.problem_type}",
                    offending_step=req.student_step,
                    correct_principle=diag.description,
                    remediation_directive=diag.remediation_directive,
                )
                vault_recorded = True

    return ProbabilitySolveResponse(
        problem_type=req.problem_type,
        result_data=res,
        detected_bug=detected_diag,
        vault_recorded=vault_recorded,
    )


@router.post("/api/v1/probability/monte-carlo")
async def simulate_monte_carlo_endpoint(req: MonteCarloSimulateRequest) -> Dict[str, Any]:
    """
    Canlı Monte Carlo Olasılık Simülatörü API'si.
    100.000 sanal deney ile büyük sayılar yasasını deneysel olarak doğrular.
    """
    safe_trials = max(10, min(1_000_000, req.num_trials))
    sim = MonteCarloProbabilitySimulator(seed=req.params.get("seed", 42))

    if req.experiment_type == "urn_draw":
        return sim.simulate_urn_draw(
            red_count=req.params.get("red_count", 4),
            blue_count=req.params.get("blue_count", 6),
            draw_count=req.params.get("draw_count", 2),
            target_reds=req.params.get("target_reds", 2),
            with_replacement=req.params.get("with_replacement", False),
            num_trials=safe_trials,
        )
    else:
        prob = req.params.get("prob", 0.5)
        return sim.simulate_event(
            trial_func=lambda rng: rng.random() < prob,
            num_trials=safe_trials,
            theoretical_prob=prob,
        )


# --- Proof Lab ---

class ProofTruthTableRequest(BaseModel):
    variables: List[str] = ["p", "q"]
    expression_type: str = "implies"


class ProofVerifyStepRequest(BaseModel):
    theorem_id: str
    step_number: int
    student_statement: str
    selected_rule: str
    student_id: Optional[str] = None
    problem_statement: Optional[str] = None


class ProofVerifyStepResponse(BaseModel):
    step_number: int
    is_valid: bool
    feedback: str
    expected_statement: Optional[str] = None
    expected_justification: Optional[str] = None
    detected_bug: Optional[str] = None
    vault_recorded: bool = False


class InductionSimulateRequest(BaseModel):
    claim_type: str = "gauss"
    start_k: int = 1
    test_range: int = 10


@router.post("/api/v1/proof/truth-table")
async def generate_truth_table_endpoint(req: ProofTruthTableRequest) -> Dict[str, Any]:
    """
    Hedef 15: Mantıksal önermeler için 2^n satırlı doğruluk tablosu ve totoloji/çelişki analizi.
    """
    safe_variables = [str(v)[:10] for v in req.variables[:6]]
    expr_type = req.expression_type.lower()
    if expr_type == "implies":
        formula = lambda env: logic_implies(env.get("p", False), env.get("q", False))
    elif expr_type == "iff":
        formula = lambda env: logic_iff(env.get("p", False), env.get("q", False))
    elif expr_type == "and":
        formula = lambda env: logic_and(env.get("p", False), env.get("q", False))
    elif expr_type == "or":
        formula = lambda env: logic_or(env.get("p", False), env.get("q", False))
    elif expr_type == "xor":
        formula = lambda env: logic_xor(env.get("p", False), env.get("q", False))
    elif expr_type == "de_morgan_and":
        formula = lambda env: logic_iff(
            logic_not(logic_and(env.get("p", False), env.get("q", False))),
            logic_or(logic_not(env.get("p", False)), logic_not(env.get("q", False))),
        )
    elif expr_type == "contrapositive":
        formula = lambda env: logic_iff(
            logic_implies(env.get("p", False), env.get("q", False)),
            logic_implies(logic_not(env.get("q", False)), logic_not(env.get("p", False))),
        )
    else:
        formula = lambda env: env.get("p", False)

    return TruthTableGenerator.generate_table(safe_variables, formula)


@router.get("/api/v1/proof/catalog")
async def get_proof_catalog_endpoint() -> List[Dict[str, Any]]:
    """
    Hedef 15: Temel teorem ispat kataloğu (√2 irrasyonelliği, asal sayıların sonsuzluğu, Gauss vb.).
    """
    return ProofCatalog.get_all_theorems()


@router.post("/api/v1/proof/verify-step", response_model=ProofVerifyStepResponse)
async def verify_proof_step_endpoint(req: ProofVerifyStepRequest) -> ProofVerifyStepResponse:
    """
    Hedef 15: Öğrencinin teorem ispat adımını denetler; safsata ve bilişsel hataları tespit eder.
    """
    try:
        res = ProofChecker.verify_step(
            theorem_id=req.theorem_id,
            step_number=req.step_number,
            student_statement=req.student_statement,
            selected_rule=req.selected_rule,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    vault_recorded = False
    detected_bug = res.get("detected_bug")

    if not detected_bug:
        diag = misconception_detector.detect(req.student_statement, req.problem_statement or "", "")
        if diag and diag.bug_id.startswith("BUG-LOGIC"):
            detected_bug = diag.bug_id
            res["is_valid"] = False
            res["feedback"] = diag.description

    if detected_bug and req.student_id:
        node_map = {
            "BUG-LOGIC-01": "N214",
            "BUG-LOGIC-02": "N217",
            "BUG-LOGIC-03": "N219",
            "BUG-LOGIC-04": "N226",
            "BUG-LOGIC-05": "N223",
        }
        node_id = node_map.get(detected_bug, "N211")
        cognitive_mistake_vault.record_mistake(
            user_id=req.student_id,
            node_id=node_id,
            bug_id=detected_bug,
            problem_statement=req.problem_statement or f"İspat Denetimi: {req.theorem_id} Adım {req.step_number}",
            offending_step=req.student_statement,
            correct_principle=res.get("feedback", "Mantıksal çıkarım kuralına uyulmalıdır."),
            remediation_directive="Çıkarım kurallarını ve ters varsayım/taban adımı ilkelerini gözden geçir.",
        )
        vault_recorded = True

    return ProofVerifyStepResponse(
        step_number=res["step_number"],
        is_valid=res["is_valid"],
        feedback=res["feedback"],
        expected_statement=res.get("expected_statement"),
        expected_justification=res.get("expected_justification"),
        detected_bug=detected_bug,
        vault_recorded=vault_recorded,
    )


@router.post("/api/v1/proof/induction/simulate")
async def simulate_induction_endpoint(req: InductionSimulateRequest) -> Dict[str, Any]:
    """
    Hedef 15: Matematiksel tümevarım domino zinciri simülasyonu.
    """
    safe_start = max(-1000, min(1000, req.start_k))
    safe_range = max(1, min(100, req.test_range))

    if req.claim_type == "exp_ineq":
        pred = lambda n: (2 ** n) > n
    else:
        pred = lambda n: sum(range(1, n + 1)) == (n * (n + 1)) // 2

    return MathematicalInductionEngine.simulate_inductive_step(
        predicate=pred,
        start_k=safe_start,
        test_range=safe_range,
    )
