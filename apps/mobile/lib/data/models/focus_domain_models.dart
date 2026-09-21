/// Focus Domain v0.4 & API Boundary v0.1 Mobile Contract Models.
///
/// Encodes domain judgments, input kinds, state transitions,
/// server decisions, and learner profiles according to the frozen contract.
library;

enum AttemptJudgment {
  validExpected,
  validIncomplete,
  validShortcut,
  invalidMathematics,
  ambiguousInput,
  unsupportedStepForm,
  unsupportedDomain;

  static AttemptJudgment fromString(String value) {
    switch (value) {
      case 'VALID_EXPECTED':
        return AttemptJudgment.validExpected;
      case 'VALID_INCOMPLETE':
        return AttemptJudgment.validIncomplete;
      case 'VALID_SHORTCUT':
        return AttemptJudgment.validShortcut;
      case 'INVALID_MATHEMATICS':
        return AttemptJudgment.invalidMathematics;
      case 'AMBIGUOUS_INPUT':
        return AttemptJudgment.ambiguousInput;
      case 'UNSUPPORTED_STEP_FORM':
        return AttemptJudgment.unsupportedStepForm;
      case 'UNSUPPORTED_DOMAIN':
        return AttemptJudgment.unsupportedDomain;
      default:
        return AttemptJudgment.unsupportedStepForm;
    }
  }

  String get wireName {
    switch (this) {
      case AttemptJudgment.validExpected:
        return 'VALID_EXPECTED';
      case AttemptJudgment.validIncomplete:
        return 'VALID_INCOMPLETE';
      case AttemptJudgment.validShortcut:
        return 'VALID_SHORTCUT';
      case AttemptJudgment.invalidMathematics:
        return 'INVALID_MATHEMATICS';
      case AttemptJudgment.ambiguousInput:
        return 'AMBIGUOUS_INPUT';
      case AttemptJudgment.unsupportedStepForm:
        return 'UNSUPPORTED_STEP_FORM';
      case AttemptJudgment.unsupportedDomain:
        return 'UNSUPPORTED_DOMAIN';
    }
  }
}

enum NextActionType {
  advance,
  stay,
  probe,
  startRepair,
  escalate;

  static NextActionType fromString(String value) {
    switch (value) {
      case 'ADVANCE':
        return NextActionType.advance;
      case 'STAY':
        return NextActionType.stay;
      case 'PROBE':
        return NextActionType.probe;
      case 'START_REPAIR':
        return NextActionType.startRepair;
      case 'ESCALATE':
        return NextActionType.escalate;
      default:
        return NextActionType.stay;
    }
  }
}

enum FocusAttemptInputKind {
  factorPair,
  branchDecomposition,
  singleBranch,
  solutionSet,
  coefficients,
  equationRewrite,
  variableAssignment,
  inequalityRewrite,
  coordinateAssignment,
  classification,
  arithmeticResult,
  expressionRewrite;

  String get wireName {
    switch (this) {
      case FocusAttemptInputKind.factorPair:
        return 'FACTOR_PAIR';
      case FocusAttemptInputKind.branchDecomposition:
        return 'BRANCH_DECOMPOSITION';
      case FocusAttemptInputKind.singleBranch:
        return 'SINGLE_BRANCH';
      case FocusAttemptInputKind.solutionSet:
        return 'SOLUTION_SET';
      case FocusAttemptInputKind.coefficients:
        return 'COEFFICIENTS';
      case FocusAttemptInputKind.equationRewrite:
        return 'EQUATION_REWRITE';
      case FocusAttemptInputKind.variableAssignment:
        return 'VARIABLE_ASSIGNMENT';
      case FocusAttemptInputKind.inequalityRewrite:
        return 'INEQUALITY_REWRITE';
      case FocusAttemptInputKind.coordinateAssignment:
        return 'COORDINATE_ASSIGNMENT';
      case FocusAttemptInputKind.classification:
        return 'CLASSIFICATION';
      case FocusAttemptInputKind.arithmeticResult:
        return 'ARITHMETIC_RESULT';
      case FocusAttemptInputKind.expressionRewrite:
        return 'EXPRESSION_REWRITE';
    }
  }
}

enum PrerequisiteChainHealth {
  healthy,
  atRisk,
  blocked;

