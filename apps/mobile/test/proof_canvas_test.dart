import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/proof_canvas.dart';

void main() {
  testWidgets('ProofCanvas renders Truth Table mode and toggles inputs',
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

    // 1. Verify Mode buttons
    expect(find.text("Doğruluk Tablosu"), findsOneWidget);
    expect(find.text("Tümevarım"), findsOneWidget);
    expect(find.text("İspat Tahtası"), findsOneWidget);

    // 2. Verify chips
    expect(find.byKey(const Key('chip_toggle_p')), findsOneWidget);
    expect(find.byKey(const Key('chip_toggle_q')), findsOneWidget);

    // 3. Toggle p to False
    await tester.tap(find.byKey(const Key('chip_toggle_p')));
    await tester.pumpAndSettle();

    // With p=0, q=1 -> p => q should still be 1 (green)
    expect(find.textContaining("p ⇒ q"), findsWidgets);
  });

  testWidgets('ProofCanvas switches to Induction mode and advances stages',
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

    // Switch to Induction
    await tester.tap(find.text("Tümevarım"));
    await tester.pumpAndSettle();

    // Verify stages
    expect(find.byKey(const Key('tile_stage_base')), findsOneWidget);
    expect(find.byKey(const Key('tile_stage_hypothesis')), findsOneWidget);
    expect(find.byKey(const Key('tile_stage_step')), findsOneWidget);

    // Tap Next Stage
    await tester.tap(find.byKey(const Key('btn_next_induction_stage')));
    await tester.pumpAndSettle();

    expect(find.textContaining("n = 2"), findsOneWidget);
  });

  testWidgets('ProofCanvas switches to Deduction mode and changes rule',
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

    // Switch to Deduction
    await tester.tap(find.text("İspat Tahtası"));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('dropdown_deduction_rule')), findsOneWidget);
    expect(find.textContaining("Modus Ponens"), findsWidgets);
  });
}
