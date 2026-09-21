"""
Aggregator API Router for Core Engine.
Re-exports dependencies for backwards compatibility and mounts all domain routers.
"""
from fastapi import APIRouter

# Re-export shared singletons and dependencies for backwards compatibility
from app.api.deps import (
    IdempotencyCache,
    _IDEMPOTENCY_CACHE,
    cas_engine,
    misconception_detector,
    knowledge_dag,
    curriculum_registry,
    cat_engine,
    fsrs_engine,
    affective_detector,
    socratic_pipeline,
    local_analytics,
    classroom_reporter,
    stroke_parser,
    lti_service,
    voice_engine,
    curriculum_synthesizer,
    simulation_factory,
    dp_exporter,
    model_benchmark,
    cognitive_mistake_vault,
    self_correction_manager,
    boss_battle_engine,
    math_vision_pipeline,
    socratic_diagnoser,
    modeling_scaffold_engine,
    root_dag,
    zero_baseline_diagnostic,
    weakness_ledger,
    active_cosolver,
    insitu_sandbox,
    trap_question_generator,
    dynamic_exam_factory,
    atlas_engine,
)

# Import domain routers
from app.api.routers.session import router as session_router
from app.api.routers.diagnostic import router as diagnostic_router
from app.api.routers.socratic import router as socratic_router
from app.api.routers.multimodal import router as multimodal_router
from app.api.routers.vault import router as vault_router
from app.api.routers.geometry import router as geometry_router
from app.api.routers.curriculum import router as curriculum_router
from app.api.routers.exam import router as exam_router
from app.api.routers.twin import router as twin_router

# Main aggregator router
router = APIRouter(tags=["Session, Verification, Diagnostic, Multimodal, LTI, Voice, Autonomous Generator & Benchmark, Mistake Vault"])

router.include_router(session_router)
router.include_router(diagnostic_router)
router.include_router(socratic_router)
router.include_router(multimodal_router)
router.include_router(vault_router)
router.include_router(geometry_router)
router.include_router(curriculum_router)
router.include_router(exam_router)
router.include_router(twin_router)

__all__ = [
    "router",
    "IdempotencyCache",
    "_IDEMPOTENCY_CACHE",
    "cas_engine",
    "misconception_detector",
    "knowledge_dag",
    "curriculum_registry",
    "cat_engine",
    "fsrs_engine",
    "affective_detector",
    "socratic_pipeline",
    "local_analytics",
    "classroom_reporter",
    "stroke_parser",
    "lti_service",
    "voice_engine",
    "curriculum_synthesizer",
    "simulation_factory",
    "dp_exporter",
    "model_benchmark",
    "cognitive_mistake_vault",
    "self_correction_manager",
    "boss_battle_engine",
    "math_vision_pipeline",
    "socratic_diagnoser",
    "modeling_scaffold_engine",
    "root_dag",
    "zero_baseline_diagnostic",
    "weakness_ledger",
    "active_cosolver",
    "insitu_sandbox",
    "trap_question_generator",
    "dynamic_exam_factory",
    "atlas_engine",
]
