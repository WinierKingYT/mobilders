import 'dart:ui' show PointerDeviceKind;
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

    test('Stage 69: PalmRejectionFilter thresholding and device kind checks', () {
      // Small touch contact -> Normal finger, NOT palm
      const normalTouch = PointerDownEvent(
        kind: PointerDeviceKind.touch,
        size: 0.1,
        radiusMajor: 8.0,
        radiusMinor: 7.0,
      );
      expect(PalmRejectionFilter.isPalmTouch(normalTouch), isFalse);

      // Large contact area (>0.4 size) -> Palm touch
      const largeSizeTouch = PointerDownEvent(
        kind: PointerDeviceKind.touch,
        size: 0.55,
        radiusMajor: 12.0,
      );
      expect(PalmRejectionFilter.isPalmTouch(largeSizeTouch), isTrue);

      // Large contact radius (>25.0 dp) -> Palm touch
      const largeRadiusTouch = PointerDownEvent(
        kind: PointerDeviceKind.touch,
        size: 0.2,
        radiusMajor: 32.0,
      );
      expect(PalmRejectionFilter.isPalmTouch(largeRadiusTouch), isTrue);

      // Stylus input is never rejected as palm regardless of size or radius
      const stylusEvent = PointerDownEvent(
        kind: PointerDeviceKind.stylus,
        size: 0.8,
        radiusMajor: 40.0,
      );
      expect(PalmRejectionFilter.isPalmTouch(stylusEvent), isFalse);
    });

    testWidgets('Stage 69: Palm Rejection Benchmark - Large contact area ignores stroke creation', (tester) async {
      List<VectorInkingStroke> receivedStrokes = [];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              height: 500,
              child: VectorInkingCanvas(
                enablePalmRejection: true,
                onStrokesUpdated: (strokes) => receivedStrokes = strokes,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Dispatch accidental palm press event
      await tester.sendEventToBinding(
        const PointerDownEvent(
          pointer: 10,
          position: Offset(120, 200),
          kind: PointerDeviceKind.touch,
          size: 0.65,
          radiusMajor: 38.0,
        ),
      );
      await tester.pump();

      await tester.sendEventToBinding(
        const PointerMoveEvent(
          pointer: 10,
          position: Offset(140, 220),
          kind: PointerDeviceKind.touch,
          size: 0.65,
        ),
      );
      await tester.pump();

      await tester.sendEventToBinding(
        const PointerUpEvent(
          pointer: 10,
          position: Offset(140, 220),
          kind: PointerDeviceKind.touch,
        ),
      );
      await tester.pump();

      // Large palm contact must be completely discarded
      expect(receivedStrokes, isEmpty);
    });

    testWidgets('Stage 69: Multi-touch Pinch & Palm Isolation freezes inking', (tester) async {
      List<VectorInkingStroke> receivedStrokes = [];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              height: 500,
              child: VectorInkingCanvas(
                enablePalmRejection: true,
                onStrokesUpdated: (strokes) => receivedStrokes = strokes,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // First finger touches down
      final g1 = await tester.startGesture(const Offset(100, 100), pointer: 1);
      await tester.pump();

      // Second finger / resting palm touches down simultaneously
      final g2 = await tester.startGesture(const Offset(200, 200), pointer: 2);
      await tester.pump();

      // Moving while multi-touch active
      await g1.moveBy(const Offset(30, 30));
      await g2.moveBy(const Offset(-20, -20));
      await tester.pump();

      // Lift both fingers
      await g1.up();
      await g2.up();
      await tester.pump();

      // Multi-touch must cancel active touch stroke and produce 0 valid strokes
      expect(receivedStrokes, isEmpty);

      // Subsequent single touch should work normally
      final g3 = await tester.startGesture(const Offset(150, 150), pointer: 3);
      await tester.pump();
      await g3.moveBy(const Offset(20, 20));
      await tester.pump();
      await g3.up();
      await tester.pump();

      expect(receivedStrokes.length, 1);
    });
  });
}
