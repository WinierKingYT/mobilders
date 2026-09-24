import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/scratchpad_overlay.dart';

void main() {
  testWidgets('ScratchpadOverlay renders controls and responds to gesture interactions', (tester) async {
    bool closed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ScratchpadOverlay(
            onClose: () => closed = true,
          ),
        ),
      ),
    );

    // Verify Title and Icons
    expect(find.text('Serbest Karalama (Scratchpad)'), findsOneWidget);
    expect(find.byIcon(Icons.undo), findsOneWidget);
    expect(find.byIcon(Icons.delete_outline), findsOneWidget);
    expect(find.byIcon(Icons.close), findsOneWidget);
    expect(find.text('İnce'), findsOneWidget);

    // Simulate drawing gestures on the canvas
    final gestureTarget = find.byType(GestureDetector).at(1);
    await tester.drag(gestureTarget, const Offset(50, 50));
    await tester.pumpAndSettle();

    // Undo button should become active
    await tester.tap(find.byIcon(Icons.undo));
    await tester.pumpAndSettle();

    // Toggle stroke width
    await tester.tap(find.text('İnce'));
    await tester.pumpAndSettle();
    expect(find.text('Kalın'), findsOneWidget);

    // Tap close button
    await tester.tap(find.byIcon(Icons.close));
    await tester.pumpAndSettle();
    expect(closed, isTrue);
  });

  testWidgets('ScratchpadOverlay enforces 50-stroke ring buffer limit', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ScratchpadOverlay(
            onClose: () {},
          ),
        ),
      ),
    );

    final gestureTarget = find.byKey(const Key('scratchpad_drawing_area'));

    // Draw 55 strokes
    for (int i = 0; i < 55; i++) {
      await tester.drag(gestureTarget, Offset(10.0 + (i % 10) * 5, 10.0 + (i % 10) * 5));
      await tester.pump();
    }
    await tester.pumpAndSettle();

    // Verify CustomPaint has exactly 50 strokes (ring buffer dropped the oldest 5)
    final customPaint = tester.widget<CustomPaint>(find.descendant(
      of: find.byKey(const Key('scratchpad_drawing_area')),
      matching: find.byType(CustomPaint),
    ));
    final painter = customPaint.painter as ScratchpadPainter;
    expect(painter.strokes.length, 50);
  });

  testWidgets('ScratchpadOverlay supports undo and redo stack', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ScratchpadOverlay(
            onClose: () {},
          ),
        ),
      ),
    );

    final gestureTarget = find.byKey(const Key('scratchpad_drawing_area'));

    // Draw 2 strokes
    await tester.drag(gestureTarget, const Offset(30, 30));
    await tester.pumpAndSettle();
    await tester.drag(gestureTarget, const Offset(40, 40));
    await tester.pumpAndSettle();

    var customPaint = tester.widget<CustomPaint>(find.descendant(
      of: find.byKey(const Key('scratchpad_drawing_area')),
      matching: find.byType(CustomPaint),
    ));
    var painter = customPaint.painter as ScratchpadPainter;
    expect(painter.strokes.length, 2);

    // Undo 1 stroke
    await tester.tap(find.byIcon(Icons.undo));
    await tester.pumpAndSettle();

    customPaint = tester.widget<CustomPaint>(find.descendant(
      of: find.byKey(const Key('scratchpad_drawing_area')),
      matching: find.byType(CustomPaint),
    ));
    painter = customPaint.painter as ScratchpadPainter;
    expect(painter.strokes.length, 1);

    // Redo the stroke
    await tester.tap(find.byKey(const Key('scratchpad_redo_button')));
    await tester.pumpAndSettle();

    customPaint = tester.widget<CustomPaint>(find.descendant(
      of: find.byKey(const Key('scratchpad_drawing_area')),
      matching: find.byType(CustomPaint),
    ));
    painter = customPaint.painter as ScratchpadPainter;
    expect(painter.strokes.length, 2);
  });

  testWidgets('ScratchpadOverlay pass-through mode enables tapping underlying widgets via IgnorePointer', (tester) async {
    bool underlyingButtonClicked = false;
    bool? passThroughState;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Stack(
            children: [
              // Underlying widget that should be clickable in pass-through mode
              Center(
                child: ElevatedButton(
                  key: const Key('underlying_action_button'),
                  onPressed: () => underlyingButtonClicked = true,
                  child: const Text('Alttaki Formül Butonu'),
                ),
              ),
              // Scratchpad Overlay on top
              ScratchpadOverlay(
                onClose: () {},
                onPassThroughChanged: (val) => passThroughState = val,
              ),
            ],
          ),
        ),
      ),
    );

    // In normal drawing mode, tapping center should NOT hit the button because Scratchpad drawing area catches it
    await tester.tapAt(tester.getCenter(find.byKey(const Key('underlying_action_button'))));
    await tester.pumpAndSettle();
    expect(underlyingButtonClicked, isFalse);

    // Toggle Pass-Through Mode
    await tester.tap(find.byKey(const Key('scratchpad_passthrough_toggle')));
    await tester.pumpAndSettle();

    expect(passThroughState, isTrue);
    expect(find.text('Geçirgen Mod'), findsOneWidget);

    // Now tap the button again: IgnorePointer passes touch right through to the underlying button
    await tester.tapAt(tester.getCenter(find.byKey(const Key('underlying_action_button'))));
    await tester.pumpAndSettle();
    expect(underlyingButtonClicked, isTrue);
  });
}
