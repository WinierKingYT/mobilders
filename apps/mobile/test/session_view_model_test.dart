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
  @override
  Future<Map<String, dynamic>> replayOfflineBatch({
    required String sessionId,
    required List<Map<String, dynamic>> events,
  }) async {
    if (throwNetworkError) {
      throw const HttpException('Simulated network offline');
    }
    return {
      'session_id': sessionId,
      'synced_count': events.length,
      'latest_p_l': 0.70,
      'is_target_reached': true,
      'replayed_steps': events.map((e) => {
        'step_number': e['step_number'],
        'user_expression': e['user_expression'],
        'is_valid': true,
        'is_target_reached': true,
        'canonical_expression': 'x = 2',
        'error_message': null,
      }).toList(),
    };
  }

  @override
  Future<Map<String, dynamic>> startDailySession({String? userId}) async {
    if (throwNetworkError) {
      throw const HttpException('Simulated network offline');
    }
    return {
      'session_id': 'sess_daily_test_123',
      'duration_limit_minutes': 20,
      'phases': ['warm_up', 'cat_diagnostic', 'problem_board', 'metacognitive_reflection'],
      'target_node': 'N15',
      'target_problem': 'x^2 + 6x = 2',
      'circadian_lock_hours': 14,
    };
  }

  @override
  Future<Map<String, dynamic>> concludeDailySession({String? sessionId}) async {
    if (throwNetworkError) {
      throw const HttpException('Simulated network offline');
    }
    return {
      'status': 'CONCLUDED',
      'circadian_lock_active': true,
      'lock_duration_seconds': 50400,
    };
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

    test('Submitting terminal step marks target reached', () async {
      final step = await viewModel.submitStep('x = 2');

      expect(step, isNotNull);
      expect(step!.isValid, isTrue);
      expect(step.isTargetReached, isTrue);
      expect(viewModel.isTargetReached, isTrue);
      expect(viewModel.currentPl, 0.70);
    });

    test('Submitting invalid step diagnoses misconception bug', () async {
      final step = await viewModel.submitStep('(x - 2)(x - 3) = 4');

      expect(step, isNotNull);
      expect(step!.isValid, isFalse);
      expect(step.detectedBug, isNotNull);
      expect(step.detectedBug!.bugId, 'BUG-QUAD-01');
      expect(viewModel.isTargetReached, isFalse);
    });

    test('Rollback removes steps from current session state', () async {
      await viewModel.submitStep('(x - 2)(x - 3) = 0');
      await viewModel.submitStep('(x - 2)(x - 3) = 4');
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

    test('syncPendingOfflineSteps reconciles local steps and updates mastery', () async {
      final fakeApi = FakeEngineApiService();
      fakeApi.throwNetworkError = true;
      final offlineQueue = OfflineSyncQueue();
      final vm = SessionViewModel(
        apiService: fakeApi,
        sessionId: 'test-session-recon',
        targetEquation: 'x^2 - 5x + 6 = 0',
        syncQueue: offlineQueue,
      );

      // Submit while offline
      await vm.submitStep('x = 2');
      expect(vm.steps.length, 1);
      expect(vm.steps.first.isValid, isFalse);
      expect(vm.pendingOfflineCount, 1);

      // Restore network and sync
      fakeApi.throwNetworkError = false;
      final synced = await vm.syncPendingOfflineSteps();

      expect(synced, 1);
      expect(vm.pendingOfflineCount, 0);
      expect(vm.steps.first.isValid, isTrue);
      expect(vm.steps.first.isTargetReached, isTrue);
      expect(vm.isTargetReached, isTrue);
      expect(vm.currentPl, 0.70);
    });

    test('Accessibility toggles update ViewModel states', () {
      expect(viewModel.isTunnelFocusMode, isFalse);
      expect(viewModel.isDyscalculiaHelper, isFalse);

      viewModel.toggleTunnelFocusMode();
      expect(viewModel.isTunnelFocusMode, isTrue);

      viewModel.toggleDyscalculiaHelper();
      expect(viewModel.isDyscalculiaHelper, isTrue);
    });

    test('startDailySession dynamically initializes session from backend', () async {
      final fakeApi = FakeEngineApiService();
      final vm = SessionViewModel(
        apiService: fakeApi,
        sessionId: 'initial-sess',
        targetEquation: 'initial-eq',
      );

      final result = await vm.startDailySession();

      expect(result['session_id'], 'sess_daily_test_123');
      expect(vm.sessionId, 'sess_daily_test_123');
      expect(vm.targetEquation, 'x^2 + 6x = 2');
      expect(vm.nodeId, 'N15');
      expect(vm.steps, isEmpty);
    });

    test('startDailySession falls back gracefully to local unique session id when offline', () async {
      final fakeApi = FakeEngineApiService();
      fakeApi.throwNetworkError = true;
      final vm = SessionViewModel(
        apiService: fakeApi,
        sessionId: 'initial-sess',
        targetEquation: 'initial-eq',
      );

      final result = await vm.startDailySession();

      expect(result['offline_fallback'], isTrue);
      expect(vm.sessionId.startsWith('sess_local_'), isTrue);
      expect(vm.targetEquation, 'initial-eq');
      expect(vm.steps, isEmpty);
    });

    test('Streak increments on valid step and activates Streak Shield on mistake without reset', () async {
      final fakeApi = FakeEngineApiService();
      final vm = SessionViewModel(
        apiService: fakeApi,
        sessionId: 'streak-test-sess',
        targetEquation: 'x^2 - 5x + 6 = 0',
      );

      expect(vm.streak, 0);
      expect(vm.isShieldActive, isFalse);

      // Step 1: Valid
      await vm.submitStep('(x - 2)(x - 3) = 0');
      expect(vm.streak, 1);
      expect(vm.isShieldActive, isFalse);

      // Step 2: Invalid step -> triggers Streak Shield instead of zeroing streak
      await vm.submitStep('invalid_attempt');
      expect(vm.streak, 1);
      expect(vm.isShieldActive, isTrue);

      // Step 3: Valid recovery step -> Shield consumed, streak increments to 2
      await vm.submitStep('x = 2');
      expect(vm.streak, 2);
      expect(vm.isShieldActive, isFalse);
    });
  });
}
