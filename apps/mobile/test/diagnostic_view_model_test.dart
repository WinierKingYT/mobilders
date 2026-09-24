import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/diagnostic_item.dart';
import 'package:personal_learning_engine/ui/features/diagnostic/view_models/diagnostic_view_model.dart';

class FakeCatApiService extends EngineApiService {
  FakeCatApiService() : super(baseUrl: 'http://localhost:8000');

  @override
  Future<DiagnosticItem?> getNextCatItem({
    required String sessionId,
    required double currentTheta,
    required List<String> administeredItemIds,
  }) async {
    return const DiagnosticItem(
      itemId: 'CAT-ITEM-01',
      targetNodeId: 'N10',
      prompt: '2x^2 - 8 = 0 denkleminin kökleri nelerdir?',
      difficultyB: 0.0,
      discriminationA: 1.5,
    );
  }

  @override
  Future<DiagnosticSubmitResult> submitCatResponse({
    required String sessionId,
    required String itemId,
    required bool isCorrect,
    required List<List<dynamic>> administeredHistory,
  }) async {
    if (administeredHistory.isEmpty) {
      // First submission: not complete yet
      return const DiagnosticSubmitResult(
        thetaHat: 0.85,
        standardError: 0.52,
        isComplete: false,
        nextItem: DiagnosticItem(
          itemId: 'CAT-ITEM-02',
          targetNodeId: 'N12',
          prompt: 'x^2 - 5x + 6 = 0 ifadesini çarpanlara ayırınız.',
          difficultyB: 0.8,
          discriminationA: 1.6,
        ),
      );
    } else {
      // Second submission: complete (SE <= 0.35)
      return const DiagnosticSubmitResult(
        thetaHat: 1.25,
        standardError: 0.32,
        isComplete: true,
        seededMastery: {'N01': 0.95, 'N12': 0.85, 'N15': 0.40},
        zpdCandidates: ['N15'],
      );
    }
  }
}

void main() {
  group('DiagnosticViewModel Tests', () {
    late DiagnosticViewModel viewModel;

    setUp(() {
      viewModel = DiagnosticViewModel(
        apiService: FakeCatApiService(),
        sessionId: 'test-cat-session-001',
      );
    });

    test('Initial state before loading item', () {
      expect(viewModel.currentItem, isNull);
      expect(viewModel.thetaHat, 0.0);
      expect(viewModel.standardError, 1.0);
      expect(viewModel.isComplete, isFalse);
      expect(viewModel.isLoading, isFalse);
    });

    test('loadFirstItem populates currentItem', () async {
      await viewModel.loadFirstItem();

      expect(viewModel.currentItem, isNotNull);
      expect(viewModel.currentItem!.itemId, 'CAT-ITEM-01');
      expect(viewModel.isLoading, isFalse);
      expect(viewModel.errorMessage, isNull);
    });

    test('submitAnswer updates thetaHat, SE and transitions to next item then completion', () async {
      await viewModel.loadFirstItem();
      expect(viewModel.currentItem!.itemId, 'CAT-ITEM-01');

      // 1. Submit first answer
      final result1 = await viewModel.submitAnswer(true);
      expect(result1, isNotNull);
      expect(viewModel.thetaHat, 0.85);
      expect(viewModel.standardError, 0.52);
      expect(viewModel.isComplete, isFalse);
      expect(viewModel.currentItem, isNotNull);
      expect(viewModel.currentItem!.itemId, 'CAT-ITEM-02');
      expect(viewModel.administeredHistory.length, 1);

      // 2. Submit second answer -> completes test
      final result2 = await viewModel.submitAnswer(true);
      expect(result2, isNotNull);
      expect(viewModel.isComplete, isTrue);
      expect(viewModel.standardError, 0.32);
      expect(viewModel.currentItem, isNull);
      expect(viewModel.zpdCandidates, ['N15']);
      expect(viewModel.calibrationProgress, 1.0);
      expect(viewModel.overallMasteryScore, greaterThan(0.0));
    });

    test('computeWeightedMastery returns 0.0 for empty profile', () {
      final score = DiagnosticViewModel.computeWeightedMastery(
        nodeMasteries: {},
      );
      expect(score, 0.0);
    });

    test('computeWeightedMastery filters NaN and Infinity values safely', () {
      final score = DiagnosticViewModel.computeWeightedMastery(
        nodeMasteries: {
          'N01': double.nan,
          'N02': double.infinity,
          'N03': 0.80,
        },
      );
      expect(score, 0.80);
    });

    test('computeWeightedMastery correctly incorporates resolved twins weighting', () {
      // Without twins: average of 0.40 and 0.80 is 0.60
      final baseline = DiagnosticViewModel.computeWeightedMastery(
        nodeMasteries: {'N01': 0.40, 'N02': 0.80},
      );
      expect(baseline, closeTo(0.60, 0.001));

      // With twins on N02: weight of N02 increases, raising overall mastery
      final boosted = DiagnosticViewModel.computeWeightedMastery(
        nodeMasteries: {'N01': 0.40, 'N02': 0.80},
        resolvedTwinsCount: {'N02': 4},
      );
      expect(boosted, greaterThan(baseline));
    });

    test('overallMasteryScore returns 0.0 before test completion', () {
      expect(viewModel.overallMasteryScore, 0.0);
    });
  });
}
