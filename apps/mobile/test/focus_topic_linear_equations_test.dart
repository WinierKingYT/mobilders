import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/models/focus_domain_models.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/focus_session_view_model.dart';

void main() {
  group('Focus Pedagogical Topics (CT-LIN1 & CT-INEQ1) Contract Tests', () {
    test('FocusAttemptInputKind maps new linear and inequality wire names', () {
      expect(FocusAttemptInputKind.equationRewrite.wireName, 'EQUATION_REWRITE');
      expect(FocusAttemptInputKind.variableAssignment.wireName, 'VARIABLE_ASSIGNMENT');
      expect(FocusAttemptInputKind.inequalityRewrite.wireName, 'INEQUALITY_REWRITE');
    });

    test('FocusEpisodeState parses taskContext properly', () {
      final json = {
        'workspace_kc': 'KC-L1',
        'composite_task_id': 'CT-LIN1',
        'current_stage': 'S1_ISOLATE_TERM',
        'phase': 'WORKSPACE',
        'probe_budget_remaining': 1,
        'task_context': {
          'a': 2,
          'b': 4,
          'c': 10,
          'expected_intermediate_rhs': 6,
          'expected_root': 3,
        },
      };

      final state = FocusEpisodeState.fromJson(json);
      expect(state.compositeTaskId, 'CT-LIN1');
      expect(state.currentStage, 'S1_ISOLATE_TERM');
      expect(state.taskContext, isNotNull);
      expect(state.taskContext!['a'], 2);
      expect(state.taskContext!['expected_root'], 3);
    });

    test('FocusApiService sends topicId, a, and comparator in startEpisode', () async {
      late Map<String, dynamic> capturedBody;

      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/episodes') && request.method == 'POST') {
          capturedBody = jsonDecode(request.body) as Map<String, dynamic>;
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-lin-mock',
              'stream_version': 1,
              'state': {
                'workspace_kc': 'KC-L1',
                'composite_task_id': 'CT-LIN1',
                'current_stage': 'S1_ISOLATE_TERM',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 1,
                'task_context': capturedBody,
              },
              'event_id': 'ep-lin-mock:1:start',
              'event_type': 'EPISODE_CREATED',
            }),
            201,
          );
        }
        return http.Response('Not Found', 404);
      });

      final service = FocusApiService(
        baseUrl: 'https://api.test/focus/v1',
        client: mockClient,
      );

      final result = await service.startEpisode(
        episodeId: 'ep-lin-mock',
        topicId: 'CT-LIN1',
        a: 3,
        b: 6,
        c: 15,
        idempotencyKey: 'k-start-lin',
      );

      expect(capturedBody['topic_id'], 'CT-LIN1');
      expect(capturedBody['a'], 3);
      expect(capturedBody['b'], 6);
      expect(capturedBody['c'], 15);
      expect(result.state.compositeTaskId, 'CT-LIN1');
    });

    test('FocusSessionViewModel supports CT-LIN1 dynamic LaTeX and stages', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-lin-vm',
            'stream_version': 1,
            'state': {
              'workspace_kc': 'KC-L1',
              'composite_task_id': 'CT-LIN1',
              'current_stage': 'S1_ISOLATE_TERM',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
            },
            'event_id': 'ep-lin-vm:1:start',
            'event_type': 'EPISODE_CREATED',
          }),
          201,
        );
      });

      final service = FocusApiService(
        baseUrl: 'https://api.test/focus/v1',
        client: mockClient,
      );
      final vm = FocusSessionViewModel(apiService: service);

      await vm.startEpisode(
        episodeId: 'ep-lin-vm',
        topicId: 'CT-LIN1',
        a: 2,
        b: 4,
        c: 10,
      );

      expect(vm.topicId, 'CT-LIN1');
      expect(vm.a, 2);
      expect(vm.b, 4);
      expect(vm.c, 10);
      expect(vm.targetEquationLatex, '2 x + 4 = 10');
      expect(vm.currentStage, 'S1_ISOLATE_TERM');
    });

    test('FocusSessionViewModel supports CT-INEQ1 dynamic LaTeX and stages', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-ineq-vm',
            'stream_version': 1,
            'state': {
              'workspace_kc': 'KC-I1',
              'composite_task_id': 'CT-INEQ1',
              'current_stage': 'S1_ISOLATE_TERM',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
            },
            'event_id': 'ep-ineq-vm:1:start',
            'event_type': 'EPISODE_CREATED',
          }),
          201,
        );
      });

      final service = FocusApiService(
        baseUrl: 'https://api.test/focus/v1',
        client: mockClient,
      );
      final vm = FocusSessionViewModel(apiService: service);

      await vm.startEpisode(
        episodeId: 'ep-ineq-vm',
        topicId: 'CT-INEQ1',
        a: -3,
        b: 5,
        c: 14,
        comparator: '<=',
      );

      expect(vm.topicId, 'CT-INEQ1');
      expect(vm.a, -3);
      expect(vm.b, 5);
      expect(vm.c, 14);
      expect(vm.comparator, '<=');
      expect(vm.targetEquationLatex, '-3 x + 5 \\le 14');
      expect(vm.currentStage, 'S1_ISOLATE_TERM');
    });
  });
}
