import 'dart:ui' show PointerDeviceKind;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/touchpad/vector_inking_canvas.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late HapticFeedbackService hapticService;

  setUp(() {
    hapticService = HapticFeedbackService();
    hapticService.isEnabled = true;
    hapticService.clearHistory();
    hapticService.testListener = null;
  });

  Widget buildTestableCanvas({
    Function(List<VectorInkingStroke>)? onStrokesUpdated,
    Function(String)? onExpressionRecognized,
    VoidCallback? onDismiss,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: SizedBox(
          width: 400,
          height: 600,
          child: VectorInkingCanvas(
            onStrokesUpdated: onStrokesUpdated,
            onExpressionRecognized: onExpressionRecognized,
            onDismiss: onDismiss,
          ),
        ),
      ),
    );
  }

  group('VectorInkingCanvas Haptic Feedback Integration Tests', () {
    testWidgets('PointerDown on canvas triggers HapticFeedbackService selectionClick', (tester) async {
      await tester.pumpWidget(buildTestableCanvas());

      final gesture = await tester.startGesture(const Offset(100, 200), pointer: 1);
      await tester.pump();

      expect(hapticService.triggeredHistory, contains(HapticType.selectionClick));

      await gesture.up();
      await tester.pump();
    });

    testWidgets('Drawing a stroke and tapping Undo triggers lightImpact', (tester) async {
      await tester.pumpWidget(buildTestableCanvas());

      // Draw stroke
      final gesture = await tester.startGesture(const Offset(100, 200), pointer: 1);
      await tester.pump();
      await gesture.moveBy(const Offset(50, 50));
      await tester.pump();
      await gesture.up();
      await tester.pump();

      hapticService.clearHistory();

      // Tap Undo button
      final undoButton = find.byTooltip('Geri Al');
      expect(undoButton, findsOneWidget);
      await tester.tap(undoButton);
      await tester.pump();

      expect(hapticService.triggeredHistory, contains(HapticType.lightImpact));
    });

    testWidgets('Drawing a stroke and tapping Clear triggers mediumImpact', (tester) async {
      await tester.pumpWidget(buildTestableCanvas());

      // Draw stroke
      final gesture = await tester.startGesture(const Offset(100, 200), pointer: 1);
      await tester.pump();
      await gesture.moveBy(const Offset(30, 30));
      await tester.pump();
      await gesture.up();
      await tester.pump();

      hapticService.clearHistory();

      // Tap Clear button
      final clearButton = find.byTooltip('Temizle');
      expect(clearButton, findsOneWidget);
      await tester.tap(clearButton);
      await tester.pump();

      expect(hapticService.triggeredHistory, contains(HapticType.mediumImpact));
    });

    testWidgets('Tapping Commit button triggers heavyImpact', (tester) async {
      String? recognized;
      await tester.pumpWidget(buildTestableCanvas(
        onExpressionRecognized: (expr) => recognized = expr,
      ));

      // Draw stroke to trigger heuristic preview
      final gesture = await tester.startGesture(const Offset(100, 200), pointer: 1);
      await tester.pump();
      await gesture.moveBy(const Offset(10, 10));
      await tester.pump();
      await gesture.up();
      await tester.pump();

      hapticService.clearHistory();

      // Find "Adımı Aktar" button
      final commitButton = find.text('Adımı Aktar');
      expect(commitButton, findsOneWidget);
      await tester.tap(commitButton);
      await tester.pump();

      expect(hapticService.triggeredHistory, contains(HapticType.heavyImpact));
      expect(recognized, isNotEmpty);
    });

    testWidgets('When HapticFeedbackService is disabled, no haptics are triggered', (tester) async {
      hapticService.isEnabled = false;

      await tester.pumpWidget(buildTestableCanvas());

      final gesture = await tester.startGesture(const Offset(100, 200), pointer: 1);
      await tester.pump();
      await gesture.moveBy(const Offset(20, 20));
      await tester.pump();
      await gesture.up();
      await tester.pump();

      expect(hapticService.triggeredHistory, isEmpty);
    });

    test('VectorInkingStrokeSimplifier simplifies collinear points and keeps endpoints', () {
      final points = [
        const VectorInkingPoint(x: 0, y: 0, timestampMs: 0),
        const VectorInkingPoint(x: 1, y: 1.01, timestampMs: 10), // Collinear jitter
        const VectorInkingPoint(x: 2, y: 1.99, timestampMs: 20), // Collinear jitter
        const VectorInkingPoint(x: 3, y: 3.02, timestampMs: 30), // Collinear jitter
        const VectorInkingPoint(x: 10, y: 10, timestampMs: 100),
      ];

      final simplified = VectorInkingStrokeSimplifier.simplify(points, epsilon: 0.5);
      expect(simplified.length, lessThan(points.length));
      expect(simplified.first.x, 0);
      expect(simplified.last.x, 10);
    });

    test('VectorInkingPainter.shouldRepaint optimizes repaints', () {
      final p1 = VectorInkingPainter(strokes: []);
      final p2 = VectorInkingPainter(strokes: []);
      expect(p1.shouldRepaint(p2), isFalse);

      final stroke = VectorInkingStroke(
        id: 's1',
        points: [const VectorInkingPoint(x: 1, y: 1, timestampMs: 0)],
        color: Colors.blue,
        strokeWidth: 2.0,
      );
      final p3 = VectorInkingPainter(strokes: [stroke]);
      expect(p3.shouldRepaint(p1), isTrue);
    });

    testWidgets('Stylus drawing records PointerDeviceKind.stylus and pressure in strokes', (tester) async {
      List<VectorInkingStroke>? capturedStrokes;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 400,
            height: 600,
            child: VectorInkingCanvas(
              onStrokesUpdated: (strokes) => capturedStrokes = strokes,
            ),
          ),
        ),
      ));

      final stylusGesture = await tester.startGesture(
        const Offset(120, 220),
        pointer: 1,
        kind: PointerDeviceKind.stylus,
      );
      await tester.pump();
      await stylusGesture.moveBy(const Offset(30, 40));
      await tester.pump();
      await stylusGesture.up();
      await tester.pumpAndSettle();

      expect(capturedStrokes, isNotNull);
      expect(capturedStrokes!.length, 1);
      expect(capturedStrokes!.first.deviceKind, PointerDeviceKind.stylus);
    });

    testWidgets('Palm rejection rejects accidental touch down while stylus is active', (tester) async {
      List<VectorInkingStroke>? capturedStrokes;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 400,
            height: 600,
            child: VectorInkingCanvas(
              enablePalmRejection: true,
              onStrokesUpdated: (strokes) => capturedStrokes = strokes,
            ),
          ),
        ),
      ));

      // Stylus begins writing
      final stylusGesture = await tester.startGesture(
        const Offset(100, 150),
        pointer: 1,
        kind: PointerDeviceKind.stylus,
      );
      await tester.pump();

      // Accidental palm touch down concurrently
      final palmGesture = await tester.startGesture(
        const Offset(250, 350),
        pointer: 2,
        kind: PointerDeviceKind.touch,
      );
      await tester.pump();
      await palmGesture.moveBy(const Offset(20, 20));
      await tester.pump();
      await palmGesture.up();
      await tester.pump();

      // Finish stylus stroke
      await stylusGesture.moveBy(const Offset(40, 40));
      await tester.pump();
      await stylusGesture.up();
      await tester.pumpAndSettle();

      // Palm stroke was rejected; only 1 stroke exists
      expect(capturedStrokes, isNotNull);
      expect(capturedStrokes!.length, 1);
      expect(capturedStrokes!.first.deviceKind, PointerDeviceKind.stylus);
    });

    testWidgets('Stylus-only mode completely ignores finger touches', (tester) async {
      List<VectorInkingStroke>? capturedStrokes;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 400,
            height: 600,
            child: VectorInkingCanvas(
              stylusOnlyMode: true,
              onStrokesUpdated: (strokes) => capturedStrokes = strokes,
            ),
          ),
        ),
      ));

      final fingerTouch = await tester.startGesture(
        const Offset(100, 200),
        pointer: 1,
        kind: PointerDeviceKind.touch,
      );
      await tester.pump();
      await fingerTouch.moveBy(const Offset(30, 30));
      await tester.pump();
      await fingerTouch.up();
      await tester.pumpAndSettle();

      expect(capturedStrokes, isNull);
    });

    testWidgets('Header toggle toggles S-Pen only mode', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 400,
            height: 600,
            child: VectorInkingCanvas(),
          ),
        ),
      ));

      expect(find.text('Tümü'), findsOneWidget);
      await tester.tap(find.byKey(const Key('inking_stylus_toggle')));
      await tester.pumpAndSettle();

      expect(find.text('S-Pen'), findsOneWidget);
    });

    test('VectorInkingPoint and VectorInkingStroke JSON serialization preserves stylus fields', () {
      const pt = VectorInkingPoint(
        x: 45.5,
        y: 89.2,
        timestampMs: 12345678,
        pressure: 0.72,
        tilt: 0.15,
        deviceKind: PointerDeviceKind.stylus,
      );
      final json = pt.toJson();
      expect(json['x'], 45.5);
      expect(json['p'], 0.72);
      expect(json['tilt'], 0.15);
      expect(json['kind'], 'stylus');

      final stroke = VectorInkingStroke(
        id: 's_test',
        points: [pt],
        color: Colors.cyan,
        strokeWidth: 3.5,
        deviceKind: PointerDeviceKind.stylus,
      );
      final strokeJson = stroke.toJson();
      expect(strokeJson['id'], 's_test');
      expect(strokeJson['kind'], 'stylus');
    });

    test('StylusTrajectoryPredictor calculates forward low-latency point along velocity vector', () {
      const p1 = VectorInkingPoint(
        x: 10.0,
        y: 20.0,
        timestampMs: 1000,
        deviceKind: PointerDeviceKind.stylus,
      );
      const p2 = VectorInkingPoint(
        x: 20.0,
        y: 40.0,
        timestampMs: 1016,
        deviceKind: PointerDeviceKind.stylus,
      );

      // Single point returns null
      expect(StylusTrajectoryPredictor.predictNextPoint([p1]), isNull);

      // Two points computes forward predicted point
      final predicted = StylusTrajectoryPredictor.predictNextPoint([p1, p2], predictionFactor: 0.5);
      expect(predicted, isNotNull);
      expect(predicted!.isPredicted, isTrue);
      // vx = (20 - 10) / 16 = 0.625; predX = 20 + 0.625 * 8 = 25.0
      expect(predicted.x, closeTo(25.0, 0.01));
      // vy = (40 - 20) / 16 = 1.25; predY = 40 + 1.25 * 8 = 50.0
      expect(predicted.y, closeTo(50.0, 0.01));
      expect(predicted.deviceKind, equals(PointerDeviceKind.stylus));
    });

    testWidgets('Stylus drawing utilizes forward prediction during motion and purges predicted point on stroke commit', (tester) async {
      List<VectorInkingStroke>? finishedStrokes;

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SizedBox(
            width: 400,
            height: 600,
            child: VectorInkingCanvas(
              enableStylusPrediction: true,
              onStrokesUpdated: (strokes) => finishedStrokes = strokes,
            ),
          ),
        ),
      ));

      final stylusGesture = await tester.startGesture(
        const Offset(100, 150),
        pointer: 7,
        kind: PointerDeviceKind.stylus,
      );
      await tester.pump();

      await stylusGesture.moveBy(const Offset(30, 30));
      await tester.pump();
      await stylusGesture.moveBy(const Offset(30, 30));
      await tester.pump();

      await stylusGesture.up();
      await tester.pumpAndSettle();

      expect(finishedStrokes, isNotNull);
      expect(finishedStrokes!.length, 1);
      // Ensure all saved stroke points have isPredicted == false
      for (final pt in finishedStrokes!.first.points) {
        expect(pt.isPredicted, isFalse);
      }
    });
  });
}

