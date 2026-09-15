import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late HapticFeedbackService hapticService;

  setUp(() {
    hapticService = HapticFeedbackService();
    hapticService.isEnabled = true;
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
  });
}
