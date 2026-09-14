import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/localization.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';
import 'package:personal_learning_engine/ui/features/accessibility/dyscalculia_helpers.dart';
import 'package:personal_learning_engine/ui/features/accessibility/tunnel_focus_mode.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';
import 'package:personal_learning_engine/ui/features/touchpad/vector_inking_canvas.dart';

void main() {
  group('Accessibility & Inking Widget Tests', () {
    testWidgets('TunnelFocusContainer renders banner when disabled and obsidian black when enabled', (tester) async {
      bool tunnelEnabled = false;

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                return TunnelFocusContainer(
                  isTunnelModeEnabled: tunnelEnabled,
                  onToggleTunnelMode: () => setState(() => tunnelEnabled = !tunnelEnabled),
                  activeGoalText: 'Hedef: x^2 - 5x + 6 = 0',
                  child: const Text('Problem İçeriği'),
                );
              },
            ),
          ),
        ),
      );

      // Initially disabled: banner visible
      expect(find.text('DEHB / Dikkat Odaklama Modu'), findsOneWidget);
      expect(find.text('Tünel Görüşünü Aç'), findsOneWidget);

      // Tap to toggle tunnel mode
      await tester.tap(find.text('Tünel Görüşünü Aç'));
      await tester.pumpAndSettle();

      // Now enabled: Header shows active goal text with pure white text
      expect(find.text('Hedef: x^2 - 5x + 6 = 0'), findsOneWidget);
      expect(find.byIcon(Icons.fullscreen_exit_rounded), findsOneWidget);
    });

    testWidgets('VisualNumberLine renders with position label and painter', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: VisualNumberLine(
              currentPosition: 4.0,
              targetPosition: 6.0,
              minRange: -10.0,
              maxRange: 10.0,
            ),
          ),
        ),
      );

      expect(find.text('Görsel Sayı Çizgisi (Diskalkuli Desteği)'), findsOneWidget);
      expect(find.text('Konum: 4'), findsOneWidget);
      expect(find.byType(CustomPaint), findsWidgets);
    });

    testWidgets('ColorCodedAlgebraicExpression renders colored term badges', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ColorCodedAlgebraicExpression(
              expression: 'x^2 + 6x - 2 = 0',
            ),
          ),
        ),
      );

      expect(find.text('x^2'), findsOneWidget);
      expect(find.text('+'), findsOneWidget);
      expect(find.text('6x'), findsOneWidget);
      expect(find.text('='), findsOneWidget);
      expect(find.text('0'), findsOneWidget);
    });

    testWidgets('MathTouchpad switches to inkingCanvas mode and renders VectorInkingCanvas', (tester) async {
      final controller = TextEditingController();
      InputMode currentMode = InputMode.touchpad;

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                return MathTouchpad(
                  controller: controller,
                  inputMode: currentMode,
                  onModeChanged: (newMode) => setState(() => currentMode = newMode),
                  onSubmit: () {},
                );
              },
            ),
          ),
        ),
      );

      // Initial touchpad mode
      expect(find.widgetWithText(ElevatedButton, 'x'), findsOneWidget);

      // Tap 'El Yazısı Kanvası' switch button
      await tester.tap(find.text('El Yazısı Kanvası'));
      await tester.pumpAndSettle();

      // Inking canvas visible
      expect(find.byType(VectorInkingCanvas), findsOneWidget);
      expect(find.text('Vektörel El Yazısı (Multimodal Inking)'), findsOneWidget);

      // Switch back to touchpad
      await tester.tap(find.byIcon(Icons.grid_view_rounded));
      await tester.pumpAndSettle();
      expect(find.widgetWithText(ElevatedButton, 'x'), findsOneWidget);
    });

    test('AppLocalization language and curriculum switching', () {
      AppLocalization.setLanguage('tr');
      expect(AppLocalization.text('mode_inking'), 'El Yazısı Kanvası');

      AppLocalization.setLanguage('en');
      expect(AppLocalization.text('mode_inking'), 'Freehand Inking Canvas');

      AppLocalization.setCurriculum(CurriculumType.ibAA);
      expect(AppLocalization.currentCurriculum.code, 'IB_AA');
      expect(AppLocalization.currentCurriculum.displayName, contains('Analysis & Approaches'));

      AppLocalization.setCurriculum(CurriculumType.meb);
      expect(AppLocalization.currentCurriculum.code, 'MEB');
    });
  });
}
