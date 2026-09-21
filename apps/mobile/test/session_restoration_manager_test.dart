import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/domain/models/solution_step.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late InMemorySessionStorageBackend mockStorage;
  late SessionRestorationManager manager;

  setUp(() {
    mockStorage = InMemorySessionStorageBackend();
    manager = SessionRestorationManager(storage: mockStorage);
  });

  group('SessionRestorationManager Tests', () {
    test('RestoredSessionState serializes and deserializes accurately', () {
      final state = RestoredSessionState(
        sessionId: 'sess_101',
        nodeId: 'N15',
        targetEquation: '2x + 4 = 10',
        draftText: '2x = 6',
        inputMode: InputMode.touchpad,
        serializedSteps: [
          {
            'step_number': 1,
            'user_expression': '2x = 6',
            'is_valid': true,
            'is_target_reached': false,
            'error_message': null,
            'canonical_expression': '2x = 6',
            'elapsed_ms': 1200,
          }
        ],
        currentPl: 0.65,
        lastUpdated: DateTime(2026, 9, 15, 10, 0),
      );

      final json = state.toJson();
      final revived = RestoredSessionState.fromJson(json);

      expect(revived.sessionId, 'sess_101');
      expect(revived.nodeId, 'N15');
      expect(revived.targetEquation, '2x + 4 = 10');
      expect(revived.draftText, '2x = 6');
      expect(revived.inputMode, InputMode.touchpad);
      expect(revived.currentPl, 0.65);
      expect(revived.serializedSteps.length, 1);

      final steps = revived.toSolutionSteps();
      expect(steps.length, 1);
      expect(steps.first.userExpression, '2x = 6');
      expect(steps.first.isValid, isTrue);
    });

    test('saveDraft persists state to storage backend and cachedState', () async {
      await manager.saveDraft(
        sessionId: 'sess_auto_1',
        nodeId: 'N15',
        targetEquation: 'x^2 - 4 = 0',
        draftText: 'x^2 = 4',
        inputMode: InputMode.virtualKeyboard,
        steps: [
          const SolutionStep(
            stepNumber: 1,
            userExpression: 'x^2 = 4',
            isValid: true,
            isTargetReached: false,
            elapsedMs: 2500,
          ),
        ],
        currentPl: 0.72,
      );

      expect(manager.cachedState, isNotNull);
      expect(manager.cachedState?.targetEquation, 'x^2 - 4 = 0');
      expect(manager.cachedState?.draftText, 'x^2 = 4');

      final rawPersisted = await mockStorage.read(SessionRestorationManager.defaultDraftKey);
      expect(rawPersisted, isNotNull);
      expect(rawPersisted!.contains('x^2 - 4 = 0'), isTrue);
    });

    test('restoreDraft reads persisted state and recreates session model', () async {
      await manager.saveDraft(
        sessionId: 'sess_recovery_99',
        nodeId: 'N20',
        targetEquation: '3x = 15',
        draftText: 'x = 5',
        inputMode: InputMode.inkingCanvas,
        steps: [],
        currentPl: 0.85,
      );

      // Create new manager instance using same storage
      final newManager = SessionRestorationManager(storage: mockStorage);
      final restored = await newManager.restoreDraft();

      expect(restored, isNotNull);
      expect(restored!.sessionId, 'sess_recovery_99');
      expect(restored.nodeId, 'N20');
      expect(restored.targetEquation, '3x = 15');
      expect(restored.draftText, 'x = 5');
      expect(restored.inputMode, InputMode.inkingCanvas);
      expect(restored.currentPl, 0.85);
    });

    test('Expired draft returns null and clears storage', () async {
      await mockStorage.write(
        SessionRestorationManager.defaultDraftKey,
        '{"sessionId":"sess_old","nodeId":"N1","targetEquation":"x = 1","draftText":"","inputMode":"touchpad","serializedSteps":[],"currentPl":0.1,"lastUpdated":"2020-01-01T00:00:00.000"}',
      );

      final restored = await manager.restoreDraft(maxAge: const Duration(hours: 24));
      expect(restored, isNull);

      final postCheck = await mockStorage.read(SessionRestorationManager.defaultDraftKey);
      expect(postCheck, isNull);
    });

    test('Corrupt storage payload handles gracefully and clears', () async {
      await mockStorage.write(
        SessionRestorationManager.defaultDraftKey,
        '{ corrupted_broken_json: !! }',
      );

      final restored = await manager.restoreDraft();
      expect(restored, isNull);

      final cleared = await mockStorage.read(SessionRestorationManager.defaultDraftKey);
      expect(cleared, isNull);
    });

    test('clearDraft empties cachedState and storage', () async {
      await manager.saveDraft(
        sessionId: 'sess_to_clear',
        nodeId: 'N1',
        targetEquation: 'x = 2',
        draftText: '',
        inputMode: InputMode.touchpad,
        steps: [],
        currentPl: 0.5,
      );

      expect(manager.cachedState, isNotNull);
      await manager.clearDraft();

      expect(manager.cachedState, isNull);
      final raw = await mockStorage.read(SessionRestorationManager.defaultDraftKey);
      expect(raw, isNull);
    });
  });
}
