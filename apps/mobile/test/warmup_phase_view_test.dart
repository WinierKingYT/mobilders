import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/session/views/components/warmup_phase_view.dart';

void main() {
  group('WarmupPhaseView Widget Tests', () {
    testWidgets('renders prompt and options from default bank', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: WarmupPhaseView(
                onCompleted: () {},
              ),
            ),
          ),
        ),
      );

      expect(find.text("Faz 1: Bilişsel Isınma (3 Dakika)"), findsOneWidget);
      expect(find.textContaining("3(x - 4) = 12"), findsOneWidget);
      expect(find.text("x = 4"), findsOneWidget);
      expect(find.text("x = 8"), findsOneWidget);
    });

    testWidgets('selecting incorrect and correct options triggers respective feedback', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: WarmupPhaseView(
                onCompleted: () {},
              ),
            ),
          ),
        ),
      );

      // Select incorrect option 4 (correct is 8)
      await tester.tap(find.text("x = 4"));
      await tester.pumpAndSettle();
      expect(find.textContaining("Tekrar dene!"), findsOneWidget);

      // Select correct option 8
      await tester.tap(find.text("x = 8"));
      await tester.pumpAndSettle();
      expect(find.textContaining("Harika!"), findsOneWidget);
    });

    testWidgets('collapsible Quick Recall Card toggles expansion', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: WarmupPhaseView(
                onCompleted: () {},
              ),
            ),
          ),
        ),
      );

      final toggleFinder = find.byKey(const Key('warmup_rule_card_toggle'));
      final contentFinder = find.byKey(const Key('warmup_rule_card_content'));

      expect(toggleFinder, findsOneWidget);
      expect(contentFinder, findsNothing);

      // Expand card
      await tester.tap(toggleFinder);
      await tester.pumpAndSettle();

      expect(contentFinder, findsOneWidget);
      expect(find.textContaining("a(x - b) = c denkleminde"), findsOneWidget);

      // Collapse card
      await tester.tap(toggleFinder);
      await tester.pumpAndSettle();

      expect(contentFinder, findsNothing);
    });

    testWidgets('onCompleted callback fires when completion button is pressed', (tester) async {
      bool completed = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: WarmupPhaseView(
                onCompleted: () => completed = true,
              ),
            ),
          ),
        ),
      );

      final completeBtn = find.text("Isınmayı Tamamla -> CAT Teşhise Başla");
      await tester.ensureVisible(completeBtn);
      await tester.tap(completeBtn);
      await tester.pumpAndSettle();

      expect(completed, isTrue);
    });

    testWidgets('does not show quick recall card if title/content is omitted', (tester) async {
      const customQ = WarmupQuestion(
        prompt: "x + 5 = 10 ise x kaçtır?",
        options: [3, 4, 5, 6],
        correctOption: 5,
        successFeedback: "Doğru!",
        retryFeedback: "Yanlış!",
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: WarmupPhaseView(
                question: customQ,
                onCompleted: () {},
              ),
            ),
          ),
        ),
      );

      expect(find.byKey(const Key('warmup_rule_card_toggle')), findsNothing);
    });
  });
}
