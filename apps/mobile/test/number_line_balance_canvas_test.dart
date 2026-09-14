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
  });
}
