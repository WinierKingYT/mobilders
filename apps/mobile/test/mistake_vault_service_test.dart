import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/mistake_vault_service.dart';

void main() {
  late Directory tempDir;
  late File tempFile;
  late MistakeVaultService service;

  setUp(() async {
    tempDir = await Directory.systemTemp.createTemp('mistake_vault_test_');
    tempFile = File('${tempDir.path}/mistake_vault.json');
    service = MistakeVaultService(storageFilePath: tempFile.path);
    service.clearMistakes();
    await service.saveToDisk();
  });

  tearDown(() async {
    service.clearMistakes();
    await service.saveToDisk();
    await Future.delayed(const Duration(milliseconds: 30));
    try {
      if (await tempFile.exists()) {
        await tempFile.delete();
      }
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    } catch (_) {}
  });

  group('MistakeVaultService Unit & Persistence Tests', () {
    test('Initial service is empty', () {
      expect(service.isEmpty, isTrue);
      expect(service.count, equals(0));
      expect(service.mistakes, isEmpty);
    });

    test('recordMistake adds item and prevents duplicate active mistakes', () async {
      service.recordMistake(
        bugId: 'BUG-QUAD-01',
        nodeId: 'N10',
        problem: 'x^2 = 4',
        offendingStep: 'x = 2',
        correctPrinciple: 'x = \\pm 2',
      );

      expect(service.count, equals(1));
      expect(service.isEmpty, isFalse);
      expect(service.mistakes.first.bugId, equals('BUG-QUAD-01'));
      expect(service.mistakes.first.status, equals('open'));

      // Attempt duplicate insertion of active mistake
      service.recordMistake(
        bugId: 'BUG-QUAD-01',
        nodeId: 'N10',
        problem: 'x^2 = 4',
        offendingStep: 'x = 2',
        correctPrinciple: 'x = \\pm 2',
      );

      // Count remains 1
      expect(service.count, equals(1));
    });

    test('updateMistakeStatus updates status and multiplies stability on cure', () async {
      service.recordMistake(
        bugId: 'BUG-EUC-01',
        nodeId: 'N20',
        problem: 'Triangle problem',
        offendingStep: 'a + b < c',
        correctPrinciple: 'a + b > c',
        initialStabilityDays: 1.0,
      );

      final item = service.mistakes.first;
      service.updateMistakeStatus(item.id, 'in_remediation');
      expect(service.mistakes.first.status, equals('in_remediation'));
      expect(service.mistakes.first.stabilityDays, equals(1.0));

      service.updateMistakeStatus(item.id, 'cured');
      expect(service.mistakes.first.status, equals('cured'));
      expect(service.mistakes.first.stabilityDays, equals(2.5));
      expect(service.mistakes.first.isDue, isFalse);
    });

    test('persists mistakes to disk and reloads across instances', () async {
      service.recordMistake(
        bugId: 'BUG-TRIG-01',
        nodeId: 'N30',
        problem: 'sin(x)^2 + cos(x)^2',
        offendingStep: '= 2',
        correctPrinciple: '= 1',
      );
      await service.saveToDisk();

      // Verify file was written
      expect(await tempFile.exists(), isTrue);
      final rawJson = await tempFile.readAsString();
      final decoded = jsonDecode(rawJson) as List;
      expect(decoded.length, equals(1));
      expect(decoded.first['bug_id'], equals('BUG-TRIG-01'));

      // Clear memory without deleting file
      service.clearMistakes(persist: false);
      expect(service.count, equals(0));

      // Reload from disk file
      await service.load();
      expect(service.count, equals(1));
      expect(service.mistakes.first.bugId, equals('BUG-TRIG-01'));
    });

    test('syncWithApi reconciles remote mistakes into local list', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.contains('/api/v1/vault/list/student_1')) {
          return http.Response(
            jsonEncode([
              {
                'mistake_id': 'm_remote_1',
                'node_id': 'N40',
                'bug_id': 'BUG-CALC-01',
                'problem_statement': 'Derivative of sin(x)',
                'offending_step': 'cos(x)',
                'correct_principle': 'cos(x)',
                'status': 'open',
                'dsr_state': {'stability': 1.5},
              }
            ]),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final apiService = EngineApiService(client: mockClient);
      await service.syncWithApi(apiService, 'student_1');

      expect(service.count, equals(1));
      expect(service.mistakes.first.bugId, equals('BUG-CALC-01'));
      expect(service.mistakes.first.stabilityDays, equals(1.5));
    });
  });
}
