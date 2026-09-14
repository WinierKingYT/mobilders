import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/offline_sync_queue.dart';

class MockReplayEngineApiService extends EngineApiService {
  bool shouldSucceed = true;
  List<Map<String, dynamic>> receivedEvents = [];

  MockReplayEngineApiService() : super(baseUrl: 'http://localhost:8000');

  @override
  Future<Map<String, dynamic>> replayOfflineBatch({
    required String sessionId,
    required List<Map<String, dynamic>> events,
  }) async {
    if (!shouldSucceed) {
      throw Exception('Network unreachable (503 Service Unavailable)');
    }
    receivedEvents = List.from(events);
    return {
      'session_id': sessionId,
      'synced_count': events.length,
      'latest_p_l': 0.65,
      'is_target_reached': true,
    };
  }
}

void main() {
  group('OfflineSyncQueue Unit Tests', () {
    late OfflineSyncQueue queue;
    late MockReplayEngineApiService mockApi;

    setUp(() {
      queue = OfflineSyncQueue(); // In-memory
      mockApi = MockReplayEngineApiService();
    });

    test('Initial queue is empty', () {
      expect(queue.pendingCount, 0);
      expect(queue.pendingEvents, isEmpty);
      expect(queue.isSyncing, isFalse);
    });

    test('enqueueStep adds event to queue', () {
      final event = UnsyncedStepEvent(
        clientMsgId: 'msg-001',
        sessionId: 'sess-1',
        nodeId: 'N15',
        stepNumber: 1,
        userExpression: '(x - 2)(x - 3) = 0',
        targetEquation: 'x^2 - 5x + 6 = 0',
        clientTimestamp: DateTime.now(),
        elapsedMs: 1500,
        currentPl: 0.20,
      );

      queue.enqueueStep(event);

      expect(queue.pendingCount, 1);
      expect(queue.pendingEvents.first.clientMsgId, 'msg-001');
      expect(queue.pendingEvents.first.isSynced, isFalse);
    });

    test('calculateBackoffSeconds implements exponential backoff', () {
      expect(OfflineSyncQueue.calculateBackoffSeconds(0), 2);
      expect(OfflineSyncQueue.calculateBackoffSeconds(1), 4);
      expect(OfflineSyncQueue.calculateBackoffSeconds(2), 8);
      expect(OfflineSyncQueue.calculateBackoffSeconds(3), 16);
      expect(OfflineSyncQueue.calculateBackoffSeconds(4), 30); // Capped at 30s
      expect(OfflineSyncQueue.calculateBackoffSeconds(10), 30);
    });

    test('replayQueue synchronizes all pending events and clears queue on success', () async {
      final t0 = DateTime(2026, 9, 14, 20, 0, 0);
      final t1 = DateTime(2026, 9, 14, 20, 1, 0);

      // Enqueue in reverse order to verify chronological sorting
      queue.enqueueStep(UnsyncedStepEvent(
        clientMsgId: 'msg-002',
        sessionId: 'sess-1',
        nodeId: 'N15',
        stepNumber: 2,
        userExpression: 'x = 2',
        targetEquation: 'x^2 - 5x + 6 = 0',
        clientTimestamp: t1,
      ));

      queue.enqueueStep(UnsyncedStepEvent(
        clientMsgId: 'msg-001',
        sessionId: 'sess-1',
        nodeId: 'N15',
        stepNumber: 1,
        userExpression: '(x - 2)(x - 3) = 0',
        targetEquation: 'x^2 - 5x + 6 = 0',
        clientTimestamp: t0,
      ));

      expect(queue.pendingCount, 2);

      final synced = await queue.replayQueue(mockApi);

      expect(synced, 2);
      expect(queue.pendingCount, 0);
      expect(queue.pendingEvents, isEmpty);

      // Verify received events were sent in strict chronological order
      expect(mockApi.receivedEvents.length, 2);
      expect(mockApi.receivedEvents[0]['client_msg_id'], 'msg-001');
      expect(mockApi.receivedEvents[1]['client_msg_id'], 'msg-002');
    });

    test('replayQueue increments retryCount and records error when network fails', () async {
      mockApi.shouldSucceed = false;

      queue.enqueueStep(UnsyncedStepEvent(
        clientMsgId: 'msg-fail',
        sessionId: 'sess-1',
        nodeId: 'N15',
        stepNumber: 1,
        userExpression: 'x^2 = 25',
        targetEquation: 'x^2 - 25 = 0',
        clientTimestamp: DateTime.now(),
      ));

      final synced = await queue.replayQueue(mockApi);

      expect(synced, 0);
      expect(queue.pendingCount, 1);
      final failedEvent = queue.pendingEvents.first;
      expect(failedEvent.retryCount, 1);
      expect(failedEvent.syncError, isNotNull);
      expect(failedEvent.syncError, contains('Network unreachable'));
    });
  });
}
