import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/dynamic_tangent_canvas.dart';

void main() {
  testWidgets('DynamicTangentCanvas renders properly with initial slope metrics', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: DynamicTangentCanvas(initialX0: 1.0, initialH: 1.0),
          ),
        ),
      ),
    );

    // 1. Verify title
    expect(find.text("Dinamik Türev & Teğet Simülatörü"), findsOneWidget);

    // 2. Verify curve chips
    expect(find.text("f(x) = 0.5x²"), findsOneWidget);
    expect(find.text("f(x) = 0.25x³"), findsOneWidget);
    expect(find.text("f(x) = 1.8 sin(x)"), findsOneWidget);

    // 3. Verify slope readout widgets
    expect(find.text("Sekant Eğimi (m_sec)"), findsOneWidget);
    expect(find.text("Teğet Eğimi (m_tan)"), findsOneWidget);

    // 4. Initial state with x0 = 1.0, h = 1.0 on f(x) = 0.5x^2:
    // f(1) = 0.5, f(2) = 2.0 -> m_sec = (2.0 - 0.5)/1 = 1.500
    // m_tan = x0 = 1.000
    expect(find.text("1.500"), findsOneWidget);
    expect(find.text("1.000"), findsOneWidget);
  });

  testWidgets('DynamicTangentCanvas limit preset chip triggers limit convergence badge', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: DynamicTangentCanvas(initialX0: 1.0, initialH: 1.5),
          ),
        ),
      ),
    );

    // Initially with h = 1.5: deltaM is large, should show "Sekant Doğrusu"
    expect(find.text("Sekant Doğrusu"), findsOneWidget);

    // Tap "h → 0.02 (Limit)" chip
    final limitChip = find.text("h → 0.02 (Limit)");
    expect(limitChip, findsOneWidget);
    await tester.ensureVisible(limitChip);
    await tester.tap(limitChip);
    await tester.pumpAndSettle();

    // Now deltaM < 0.08, badge should switch to "Teğete Yakınsadı (Limit!)"
    expect(find.text("Teğete Yakınsadı (Limit!)"), findsOneWidget);
  });

  test('DynamicTangentCanvas.clampH prevents division by zero and preserves minimum 0.001 bound', () {
    expect(DynamicTangentCanvas.clampH(0.0), 0.001);
    expect(DynamicTangentCanvas.clampH(-0.5), 0.001);
    expect(DynamicTangentCanvas.clampH(0.0001), 0.001);
    expect(DynamicTangentCanvas.clampH(0.001), 0.001);
    expect(DynamicTangentCanvas.clampH(1.2), 1.2);
    expect(DynamicTangentCanvas.clampH(5.0), 2.0);
    expect(DynamicTangentCanvas.clampH(double.nan), 0.001);
  });

  testWidgets('DynamicTangentCanvas renders instantaneous limit formula card and handles h=0.001 limit chip', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: DynamicTangentCanvas(initialX0: 2.0, initialH: 0.5),
          ),
        ),
      ),
    );

    // Verify instantaneous limit card is rendered
    expect(find.byKey(const Key('instantaneous_slope_formula_card')), findsOneWidget);
    expect(find.textContaining("m = lim_{h→0}"), findsOneWidget);

    // Tap h -> 0.001 limit chip
    final chip0001 = find.byKey(const Key('tangent_preset_h_limit_0001'));
    expect(chip0001, findsOneWidget);
    await tester.ensureVisible(chip0001);
    await tester.tap(chip0001);
    await tester.pumpAndSettle();

    expect(find.text("Teğete Yakınsadı (Limit!)"), findsOneWidget);
    // At x0=2.0 on f(x)=0.5x^2, m_tan = 2.000
    expect(find.text("2.000"), findsWidgets);
  });

  testWidgets('DynamicTangentCanvas safely clamps out-of-range initialH without Slider assertion crash', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: DynamicTangentCanvas(initialX0: 10.0, initialH: 99.0),
          ),
        ),
      ),
    );

    expect(tester.takeException(), isNull);
    expect(find.text("Dinamik Türev & Teğet Simülatörü"), findsOneWidget);
  });
}

