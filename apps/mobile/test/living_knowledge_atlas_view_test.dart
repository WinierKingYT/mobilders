import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/atlas/living_knowledge_atlas_view.dart';

void main() {
  testWidgets('LivingKnowledgeAtlasView renders stats bar, search, and nodes list',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: LivingKnowledgeAtlasView(),
        ),
      ),
    );

    // 1. Verify Stats Bar
    expect(find.text("Toplam Düğüm"), findsOneWidget);
    expect(find.text("Usta Olunan"), findsOneWidget);
    expect(find.text("ZPD (Hazır)"), findsOneWidget);

    // 2. Verify Search Bar
    expect(find.byKey(const Key('atlas_search_field')), findsOneWidget);

    // 3. Verify Nodes rendered
    expect(find.byKey(const Key('atlas_nodes_list')), findsOneWidget);
    expect(find.text("Sayı Doğrusu ve Yön Sezgisi"), findsOneWidget);
    expect(find.text("Toplam ve Farkın Türevi"), findsOneWidget);
  });

  testWidgets('LivingKnowledgeAtlasView filters nodes by search query',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: LivingKnowledgeAtlasView(),
        ),
      ),
    );

    // Enter search text "Türev"
    await tester.enterText(find.byKey(const Key('atlas_search_field')), "Türev");
    await tester.pumpAndSettle();

    // Verify filtered results
    expect(find.text("Toplam ve Farkın Türevi"), findsOneWidget);
    expect(find.text("Sayı Doğrusu ve Yön Sezgisi"), findsNothing);
  });

  testWidgets('LivingKnowledgeAtlasView opens detail modal sheet on card tap',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: LivingKnowledgeAtlasView(),
        ),
      ),
    );

    // Tap the first node card
    await tester.tap(find.byKey(const Key('node_card_N_ROOT_01')));
    await tester.pumpAndSettle();

    // Verify modal sheet content
    expect(find.byKey(const Key('btn_start_learning_path')), findsOneWidget);
    expect(find.text("Öğrenme Yolunu Başlat"), findsOneWidget);

    // Close modal sheet
    await tester.tap(find.byKey(const Key('btn_start_learning_path')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('btn_start_learning_path')), findsNothing);
  });
}
