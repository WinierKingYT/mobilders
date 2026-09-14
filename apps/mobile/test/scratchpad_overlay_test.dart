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
}
