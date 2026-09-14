import 'package:flutter/foundation.dart';
import '../../../../data/services/engine_api_service.dart';
import '../../../../domain/models/solution_step.dart';
import '../../touchpad/math_touchpad.dart';

class SessionViewModel extends ChangeNotifier {
  final EngineApiService _apiService;

  final String sessionId;
  final String targetEquation;
  final String nodeId;

  final List<SolutionStep> _steps = [];
  bool _isSubmitting = false;
  bool _isTargetReached = false;
  double _currentPl = 0.20;
  InputMode _inputMode = InputMode.touchpad;
  DateTime _stepStartTime = DateTime.now();

  SessionViewModel({
    required EngineApiService apiService,
    required this.sessionId,
    required this.targetEquation,
    this.nodeId = 'N15',
    double initialPl = 0.20,
  })  : _apiService = apiService,
        _currentPl = initialPl {
    _stepStartTime = DateTime.now();
  }

  // Getters
  List<SolutionStep> get steps => List.unmodifiable(_steps);
  bool get isSubmitting => _isSubmitting;
  bool get isTargetReached => _isTargetReached;
  double get currentPl => _currentPl;
  InputMode get inputMode => _inputMode;

  void setInputMode(InputMode mode) {
    _inputMode = mode;
    notifyListeners();
  }

  Future<SolutionStep?> submitStep(String rawExpression) async {
    final trimmed = rawExpression.trim();
    if (trimmed.isEmpty || _isSubmitting) return null;

    _isSubmitting = true;
    notifyListeners();

    final now = DateTime.now();
    final elapsedMs = now.difference(_stepStartTime).inMilliseconds;

    final stepNumber = _steps.length + 1;
    final previousStep = _steps.isNotEmpty ? _steps.last.userExpression : null;

    try {
      final verifiedStep = await _apiService.verifyStep(
        sessionId: sessionId,
        nodeId: nodeId,
        stepNumber: stepNumber,
        userExpression: trimmed,
        targetEquation: targetEquation,
        previousStep: previousStep,
        elapsedMs: elapsedMs,
        currentPl: _currentPl,
      );

      _steps.add(verifiedStep);

      if (verifiedStep.isValid) {
        if (verifiedStep.psychometrics != null) {
          _currentPl = verifiedStep.psychometrics!.bktPosteriorPl;
        }
        if (verifiedStep.isTargetReached) {
          _isTargetReached = true;
        }
      }

      _stepStartTime = DateTime.now();
      _isSubmitting = false;
      notifyListeners();
      return verifiedStep;
    } catch (e) {
      // Offline fallback or network error
      final fallbackStep = SolutionStep(
        stepNumber: stepNumber,
        userExpression: trimmed,
        isValid: false,
        isTargetReached: false,
        errorMessage: 'Bağlantı hatası: Adım yerel olarak kaydedildi.',
        elapsedMs: elapsedMs,
      );
      _steps.add(fallbackStep);
      _isSubmitting = false;
      notifyListeners();
      return fallbackStep;
    }
  }

  void rollbackToStep(int stepIndex) {
    if (stepIndex >= 0 && stepIndex < _steps.length) {
      _steps.removeRange(stepIndex, _steps.length);
      _isTargetReached = false;
      _stepStartTime = DateTime.now();
      notifyListeners();
    }
  }

  void resetSession() {
    _steps.clear();
    _isTargetReached = false;
    _stepStartTime = DateTime.now();
    notifyListeners();
  }
}
