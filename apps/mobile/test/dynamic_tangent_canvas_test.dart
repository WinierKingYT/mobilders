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
    await tester.tap(limitChip);
    await tester.pumpAndSettle();

    // Now deltaM < 0.08, badge should switch to "Teğete Yakınsadı (Limit!)"
    expect(find.text("Teğete Yakınsadı (Limit!)"), findsOneWidget);
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

