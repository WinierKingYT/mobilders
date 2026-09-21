import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/misconception_profile_model.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/misconception_profiler_screen.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/interactive_socratic_chat_dialog.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('SessionViewModel Lifecycle & Disposal Tests', () {
    test('SessionViewModel dispose safely cancels timers', () {
      final api = EngineApiService();
      final vm = SessionViewModel(
        apiService: api,
        sessionId: 'test_lifecycle_01',
        targetEquation: '2x + 4 = 10',
      );

      vm.startHesitationTimer(duration: const Duration(seconds: 10));
      expect(() => vm.dispose(), returnsNormally);
    });

    test('SessionViewModel resetSession clears steps and resets target', () {
      final api = EngineApiService();
      final vm = SessionViewModel(
        apiService: api,
        sessionId: 'test_lifecycle_02',
        targetEquation: 'x^2 = 16',
      );

      vm.startNewTarget(newTargetEquation: 'y^2 = 25', newNodeId: 'N_NEW');
      expect(vm.targetEquation, 'y^2 = 25');
      expect(vm.nodeId, 'N_NEW');
      expect(vm.steps.isEmpty, true);

      vm.resetSession();
      expect(vm.steps.isEmpty, true);
      expect(vm.isTargetReached, false);
    });
  });

  group('EngineApiService Resilience Tests', () {
    test('fetchMisconceptionProfile returns safe fallback on connection error', () async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
      final profile = await api.fetchMisconceptionProfile('unreachable_user');

      expect(profile.userId, 'unreachable_user');
      expect(profile.totalRecordedMistakes, 0);
      expect(profile.categories.isNotEmpty, true);
    });

    test('generateTwinQuestion returns safe fallback for unknown bugId', () async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
      final twin = await api.generateTwinQuestion(bugId: 'UNKNOWN_BUG');

      expect(twin.targetedBugId, 'GENERIC');
      expect(twin.targetEquation.isNotEmpty, true);
      expect(twin.canonicalRoots.isNotEmpty, true);
    });
  });

  group('UI Resilience Without Session Context Tests', () {
    testWidgets('MisconceptionProfilerScreen gracefully shows SnackBar when tapped outside SessionViewModel', (tester) async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');
      const profile = MisconceptionProfileResponse(
        userId: 'standalone_user',
        totalRecordedMistakes: 1,
        totalCured: 0,
        overallCureRate: 0.0,
        topRecurringTraps: [
          MisconceptionNode(
            bugId: 'BUG-QUAD-01',
            title: 'Sıfır-Çarpım Kuralı İhlali',
            categoryId: 'KUADRATIK_DENKLEMLER',
            categoryTitle: 'Kuadratik Denklemler',
            cognitiveCause: 'Eşitliğin sağ tarafı sıfırdan farklı.',
            remediationDirective: 'Sağ tarafı sıfır yap.',
            correctPrinciple: 'Sağ taraf sıfır olmalıdır.',
            frequency: 1,
            openCount: 1,
            inRemediationCount: 0,
            curedCount: 0,
            status: 'critical',
            lastOffendingStep: '(x - 2)(x - 3) = 6',
            lastProblem: '(x - 2)(x - 3) = 6',
            avgStabilityDays: 1.0,
          ),
        ],
        categories: [],
      );

      // Render screen WITHOUT SessionViewModel in Provider tree
      await tester.pumpWidget(
        MaterialApp(
          home: MisconceptionProfilerScreen(
            userId: 'standalone_user',
            apiService: api,
            initialProfile: profile,
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap trap card to open bottom sheet
      final card = find.byKey(const Key('trap_card_BUG-QUAD-01'));
      expect(card, findsOneWidget);
      await tester.tap(card);
      await tester.pumpAndSettle();

      // Tap twin practice button
      final twinBtn = find.byKey(const Key('start_twin_practice_button'));
      expect(twinBtn, findsOneWidget);
      await tester.tap(twinBtn);
      await tester.pumpAndSettle();

      // Should show the fallback SnackBar without crashing
      expect(find.textContaining('İkiz soru hazırlandı:'), findsOneWidget);
    });

    testWidgets('InteractiveSocraticChatDialog mounts and unmounts cleanly', (tester) async {
      final api = EngineApiService(baseUrl: 'http://127.0.0.1:54321');

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: InteractiveSocraticChatDialog(
              targetEquation: 'x^2 - 5x + 6 = 0',
              apiService: api,
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.text('Sokratik Öğretmen'), findsOneWidget);

      // Unmount
      await tester.pumpWidget(const MaterialApp(home: SizedBox()));
      await tester.pumpAndSettle();
      // No crashes on dispose
      expect(find.text('Sokratik Öğretmen'), findsNothing);
    });
  });
}
