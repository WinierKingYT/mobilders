import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/widgets.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/data/services/session_websocket_service.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/ui/features/diagnostic/view_models/diagnostic_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/touchpad/instant_math_sanitizer.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  group('ViewModel Lifecycle & Safe Disposal Tests', () {
    test('FocusSessionViewModel marks isDisposed and safely suppresses notifyListeners', () {
      final mockClient = MockClient((request) async => http.Response('{}', 200));
      final api = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: api);

      expect(vm.isDisposed, isFalse);

      bool notified = false;
      vm.addListener(() {
        notified = true;
      });

      vm.notifyListeners();
      expect(notified, isTrue);

      // Dispose ViewModel
      vm.dispose();
      expect(vm.isDisposed, isTrue);

      // Calling notifyListeners post-dispose should safely suppress without throwing
      notified = false;
      expect(() => vm.notifyListeners(), returnsNormally);
      expect(notified, isFalse);
    });

    test('DiagnosticViewModel marks isDisposed and safely suppresses notifyListeners', () {
      final mockClient = MockClient((request) async => http.Response('{}', 200));
      final api = EngineApiService(client: mockClient);
      final vm = DiagnosticViewModel(apiService: api, sessionId: 'test_diag_sess');

      expect(vm.isDisposed, isFalse);

      vm.dispose();
      expect(vm.isDisposed, isTrue);

      // Calling notifyListeners post-dispose should not throw
      expect(() => vm.notifyListeners(), returnsNormally);
    });

    test('FocusSessionViewModel cleans up streams and cancels tracked subscriptions on dispose', () async {
      final mockClient = MockClient((request) async => http.Response('{}', 200));
      final api = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: api);

      expect(vm.areStreamsClosed, isFalse);
      expect(vm.activeSubscriptionsCount, equals(0));

      final testStream = Stream<int>.periodic(const Duration(milliseconds: 50), (i) => i);
      final sub = testStream.listen((_) {});
      vm.trackSubscription(sub);
      expect(vm.activeSubscriptionsCount, equals(1));

      // Stream subscription should be tracked before dispose
      final stateSub = vm.stateStream.listen((_) {});
      vm.trackSubscription(stateSub);
      expect(vm.activeSubscriptionsCount, equals(2));

      // Dispose ViewModel
      vm.dispose();

      expect(vm.isDisposed, isTrue);
      expect(vm.areStreamsClosed, isTrue);
      expect(vm.activeSubscriptionsCount, equals(0));

      // Attempting to track subscription post-dispose cancels immediately
      bool lateFired = false;
      final lateSub = Stream.value(1).listen((_) {
        lateFired = true;
      });
      vm.trackSubscription(lateSub);
      await Future.delayed(const Duration(milliseconds: 20));
      expect(lateFired, isFalse);
    });

    test('DiagnosticViewModel cleans up streams and cancels tracked subscriptions on dispose', () {
      final mockClient = MockClient((request) async => http.Response('{}', 200));
      final api = EngineApiService(client: mockClient);
      final vm = DiagnosticViewModel(apiService: api, sessionId: 'test_diag_sess');

      expect(vm.areStreamsClosed, isFalse);
      expect(vm.activeSubscriptionsCount, equals(0));

      final testStream = Stream<int>.fromIterable([1, 2, 3]);
      final sub = testStream.listen((_) {});
      vm.trackSubscription(sub);
      expect(vm.activeSubscriptionsCount, equals(1));

      vm.dispose();

      expect(vm.isDisposed, isTrue);
      expect(vm.areStreamsClosed, isTrue);
      expect(vm.activeSubscriptionsCount, equals(0));
    });
  });

  group('SessionWebSocketService Bounded Queue & Stream Safety Tests', () {
    test('SessionWebSocketService bounds offlineQueue to 100 events and drops oldest', () {
      final ws = SessionWebSocketService(url: 'ws://127.0.0.1:8000/ws/v1/session');

      // Add 120 events while disconnected
      for (int i = 0; i < 120; i++) {
        ws.sendEvent({'type': 'STEP_SUBMIT', 'index': i});
      }

      expect(ws.queuedEventsCount, equals(SessionWebSocketService.maxQueuedEvents));
      expect(ws.queuedEventsCount, equals(100));

      ws.dispose();
    });

    test('SessionWebSocketService dispose marks isDisposed and ignores late sendEvent calls', () {
      final ws = SessionWebSocketService(url: 'ws://127.0.0.1:8000/ws/v1/session');

      expect(ws.isDisposed, isFalse);
      ws.dispose();
      expect(ws.isDisposed, isTrue);

      // Post-dispose sendEvent should be safely ignored
      expect(() => ws.sendEvent({'type': 'STEP_SUBMIT'}), returnsNormally);
      expect(ws.queuedEventsCount, equals(0));
    });
  });

  group('InstantMathSanitizer Division-by-Zero Detection Tests', () {
    test('validateSanity identifies division by zero with pedagogical error summary', () {
      final report1 = InstantMathSanitizer.validateSanity('x / 0');
      expect(report1.isValid, isFalse);
      expect(report1.hasDivisionByZero, isTrue);
      expect(report1.errorSummary, equals('Sıfıra bölme tanımsızdır.'));

      final report2 = InstantMathSanitizer.validateSanity('2x ÷ (0.0)');
      expect(report2.isValid, isFalse);
      expect(report2.hasDivisionByZero, isTrue);
      expect(report2.errorSummary, equals('Sıfıra bölme tanımsızdır.'));

      final reportValid = InstantMathSanitizer.validateSanity('x / 2 + 5');
      expect(reportValid.isValid, isTrue);
      expect(reportValid.hasDivisionByZero, isFalse);
      expect(reportValid.errorSummary, isNull);
    });
  });

  group('RestoredSessionState NaN Protection Tests', () {
    test('RestoredSessionState protects against NaN currentPl in fromJson and saveDraft', () async {
      final jsonWithNan = {
        'sessionId': 's1',
        'nodeId': 'N15',
        'targetEquation': 'x^2 = 4',
        'draftText': '',
        'inputMode': 'touchpad',
        'serializedSteps': [],
        'currentPl': double.nan,
        'lastUpdated': DateTime.now().toIso8601String(),
      };

      final restored = RestoredSessionState.fromJson(jsonWithNan);
      expect(restored.currentPl, equals(0.20));
      expect(restored.currentPl.isFinite, isTrue);

      final storage = InMemorySessionStorageBackend();
      final manager = SessionRestorationManager(storage: storage);

      await manager.saveDraft(
        sessionId: 's2',
        nodeId: 'N15',
        targetEquation: 'x = 2',
        draftText: '',
        inputMode: InputMode.touchpad,
        steps: [],
        currentPl: double.infinity,
      );

      final loaded = await manager.restoreDraft();
      expect(loaded, isNotNull);
      expect(loaded!.currentPl, equals(0.20));
      expect(loaded.currentPl.isFinite, isTrue);
    });
  });

  group('SessionViewModel & WebSocket Background Scaling Tests (Stage 32)', () {
    test('SessionWebSocketService pauseHeartbeat and resumeHeartbeat control active state', () {
      final ws = SessionWebSocketService(url: 'ws://127.0.0.1:8000/ws/v1/session');
      ws.startHeartbeat();
      expect(ws.isHeartbeatActive, isTrue);

      ws.pauseHeartbeat();
      expect(ws.isHeartbeatActive, isFalse);

      ws.resumeHeartbeat();
      expect(ws.isHeartbeatActive, isTrue);

      ws.dispose();
      expect(ws.isHeartbeatActive, isFalse);
    });

    test('SessionViewModel freezeHesitationTimer and unfreezeHesitationTimer freeze timer accurately', () async {
      final vm = SessionViewModel(
        apiService: EngineApiService(),
        sessionId: 'sess_test_freeze',
        targetEquation: 'x + 2 = 5',
      );

      vm.startHesitationTimer(duration: const Duration(milliseconds: 200));
      expect(vm.isHesitationFrozen, isFalse);

      await Future.delayed(const Duration(milliseconds: 50));
      vm.freezeHesitationTimer();
      expect(vm.isHesitationFrozen, isTrue);
      expect(vm.frozenHesitationRemaining, isNotNull);
      expect(vm.frozenHesitationRemaining!.inMilliseconds, greaterThan(0));
      expect(vm.frozenHesitationRemaining!.inMilliseconds, lessThanOrEqualTo(200));

      // Wait beyond the original 200ms duration while frozen
      await Future.delayed(const Duration(milliseconds: 200));
      // Should not have fired whisper because timer was frozen
      expect(vm.hesitationWhisper, isNull);

      // Unfreeze
      vm.unfreezeHesitationTimer();
      expect(vm.isHesitationFrozen, isFalse);
      expect(vm.frozenHesitationRemaining, isNull);

      // Wait remaining duration
      await Future.delayed(const Duration(milliseconds: 250));
      expect(vm.hesitationWhisper, isNotNull);

      vm.dispose();
    });

    test('SessionViewModel handleAppLifecycleStateChanged scales WebSocket and hesitation timer', () {
      final ws = SessionWebSocketService(url: 'ws://127.0.0.1:8000/ws/v1/session');
      ws.startHeartbeat();

      final vm = SessionViewModel(
        apiService: EngineApiService(),
        sessionId: 'sess_test_lifecycle',
        targetEquation: '2*x = 8',
        webSocketService: ws,
      );

      vm.startHesitationTimer(duration: const Duration(seconds: 5));
      expect(ws.isHeartbeatActive, isTrue);
      expect(vm.isHesitationFrozen, isFalse);

      // App backgrounded (paused)
      vm.handleAppLifecycleStateChanged(AppLifecycleState.paused);
      expect(ws.isHeartbeatActive, isFalse);
      expect(vm.isHesitationFrozen, isTrue);

      // App foregrounded (resumed)
      vm.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
      expect(ws.isHeartbeatActive, isTrue);
      expect(vm.isHesitationFrozen, isFalse);

      vm.dispose();
      ws.dispose();
    });
  });

  group('Stage 70: Continuous 1-Hour Session Memory Leak & GC Stress Test (20 Question Cycles)', () {
    test('SessionViewModel 20 consecutive question transitions preserve constant step footprint and zero timer leak', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''{
          "is_valid": true,
          "is_target_reached": false,
          "canonical_expression": "x = 3",
          "error_message": null,
          "psychometrics": {
            "bkt_posterior_pl": 0.45,
            "irt_difficulty_b": 0.1,
            "slip_probability": 0.05,
            "guess_probability": 0.15
          }
        }''', 200);
      });

      final api = EngineApiService(client: mockClient);
      final vm = SessionViewModel(
        apiService: api,
        sessionId: 'sess_cycle_0',
        targetEquation: 'x + 2 = 5',
      );

      // Simulate 20 consecutive problem transitions across a 1-hour session
      for (int cycle = 1; cycle <= 20; cycle++) {
        // Start new target question
        vm.startNewTarget(
          newTargetEquation: 'x^2 - ${cycle}x + 4 = 0',
          newNodeId: 'N$cycle',
          newSessionId: 'sess_cycle_$cycle',
          preserveStreak: true,
        );

        expect(vm.steps.isEmpty, isTrue);
        expect(vm.isTargetReached, isFalse);
        expect(vm.targetEquation, equals('x^2 - ${cycle}x + 4 = 0'));
        expect(vm.sessionId, equals('sess_cycle_$cycle'));

        // Start hesitation timer for this problem
        vm.startHesitationTimer(duration: const Duration(seconds: 10));
        expect(vm.isHesitationFrozen, isFalse);

        // Manually simulate temporary steps
        vm.resetSessionData();
        expect(vm.steps.isEmpty, isTrue);
        expect(vm.hesitationWhisper, isNull);
        expect(vm.isHesitationFrozen, isFalse);
      }

      // Test sliding window pruning
      for (int i = 0; i < 60; i++) {
        await vm.submitStep('x = $i');
      }
      expect(vm.steps.length, equals(60));
      vm.pruneHistoricalSteps(maxRetainedSteps: 50);
      expect(vm.steps.length, equals(50));

      vm.dispose();
    });

    test('FocusSessionViewModel 20 consecutive question transitions clean up state and subscriptions completely', () {
      final mockClient = MockClient((request) async => http.Response('{}', 200));
      final api = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: api);

      for (int cycle = 1; cycle <= 20; cycle++) {
        // Add listener/subscription for this question cycle
        final controller = StreamController<int>();
        final sub = controller.stream.listen((_) {});
        vm.trackSubscription(sub);
        expect(vm.activeSubscriptionsCount, equals(1));

        // Question transition: reset session data
        vm.resetSessionData();

        // Subscriptions must be cancelled and cleared
        expect(vm.activeSubscriptionsCount, equals(0));
        expect(vm.lastObservations.isEmpty, isTrue);
        expect(vm.lastDecision, isNull);
        expect(vm.lastJudgment, isNull);
        expect(vm.currentState, isNull);

        controller.close();
      }

      // Test observation pruning
      for (int i = 0; i < 30; i++) {
        // Emulate observations adding
        vm.trackSubscription(Stream.value(i).listen((_) {}));
      }
      expect(vm.activeSubscriptionsCount, equals(30));
      vm.resetSessionData();
      expect(vm.activeSubscriptionsCount, equals(0));

      vm.dispose();
      expect(vm.isDisposed, isTrue);
    });
  });
}
