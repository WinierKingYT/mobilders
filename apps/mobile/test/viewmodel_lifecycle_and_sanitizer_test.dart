import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/data/services/session_websocket_service.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/ui/features/diagnostic/view_models/diagnostic_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';
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
}
