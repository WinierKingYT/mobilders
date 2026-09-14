import 'package:flutter/foundation.dart';
import '../../../../data/services/engine_api_service.dart';
import '../../../../domain/models/diagnostic_item.dart';

class DiagnosticViewModel extends ChangeNotifier {
  final EngineApiService _apiService;
  final String sessionId;

  DiagnosticItem? _currentItem;
  double _thetaHat = 0.0;
  double _standardError = 1.0;
  bool _isComplete = false;
  bool _isLoading = false;
  String? _errorMessage;

  final List<List<dynamic>> _administeredHistory = [];
  Map<String, double>? _seededMastery;
  List<String>? _zpdCandidates;

  DiagnosticViewModel({
    required EngineApiService apiService,
    required this.sessionId,
  }) : _apiService = apiService;

  // Getters
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
    final progress = (1.0 - _standardError) / (1.0 - 0.35);
    return progress.clamp(0.05, 0.95);
  }

  Future<void> loadFirstItem() async {
    if (_isLoading) return;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentItem = await _apiService.getNextCatItem(
        sessionId: sessionId,
        currentTheta: _thetaHat,
        administeredItemIds: [],
      );
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = 'Soru yüklenemedi: $e';
      _isLoading = false;
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
      _errorMessage = 'Cevap gönderilemedi: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }
}
