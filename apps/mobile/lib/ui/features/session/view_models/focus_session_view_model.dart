import 'package:flutter/foundation.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../../data/models/focus_domain_models.dart';
import '../../../../data/services/focus_api_service.dart';
import '../../touchpad/math_touchpad.dart';

/// Reactive ViewModel managing the cognitive domain lifecycle of a Focus CT-QF1 episode.
class FocusSessionViewModel extends ChangeNotifier {
  final FocusApiService _apiService;
  final HapticFeedbackService _haptic;

  String? _episodeId;
  int _currentSequence = 0;
  FocusEpisodeState? _currentState;
  FocusDecision? _lastDecision;
  AttemptJudgment? _lastJudgment;
  List<String> _lastObservations = [];

  bool _isSubmitting = false;
  String? _errorMessage;
  String? _feedbackMessage;

  String _topicId = 'CT-QF1';
  int _a = 1;
  int _b = 5;
  int _c = 6;
  String _comparator = '<=';
  InputMode _inputMode = InputMode.touchpad;
  bool _isZenMode = false;
  bool _isDisposed = false;

  FocusSessionViewModel({
    required FocusApiService apiService,
    HapticFeedbackService? haptic,
  })  : _apiService = apiService,
        _haptic = haptic ?? HapticFeedbackService();

  // Getters
  String? get episodeId => _episodeId;
  int get currentSequence => _currentSequence;
  FocusEpisodeState? get currentState => _currentState;
  FocusDecision? get lastDecision => _lastDecision;
  AttemptJudgment? get lastJudgment => _lastJudgment;
  List<String> get lastObservations => List.unmodifiable(_lastObservations);

  bool get isSubmitting => _isSubmitting;
  String? get errorMessage => _errorMessage;
  String? get feedbackMessage => _feedbackMessage;

  String get topicId => _topicId;
  int? _divisorRoot;
  int? _x0;

  int get a => _a;
  int get b => _b;
  int get c => _c;
  String get comparator => _comparator;
  int? get divisorRoot => _divisorRoot;
  int? get x0 => _x0;
  InputMode get inputMode => _inputMode;
  bool get isZenMode => _isZenMode;

  String get currentStage => _currentState?.currentStage ?? 'S1_FACTOR';
  String get currentPhase => _currentState?.phase ?? 'WORKSPACE';

  bool get isCompleted => currentPhase == 'COMPLETED';
  bool get isProbing => currentPhase == 'PROBING';
  bool get isRepairing => currentPhase == 'REPAIRING';
  bool get isAwaitingOriginalSelfCorrection =>
      currentPhase == 'AWAITING_ORIGINAL_SELF_CORRECTION';
  bool get isAwaitingTransfer => currentPhase == 'AWAITING_TRANSFER';

