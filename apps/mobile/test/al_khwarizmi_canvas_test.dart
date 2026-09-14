import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/al_khwarizmi_canvas.dart';

void main() {
  testWidgets('AlKhwarizmiCanvas renders geometric tiles and updates completion state', (tester) async {
    bool toggled = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AlKhwarizmiCanvas(
            bCoefficient: 6.0,
            onCompleteToggled: () => toggled = true,
          ),
        ),
      ),
    );

    // Initial state: uncompleted square
    expect(find.text('El-Harezmi Geometrik Alan Karoları'), findsOneWidget);
    expect(find.text('Eksik Parça'), findsOneWidget);
    expect(find.textContaining('Mevcut: x² + 6x'), findsOneWidget);

    // Tap toggle completion button
    await tester.tap(find.text('Eksik Parça'));
    await tester.pumpAndSettle();

    // Completed state
    expect(toggled, isTrue);
    expect(find.text('Tam Kare'), findsOneWidget);
    expect(find.textContaining('Alan: (x + 3)² = x² + 6x + 9'), findsOneWidget);
  });
}
