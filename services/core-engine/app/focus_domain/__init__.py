"""Mobilders V1 Focus Domain foundation.

This package encodes the narrow cognitive-domain contracts separately from
legacy broad curriculum/diagnostic systems. The core decision logic remains
pure; persistence is exposed through narrow journal/snapshot ports plus an
in-memory reference adapter. No production database or API integration exists yet.
"""

from .models import (
    AttemptActionType,
    AttemptJudgment,
    BarrierState,
    BranchAssignmentStatus,
    BranchWorkItem,
    BranchWorkSet,
    CompositeTaskFailureCode,
    CompositeTaskState,
    KCId,
    KCState,
    ProbeEvidenceKind,
    StageId,
)
from .rules import (
    apply_valid_shortcut,
    judge_branch_work,
)
from .attempt_language import (
    CanonicalSolutionSet,
    NormalizationStatus,
    NormalizedAttempt,
    SupportedAttemptNormalizer,
)
from .stage_judgment import CTQF1StageJudgmentService, StageJudgmentResult
from .registry import (
    ACTIVE_DIAGNOSTIC_ROUTES,
    INTERVENTION_TEMPLATES,
    PROBE_TEMPLATES,
    REPAIR_EDGES,
    validate_focus_registry,
)

__all__ = [
    "AttemptActionType",
    "AttemptJudgment",
    "BarrierState",
    "BranchAssignmentStatus",
    "BranchWorkItem",
    "BranchWorkSet",
    "CompositeTaskFailureCode",
    "CompositeTaskState",
    "KCId",
    "KCState",
    "ProbeEvidenceKind",
    "StageId",
    "CanonicalSolutionSet",
    "NormalizationStatus",
    "NormalizedAttempt",
    "SupportedAttemptNormalizer",
    "CTQF1StageJudgmentService",
    "StageJudgmentResult",
    "ACTIVE_DIAGNOSTIC_ROUTES",
    "INTERVENTION_TEMPLATES",
    "PROBE_TEMPLATES",
    "REPAIR_EDGES",
    "apply_valid_shortcut",
    "judge_branch_work",
    "validate_focus_registry",
    "AlphaQuadraticTaskSpec",
    "AlphaTruthAdapter",
    "AlphaTruthResult",
    "TruthFactCode",
    "ErrorObservation",
    "ErrorObservationCode",
    "ErrorObservationProducer",
    "RepairEdgeEligibilityEvaluator",
    "RepairEligibilityResult",
    "RepairEligibilityStatus",
    "RepairEvidenceContext",
    "InvalidLearnerStateTransition",
    "LearnerEvidenceEvent",
    "LearnerEvidenceEventType",
    "LearnerEvidenceSnapshot",
    "LearnerStateTransitionResult",
    "LearnerStateTransitionService",
]

from .truth_adapter import AlphaQuadraticTaskSpec, AlphaTruthAdapter, AlphaTruthResult, TruthFactCode
from .observations import ErrorObservation, ErrorObservationCode, ErrorObservationProducer
from .repair_evaluator import (
    RepairEdgeEligibilityEvaluator,
    RepairEligibilityResult,
    RepairEligibilityStatus,
    RepairEvidenceContext,
)
from .learner_state import (
    InvalidLearnerStateTransition,
    LearnerEvidenceEvent,
    LearnerEvidenceEventType,
    LearnerEvidenceSnapshot,
    LearnerStateTransitionResult,
    LearnerStateTransitionService,
)


from .probe_evaluator import (
    ProbeEvaluationResult,
    ProbeResponseEvaluator,
    UnknownProbeResponse,
)
from .decision_pipeline import (
    EpisodePhase,
    FocusDecision,
    FocusDecisionPipeline,
    FocusEpisodeOrchestrator,
    FocusEpisodeState,
    NextActionType,
    ProbeApplicationResult,
)

__all__.extend([
    "ProbeEvaluationResult",
    "ProbeResponseEvaluator",
    "UnknownProbeResponse",
    "EpisodePhase",
    "FocusDecision",
    "FocusDecisionPipeline",
    "FocusEpisodeOrchestrator",
    "FocusEpisodeState",
    "NextActionType",
    "ProbeApplicationResult",
])

from .persistence import (
    DOMAIN_CONTRACT_VERSION,
    EVENT_SCHEMA_VERSION,
    AppendResult,
    EpisodeNotFound,
    EventJournalConflict,
    EventJournalCorruption,
    FocusEpisodePersistenceService,
    FocusEpisodeReconstructor,
    FocusEventJournal,
    FocusSnapshotStore,
    FocusEpisodeSnapshotRecord,
    FocusEvent,
    FocusEventDraft,
    FocusEventType,
    InMemoryFocusEventRepository,
    InMemoryFocusSnapshotRepository,
    SnapshotConflict,
)

__all__.extend([
    "DOMAIN_CONTRACT_VERSION",
    "EVENT_SCHEMA_VERSION",
    "AppendResult",
    "EpisodeNotFound",
    "EventJournalConflict",
    "EventJournalCorruption",
    "FocusEpisodePersistenceService",
    "FocusEpisodeReconstructor",
    "FocusEventJournal",
    "FocusSnapshotStore",
    "FocusEpisodeSnapshotRecord",
    "FocusEvent",
    "FocusEventDraft",
    "FocusEventType",
    "InMemoryFocusEventRepository",
    "InMemoryFocusSnapshotRepository",
    "SnapshotConflict",
])

from .application import (
    CTQF1AttemptAssessmentService,
    FocusApplicationError,
    FocusAttemptAssessment,
    FocusAttemptInputKind,
    FocusCommandResult,
    FocusEpisodeView,
    FocusServiceFacade,
)
from .api import (
    create_focus_router,
    focus_v1_enabled_from_env,
    install_focus_api,
)

__all__.extend([
    "CTQF1AttemptAssessmentService",
    "FocusApplicationError",
    "FocusAttemptAssessment",
    "FocusAttemptInputKind",
    "FocusCommandResult",
    "FocusEpisodeView",
    "FocusServiceFacade",
    "create_focus_router",
    "focus_v1_enabled_from_env",
    "install_focus_api",
])
