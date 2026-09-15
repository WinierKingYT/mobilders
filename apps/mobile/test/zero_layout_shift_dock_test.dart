import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';
import 'package:personal_learning_engine/ui/features/touchpad/zero_layout_shift_dock.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  Widget buildTestableWidget({
    InputMode mode = InputMode.touchpad,
    ValueChanged<InputMode>? onModeChanged,
    VoidCallback? onToggleZen,
    bool isZenActive = false,
    Widget? child,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: Column(
          children: [
            const Expanded(child: Center(child: Text('Equation Viewport'))),
            ZeroLayoutShiftDock(
              currentMode: mode,
              onModeChanged: onModeChanged ?? (_) {},
              onToggleZenMode: onToggleZen,
              isZenModeActive: isZenActive,
              child: child ?? Container(key: const ValueKey('dock_content'), height: 260),
            ),
          ],
        ),
      ),
    );
  }

  group('ZeroLayoutShiftDock Widget Tests', () {
    testWidgets('Dock maintains constant height and renders ribbon items', (tester) async {
      await tester.pumpWidget(buildTestableWidget());
      await tester.pumpAndSettle();

      final dockFinder = find.byType(ZeroLayoutShiftDock);
      expect(dockFinder, findsOneWidget);

      final container = tester.widget<Container>(find.descendant(
        of: dockFinder,
        matching: find.byType(Container).first,
      ));
      expect(container.constraints?.maxHeight, 310.0);

      // Verify ribbon pills exist
      expect(find.text('Touchpad'), findsOneWidget);
      expect(find.text('Klavye'), findsOneWidget);
      expect(find.text('El Yazısı'), findsOneWidget);
    });

    testWidgets('Tapping mode pill switches input mode and triggers haptics', (tester) async {
      InputMode selectedMode = InputMode.touchpad;

      await tester.pumpWidget(buildTestableWidget(
        mode: selectedMode,
        onModeChanged: (newMode) => selectedMode = newMode,
      ));
      await tester.pumpAndSettle();

      // Tap Klavye pill
      await tester.tap(find.text('Klavye'));
      await tester.pumpAndSettle();

      expect(selectedMode, InputMode.virtualKeyboard);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('AnimatedSwitcher handles child transition smoothly', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        mode: InputMode.touchpad,
        child: const Text('Touchpad Screen', key: ValueKey('touchpad')),
      ));
      await tester.pumpAndSettle();
      expect(find.text('Touchpad Screen'), findsOneWidget);

      // Switch to Inking
      await tester.pumpWidget(buildTestableWidget(
        mode: InputMode.inkingCanvas,
        child: const Text('Inking Canvas Screen', key: ValueKey('inking')),
      ));

      // AnimatedSwitcher should animate between children
      await tester.pump(const Duration(milliseconds: 100));
      expect(find.byType(AnimatedSwitcher), findsOneWidget);

      await tester.pumpAndSettle();
      expect(find.text('Inking Canvas Screen'), findsOneWidget);
    });

    testWidgets('Tapping Zen pill triggers onToggleZenMode and modeSwitch haptic', (tester) async {
      bool zenToggled = false;

      await tester.pumpWidget(buildTestableWidget(
        onToggleZen: () => zenToggled = true,
      ));
      await tester.pumpAndSettle();

      expect(find.text('Zen'), findsOneWidget);
      await tester.tap(find.text('Zen'));
      await tester.pumpAndSettle();

      expect(zenToggled, isTrue);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.mediumImpact), isTrue);
    });

    testWidgets('Zen active state reflects cyan highlight badge', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        isZenActive: true,
        onToggleZen: () {},
      ));
      await tester.pumpAndSettle();

      final zenText = tester.widget<Text>(find.text('Zen'));
      expect(zenText.style?.color, const Color(0xFF38BDF8));
    });
  });
}
