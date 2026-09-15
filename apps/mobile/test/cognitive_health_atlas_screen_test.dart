import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/cognitive_health_atlas_screen.dart';
import 'package:personal_learning_engine/ui/features/atlas/living_knowledge_atlas_view.dart';

void main() {
  testWidgets('CognitiveHealthAtlasScreen renders tabs and switches views', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: CognitiveHealthAtlasScreen(studentId: 'EXP-STU-TEST'),
      ),
    );
    await tester.pumpAndSettle();

    // Verify Title
    expect(find.text('Bilişsel Sağlık & Cebir Atlası'), findsOneWidget);

    // Verify Tab 1 (Metacognitive)
    expect(find.text('Beklenen Kalibrasyon Hatası (ECE)'), findsOneWidget);
    expect(find.text('0.0661'), findsOneWidget);
    expect(find.text('Brier Skoru'), findsOneWidget);

    // Tap Tab 2 (Paas)
    await tester.tap(find.text('Paas Bilişsel Yük'));
    await tester.pumpAndSettle();

    expect(find.text('Paas Bilişsel Verimlilik İndeksi (E)'), findsOneWidget);
    expect(find.text('+0.752'), findsOneWidget);

    // Tap Tab 3 (FSRS Retention)
    await tester.tap(find.text('FSRS 14 Gün Kalıcılık'));
    await tester.pumpAndSettle();

    expect(find.text('14 Günlük Hatırlama Kalıcılığı S(14)'), findsOneWidget);
    expect(find.text('%86.7'), findsWidgets);

    // Tap Tab 4 (26 Node Atlas)
    await tester.tap(find.text('26 Düğüm Atlası'));
    await tester.pumpAndSettle();

    expect(find.text('Seviye 0: Temel Cebir & Aritmetik'), findsOneWidget);
    expect(find.text('N01'), findsOneWidget);

    // Scroll down to see Level 5
    await tester.drag(find.byType(ListView), const Offset(0, -600));
    await tester.pumpAndSettle();

    expect(find.text('Seviye 5 (Grup A): İkinci Dereceden Eşitsizlikler'), findsOneWidget);
    expect(find.text('N21'), findsOneWidget);

    // Tap Tab 5 (Yaşayan Zihin Haritası - 246 Düğüm)
    await tester.tap(find.text('Yaşayan Zihin Haritası (246)'));
    await tester.pumpAndSettle();

    expect(find.byType(LivingKnowledgeAtlasView), findsOneWidget);
    expect(find.text('Toplam Düğüm'), findsOneWidget);
  });
}
