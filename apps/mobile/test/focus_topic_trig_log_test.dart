import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/data/models/focus_domain_models.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/views/focus_session_screen.dart';
import 'package:personal_learning_engine/ui/features/session/views/unit_circle_canvas.dart';

void main() {
  group('Focus Topic CT-TRIG1 and CT-LOG1 Mobile Tests', () {
    late HapticFeedbackService haptic;

    setUp(() {
      haptic = HapticFeedbackService();
      haptic.clearHistory();
    });

    test('CT-TRIG1 LaTeX formatting and input kind mapping for all stages', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-TRIG1');
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_trig_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-TR1',
                'composite_task_id': 'CT-TRIG1',
                'current_stage': 'S1_ISOLATE_TRIG_VALUE',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'composite_task_id': 'CT-TRIG1',
                  'a': 2,
                  'c': 1,
                  'expected_ratio': 0.5,
                  'expected_principal_deg': 30,
                  'expected_secondary_deg': 150,
                },
              },
              'event_id': 'evt_1',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);

      await vm.startEpisode(
        topicId: 'CT-TRIG1',
        a: 2,
        b: 0,
        c: 1,
      );

      expect(vm.topicId, 'CT-TRIG1');
      expect(vm.currentStage, 'S1_ISOLATE_TRIG_VALUE');
      expect(vm.targetEquationLatex, r'2\sin(x) - 1 = 0');
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('CT-LOG1 LaTeX formatting and parameter handling', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-LOG1');
          expect(body['a'], 2);
          expect(body['b'], 3);
          expect(body['c'], 3);
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_log_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-LG1',
                'composite_task_id': 'CT-LOG1',
                'current_stage': 'S1_EXPONENTIAL_CONVERSION',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'composite_task_id': 'CT-LOG1',
                  'base': 2,
                  'c': 3,
                  'k': 3,
                  'expected_power': 8,
                  'expected_x': 11,
                  'is_domain_valid': true,
                },
              },
              'event_id': 'evt_1',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);

      await vm.startEpisode(
        topicId: 'CT-LOG1',
        a: 2,
        b: 3,
        c: 3,
      );

      expect(vm.topicId, 'CT-LOG1');
      expect(vm.currentStage, 'S1_EXPONENTIAL_CONVERSION');
      expect(vm.targetEquationLatex, r'\log_{2}(x - 3) = 3');
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('CT-TRIG1 step submission forwards ARITHMETIC_RESULT for S1', () async {
      String? capturedInputKind;
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_trig_s1',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-TR1',
                'composite_task_id': 'CT-TRIG1',
                'current_stage': 'S1_ISOLATE_TRIG_VALUE',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
              },
              'event_id': 'evt_1',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        }
        if (request.url.path.endsWith('/attempts')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          capturedInputKind = body['input_kind'];
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_trig_s1',
              'stream_version': 2,
              'state': {
                'workspace_kc': 'KC-TR1',
                'composite_task_id': 'CT-TRIG1',
                'current_stage': 'S2_DETERMINE_PRINCIPAL_ANGLE',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'last_judgment': 'VALID_EXPECTED',
              },
              'event_id': 'evt_2',
              'event_type': 'ATTEMPT_HANDLED',
              'judgment': 'VALID_EXPECTED',
              'observations': [],
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);

      await vm.startEpisode(topicId: 'CT-TRIG1', a: 2, b: 0, c: 1);
      await vm.submitStageAttempt('0.5');

      expect(capturedInputKind, 'ARITHMETIC_RESULT');
      expect(vm.currentStage, 'S2_DETERMINE_PRINCIPAL_ANGLE');
      expect(haptic.triggeredHistory, contains(HapticType.mediumImpact));
    });

    test('CT-LOG1 step submission forwards CLASSIFICATION for S3', () async {
      String? capturedInputKind;
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_log_s3',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-LG1',
                'composite_task_id': 'CT-LOG1',
                'current_stage': 'S3_VERIFY_DOMAIN_CONSTRAINT',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
              },
              'event_id': 'evt_1',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        }
        if (request.url.path.endsWith('/attempts')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          capturedInputKind = body['input_kind'];
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_log_s3',
              'stream_version': 2,
              'state': {
                'workspace_kc': 'KC-LG1',
                'composite_task_id': 'CT-LOG1',
                'current_stage': 'S3_VERIFY_DOMAIN_CONSTRAINT',
                'phase': 'COMPLETED',
                'probe_budget_remaining': 1,
                'last_judgment': 'VALID_EXPECTED',
              },
              'event_id': 'evt_2',
              'event_type': 'ATTEMPT_HANDLED',
              'judgment': 'VALID_EXPECTED',
              'observations': [],
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);

      await vm.startEpisode(topicId: 'CT-LOG1', a: 2, b: 3, c: 3);
      await vm.submitStageAttempt('gecerli');

      expect(capturedInputKind, 'CLASSIFICATION');
      expect(vm.isCompleted, isTrue);
    });

    test('FocusAttemptInputKind wireName includes ARITHMETIC_RESULT', () {
      expect(FocusAttemptInputKind.arithmeticResult.wireName, 'ARITHMETIC_RESULT');
    });

    testWidgets('FocusSessionScreen renders UnitCircleCanvas button for CT-TRIG1 and opens modal', (tester) async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_trig_ui',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-TR1',
                'composite_task_id': 'CT-TRIG1',
                'current_stage': 'S1_ISOLATE_TRIG_VALUE',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'composite_task_id': 'CT-TRIG1',
                  'a': 2,
                  'c': 1,
                  'expected_ratio': 0.5,
                  'expected_principal_deg': 30,
                  'expected_secondary_deg': 150,
                },
              },
              'event_id': 'evt_1',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);
      await vm.startEpisode(topicId: 'CT-TRIG1', a: 2, b: 0, c: 1);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(
            viewModel: vm,
            topicId: 'CT-TRIG1',
            a: 2,
            b: 0,
            c: 1,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify stage stepper labels
      expect(find.text('1. Oran'), findsOneWidget);
      expect(find.text('2. Esas Açı'), findsOneWidget);
      expect(find.text('3. İkincil Kök'), findsOneWidget);

      // Verify Birim Çember button exists in header
      final circleBtn = find.byTooltip('Birim Çember');
      expect(circleBtn, findsOneWidget);

      // Tap Birim Çember button and verify UnitCircleCanvas opens
      await tester.tap(circleBtn);
      await tester.pumpAndSettle();

      expect(find.byType(UnitCircleCanvas), findsOneWidget);
    });

    testWidgets('FocusSessionScreen renders CT-LOG1 stage stepper properly', (tester) async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_log_ui',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-LG1',
                'composite_task_id': 'CT-LOG1',
                'current_stage': 'S1_EXPONENTIAL_CONVERSION',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
              },
              'event_id': 'evt_1',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);
      await vm.startEpisode(topicId: 'CT-LOG1', a: 2, b: 3, c: 3);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(
            viewModel: vm,
            topicId: 'CT-LOG1',
            a: 2,
            b: 3,
            c: 3,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify stage stepper labels for LOG1
      expect(find.text('1. Üstel Biçim'), findsOneWidget);
      expect(find.text('2. Değişken x'), findsOneWidget);
      expect(find.text('3. Tanım Kümesi'), findsOneWidget);

      // Ensure Birim Çember button is not present for LOG1
      expect(find.byTooltip('Birim Çember'), findsNothing);
    });
  });
}
