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
import 'package:personal_learning_engine/ui/features/session/views/dynamic_tangent_canvas.dart';

void main() {
  group('Focus Topic CT-LIM1 and CT-DERIV1 Mobile Tests (Faz C - Kalkülüs I)', () {
    late HapticFeedbackService haptic;

    setUp(() {
      haptic = HapticFeedbackService();
      haptic.clearHistory();
    });

    test('CT-LIM1 LaTeX formatting, feedback, and stage input kind resolution', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-LIM1');
          expect(body['a'], 2);
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_lim_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-LM1',
                'composite_task_id': 'CT-LIM1',
                'current_stage': 'S1_EVALUATE_LIMIT_FORM',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'topic_id': 'CT-LIM1',
                  'a': 2,
                  'function_expr': '(x^2 - 4)/(x - 2)',
                  'limit_point': 2,
                  'expected_limit': 4,
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
        topicId: 'CT-LIM1',
        a: 2,
      );

      expect(vm.topicId, 'CT-LIM1');
      expect(vm.currentStage, 'S1_EVALUATE_LIMIT_FORM');
      expect(vm.targetEquationLatex, r'\lim_{x \to 2} \frac{x^2 - 4}{x - 2}');
      expect(vm.feedbackMessage, 'Limit ve 0/0 belirsizliği odak seansı başlatıldı.');
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('CT-DERIV1 LaTeX formatting, parameters, and tangent slope context', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-DERIV1');
          expect(body['a'], 1);
          expect(body['b'], 2);
          expect(body['c'], 1);
          expect(body['x0'], 1);
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_deriv_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-DV1',
                'composite_task_id': 'CT-DERIV1',
                'current_stage': 'S1_COMPUTE_DERIVATIVE',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'topic_id': 'CT-DERIV1',
                  'a': 1,
                  'b': 2,
                  'c': 1,
                  'x0': 1,
                  'expected_deriv': '2*x + 2',
                  'expected_slope': 4,
                  'expected_y0': 4,
                  'expected_tangent_line': 'y = 4*x',
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
        topicId: 'CT-DERIV1',
        a: 1,
        b: 2,
        c: 1,
        x0: 1,
      );

      expect(vm.topicId, 'CT-DERIV1');
      expect(vm.currentStage, 'S1_COMPUTE_DERIVATIVE');
      expect(vm.targetEquationLatex, r'f(x) =  x^2 + 2 x + 1, \quad x_0 = 1');
      expect(vm.feedbackMessage, 'Polinom türevi ve teğet denklemi odak seansı başlatıldı.');
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('FocusAttemptInputKind enum serialization contains EXPRESSION_REWRITE', () {
      expect(FocusAttemptInputKind.expressionRewrite.wireName, 'EXPRESSION_REWRITE');
    });

    test('CT-LIM1 multi-stage attempt submission with EXPRESSION_REWRITE', () async {
      int requestCount = 0;
      final mockClient = MockClient((request) async {
        requestCount++;
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_lim_submit',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-LM1',
                'composite_task_id': 'CT-LIM1',
                'current_stage': 'S1_EVALUATE_LIMIT_FORM',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
              },
              'event_id': 'evt_start',
              'event_type': 'EPISODE_STARTED',
            }),
            201,
            headers: {'content-type': 'application/json'},
          );
        } else if (request.url.path.endsWith('/attempts')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          if (requestCount == 2) {
            // Stage 1: classification of "0/0"
            expect(body['input_kind'], 'CLASSIFICATION');
            expect(body['input'], '0/0');
            return http.Response(
              jsonEncode({
                'episode_id': 'ep_lim_submit',
                'stream_version': 2,
                'state': {
                  'workspace_kc': 'KC-LM1',
                  'composite_task_id': 'CT-LIM1',
                  'current_stage': 'S2_SIMPLIFY_EXPRESSION',
                  'phase': 'WORKSPACE',
                  'probe_budget_remaining': 1,
                },
                'decision': {'action': 'ADVANCE'},
                'judgment': 'VALID_EXPECTED',
                'event_id': 'evt_att_1',
                'event_type': 'ATTEMPT_SUBMITTED',
              }),
              200,
              headers: {'content-type': 'application/json'},
            );
          } else if (requestCount == 3) {
            // Stage 2: expression rewrite of "x + 2"
            expect(body['input_kind'], 'EXPRESSION_REWRITE');
            expect(body['input'], 'x + 2');
            return http.Response(
              jsonEncode({
                'episode_id': 'ep_lim_submit',
                'stream_version': 3,
                'state': {
                  'workspace_kc': 'KC-LM1',
                  'composite_task_id': 'CT-LIM1',
                  'current_stage': 'S3_COMPUTE_FINAL_LIMIT',
                  'phase': 'WORKSPACE',
                  'probe_budget_remaining': 1,
                },
                'decision': {'action': 'ADVANCE'},
                'judgment': 'VALID_EXPECTED',
                'event_id': 'evt_att_2',
                'event_type': 'ATTEMPT_SUBMITTED',
              }),
              200,
              headers: {'content-type': 'application/json'},
            );
          }
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);

      await vm.startEpisode(topicId: 'CT-LIM1', a: 2);
      expect(vm.currentStage, 'S1_EVALUATE_LIMIT_FORM');

      // Submit Stage 1
      await vm.submitStageAttempt('0/0');
      expect(vm.currentStage, 'S2_SIMPLIFY_EXPRESSION');
      expect(vm.lastJudgment, AttemptJudgment.validExpected);

      // Submit Stage 2
      await vm.submitStageAttempt('x + 2');
      expect(vm.currentStage, 'S3_COMPUTE_FINAL_LIMIT');
      expect(vm.lastJudgment, AttemptJudgment.validExpected);
      expect(haptic.triggeredHistory, contains(HapticType.mediumImpact));
    });

    testWidgets('FocusSessionScreen renders CT-LIM1 stage stepper and guidance', (tester) async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_lim_ui',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-LM1',
                'composite_task_id': 'CT-LIM1',
                'current_stage': 'S1_EVALUATE_LIMIT_FORM',
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
      await vm.startEpisode(topicId: 'CT-LIM1', a: 2);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(
            viewModel: vm,
            topicId: 'CT-LIM1',
            a: 2,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify stage stepper labels for CT-LIM1
      expect(find.text('1. Belirsizlik (0/0)'), findsOneWidget);
      expect(find.text('2. Sadeleştirme'), findsOneWidget);
      expect(find.text('3. Limit Değeri'), findsOneWidget);

      // Verify workspace stage guidance
      expect(find.text('Aşama 1: Belirsizlik Tespiti'), findsOneWidget);
      expect(find.textContaining('belirsizlik biçimini tespit edin'), findsOneWidget);
    });

    testWidgets('FocusSessionScreen renders CT-DERIV1 with dynamic tangent simulator modal', (tester) async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_deriv_ui',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-DV1',
                'composite_task_id': 'CT-DERIV1',
                'current_stage': 'S1_COMPUTE_DERIVATIVE',
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
      await vm.startEpisode(topicId: 'CT-DERIV1', a: 1, b: 2, c: 1, x0: 1);

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(
            viewModel: vm,
            topicId: 'CT-DERIV1',
            a: 1,
            b: 2,
            c: 1,
            x0: 1,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify stage stepper labels for CT-DERIV1
      expect(find.text("1. f'(x) Türev"), findsOneWidget);
      expect(find.text("2. m = f'(x0)"), findsOneWidget);
      expect(find.text('3. Teğet Doğrusu'), findsOneWidget);

      // Verify Dynamic Tangent Simulator button in header
      final tangentBtn = find.byTooltip('Dinamik Teğet Simülatörü');
      expect(tangentBtn, findsOneWidget);

      // Tap button and verify modal opens with DynamicTangentCanvas
      await tester.tap(tangentBtn);
      await tester.pumpAndSettle();

      expect(find.byType(DynamicTangentCanvas), findsOneWidget);
      expect(find.text('Dinamik Türev & Teğet Simülatörü'), findsOneWidget);
    });
  });
}
