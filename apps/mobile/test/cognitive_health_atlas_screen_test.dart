import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/analytics/views/cognitive_health_atlas_screen.dart';
import 'package:personal_learning_engine/ui/features/atlas/living_knowledge_atlas_view.dart';

void main() {
  testWidgets('CognitiveHealthAtlasScreen renders populated metrics when real telemetry is available', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: CognitiveHealthAtlasScreen(
          studentId: 'EXP-STU-TEST',
          hasRealData: true,
          ece: 0.0661,
          brierScore: 0.048,
          imposterRate: 4.2,
          paasIndex: 0.752,
          meanLatencySeconds: 3.12,
          ddmDriftRate: 0.184,
          retentionS14: 86.7,
          stabilityDays: 18.25,
        ),
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

  testWidgets('CognitiveHealthAtlasScreen displays honest baseline empty state when no session data exists', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: CognitiveHealthAtlasScreen(
          studentId: 'EXP-STU-FRESH',
          hasRealData: false,
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Verify Title
    expect(find.text('Bilişsel Sağlık & Cebir Atlası'), findsOneWidget);

    // Verify Tab 1: Shows '--' and 'SEANS VERİSİ GEREKLİ' without fabricated numbers
    expect(find.text('SEANS VERİSİ GEREKLİ'), findsOneWidget);
    expect(find.text('--'), findsWidgets);

    // Tap Tab 2 (Paas): Shows '--' and 'ÖLÇÜM BEKLENİYOR'
    await tester.tap(find.text('Paas Bilişsel Yük'));
    await tester.pumpAndSettle();

    expect(find.text('ÖLÇÜM BEKLENİYOR'), findsOneWidget);
    expect(find.text('Öğrenci Konumu (Seans Bekleniyor)'), findsOneWidget);

    // Tap Tab 3 (FSRS): Shows '--' and 'FSRS-4.5 TAKİBİ BEKLEMEDE'
    await tester.tap(find.text('FSRS 14 Gün Kalıcılık'));
    await tester.pumpAndSettle();

    expect(find.text('FSRS-4.5 TAKİBİ BEKLEMEDE'), findsOneWidget);
  });
}
