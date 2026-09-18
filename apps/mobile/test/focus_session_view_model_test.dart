import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/models/focus_domain_models.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';

void main() {
  group('FocusSessionViewModel Unit Tests', () {
    test('startEpisode initializes episode state and sequence', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/focus/v1/episodes');
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-vm-1',
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

      expect(vm.episodeId, isNull);
      expect(vm.currentSequence, 0);

      await vm.startEpisode(episodeId: 'ep-vm-1', b: 5, c: 6);

      expect(vm.episodeId, 'ep-vm-1');
      expect(vm.currentSequence, 1);
      expect(vm.currentStage, 'S1_FACTOR');
      expect(vm.currentPhase, 'WORKSPACE');
      expect(vm.isCompleted, isFalse);
      expect(vm.feedbackMessage, isNotNull);
      expect(vm.errorMessage, isNull);
    });

    test('submitStageAttempt S1 advances to S2 on VALID_EXPECTED', () async {
      final mockClient = MockClient((request) async {
        if (request.method == 'POST' && request.url.path == '/focus/v1/episodes') {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-vm-2',
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

        if (request.method == 'POST' && request.url.path == '/focus/v1/episodes/ep-vm-2/attempts') {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['input_kind'], 'FACTOR_PAIR');
          expect(body['input'], '2, 3');

          return http.Response(
            jsonEncode({
              'episode_id': 'ep-vm-2',
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

      await vm.startEpisode(episodeId: 'ep-vm-2');
      expect(vm.currentStage, 'S1_FACTOR');

      await vm.submitStageAttempt('2, 3');

      expect(vm.currentSequence, 2);
      expect(vm.currentStage, 'S2_BRANCH');
      expect(vm.lastJudgment, AttemptJudgment.validExpected);
      expect(vm.lastDecision?.action, NextActionType.advance);
    });

    test('submitStageAttempt triggers PROBING phase and submitProbeOption answers probe', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path == '/focus/v1/episodes') {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-vm-3',
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

        if (request.url.path == '/focus/v1/episodes/ep-vm-3/attempts') {
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-vm-3',
              'stream_version': 2,
              'state': {
                'composite_task_id': 'CT-QF1',
                'current_stage': 'S1_FACTOR',
                'phase': 'PROBING',
                'probe_budget_remaining': 0,
              },
              'event_id': 'evt-2',
              'event_type': 'ATTEMPT_EVALUATED',
              'judgment': 'INVALID_MATHEMATICS',
              'decision': {
                'action': 'PROBE',
                'reason': 'Diagnostic probe needed',
                'probe_id': 'PR-F2-01',
              },
            }),
            200,
          );
        }

        if (request.url.path == '/focus/v1/episodes/ep-vm-3/probe-responses') {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['response_code'], 'PRODUCT_ONLY');

          return http.Response(
            jsonEncode({
              'episode_id': 'ep-vm-3',
              'stream_version': 3,
              'state': {
                'composite_task_id': 'CT-QF1',
                'current_stage': 'S1_FACTOR',
                'phase': 'PROBING',
                'probe_budget_remaining': 0,
              },
              'event_id': 'evt-3',
              'event_type': 'PROBE_RESPONSE_RECORDED',
              'decision': {
                'action': 'START_REPAIR',
                'reason': 'Confirmed sign confusion gap',
                'intervention_id': 'IT-F2-01',
              },
            }),
            200,
          );
        }

        return http.Response('Not Found', 404);
      });

      final service = FocusApiService(client: mockClient);
      final vm = FocusSessionViewModel(apiService: service);

      await vm.startEpisode(episodeId: 'ep-vm-3');
      await vm.submitStageAttempt('1, 6'); // Misconception

      expect(vm.isProbing, isTrue);
      expect(vm.currentPhase, 'PROBING');

      await vm.submitProbeOption('PRODUCT_ONLY');

      expect(vm.currentSequence, 3);
      expect(vm.lastDecision?.action, NextActionType.startRepair);
    });

    test('handles HTTP 409 conflict and HTTP 503 disabled gracefully', () async {
      final mockConflictClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'detail': {'message': 'Sequence 1 expected, got 0', 'code': 'FOCUS_STREAM_CONFLICT'}
          }),
          409,
        );
      });

      final service = FocusApiService(client: mockConflictClient);
      final vm = FocusSessionViewModel(apiService: service);

      await vm.startEpisode(episodeId: 'ep-err');

      expect(vm.errorMessage, contains('Sequence 1 expected'));
      expect(vm.isSubmitting, isFalse);

      final mockDisabledClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'detail': {'message': 'Focus engine is disabled', 'code': 'FOCUS_DISABLED'}
          }),
          503,
        );
      });

      final disabledService = FocusApiService(client: mockDisabledClient);
      final disabledVm = FocusSessionViewModel(apiService: disabledService);

      await disabledVm.startEpisode(episodeId: 'ep-dis');

      expect(disabledVm.errorMessage, contains('Focus engine is disabled'));
    });
  });
}
