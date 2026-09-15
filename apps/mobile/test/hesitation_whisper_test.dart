import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/hesitation_whisper_bubble.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  Widget buildTestableWidget({
    required String message,
    VoidCallback? onDismiss,
    VoidCallback? onTapAction,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: HesitationWhisperBubble(
          whisperMessage: message,
          onDismiss: onDismiss,
          onTapAction: onTapAction,
        ),
      ),
    );
  }

  group('HesitationWhisperBubble Widget Tests', () {
    testWidgets('renders whisper message text and icon', (tester) async {
      const message = 'Önce parantezin önündeki sayıya odaklanalım mı?';
      await tester.pumpWidget(buildTestableWidget(message: message));
      await tester.pumpAndSettle();

      expect(find.byType(HesitationWhisperBubble), findsOneWidget);
      expect(find.text(message), findsOneWidget);
      expect(find.byIcon(Icons.psychology_alt_rounded), findsOneWidget);
    });

    testWidgets('tapping dismiss triggers onDismiss and haptic feedback', (tester) async {
      bool dismissed = false;
      await tester.pumpWidget(buildTestableWidget(
        message: 'Küçük bir adımla başlayalım.',
        onDismiss: () => dismissed = true,
      ));
      await tester.pumpAndSettle();

      final dismissButton = find.byKey(const Key('hesitation_whisper_dismiss'));
      expect(dismissButton, findsOneWidget);

      await tester.tap(dismissButton);
      await tester.pumpAndSettle();

      expect(dismissed, isTrue);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('tapping text body triggers onTapAction', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(buildTestableWidget(
        message: 'Sabit sayıyı karşıya geçirelim mi?',
        onTapAction: () => tapped = true,
      ));
      await tester.pumpAndSettle();

      final textFinder = find.byKey(const Key('hesitation_whisper_text'));
      expect(textFinder, findsOneWidget);

      await tester.tap(textFinder);
      await tester.pumpAndSettle();

      expect(tapped, isTrue);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });
  });
}
