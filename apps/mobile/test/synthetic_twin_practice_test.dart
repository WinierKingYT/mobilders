import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/misconception_profile_model.dart';
import 'package:personal_learning_engine/domain/models/twin_question_model.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/misconception_profiler_screen.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('TwinQuestionModel Serialization Tests', () {
    test('roundtrip fromJson and toJson matches data', () {
      final json = {
        'twin_id': 'TWIN-BUG-QUAD-01-001',
        'target_equation': '(x - 2)(x + 4) = 7',
        'canonical_roots': [3.0, -5.0],
        'targeted_bug_id': 'BUG-QUAD-01',
        'targeted_bug_title': 'Sıfır-Çarpım Kuralı İhlali',
        'pedagogical_focus': 'Zero-product property remediation',
        'hint': 'Sağ taraf sıfır olmalıdır.',
        'difficulty_level': 2,
      };

      final model = TwinQuestionModel.fromJson(json);
      expect(model.twinId, 'TWIN-BUG-QUAD-01-001');
      expect(model.targetedBugId, 'BUG-QUAD-01');
      expect(model.targetEquation, '(x - 2)(x + 4) = 7');
      expect(model.canonicalRoots, [3.0, -5.0]);
      expect(model.difficultyLevel, 2);
      expect(model.hint, 'Sağ taraf sıfır olmalıdır.');

      final serialized = model.toJson();
      expect(serialized['twin_id'], 'TWIN-BUG-QUAD-01-001');
      expect(serialized['targeted_bug_id'], 'BUG-QUAD-01');
      expect(serialized['target_equation'], '(x - 2)(x + 4) = 7');
      expect(serialized['canonical_roots'], [3.0, -5.0]);
    });
  });

  group('EngineApiService Twin Fallback Tests', () {
    test('generateTwinQuestion returns fallback for BUG-QUAD-01 when offline', () async {
      final apiService = EngineApiService(baseUrl: 'http://127.0.0.1:9999'); // non-existent server
      final twin = await apiService.generateTwinQuestion(bugId: 'BUG-QUAD-01');

      expect(twin.targetedBugId, 'BUG-QUAD-01');
      expect(twin.targetEquation, '(x - 3)(x + 2) = 6');
      expect(twin.canonicalRoots.isNotEmpty, true);
    });

    test('generateTwinQuestion returns fallback for BUG-QUAD-02 when offline', () async {
      final apiService = EngineApiService(baseUrl: 'http://127.0.0.1:9999');
      final twin = await apiService.generateTwinQuestion(bugId: 'BUG-QUAD-02');

      expect(twin.targetedBugId, 'BUG-QUAD-02');
      expect(twin.targetEquation, 'x² = 49');
      expect(twin.canonicalRoots, [7.0, -7.0]);
    });
  });

  group('SessionViewModel startNewTarget Tests', () {
    test('startNewTarget resets target equation and clears steps', () {
      final apiService = EngineApiService();
      final vm = SessionViewModel(
        apiService: apiService,
        sessionId: 'session-twin-01',
        targetEquation: 'x^2 - 5x + 6 = 0',
      );

      expect(vm.targetEquation, 'x^2 - 5x + 6 = 0');

      vm.startNewTarget(
        newTargetEquation: '(x - 4)(x + 1) = 6',
        newNodeId: 'TWIN-BUG-QUAD-01',
      );

      expect(vm.targetEquation, '(x - 4)(x + 1) = 6');
      expect(vm.nodeId, 'TWIN-BUG-QUAD-01');
      expect(vm.steps.isEmpty, true);
      expect(vm.isTargetReached, false);
      expect(vm.isSubmitting, false);
    });
  });

  group('MisconceptionProfilerScreen Twin Practice Integration Tests', () {
    MisconceptionProfileResponse createMockProfile() {
      return const MisconceptionProfileResponse(
        userId: 'student_twin_01',
        totalRecordedMistakes: 1,
        totalCured: 0,
        overallCureRate: 0.0,
        topRecurringTraps: [
          MisconceptionNode(
            bugId: 'BUG-QUAD-01',
            title: 'Sıfır-Çarpım Kuralı İhlali',
            categoryId: 'KUADRATIK_DENKLEMLER',
            categoryTitle: 'Kuadratik Denklemler',
            cognitiveCause: 'Eşitliğin sağ tarafı sıfırdan farklı iken çarpanları doğrudan sayıya eşitleme.',
            remediationDirective: 'Denklemi önce ax^2 + bx + c = 0 formuna getir.',
            correctPrinciple: 'Eşitliğin sağ tarafı sıfır olmalıdır.',
            frequency: 2,
            openCount: 2,
            inRemediationCount: 0,
            curedCount: 0,
            status: 'critical',
            lastOffendingStep: '(x - 2)(x - 3) = 6',
            lastProblem: '(x - 2)(x - 3) = 6',
            avgStabilityDays: 0.5,
          ),
        ],
        categories: [
          MisconceptionCategory(
            categoryId: 'KUADRATIK_DENKLEMLER',
            categoryTitle: 'Kuadratik Denklemler',
            totalMistakes: 1,
            activeMistakes: 1,
            curedMistakes: 0,
            nodes: [
              MisconceptionNode(
                bugId: 'BUG-QUAD-01',
                title: 'Sıfır-Çarpım Kuralı İhlali',
                categoryId: 'KUADRATIK_DENKLEMLER',
                categoryTitle: 'Kuadratik Denklemler',
                cognitiveCause: 'Eşitliğin sağ tarafı sıfırdan farklı iken çarpanları doğrudan sayıya eşitleme.',
                remediationDirective: 'Denklemi önce ax^2 + bx + c = 0 formuna getir.',
                correctPrinciple: 'Eşitliğin sağ tarafı sıfır olmalıdır.',
                frequency: 2,
                openCount: 2,
                inRemediationCount: 0,
                curedCount: 0,
                status: 'critical',
                lastOffendingStep: '(x - 2)(x - 3) = 6',
                lastProblem: '(x - 2)(x - 3) = 6',
                avgStabilityDays: 0.5,
              ),
            ],
          ),
        ],
      );
    }

    testWidgets('tapping start_twin_practice_button generates twin and calls startNewTarget', (tester) async {
      final apiService = EngineApiService(baseUrl: 'http://127.0.0.1:9999');
      final sessionVm = SessionViewModel(
        apiService: apiService,
        sessionId: 'test-session-twin',
        targetEquation: 'initial = 0',
      );

      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider<SessionViewModel>.value(value: sessionVm),
          ],
          child: MaterialApp(
            home: MisconceptionProfilerScreen(
              userId: 'student_twin_01',
              apiService: apiService,
              initialProfile: createMockProfile(),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Tap on the recurring trap card to open bottom sheet
      final cardFinder = find.byKey(const Key('trap_card_BUG-QUAD-01'));
      expect(cardFinder, findsOneWidget);
      await tester.tap(cardFinder);
      await tester.pumpAndSettle();

      // Verify the twin practice button exists
      final twinButtonFinder = find.byKey(const Key('start_twin_practice_button'));
      expect(twinButtonFinder, findsOneWidget);
      expect(find.text('🎯 İkiz Soru Üret & Alıştırmaya Başla'), findsOneWidget);

      // Tap twin practice button
      await tester.tap(twinButtonFinder);
      await tester.pumpAndSettle();

      // Verify sessionVm updated to the twin equation
      expect(sessionVm.targetEquation, '(x - 3)(x + 2) = 6');
      expect(sessionVm.nodeId, 'TWIN-BUG-QUAD-01');
    });
  });
}
