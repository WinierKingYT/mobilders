import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/views/euclidean_canvas.dart';
import 'package:personal_learning_engine/ui/features/session/views/proof_canvas.dart';

void main() {
  testWidgets('ProofCanvas renders Truth Table mode by default and handles chip toggle',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ProofCanvas(
              initialMode: ProofCanvasMode.truthTable,
            ),
          ),
        ),
      ),
    );

    // 1. Verify segmented buttons
    expect(find.text("Doğruluk Tablosu"), findsOneWidget);
    expect(find.text("Teorem İspatı"), findsOneWidget);
    expect(find.text("Tümevarım"), findsOneWidget);

    // 2. Verify Table Columns
    expect(find.text("p"), findsWidgets);
    expect(find.text("q"), findsWidgets);
    expect(find.text("Sonuç"), findsOneWidget);

    // 3. Contingency badge initially (for implies)
    expect(find.byKey(const Key('badge_contingency')), findsOneWidget);

    // 4. Tap De Morgan Chip (Tautology)
    await tester.tap(find.text("De Morgan (∧)"));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('badge_tautology')), findsOneWidget);
  });

  testWidgets('ProofCanvas switches to Theorem Proof mode and verifies step',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ProofCanvas(),
          ),
        ),
      ),
    );

    // Switch to Theorem Proof Mode
    await tester.tap(find.text("Teorem İspatı"));
    await tester.pumpAndSettle();

    // Verify inputs exist
    expect(find.byKey(const Key('input_proof_step')), findsOneWidget);
    expect(find.byKey(const Key('dropdown_proof_rule')), findsOneWidget);
    expect(find.byKey(const Key('btn_verify_proof_step')), findsOneWidget);

    // Enter a valid step
    await tester.enterText(
      find.byKey(const Key('input_proof_step')),
      "Varsayalim ki kok 2 rasyoneldir",
    );
    await tester.tap(find.byKey(const Key('btn_verify_proof_step')));
    await tester.pumpAndSettle();

    // Verify feedback
    expect(find.byKey(const Key('box_step_feedback')), findsOneWidget);
    expect(find.textContaining("geçerlidir"), findsOneWidget);

    // Enter an invalid step with fallacy
    await tester.enterText(
      find.byKey(const Key('input_proof_step')),
      "taban_adimi_gerekmez direkt gecis yapalim",
    );
    await tester.tap(find.byKey(const Key('btn_verify_proof_step')));
    await tester.pumpAndSettle();

    expect(find.textContaining("Yanılgı"), findsOneWidget);
  });

  testWidgets('ProofCanvas switches to Induction mode and runs domino simulation',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ProofCanvas(),
          ),
        ),
      ),
    );

    // Switch to Induction Mode
    await tester.tap(find.text("Tümevarım"));
    await tester.pumpAndSettle();

    // Verify stage chips
    expect(find.text("1. Taban Adımı"), findsOneWidget);
    expect(find.text("2. Hipotez"), findsOneWidget);
    expect(find.text("3. Geçiş Adımı"), findsOneWidget);

    // Tap Domino Simulation
    expect(find.byKey(const Key('btn_simulate_domino')), findsOneWidget);
    await tester.tap(find.byKey(const Key('btn_simulate_domino')));
    await tester.pumpAndSettle();

    // Verify domino chain
    expect(find.byKey(const Key('domino_chain_wrap')), findsOneWidget);
    expect(find.text("P(1) ✓"), findsOneWidget);
    expect(find.text("P(10) ✓"), findsOneWidget);
  });

  group('EngineApiService - Proof & Logic API Client Tests', () {
    test('generateTruthTable sends payload and returns truth table', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/proof/truth-table');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['variables'], ['p', 'q']);
        expect(body['expression_type'], 'implies');

        final responseJson = {
          'variables': ['p', 'q'],
          'row_count': 4,
          'is_tautology': false,
          'is_contradiction': false,
          'is_contingency': true,
        };
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final result = await api.generateTruthTable(variables: ['p', 'q'], expressionType: 'implies');

      expect(result['row_count'], 4);
      expect(result['is_contingency'], true);
    });

    test('fetchProofCatalog returns list of theorems', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/proof/catalog');
        final responseJson = [
          {'id': 'THM-IRR-SQRT2', 'title': '√2 Sayısının İrrasyonelliği'},
          {'id': 'THM-EUCLID-PRIMES', 'title': 'Asal Sayıların Sonsuzluğu'},
        ];
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final catalog = await api.fetchProofCatalog();

      expect(catalog, hasLength(2));
      expect(catalog[0]['id'], 'THM-IRR-SQRT2');
    });

    test('verifyProofStep sends payload and parses validation response', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/proof/verify-step');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['theorem_id'], 'THM-IRR-SQRT2');
        expect(body['step_number'], 1);

        final responseJson = {
          'step_number': 1,
          'is_valid': true,
          'feedback': '1. adım mantıksal olarak geçerlidir.',
          'detected_bug': null,
          'vault_recorded': false,
        };
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final result = await api.verifyProofStep(
        theoremId: 'THM-IRR-SQRT2',
        stepNumber: 1,
        studentStatement: 'Varsayalim ki kok 2 rasyoneldir',
        selectedRule: 'CONTRADICTION_ASSUMPTION',
      );

      expect(result['is_valid'], true);
      expect(result['detected_bug'], isNull);
    });

    test('simulateInduction sends request and parses domino chain', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/proof/induction/simulate');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['claim_type'], 'gauss');
        expect(body['test_range'], 5);

        final responseJson = {
          'start_k': 1,
          'test_range': 5,
          'all_steps_valid': true,
          'domino_chain': List.generate(5, (i) => {'k': i + 1, 'implication_holds': true}),
        };
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final result = await api.simulateInduction(claimType: 'gauss', testRange: 5);

      expect(result['all_steps_valid'], true);
      expect(result['domino_chain'], hasLength(5));
    });
  });

  group('EuclideanCanvas & Proof Logic Sequence Tests (Stage 61)', () {
    testWidgets('EuclideanCanvas magnetic snap-to-vertex engages within 24dp and ignores far touches', (tester) async {
      EuclideanVertex? selectedVertex;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                width: 400,
                child: EuclideanCanvas(
                  initialPreset: EuclideanShapePreset.isosceles,
                  initialShowAuxiliary: true,
                  onVertexSelected: (v) => selectedVertex = v,
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      var gestureFinder = find.byKey(const Key('euclidean_gesture_detector'));
      expect(gestureFinder, findsOneWidget);

      var topLeft = tester.getTopLeft(gestureFinder);
      var size = tester.getSize(gestureFinder);

      // Top vertex A is at: (size.width / 2.0, size.height * 0.18)
      final vertexAPos = Offset(size.width / 2.0, size.height * 0.18);

      // 1. Touch 10dp away from Vertex A (<= 24dp): should snap!
      final nearTouch = topLeft + vertexAPos + const Offset(8, 6); // dist = 10dp <= 24dp
      await tester.tapAt(nearTouch);
      await tester.pumpAndSettle();

      expect(selectedVertex, isNotNull);
      expect(selectedVertex!.id, equals('A'));
      expect(find.byKey(const Key('snapped_vertex_badge')), findsOneWidget);
      expect(find.textContaining("Manyetik Kenetlenme (24dp): A"), findsOneWidget);

      // 2. Touch 100dp away from any vertex (> 24dp): should NOT snap
      topLeft = tester.getTopLeft(gestureFinder);
      final farTouch = topLeft + Offset(size.width * 0.1, size.height * 0.1);
      await tester.tapAt(farTouch);
      await tester.pumpAndSettle();

      expect(selectedVertex, isNull);
      expect(find.byKey(const Key('snapped_vertex_badge')), findsNothing);

      // 3. Switch to Right Triangle and test 90° vertex snap
      await tester.tap(find.byKey(const Key('preset_right')));
      await tester.pumpAndSettle();

      gestureFinder = find.byKey(const Key('euclidean_gesture_detector'));
      topLeft = tester.getTopLeft(gestureFinder);
      size = tester.getSize(gestureFinder);

      // Vertex B is at (size.width * 0.22, size.height * 0.80)
      final vertexBPos = Offset(size.width * 0.22, size.height * 0.80);
      final nearVertexB = topLeft + vertexBPos + const Offset(12, 0); // 12dp <= 24dp
      await tester.tapAt(nearVertexB);
      await tester.pumpAndSettle();

      expect(selectedVertex, isNotNull);
      expect(selectedVertex!.id, equals('B'));
      expect(find.textContaining("90° Dik Açı"), findsOneWidget);
    });

    testWidgets('ProofCanvas enforces strict premise-first sequence and rejects out-of-order conclusions', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: ProofCanvas(
                initialMode: ProofCanvasMode.theoremProof,
                initialTheoremId: 'THM-IRR-SQRT2',
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // 1. Attempt to apply deduction (Modus Tollens) before establishing hypothesis (¬P)
      await tester.tap(find.byKey(const Key('dropdown_proof_rule')));
      await tester.pumpAndSettle();
      await tester.tap(find.text("Modus Tollens (Sonucu Yadsıma)").last);
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('input_proof_step')), 'q çifttir, o halde çelişki');
      await tester.tap(find.byKey(const Key('btn_verify_proof_step')));
      await tester.pumpAndSettle();

      // Order violation rejected!
      expect(find.byKey(const Key('box_step_feedback')), findsOneWidget);
      expect(find.textContaining("Mantıksal Sıralama Hatası"), findsOneWidget);
      expect(find.byKey(const Key('proof_step_chain')), findsNothing);

      // 2. Now submit Step 1 correctly with Contradiction Assumption
      await tester.tap(find.byKey(const Key('dropdown_proof_rule')));
      await tester.pumpAndSettle();
      await tester.tap(find.text("Çelişki İçin Ters Kabul (¬P)").last);
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('input_proof_step')), 'Varsayalım ki √2 = p/q rasyoneldir');
      await tester.tap(find.byKey(const Key('btn_verify_proof_step')));
      await tester.pumpAndSettle();

      // Step 1 accepted!
      expect(find.textContaining("1. adım mantıksal olarak geçerlidir"), findsOneWidget);
      expect(find.byKey(const Key('proof_step_chain')), findsOneWidget);

      // 3. Now attempt out-of-order jump (Induction base step on contradiction proof)
      await tester.tap(find.byKey(const Key('dropdown_proof_rule')));
      await tester.pumpAndSettle();
      await tester.tap(find.text("Tümevarım Taban Adımı").last);
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('input_proof_step')), 'n=1 için taban');
      await tester.tap(find.byKey(const Key('btn_verify_proof_step')));
      await tester.pumpAndSettle();

      expect(find.textContaining("Mantıksal Sıralama Hatası"), findsOneWidget);

      // 4. Submit Step 2 correctly with Modus Ponens (Algebraic deduction)
      await tester.tap(find.byKey(const Key('dropdown_proof_rule')));
      await tester.pumpAndSettle();
      await tester.tap(find.text("Modus Ponens (Öncülü Olumlama)").last);
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('input_proof_step')), '2q² = p² olduğundan p çift sayıdır');
      await tester.tap(find.byKey(const Key('btn_verify_proof_step')));
      await tester.pumpAndSettle();

      expect(find.textContaining("2. adım mantıksal olarak geçerlidir"), findsOneWidget);
      expect(find.textContaining("Doğrulanan İspat Adımları (2)"), findsOneWidget);

      // 5. Test Reset Button clears step chain
      await tester.tap(find.byKey(const Key('btn_reset_proof_steps')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('proof_step_chain')), findsNothing);
    });
  });
}
