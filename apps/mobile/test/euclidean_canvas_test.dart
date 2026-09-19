import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/euclidean_canvas.dart';

void main() {
  testWidgets('EuclideanCanvas renders properly with initial isosceles preset and hint',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: EuclideanCanvas(
              initialPreset: EuclideanShapePreset.isosceles,
              initialShowAuxiliary: false,
            ),
          ),
        ),
      ),
    );

    // 1. Verify canvas and header
    expect(find.byKey(const Key('euclidean_canvas')), findsOneWidget);
    expect(find.text("İkizkenar Üçgen"), findsWidgets);

    // 2. Verify hint banner
    expect(find.byKey(const Key('hint_banner')), findsOneWidget);
    expect(find.textContaining("yükseklik indir"), findsOneWidget);

    // 3. Verify toggle button
    final toggleBtn = find.byKey(const Key('btn_toggle_auxiliary'));
    expect(toggleBtn, findsOneWidget);
    expect(find.text("Ek Çizimi Göster"), findsOneWidget);

    // 4. Tap toggle button -> shows auxiliary lines
    await tester.tap(toggleBtn);
    await tester.pumpAndSettle();
    expect(find.text("Ek Çizimi Gizle"), findsOneWidget);
  });

  testWidgets('EuclideanCanvas switches presets and updates Socratic hints correctly',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: EuclideanCanvas(),
          ),
        ),
      ),
    );

    // Switch to Right Triangle
    await tester.tap(find.byKey(const Key('preset_right')));
    await tester.pumpAndSettle();
    expect(find.textContaining("Muhteşem Üçlü"), findsOneWidget);

    // Switch to Trapezoid
    await tester.tap(find.byKey(const Key('preset_trapezoid')));
    await tester.pumpAndSettle();
    expect(find.textContaining("paralelkenar ve üçgene"), findsOneWidget);

    // Switch to Circle & Tangent
    await tester.tap(find.byKey(const Key('preset_circle')));
    await tester.pumpAndSettle();
    expect(find.textContaining("r ⊥ d"), findsOneWidget);
  });

  testWidgets('EuclideanCanvas renders with initialShowAuxiliary true and toggles off',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: EuclideanCanvas(
              initialPreset: EuclideanShapePreset.rightTriangle,
              initialShowAuxiliary: true,
            ),
          ),
        ),
      ),
    );

    // Verify initial auxiliary state is shown
    expect(find.text("Ek Çizimi Gizle"), findsOneWidget);
    expect(find.textContaining("Muhteşem Üçlü"), findsOneWidget);

    // Toggle off
    await tester.tap(find.byKey(const Key('btn_toggle_auxiliary')));
    await tester.pumpAndSettle();
    expect(find.text("Ek Çizimi Göster"), findsOneWidget);
  });

  testWidgets('EuclideanCanvas trapezoid preset renders title and toggles auxiliary parallel line',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: EuclideanCanvas(
              initialPreset: EuclideanShapePreset.trapezoid,
              initialShowAuxiliary: false,
            ),
          ),
        ),
      ),
    );

    expect(find.text("Yamuk"), findsWidgets);
    expect(find.textContaining("paralelkenar ve üçgene"), findsOneWidget);

    // Toggle auxiliary
    await tester.tap(find.byKey(const Key('btn_toggle_auxiliary')));
    await tester.pumpAndSettle();
    expect(find.text("Ek Çizimi Gizle"), findsOneWidget);
  });
}

