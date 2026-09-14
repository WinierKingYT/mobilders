import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/scanner/math_scanner_view.dart';

void main() {
  testWidgets('MathScannerView renders viewfinder with Anti-Photomath badge', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: MathScannerView(),
          ),
        ),
      ),
    );

    // 1. Verify title and anti-photomath shield badge
    expect(find.text("Sokratik Soru & Defter Kamerası"), findsOneWidget);
    expect(find.text("Anti-Photomath (Sıfır Sızıntı)"), findsOneWidget);

    // 2. Viewfinder instructions
    expect(find.textContaining("Defterdeki matematiksel adımları"), findsOneWidget);

    // 3. Camera shutter button
    expect(find.byIcon(Icons.camera_alt), findsOneWidget);
  });

  testWidgets('MathScannerView shutter tap reveals segmented steps and Socratic hint', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: MathScannerView(
              initialProblem: "(x + 3)² = 25",
              dagNodeId: "N19",
              dagNodeTitle: "Kuadratik Denklemler",
            ),
          ),
        ),
      ),
    );

    // Tap shutter button
    final shutter = find.byIcon(Icons.camera_alt);
    expect(shutter, findsOneWidget);
    await tester.tap(shutter);
    await tester.pump(); // Start async delay
    await tester.pump(const Duration(milliseconds: 150)); // Finish delay
    await tester.pump();

    // 1. Verify problem header and DAG node
    expect(find.text("(x + 3)² = 25"), findsOneWidget);
    expect(find.text("N19: Kuadratik Denklemler"), findsOneWidget);

    // 2. Verify segmented step with BUG-QUAD-03
    expect(find.text("Adım 1:"), findsOneWidget);
    expect(find.text("x² + 9 = 25"), findsOneWidget);
    expect(find.text("BUG-QUAD-03"), findsOneWidget);

    // 3. Verify Socratic inquiry bubble
    expect(find.text("Sokratik Düşünme Sorusu:"), findsOneWidget);
    expect(find.textContaining("çarpımın iki katı (2ab)"), findsOneWidget);

    // 4. Verify reset button works
    final resetBtn = find.text("Yeni Fotoğraf Çek");
    expect(resetBtn, findsOneWidget);
    await tester.tap(resetBtn);
    await tester.pump(const Duration(milliseconds: 50));

    // Back to viewfinder
    expect(find.byIcon(Icons.camera_alt), findsOneWidget);
  });
}
