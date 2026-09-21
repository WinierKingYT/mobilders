import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/root_pedagogy/number_line_balance_canvas.dart';

void main() {
  testWidgets('NumberLineBalanceCanvas renders header, tabs, and switches views', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: NumberLineBalanceCanvas(),
        ),
      ),
    );

    // Initial check
    expect(find.text('Kök Pedagoji Mikro-Kum Havuzu'), findsOneWidget);
    expect(find.text('Seviye -3..-1'), findsOneWidget);
    expect(find.text('Konum: 0'), findsOneWidget);
    expect(find.text('Sıfır Denge'), findsOneWidget);

    // Tap 1 Sağa Yürü (+1)
    await tester.tap(find.text('1 Sağa Yürü (+1)'));
    await tester.pump();
    expect(find.text('Konum: 1'), findsOneWidget);
    expect(find.text('Alacak / Kazanç Alanı'), findsOneWidget);

    // Switch to Pasta Kesir
    await tester.tap(find.text('Pasta Kesir'));
    await tester.pump();
    expect(find.text('Toplam Dilim (Payda)'), findsOneWidget);
    expect(find.textContaining('Kesir Değeri = 1 / 4'), findsOneWidget);

    // Switch to Terazi
    await tester.tap(find.text('Terazi'));
    await tester.pump();
    expect(find.text('Sol Kefe: 2x + 3'), findsOneWidget);
    expect(find.text('Sağ Kefe: 11'), findsOneWidget);

    // Tap Her İki Kefeden 3 Eksilt
    await tester.tap(find.text('Her İki Kefeden 3 Eksilt (-3)'));
    await tester.pump();
    expect(find.text('Sol Kefe: 2x + 0'), findsOneWidget);
    expect(find.text('Sağ Kefe: 8'), findsOneWidget);

    // Verify reset button appears and restores initial balance state
    final resetBtn = find.byKey(const Key('btn_reset_balance'));
    expect(resetBtn, findsOneWidget);
    await tester.tap(resetBtn);
    await tester.pump();
    expect(find.text('Sol Kefe: 2x + 3'), findsOneWidget);
    expect(find.text('Sağ Kefe: 11'), findsOneWidget);
  });

  testWidgets('NumberLine stepping is clamped between -6 and +6', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: NumberLineBalanceCanvas(),
        ),
      ),
    );

    // Walk left 8 times
    for (int i = 0; i < 8; i++) {
      final leftBtn = find.byKey(const Key('btn_step_left'));
      if (tester.widget<ElevatedButton>(leftBtn).onPressed != null) {
        await tester.tap(leftBtn);
        await tester.pump();
      }
    }
    expect(find.text('Konum: -6'), findsOneWidget);
    // Left button should be disabled at edge -6
    final leftBtnAtEdge = find.byKey(const Key('btn_step_left'));
    expect(tester.widget<ElevatedButton>(leftBtnAtEdge).onPressed, isNull);
  });

  testWidgets('Pasta kesir synchronizes shaded slices when total slices decremented', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: NumberLineBalanceCanvas(initialMode: RootCanvasMode.pieFraction),
        ),
      ),
    );

    // Initial: 1 / 4. Increase shaded slices to 4.
    final addShadedBtn = find.byIcon(Icons.add_circle_outline).last;
    for (int i = 0; i < 3; i++) {
      await tester.tap(addShadedBtn);
      await tester.pump();
    }
    expect(find.textContaining('Kesir Değeri = 4 / 4'), findsOneWidget);

    // Now decrement fraction slices (from 4 to 3)
    final removeSliceBtn = find.byIcon(Icons.remove_circle_outline).first;
    await tester.tap(removeSliceBtn);
    await tester.pump();

    // Shaded slices should automatically be capped at 3, not remain at 4!
    expect(find.textContaining('Kesir Değeri = 3 / 3'), findsOneWidget);
  });
}

