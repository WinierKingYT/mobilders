import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/session/widgets/socratic_hint_dialog.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  Widget buildTestableWidget({
    String targetEquation = '-2x < 10',
    VoidCallback? onResolved,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: SocraticHintDialog(
          targetEquation: targetEquation,
          onResolved: onResolved,
        ),
      ),
    );
  }

  group('SocraticHintDialog Widget Tests', () {
    testWidgets('renders initial empathy stage with header and message', (tester) async {
      await tester.pumpWidget(buildTestableWidget(targetEquation: '-2x < 10'));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_dialog_header')), findsOneWidget);
      expect(find.text('Eşitsizlikte Negatif Sayıya Bölme'), findsOneWidget);
      expect(find.byKey(const Key('socratic_empathy_view')), findsOneWidget);
      expect(find.text('1. Empati'), findsOneWidget);
      expect(find.text('2. Sezgi'), findsOneWidget);
      expect(find.text('3. Keşif'), findsOneWidget);
    });

    testWidgets('advances from Empathy to Grounding stage', (tester) async {
      await tester.pumpWidget(buildTestableWidget(targetEquation: '-2x < 10'));
      await tester.pumpAndSettle();

      final nextBtn = find.byKey(const Key('socratic_next_button'));
      expect(nextBtn, findsOneWidget);

      await tester.tap(nextBtn);
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_grounding_view')), findsOneWidget);
      expect(find.textContaining('Sayı doğrusunda 2 < 5 olduğunu biliyoruz'), findsOneWidget);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('advances from Grounding to Self-Discovery stage', (tester) async {
      await tester.pumpWidget(buildTestableWidget(targetEquation: '-2x < 10'));
      await tester.pumpAndSettle();

      // Tap to Grounding
      await tester.tap(find.byKey(const Key('socratic_next_button')));
      await tester.pumpAndSettle();

      // Tap to Self-Discovery
      await tester.tap(find.byKey(const Key('socratic_next_button')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_discovery_view')), findsOneWidget);
      expect(find.byKey(const Key('socratic_input_field')), findsOneWidget);
      expect(find.byKey(const Key('socratic_submit_discovery')), findsOneWidget);
    });

    testWidgets('submitting incorrect guess shows guidance and error haptics', (tester) async {
      await tester.pumpWidget(buildTestableWidget(targetEquation: '-2x < 10'));
      await tester.pumpAndSettle();

      // Navigate to Self-Discovery
      await tester.tap(find.byKey(const Key('socratic_next_button')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('socratic_next_button')));
      await tester.pumpAndSettle();

      // Enter incorrect guess with explicit negation
      await tester.enterText(find.byKey(const Key('socratic_input_field')), 'İşaret hiçbir zaman değişmez');
      await tester.tap(find.byKey(const Key('socratic_submit_discovery')));
      await tester.pumpAndSettle();

      expect(find.textContaining('İpucu: Negatif tarafa geçince'), findsOneWidget);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.heavyImpact), isTrue);
    });

    testWidgets('submitting correct guess resolves stage and fires onResolved', (tester) async {
      bool wasResolved = false;
      await tester.pumpWidget(buildTestableWidget(
        targetEquation: '-2x < 10',
        onResolved: () => wasResolved = true,
      ));
      await tester.pumpAndSettle();

      // Navigate to Self-Discovery
      await tester.tap(find.byKey(const Key('socratic_next_button')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('socratic_next_button')));
      await tester.pumpAndSettle();

      // Enter correct discovery keyword
      await tester.enterText(find.byKey(const Key('socratic_input_field')), 'Eşitsizlik yön değiştirir');
      await tester.tap(find.byKey(const Key('socratic_submit_discovery')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('socratic_resolved_view')), findsOneWidget);
      expect(find.text('Başardın!'), findsOneWidget);
      expect(find.textContaining('+0.10 BKT Güven Bonusu'), findsOneWidget);
      expect(wasResolved, isTrue);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.mediumImpact), isTrue);
    });

    testWidgets('tapping close button triggers pop', (tester) async {
      await tester.pumpWidget(buildTestableWidget(targetEquation: '2x + 6 = 14'));
      await tester.pumpAndSettle();

      final closeBtn = find.byKey(const Key('socratic_close_button'));
      expect(closeBtn, findsOneWidget);
      await tester.tap(closeBtn);
      await tester.pumpAndSettle();
    });

    testWidgets('selects correct template for distributive property', (tester) async {
      await tester.pumpWidget(buildTestableWidget(targetEquation: '-(x - 4) = 10'));
      await tester.pumpAndSettle();

      expect(find.text('Parantez Önündeki Eksi İşaretini Dağıtma'), findsOneWidget);
    });
  });
}
