import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/ui/features/atlas/living_knowledge_atlas_view.dart';

void main() {
  testWidgets('LivingKnowledgeAtlasView renders stats bar, search, and nodes list',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: LivingKnowledgeAtlasView(),
        ),
      ),
    );

    // 1. Verify Stats Bar
    expect(find.text("Toplam Düğüm"), findsOneWidget);
    expect(find.text("Usta Olunan"), findsOneWidget);
    expect(find.text("ZPD (Hazır)"), findsOneWidget);

    // 2. Verify Search Bar
    expect(find.byKey(const Key('atlas_search_field')), findsOneWidget);

    // 3. Verify Nodes rendered
    expect(find.byKey(const Key('atlas_nodes_list')), findsOneWidget);
    expect(find.text("Sayı Doğrusu ve Yön Sezgisi"), findsOneWidget);
    expect(find.text("Eşitlik ve İki Kefeli Terazi Sezgisi"), findsOneWidget);
  });

  testWidgets('LivingKnowledgeAtlasView filters nodes by search query',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: LivingKnowledgeAtlasView(),
        ),
      ),
    );

    // Enter search text "Türev"
    await tester.enterText(find.byKey(const Key('atlas_search_field')), "Türev");
    await tester.pumpAndSettle();

    // Verify filtered results
    expect(find.text("Türev ve Anlık Hız Sezgisi"), findsOneWidget);
    expect(find.text("Sayı Doğrusu ve Yön Sezgisi"), findsNothing);
  });

  testWidgets('LivingKnowledgeAtlasView opens detail modal sheet on card tap',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: LivingKnowledgeAtlasView(),
        ),
      ),
    );

    // Tap the first node card
    await tester.tap(find.byKey(const Key('node_card_N_ROOT_01')));
    await tester.pumpAndSettle();

    // Verify modal sheet content
    expect(find.byKey(const Key('btn_start_learning_path')), findsOneWidget);
    expect(find.text("Öğrenme Yolunu Başlat"), findsOneWidget);

    // Close modal sheet
    await tester.tap(find.byKey(const Key('btn_start_learning_path')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('btn_start_learning_path')), findsNothing);
  });

  group('EngineApiService - Living Knowledge Atlas API Client Tests', () {
    test('fetchAtlasSummary returns total nodes and domains', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/atlas/summary');
        final responseJson = {
          'total_nodes': 246,
          'domains': {'Temel Kökler & Sezgi': 16, 'Cebir & Polinomlar': 50},
        };
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final result = await api.fetchAtlasSummary();

      expect(result['total_nodes'], 246);
      expect(result['domains']['Temel Kökler & Sezgi'], 16);
    });

    test('fetchAtlasPayload sends mastered_ids and returns nodes and edges', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/atlas/payload');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['mastered_ids'], ['N_ROOT_01']);

        final responseJson = {
          'meta': {'total_nodes': 246, 'mastered_count': 1, 'zpd_count': 3},
          'nodes': [{'id': 'N_ROOT_01', 'title': 'Sayı Doğrusu', 'status': 'MASTERED'}],
          'edges': [{'source': 'N_ROOT_01', 'target': 'N01', 'active': true}],
        };
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final payload = await api.fetchAtlasPayload(masteredIds: ['N_ROOT_01']);

      expect(payload['meta']['total_nodes'], 246);
      expect(payload['nodes'], hasLength(1));
      expect(payload['edges'], hasLength(1));
    });

    test('fetchAtlasBottlenecks returns list of bottlenecks', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/atlas/bottlenecks');
        final responseJson = [
          {'node_id': 'N01', 'title': 'Temel Dört İşlem', 'blocked_dependents_count': 60},
        ];
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final bottlenecks = await api.fetchAtlasBottlenecks(masteredIds: []);

      expect(bottlenecks, hasLength(1));
      expect(bottlenecks[0]['node_id'], 'N01');
    });

    test('fetchAtlasZpd returns list of ready node IDs', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/atlas/zpd');
        final responseJson = ['N_ROOT_01', 'N_ROOT_02'];
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final zpd = await api.fetchAtlasZpd();

      expect(zpd, ['N_ROOT_01', 'N_ROOT_02']);
    });
  });

  group('LivingKnowledgeAtlasView DAG Canvas & RepaintBoundary Tests (Stage 35)', () {
    testWidgets('Toggling to DAG Kanvası renders InteractiveViewer and RepaintBoundary layers',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LivingKnowledgeAtlasView(),
          ),
        ),
      );

      // Verify list view is default with RepaintBoundary on items
      expect(find.byKey(const Key('atlas_nodes_list')), findsOneWidget);
      expect(find.byKey(const Key('repaint_node_N_ROOT_01')), findsOneWidget);

      // Switch to DAG Canvas mode
      await tester.tap(find.text('DAG Kanvası'));
      await tester.pumpAndSettle();

      // Verify DAG InteractiveViewer and isolated RepaintBoundary layers
      expect(find.byKey(const Key('atlas_dag_interactive_viewer')), findsOneWidget);
      expect(find.byKey(const Key('atlas_grid_repaint_boundary')), findsOneWidget);
      expect(find.byKey(const Key('atlas_dag_repaint_boundary')), findsOneWidget);

      // Tapping node in DAG canvas opens detail sheet
      expect(find.byKey(const Key('dag_node_tap_N_ROOT_01')), findsOneWidget);
      await tester.tap(find.byKey(const Key('dag_node_tap_N_ROOT_01')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('btn_start_learning_path')), findsOneWidget);
      await tester.tap(find.byKey(const Key('btn_start_learning_path')));
      await tester.pumpAndSettle();
    });

    test('KnowledgeDagPainter sanitizeCoordinate and sanitizeOffset guard against NaN and Infinity', () {
      expect(KnowledgeDagPainter.sanitizeCoordinate(120.5), equals(120.5));
      expect(KnowledgeDagPainter.sanitizeCoordinate(double.nan), equals(0.0));
      expect(KnowledgeDagPainter.sanitizeCoordinate(double.nan, fallback: 50.0), equals(50.0));
      expect(KnowledgeDagPainter.sanitizeCoordinate(double.infinity), equals(0.0));
      expect(KnowledgeDagPainter.sanitizeCoordinate(double.negativeInfinity, fallback: -1.0), equals(-1.0));

      const validOffset = Offset(100.0, 200.0);
      expect(KnowledgeDagPainter.sanitizeOffset(validOffset), equals(validOffset));

      const nanOffset = Offset(double.nan, 200.0);
      expect(KnowledgeDagPainter.sanitizeOffset(nanOffset), equals(Offset.zero));

      const infOffset = Offset(100.0, double.infinity);
      expect(KnowledgeDagPainter.sanitizeOffset(infOffset, fallback: const Offset(10, 20)), equals(const Offset(10, 20)));
    });
  });
}
