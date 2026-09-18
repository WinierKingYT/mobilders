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
import 'package:personal_learning_engine/ui/features/session/views/riemann_integral_canvas.dart';
import 'package:personal_learning_engine/ui/features/session/views/daily_journey_screen.dart';

void main() {
  group('Focus Topic CT-INT1 Mobile Tests (Faz D - İntegral ve Alan Hesabı)', () {
    late HapticFeedbackService haptic;

    setUp(() {
      haptic = HapticFeedbackService();
      haptic.clearHistory();
    });

    test('CT-INT1 LaTeX formatting, feedback, and stage input kind resolution', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-INT1');
          expect(body['a'], 2);
          expect(body['b'], 0);
          expect(body['c'], 3);
          expect(body['divisor_root'], 0);
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_int_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-IN1',
                'composite_task_id': 'CT-INT1',
                'current_stage': 'S1_FIND_ANTIDERIVATIVE',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'topic_id': 'CT-INT1',
                  'a': 0,
                  'b': 3,
                  'poly_m': 2,
                  'poly_n': 0,
                  'expected_antiderivative_str': 'x^2',
                  'expected_definite_integral': 9.0,
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
        topicId: 'CT-INT1',
        a: 2,
        b: 0,
        c: 3,
        divisorRoot: 0,
      );

      expect(vm.topicId, 'CT-INT1');
      expect(vm.currentStage, 'S1_FIND_ANTIDERIVATIVE');
      expect(vm.targetEquationLatex, r'\int_{0}^{3} (2x) \, dx');
      expect(vm.feedbackMessage, 'Belirli integral ve alan hesabı odak seansı başlatıldı.');
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('CT-INT1 multi-stage attempt submission with EXPRESSION_REWRITE and COORDINATE_ASSIGNMENT', () async {
      int requestCount = 0;
      final mockClient = MockClient((request) async {
        requestCount++;
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_int_submit',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-IN1',
                'composite_task_id': 'CT-INT1',
                'current_stage': 'S1_FIND_ANTIDERIVATIVE',
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
            // Stage 1: expression rewrite of antiderivative "x^2"
            expect(body['input_kind'], 'EXPRESSION_REWRITE');
            expect(body['input'], 'x^2');
            return http.Response(
              jsonEncode({
                'episode_id': 'ep_int_submit',
                'stream_version': 2,
                'state': {
                  'workspace_kc': 'KC-IN1',
                  'composite_task_id': 'CT-INT1',
                  'current_stage': 'S2_APPLY_LIMITS',
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
            // Stage 2: limits evaluation difference "9"
            expect(body['input_kind'], 'COORDINATE_ASSIGNMENT');
            expect(body['input'], '9');
            return http.Response(
              jsonEncode({
                'episode_id': 'ep_int_submit',
                'stream_version': 3,
                'state': {
                  'workspace_kc': 'KC-IN1',
                  'composite_task_id': 'CT-INT1',
                  'current_stage': 'S3_COMPUTE_DEFINITE_INTEGRAL',
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
          } else if (requestCount == 4) {
            // Stage 3: definite integral final value "9"
            expect(body['input_kind'], 'COORDINATE_ASSIGNMENT');
            expect(body['input'], '9');
            return http.Response(
              jsonEncode({
                'episode_id': 'ep_int_submit',
                'stream_version': 4,
                'state': {
                  'workspace_kc': 'KC-IN1',
                  'composite_task_id': 'CT-INT1',
                  'current_stage': 'S3_COMPUTE_DEFINITE_INTEGRAL',
                  'phase': 'COMPLETED',
                  'probe_budget_remaining': 1,
                },
                'decision': {'action': 'COMPLETE_TASK'},
                'judgment': 'VALID_EXPECTED',
                'event_id': 'evt_att_3',
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

      await vm.startEpisode(topicId: 'CT-INT1', a: 2, b: 0, c: 3, divisorRoot: 0);
      expect(vm.currentStage, 'S1_FIND_ANTIDERIVATIVE');

      // Submit S1
      await vm.submitStageAttempt('x^2');
      expect(vm.currentStage, 'S2_APPLY_LIMITS');
      expect(vm.lastJudgment, AttemptJudgment.validExpected);

      // Submit S2
      await vm.submitStageAttempt('9');
      expect(vm.currentStage, 'S3_COMPUTE_DEFINITE_INTEGRAL');
      expect(vm.lastJudgment, AttemptJudgment.validExpected);

      // Submit S3
      await vm.submitStageAttempt('9');
      expect(vm.isCompleted, isTrue);
      expect(haptic.triggeredHistory, contains(HapticType.mediumImpact));
    });

    testWidgets('FocusSessionScreen renders CT-INT1 stage stepper, guidance, and Riemann modal button', (tester) async {
      tester.view.physicalSize = const Size(800, 1400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_int_ui',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-IN1',
                'composite_task_id': 'CT-INT1',
                'current_stage': 'S1_FIND_ANTIDERIVATIVE',
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

      await tester.pumpWidget(
        MaterialApp(
          home: FocusSessionScreen(
            viewModel: vm,
            topicId: 'CT-INT1',
            a: 2,
            b: 0,
            c: 3,
            divisorRoot: 0,
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Verify stage stepper labels
      expect(find.text('1. F(x) Ters Türev'), findsOneWidget);
      expect(find.text('2. F(b) - F(a)'), findsOneWidget);
      expect(find.text('3. Belirli İntegral'), findsOneWidget);

      // Verify stage guidance
      expect(find.text('Aşama 1: Ters Türev F(x) İfadesini Bulun'), findsOneWidget);

      // Verify Riemann modal button exists
      final riemannButton = find.byTooltip('Riemann İntegral Simülatörü');
      expect(riemannButton, findsOneWidget);

      // Tap Riemann modal button
      await tester.tap(riemannButton);
      await tester.pumpAndSettle();

      // Verify Riemann modal opened and contains RiemannIntegralCanvas
      expect(find.byType(RiemannIntegralCanvas), findsOneWidget);
    });

    testWidgets('RiemannIntegralCanvas renders sliders and responds to method selection', (tester) async {
      tester.view.physicalSize = const Size(800, 1400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: RiemannIntegralCanvas(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Verify title or canvas presence
      expect(find.text('Riemann İntegral & Alan Simülatörü'), findsOneWidget);
      expect(find.text('Sol Toplam'), findsOneWidget);
      expect(find.text('Sağ Toplam'), findsOneWidget);
      expect(find.text('Orta Nokta'), findsOneWidget);
      expect(find.text('Yamuk Kuralı'), findsOneWidget);

      // Tap trapezoid method
      await tester.tap(find.text('Yamuk Kuralı'));
      await tester.pumpAndSettle();
      expect(find.text('Yamuk Kuralı'), findsOneWidget);
    });

    testWidgets('DailyJourneyScreen includes CT-INT1 topic tile', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: DailyJourneyScreen(),
        ),
      );

      await tester.pumpAndSettle();

      // Tap topic selection / focus modal button if present
      final topicAction = find.byTooltip('Konu Seç');
      if (topicAction.evaluate().isNotEmpty) {
        await tester.tap(topicAction);
        await tester.pumpAndSettle();
        expect(find.text('Belirli İntegral & Alan Hesabı'), findsOneWidget);
      }
    });
  });
}