  String get targetEquationLatex {
    if (_topicId == 'CT-LIN1') {
      final aStr = _a == 1 ? '' : (_a == -1 ? '-' : '$_a');
      final bPart = _b >= 0 ? '+ $_b' : '- ${-_b}';
      return '$aStr x $bPart = $_c';
    } else if (_topicId == 'CT-INEQ1') {
      final aStr = _a == 1 ? '' : (_a == -1 ? '-' : '$_a');
      final bPart = _b >= 0 ? '+ $_b' : '- ${-_b}';
      final comp = _comparator == '<='
          ? '\\le'
          : (_comparator == '>=' ? '\\ge' : _comparator);
      return '$aStr x $bPart $comp $_c';
    } else if (_topicId == 'CT-PAR1') {
      final aStr = _a == 1 ? '' : (_a == -1 ? '-' : '$_a');
      final bPart = _b >= 0 ? '+ $_b' : '- ${-_b}';
      final cPart = _c >= 0 ? '+ $_c' : '- ${-_c}';
      return 'f(x) = $aStr x^2 $bPart x $cPart';
    } else if (_topicId == 'CT-POLY1') {
      final aStr = _a == 1 ? '' : (_a == -1 ? '-' : '$_a');
      final bPart = _b >= 0 ? '+ $_b' : '- ${-_b}';
      final cPart = _c >= 0 ? '+ $_c' : '- ${-_c}';
      final rootVal = _divisorRoot ?? 1;
      final divPart = rootVal >= 0 ? '(x - $rootVal)' : '(x + ${-rootVal})';
      return 'P(x) = $aStr x^2 $bPart x $cPart \\div $divPart';
    } else if (_topicId == 'CT-TRIG1') {
      final aStr = _a == 1 ? '' : (_a == -1 ? '-' : '$_a');
      final cPart = _c >= 0 ? '- $_c' : '+ ${-_c}';
      return '$aStr\\sin(x) $cPart = 0';
    } else if (_topicId == 'CT-LOG1') {
      final bPart = _b >= 0 ? '- $_b' : '+ ${-_b}';
      return '\\log_{$_a}(x $bPart) = $_c';
    } else if (_topicId == 'CT-LIM1') {
      final aVal = _a;
      final aSquared = aVal * aVal;
      return '\\lim_{x \\to $aVal} \\frac{x^2 - $aSquared}{x - $aVal}';
    } else if (_topicId == 'CT-DERIV1') {
      final aStr = _a == 1 ? '' : (_a == -1 ? '-' : '$_a');
      final bPart = _b >= 0 ? '+ $_b' : '- ${-_b}';
      final cPart = _c >= 0 ? '+ $_c' : '- ${-_c}';
      final x0Val = _x0 ?? _divisorRoot ?? 1;
      return 'f(x) = $aStr x^2 $bPart x $cPart, \\quad x_0 = $x0Val';
    } else if (_topicId == 'CT-INT1') {
      final aVal = _divisorRoot ?? 0;
      final bVal = _c;
      final mVal = _a;
      final nVal = _b;
      final mStr = mVal == 1 ? 'x' : (mVal == -1 ? '-x' : (mVal == 0 ? '' : '${mVal}x'));
      final nStr = nVal > 0 ? '+ $nVal' : (nVal < 0 ? '- ${-nVal}' : '');
      final integrand = (mStr.isNotEmpty && nStr.isNotEmpty)
          ? '$mStr $nStr'
          : (mStr.isNotEmpty ? mStr : (nStr.isNotEmpty ? nStr : '0'));
      return '\\int_{$aVal}^{$bVal} ($integrand) \\, dx';
    }
    final bPart = _b >= 0 ? '+ $_b' : '- ${-_b}';
    final cPart = _c >= 0 ? '+ $_c' : '- ${-_c}';
    return 'x^2 $bPart x $cPart = 0';
  }

  void setInputMode(InputMode mode) {
    _inputMode = mode;
    notifyListeners();
  }