  static PrerequisiteChainHealth fromString(String value) {
    switch (value) {
      case 'HEALTHY':
        return PrerequisiteChainHealth.healthy;
      case 'AT_RISK':
        return PrerequisiteChainHealth.atRisk;
      case 'BLOCKED':
        return PrerequisiteChainHealth.blocked;
      default:
        return PrerequisiteChainHealth.atRisk;
    }
  }
}

class FocusDecision {
  final NextActionType action;
  final String reason;
  final String? probeId;
  final String? repairEdgeId;
  final String? diagnosticRouteId;
  final String? targetKc;
  final String? barrierId;
  final String? interventionId;

  const FocusDecision({
    required this.action,
    required this.reason,
    this.probeId,
    this.repairEdgeId,
    this.diagnosticRouteId,
    this.targetKc,
    this.barrierId,
    this.interventionId,
  });

  factory FocusDecision.fromJson(Map<String, dynamic> json) {
    return FocusDecision(
      action: NextActionType.fromString(json['action'] as String? ?? 'STAY'),
      reason: json['reason'] as String? ?? '',
      probeId: json['probe_id'] as String?,
      repairEdgeId: json['repair_edge_id'] as String?,
      diagnosticRouteId: json['diagnostic_route_id'] as String?,
      targetKc: json['target_kc'] as String?,
      barrierId: json['barrier_id'] as String?,
      interventionId: json['intervention_id'] as String?,
    );
  }
}

class FocusEpisodeState {
  final String? workspaceKc;
  final String compositeTaskId;
  final String currentStage;
  final String phase;
  final int probeBudgetRemaining;
  final AttemptJudgment? lastJudgment;
  final List<String> lastObservations;
  final String? repairKc;
  final String? repairInterventionId;
  final Map<String, dynamic>? transferTaskContext;
  final Map<String, dynamic>? retestTaskContext;
  final Map<String, dynamic>? taskContext;

  const FocusEpisodeState({
    this.workspaceKc,
    required this.compositeTaskId,
    required this.currentStage,
    required this.phase,
    required this.probeBudgetRemaining,
    this.lastJudgment,
    this.lastObservations = const [],
    this.repairKc,
    this.repairInterventionId,
    this.transferTaskContext,
    this.retestTaskContext,
    this.taskContext,
  });

