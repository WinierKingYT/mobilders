import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late HapticFeedbackService hapticService;

  setUp(() {
    hapticService = HapticFeedbackService();
    hapticService.isEnabled = true;
    hapticService.throttleIntervalMs = 0;
    hapticService.clearHistory();
    hapticService.testListener = null;
  });

  group('HapticFeedbackService Tests', () {
    test('keyPress triggers light impact and appends to history', () async {
      await hapticService.keyPress();
      expect(hapticService.triggeredHistory.length, 1);
      expect(hapticService.triggeredHistory.first, HapticType.lightImpact);
    });

    test('stepSuccess triggers medium impact for celebratory feel', () async {
      await hapticService.stepSuccess();
      expect(hapticService.triggeredHistory.length, 1);
      expect(hapticService.triggeredHistory.first, HapticType.mediumImpact);
    });

    test('stepError triggers heavy impact warning', () async {
      await hapticService.stepError();
      expect(hapticService.triggeredHistory.length, 1);
      expect(hapticService.triggeredHistory.first, HapticType.heavyImpact);
    });

    test('selectionClick, modeSwitch, and clearAction trigger correct haptics', () async {
      await hapticService.selectionClick();
      await hapticService.modeSwitch();
      await hapticService.clearAction();

      expect(hapticService.triggeredHistory, [
        HapticType.selectionClick,
        HapticType.mediumImpact,
        HapticType.heavyImpact,
      ]);
    });

    test('Disabled mode suppresses haptic events without crashing', () async {
      hapticService.isEnabled = false;
      await hapticService.keyPress();
      await hapticService.stepSuccess();
      await hapticService.stepError();

      expect(hapticService.triggeredHistory, isEmpty);
    });

    test('testListener receives real-time event notifications', () async {
      final List<HapticType> receivedEvents = [];
      hapticService.testListener = (type) => receivedEvents.add(type);

      await hapticService.keyPress();
      await hapticService.stepSuccess();

      expect(receivedEvents, [HapticType.lightImpact, HapticType.mediumImpact]);
    });

    test('triggeredHistory is strictly bounded to maxHistoryLength to prevent memory leak', () async {
      for (int i = 0; i < 150; i++) {
        await hapticService.keyPress();
      }

      expect(hapticService.triggeredHistory.length, HapticFeedbackService.maxHistoryLength);
      expect(hapticService.triggeredHistory.length, 100);
    });
  });

  group('Haptic Throttling & Hardware Protection Tests', () {
    setUp(() {
      hapticService.throttleIntervalMs = 40;
      hapticService.clearHistory();
    });

    test('Rapid successive pulses within 40ms are throttled to protect hardware', () async {
      for (int i = 0; i < 10; i++) {
        await hapticService.keyPress();
      }

      expect(hapticService.triggeredHistory.length, 1);
      expect(hapticService.throttledCount, 9);
    });

    test('Pulses spaced apart by >= 40ms are all successfully triggered', () async {
      await hapticService.keyPress();
      await Future<void>.delayed(const Duration(milliseconds: 50));
      await hapticService.keyPress();
      await Future<void>.delayed(const Duration(milliseconds: 50));
      await hapticService.keyPress();

      expect(hapticService.triggeredHistory.length, 3);
      expect(hapticService.throttledCount, 0);
    });

    test('Critical error feedback bypasses throttling window', () async {
      await hapticService.keyPress();
      await hapticService.stepError(force: true);

      expect(hapticService.triggeredHistory.length, 2);
      expect(hapticService.triggeredHistory.last, HapticType.heavyImpact);
    });

    test('Setting throttleIntervalMs to 0 disables throttling', () async {
      hapticService.throttleIntervalMs = 0;
      for (int i = 0; i < 5; i++) {
        await hapticService.keyPress();
      }

      expect(hapticService.triggeredHistory.length, 5);
      expect(hapticService.throttledCount, 0);
    });
  });
}
