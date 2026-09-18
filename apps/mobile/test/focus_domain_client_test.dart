import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/models/focus_domain_models.dart';
import 'package:personal_learning_engine/data/services/focus_api_service.dart';

void main() {
  group('Focus Domain Mobile Models & Service Tests', () {
    test('Enums deserialize correctly', () {
      expect(AttemptJudgment.fromString('VALID_EXPECTED'), AttemptJudgment.validExpected);
      expect(AttemptJudgment.fromString('VALID_INCOMPLETE'), AttemptJudgment.validIncomplete);
      expect(AttemptJudgment.fromString('VALID_SHORTCUT'), AttemptJudgment.validShortcut);
      expect(AttemptJudgment.fromString('INVALID_MATHEMATICS'), AttemptJudgment.invalidMathematics);
      expect(AttemptJudgment.fromString('UNKNOWN_FORM'), AttemptJudgment.unsupportedStepForm);

      expect(NextActionType.fromString('ADVANCE'), NextActionType.advance);
      expect(NextActionType.fromString('START_REPAIR'), NextActionType.startRepair);
      expect(NextActionType.fromString('PROBE'), NextActionType.probe);

      expect(PrerequisiteChainHealth.fromString('HEALTHY'), PrerequisiteChainHealth.healthy);
      expect(PrerequisiteChainHealth.fromString('BLOCKED'), PrerequisiteChainHealth.blocked);
    });

    test('startEpisode sends Idempotency-Key and parses FocusCommandResult', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/focus/v1/episodes');
        expect(request.headers['Idempotency-Key'], 'start:key:1');
        expect(request.headers['Content-Type'], 'application/json');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['episode_id'], 'ep-101');
        expect(body['b'], 5);
        expect(body['c'], 6);

        return http.Response(
          jsonEncode({
            'episode_id': 'ep-101',
            'stream_version': 1,
            'state': {
              'composite_task_id': 'CT-QF1',
              'current_stage': 'S1_FACTOR',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
            },
            'event_id': 'ep-101:1:start:key:1',
            'event_type': 'EPISODE_CREATED',
          }),
          201,
        );
      });

      final service = FocusApiService(client: mockClient);
      final res = await service.startEpisode(
        episodeId: 'ep-101',
        b: 5,
        c: 6,
        idempotencyKey: 'start:key:1',
      );

      expect(res.episodeId, 'ep-101');
      expect(res.streamVersion, 1);
      expect(res.state.currentStage, 'S1_FACTOR');
      expect(res.state.phase, 'WORKSPACE');
    });

    test('submitAttempt sends X-Focus-Expected-Sequence and Idempotency-Key', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/focus/v1/episodes/ep-101/attempts');
        expect(request.headers['Idempotency-Key'], 'att:key:1');
        expect(request.headers['X-Focus-Expected-Sequence'], '1');

        return http.Response(
          jsonEncode({
            'episode_id': 'ep-101',
            'stream_version': 2,
            'state': {
              'composite_task_id': 'CT-QF1',
              'current_stage': 'S2_BRANCH',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
            },
            'event_id': 'ep-101:2:att:key:1',
            'event_type': 'ATTEMPT_HANDLED',
            'judgment': 'VALID_EXPECTED',
            'decision': {
              'action': 'ADVANCE',
              'reason': 'Expected supported work is mathematically valid.',
            },
          }),
          200,
        );
      });

      final service = FocusApiService(client: mockClient);
      final res = await service.submitAttempt(
        episodeId: 'ep-101',
        inputKind: FocusAttemptInputKind.factorPair,
        rawInput: [2, 3],
        idempotencyKey: 'att:key:1',
        expectedPreviousSequence: 1,
      );

      expect(res.streamVersion, 2);
      expect(res.judgment, AttemptJudgment.validExpected);
      expect(res.decision?.action, NextActionType.advance);
    });

    test('getEpisode retrieves FocusEpisodeView', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/focus/v1/episodes/ep-101');
        return http.Response(
          jsonEncode({
            'episode_id': 'ep-101',
            'stream_version': 2,
            'state': {
              'composite_task_id': 'CT-QF1',
              'current_stage': 'S2_BRANCH',
              'phase': 'WORKSPACE',
              'probe_budget_remaining': 1,
            },
          }),
          200,
        );
      });

      final service = FocusApiService(client: mockClient);
      final view = await service.getEpisode('ep-101');
      expect(view.episodeId, 'ep-101');
      expect(view.streamVersion, 2);
      expect(view.state.currentStage, 'S2_BRANCH');
    });

    test('submitRepairWork and submitTransferWork send headers correctly', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.contains('/repair/work')) {
          expect(request.headers['Idempotency-Key'], 'repair:work:k');
          expect(request.headers['X-Focus-Expected-Sequence'], '3');
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-101',
              'stream_version': 4,
              'state': {
                'composite_task_id': 'CT-QF1',
                'current_stage': 'S1_FACTOR',
                'phase': 'AWAITING_TRANSFER',
                'probe_budget_remaining': 0,
              },
              'event_id': 'ep-101:4:repair:work:k',
              'event_type': 'REPAIR_ACTION_SUCCEEDED',
              'repair_evaluation_success': true,
              'repair_evaluation_feedback': 'Intervention completed successfully.',
            }),
            200,
          );
        } else if (request.url.path.contains('/repair/transfer')) {
          expect(request.headers['Idempotency-Key'], 'transfer:k');
          expect(request.headers['X-Focus-Expected-Sequence'], '4');
          return http.Response(
            jsonEncode({
              'episode_id': 'ep-101',
              'stream_version': 5,
              'state': {
                'composite_task_id': 'CT-QF1',
                'current_stage': 'S1_FACTOR',
                'phase': 'WORKSPACE',
                'probe_budget_remaining': 0,
              },
              'event_id': 'ep-101:5:transfer:k',
              'event_type': 'TRANSFER_RECORDED',
              'repair_evaluation_success': true,
              'repair_evaluation_feedback': 'Transfer succeeded.',
            }),
            200,
          );
        }
        return http.Response('Not Found', 404);
      });

      final service = FocusApiService(client: mockClient);
      final rWork = await service.submitRepairWork(
        episodeId: 'ep-101',
        rawWork: '6',
        idempotencyKey: 'repair:work:k',
        expectedPreviousSequence: 3,
      );
      expect(rWork.repairEvaluationSuccess, isTrue);

      final rTransfer = await service.submitTransferWork(
        episodeId: 'ep-101',
        rawWork: 'valid',
        idempotencyKey: 'transfer:k',
        expectedPreviousSequence: 4,
      );
      expect(rTransfer.repairEvaluationSuccess, isTrue);
    });

    test('getLearnerProfile and getReEntryDiagnostic deserialize profiles', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/profile')) {
          return http.Response(
            jsonEncode({
              'kc_states': {'KC-F1': 'DURABLE_EVIDENCE', 'KC-F2': 'CONFIRMED_GAP'},
              'barrier_states': {'CTB-01': 'CONFIRMED'},
              'retest_due': ['KC-N1'],
              'active_gaps': ['KC-F2'],
            }),
            200,
          );
        } else if (request.url.path.contains('/diagnostics/re-entry/KC-F2')) {
          return http.Response(
            jsonEncode({
              'target_kc': 'KC-F2',
              'chain_health': 'BLOCKED',
              'blocking_dependencies': ['KC-F1'],
              'at_risk_dependencies': [],
              'recommended_action': 'REPAIR_PREREQUISITE',
              'intervention_kc': 'KC-F1',
              'rationale': 'Prerequisite KC-F1 has unresolved gap.',
            }),
            200,
          );
        }
        return http.Response('Not Found', 404);
      });

      final service = FocusApiService(client: mockClient);
      final profile = await service.getLearnerProfile();
      expect(profile.kcStates['KC-F1'], 'DURABLE_EVIDENCE');
      expect(profile.activeGaps, contains('KC-F2'));

      final diag = await service.getReEntryDiagnostic('KC-F2');
      expect(diag.targetKc, 'KC-F2');
      expect(diag.chainHealth, PrerequisiteChainHealth.blocked);
      expect(diag.blockingDependencies, contains('KC-F1'));
    });

    test('HTTP 409 maps to FocusConflictException', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'detail': {
              'code': 'FOCUS_STREAM_CONFLICT',
              'message': 'Stale Focus stream version',
            }
          }),
          409,
        );
      });

      final service = FocusApiService(client: mockClient);
      expect(
        () => service.submitAttempt(
          episodeId: 'ep-1',
          inputKind: FocusAttemptInputKind.factorPair,
          rawInput: [1, 2],
          idempotencyKey: 'k',
          expectedPreviousSequence: 1,
        ),
        throwsA(isA<FocusConflictException>()),
      );
    });

    test('HTTP 429 maps to FocusRateLimitException', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'detail': {
              'code': 'FOCUS_RATE_LIMIT_EXCEEDED',
              'message': 'Rate limit of 60 requests/minute exceeded',
            }
          }),
          429,
        );
      });

      final service = FocusApiService(client: mockClient);
      expect(
        () => service.getEpisode('ep-1'),
        throwsA(isA<FocusRateLimitException>()),
      );
    });

    test('HTTP 503 maps to FocusDisabledException', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'detail': {
              'code': 'FOCUS_DISABLED',
              'message': 'Focus feature is currently disabled',
            }
          }),
          503,
        );
      });

      final service = FocusApiService(client: mockClient);
      expect(
        () => service.getEpisode('ep-1'),
        throwsA(isA<FocusDisabledException>()),
      );
    });
  });
}
