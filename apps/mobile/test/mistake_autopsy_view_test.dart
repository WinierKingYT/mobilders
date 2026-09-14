import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
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
}
