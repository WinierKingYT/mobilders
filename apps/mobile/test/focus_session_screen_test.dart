import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/views/focus_session_screen.dart';

void main() {
  group('FocusSessionScreen Widget Tests', () {
    testWidgets('Renders header, stage stepper, target equation card, and input dock', (tester) async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-screen-1',
            'stream_version': 1,
            'state': {
              'composite_task_id': 'CT-QF1',
              'current_stage': 'S1_FACTOR',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
            },
            'event_id': 'evt-1',
            'event_type': 'EPISODE_CREATED',
          }),
          201,
        );
      });

      final service = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: service);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: vm),
        ),
      );
      await tester.pumpAndSettle();

      // Verify Header
      expect(find.text('FOCUS KERNEL (CT-QF1)'), findsOneWidget);
      expect(find.text('Seq #1'), findsOneWidget);

      // Verify Stepper
      expect(find.text('1. Çarpan'), findsOneWidget);
      expect(find.text('2. Dal'), findsOneWidget);
      expect(find.text('3. Çözüm'), findsOneWidget);
      expect(find.text('4. Küme'), findsOneWidget);

      // Verify Target Card
      expect(find.text('HEDEF FORMÜL (CT-QF1)'), findsOneWidget);
      expect(find.text('ÇALIŞMA ALANI'), findsOneWidget);

      // Verify Stage 1 Guidance
      expect(find.text('Aşama 1: Faktör Çiftini Bulun'), findsOneWidget);
      expect(find.text('Örnek: 2, 3'), findsOneWidget);

      // Verify Input Field
      expect(find.byType(TextField), findsOneWidget);
    });

    testWidgets('Entering attempt and submitting advances UI', (tester) async {
      final mockClient = MockClient((request) async {
        if (request.method == 'POST' && request.url.path == '/focus/v1/episodes') {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-screen-2',
              'stream_version': 1,
              'state': {
                'composite_task_id': 'CT-QF1',
                'current_stage': 'S1_FACTOR',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
              },
              'event_id': 'evt-1',
              'event_type': 'EPISODE_CREATED',
            }),
            201,
          );
        }

        if (request.method == 'POST' && request.url.path.contains('/attempts')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-screen-2',
              'stream_version': 2,
              'state': {
                'composite_task_id': 'CT-QF1',
                'current_stage': 'S2_BRANCH',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
              },
              'event_id': 'evt-2',
              'event_type': 'ATTEMPT_EVALUATED',
              'judgment': 'VALID_EXPECTED',
              'decision': {'action': 'ADVANCE', 'reason': 'Stage 1 complete'},
            }),
            200,
          );
        }

        return http.Response('Not Found', 404);
      });

      final service = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: service);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: vm),
        ),
      );
      await tester.pumpAndSettle();

      // Enter attempt "2, 3"
      await tester.enterText(find.byType(TextField), '2, 3');
      await tester.tap(find.byIcon(Icons.arrow_upward_rounded));
      await tester.pumpAndSettle();

      // Verify Stage 2 Guidance appears
      expect(find.text('Aşama 2: Çarpan Denklemlerine Ayırın'), findsOneWidget);
      expect(find.text('Örnek: x+2=0 or x+3=0'), findsOneWidget);
      expect(find.text('Seq #2'), findsOneWidget);
    });

    testWidgets('Probing phase displays diagnostic probe card and choice buttons', (tester) async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-probe',
            'stream_version': 2,
            'state': {
              'composite_task_id': 'CT-QF1',
              'current_stage': 'S1_FACTOR',
              'phase': 'PROBING',
              'probe_budget_remaining': 0,
            },
            'event_id': 'evt-probe',
            'event_type': 'ATTEMPT_EVALUATED',
            'judgment': 'INVALID_MATHEMATICS',
            'decision': {
              'action': 'PROBE',
              'reason': 'Sign probe needed',
              'probe_id': 'PR-F2-01',
            },
          }),
          201,
        );
      });

      final service = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: service);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: vm),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Sokratik Teşhis Probu (PR-F2-01)'), findsOneWidget);
      expect(find.text('TEŞHİS PROBU'), findsOneWidget);
      expect(find.text('Hem çarpımı hem toplamı birlikte sağlarım'), findsOneWidget);
      expect(find.text('Yalnızca çarpımın işaretini tuttururum'), findsOneWidget);
    });

    testWidgets('Completed phase displays completion victory card', (tester) async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-done',
            'stream_version': 5,
            'state': {
              'composite_task_id': 'CT-QF1',
              'current_stage': 'S4_COMPLETE_SOLUTION_SET',
              'phase': 'COMPLETED',
              'probe_budget_remaining': 1,
            },
            'event_id': 'evt-done',
            'event_type': 'EPISODE_COMPLETED',
          }),
          201,
        );
      });

      final service = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: service);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(viewModel: vm),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Odak Seansı Başarıyla Tamamlandı!'), findsOneWidget);
      expect(find.text('TAMAMLANDI'), findsOneWidget);
      expect(find.text('Yeni CT-QF1 Seansı Başlat'), findsOneWidget);
    });
  });
}
