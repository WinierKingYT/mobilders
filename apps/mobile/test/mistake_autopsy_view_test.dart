import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/data/services/mistake_vault_service.dart';
import 'package:personal_learning_engine/ui/features/vault/mistake_autopsy_view.dart';

void main() {
  final testMistakes = [
    const MistakeAutopsyItem(
      id: "m1",
      bugId: "BUG-EUC-04",
      nodeId: "N165",
      problem: "Öklid Bağıntısı Sorusu",
      offendingStep: "h^2 = b * c",
      correctPrinciple: "h^2 = p * k",
      status: "open",
      stabilityDays: 0.4,
      isDue: true,
    ),
    const MistakeAutopsyItem(
      id: "m2",
      bugId: "BUG-QUAD-01",
      nodeId: "N30",
      problem: "Kuadratik Soru",
      offendingStep: "x(x+2)=3 => x=3",
      correctPrinciple: "ax^2+bx+c=0 formuna getir",
      status: "in_remediation",
      stabilityDays: 1.2,
      isDue: true,
    ),
    const MistakeAutopsyItem(
      id: "m3",
      bugId: "BUG-FOUND-09",
      nodeId: "N01",
      problem: "Üs Taban Çarpımı",
      offendingStep: "2^3 = 6",
      correctPrinciple: "2^3 = 2*2*2 = 8",
      status: "open",
      stabilityDays: 0.2,
      isDue: true,
    ),
    const MistakeAutopsyItem(
      id: "m4",
      bugId: "BUG-TRIG-01",
      nodeId: "N51",
      problem: "Trigonometri Sorusu",
      offendingStep: "sin(2x)=2sin(x)",
      correctPrinciple: "sin(2x)=2sin(x)cos(x)",
      status: "cured",
      stabilityDays: 5.4,
      isDue: false,
    ),
  ];

  testWidgets('MistakeAutopsyView renders stats bar, filter chips, and mistake items',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: MistakeAutopsyView(
          mistakes: testMistakes,
        ),
      ),
    );

    // 1. Verify view and header
    expect(find.byKey(const Key('mistake_vault_view')), findsOneWidget);
    expect(find.text("Bilişsel Hata Otopsisi Kasası"), findsOneWidget);

    // 2. Verify Stats
    expect(find.text("Toplam Hata"), findsOneWidget);
    expect(find.text("4"), findsOneWidget); // total = 4
    expect(find.text("Kür Edildi"), findsWidgets);

    // 3. Verify Boss battle banner (since 3 mistakes are due: m1, m2, m3)
    expect(find.byKey(const Key('boss_battle_banner')), findsOneWidget);
    expect(find.text("KAVRAM CANAVARI UYANDI!"), findsOneWidget);

    // 4. Verify items rendered
    expect(find.text("BUG-EUC-04"), findsOneWidget);
    expect(find.text("BUG-QUAD-01"), findsOneWidget);
  });

  testWidgets('MistakeAutopsyView filters mistakes properly',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: MistakeAutopsyView(
          mistakes: testMistakes,
        ),
      ),
    );

    // Filter by "Kür Edildi"
    await tester.tap(find.byKey(const Key('filter_cured')));
    await tester.pumpAndSettle();

    // Only BUG-TRIG-01 is cured
    expect(find.text("BUG-TRIG-01"), findsOneWidget);
    expect(find.text("BUG-EUC-04"), findsNothing);

    // Filter by "Telafide"
    await tester.tap(find.byKey(const Key('filter_remediation')));
    await tester.pumpAndSettle();

    expect(find.text("BUG-QUAD-01"), findsOneWidget);
    expect(find.text("BUG-TRIG-01"), findsNothing);
  });

  testWidgets('MistakeAutopsyView steps through 3-stage self-correction flow',
      (WidgetTester tester) async {
    bool completed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: MistakeAutopsyView(
          mistakes: testMistakes,
          onSelfCorrectionCompleted: (item) {
            completed = true;
          },
        ),
      ),
    );

    // Click "Hatayı Düzelt" on m1
    final btnCorrect = find.byKey(const Key('btn_start_self_correction_m1'));
    expect(btnCorrect, findsOneWidget);
    await tester.tap(btnCorrect);
    await tester.pumpAndSettle();

    // Stage 1: Hatanı Teşhis Et
    expect(find.byKey(const Key('stage_1_view')), findsOneWidget);
    await tester.tap(find.byKey(const Key('btn_stage_1_confirm')));
    await tester.pumpAndSettle();

    // Stage 2: Doğru İlkeyi İfade Et
    expect(find.byKey(const Key('stage_2_view')), findsOneWidget);
    await tester.tap(find.byKey(const Key('btn_stage_2_confirm')));
    await tester.pumpAndSettle();

    // Stage 3: Yeniden Temiz Çöz
    expect(find.byKey(const Key('stage_3_view')), findsOneWidget);
    await tester.tap(find.byKey(const Key('btn_stage_3_complete')));
    await tester.pumpAndSettle();

    expect(completed, isTrue);
    expect(find.byKey(const Key('self_correction_flow')), findsNothing);
  });

  group('EngineApiService Vault & Boss Battle API Client Tests', () {
    test('fetchVaultMistakes calls correct endpoint and parses list', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, equals('GET'));
        expect(request.url.path, equals('/api/v1/vault/list/user_123'));
        expect(request.url.queryParameters['status'], equals('open'));
        return http.Response(
          jsonEncode([
            {
              'mistake_id': 'm1',
              'user_id': 'user_123',
              'bug_id': 'BUG-EUC-04',
              'status': 'open',
            }
          ]),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final res = await api.fetchVaultMistakes('user_123', status: 'open');
      expect(res.length, equals(1));
      expect(res[0]['bug_id'], equals('BUG-EUC-04'));
    });

    test('fetchDueVaultMistakes and fetchVaultAnalytics call correct endpoints', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path == '/api/v1/vault/due/user_123') {
          return http.Response(
            jsonEncode([
              {'mistake_id': 'm1', 'is_due': true}
            ]),
            200,
            headers: {'content-type': 'application/json'},
          );
        } else if (request.url.path == '/api/v1/vault/analytics/user_123') {
          return http.Response(
            jsonEncode({
              'total_mistakes': 5,
              'cured_count': 2,
              'cure_rate': 0.4,
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final api = EngineApiService(client: mockClient);
      final due = await api.fetchDueVaultMistakes('user_123');
      expect(due.length, equals(1));

      final analytics = await api.fetchVaultAnalytics('user_123');
      expect(analytics['total_mistakes'], equals(5));
      expect(analytics['cure_rate'], equals(0.4));
    });

    test('recordVaultMistake posts mistake payload', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, equals('POST'));
        expect(request.url.path, equals('/api/v1/vault/record'));
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['bug_id'], equals('BUG-ANAG-01'));
        expect(body['node_id'], equals('N143'));
        return http.Response(
          jsonEncode({'mistake_id': 'm_new', 'bug_id': 'BUG-ANAG-01'}),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final res = await api.recordVaultMistake(
        userId: 'u1',
        nodeId: 'N143',
        bugId: 'BUG-ANAG-01',
        problemStatement: 'Problem 1',
        offendingStep: 'Step 1',
        correctPrinciple: 'Principle 1',
        remediationDirective: 'Directive 1',
      );
      expect(res['mistake_id'], equals('m_new'));
    });

    test('Self-correction 3-stage lifecycle API calls', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path == '/api/v1/vault/self-correction/start') {
          return http.Response(jsonEncode({'stage': 1, 'mistake_id': 'm1'}), 200);
        } else if (request.url.path == '/api/v1/vault/self-correction/diagnose') {
          return http.Response(jsonEncode({'stage': 2, 'success': true}), 200);
        } else if (request.url.path == '/api/v1/vault/self-correction/explain') {
          return http.Response(jsonEncode({'stage': 3, 'success': true}), 200);
        } else if (request.url.path == '/api/v1/vault/self-correction/resolve') {
          return http.Response(
              jsonEncode({'stage': 4, 'status': 'cured', 'success': true}), 200);
        }
        return http.Response('Not Found', 404);
      });

      final api = EngineApiService(client: mockClient);
      final start = await api.startSelfCorrection('m1');
      expect(start['stage'], equals(1));

      final diag = await api.submitSelfCorrectionDiagnosis(mistakeId: 'm1', isIdentified: true);
      expect(diag['stage'], equals(2));

      final exp = await api.submitSelfCorrectionExplanation(mistakeId: 'm1', isPrincipleCorrect: true);
      expect(exp['stage'], equals(3));

      final res = await api.submitSelfCorrectionResolve(mistakeId: 'm1', isCorrect: true);
      expect(res['stage'], equals(4));
      expect(res['status'], equals('cured'));
    });

    test('Boss battle spawn and turn submission API calls', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path == '/api/v1/vault/boss-battle/spawn') {
          return http.Response(
            jsonEncode({
              'battle_id': 'b1',
              'boss_name': 'Kavram Canavari',
              'boss_max_hp': 300,
              'boss_current_hp': 300,
            }),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        } else if (request.url.path == '/api/v1/vault/boss-battle/turn') {
          return http.Response(
            jsonEncode({
              'boss_defeated': false,
              'damage_dealt': 100,
              'remaining_hp': 200,
              'combo_streak': 1,
            }),
            200,
          );
        }
        return http.Response('Not Found', 404);
      });

      final api = EngineApiService(client: mockClient);
      final spawn = await api.spawnBossBattle(userId: 'u1');
      expect(spawn['battle_id'], equals('b1'));
      expect(spawn['boss_max_hp'], equals(300));

      final turn = await api.submitBossBattleTurn(battleId: 'b1', isCleanSolve: true);
      expect(turn['damage_dealt'], equals(100));
      expect(turn['remaining_hp'], equals(200));
    });

    testWidgets('MistakeAutopsyView renders honest empty state when zero mistakes exist',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: MistakeAutopsyView(
            mistakes: [],
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Kayıtlı Bilişsel Hata Yok'), findsOneWidget);
      expect(find.textContaining('Harika! Henüz tespit edilen kavram yanılgısı'), findsOneWidget);
    });

    testWidgets('MistakeAutopsyView Stage 3 generates synthetic twin question and triggers practice callback',
        (WidgetTester tester) async {
      String? launchedEquation;
      MistakeAutopsyItem? launchedItem;

      final mockClient = MockClient((request) async {
        if (request.url.path == '/api/v1/twin/generate') {
          return http.Response(
            jsonEncode({
              'twin_id': 'twin_test_01',
              'target_equation': '(x - 3)(x + 2) = 6',
              'canonical_roots': [4.0, -3.0],
              'targeted_bug_id': 'BUG-QUAD-01',
              'targeted_bug_title': 'Sıfır-Çarpım Kuralı İhlali',
              'pedagogical_focus': 'Eşitliğin sağ tarafı sıfırdan farklıdır.',
              'hint': 'Önce parantezleri aç.',
            }),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        }
        return http.Response('Not Found', 404);
      });
      final mockApi = EngineApiService(client: mockClient);

      await tester.pumpWidget(
        MaterialApp(
          home: MistakeAutopsyView(
            mistakes: testMistakes,
            apiService: mockApi,
            onLaunchTwinPractice: (item, eq) async {
              launchedItem = item;
              launchedEquation = eq;
            },
          ),
        ),
      );

      // Open self correction on m2 (BUG-QUAD-01)
      final btnStartM2 = find.byKey(const Key('btn_start_self_correction_m2'));
      await tester.ensureVisible(btnStartM2);
      await tester.pumpAndSettle();
      await tester.tap(btnStartM2);
      await tester.pumpAndSettle();

      // Step through stage 1 and 2
      await tester.tap(find.byKey(const Key('btn_stage_1_confirm')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('btn_stage_2_confirm')));
      await tester.pumpAndSettle();

      // We are at Stage 3
      expect(find.byKey(const Key('stage_3_view')), findsOneWidget);
      expect(find.byKey(const Key('btn_stage_3_launch_twin')), findsOneWidget);
      expect(find.byKey(const Key('stage_3_twin_equation_card')), findsNothing);

      // Tap launch twin button
      await tester.tap(find.byKey(const Key('btn_stage_3_launch_twin')));
      await tester.pumpAndSettle();

      // Twin equation card should now be visible
      expect(find.byKey(const Key('stage_3_twin_equation_card')), findsOneWidget);
      expect(find.textContaining('(x - 3)(x + 2) = 6'), findsOneWidget);
      expect(find.byKey(const Key('btn_stage_3_start_practice')), findsOneWidget);

      // Tap practice button
      final btnPractice = find.byKey(const Key('btn_stage_3_start_practice'));
      await tester.ensureVisible(btnPractice);
      await tester.pumpAndSettle();
      await tester.tap(btnPractice);
      await tester.pumpAndSettle();

      expect(launchedItem?.id, equals('m2'));
      expect(launchedEquation, equals('(x - 3)(x + 2) = 6'));

      // Tap complete
      final btnComplete = find.byKey(const Key('btn_stage_3_complete'));
      await tester.ensureVisible(btnComplete);
      await tester.pumpAndSettle();
      await tester.tap(btnComplete);
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('self_correction_flow')), findsNothing);
    });

    testWidgets('MistakeAutopsyView Stage 3 fallback updates MistakeVaultService status',
        (WidgetTester tester) async {
      MistakeVaultService.instance.clearMistakes(persist: false);
      MistakeVaultService.instance.recordMistake(
        bugId: 'BUG-QUAD-01',
        nodeId: 'N30',
        problem: 'x(x+2)=3',
        offendingStep: 'x=3',
        correctPrinciple: 'ax^2+bx+c=0',
      );

      final item = MistakeVaultService.instance.mistakes.first;
      expect(item.status, equals('open'));

      await tester.pumpWidget(
        MaterialApp(
          home: MistakeAutopsyView(
            mistakes: MistakeVaultService.instance.mistakes,
          ),
        ),
      );

      await tester.tap(find.byKey(Key('btn_start_self_correction_${item.id}')));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('btn_stage_1_confirm')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('btn_stage_2_confirm')));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('btn_stage_3_complete')));
      await tester.pumpAndSettle();

      expect(MistakeVaultService.instance.mistakes.first.status, equals('cured'));
    });
  });
}

