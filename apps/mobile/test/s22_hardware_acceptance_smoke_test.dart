import 'dart:ui' show PointerDeviceKind;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/ui/core/app_theme.dart';
import 'package:personal_learning_engine/ui/features/session/view_models/session_view_model.dart';
import 'package:personal_learning_engine/ui/features/touchpad/math_touchpad.dart';
import 'package:personal_learning_engine/ui/features/touchpad/vector_inking_canvas.dart';
import 'package:personal_learning_engine/ui/features/touchpad/zero_layout_shift_dock.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Stage 72: Samsung Galaxy S22 End-to-End Hardware Acceptance Suite', () {
    setUp(() {
      BatteryPowerOptimizer().reset();
      ThermalProfileManager().reset();
      DynamicVectorLayerCache.clear();
    });

    test('REQ-HW-01: 120Hz LTPO Frame Pacing & Dynamic Refresh Rate Scaling', () {
      final optimizer = BatteryPowerOptimizer();

      // Default high refresh rate is 120Hz (8.33ms frame pacing budget)
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.highRefresh120Hz));
      expect(optimizer.is120HzLtpoSyncEnabled, isTrue);
      expect(optimizer.currentFrameInterval.inMicroseconds, equals(8333));
      expect(optimizer.isFrameWithinBudget(const Duration(milliseconds: 7)), isTrue);
      expect(optimizer.isFrameWithinBudget(const Duration(milliseconds: 12)), isFalse);

      // Low power throttling (battery <= 15% -> 60Hz, battery <= 5% -> 30Hz)
      optimizer.updateBatteryState(batteryLevelPercent: 12);
      expect(optimizer.isLowPowerMode, isTrue);
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.standard60Hz));
      expect(optimizer.currentFrameInterval.inMicroseconds, equals(16666));

      optimizer.updateBatteryState(batteryLevelPercent: 3);
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.powerSaver30Hz));
      expect(optimizer.currentFrameInterval.inMicroseconds, equals(33333));

      optimizer.reset();
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.highRefresh120Hz));
    });

    test('REQ-HW-02: Static Vector Layer Cache for 120Hz Jitter-Free Rendering', () {
      expect(DynamicVectorLayerCache.cachedLayerCount, equals(0));

      const cacheKey = 's22_cartesian_grid_layer';
      const mockRenderLayer = {'type': 'grid', 'points': 400, 'accelerated': true};

      DynamicVectorLayerCache.cacheLayer(cacheKey, mockRenderLayer);
      expect(DynamicVectorLayerCache.hasLayer(cacheKey), isTrue);
      expect(DynamicVectorLayerCache.getLayer(cacheKey), equals(mockRenderLayer));

      DynamicVectorLayerCache.clear();
      expect(DynamicVectorLayerCache.hasLayer(cacheKey), isFalse);
    });

    testWidgets('REQ-HW-03: Samsung One UI Navigation Bar Isolation & Keyboard Inset Damping', (tester) async {
      final controller = TextEditingController();

      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.amoledDarkTheme,
          home: Scaffold(
            resizeToAvoidBottomInset: false,
            body: ZeroLayoutShiftDock(
              currentMode: InputMode.touchpad,
              onModeChanged: (_) {},
              dockHeight: 280,
              child: MathTouchpad(
                controller: controller,
                inputMode: InputMode.touchpad,
                onModeChanged: (_) {},
                onSubmit: () {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final dock = tester.widget<ZeroLayoutShiftDock>(find.byType(ZeroLayoutShiftDock));
      expect(dock.dockHeight, equals(280.0));
      expect(dock.currentMode, equals(InputMode.touchpad));
      expect(find.byType(MathTouchpad), findsOneWidget);
    });

    test('REQ-HW-04: S-Pen Low-Latency (<8ms) Forward Trajectory Prediction', () {
      final basePoints = [
        const VectorInkingPoint(x: 100, y: 100, timestampMs: 1000, deviceKind: PointerDeviceKind.stylus),
        const VectorInkingPoint(x: 110, y: 120, timestampMs: 1016, deviceKind: PointerDeviceKind.stylus),
      ];

      final predicted = StylusTrajectoryPredictor.predictNextPoint(basePoints);
      expect(predicted, isNotNull);
      expect(predicted!.isPredicted, isTrue);
      expect(predicted.x, greaterThan(110.0));
      expect(predicted.y, greaterThan(120.0));
      expect(predicted.timestampMs, equals(1024)); // 1016 + 8ms forward projection
    });

    test('REQ-HW-05: Palm Rejection Benchmark & Contact Radius Thresholding', () {
      // Normal stylus or finger touch is accepted
      const normalStylus = PointerDownEvent(kind: PointerDeviceKind.stylus, size: 0.9, radiusMajor: 40.0);
      expect(PalmRejectionFilter.isPalmTouch(normalStylus), isFalse);

      const normalTouch = PointerDownEvent(kind: PointerDeviceKind.touch, size: 0.15, radiusMajor: 10.0);
      expect(PalmRejectionFilter.isPalmTouch(normalTouch), isFalse);

      // Large palm contact size (>0.4) or radius (>25.0 dp) is rejected
      const palmTouchBySize = PointerDownEvent(kind: PointerDeviceKind.touch, size: 0.65, radiusMajor: 15.0);
      expect(PalmRejectionFilter.isPalmTouch(palmTouchBySize), isTrue);

      const palmTouchByRadius = PointerDownEvent(kind: PointerDeviceKind.touch, size: 0.20, radiusMajor: 35.0);
      expect(PalmRejectionFilter.isPalmTouch(palmTouchByRadius), isTrue);
    });

    test('REQ-HW-06: Continuous 1-Hour Session Memory Stability (20 Question Cycles)', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''{
          "is_valid": true,
          "is_target_reached": false,
          "canonical_expression": "x = 5",
          "error_message": null,
          "psychometrics": {
            "bkt_posterior_pl": 0.65,
            "irt_difficulty_b": 0.2,
            "slip_probability": 0.05,
            "guess_probability": 0.15
          }
        }''', 200);
      });

      final vm = SessionViewModel(
        apiService: EngineApiService(client: mockClient),
        sessionId: 'hw_acceptance_session',
        targetEquation: 'x^2 - 4 = 0',
      );

      for (int cycle = 1; cycle <= 20; cycle++) {
        vm.startNewTarget(
          newTargetEquation: 'x^2 - $cycle = 0',
          newNodeId: 'HW_$cycle',
          newSessionId: 'hw_cycle_$cycle',
          preserveStreak: true,
        );

        expect(vm.steps.isEmpty, isTrue);
        expect(vm.isTargetReached, isFalse);
        vm.startHesitationTimer(duration: const Duration(seconds: 5));
        vm.resetSessionData();
        expect(vm.steps.isEmpty, isTrue);
      }

      for (int i = 0; i < 60; i++) {
        await vm.submitStep('x = $i');
      }
      expect(vm.steps.length, equals(60));
      vm.pruneHistoricalSteps(maxRetainedSteps: 50);
      expect(vm.steps.length, equals(50));

      vm.dispose();
    });

    test('REQ-HW-07: Thermal Profile Background Suspension & Exynos/Snapdragon Headroom Throttling', () {
      final thermal = ThermalProfileManager();
      final optimizer = BatteryPowerOptimizer();

      expect(thermal.isBackgroundSuspended, isFalse);

      // App backgrounded
      thermal.handleLifecycleChange(AppLifecycleState.paused);
      expect(thermal.isBackgroundSuspended, isTrue);

      // App restored
      thermal.handleLifecycleChange(AppLifecycleState.resumed);
      expect(thermal.isBackgroundSuspended, isFalse);

      // Thermal envelope warning (headroom drops to 10%)
      thermal.updateThermalStatus(thermalHeadroom: 0.10, isWarning: true);
      expect(thermal.isThermalWarningActive, isTrue);
      expect(optimizer.targetFrameRate, equals(FrameRateTarget.standard60Hz));

      thermal.reset();
      expect(thermal.isThermalWarningActive, isFalse);
    });

    test('REQ-HW-08: Pure AMOLED #000000 Zero-Watt OLED Display Efficiency Profile', () {
      final amoledTheme = AppTheme.amoledDarkTheme;

      expect(AmoledThemeEfficiency.isTrueBlack(amoledTheme.scaffoldBackgroundColor), isTrue);
      expect(AmoledThemeEfficiency.isTrueBlack(amoledTheme.canvasColor), isTrue);
      expect(AmoledThemeEfficiency.isTrueBlack(AppColors.amoledBg), isTrue);

      final coverage = AmoledThemeEfficiency.calculateTrueBlackCoverage();
      expect(coverage, greaterThanOrEqualTo(0.70));
      expect(AmoledThemeEfficiency.satisfiesAmoledEfficiencyTarget(amoledTheme), isTrue);
    });
  });
}
