import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/data/services/offline_sync_queue.dart';
import 'package:personal_learning_engine/data/services/session_restoration_manager.dart';
import 'package:personal_learning_engine/ui/features/root_pedagogy/number_line_balance_canvas.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/views/focus_session_screen.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/socratic_hint_dialog.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Focus Session Micro-Sandbox and Socratic Integration Tests', () {
    late FocusSessionViewModel viewModel;
    late FocusApiService apiService;
    late HapticFeedbackService haptic;

    setUp(() async {
      haptic = HapticFeedbackService();
      haptic.clearHistory();

      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'episode_id': 'mock-ep-1',
            'stream_version': 1,
            'state': {
              'workspace_kc': 'KC-L1',
              'composite_task_id': 'CT-LIN1',
              'current_stage': 'S1_ISOLATE_TERM',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
              'task_context': {
                'composite_task_id': 'CT-LIN1',
                'a': 2,
                'b': 6,
                'c': 14,
                'comparator': '=',
              },
            },
            'event_id': 'evt_1',
            'event_type': 'EPISODE_STARTED',
          }),
          201,
          headers: {'content-type': 'application/json'},
        );
      });

      apiService = FocusApiService(client: mockClient);
      viewModel = FocusSessionViewModel(apiService: apiService, haptic: haptic);
      await viewModel.startEpisode(topicId: 'CT-LIN1', a: 2, b: 6, c: 14);
    });

    testWidgets('Renders Sandbox and Socratic action buttons in header', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: viewModel),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byTooltip('Mikro-Kum Havuzu'), findsOneWidget);
      expect(find.byTooltip('Sokratik İskele'), findsOneWidget);
    });

    testWidgets('Tapping Mikro-Kum Havuzu button opens NumberLineBalanceCanvas bottom sheet', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: viewModel),
        ),
      );
      await tester.pumpAndSettle();

      final sandboxButton = find.byTooltip('Mikro-Kum Havuzu');
      expect(sandboxButton, findsOneWidget);

      await tester.tap(sandboxButton);
      await tester.pumpAndSettle();

      expect(find.byType(NumberLineBalanceCanvas), findsOneWidget);
      expect(find.text('Kök Pedagoji Mikro-Kum Havuzu'), findsOneWidget);
      expect(haptic.triggeredHistory.contains(HapticType.mediumImpact), isTrue);
    });

    testWidgets('Tapping Sokratik İskele button opens SocraticHintDialog bottom sheet', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: viewModel),
        ),
      );
      await tester.pumpAndSettle();

      final socraticButton = find.byTooltip('Sokratik İskele');
      expect(socraticButton, findsOneWidget);

      await tester.tap(socraticButton);
      await tester.pumpAndSettle();

      expect(find.byType(SocraticHintDialog), findsOneWidget);
      expect(haptic.triggeredHistory.contains(HapticType.lightImpact), isTrue);
    });
  });

  group('Focus Session Offline Queue and Restoration Tests', () {
    test('OfflineSyncQueue enqueues and syncs focus attempts idempotently', () {
      final queue = OfflineSyncQueue();
      expect(queue.pendingFocusCount, 0);

      final event = UnsyncedFocusAttemptEvent(
        clientMsgId: 'msg-uuid-001',
        episodeId: 'ep-offline-1',
        expectedSequence: 2,
        rawAttempt: 'x + 3 = 0',
        inputKind: 'equation_rewrite',
        clientTimestamp: DateTime.now(),
      );

      queue.enqueueFocusAttempt(event);
      expect(queue.pendingFocusCount, 1);
      expect(queue.pendingFocusEvents.first.clientMsgId, 'msg-uuid-001');

      // Mark as synced
      queue.markFocusAttemptSynced('msg-uuid-001');
      expect(queue.pendingFocusCount, 0);
    });

    test('SessionRestorationManager saves, restores and clears focus session draft', () async {
      final manager = SessionRestorationManager();
      await manager.clearFocusDraft();
      expect(manager.cachedFocusState, isNull);

      final draft = RestoredFocusSessionState(
        episodeId: 'ep-restore-1',
        topicId: 'CT-LIN1',
        sequence: 3,
        a: 2,
        b: 6,
        c: 14,
        comparator: '=',
        draftText: '2x = 8',
        inputMode: InputMode.touchpad,
        isZenMode: false,
        currentStage: 'S2_ISOLATE_VARIABLE',
        currentPhase: 'WORKSPACE',
        lastUpdated: DateTime.now(),
      );

      await manager.saveFocusDraft(draft);
      expect(manager.cachedFocusState?.episodeId, 'ep-restore-1');

      final restored = await manager.restoreFocusDraft();
      expect(restored, isNotNull);
      expect(restored!.episodeId, 'ep-restore-1');
      expect(restored.topicId, 'CT-LIN1');
      expect(restored.sequence, 3);
      expect(restored.draftText, '2x = 8');
      expect(restored.currentStage, 'S2_ISOLATE_VARIABLE');

      await manager.clearFocusDraft();
      expect(manager.cachedFocusState, isNull);
      final emptyRestored = await manager.restoreFocusDraft();
      expect(emptyRestored, isNull);
    });
  });
}
