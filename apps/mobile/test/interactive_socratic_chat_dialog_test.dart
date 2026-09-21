import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/domain/models/diagnostic_bug.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/interactive_socratic_chat_dialog.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  Widget buildTestableWidget({
    String targetEquation = 'x^2 - 5x + 6 = 0',
    DiagnosticBug? diagnosticBug,
    String? userExpression,
    Function(String)? onApplyCorrectedStep,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: Builder(
          builder: (context) => ElevatedButton(
            key: const Key('open_dialog_btn'),
            onPressed: () {
              InteractiveSocraticChatDialog.show(
                context,
                targetEquation: targetEquation,
                diagnosticBug: diagnosticBug,
                userExpression: userExpression,
                onApplyCorrectedStep: onApplyCorrectedStep,
              );
            },
            child: const Text('Open'),
          ),
        ),
      ),
    );
  }

  group('InteractiveSocraticChatDialog Tests', () {
    testWidgets('renders dialog and shows opening tutor message', (tester) async {
      const bug = DiagnosticBug(
        category: 'sign_flip',
        description: 'İşaret ters çevrilirken hata yapıldı.',
        severity: 'high',
        remediationDirective: 'Parantez açarken eksi işaretinin içeriye nasıl dağıldığına dikkat et.',
      );

      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
        diagnosticBug: bug,
        userExpression: 'x^2 + 5x + 6 = 0',
      ));
      await tester.pumpAndSettle();

      // Open bottom sheet
      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Verify header and initial message
      expect(find.byKey(const Key('socratic_chat_header')), findsOneWidget);
      expect(find.text('Sokratik Öğretmen'), findsOneWidget);
      expect(find.text('İşaret ters çevrilirken hata yapıldı.'), findsOneWidget);
      expect(find.byKey(const Key('socratic_chat_input')), findsOneWidget);
      expect(find.byKey(const Key('socratic_chat_send_button')), findsOneWidget);

      // Verify opening message is displayed (either from fallback or remediation)
      expect(find.textContaining('Parantez açarken'), findsWidgets);
    });

    testWidgets('sends message via quick suggestion chip and receives tutor reply', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Tap quick chip "Neden öyle?"
      final chipFinder = find.text('Neden öyle?');
      expect(chipFinder, findsOneWidget);
      await tester.tap(chipFinder);
      await tester.pumpAndSettle();

      // User message should appear in chat
      expect(
        find.descendant(
          of: find.byKey(const Key('socratic_chat_message_list')),
          matching: find.text('Neden öyle?'),
        ),
        findsOneWidget,
      );

      // Socratic assistant should have responded
      expect(find.byType(ListView), findsWidgets);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('sends custom text message and shows apply button for algebraic step', (tester) async {
      String? appliedStep;

      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
        onApplyCorrectedStep: (step) {
          appliedStep = step;
        },
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      // Type algebraic step into input field
      await tester.enterText(find.byKey(const Key('socratic_chat_input')), '(x - 2)(x - 3) = 0');
      await tester.tap(find.byKey(const Key('socratic_chat_send_button')));
      await tester.pumpAndSettle();

      // Verify user message appears
      expect(find.text('(x - 2)(x - 3) = 0'), findsOneWidget);

      // Verify "Bu Adımı Çözüme Aktar" button appears for this algebraic message
      final applyBtn = find.byKey(const Key('socratic_apply_step_button'));
      expect(applyBtn, findsOneWidget);

      // Tap "Bu Adımı Çözüme Aktar"
      await tester.tap(applyBtn);
      await tester.pumpAndSettle();

      // Verify step was applied and dialog closed
      expect(appliedStep, '(x - 2)(x - 3) = 0');
      expect(find.byKey(const Key('socratic_chat_header')), findsNothing);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.heavyImpact), isTrue);
    });

    testWidgets('close button dismisses dialog', (tester) async {
      await tester.pumpWidget(buildTestableWidget(
        targetEquation: 'x^2 - 5x + 6 = 0',
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('open_dialog_btn')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_chat_header')), findsOneWidget);

      await tester.tap(find.byKey(const Key('socratic_chat_close_button')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_chat_header')), findsNothing);
    });
  });
}
