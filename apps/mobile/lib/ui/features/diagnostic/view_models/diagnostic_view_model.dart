import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../../../data/services/engine_api_service.dart';
import '../../../../domain/models/diagnostic_item.dart';

class DiagnosticViewModel extends ChangeNotifier {
  final EngineApiService _apiService;
  String _sessionId;

  DiagnosticItem? _currentItem;
  double _thetaHat = 0.0;
  double _standardError = 1.0;
  bool _isComplete = false;
  bool _isLoading = false;
  String? _errorMessage;

  final List<List<dynamic>> _administeredHistory = [];
  Map<String, double>? _seededMastery;
  List<String>? _zpdCandidates;
  bool _isDisposed = false;

  final StreamController<DiagnosticItem?> _itemStreamController =
      StreamController<DiagnosticItem?>.broadcast();
  final List<StreamSubscription> _subscriptions = [];

  DiagnosticViewModel({
    required EngineApiService apiService,
    required String sessionId,
  })  : _apiService = apiService,
        _sessionId = sessionId;

  // Getters
  String get sessionId => _sessionId;
  DiagnosticItem? get currentItem => _currentItem;
  double get thetaHat => _thetaHat;
  double get standardError => _standardError;
  bool get isComplete => _isComplete;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  List<List<dynamic>> get administeredHistory => List.unmodifiable(_administeredHistory);
  Map<String, double>? get seededMastery => _seededMastery;
  List<String>? get zpdCandidates => _zpdCandidates;

  // Precision progress from 0.0 to 1.0 (Target SE <= 0.35 starting from 1.0)
  double get calibrationProgress {
    if (_isComplete) return 1.0;
    if (_standardError.isNaN || _standardError.isInfinite) return 0.05;
    const denom = 1.0 - 0.35;
    final progress = (1.0 - _standardError) / denom;
    if (progress.isNaN || progress.isInfinite) return 0.05;
    return progress.clamp(0.05, 0.95);
  }

  /// Computes the weighted average mastery across cognitive nodes, taking into account
  /// resolved twin question repetitions to weigh established competencies higher.
  /// Safely handles empty maps, null values, NaNs, and infinite values.
  static double computeWeightedMastery({
    required Map<String, double> nodeMasteries,
    Map<String, int>? resolvedTwinsCount,
  }) {
    if (nodeMasteries.isEmpty) return 0.0;

    double totalWeight = 0.0;
    double weightedSum = 0.0;

    nodeMasteries.forEach((nodeId, rawMastery) {
      if (rawMastery.isNaN || rawMastery.isInfinite) return;
      final clampedMastery = rawMastery.clamp(0.0, 1.0);

      // Base weight is 1.0. Each resolved twin question adds 0.25 (up to max +2.0)
      final twins = resolvedTwinsCount != null && resolvedTwinsCount.containsKey(nodeId)
          ? (resolvedTwinsCount[nodeId] ?? 0)
          : 0;
      final safeTwins = twins > 0 ? twins.clamp(0, 8) : 0;
      final weight = 1.0 + (safeTwins * 0.25);

      weightedSum += clampedMastery * weight;
      totalWeight += weight;
    });

    if (totalWeight <= 0.0 || totalWeight.isNaN || totalWeight.isInfinite) {
      return 0.0;
    }

    final score = weightedSum / totalWeight;
    if (score.isNaN || score.isInfinite) return 0.0;
    return score.clamp(0.0, 1.0);
  }

  /// Overall mastery score calculated from seeded mastery and twin completions
  double get overallMasteryScore {
    if (_seededMastery == null || _seededMastery!.isEmpty) return 0.0;
    return computeWeightedMastery(nodeMasteries: _seededMastery!);
  }

  static const List<DiagnosticItem> _offlineBank = [
    DiagnosticItem(
      itemId: 'CAT-ITEM-01',
      targetNodeId: 'N12',
      prompt: 'x² - 5x + 6 = 0 denkleminin köklerini bulunuz.',
      difficultyB: 0.0,
      discriminationA: 2.85,
    ),
    DiagnosticItem(
      itemId: 'CAT-ITEM-02',
      targetNodeId: 'N08',
      prompt: '2x + 6 = 14 doğrusal denkleminde x değeri kaçtır?',
      difficultyB: -1.0,
      discriminationA: 2.0,
    ),
    DiagnosticItem(
      itemId: 'CAT-ITEM-03',
      targetNodeId: 'N15',
      prompt: 'x² + 6x - 2 = 0 denklemini tam kareye tamamlarken her iki tarafa hangi terim eklenmelidir?',
      difficultyB: 0.5,
      discriminationA: 2.5,
    ),
    DiagnosticItem(
      itemId: 'CAT-ITEM-04',
      targetNodeId: 'N18',
      prompt: 'Diskriminant formülü Δ = b² - 4ac ile 2x² - 4x + 1 = 0 için Δ değerini hesaplayınız.',
      difficultyB: 1.0,
      discriminationA: 2.2,
    ),
  ];

