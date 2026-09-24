import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart' show AppLifecycleState;
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../../data/services/engine_api_service.dart';
import '../../../../data/services/offline_sync_queue.dart';
import '../../../../data/services/session_restoration_manager.dart';
import '../../../../data/services/session_websocket_service.dart';
import '../../../../domain/models/solution_step.dart';
import '../../touchpad/math_touchpad.dart';

class SessionViewModel extends ChangeNotifier {
  final EngineApiService _apiService;
  final OfflineSyncQueue _syncQueue;
  SessionWebSocketService? webSocketService;

  String _sessionId;
  String _targetEquation;
  String _nodeId;

  final List<SolutionStep> _steps = [];
  bool _isSubmitting = false;
  bool _isTargetReached = false;
  double _currentPl = 0.20;
  InputMode _inputMode = InputMode.touchpad;
  DateTime _stepStartTime = DateTime.now();

  // Accessibility, Gamification & UX States
  bool _isTunnelFocusMode = false;
  bool _isDyscalculiaHelper = false;
  bool _isZenMode = false;
  String? _hesitationWhisper;
  Timer? _hesitationTimer;
  DateTime? _hesitationTimerStartedAt;
  Duration _hesitationDuration = const Duration(milliseconds: 6500);
  Duration? _frozenHesitationRemaining;
  int _streak = 0;
  bool _isShieldActive = false;

  SessionViewModel({
    required EngineApiService apiService,
    required String sessionId,
    required String targetEquation,
    String nodeId = 'N15',
    double initialPl = 0.20,
    OfflineSyncQueue? syncQueue,
    this.webSocketService,
  })  : _apiService = apiService,
        _syncQueue = syncQueue ?? OfflineSyncQueue(),
        _sessionId = sessionId,
        _targetEquation = targetEquation,
        _nodeId = nodeId,
        _currentPl = initialPl {
    _stepStartTime = DateTime.now();
  }

  // Getters
  String get sessionId => _sessionId;
  String get targetEquation => _targetEquation;
  String get nodeId => _nodeId;
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
  int get streak => _streak;
  bool get isShieldActive => _isShieldActive;

  void reinitializeSession({
    required String sessionId,
    required String targetEquation,
    required String nodeId,
    double initialPl = 0.20,
    bool preserveStreak = false,
  }) {
    _sessionId = sessionId;
    _targetEquation = targetEquation;
    _nodeId = nodeId;
    _currentPl = initialPl;
    _steps.clear();
    _isTargetReached = false;
    _hesitationTimer?.cancel();
    _hesitationWhisper = null;
    _stepStartTime = DateTime.now();
    if (!preserveStreak) {
      _streak = 0;
      _isShieldActive = false;
    }
    notifyListeners();
  }

  void startNewTarget({
    required String newTargetEquation,
    String? newNodeId,
    String? newSessionId,
    bool preserveStreak = true,
  }) {
    final now = DateTime.now().millisecondsSinceEpoch;
    reinitializeSession(
      sessionId: newSessionId ?? 'sess_twin_$now',
      targetEquation: newTargetEquation,
      nodeId: newNodeId ?? _nodeId,
      preserveStreak: preserveStreak,
    );
  }

  Future<Map<String, dynamic>> startDailySession({String? userId}) async {
    try {
      final data = await _apiService.startDailySession(userId: userId);
      final newSessionId = data['session_id'] as String? ?? 'sess_daily_${DateTime.now().millisecondsSinceEpoch}';
      final newTarget = data['target_problem'] as String? ?? _targetEquation;
      final newNode = data['target_node'] as String? ?? _nodeId;

      reinitializeSession(
        sessionId: newSessionId,
        targetEquation: newTarget,
        nodeId: newNode,
      );
      return data;
    } catch (_) {
      // Graceful offline fallback: generate local unique session id and keep operating
      final fallbackId = 'sess_local_${DateTime.now().millisecondsSinceEpoch}';
      reinitializeSession(
        sessionId: fallbackId,
        targetEquation: _targetEquation,
        nodeId: _nodeId,
      );
      return {
        'session_id': fallbackId,
        'target_problem': _targetEquation,
        'target_node': _nodeId,
        'offline_fallback': true,
      };
    }
  }

  Future<Map<String, dynamic>?> concludeSession() async {
    try {
      final res = await _apiService.concludeDailySession(sessionId: _sessionId);
      return res;
    } catch (_) {
      return {
        'status': 'CONCLUDED',
        'circadian_lock_active': true,
        'offline_fallback': true,
      };
    }
  }

  void setHesitationWhisper(String? whisper) {
    _hesitationWhisper = whisper;
    notifyListeners();
  }

  void dismissHesitationWhisper() {
    _hesitationWhisper = null;
    _hesitationTimer?.cancel();
    notifyListeners();
  }

  bool get isHesitationFrozen => _frozenHesitationRemaining != null;
  Duration? get frozenHesitationRemaining => _frozenHesitationRemaining;

