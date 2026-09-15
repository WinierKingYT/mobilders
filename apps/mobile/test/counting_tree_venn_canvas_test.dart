import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
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
}
