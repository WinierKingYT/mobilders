import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';

void main() {
  group('EngineApiService Unit Tests', () {
    test('baseUrl removes trailing slashes', () {
      final service1 = EngineApiService(baseUrl: 'http://127.0.0.1:8000/');
      expect(service1.baseUrl, 'http://127.0.0.1:8000');

      final service2 = EngineApiService(baseUrl: 'http://127.0.0.1:8000///');
      expect(service2.baseUrl, 'http://127.0.0.1:8000');

      final service3 = EngineApiService(baseUrl: 'http://127.0.0.1:8000');
      expect(service3.baseUrl, 'http://127.0.0.1:8000');

      service1.dispose();
      service2.dispose();
      service3.dispose();
    });

    test('getNextCatItem handles empty, null, and incomplete bodies safely without throwing', () async {
      // 1. Mock client returning 'null'
      final clientNull = MockClient((request) async {
        return http.Response('null', 200);
      });
      final serviceNull = EngineApiService(client: clientNull);
      final itemNull = await serviceNull.getNextCatItem(
        sessionId: 'test',
        currentTheta: 0.0,
        administeredItemIds: [],
      );
      expect(itemNull, isNull);
      serviceNull.dispose();

      // 2. Mock client returning empty body ''
      final clientEmpty = MockClient((request) async {
        return http.Response('', 200);
      });
      final serviceEmpty = EngineApiService(client: clientEmpty);
      final itemEmpty = await serviceEmpty.getNextCatItem(
        sessionId: 'test',
        currentTheta: 0.0,
        administeredItemIds: [],
      );
      expect(itemEmpty, isNull);
      serviceEmpty.dispose();

      // 3. Mock client returning empty json '{}' without item_id
      final clientEmptyJson = MockClient((request) async {
        return http.Response('{}', 200);
      });
      final serviceEmptyJson = EngineApiService(client: clientEmptyJson);
      final itemEmptyJson = await serviceEmptyJson.getNextCatItem(
        sessionId: 'test',
        currentTheta: 0.0,
        administeredItemIds: [],
      );
      expect(itemEmptyJson, isNull);
      serviceEmptyJson.dispose();

      // 4. Mock client returning valid item
      final clientValid = MockClient((request) async {
        final payload = {
          'item_id': 'CAT-01',
          'target_node_id': 'N12',
          'prompt': 'Solve x^2 = 4',
          'difficulty_b': 0.0,
          'discrimination_a': 2.0,
        };
        return http.Response(jsonEncode(payload), 200);
      });
      final serviceValid = EngineApiService(client: clientValid);
      final itemValid = await serviceValid.getNextCatItem(
        sessionId: 'test',
        currentTheta: 0.0,
        administeredItemIds: [],
      );
      expect(itemValid, isNotNull);
      expect(itemValid!.itemId, 'CAT-01');
      serviceValid.dispose();
    });

    test('dispose closes client cleanly and idempotently', () {
      final service = EngineApiService();
      expect(() => service.dispose(), returnsNormally);
    });
  });
}
