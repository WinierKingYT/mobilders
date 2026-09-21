import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/unit_circle_canvas.dart';

void main() {
  testWidgets('UnitCircleCanvas renders header, canvas, slider, and quadrant badge', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: UnitCircleCanvas(
            initialAngle: 45.0,
          ),
        ),
      ),
    );

    // Initial assertions
    expect(find.text('İnteraktif Birim Çember Kanvası'), findsOneWidget);
    expect(find.text('1. Bölge (+, +)'), findsOneWidget);
    expect(find.text('45°'), findsNWidgets(2)); // Once in readout, once in preset chip
    expect(find.textContaining('π/4 rad'), findsOneWidget);
    expect(find.text('cos θ (Apsis)'), findsOneWidget);
    expect(find.text('sin θ (Ordinat)'), findsOneWidget);
    expect(find.text('tan θ (Eğim)'), findsOneWidget);
  });

  testWidgets('UnitCircleCanvas updates quadrant badge and metrics when 180° preset is tapped', (tester) async {
    double changedAngle = 0.0;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: UnitCircleCanvas(
            initialAngle: 30.0,
            onAngleChanged: (val) => changedAngle = val,
          ),
        ),
      ),
    );

    expect(find.text('30°'), findsNWidgets(2)); // Once in readout, once in chip

    // Tap the 180° preset chip
    final chip180 = find.widgetWithText(ChoiceChip, '180°');
    expect(chip180, findsOneWidget);
    await tester.tap(chip180);
    await tester.pumpAndSettle();

    expect(changedAngle, 180.0);
    expect(find.text('180°'), findsNWidgets(2));
    expect(find.textContaining('π rad'), findsOneWidget);
    // At 180 deg, quadrant is 3. Bolge or 2. Bolge
    expect(find.text('3. Bölge (-, -)'), findsOneWidget);
  });
}
