import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/offline_sync_queue.dart';
import 'package:personal_learning_engine/domain/models/diagnostic_bug.dart';
import 'package:personal_learning_engine/domain/models/solution_step.dart';
import 'package:personal_learning_engine/domain/models/step_psychometrics.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';

class FakeEngineApiService extends EngineApiService {
  bool throwNetworkError = false;

  FakeEngineApiService() : super(baseUrl: 'http://localhost:8000');

  @override
  Future<SolutionStep> verifyStep({
    required String sessionId,
    required String nodeId,
    required int stepNumber,
    required String userExpression,
    required String targetEquation,
    String? previousStep,
    int? elapsedMs,
    double? currentPl,
    String? clientMsgId,
    DateTime? clientTimestamp,
  }) async {
    if (throwNetworkError) {
      throw const HttpException('Simulated network offline');
    }
    if (userExpression == '(x - 2)(x - 3) = 0') {
      return SolutionStep(
        stepNumber: stepNumber,
        userExpression: userExpression,
        isValid: true,
        isTargetReached: false,
        elapsedMs: elapsedMs ?? 1000,
        psychometrics: const StepPsychometricsModel(
          bktPosteriorPl: 0.45,
          bktNextPl: 0.52,
          ddmDriftRate: 0.15,
          ddmBoundarySeparation: 0.10,
          ddmCognitiveState: 'fluent_mastery',
        ),
      );
    } else if (userExpression == 'x = 2') {
      return SolutionStep(
        stepNumber: stepNumber,
        userExpression: userExpression,
        isValid: true,
        isTargetReached: true,
        elapsedMs: elapsedMs ?? 800,
        psychometrics: const StepPsychometricsModel(
          bktPosteriorPl: 0.70,
          bktNextPl: 0.75,
        ),
      );
    } else {
      return SolutionStep(
        stepNumber: stepNumber,
        userExpression: userExpression,
        isValid: false,
        isTargetReached: false,
        elapsedMs: elapsedMs ?? 2000,
        detectedBug: const DiagnosticBug(
          bugId: 'BUG-QUAD-01',
          severity: 'WARNING',
          category: 'ALGEBRAIC',
          description: 'Sıfır olmayan sayıya sıfır-çarpım kuralı uygulandı',
          remediationDirective: 'Önce tüm terimleri sol tarafa toplayarak sağ tarafı sıfır yap.',
        ),
      );
    }
  }
}

void main() {
  group('SessionViewModel Tests', () {
    late SessionViewModel viewModel;

    setUp(() {
      viewModel = SessionViewModel(
        apiService: FakeEngineApiService(),
        sessionId: 'test-session-001',
        targetEquation: 'x^2 - 5x + 6 = 0',
        nodeId: 'N15',
        initialPl: 0.20,
      );
    });

    test('Initial state is clean with 0 steps', () {
      expect(viewModel.steps, isEmpty);
      expect(viewModel.isSubmitting, isFalse);
      expect(viewModel.isTargetReached, isFalse);
      expect(viewModel.currentPl, 0.20);
    });

    test('Submitting valid step updates mastery and appends step', () async {
      final step = await viewModel.submitStep('(x - 2)(x - 3) = 0');

      expect(step, isNotNull);
      expect(step!.isValid, isTrue);
      expect(viewModel.steps.length, 1);
      expect(viewModel.currentPl, 0.45);
      expect(viewModel.isTargetReached, isFalse);
    });

    test('Submitting final step marks target reached', () async {
      await viewModel.submitStep('(x - 2)(x - 3) = 0');
      await viewModel.submitStep('x = 2');

      expect(viewModel.steps.length, 2);
      expect(viewModel.isTargetReached, isTrue);
    });

    test('Submitting misconception step records bug and preserves currentPl', () async {
      final step = await viewModel.submitStep('(x - 2)(x - 3) = 12');

      expect(step, isNotNull);
      expect(step!.isValid, isFalse);
      expect(step.detectedBug, isNotNull);
      expect(step.detectedBug!.bugId, 'BUG-QUAD-01');
      expect(viewModel.steps.length, 1);
      expect(viewModel.currentPl, 0.20); // Not updated on error
    });

    test('Rollback removes subsequent steps', () async {
      await viewModel.submitStep('(x - 2)(x - 3) = 0');
      await viewModel.submitStep('(x - 2)(x - 3) = 12'); // bad step
      expect(viewModel.steps.length, 2);

      // Rollback to step 1 (remove bad step)
      viewModel.rollbackToStep(1);
      expect(viewModel.steps.length, 1);
      expect(viewModel.steps.first.userExpression, '(x - 2)(x - 3) = 0');
    });

    test('Submitting step during network disconnection enqueues step into offline syncQueue', () async {
      final fakeApi = FakeEngineApiService();
      fakeApi.throwNetworkError = true;
      final offlineQueue = OfflineSyncQueue();
      final vm = SessionViewModel(
        apiService: fakeApi,
        sessionId: 'test-session-offline',
        targetEquation: 'x^2 - 5x + 6 = 0',
        syncQueue: offlineQueue,
      );

      final step = await vm.submitStep('(x - 2)(x - 3) = 0');
      expect(step, isNotNull);
      expect(step!.isValid, isFalse);
      expect(step.errorMessage, contains('çevrimdışı kuyruğa'));
      expect(vm.pendingOfflineCount, 1);
      expect(offlineQueue.pendingEvents.first.userExpression, '(x - 2)(x - 3) = 0');
    });

    test('Accessibility toggles update ViewModel states', () {
      expect(viewModel.isTunnelFocusMode, isFalse);
      expect(viewModel.isDyscalculiaHelper, isFalse);

      viewModel.toggleTunnelFocusMode();
      expect(viewModel.isTunnelFocusMode, isTrue);

      viewModel.toggleDyscalculiaHelper();
      expect(viewModel.isDyscalculiaHelper, isTrue);
    });
  });
}
