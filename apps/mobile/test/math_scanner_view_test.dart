import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/scanner/math_scanner_view.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';

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

  testWidgets('MathScannerView switches preset scenario chips and reveals calculus integral error', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: MathScannerView(),
          ),
        ),
      ),
    );

    // 1. Find and tap "İntegral +C" preset chip
    final integralChip = find.text("İntegral +C");
    expect(integralChip, findsOneWidget);
    await tester.tap(integralChip);
    await tester.pump();

    // 2. Tap shutter button
    final shutter = find.byIcon(Icons.camera_alt);
    await tester.tap(shutter);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 150));
    await tester.pump();

    // 3. Verify Integral problem and DAG node
    expect(find.text("N111: Belirsiz İntegral"), findsOneWidget);
    expect(find.text("BUG-INT-01"), findsOneWidget);
    expect(find.textContaining("integrasyon sabiti"), findsWidgets);
  });

  testWidgets('MathScannerView switches to valid scenario and shows celebration state', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: MathScannerView(),
          ),
        ),
      ),
    );

    // 1. Find and tap "Hatasız Çözüm" preset chip
    final cleanChip = find.text("Hatasız Çözüm");
    expect(cleanChip, findsOneWidget);
    await tester.tap(cleanChip);
    await tester.pump(const Duration(milliseconds: 100));

    // 2. Tap shutter
    await tester.tap(find.byIcon(Icons.camera_alt));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 150));
    await tester.pump();

    // 3. Verify celebration bubble and valid check icons
    expect(find.text("Harika Başarı!"), findsOneWidget);
    expect(find.textContaining("matematiksel olarak tamamen doğru"), findsOneWidget);
    expect(find.byIcon(Icons.check_circle), findsNWidgets(2));
  });

  testWidgets('MathScannerView live API service integration returns diagnosed steps', (WidgetTester tester) async {
    final mockApi = _MockEngineApiService(
      onScan: ({imageBase64, rawTextOverride, targetProblem, studentId}) {
        return {
          'problem_statement': '-3x ≤ 9',
          'dag_node_id': 'N08',
          'dag_node_title': 'Eşitsizlikler',
          'segmented_steps': [
            {
              'step_index': 1,
              'raw_text': 'x ≤ -3',
              'latex': 'x ≤ -3',
              'is_valid': false,
              'diagnostic_bug_id': 'BUG-QUAD-06',
              'error_reason': 'Negatif sayıya bölerken yön değişmedi',
            },
          ],
          'has_error': true,
          'error_step_index': 1,
          'detected_bug_id': 'BUG-QUAD-06',
          'socratic_hint': 'Negatif bir sayıya bölerken eşitsizlik yönü ne olmalı?',
          'is_zero_leakage_sanitized': true,
          'confidence': 0.98,
        };
      },
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: MathScannerView(apiService: mockApi),
          ),
        ),
      ),
    );

    // Tap shutter
    await tester.tap(find.byIcon(Icons.camera_alt));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    await tester.pump();

    // Verify response rendered from API
    expect(find.text("N08: Eşitsizlikler"), findsOneWidget);
    expect(find.text("BUG-QUAD-06"), findsOneWidget);
    expect(find.textContaining("eşitsizlik yönü ne olmalı?"), findsOneWidget);
  });

  group('MathScannerView Loupe Magnifier & Diagnostic Step Error Highlights (Stage 63)', () {
    testWidgets('Dragging crop handle activates loupe magnifier with 2.0x precision reticle', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: MathScannerView(),
            ),
          ),
        ),
      );

      // Verify crop box and handles exist
      expect(find.byKey(const Key('scanner_crop_box')), findsOneWidget);
      final handle = find.byKey(const Key('crop_handle_top_left'));
      expect(handle, findsOneWidget);

      // Loupe should not be visible before drag
      expect(find.byKey(const Key('crop_loupe_magnifier')), findsNothing);

      // Start dragging handle
      final gesture = await tester.startGesture(tester.getCenter(handle));
      await tester.pump();
      await gesture.moveBy(const Offset(20, 20));
      await tester.pump();

      // Loupe magnifier must appear with reticle and label
      expect(find.byKey(const Key('crop_loupe_magnifier')), findsOneWidget);
      expect(find.text("2.0x Hassas Ayar"), findsOneWidget);

      // End drag
      await gesture.up();
      await tester.pump();

      // Loupe disappears after gesture release
      expect(find.byKey(const Key('crop_loupe_magnifier')), findsNothing);
    });

    testWidgets('Scanned steps with errors display red highlight container, error badge, and diagnostic report', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: MathScannerView(
                initialProblem: "(x + 3)² = 25",
              ),
            ),
          ),
        ),
      );

      // Tap shutter to reveal diagnostic result
      await tester.tap(find.byIcon(Icons.camera_alt));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 150));
      await tester.pump();

      // Verify red highlight container for error step 1
      expect(find.byKey(const Key('step_error_highlight_1')), findsOneWidget);

      // Verify "Hatalı Adım" badge
      expect(find.byKey(const Key('step_error_badge')), findsOneWidget);
      expect(find.text("Hatalı Adım"), findsOneWidget);

      // Verify diagnostic error reason
      expect(find.byKey(const Key('step_error_reason_1')), findsOneWidget);
      expect(find.textContaining("Teşhis Raporu:"), findsOneWidget);
      expect(find.textContaining("çarpımın iki katı (2ab)"), findsWidgets);
    });
  });
}

class _MockEngineApiService extends Fake implements EngineApiService {
  final Map<String, dynamic> Function({
    String? imageBase64,
    String? rawTextOverride,
    String? targetProblem,
    String? studentId,
  }) onScan;

  _MockEngineApiService({required this.onScan});

  @override
  Future<Map<String, dynamic>> scanAndDiagnoseNotebook({
    String? imageBase64,
    String? rawTextOverride,
    String? targetProblem,
    String? studentId,
  }) async {
    return onScan(
      imageBase64: imageBase64,
      rawTextOverride: rawTextOverride,
      targetProblem: targetProblem,
      studentId: studentId,
    );
  }
}

