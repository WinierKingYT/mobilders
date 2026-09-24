import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/riemann_integral_canvas.dart';

void main() {
  testWidgets('RiemannIntegralCanvas renders properly with initial area metrics', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: RiemannIntegralCanvas(
              initialN: 4,
              initialMethod: RiemannMethod.left,
              initialFunc: IntegralFunctionType.parabola,
            ),
          ),
        ),
      ),
    );

    // 1. Verify title
    expect(find.text("Riemann İntegral & Alan Simülatörü"), findsOneWidget);

    // 2. Verify function chips
    expect(find.text("f(x) = 0.5x²"), findsOneWidget);
    expect(find.text("f(x) = 2.5 - 0.4x²"), findsOneWidget);
    expect(find.text("f(x) = sin(x) + 1.2"), findsOneWidget);

    // 3. Verify method chips
    expect(find.text("Sol Toplam"), findsOneWidget);
    expect(find.text("Sağ Toplam"), findsOneWidget);
    expect(find.text("Orta Nokta"), findsOneWidget);
    expect(find.text("Yamuk Kuralı"), findsOneWidget);

    // 4. Verify metrics box labels
    expect(find.text("Riemann Toplamı (S_n)"), findsOneWidget);
    expect(find.text("Tam Alan (∫ f dx)"), findsOneWidget);
    expect(find.text("Hata Payı (|ΔA|)"), findsOneWidget);

    // 5. Initial state for f(x) = 0.5x^2 on [0, 2] with n=4 left sum:
    // dx = 0.5; x = 0, 0.5, 1.0, 1.5
    // f(0)=0, f(0.5)=0.125, f(1)=0.5, f(1.5)=1.125
    // sum = 0.5 * (0 + 0.125 + 0.5 + 1.125) = 0.5 * 1.75 = 0.8750
    // Exact area = 4/3 ~ 1.3333
    expect(find.text("0.8750"), findsOneWidget);
    expect(find.text("1.3333"), findsOneWidget);
  });

  testWidgets('RiemannIntegralCanvas preset n=64 triggers limit convergence badge', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: RiemannIntegralCanvas(
              initialN: 4,
              initialMethod: RiemannMethod.left,
              initialFunc: IntegralFunctionType.parabola,
            ),
          ),
        ),
      ),
    );

    // Initially with n=4 left sum: deltaA = |0.875 - 1.333| = 0.458 > 0.05
    expect(find.text("ΔA Yaklaşıyor"), findsOneWidget);

    // Tap "n = 64 (Limit)" chip
    final limitChip = find.text("n = 64 (Limit)");
    expect(limitChip, findsOneWidget);
    await tester.tap(limitChip);
    await tester.pumpAndSettle();

    // Now with n=64 and midpoint/left, error is tiny -> badge switches to "Yakınsadı (Limit!)"
    expect(find.text("Yakınsadı (Limit!)"), findsOneWidget);
  });

  testWidgets('RiemannIntegralCanvas clamps out-of-range initialN without crashing Slider', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: RiemannIntegralCanvas(
              initialN: 999,
            ),
          ),
        ),
      ),
    );

    expect(tester.takeException(), isNull);
    expect(find.text("Riemann İntegral & Alan Simülatörü"), findsOneWidget);
  });

  test('RiemannIntegralCanvas.clampN clamps n strictly into [2, 100]', () {
    expect(RiemannIntegralCanvas.clampN(0), 2);
    expect(RiemannIntegralCanvas.clampN(1), 2);
    expect(RiemannIntegralCanvas.clampN(-10), 2);
    expect(RiemannIntegralCanvas.clampN(50), 50);
    expect(RiemannIntegralCanvas.clampN(100), 100);
    expect(RiemannIntegralCanvas.clampN(250), 100);
  });

  testWidgets('RiemannIntegralCanvas computes Alt Toplam (lower) and Üst Toplam (upper) correctly', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: RiemannIntegralCanvas(
              initialN: 4,
              initialMethod: RiemannMethod.lower,
              initialFunc: IntegralFunctionType.parabola,
            ),
          ),
        ),
      ),
    );

    // Initial with Alt Toplam on f(x)=0.5x^2, n=4 on [0, 2]:
    // dx = 0.5. Intervals: [0, 0.5], [0.5, 1], [1, 1.5], [1.5, 2]
    // Since f(x)=0.5x^2 is increasing on [0, 2], lower Darboux sum equals left sum = 0.8750
    expect(find.text("0.8750"), findsOneWidget);

    // Switch to Üst Toplam
    final upperChip = find.text("Üst Toplam");
    expect(upperChip, findsOneWidget);
    await tester.tap(upperChip);
    await tester.pumpAndSettle();

    // Upper Darboux sum equals right sum:
    // dx * (f(0.5) + f(1) + f(1.5) + f(2)) = 0.5 * (0.125 + 0.5 + 1.125 + 2.0) = 0.5 * 3.75 = 1.8750
    expect(find.text("1.8750"), findsOneWidget);
  });

  testWidgets('RiemannIntegralCanvas preset n=100 triggers limit convergence badge', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: RiemannIntegralCanvas(
              initialN: 4,
              initialMethod: RiemannMethod.left,
              initialFunc: IntegralFunctionType.parabola,
            ),
          ),
        ),
      ),
    );

    final limitChip = find.text("n = 100 (Limit n→∞)");
    expect(limitChip, findsOneWidget);
    await tester.ensureVisible(limitChip);
    await tester.tap(limitChip);
    await tester.pumpAndSettle();

    expect(find.text("Yakınsadı (Limit!)"), findsOneWidget);
  });
}

