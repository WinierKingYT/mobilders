import 'package:flutter/foundation.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../../data/services/engine_api_service.dart';
import '../../../../data/services/offline_sync_queue.dart';
import '../../../../data/services/session_restoration_manager.dart';
import '../../../../domain/models/solution_step.dart';
import '../../touchpad/math_touchpad.dart';

class SessionViewModel extends ChangeNotifier {
  final EngineApiService _apiService;
  final OfflineSyncQueue _syncQueue;

  final String sessionId;
  final String targetEquation;
  final String nodeId;

  final List<SolutionStep> _steps = [];
  bool _isSubmitting = false;
  bool _isTargetReached = false;
  double _currentPl = 0.20;
  InputMode _inputMode = InputMode.touchpad;
  DateTime _stepStartTime = DateTime.now();

  // Accessibility & UX States
  bool _isTunnelFocusMode = false;
  bool _isDyscalculiaHelper = false;
  bool _isZenMode = false;
  String? _hesitationWhisper;

  SessionViewModel({
    required EngineApiService apiService,
    required this.sessionId,
    required this.targetEquation,
    this.nodeId = 'N15',
    double initialPl = 0.20,
    OfflineSyncQueue? syncQueue,
  })  : _apiService = apiService,
        _syncQueue = syncQueue ?? OfflineSyncQueue(),
        _currentPl = initialPl {
    _stepStartTime = DateTime.now();
  }

  // Getters
  List<SolutionStep> get steps => List.unmodifiable(_steps);
  bool get isSubmitting => _isSubmitting;
  bool get isTargetReached => _isTargetReached;
  double get currentPl => _currentPl;
  InputMode get inputMode => _inputMode;
  OfflineSyncQueue get syncQueue => _syncQueue;
  bool get isTunnelFocusMode => _isTunnelFocusMode;
  bool get isDyscalculiaHelper => _isDyscalculiaHelper;
  bool get isZenMode => _isZenMode;
  String? get hesitationWhisper => _hesitationWhisper;
  int get pendingOfflineCount => _syncQueue.pendingCount;

  void setHesitationWhisper(String? whisper) {
    _hesitationWhisper = whisper;
    notifyListeners();
  }

  void dismissHesitationWhisper() {
    _hesitationWhisper = null;
    notifyListeners();
  }

  void toggleZenMode() {
    _isZenMode = !_isZenMode;
    notifyListeners();
  }

  void loadFromRestoredState(RestoredSessionState state) {
    _steps.clear();
    _steps.addAll(state.toSolutionSteps());
    _inputMode = state.inputMode;
    _currentPl = state.currentPl;
    _isTargetReached = _steps.isNotEmpty && _steps.any((s) => s.isTargetReached);
    notifyListeners();
  }

  void setInputMode(InputMode mode) {
    _inputMode = mode;
    notifyListeners();
  }

  void toggleTunnelFocusMode() {
    _isTunnelFocusMode = !_isTunnelFocusMode;
    notifyListeners();
  }

  void toggleDyscalculiaHelper() {
    _isDyscalculiaHelper = !_isDyscalculiaHelper;
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
    final clientMsgId = 'evt_${DateTime.now().microsecondsSinceEpoch}';

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
        clientMsgId: clientMsgId,
        clientTimestamp: now,
      );

      _steps.add(verifiedStep);

      if (verifiedStep.isValid) {
        HapticFeedbackService().stepSuccess();
        if (verifiedStep.psychometrics != null) {
          _currentPl = verifiedStep.psychometrics!.bktPosteriorPl;
        }
        if (verifiedStep.isTargetReached) {
          _isTargetReached = true;
        }
      } else {
        HapticFeedbackService().stepError();
      }

      // Check if there are any pending offline steps to sync in the background
      if (_syncQueue.pendingCount > 0) {
        _syncQueue.replayQueue(_apiService);
      }

      _stepStartTime = DateTime.now();
      _isSubmitting = false;
      notifyListeners();
      return verifiedStep;
    } catch (e) {
      HapticFeedbackService().stepError();
      // Offline fallback: enqueue step into local persistent queue
      final offlineEvent = UnsyncedStepEvent(
        clientMsgId: clientMsgId,
        sessionId: sessionId,
        nodeId: nodeId,
        stepNumber: stepNumber,
        userExpression: trimmed,
        targetEquation: targetEquation,
        previousStep: previousStep,
        clientTimestamp: now,
        elapsedMs: elapsedMs,
        currentPl: _currentPl,
      );
      _syncQueue.enqueueStep(offlineEvent);

      final fallbackStep = SolutionStep(
        stepNumber: stepNumber,
        userExpression: trimmed,
        isValid: false,
        isTargetReached: false,
        errorMessage: 'Bağlantı kesildi: Adım çevrimdışı kuyruğa güvenle kaydedildi (${_syncQueue.pendingCount} bekliyor).',
        elapsedMs: elapsedMs,
      );
      _steps.add(fallbackStep);
      _isSubmitting = false;
      notifyListeners();
      return fallbackStep;
    }
  }

  Future<int> syncPendingOfflineSteps() async {
    final count = await _syncQueue.replayQueue(_apiService);
    notifyListeners();
    return count;
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