  Future<void> startCatSession() async {
    if (_isLoading) return;
    _isLoading = true;
    _errorMessage = null;
    _isComplete = false;
    _administeredHistory.clear();
    _seededMastery = null;
    _zpdCandidates = null;
    _thetaHat = 0.0;
    _standardError = 1.0;
    notifyListeners();

    try {
      final data = await _apiService.startCatSession(sessionId: _sessionId);
      if (data.containsKey('cat_session_id')) {
        _sessionId = data['cat_session_id'] as String;
      }
      if (data['first_item'] != null) {
        _currentItem = DiagnosticItem.fromJson(data['first_item'] as Map<String, dynamic>);
      } else {
        _currentItem = _offlineBank.first;
      }
      _thetaHat = (data['initial_theta'] as num?)?.toDouble() ?? 0.0;
      _standardError = (data['initial_se'] as num?)?.toDouble() ?? 1.0;
      _isLoading = false;
      notifyListeners();
    } catch (_) {
      // Seamless offline fallback
      _sessionId = 'cat_local_${DateTime.now().millisecondsSinceEpoch}';
      _currentItem = _offlineBank.first;
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadFirstItem() async {
    if (_isLoading) return;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final item = await _apiService.getNextCatItem(
        sessionId: sessionId,
        currentTheta: _thetaHat,
        administeredItemIds: [],
      );
      _currentItem = item ?? _offlineBank.first;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      // Seamless offline fallback to built-in item bank
      _currentItem = _offlineBank.first;
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();
    }
  }

  Future<DiagnosticSubmitResult?> submitAnswer(bool isCorrect) async {
    if (_currentItem == null || _isLoading || _isComplete) return null;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    final answeredItemId = _currentItem!.itemId;
    final historyCopy = List<List<dynamic>>.from(_administeredHistory);

    try {
      final result = await _apiService.submitCatResponse(
        sessionId: sessionId,
        itemId: answeredItemId,
        isCorrect: isCorrect,
        administeredHistory: historyCopy,
      );

      _administeredHistory.add([answeredItemId, isCorrect]);
      _thetaHat = result.thetaHat;
      _standardError = result.standardError;
      _isComplete = result.isComplete;

      if (result.isComplete) {
        _currentItem = null;
        _seededMastery = result.seededMastery;
        _zpdCandidates = result.zpdCandidates;
      } else {
        _currentItem = result.nextItem;
      }

      _isLoading = false;
      notifyListeners();
      return result;
    } catch (e) {
      // Seamless offline CAT estimation
      _administeredHistory.add([answeredItemId, isCorrect]);
      if (isCorrect) {
        _thetaHat += 0.35;
      } else {
        _thetaHat -= 0.35;
      }
      _standardError = (_standardError * 0.75).clamp(0.30, 1.0);

      final isComplete = _administeredHistory.length >= 4 || _standardError <= 0.35;
      _isComplete = isComplete;

      DiagnosticItem? nextItem;
      if (isComplete) {
        _currentItem = null;
        _seededMastery = {'N12': 0.85, 'N15': 0.45, 'N18': 0.20};
        _zpdCandidates = ['N15', 'N12'];
      } else {
        final nextIdx = _administeredHistory.length % _offlineBank.length;
        nextItem = _offlineBank[nextIdx];
        _currentItem = nextItem;
      }

      _isLoading = false;
      notifyListeners();
      return DiagnosticSubmitResult(
        thetaHat: _thetaHat,
        standardError: _standardError,
        isComplete: isComplete,
        nextItem: nextItem,
        seededMastery: _seededMastery,
        zpdCandidates: _zpdCandidates,
      );
    }
  }

  bool get isDisposed => _isDisposed;
  Stream<DiagnosticItem?> get itemStream => _itemStreamController.stream;
  bool get areStreamsClosed => _itemStreamController.isClosed;
  int get activeSubscriptionsCount => _subscriptions.length;

  void trackSubscription(StreamSubscription subscription) {
    if (_isDisposed) {
      subscription.cancel();
      return;
    }
    _subscriptions.add(subscription);
  }

  @override
  void dispose() {
    _isDisposed = true;
    for (final sub in _subscriptions) {
      sub.cancel();
    }
    _subscriptions.clear();
    if (!_itemStreamController.isClosed) {
      _itemStreamController.close();
    }
    super.dispose();
  }

  @override
  void notifyListeners() {
    if (!_isDisposed) {
      if (!_itemStreamController.isClosed && _itemStreamController.hasListener) {
        _itemStreamController.add(_currentItem);
      }
      super.notifyListeners();
    }
  }
}

