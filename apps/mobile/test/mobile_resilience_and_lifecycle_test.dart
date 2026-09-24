import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/offline_sync_queue.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/domain/models/misconception_profile_model.dart';
import 'package:personal_learning_engine/domain/models/solution_step.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/misconception_profiler_screen.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/interactive_socratic_chat_dialog.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('SessionViewModel Lifecycle & Disposal Tests', () {
    test('SessionViewModel dispose safely cancels timers', () {
      final api = EngineApiService();
      final vm = SessionViewModel(
        apiService: api,
        sessionId: 'test_lifecycle_01',
        targetEquation: '2x + 4 = 10',
      );

      vm.startHesitationTimer(duration: const Duration(seconds: 10));
      expect(() => vm.dispose(), returnsNormally);
    });

    test('SessionViewModel resetSession clears steps and resets target', () {
      final api = EngineApiService();
      final vm = SessionViewModel(
        apiService: api,
        sessionId: 'test_lifecycle_02',
        targetEquation: 'x^2 = 16',
      );

      vm.startNewTarget(newTargetEquation: 'y^2 = 25', newNodeId: 'N_NEW');
      expect(vm.targetEquation, 'y^2 = 25');
      expect(vm.nodeId, 'N_NEW');
      expect(vm.steps.isEmpty, true);

      vm.resetSession();
      expect(vm.steps.isEmpty, true);
      expect(vm.isTargetReached, false);
    });
  });

  group('EngineApiService Resilience Tests', () {
    test('fetchMisconceptionProfile returns safe fallback on connection error', () async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
      final profile = await api.fetchMisconceptionProfile('unreachable_user');

      expect(profile.userId, 'unreachable_user');
      expect(profile.totalRecordedMistakes, 0);
      expect(profile.categories.isNotEmpty, true);
    });

    test('generateTwinQuestion returns safe fallback for unknown bugId', () async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
      final twin = await api.generateTwinQuestion(bugId: 'UNKNOWN_BUG');

      expect(twin.targetedBugId, 'GENERIC');
      expect(twin.targetEquation.isNotEmpty, true);
      expect(twin.canonicalRoots.isNotEmpty, true);
    });
  });

  group('UI Resilience Without Session Context Tests', () {
    testWidgets('MisconceptionProfilerScreen gracefully shows SnackBar when tapped outside SessionViewModel', (tester) async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
      const profile = MisconceptionProfileResponse(
        userId: 'standalone_user',
        totalRecordedMistakes: 1,
        totalCured: 0,
        overallCureRate: 0.0,
        topRecurringTraps: [
          MisconceptionNode(
            bugId: 'BUG-QUAD-01',
            title: 'Sıfır-Çarpım Kuralı İhlali',
            categoryId: 'KUADRATIK_DENKLEMLER',
            categoryTitle: 'Kuadratik Denklemler',
            cognitiveCause: 'Eşitliğin sağ tarafı sıfırdan farklı.',
            remediationDirective: 'Sağ tarafı sıfır yap.',
            correctPrinciple: 'Sağ taraf sıfır olmalıdır.',
            frequency: 1,
            openCount: 1,
            inRemediationCount: 0,
            curedCount: 0,
            status: 'critical',
            lastOffendingStep: '(x - 2)(x - 3) = 6',
            lastProblem: '(x - 2)(x - 3) = 6',
            avgStabilityDays: 1.0,
          ),
        ],
        categories: [],
      );

      // Render screen WITHOUT SessionViewModel in Provider tree
      await tester.pumpWidget(
        MaterialApp(
          home: MisconceptionProfilerScreen(
            userId: 'standalone_user',
            apiService: api,
            initialProfile: profile,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap trap card to open bottom sheet
      final card = find.byKey(const Key('trap_card_BUG-QUAD-01'));
      expect(card, findsOneWidget);
      await tester.tap(card);
      await tester.pumpAndSettle();

      // Tap twin practice button
      final twinBtn = find.byKey(const Key('start_twin_practice_button'));
      expect(twinBtn, findsOneWidget);
      await tester.tap(twinBtn);
      await tester.pumpAndSettle();

      // Should show the fallback SnackBar without crashing
      expect(find.textContaining('İkiz soru hazırlandı:'), findsOneWidget);
    });

    testWidgets('InteractiveSocraticChatDialog mounts and unmounts cleanly', (tester) async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: InteractiveSocraticChatDialog(
              targetEquation: 'x^2 - 5x + 6 = 0',
              apiService: api,
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.text('Sokratik Öğretmen'), findsOneWidget);

      // Unmount
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
      await tester.pumpAndSettle();
      // No crashes on dispose
      expect(find.text('Sokratik Öğretmen'), findsNothing);
    });
  });

  group('CircuitBreaker & Jitter Retry Network Resilience Tests', () {
    test('CircuitBreaker transitions from closed to open after failureThreshold', () {
      final breaker = CircuitBreaker(failureThreshold: 3, resetTimeout: const Duration(milliseconds: 100));
      expect(breaker.state, CircuitState.closed);
      expect(breaker.isOpen, false);

      breaker.recordFailure();
      expect(breaker.state, CircuitState.closed);
      expect(breaker.isOpen, false);

      breaker.recordFailure();
      expect(breaker.isOpen, false);

      breaker.recordFailure(); // Reached threshold of 3
      expect(breaker.state, CircuitState.open);
      expect(breaker.isOpen, true);
    });

    test('CircuitBreaker transitions to halfOpen after resetTimeout and resets on success', () async {
      final breaker = CircuitBreaker(failureThreshold: 2, resetTimeout: const Duration(milliseconds: 50));
      breaker.recordFailure();
      breaker.recordFailure();
      expect(breaker.isOpen, true);

      await Future<void>.delayed(const Duration(milliseconds: 60));
      // Checking isOpen after timeout transitions to halfOpen and returns false (allows probe)
      expect(breaker.isOpen, false);
      expect(breaker.state, CircuitState.halfOpen);

      breaker.recordSuccess();
      expect(breaker.state, CircuitState.closed);
      expect(breaker.failureCount, 0);
    });

    test('executeWithRetry retries transient errors and succeeds within maxRetries', () async {
      final api = EngineApiService();
      int callCount = 0;

      final result = await api.executeWithRetry(() async {
        callCount++;
        if (callCount < 2) {
          throw const FormatException('Transient socket drop');
        }
        return 'success_payload';
      }, maxRetries: 2, minJitterMs: 10, maxJitterMs: 20);

      expect(result, 'success_payload');
      expect(callCount, 2);
    });

    test('When CircuitBreaker is open, executeWithRetry fails fast without making network requests', () async {
      final breaker = CircuitBreaker(failureThreshold: 1);
      breaker.recordFailure(); // Open circuit immediately
      expect(breaker.isOpen, true);

      final api = EngineApiService(circuitBreaker: breaker);
      int attemptsMade = 0;

      expect(
        () => api.executeWithRetry(() async {
          attemptsMade++;
          return 'ok';
        }),
        throwsA(isA<Exception>()),
      );

      // Failed fast without invoking action
      expect(attemptsMade, 0);
    });

    test('SessionViewModel submitStep falls back immediately to offline queue when circuit breaker trips', () async {
      final breaker = CircuitBreaker(failureThreshold: 1);
      breaker.recordFailure(); // Circuit is OPEN
      expect(breaker.isOpen, true);

      final api = EngineApiService(circuitBreaker: breaker);
      final vm = SessionViewModel(
        apiService: api,
        sessionId: 'test_circuit_open',
        targetEquation: 'x + 3 = 7',
      );

      final step = await vm.submitStep('x = 4');
      expect(step, isNotNull);
      expect(step!.isValid, false);
      expect(step.errorMessage, contains('çevrimdışı'));
      expect(vm.syncQueue.pendingCount, 1);
    });
  });

  group('BatteryPowerOptimizer & Dynamic Refresh Rate (120Hz -> 60Hz) Tests (Stage 34)', () {
    late BatteryPowerOptimizer optimizer;

    setUp(() {
      optimizer = BatteryPowerOptimizer();
      optimizer.reset();
    });

    tearDown(() {
      optimizer.reset();
    });

    test('Normal battery level (> 15%) maintains 120Hz LTPO refresh and enables particle effects', () {
      optimizer.updateBatteryState(batteryLevelPercent: 85);

      expect(optimizer.isLowPowerMode, isFalse);
      expect(optimizer.batteryLevelPercent, equals(85));
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.highRefresh120Hz));
      expect(optimizer.targetFrameRate.targetFps, equals(120));
      expect(optimizer.enableParticleEffects, isTrue);
      expect(optimizer.enableHeavyCanvasAnimations, isTrue);

      expect(AppTheme.currentFrameRate, equals(FrameRateTarget.highRefresh120Hz));
      expect(AppTheme.areParticlesEnabled, isTrue);
      expect(AppTheme.isLowPowerMode, isFalse);
    });

    test('Low battery (<= 15%) dynamically throttles frame rate to 60Hz and disables particles', () {
      optimizer.updateBatteryState(batteryLevelPercent: 14);

      expect(optimizer.isLowPowerMode, isTrue);
      expect(optimizer.batteryLevelPercent, equals(14));
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.standard60Hz));
      expect(optimizer.targetFrameRate.targetFps, equals(60));
      expect(optimizer.enableParticleEffects, isFalse);
      expect(optimizer.enableHeavyCanvasAnimations, isFalse);

      expect(AppTheme.currentFrameRate, equals(FrameRateTarget.standard60Hz));
      expect(AppTheme.areParticlesEnabled, isFalse);
      expect(AppTheme.isLowPowerMode, isTrue);
    });

    test('Critical battery (<= 5%) throttles frame rate to 30Hz power saver mode', () {
      optimizer.updateBatteryState(batteryLevelPercent: 4);

      expect(optimizer.isLowPowerMode, isTrue);
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.powerSaver30Hz));
      expect(optimizer.targetFrameRate.targetFps, equals(30));
      expect(optimizer.enableParticleEffects, isFalse);
    });

    test('Manual power saver trigger forces 60Hz throttle regardless of battery level', () {
      optimizer.updateBatteryState(batteryLevelPercent: 90, isPowerSaverActive: true);

      expect(optimizer.isLowPowerMode, isTrue);
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.standard60Hz));
      expect(optimizer.enableParticleEffects, isFalse);
    });

    test('Reset restores 100% battery state and 120Hz high refresh target', () {
      optimizer.updateBatteryState(batteryLevelPercent: 10);
      expect(optimizer.isLowPowerMode, isTrue);

      optimizer.reset();
      expect(optimizer.isLowPowerMode, isFalse);
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.highRefresh120Hz));
      expect(optimizer.enableParticleEffects, isTrue);
    });
  });

  group('Cold Boot, Application Termination & Offline Recovery Tests (Stage 59)', () {
    test('Lifecycle & Cold Boot: Application termination restores session steps and state', () async {
      final tempDir = Directory.systemTemp.createTempSync('cold_boot_sim_');
      final backend = FileSessionStorageBackend(baseDirectoryPath: tempDir.path);
      final manager = SessionRestorationManager(storage: backend);

      final steps = [
        const SolutionStep(
          stepNumber: 1,
          userExpression: 'x^2 - 5x = -6',
          isValid: true,
          isTargetReached: false,
          elapsedMs: 1200,
          canonicalExpression: 'x^2 - 5*x + 6 = 0',
        ),
        const SolutionStep(
          stepNumber: 2,
          userExpression: '(x - 2)(x - 3) = 0',
          isValid: true,
          isTargetReached: false,
          elapsedMs: 1400,
          canonicalExpression: '(x - 2)*(x - 3) = 0',
        ),
        const SolutionStep(
          stepNumber: 3,
          userExpression: 'x = 2 or x = 3',
          isValid: true,
          isTargetReached: true,
          elapsedMs: 1600,
          canonicalExpression: 'x = 2',
        ),
      ];

      // Uygulama kapanmadan önce aktif seansı kaydet
      await manager.saveDraft(
        sessionId: 'sess_cold_boot_01',
        nodeId: 'N15',
        targetEquation: 'x^2 - 5*x + 6 = 0',
        draftText: 'x = 2 or x = 3',
        inputMode: InputMode.touchpad,
        steps: steps,
        currentPl: 0.85,
      );

      expect((await manager.restoreDraft()), isNotNull);

      // Uygulama kapanması ve soğuk başlatma simülasyonu (Cold Boot)
      final coldBootBackend = FileSessionStorageBackend(baseDirectoryPath: tempDir.path);
      final coldBootManager = SessionRestorationManager(storage: coldBootBackend);

      final restored = await coldBootManager.restoreDraft();
      expect(restored, isNotNull);
      expect(restored!.sessionId, equals('sess_cold_boot_01'));
      expect(restored.nodeId, equals('N15'));
      expect(restored.targetEquation, equals('x^2 - 5*x + 6 = 0'));
      expect(restored.draftText, equals('x = 2 or x = 3'));
      expect(restored.currentPl, equals(0.85));

      final restoredSteps = restored.toSolutionSteps();
      expect(restoredSteps.length, equals(3));
      expect(restoredSteps[0].userExpression, equals('x^2 - 5x = -6'));
      expect(restoredSteps[1].userExpression, equals('(x - 2)(x - 3) = 0'));
      expect(restoredSteps[2].userExpression, equals('x = 2 or x = 3'));
      expect(restoredSteps[2].isTargetReached, isTrue);

      try {
        tempDir.deleteSync(recursive: true);
      } catch (_) {}
    });

    test('Offline Step Recovery: 5 consecutive steps are queued and synced upon reconnection', () async {
      final tempQueueFile = File('${Directory.systemTemp.path}/offline_queue_test_59.json');
      final syncQueue = OfflineSyncQueue(storageFilePath: tempQueueFile.path);
      await syncQueue.clearQueue();

      // Çevrimdışıyken girilen 5 ardışık adımı simüle et
      final offlineSteps = [
        'x^2 - 5x = -6',
        'x^2 - 5x + 6 = 0',
        '(x - 2)(x - 3) = 0',
        'x - 2 = 0 or x - 3 = 0',
        'x = 2 or x = 3',
      ];

      for (int i = 0; i < offlineSteps.length; i++) {
        final event = UnsyncedStepEvent(
          clientMsgId: 'cmsg_offline_${i + 1}',
          sessionId: 'sess_offline_5steps',
          nodeId: 'N15',
          stepNumber: i + 1,
          userExpression: offlineSteps[i],
          targetEquation: 'x^2 - 5*x + 6 = 0',
          previousStep: i > 0 ? offlineSteps[i - 1] : null,
          clientTimestamp: DateTime.now(),
          elapsedMs: 1200 + i * 100,
          currentPl: 0.20 + i * 0.10,
        );
        syncQueue.enqueueStep(event);
      }

      expect(syncQueue.pendingCount, equals(5));

      // Sunucu yeniden bağlandığında batch replay paketi kabul edilir
      final mockClient = MockClient((request) async {
        if (request.url.path.contains('/api/v1/session/replay-queue')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          final events = body['events'] as List<dynamic>;
          expect(events.length, equals(5));

          final replayed = events.map((e) {
            final num = e['step_number'] as int;
            return {
              'step_number': num,
              'is_valid': true,
              'is_target_reached': num == 5,
              'canonical_expression': e['user_expression'],
              'error_message': null,
            };
          }).toList();

          return http.Response(
            jsonEncode({
              'replayed_steps': replayed,
              'latest_p_l': 0.85,
              'is_target_reached': true,
              'synced_count': 5,
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final onlineApi = EngineApiService(client: mockClient);

      // Yeniden bağlanma sonrası kuyruk replay edilir
      final result = await syncQueue.replayBatch(onlineApi);

      expect(result.syncedCount, equals(5));
      expect(result.isTargetReached, isTrue);
      expect(result.latestPl, equals(0.85));
      expect(syncQueue.pendingCount, equals(0));

      try {
        if (tempQueueFile.existsSync()) {
          tempQueueFile.deleteSync();
        }
      } catch (_) {}
    });
  });
}
