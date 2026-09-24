import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/offline_sync_queue.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/domain/models/solution_step.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('FileSessionStorageBackend Tests', () {
    late Directory tempDir;
    late FileSessionStorageBackend storage;

    setUp(() async {
      tempDir = await Directory.systemTemp.createTemp('ple_storage_test_');
      storage = FileSessionStorageBackend(baseDirectoryPath: tempDir.path);
    });

    tearDown(() async {
      try {
        if (await tempDir.exists()) {
          await tempDir.delete(recursive: true);
        }
      } catch (_) {
        // Windows file locking tolerance for temporary test directories
      }
    });

    test('write, read, and delete perform persistent async operations', () async {
      const key = 'test_session_key';
      const data = '{"sessionId": "test-123", "score": 95}';

      // Initially null
      expect(await storage.read(key), isNull);

      // Write
      await storage.write(key, data);

      // Read back
      final readData = await storage.read(key);
      expect(readData, equals(data));

      // Delete
      await storage.delete(key);
      expect(await storage.read(key), isNull);
    });

    test('SessionRestorationManager persists and restores regular session drafts with File backend', () async {
      final manager = SessionRestorationManager(storage: storage);

      final steps = [
        const SolutionStep(
          stepNumber: 1,
          userExpression: 'x^2 + 6x = 2',
          isValid: true,
          isTargetReached: false,
          elapsedMs: 1200,
        ),
      ];

      await manager.saveDraft(
        sessionId: 'sess-restore-01',
        nodeId: 'N15',
        targetEquation: 'x^2 + 6x - 2 = 0',
        draftText: 'x^2 + 6x + 9',
        inputMode: InputMode.touchpad,
        steps: steps,
        currentPl: 0.45,
      );

      // Instantiate a new manager using the same storage backend (simulating app relaunch)
      final restoredManager = SessionRestorationManager(storage: storage);
      final restoredState = await restoredManager.restoreDraft();

      expect(restoredState, isNotNull);
      expect(restoredState!.sessionId, 'sess-restore-01');
      expect(restoredState.nodeId, 'N15');
      expect(restoredState.targetEquation, 'x^2 + 6x - 2 = 0');
      expect(restoredState.draftText, 'x^2 + 6x + 9');
      expect(restoredState.currentPl, 0.45);
      expect(restoredState.serializedSteps.length, 1);
      expect(restoredState.toSolutionSteps().first.userExpression, 'x^2 + 6x = 2');

      // Clear draft
      await restoredManager.clearDraft();
      expect(await restoredManager.restoreDraft(), isNull);
    });

    test('SessionRestorationManager persists and restores Focus session drafts with File backend', () async {
      final manager = SessionRestorationManager(storage: storage);

      final focusDraft = RestoredFocusSessionState(
        episodeId: 'ep-focus-01',
        topicId: 'CT-QF1',
        sequence: 2,
        a: 1,
        b: 5,
        c: 6,
        comparator: '<=',
        draftText: '(x + 2)(x + 3) <= 0',
        inputMode: InputMode.touchpad,
        isZenMode: true,
        currentStage: 'S1_FACTOR',
        currentPhase: 'WORKSPACE',
        lastUpdated: DateTime.now(),
      );

      await manager.saveFocusDraft(focusDraft);

      // Restore from fresh manager
      final restoredManager = SessionRestorationManager(storage: storage);
      final restored = await restoredManager.restoreFocusDraft();

      expect(restored, isNotNull);
      expect(restored!.episodeId, 'ep-focus-01');
      expect(restored.topicId, 'CT-QF1');
      expect(restored.sequence, 2);
      expect(restored.draftText, '(x + 2)(x + 3) <= 0');
      expect(restored.isZenMode, isTrue);

      await restoredManager.clearFocusDraft();
      expect(await restoredManager.restoreFocusDraft(), isNull);
    });

    test('FileSessionStorageBackend writes atomically and cleans up .tmp', () async {
      const key = 'atomic_test_key';
      const data = '{"status": "atomic_ok"}';

      await storage.write(key, data);

      final primaryFile = storage.getFile(key);
      final tmpFile = File('${primaryFile.path}.tmp');

      expect(await primaryFile.exists(), isTrue);
      expect(await tmpFile.exists(), isFalse);
      expect(await storage.read(key), equals(data));
    });

    test('FileSessionStorageBackend recovers from .tmp file on read if primary file is missing', () async {
      const key = 'crash_recovery_key';
      const data = '{"status": "recovered_from_tmp"}';

      final primaryFile = storage.getFile(key);
      final tmpFile = File('${primaryFile.path}.tmp');

      await tmpFile.parent.create(recursive: true);
      await tmpFile.writeAsString(data, flush: true);

      // Primary file does not exist yet
      expect(await primaryFile.exists(), isFalse);

      final readData = await storage.read(key);
      expect(readData, equals(data));

      // After read recovery, primary file exists
      expect(await primaryFile.exists(), isTrue);
    });

    test('FileSessionStorageBackend delete removes both primary and .tmp files', () async {
      const key = 'cleanup_both_key';
      final primaryFile = storage.getFile(key);
      final tmpFile = File('${primaryFile.path}.tmp');

      await primaryFile.parent.create(recursive: true);
      await primaryFile.writeAsString('primary');
      await tmpFile.writeAsString('temporary');

      expect(await primaryFile.exists(), isTrue);
      expect(await tmpFile.exists(), isTrue);

      await storage.delete(key);

      expect(await primaryFile.exists(), isFalse);
      expect(await tmpFile.exists(), isFalse);
    });

    test('SessionRestorationManager creates .corrupt.bak when reading corrupt session draft', () async {
      final manager = SessionRestorationManager(storage: storage);
      final primaryFile = storage.getFile(SessionRestorationManager.defaultDraftKey);

      await primaryFile.parent.create(recursive: true);
      await primaryFile.writeAsString('{ broken_json_payload !!!');

      final restored = await manager.restoreDraft();
      expect(restored, isNull);

      final bakFile = File('${primaryFile.path}.corrupt.bak');
      expect(await bakFile.exists(), isTrue);
      expect(await bakFile.readAsString(), equals('{ broken_json_payload !!!'));

      // Primary file should have been cleared
      expect(await primaryFile.exists(), isFalse);
    });

    test('SessionRestorationManager creates .corrupt.bak when reading corrupt focus session draft', () async {
      final manager = SessionRestorationManager(storage: storage);
      final primaryFile = storage.getFile(SessionRestorationManager.defaultFocusDraftKey);

      await primaryFile.parent.create(recursive: true);
      await primaryFile.writeAsString('INVALID_FOCUS_JSON ####');

      final restored = await manager.restoreFocusDraft();
      expect(restored, isNull);

      final bakFile = File('${primaryFile.path}.corrupt.bak');
      expect(await bakFile.exists(), isTrue);
      expect(await bakFile.readAsString(), equals('INVALID_FOCUS_JSON ####'));

      // Primary file should have been cleared
      expect(await primaryFile.exists(), isFalse);
    });

    test('restoreDraftWithParity succeeds when equation matches and discards when equation differs', () async {
      final manager = SessionRestorationManager(storage: storage);

      await manager.saveDraft(
        sessionId: 'sess_parity_01',
        nodeId: 'N_PARITY',
        targetEquation: '2x + 4 = 10',
        draftText: '2x = 6',
        inputMode: InputMode.touchpad,
        steps: const [],
        currentPl: 0.30,
      );

      // 1. Matches: Should restore successfully
      final restored = await manager.restoreDraftWithParity(currentTargetEquation: '2x + 4 = 10');
      expect(restored, isNotNull);
      expect(restored!.draftText, '2x = 6');

      // 2. Mismatch: User opened a different question ('x^2 - 9 = 0')
      // Parity check must detect mismatch, discard stale draft, and return null
      final mismatched = await manager.restoreDraftWithParity(currentTargetEquation: 'x^2 - 9 = 0');
      expect(mismatched, isNull);

      // Draft has been cleared from storage
      expect(await manager.restoreDraft(), isNull);
    });

    test('OfflineSyncQueue filters and purges stale equation events for parity', () async {
      final queueFile = File('${tempDir.path}/queue.json');
      final queue = OfflineSyncQueue(storageFilePath: queueFile.path);

      final event1 = UnsyncedStepEvent(
        clientMsgId: 'm1',
        sessionId: 's1',
        nodeId: 'N1',
        stepNumber: 1,
        userExpression: '2x = 6',
        targetEquation: '2x + 4 = 10',
        clientTimestamp: DateTime.now(),
      );

      final event2 = UnsyncedStepEvent(
        clientMsgId: 'm2',
        sessionId: 's1',
        nodeId: 'N2',
        stepNumber: 1,
        userExpression: 'x = 3',
        targetEquation: 'x^2 = 9',
        clientTimestamp: DateTime.now(),
      );

      queue.enqueueStep(event1);
      queue.enqueueStep(event2);

      // Parity filter
      final target1Events = queue.getPendingEventsForEquation('2x + 4 = 10');
      expect(target1Events.length, 1);
      expect(target1Events.first.userExpression, '2x = 6');

      final target2Events = queue.getPendingEventsForEquation('x^2 = 9');
      expect(target2Events.length, 1);
      expect(target2Events.first.userExpression, 'x = 3');

      // Purge non-matching events when active problem is '2x + 4 = 10'
      final purged = await queue.purgeStaleEquationEvents('2x + 4 = 10');
      expect(purged, 1);
      expect(queue.pendingCount, 1);
      expect(queue.pendingEvents.first.targetEquation, '2x + 4 = 10');
    });
  });
}
