import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';

void main() {
  group('MathTouchpad Widget Tests', () {
    late TextEditingController controller;

    setUp(() {
      controller = TextEditingController();
    });

    tearDown(() {
      controller.dispose();
    });

    testWidgets('Tapping x, +, and 2 inserts correct text into controller', (WidgetTester tester) async {
      bool submitted = false;
      InputMode currentMode = InputMode.touchpad;

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: currentMode,
              onModeChanged: (mode) => currentMode = mode,
              onSubmit: () => submitted = true,
            ),
          ),
        ),
      );

      // Find and tap 'x'
      await tester.tap(find.widgetWithText(ElevatedButton, 'x'));
      await tester.pump();
      expect(controller.text, 'x');

      // Find and tap '+'
      await tester.tap(find.widgetWithText(ElevatedButton, '+'));
      await tester.pump();
      expect(controller.text, 'x + ');

      // Find and tap '2'
      await tester.tap(find.widgetWithText(ElevatedButton, '2'));
      await tester.pump();
      expect(controller.text, 'x + 2');

      // Tap submit button (arrow forward)
      await tester.tap(find.byIcon(Icons.arrow_forward_rounded));
      await tester.pump();
      expect(submitted, isTrue);
    });

    testWidgets('Tapping x² inserts x^2 and backspace removes token', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: InputMode.touchpad,
              onModeChanged: (_) {},
              onSubmit: () {},
            ),
          ),
        ),
      );

      // Tap 'x²'
      await tester.tap(find.widgetWithText(ElevatedButton, 'x²'));
      await tester.pump();
      expect(controller.text, 'x^2');

      // Tap backspace
      await tester.tap(find.byIcon(Icons.backspace_outlined));
      await tester.pump();
      expect(controller.text, '');
    });

    testWidgets('Tapping sqrt inserts sqrt( and Clear clears input', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: InputMode.touchpad,
              onModeChanged: (_) {},
              onSubmit: () {},
            ),
          ),
        ),
      );

      await tester.tap(find.widgetWithText(ElevatedButton, '√'));
      await tester.pump();
      expect(controller.text, 'sqrt(');

      // Tap 'C'
      await tester.tap(find.widgetWithText(ElevatedButton, 'C'));
      await tester.pump();
      expect(controller.text, '');
    });

    testWidgets('Mode switch button toggles between Touchpad and Virtual Keyboard', (WidgetTester tester) async {
      InputMode mode = InputMode.touchpad;

      await tester.pumpWidget(
        StatefulBuilder(
          builder: (context, setState) {
            return MaterialApp(
              theme: AppTheme.darkTheme,
              home: Scaffold(
                body: MathTouchpad(
                  controller: controller,
                  inputMode: mode,
                  onModeChanged: (newMode) {
                    setState(() {
                      mode = newMode;
                    });
                  },
                  onSubmit: () {},
                ),
              ),
            );
          },
        ),
      );

      // Initial state: keypad grid visible
      expect(find.widgetWithText(ElevatedButton, 'x'), findsOneWidget);

      // Tap keyboard switch icon
      await tester.tap(find.byIcon(Icons.keyboard_outlined).first);
      await tester.pumpAndSettle();

      // Keyboard mode active: TextField visible
      expect(find.byType(TextField), findsOneWidget);
      expect(find.widgetWithText(ElevatedButton, 'x'), findsNothing);

      // Tap touchpad grid switch icon
      await tester.tap(find.byIcon(Icons.grid_view_rounded));
      await tester.pumpAndSettle();

      // Back to keypad grid
      expect(find.widgetWithText(ElevatedButton, 'x'), findsOneWidget);
    });

    testWidgets('Tapping ± inserts +- and backspace removes entire +- token', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: InputMode.touchpad,
              onModeChanged: (_) {},
              onSubmit: () {},
            ),
          ),
        ),
      );

      // Tap '±'
      await tester.tap(find.widgetWithText(ElevatedButton, '±'));
      await tester.pump();
      expect(controller.text, '+-');

      // Tap backspace
      await tester.tap(find.byIcon(Icons.backspace_outlined));
      await tester.pump();
      expect(controller.text, '');
    });

    testWidgets('Cursor between matching parentheses removes both brackets on backspace', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: InputMode.touchpad,
              onModeChanged: (_) {},
              onSubmit: () {},
            ),
          ),
        ),
      );

      // Set text to "()" with cursor between: offset 1
      controller.value = const TextEditingValue(
        text: '()',
        selection: TextSelection.collapsed(offset: 1),
      );

      // Tap backspace
      await tester.tap(find.byIcon(Icons.backspace_outlined));
      await tester.pump();
      expect(controller.text, '');
      expect(controller.selection.baseOffset, 0);
    });

    testWidgets('Tapping ( with text selected wraps the selection in parentheses', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: InputMode.touchpad,
              onModeChanged: (_) {},
              onSubmit: () {},
            ),
          ),
        ),
      );

      // Set text to "x + 2" with entire text selected
      controller.value = const TextEditingValue(
        text: 'x + 2',
        selection: TextSelection(baseOffset: 0, extentOffset: 5),
      );

      // Tap '('
      await tester.tap(find.widgetWithText(ElevatedButton, '('));
      await tester.pump();
      expect(controller.text, '(x + 2)');
      expect(controller.selection.baseOffset, 7);
    });

    testWidgets('Highlighted token from dual coding illuminates matching touchpad keys', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: MathTouchpad(
              controller: controller,
              inputMode: InputMode.touchpad,
              onModeChanged: (_) {},
              onSubmit: () {},
              highlightedToken: '- 3',
            ),
          ),
        ),
      );

      final minusKey = find.byKey(const Key('touchpad_key_-'));
      final threeKey = find.byKey(const Key('touchpad_key_3'));

      expect(minusKey, findsOneWidget);
      expect(threeKey, findsOneWidget);

      final minusBtn = tester.widget<ElevatedButton>(minusKey);
      final style = minusBtn.style;
      expect(style?.backgroundColor?.resolve({}), const Color(0xFF0369A1));
    });
  });
}

