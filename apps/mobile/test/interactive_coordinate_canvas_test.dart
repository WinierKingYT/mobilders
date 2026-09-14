import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/interactive_coordinate_canvas.dart';

void main() {
  testWidgets('InteractiveCoordinateCanvas renders properly with initial slope & distance metrics',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: InteractiveCoordinateCanvas(
              initialPointA: Offset(1.0, 2.0),
              initialPointB: Offset(5.0, 5.0),
            ),
          ),
        ),
      ),
    );

    // 1. Verify canvas exists
    expect(find.byKey(const Key('coord_canvas')), findsOneWidget);

    // 2. Verify coordinate readouts
    expect(find.text("A(1.0, 2.0)"), findsOneWidget);
    expect(find.text("B(5.0, 5.0)"), findsOneWidget);

    // 3. Verify distance: dx=4, dy=3 => d=5.00
    expect(find.text("Uzaklık: 5.00"), findsOneWidget);

    // 4. Verify slope: 3/4 = 0.75
    expect(find.text("Eğim: 0.75"), findsOneWidget);
  });

  testWidgets('InteractiveCoordinateCanvas switches to Circle and Vector modes properly',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: InteractiveCoordinateCanvas(
              initialPointA: Offset(1.0, 2.0),
              initialPointB: Offset(5.0, 5.0),
            ),
          ),
        ),
      ),
    );

    // 1. Switch to Circle mode
    await tester.tap(find.text("Çember"));
    await tester.pumpAndSettle();

    expect(find.text("Yarıçap r: 5.00"), findsOneWidget);
    expect(find.textContaining("Alan:"), findsOneWidget);

    // 2. Switch to Vector mode
    await tester.tap(find.text("Vektörler"));
    await tester.pumpAndSettle();

    // u=(1,2), v=(5,5) => u.v = 1*5 + 2*5 = 15.00
    expect(find.text("u · v: 15.00"), findsOneWidget);
  });

  testWidgets('InteractiveCoordinateCanvas detects orthogonal vectors in vector mode',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: InteractiveCoordinateCanvas(
              initialPointA: Offset(2.0, 0.0),
              initialPointB: Offset(0.0, 4.0),
            ),
          ),
        ),
      ),
    );

    // Switch to Vector mode
    await tester.tap(find.text("Vektörler"));
    await tester.pumpAndSettle();

    // u=(2,0), v=(0,4) => u.v = 0.00
    expect(find.text("u · v: 0.00"), findsOneWidget);
    expect(find.text("Dik Vektörler (u ⊥ v)"), findsOneWidget);
  });
}
