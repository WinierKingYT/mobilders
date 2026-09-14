import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/session_websocket_service.dart';

void main() {
  group('SessionWebSocketService Offline Queue Tests', () {
    late SessionWebSocketService wsService;

    setUp(() {
      wsService = SessionWebSocketService(url: 'ws://127.0.0.1:8000/ws/v1/session');
    });

    tearDown(() {
      wsService.dispose();
    });

    test('Buffers step submit events in offline queue when disconnected', () {
      expect(wsService.isConnected, isFalse);
      expect(wsService.queuedEventsCount, equals(0));

      wsService.sendStepSubmit(
        rawLatex: 'x^2 + 6x = 2',
        previousStep: 'x^2 + 6x - 2 = 0',
        latencyMs: 2500,
      );

      expect(wsService.queuedEventsCount, equals(1));

      wsService.sendConfidenceSubmit(0.90);
      expect(wsService.queuedEventsCount, equals(2));

      wsService.sendHintRequest('x(x+6) = 2');
      expect(wsService.queuedEventsCount, equals(3));
    });
  });
}
