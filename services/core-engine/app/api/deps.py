from collections import OrderedDict
import threading
import time
from typing import Optional, Dict, List, Any, Tuple
from app.models.schemas import StepVerificationResponse

from app.cas.symbolic_engine import SymbolicEquivalenceEngine
from app.cas.stroke_parser import StrokeToASTParser
from app.misconceptions.detector import QuadraticMisconceptionDetector
from app.graph.knowledge_dag import KnowledgeDAG
from app.graph.curriculum_mapper import CurriculumOntologyRegistry
from app.adaptive.cat_engine import CATEngine
from app.affect.detector import AffectiveStateDetector
from app.socratic.pipeline import SocraticPipeline
from app.retention.fsrs import FSRSEngine
from app.analytics.local_reporter import LocalAnalyticsReporter
from app.analytics.classroom_reporter import ClassroomAnalyticsReporter
from app.lti.service import LTI13Service
from app.voice.service import VoiceSocraticEngine
from app.curriculum_generator.dag_synthesizer import AutonomousCurriculumSynthesizer
from app.simulation.cohort_factory import VectorizedCohortSimulationFactory
from app.curriculum_generator.trap_question_factory import (
    TrapQuestionGenerator,
    DynamicExamFactory,
)
from app.research.dp_exporter import DifferentialPrivacyExporter
from app.research.leaderboard import CognitiveModelBenchmark
from app.ocr.vision_pipeline import MathVisionPipeline
from app.ocr.socratic_diagnoser import SocraticNotebookDiagnoser
from app.modeling.scaffold_engine import SocraticModelingScaffoldEngine
from app.root_pedagogy.root_dag import RootPrerequisiteDAG
from app.root_pedagogy.diagnostic import ZeroBaselineDiagnostic
from app.root_pedagogy.weakness_ledger import CognitiveWeaknessLedger
from app.root_pedagogy.co_solver import ActiveCoSolverEngine
from app.root_pedagogy.sandbox import InSituRemediationSandbox
from app.vault.mistake_vault import (
    CognitiveMistakeVault,
    SelfCorrectionSessionManager,
    BossBattleEngine,
)
from app.graph.knowledge_atlas_engine import LivingKnowledgeAtlasEngine


from app.core.redis_service import RedisService
from app.db.connection import PostgresConnectionManager
from app.db.repository import CognitiveStateRepository


class IdempotencyCache:
    """
    Sınırlandırılmış ve TTL destekli thread-safe idempotentlik önbelleği (L1: Memory LRU, L2: Redis).
    Bellek sızıntılarını önler, en eski/zaman aşımına uğramış kayıtları tahliye eder.
    Redis bağlıysa dağıtık önbellek olarak kullanır, çevrimdışıyken kesintisiz yerel çalışır.
    """

    def __init__(self, max_size: int = 5000, ttl_seconds: float = 3600.0, redis_svc: Optional[RedisService] = None):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[float, StepVerificationResponse]] = OrderedDict()
        self._lock = threading.Lock()
        self._redis_svc = redis_svc

    def get(self, key: str) -> Optional[StepVerificationResponse]:
        with self._lock:
            if key in self._cache:
                ts, resp = self._cache[key]
                if time.time() - ts > self.ttl_seconds:
                    del self._cache[key]
                else:
                    self._cache.move_to_end(key)
                    return resp

        # L2: Redis denetimi (varsa)
        if self._redis_svc and self._redis_svc.is_connected:
            cached_json = self._redis_svc.get_idempotent_response(f"idemp:step:{key}")
            if cached_json:
                try:
                    resp = StepVerificationResponse.model_validate_json(cached_json)
                    with self._lock:
                        if len(self._cache) >= self.max_size:
                            self._cache.popitem(last=False)
                        self._cache[key] = (time.time(), resp)
                    return resp
                except Exception:
                    pass
        return None

    def set(self, key: str, resp: StepVerificationResponse) -> None:
        with self._lock:
            now = time.time()
            if key in self._cache:
                self._cache[key] = (now, resp)
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    # En eski kaydı tahliye et (LRU)
                    self._cache.popitem(last=False)
                self._cache[key] = (now, resp)

        # L2: Redis'e yaz
        if self._redis_svc and self._redis_svc.is_connected:
            try:
                self._redis_svc.store_idempotent_response(
                    f"idemp:step:{key}",
                    resp,
                    ttl_seconds=int(self.ttl_seconds),
                )
            except Exception:
                pass

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: str) -> StepVerificationResponse:
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: StepVerificationResponse) -> None:
        self.set(key, value)

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Tekil motor örnekleri (Singletons)
cas_engine = SymbolicEquivalenceEngine()
misconception_detector = QuadraticMisconceptionDetector(cas_engine)
knowledge_dag = KnowledgeDAG()
curriculum_registry = CurriculumOntologyRegistry()
cat_engine = CATEngine(dag=knowledge_dag)
fsrs_engine = FSRSEngine()
affective_detector = AffectiveStateDetector()
socratic_pipeline = SocraticPipeline()
local_analytics = LocalAnalyticsReporter(dag=knowledge_dag, fsrs=fsrs_engine)
classroom_reporter = ClassroomAnalyticsReporter(dag=knowledge_dag)
stroke_parser = StrokeToASTParser()
lti_service = LTI13Service()
voice_engine = VoiceSocraticEngine(socratic_pipeline=socratic_pipeline, guardrail=socratic_pipeline.guardrail)
curriculum_synthesizer = AutonomousCurriculumSynthesizer()
simulation_factory = VectorizedCohortSimulationFactory()
dp_exporter = DifferentialPrivacyExporter()
model_benchmark = CognitiveModelBenchmark()
cognitive_mistake_vault = CognitiveMistakeVault(fsrs_engine=fsrs_engine)
self_correction_manager = SelfCorrectionSessionManager(cognitive_mistake_vault)
boss_battle_engine = BossBattleEngine(cognitive_mistake_vault)
math_vision_pipeline = MathVisionPipeline(dag=knowledge_dag)
socratic_diagnoser = SocraticNotebookDiagnoser(
    cas=cas_engine,
    detector=misconception_detector,
    dag=knowledge_dag,
    vision_pipeline=math_vision_pipeline,
    vault=cognitive_mistake_vault,
)
modeling_scaffold_engine = SocraticModelingScaffoldEngine(
    cas_engine=cas_engine,
    detector=misconception_detector,
    vault=cognitive_mistake_vault,
)
root_dag = RootPrerequisiteDAG()
zero_baseline_diagnostic = ZeroBaselineDiagnostic()
weakness_ledger = CognitiveWeaknessLedger(root_dag)
active_cosolver = ActiveCoSolverEngine(cas_engine)
insitu_sandbox = InSituRemediationSandbox()
trap_question_generator = TrapQuestionGenerator()
dynamic_exam_factory = DynamicExamFactory(trap_question_generator)
atlas_engine = LivingKnowledgeAtlasEngine()

# Persistence and Distributed State (PostgreSQL schema.sql & Redis redis_init.lua)
redis_service = RedisService()
db_connection_manager = PostgresConnectionManager()
db_repository = CognitiveStateRepository(db_connection_manager)

# Idempotency Cache for offline event replay and network duplicate protection (TTL + LRU + Redis L2)
_IDEMPOTENCY_CACHE = IdempotencyCache(max_size=5000, ttl_seconds=3600.0, redis_svc=redis_service)

