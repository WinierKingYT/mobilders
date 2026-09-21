import 'dart:convert';
import 'dart:io';
import 'dart:math';
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

    test('replayBatch returns structured BatchReplayResult', () async {
      queue.enqueueStep(UnsyncedStepEvent(
        clientMsgId: 'msg-batch-01',
        sessionId: 'sess-batch',
        nodeId: 'N15',
        stepNumber: 1,
        userExpression: 'x^2 + 6x = 2',
        targetEquation: 'x^2 + 6x - 2 = 0',
        clientTimestamp: DateTime.now(),
      ));

      final result = await queue.replayBatch(mockApi);
      expect(result.syncedCount, 1);
      expect(result.latestPl, 0.65);
      expect(result.isTargetReached, isTrue);
      expect(queue.lastReplayResult, isNotNull);
      expect(queue.lastReplayResult!.syncedCount, 1);
    });

    test('OfflineSyncQueue persists and reloads regular and focus events from disk asynchronously', () async {
      final tempFile = '${tempDirectory()}/offline_queue_test_${DateTime.now().millisecondsSinceEpoch}.json';
      final fileQueue = OfflineSyncQueue(storageFilePath: tempFile);

      fileQueue.enqueueStep(UnsyncedStepEvent(
        clientMsgId: 'step-disk-01',
        sessionId: 'sess-disk',
        nodeId: 'N15',
        stepNumber: 1,
        userExpression: 'x + 1 = 2',
        targetEquation: 'x = 1',
        clientTimestamp: DateTime.now(),
      ));

      fileQueue.enqueueFocusAttempt(UnsyncedFocusAttemptEvent(
        clientMsgId: 'focus-disk-01',
        episodeId: 'ep-01',
        expectedSequence: 1,
        rawAttempt: '(x - 1)(x - 2) = 0',
        clientTimestamp: DateTime.now(),
      ));

      // Wait a moment for async file I/O flush
      await Future.delayed(const Duration(milliseconds: 50));

      // Create a second queue instance pointing to the same file
      final reloadedQueue = OfflineSyncQueue(storageFilePath: tempFile);
      await reloadedQueue.load();

      expect(reloadedQueue.pendingCount, 1);
      expect(reloadedQueue.pendingEvents.first.clientMsgId, 'step-disk-01');
      expect(reloadedQueue.pendingFocusCount, 1);
      expect(reloadedQueue.pendingFocusEvents.first.clientMsgId, 'focus-disk-01');

      // Cleanup
      await reloadedQueue.clearQueue();
    });

    test('calculateBackoffWithJitter returns randomized delay in [0, baseBackoff]', () {
      for (int r = 0; r <= 5; r++) {
        final base = OfflineSyncQueue.calculateBackoffSeconds(r).toDouble();
        final jitter = OfflineSyncQueue.calculateBackoffWithJitter(r);
        expect(jitter, greaterThanOrEqualTo(0.0));
        expect(jitter, lessThanOrEqualTo(base));
      }

      // Verify deterministic behavior with seeded Random
      final seeded = OfflineSyncQueue.calculateBackoffWithJitter(2, random: FakeRandom(0.5));
      expect(seeded, equals(4.0)); // 8s base * 0.5 = 4.0
    });

    test('OfflineSyncQueue recovers from .tmp file when main file is absent', () async {
      final baseFilePath = '${tempDirectory()}/offline_queue_crash_${DateTime.now().millisecondsSinceEpoch}.json';
      final tmpFile = File('$baseFilePath.tmp');
      await tmpFile.parent.create(recursive: true);

      final payload = {
        'events': [
          UnsyncedStepEvent(
            clientMsgId: 'step-crash-01',
            sessionId: 'sess-crash',
            nodeId: 'N15',
            stepNumber: 1,
            userExpression: '2x = 10',
            targetEquation: '2x - 10 = 0',
            clientTimestamp: DateTime.now(),
          ).toJson(),
        ],
        'focus_events': [],
      };
      await tmpFile.writeAsString(jsonEncode(payload), flush: true);

      final queue = OfflineSyncQueue(storageFilePath: baseFilePath);
      await queue.load();

      expect(queue.pendingCount, 1);
      expect(queue.pendingEvents.first.clientMsgId, 'step-crash-01');

      // The main file should have been restored
      expect(await File(baseFilePath).exists(), isTrue);

      // Cleanup
      await queue.clearQueue();
      if (await File(baseFilePath).exists()) await File(baseFilePath).delete();
      if (await tmpFile.exists()) await tmpFile.delete();
    });

    test('OfflineSyncQueue backs up corrupt JSON to .corrupt.bak on FormatException', () async {
      final baseFilePath = '${tempDirectory()}/offline_queue_corrupt_${DateTime.now().millisecondsSinceEpoch}.json';
      final mainFile = File(baseFilePath);
      await mainFile.parent.create(recursive: true);
      await mainFile.writeAsString('MALFORMED_JSON_CONTENT {{{', flush: true);

      final queue = OfflineSyncQueue(storageFilePath: baseFilePath);
      await queue.load();

      expect(queue.pendingCount, 0);

      final bakFile = File('$baseFilePath.corrupt.bak');
      expect(await bakFile.exists(), isTrue);
      final bakContent = await bakFile.readAsString();
      expect(bakContent, 'MALFORMED_JSON_CONTENT {{{');

      // Cleanup
      if (await mainFile.exists()) await mainFile.delete();
      if (await bakFile.exists()) await bakFile.delete();
    });
  });
}

class FakeRandom implements Random {
  final double fixedValue;
  FakeRandom(this.fixedValue);

  @override
  double nextDouble() => fixedValue;

  @override
  bool nextBool() => true;

  @override
  int nextInt(int max) => (fixedValue * max).toInt();
}

String tempDirectory() {
  return Directory.systemTemp.path;
}
