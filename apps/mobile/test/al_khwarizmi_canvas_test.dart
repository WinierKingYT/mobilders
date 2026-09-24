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

    // Pedagogical balance note verification
    expect(find.byKey(const Key('alkhwarizmi_balance_note')), findsOneWidget);
    expect(
      find.textContaining('Pedagojik Vurgu: Denklemin dengesini korumak için eşitliğin her iki tarafına da (b/2)² = +9 ilave edilir'),
      findsOneWidget,
    );
  });

  test('AlKhwarizmiCanvas.clampB clamps negative and excessive coefficients correctly', () {
    expect(AlKhwarizmiCanvas.clampB(-8.0), 2.0);
    expect(AlKhwarizmiCanvas.clampB(0.0), 2.0);
    expect(AlKhwarizmiCanvas.clampB(35.0), 20.0);
    expect(AlKhwarizmiCanvas.clampB(8.0), 8.0);
    expect(AlKhwarizmiCanvas.clampB(double.nan), 6.0);
  });

  testWidgets('AlKhwarizmiCanvas shows cognitive warning banner when b is negative', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AlKhwarizmiCanvas(
            bCoefficient: -4.0,
          ),
        ),
      ),
    );

    expect(find.byKey(const Key('alkhwarizmi_clamping_warning')), findsOneWidget);
    expect(find.textContaining('Negatif veya sıfır katsayılar'), findsOneWidget);
  });

  testWidgets('AlKhwarizmiCanvas shows cognitive warning banner when b > 20', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AlKhwarizmiCanvas(
            bCoefficient: 28.0,
          ),
        ),
      ),
    );

    expect(find.byKey(const Key('alkhwarizmi_clamping_warning')), findsOneWidget);
    expect(find.textContaining('azami 20 ile sınırlandırılmıştır'), findsOneWidget);
  });
}
