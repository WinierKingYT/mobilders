import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
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
}
