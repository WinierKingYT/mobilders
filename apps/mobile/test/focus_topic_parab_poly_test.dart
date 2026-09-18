import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/data/models/focus_domain_models.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';

void main() {
  group('Focus Topic CT-PAR1 and CT-POLY1 Mobile Tests', () {
    late HapticFeedbackService haptic;

    setUp(() {
      haptic = HapticFeedbackService();
      haptic.clearHistory();
    });

    test('CT-PAR1 LaTeX formatting and input kind mapping for all stages', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-PAR1');
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_parab_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-P1',
                'composite_task_id': 'CT-PAR1',
                'current_stage': 'S1_CALCULATE_R',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'composite_task_id': 'CT-PAR1',
                  'a': 1,
                  'b': -4,
                  'c': 3,
                  'expected_r': 2.0,
                  'expected_k': -1.0,
                  'is_minimum': true,
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
        topicId: 'CT-PAR1',
        a: 1,
        b: -4,
        c: 3,
      );

      expect(vm.topicId, 'CT-PAR1');
      expect(vm.currentStage, 'S1_CALCULATE_R');
      expect(vm.targetEquationLatex, 'f(x) =  x^2 - 4 x + 3');
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('CT-POLY1 LaTeX formatting and divisorRoot serialization', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['topic_id'], 'CT-POLY1');
          expect(body['divisor_root'], 2);
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_poly_test',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-PL1',
                'composite_task_id': 'CT-POLY1',
                'current_stage': 'S1_ROOT_OF_DIVISOR',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': {
                  'composite_task_id': 'CT-POLY1',
                  'a': 1,
                  'b': 2,
                  'c': -3,
                  'divisor_root': 2,
                  'expected_remainder': 5,
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
        topicId: 'CT-POLY1',
        a: 1,
        b: 2,
        c: -3,
        divisorRoot: 2,
      );

      expect(vm.topicId, 'CT-POLY1');
      expect(vm.divisorRoot, 2);
      expect(vm.currentStage, 'S1_ROOT_OF_DIVISOR');
      expect(vm.targetEquationLatex, contains(r'\div (x - 2)'));
      expect(haptic.triggeredHistory, contains(HapticType.selectionClick));
    });

    test('CT-PAR1 stage step submission triggers success haptic on valid response', () async {
      int step = 0;
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_parab_step',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-P1',
                'composite_task_id': 'CT-PAR1',
                'current_stage': 'S1_CALCULATE_R',
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
          step++;
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_parab_step',
              'stream_version': step + 1,
              'state': {
                'workspace_kc': 'KC-P1',
                'composite_task_id': 'CT-PAR1',
                'current_stage': 'S2_CALCULATE_K',
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

      await vm.startEpisode(topicId: 'CT-PAR1', a: 1, b: -4, c: 3);
      haptic.clearHistory();

      await vm.submitStageAttempt('r = 2');

      expect(vm.currentStage, 'S2_CALCULATE_K');
      expect(haptic.triggeredHistory, contains(HapticType.mediumImpact));
    });

    test('CT-PAR1 invalid step triggers error haptic and records observations', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes')) {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_parab_err',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-P1',
                'composite_task_id': 'CT-PAR1',
                'current_stage': 'S1_CALCULATE_R',
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
          return http.Response(
            jsonEncode({
              'episode_id': 'ep_parab_err',
              'stream_version': 2,
              'state': {
                'workspace_kc': 'KC-P1',
                'composite_task_id': 'CT-PAR1',
                'current_stage': 'S1_CALCULATE_R',
                'phase': 'PROBING',
                'probe_budget_remaining': 0,
                'last_judgment': 'INVALID_MATHEMATICS',
                'last_observations': ['EO-VERTEX-FORMULA-SIGN-INVERTED'],
              },
              'event_id': 'evt_2',
              'event_type': 'ATTEMPT_HANDLED',
              'judgment': 'INVALID_MATHEMATICS',
              'observations': ['EO-VERTEX-FORMULA-SIGN-INVERTED'],
              'decision': {
                'action': 'REQUEST_PROBE',
                'reason': 'Formula sign inverted',
                'probe_id': 'PR-P1-01',
              },
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: apiService);

      await vm.startEpisode(topicId: 'CT-PAR1', a: 1, b: -4, c: 3);
      haptic.clearHistory();

      await vm.submitStageAttempt('r = -2');

      expect(vm.isProbing, isTrue);
      expect(vm.lastObservations, contains('EO-VERTEX-FORMULA-SIGN-INVERTED'));
      expect(haptic.triggeredHistory, contains(HapticType.heavyImpact));
    });

    test('FocusAttemptInputKind wireName mapping includes coordinateAssignment and classification', () {
      expect(FocusAttemptInputKind.coordinateAssignment.wireName, 'COORDINATE_ASSIGNMENT');
      expect(FocusAttemptInputKind.classification.wireName, 'CLASSIFICATION');
    });
  });
}
