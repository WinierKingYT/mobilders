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
  });
}