  factory FocusEpisodeState.fromJson(Map<String, dynamic> json) {
    return FocusEpisodeState(
      workspaceKc: json['workspace_kc'] as String?,
      compositeTaskId: json['composite_task_id'] as String? ?? '',
      currentStage: json['current_stage'] as String? ?? '',
      phase: json['phase'] as String? ?? '',
      probeBudgetRemaining: json['probe_budget_remaining'] as int? ?? 0,
      lastJudgment: json['last_judgment'] != null
          ? AttemptJudgment.fromString(json['last_judgment'] as String)
          : null,
      lastObservations: (json['last_observations'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      repairKc: json['repair_kc'] as String?,
      repairInterventionId: json['repair_intervention_id'] as String?,
      transferTaskContext: json['transfer_task_context'] as Map<String, dynamic>?,
      retestTaskContext: json['retest_task_context'] as Map<String, dynamic>?,
      taskContext: json['task_context'] as Map<String, dynamic>?,
    );
  }
}

class FocusCommandResult {
  final String episodeId;
  final int streamVersion;
  final FocusEpisodeState state;
  final String eventId;
  final String eventType;
  final FocusDecision? decision;
  final AttemptJudgment? judgment;
  final List<String> observations;
  final String? normalizedInput;
  final String? compositeFailure;
  final bool? repairEvaluationSuccess;
  final String? repairEvaluationFeedback;

  const FocusCommandResult({
    required this.episodeId,
    required this.streamVersion,
    required this.state,
    required this.eventId,
    required this.eventType,
    this.decision,
    this.judgment,
    this.observations = const [],
    this.normalizedInput,
    this.compositeFailure,
    this.repairEvaluationSuccess,
    this.repairEvaluationFeedback,
  });

  factory FocusCommandResult.fromJson(Map<String, dynamic> json) {
    return FocusCommandResult(
      episodeId: json['episode_id'] as String,
      streamVersion: json['stream_version'] as int,
      state: FocusEpisodeState.fromJson(json['state'] as Map<String, dynamic>),
      eventId: json['event_id'] as String,
      eventType: json['event_type'] as String,
      decision: json['decision'] != null
          ? FocusDecision.fromJson(json['decision'] as Map<String, dynamic>)
          : null,
      judgment: json['judgment'] != null
          ? AttemptJudgment.fromString(json['judgment'] as String)
          : null,
      observations: (json['observations'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      normalizedInput: json['normalized_input'] as String?,
      compositeFailure: json['composite_failure'] as String?,
      repairEvaluationSuccess: json['repair_evaluation_success'] as bool?,
      repairEvaluationFeedback: json['repair_evaluation_feedback'] as String?,
    );
  }
}

class FocusEpisodeView {
  final String episodeId;
  final int streamVersion;
  final FocusEpisodeState state;

  const FocusEpisodeView({
    required this.episodeId,
    required this.streamVersion,
    required this.state,
  });

  factory FocusEpisodeView.fromJson(Map<String, dynamic> json) {
    return FocusEpisodeView(
      episodeId: json['episode_id'] as String,
      streamVersion: json['stream_version'] as int,
      state: FocusEpisodeState.fromJson(json['state'] as Map<String, dynamic>),
    );
  }
}

class LearnerProfileView {
  final Map<String, String> kcStates;
  final Map<String, String> barrierStates;
  final List<String> retestDue;
  final List<String> activeGaps;

  const LearnerProfileView({
    required this.kcStates,
    required this.barrierStates,
    required this.retestDue,
    required this.activeGaps,
  });

  factory LearnerProfileView.fromJson(Map<String, dynamic> json) {
    return LearnerProfileView(
      kcStates: (json['kc_states'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v.toString())) ??
          {},
      barrierStates: (json['barrier_states'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v.toString())) ??
          {},
      retestDue: (json['retest_due'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      activeGaps: (json['active_gaps'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

class ReEntryDiagnosticView {
  final String targetKc;
  final PrerequisiteChainHealth chainHealth;
  final List<String> blockingDependencies;
  final List<String> atRiskDependencies;
  final String recommendedAction;
  final String? interventionKc;
  final String rationale;

  const ReEntryDiagnosticView({
    required this.targetKc,
    required this.chainHealth,
    required this.blockingDependencies,
    required this.atRiskDependencies,
    required this.recommendedAction,
    this.interventionKc,
    required this.rationale,
  });

  factory ReEntryDiagnosticView.fromJson(Map<String, dynamic> json) {
    return ReEntryDiagnosticView(
      targetKc: json['target_kc'] as String,
      chainHealth: PrerequisiteChainHealth.fromString(
          json['chain_health'] as String? ?? 'AT_RISK'),
      blockingDependencies: (json['blocking_dependencies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      atRiskDependencies: (json['at_risk_dependencies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      recommendedAction: json['recommended_action'] as String? ?? '',
      interventionKc: json['intervention_kc'] as String?,
      rationale: json['rationale'] as String? ?? '',
    );
  }
}

/// Legacy / convenience response model maintained for backwards compatibility
class FocusEvaluationResponse {
  final AttemptJudgment judgment;
  final String? compositeFailure;
  final String? observedError;
  final String? details;
  final Map<String, dynamic> parsedAst;

  const FocusEvaluationResponse({
    required this.judgment,
    this.compositeFailure,
    this.observedError,
    this.details,
    this.parsedAst = const {},
  });

  factory FocusEvaluationResponse.fromJson(Map<String, dynamic> json) {
    return FocusEvaluationResponse(
      judgment: AttemptJudgment.fromString(json['judgment'] as String? ?? ''),
      compositeFailure: json['composite_failure'] as String?,
      observedError: json['observed_error'] as String?,
      details: json['details'] as String?,
      parsedAst: json['parsed_ast'] as Map<String, dynamic>? ?? {},
    );
  }

  bool get isSuccess =>
      judgment == AttemptJudgment.validExpected ||
      judgment == AttemptJudgment.validShortcut;

  bool get isIncomplete => judgment == AttemptJudgment.validIncomplete;
}

class FocusRootSlot {
  final int index;
  final String rawValue;

  const FocusRootSlot({
    required this.index,
    required this.rawValue,
  });
}
