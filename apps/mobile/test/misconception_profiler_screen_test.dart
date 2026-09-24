import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/domain/models/misconception_profile_model.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/misconception_profiler_screen.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  MisconceptionProfileResponse createMockProfile() {
    return const MisconceptionProfileResponse(
      userId: 'test_user_42',
      totalRecordedMistakes: 3,
      totalCured: 1,
      overallCureRate: 0.333,
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
        MisconceptionNode(
          bugId: 'SIGN_FLIP',
          title: 'Eksi İşareti Dağıtım Yanılgısı',
          categoryId: 'ISARET_VE_DAGILMA',
          categoryTitle: 'İşaret ve Parantez Dağılımı',
          cognitiveCause: 'Parantez önündeki eksi işaretini içteki tüm terimlere dağıtmama.',
          remediationDirective: 'Eksi ile eksinin çarpımı artıdır.',
          correctPrinciple: 'Eksi her iki terime de dağıtılmalıdır.',
          frequency: 1,
          openCount: 0,
          inRemediationCount: 0,
          curedCount: 1,
          status: 'cured',
          lastOffendingStep: '-(2x - 5) = -2x - 5',
          lastProblem: '-(2x - 5) = 3',
          avgStabilityDays: 2.5,
        ),
      ],
      categories: [
        MisconceptionCategory(
          categoryId: 'KUADRATIK_DENKLEMLER',
          categoryTitle: 'Kuadratik Denklemler',
          totalMistakes: 2,
          activeMistakes: 2,
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
        MisconceptionCategory(
          categoryId: 'ISARET_VE_DAGILMA',
          categoryTitle: 'İşaret ve Parantez Dağılımı',
          totalMistakes: 1,
          activeMistakes: 0,
          curedMistakes: 1,
          nodes: [
            MisconceptionNode(
              bugId: 'SIGN_FLIP',
              title: 'Eksi İşareti Dağıtım Yanılgısı',
              categoryId: 'ISARET_VE_DAGILMA',
              categoryTitle: 'İşaret ve Parantez Dağılımı',
              cognitiveCause: 'Parantez önündeki eksi işaretini içteki tüm terimlere dağıtmama.',
              remediationDirective: 'Eksi ile eksinin çarpımı artıdır.',
              correctPrinciple: 'Eksi her iki terime de dağıtılmalıdır.',
              frequency: 1,
              openCount: 0,
              inRemediationCount: 0,
              curedCount: 1,
              status: 'cured',
              lastOffendingStep: '-(2x - 5) = -2x - 5',
              lastProblem: '-(2x - 5) = 3',
              avgStabilityDays: 2.5,
            ),
          ],
        ),
        MisconceptionCategory(
          categoryId: 'PARABOL_VE_POLINOM',
          categoryTitle: 'Parabol ve Polinomlar',
          totalMistakes: 0,
          activeMistakes: 0,
          curedMistakes: 0,
          nodes: [],
        ),
      ],
    );
  }

  Widget buildTestableWidget({MisconceptionProfileResponse? initialProfile}) {
    return MaterialApp(
      home: MisconceptionProfilerScreen(
        userId: 'test_user_42',
        initialProfile: initialProfile,
      ),
    );
  }

  group('MisconceptionProfilerScreen Tests', () {
    testWidgets('renders empty profile with zero-fabrication clean state', (tester) async {
      const emptyProfile = MisconceptionProfileResponse(
        userId: 'clean_user',
        totalRecordedMistakes: 0,
        totalCured: 0,
        overallCureRate: 0.0,
        topRecurringTraps: [],
        categories: [
          MisconceptionCategory(
            categoryId: 'KUADRATIK_DENKLEMLER',
            categoryTitle: 'Kuadratik Denklemler',
            totalMistakes: 0,
            activeMistakes: 0,
            curedMistakes: 0,
            nodes: [],
          ),
        ],
      );

      await tester.pumpWidget(buildTestableWidget(initialProfile: emptyProfile));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('misconception_profiler_app_bar')), findsOneWidget);
      expect(find.byKey(const Key('misconception_overview_card')), findsOneWidget);
      expect(find.text('0'), findsNWidgets(2)); // Toplam 0, Kür 0
      expect(find.text('%0.0'), findsOneWidget);
      expect(find.textContaining('Harika! Henüz tekrarlayan bir kavramsal tuzak saptanmadı'), findsOneWidget);
      expect(find.textContaining('Henüz Yanılgı Saptanmadı (Temiz Dal)'), findsOneWidget);
    });

    testWidgets('renders profile with traps and tree nodes', (tester) async {
      final mock = createMockProfile();

      await tester.pumpWidget(buildTestableWidget(initialProfile: mock));
      await tester.pumpAndSettle();

      // Verify overview stats
      expect(find.text('3'), findsOneWidget); // Total
      expect(find.text('1'), findsOneWidget); // Cured
      expect(find.text('%33.3'), findsOneWidget); // Cure rate

      // Verify top traps
      expect(find.byKey(const Key('trap_card_BUG-QUAD-01')), findsOneWidget);
      expect(find.byKey(const Key('trap_card_SIGN_FLIP')), findsOneWidget);
      expect(find.text('🔴 Kritik Zaaf'), findsWidgets);
      expect(find.text('✅ Aşılmış'), findsWidgets);

      // Verify tree nodes
      expect(find.byKey(const Key('node_card_BUG-QUAD-01')), findsOneWidget);
      expect(find.byKey(const Key('node_card_SIGN_FLIP')), findsOneWidget);
    });

    testWidgets('tapping trap card opens diagnosis and autopsy bottom sheet', (tester) async {
      final mock = createMockProfile();

      await tester.pumpWidget(buildTestableWidget(initialProfile: mock));
      await tester.pumpAndSettle();

      // Tap on top trap card
      await tester.tap(find.byKey(const Key('trap_card_BUG-QUAD-01')));
      await tester.pumpAndSettle();

      // Bottom sheet should be open
      expect(find.byKey(const Key('misconception_detail_sheet')), findsOneWidget);
      expect(find.text('Sıfır-Çarpım Kuralı İhlali'), findsWidgets);
      expect(find.textContaining('Eşitliğin sağ tarafı sıfırdan farklı iken'), findsWidgets);
      expect(find.textContaining('Eşitliğin sağ tarafı sıfır olmalıdır'), findsWidgets);
      expect(find.byKey(const Key('start_remediation_cta_button')), findsOneWidget);

      // Tap start remediation button
      await tester.tap(find.byKey(const Key('start_remediation_cta_button')));
      await tester.pumpAndSettle();

      // Sheet should close and snackbar show
      expect(find.byKey(const Key('misconception_detail_sheet')), findsNothing);
      expect(find.byType(SnackBar), findsOneWidget);
    });

    testWidgets('filter chips filter category tree branches', (tester) async {
      final mock = createMockProfile();

      await tester.pumpWidget(buildTestableWidget(initialProfile: mock));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('category_tile_KUADRATIK_DENKLEMLER')), findsOneWidget);
      expect(find.byKey(const Key('category_tile_ISARET_VE_DAGILMA')), findsOneWidget);

      // Filter by "İşaret ve Parantez Dağılımı"
      await tester.tap(find.widgetWithText(ChoiceChip, 'İşaret ve Parantez Dağılımı'));
      await tester.pumpAndSettle();

      // Only that category should remain visible
      expect(find.byKey(const Key('category_tile_ISARET_VE_DAGILMA')), findsOneWidget);
      expect(find.byKey(const Key('category_tile_KUADRATIK_DENKLEMLER')), findsNothing);
    });

    testWidgets('renders heat map section and opens autopsy sheet when heat tile is tapped', (tester) async {
      final mock = createMockProfile();

      await tester.pumpWidget(buildTestableWidget(initialProfile: mock));
      await tester.pumpAndSettle();

      // Heat map section should exist
      expect(find.byKey(const Key('misconception_heat_map_section')), findsOneWidget);
      expect(find.text('Kavramsal Isı Haritası'), findsOneWidget);
      expect(find.text('1 / 2 Aşılmış'), findsOneWidget);

      // Heat tiles should be rendered for each node
      expect(find.byKey(const Key('heat_tile_BUG-QUAD-01')), findsOneWidget);
      expect(find.byKey(const Key('heat_tile_SIGN_FLIP')), findsOneWidget);

      // Tapping heat tile opens autopsy bottom sheet
      await tester.ensureVisible(find.byKey(const Key('heat_tile_BUG-QUAD-01')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('heat_tile_BUG-QUAD-01')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('misconception_detail_sheet')), findsOneWidget);
      expect(find.text('Sıfır-Çarpım Kuralı İhlali'), findsWidgets);
    });
  });
}