  void toggleZenMode() {
    _isZenMode = !_isZenMode;
    _haptic.selectionClick();
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Start a new Focus episode (supports CT-QF1, CT-LIN1, CT-INEQ1, CT-PAR1, CT-POLY1, CT-TRIG1, CT-LOG1, CT-LIM1, CT-DERIV1).
  Future<void> startEpisode({
    String? episodeId,
    String? learnerId,
    String topicId = 'CT-QF1',
    int? a,
    int? b,
    int? c,
    String? comparator,
    int? divisorRoot,
    int? x0,
  }) async {
    _isSubmitting = true;
    _errorMessage = null;
    _feedbackMessage = null;
    notifyListeners();

    try {
      _topicId = topicId;
      _a = a ?? 1;
      _b = b ?? 5;
      _c = c ?? 6;
      _comparator = comparator ?? '<=';
      _divisorRoot = divisorRoot;
      _x0 = x0;
      final epId = episodeId ?? 'ep-${DateTime.now().millisecondsSinceEpoch}';

      final idKey = '$epId:start';
      final res = await _apiService.startEpisode(
        episodeId: epId,
        topicId: _topicId,
        a: _a,
        b: _b,
        c: _c,
        comparator: _comparator,
        divisorRoot: _divisorRoot,
        x0: _x0,
        idempotencyKey: idKey,
      );

      _episodeId = res.episodeId;
      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _lastDecision = res.decision;
      _lastJudgment = res.judgment;
      _lastObservations = res.observations;
      if (_topicId == 'CT-LIM1') {
        _feedbackMessage = 'Limit ve 0/0 belirsizliği odak seansı başlatıldı.';
      } else if (_topicId == 'CT-DERIV1') {
        _feedbackMessage = 'Polinom türevi ve teğet denklemi odak seansı başlatıldı.';
      } else if (_topicId == 'CT-INT1') {
        _feedbackMessage = 'Belirli integral ve alan hesabı odak seansı başlatıldı.';
      } else if (_topicId == 'CT-QF1') {
        _feedbackMessage = '2. Dereceden denklem odak seansı başlatıldı.';
      } else {
        _feedbackMessage = 'Odak seansı başlatıldı.';
      }
      _haptic.selectionClick();
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Bağlantı hatası: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Submit an attempt for the current workspace stage (S1..S4).
  Future<void> submitStageAttempt(String rawInput) async {
    final trimmed = rawInput.trim();
    if (trimmed.isEmpty || _isSubmitting || _episodeId == null) return;

    _isSubmitting = true;
    _errorMessage = null;
    _feedbackMessage = null;
    notifyListeners();

    try {
      final inputKind = _resolveInputKindForStage(currentStage);
      final idKey = '$_episodeId:attempt:$_currentSequence';

      final res = await _apiService.submitAttempt(
        episodeId: _episodeId!,
        expectedPreviousSequence: _currentSequence,
        inputKind: inputKind,
        rawInput: trimmed,
        idempotencyKey: idKey,
      );

      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _lastDecision = res.decision;
      _lastJudgment = res.judgment;
      _lastObservations = res.observations;

      if (res.judgment == AttemptJudgment.validExpected) {
        _haptic.stepSuccess();
        if (res.state.phase == 'COMPLETED') {
          _feedbackMessage = 'Tebrikler! Denklem başarıyla çözüldü.';
        } else {
          _feedbackMessage = 'Harika! Bir sonraki aşamaya geçildi.';
        }
      } else if (res.judgment == AttemptJudgment.validShortcut) {
        _haptic.stepSuccess();
        _feedbackMessage = 'Kestirme yol başarıyla kabul edildi!';
      } else if (res.state.phase == 'PROBING') {
        _haptic.stepError();
        _feedbackMessage = 'Küçük bir tereddüt yakalandı. Teşhis sorusunu cevaplayalım.';
      } else if (res.state.phase == 'REPAIRING') {
        _haptic.stepError();
        _feedbackMessage = 'Bu kavramı sağlamlaştırmak için mini bir müdahale çalışması yapalım.';
      } else {
        _haptic.stepError();
        _feedbackMessage = 'Adım beklenen kurala uymadı. Lütfen tekrar dene.';
      }
    } on FocusConflictException {
      _errorMessage = 'Oturum dizisi uyuşmazlığı. Lütfen tekrar deneyin.';
      _haptic.stepError();
    } on FocusDisabledException {
      _errorMessage = 'Focus servisi şu an bakımda veya kapalı.';
      _haptic.stepError();
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Adım gönderilirken bir hata oluştu: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Submit response code to a diagnostic probe.
  Future<void> submitProbeOption(String responseCode) async {
    if (_isSubmitting || _episodeId == null) return;

    _isSubmitting = true;
    _errorMessage = null;
    _feedbackMessage = null;
    notifyListeners();

    try {
      final idKey = '$_episodeId:probe:$_currentSequence';
      final probeId = _lastDecision?.probeId ?? 'PR-F2-01';

      final res = await _apiService.submitProbeResponse(
        episodeId: _episodeId!,
        probeId: probeId,
        expectedPreviousSequence: _currentSequence,
        responseCode: responseCode,
        idempotencyKey: idKey,
      );

      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _lastDecision = res.decision;
      _haptic.selectionClick();

      if (res.decision?.action == NextActionType.startRepair) {
        _feedbackMessage = 'Teşhis tamamlandı. Şimdi müdahale adımına geçiyoruz.';
      } else {
        _feedbackMessage = 'Teşhis cevabınız kaydedildi.';
      }
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Prob cevabı iletilemedi: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Begin the active server-authorized repair intervention.
  Future<void> beginRepair() async {
    if (_isSubmitting || _episodeId == null) return;

    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final idKey = '$_episodeId:begin_repair:$_currentSequence';
      final res = await _apiService.beginRepair(
        episodeId: _episodeId!,
        expectedPreviousSequence: _currentSequence,
        idempotencyKey: idKey,
      );

      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _lastDecision = res.decision;
      _feedbackMessage = 'Müdahale çalışması başladı.';
      _haptic.selectionClick();
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Müdahale başlatılamadı: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Submit work on the active intervention template.
  Future<void> submitRepairWork(dynamic rawWork) async {
    if (_isSubmitting || _episodeId == null) return;

    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final idKey = '$_episodeId:repair_work:$_currentSequence';
      final res = await _apiService.submitRepairWork(
        episodeId: _episodeId!,
        expectedPreviousSequence: _currentSequence,
        rawWork: rawWork,
        idempotencyKey: idKey,
      );

      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _haptic.stepSuccess();
      _feedbackMessage = 'Müdahale çalışması başarıyla tamamlandı. Şimdi orijinal problemi düzelt!';
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Müdahale çalışması gönderilemedi: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Submit original self-correction on the quadratic problem.
  Future<void> submitOriginalSelfCorrection(String rawInput) async {
    if (_isSubmitting || _episodeId == null) return;

    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final inputKind = _resolveInputKindForStage(currentStage);
      final idKey = '$_episodeId:self_corr:$_currentSequence';
      final res = await _apiService.submitOriginalSelfCorrection(
        episodeId: _episodeId!,
        expectedPreviousSequence: _currentSequence,
        inputKind: inputKind,
        rawInput: rawInput.trim(),
        idempotencyKey: idKey,
      );

      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _haptic.stepSuccess();
      _feedbackMessage = 'Orijinal adım başarıyla düzeltildi! Şimdi transfer görevini çözelim.';
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Düzeltme adımı gönderilemedi: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Submit learner work on the server-owned transfer problem.
  Future<void> submitTransferWork(dynamic rawWork) async {
    if (_isSubmitting || _episodeId == null) return;

    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final idKey = '$_episodeId:transfer:$_currentSequence';
      final res = await _apiService.submitTransferWork(
        episodeId: _episodeId!,
        expectedPreviousSequence: _currentSequence,
        rawWork: rawWork,
        idempotencyKey: idKey,
      );

      _currentSequence = res.streamVersion;
      _currentState = res.state;
      _haptic.stepSuccess();
      _feedbackMessage = 'Transfer görevi başarıyla tamamlandı! Ana çalışma alanına dönüldü.';
    } on FocusApiException catch (e) {
      _errorMessage = e.message;
      _haptic.stepError();
    } catch (e) {
      _errorMessage = 'Transfer çalışması gönderilemedi: $e';
      _haptic.stepError();
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  /// Map current focus stage string to client attempt input kind enum.
  FocusAttemptInputKind _resolveInputKindForStage(String stage) {
    switch (stage) {
      case 'S1_FACTOR':
        return FocusAttemptInputKind.factorPair;
      case 'S2_BRANCH':
        return FocusAttemptInputKind.branchDecomposition;
      case 'S3_SOLVE_FACTOR_EQUATIONS':
        return FocusAttemptInputKind.branchDecomposition;
      case 'S4_COMPLETE_SOLUTION_SET':
      case 'S3_VERIFY_SOLUTION':
        return FocusAttemptInputKind.solutionSet;
      case 'S1_ISOLATE_TERM':
        return _topicId == 'CT-INEQ1'
            ? FocusAttemptInputKind.inequalityRewrite
            : FocusAttemptInputKind.equationRewrite;
      case 'S2_ISOLATE_VARIABLE':
        return FocusAttemptInputKind.variableAssignment;
      case 'S2_DIRECTION_AWARE_DIVISION':
        return FocusAttemptInputKind.inequalityRewrite;
      case 'S1_CALCULATE_R':
      case 'S2_CALCULATE_K':
        return FocusAttemptInputKind.coordinateAssignment;
      case 'S3_EXTREMUM_CLASSIFICATION':
        return FocusAttemptInputKind.classification;
      case 'S1_ROOT_OF_DIVISOR':
      case 'S2_EVALUATE_REMAINDER':
        return FocusAttemptInputKind.coordinateAssignment;
      case 'S1_ISOLATE_TRIG_VALUE':
        return FocusAttemptInputKind.arithmeticResult;
      case 'S2_DETERMINE_PRINCIPAL_ANGLE':
      case 'S3_DETERMINE_SECONDARY_ROOT':
      case 'S1_EXPONENTIAL_CONVERSION':
        return FocusAttemptInputKind.coordinateAssignment;
      case 'S3_VERIFY_DOMAIN_CONSTRAINT':
        return FocusAttemptInputKind.classification;
      case 'S1_EVALUATE_LIMIT_FORM':
        return FocusAttemptInputKind.classification;
      case 'S2_SIMPLIFY_EXPRESSION':
        return FocusAttemptInputKind.expressionRewrite;
      case 'S3_COMPUTE_FINAL_LIMIT':
        return FocusAttemptInputKind.coordinateAssignment;
      case 'S1_COMPUTE_DERIVATIVE':
        return FocusAttemptInputKind.expressionRewrite;
      case 'S2_EVALUATE_SLOPE':
        return FocusAttemptInputKind.coordinateAssignment;
      case 'S3_DETERMINE_TANGENT_LINE':
        return FocusAttemptInputKind.equationRewrite;
      case 'S1_FIND_ANTIDERIVATIVE':
        return FocusAttemptInputKind.expressionRewrite;
      case 'S2_APPLY_LIMITS':
        return FocusAttemptInputKind.coordinateAssignment;
      case 'S3_COMPUTE_DEFINITE_INTEGRAL':
        return FocusAttemptInputKind.coordinateAssignment;
      default:
        return FocusAttemptInputKind.factorPair;
    }
  }

  bool get isDisposed => _isDisposed;

  @override
  void dispose() {
    _isDisposed = true;
    super.dispose();
  }

  @override
  void notifyListeners() {
    if (!_isDisposed) {
      super.notifyListeners();
    }
  }
}