  void startHesitationTimer({Duration duration = const Duration(milliseconds: 6500)}) {
    _hesitationTimer?.cancel();
    _hesitationDuration = duration;
    _hesitationTimerStartedAt = DateTime.now();
    _frozenHesitationRemaining = null;
    _hesitationTimer = Timer(duration, () {
      if (_hesitationWhisper == null && !_isTargetReached && !_isSubmitting) {
        _hesitationWhisper = generateContextualWhisper(_targetEquation);
        notifyListeners();
      }
    });
  }

  /// Freezes hesitation timer when app moves to background / screen turns off (Android Doze)
  void freezeHesitationTimer() {
    if (_hesitationTimer != null && _hesitationTimer!.isActive && _hesitationTimerStartedAt != null) {
      final elapsed = DateTime.now().difference(_hesitationTimerStartedAt!);
      final remaining = _hesitationDuration - elapsed;
      _frozenHesitationRemaining = remaining.isNegative ? Duration.zero : remaining;
      _hesitationTimer?.cancel();
      _hesitationTimer = null;
    }
  }

  /// Resumes hesitation timer with remaining frozen time when returning to foreground
  void unfreezeHesitationTimer() {
    if (_frozenHesitationRemaining != null && _frozenHesitationRemaining! > Duration.zero) {
      startHesitationTimer(duration: _frozenHesitationRemaining!);
      _frozenHesitationRemaining = null;
    }
  }

  /// Handles app lifecycle state transitions to save battery and sleep timers (Android Doze compliance)
  void handleAppLifecycleStateChanged(AppLifecycleState state) {
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.inactive ||
        state == AppLifecycleState.hidden ||
        state == AppLifecycleState.detached) {
      freezeHesitationTimer();
      webSocketService?.pauseHeartbeat();
    } else if (state == AppLifecycleState.resumed) {
      unfreezeHesitationTimer();
      webSocketService?.resumeHeartbeat();
    }
  }

  void resetHesitationTimer({Duration duration = const Duration(milliseconds: 6500)}) {
    if (_hesitationWhisper != null) {
      _hesitationWhisper = null;
      notifyListeners();
    }
    startHesitationTimer(duration: duration);
  }

  static String generateContextualWhisper(String equation) {
    final clean = equation.replaceAll(' ', '');
    if (clean.contains('(')) {
      return 'Önce parantezin önündeki sayıya veya işarete odaklanalım mı?';
    }
    if (clean.contains('^2') || clean.contains('x²') || clean.contains('**2')) {
      return 'Önce tüm terimleri eşitliğin bir tarafına toplayıp sıfır yapalım mı?';
    }
    if (clean.contains('/')) {
      return 'Önce paydaları eşitlemek veya içler-dışlar yapmak işimizi kolaylaştırabilir mi?';
    }
    if (clean.contains('=')) {
      return "Önce x'in yanındaki sabit sayıyı karşıya geçirmeye ne dersin?";
    }
    return 'Küçük bir ilk adımla başlayalım mı?';
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

    _hesitationTimer?.cancel();
    _hesitationWhisper = null;
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
        if (_isShieldActive) {
          _isShieldActive = false;
        }
        _streak++;
        if (verifiedStep.psychometrics != null) {
          _currentPl = verifiedStep.psychometrics!.bktPosteriorPl;
        }
        if (verifiedStep.isTargetReached) {
          _isTargetReached = true;
        }
      } else {
        HapticFeedbackService().stepError();
        if (_streak > 0 && !_isShieldActive) {
          _isShieldActive = true;
        } else if (!_isShieldActive) {
          _streak = 0;
        }
      }

      // Check if there are any pending offline steps to sync in the background
      if (_syncQueue.pendingCount > 0) {
        _syncQueue.replayBatch(_apiService).then((res) {
          _reconcileSteps(res);
          notifyListeners();
        });
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
    final result = await _syncQueue.replayBatch(_apiService);
    _reconcileSteps(result);
    notifyListeners();
    return result.syncedCount;
  }

  void _reconcileSteps(BatchReplayResult result) {
    if (result.syncedCount == 0) return;
    if (result.latestPl != null) {
      _currentPl = result.latestPl!;
    }
    if (result.isTargetReached) {
      _isTargetReached = true;
    }

    for (final replayedJson in result.replayedSteps) {
      final stepNumber = replayedJson['step_number'] as int?;
      final isValid = replayedJson['is_valid'] as bool? ?? false;
      final isTargetReached = replayedJson['is_target_reached'] as bool? ?? false;
      final canonicalExpr = replayedJson['canonical_expression'] as String?;
      final errorMsg = replayedJson['error_message'] as String?;

      if (stepNumber != null && stepNumber > 0 && stepNumber <= _steps.length) {
        final idx = stepNumber - 1;
        final oldStep = _steps[idx];
        _steps[idx] = SolutionStep(
          stepNumber: oldStep.stepNumber,
          userExpression: oldStep.userExpression,
          isValid: isValid,
          isTargetReached: isTargetReached,
          canonicalExpression: canonicalExpr ?? oldStep.canonicalExpression,
          errorMessage: errorMsg,
          elapsedMs: oldStep.elapsedMs,
        );
      }
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
    _hesitationTimer?.cancel();
    _hesitationWhisper = null;
    _stepStartTime = DateTime.now();
    notifyListeners();
  }

  @override
  void dispose() {
    _hesitationTimer?.cancel();
    super.dispose();
  }
}
