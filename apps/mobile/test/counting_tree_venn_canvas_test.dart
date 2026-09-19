import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/ui/features/session/views/counting_tree_venn_canvas.dart';

void main() {
  testWidgets('CountingTreeVennCanvas renders Venn diagram mode with chips and formula',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: CountingTreeVennCanvas(
              initialMode: ProbabilityCanvasMode.venn,
              probA: 0.6,
              probB: 0.5,
              probIntersection: 0.3,
            ),
          ),
        ),
      ),
    );

    // 1. Verify segmented buttons
    expect(find.text("Venn Şeması"), findsOneWidget);
    expect(find.text("Ağaç Diyagramı"), findsOneWidget);
    expect(find.text("Monte Carlo"), findsOneWidget);

    // 2. Verify Venn chips
    expect(find.byKey(const Key('chip_intersection')), findsOneWidget);
    expect(find.byKey(const Key('chip_union')), findsOneWidget);
    expect(find.byKey(const Key('chip_only_a')), findsOneWidget);

    // 3. Verify calculated formula values: P(A ∪ B) = 0.6 + 0.5 - 0.3 = 0.80
    expect(find.textContaining("0.80"), findsOneWidget);
    // Conditional: P(A|B) = 0.3 / 0.5 = 0.60
    expect(find.textContaining("0.60"), findsOneWidget);

    // 4. Tap Union Chip
    await tester.tap(find.byKey(const Key('chip_union')));
    await tester.pumpAndSettle();
  });

  testWidgets('CountingTreeVennCanvas switches to Tree Diagram mode',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: CountingTreeVennCanvas(),
          ),
        ),
      ),
    );

    // Switch to Tree Mode
    await tester.tap(find.text("Ağaç Diyagramı"));
    await tester.pumpAndSettle();

    // Verify tree diagram content
    expect(find.textContaining("Çarpma Kuralı"), findsOneWidget);
  });

  testWidgets('CountingTreeVennCanvas executes Monte Carlo simulation',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: CountingTreeVennCanvas(),
          ),
        ),
      ),
    );

    // Switch to Monte Carlo Mode
    await tester.tap(find.text("Monte Carlo"));
    await tester.pumpAndSettle();

    // Verify initial state
    expect(find.text("Teorik P(Tura)"), findsOneWidget);
    expect(find.byKey(const Key('btn_run_monte_carlo')), findsOneWidget);

    // Tap Run Simulation
    await tester.tap(find.byKey(const Key('btn_run_monte_carlo')));
    await tester.pumpAndSettle();

    // Verify simulation output
    expect(find.textContaining("Fark (Sapma)"), findsOneWidget);
  });

  group('EngineApiService - Probability & Monte Carlo API Client Tests', () {
    test('solveProbabilityOrCombinatorics sends payload and parses response', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/probability/solve');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['problem_type'], 'combination');
        expect(body['params']['n'], 5);
        expect(body['params']['r'], 3);
        expect(body['student_id'], 'STU-001');

        final responseJson = {
          'problem_type': 'combination',
          'result_data': {'value': 10, 'formula': 'C(5,3) = 10'},
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
      final result = await api.solveProbabilityOrCombinatorics(
        problemType: 'combination',
        params: {'n': 5, 'r': 3},
        studentId: 'STU-001',
      );

      expect(result['problem_type'], 'combination');
      expect(result['result_data']['value'], 10);
      expect(result['vault_recorded'], false);
    });

    test('simulateMonteCarlo sends payload and parses convergence data', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/v1/probability/monte-carlo');
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['experiment_type'], 'coin_flip');
        expect(body['num_trials'], 50000);

        final responseJson = {
          'experiment_type': 'coin_flip',
          'num_trials': 50000,
          'empirical_probability': 0.5012,
          'theoretical_probability': 0.5,
          'error': 0.0012,
          'confidence_interval_95': [0.4968, 0.5056],
        };
        return http.Response(
          jsonEncode(responseJson),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final result = await api.simulateMonteCarlo(
        experimentType: 'coin_flip',
        params: {'p_success': 0.5},
        numTrials: 50000,
      );

      expect(result['experiment_type'], 'coin_flip');
      expect(result['num_trials'], 50000);
      expect(result['empirical_probability'], 0.5012);
      expect(result['theoretical_probability'], 0.5);
      expect(result['confidence_interval_95'], hasLength(2));
    });

    test('solveProbabilityOrCombinatorics throws HttpException on non-200', () async {
      final mockClient = MockClient((request) async {
        return http.Response('Internal Server Error', 500);
      });

      final api = EngineApiService(client: mockClient);
      expect(
        () => api.solveProbabilityOrCombinatorics(
          problemType: 'linear_permutation',
          params: {'n': -1},
        ),
        throwsA(isA<HttpException>()),
      );
    });
  });
}
