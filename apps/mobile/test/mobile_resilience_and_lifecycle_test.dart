import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/misconception_profile_model.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/misconception_profiler_screen.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/interactive_socratic_chat_dialog.dart';

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
}
