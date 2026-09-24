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

    testWidgets('Multi-Screen Resolutions & Foldables & Tablets: Zero RenderFlex overflow', (tester) async {
      final resolutions = [
        const Size(320, 640),   // Küçük Ekran (Compact)
        const Size(412, 915),   // Samsung Galaxy S22 Dikey Mod
        const Size(800, 1280),  // Geniş Tablet Dikey Mod
        const Size(915, 412),   // Samsung Galaxy S22 Yatay Mod (Landscape)
        const Size(1280, 800),  // Tablet Yatay Mod (Landscape)
      ];

      final controller = TextEditingController();

      for (final size in resolutions) {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1.0;

        final errors = <FlutterErrorDetails>[];
        final oldHandler = FlutterError.onError;
        FlutterError.onError = (details) => errors.add(details);

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.darkTheme,
            home: Scaffold(
              body: SafeArea(
                child: Column(
                  children: [
                    Expanded(
                      child: TunnelFocusContainer(
                        isTunnelModeEnabled: false,
                        onToggleTunnelMode: () {},
                        activeGoalText: 'Hedef: x^2 - 5x + 6 = 0',
                        child: const SingleChildScrollView(
                          child: Column(
                            children: [
                              ColorCodedAlgebraicExpression(expression: 'x^2 + 6x - 2 = 0'),
                              VisualNumberLine(currentPosition: 2, targetPosition: 5),
                            ],
                          ),
                        ),
                      ),
                    ),
                    SizedBox(
                      height: size.height > 600 ? 300 : 200,
                      child: MathTouchpad(
                        controller: controller,
                        inputMode: InputMode.touchpad,
                        onModeChanged: (_) {},
                        onSubmit: () {},
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();

        FlutterError.onError = oldHandler;
        // Aşama 58 Kriteri: Sıfır piksel taşması (Zero RenderFlex overflow)
        expect(errors, isEmpty);
        expect(find.byType(ColorCodedAlgebraicExpression), findsOneWidget);
        expect(find.byType(MathTouchpad), findsOneWidget);
      }

      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    testWidgets('Landscape Mode Proportional Scaling & Canvas Verification', (tester) async {
      // Samsung Galaxy S22 Yatay Mod: 915x412
      tester.view.physicalSize = const Size(915, 412);
      tester.view.devicePixelRatio = 1.0;

      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    flex: 1,
                    child: VectorInkingCanvas(
                      onStrokesUpdated: (_) {},
                    ),
                  ),
                  Expanded(
                    flex: 1,
                    child: MathTouchpad(
                      controller: controller,
                      inputMode: InputMode.touchpad,
                      onModeChanged: (_) {},
                      onSubmit: () {},
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Aşama 58 Kriteri: Yatay modda kanvas ve klavye orantılı render denetimi
      expect(tester.takeException(), isNull);
      expect(find.byType(VectorInkingCanvas), findsOneWidget);
      expect(find.byType(MathTouchpad), findsOneWidget);

      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
  });
}
