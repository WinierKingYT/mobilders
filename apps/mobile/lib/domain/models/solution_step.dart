import 'diagnostic_bug.dart';
import 'step_psychometrics.dart';

class SolutionStep {
  final int stepNumber;
  final String userExpression;
  final bool isValid;
  final bool isTargetReached;
  final String? canonicalExpression;
  final DiagnosticBug? detectedBug;
  final String? errorMessage;
  final int elapsedMs;
  final StepPsychometricsModel? psychometrics;

  const SolutionStep({
    required this.stepNumber,
    required this.userExpression,
    required this.isValid,
    required this.isTargetReached,
    this.canonicalExpression,
    this.detectedBug,
    this.errorMessage,
    required this.elapsedMs,
    this.psychometrics,
  });

  factory SolutionStep.fromJson(Map<String, dynamic> json, {int stepNumber = 1, String userExpression = '', int elapsedMs = 0}) {
    return SolutionStep(
      stepNumber: stepNumber,
      userExpression: userExpression,
      isValid: json['is_valid'] as bool? ?? false,
      isTargetReached: json['is_target_reached'] as bool? ?? false,
      canonicalExpression: json['canonical_expression'] as String?,
      detectedBug: json['detected_bug'] != null
          ? DiagnosticBug.fromJson(json['detected_bug'] as Map<String, dynamic>)
          : null,
      errorMessage: json['error_message'] as String?,
      elapsedMs: elapsedMs,
      psychometrics: json['psychometrics'] != null
          ? StepPsychometricsModel.fromJson(json['psychometrics'] as Map<String, dynamic>)
          : null,
    );
  }
}
