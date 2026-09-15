import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/ui/features/notes/living_notes_drawer.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    HapticFeedbackService().clearHistory();
    HapticFeedbackService().isEnabled = true;
  });

  Widget buildTestableWidget({
    String nodeId = 'N15',
    VoidCallback? onResumeSession,
    ValueChanged<String>? onNoteVisited,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: LivingNotesDrawer(
          initialNodeId: nodeId,
          onResumeSession: onResumeSession,
          onNoteVisited: onNoteVisited,
        ),
      ),
    );
  }

  group('LivingNotesDrawer Widget Tests', () {
    testWidgets('renders initial note components and 1-sentence intuition', (tester) async {
      await tester.pumpWidget(buildTestableWidget(nodeId: 'N15'));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('living_notes_drawer')), findsOneWidget);
      expect(find.text('İkinci Dereceden Denklem Çözümü'), findsOneWidget);
      expect(find.byKey(const Key('note_intuition_banner')), findsOneWidget);
      expect(find.textContaining('İçinde x² olan bir denklemde amaç'), findsOneWidget);

      // Recipe steps
      expect(find.byKey(const Key('note_recipe_step_0')), findsOneWidget);
      expect(find.byKey(const Key('note_recipe_step_1')), findsOneWidget);
      expect(find.byKey(const Key('note_recipe_step_2')), findsOneWidget);

      // Resume button
      expect(find.byKey(const Key('resume_session_button')), findsOneWidget);
    });

    testWidgets('submitting incorrect mini-exercise answer shows error hint', (tester) async {
      await tester.pumpWidget(buildTestableWidget(nodeId: 'N15'));
      await tester.pumpAndSettle();

      final inputFinder = find.byKey(const Key('mini_exercise_input'));
      final submitFinder = find.byKey(const Key('mini_exercise_submit'));

      await tester.ensureVisible(inputFinder);
      await tester.enterText(inputFinder, '999');
      await tester.ensureVisible(submitFinder);
      await tester.tap(submitFinder);
      await tester.pumpAndSettle();

      expect(find.textContaining('Tekrar dene!'), findsOneWidget);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.heavyImpact), isTrue);
    });

    testWidgets('submitting correct mini-exercise answer shows success', (tester) async {
      await tester.pumpWidget(buildTestableWidget(nodeId: 'N15'));
      await tester.pumpAndSettle();

      final inputFinder = find.byKey(const Key('mini_exercise_input'));
      final submitFinder = find.byKey(const Key('mini_exercise_submit'));

      // N15 answer is 7
      await tester.ensureVisible(inputFinder);
      await tester.enterText(inputFinder, '7');
      await tester.ensureVisible(submitFinder);
      await tester.tap(submitFinder);
      await tester.pumpAndSettle();

      expect(find.textContaining('Tebrikler!'), findsOneWidget);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.mediumImpact), isTrue);
    });

    testWidgets('tapping resume session triggers callback and haptics', (tester) async {
      bool resumed = false;
      await tester.pumpWidget(buildTestableWidget(
        nodeId: 'N15',
        onResumeSession: () => resumed = true,
      ));
      await tester.pumpAndSettle();

      final resumeBtn = find.byKey(const Key('resume_session_button'));
      await tester.tap(resumeBtn);
      await tester.pumpAndSettle();

      expect(resumed, isTrue);
      expect(HapticFeedbackService().triggeredHistory.contains(HapticType.selectionClick), isTrue);
    });

    testWidgets('tapping prerequisite ladder step loads that note', (tester) async {
      String? visited;
      await tester.pumpWidget(buildTestableWidget(
        nodeId: 'N15',
        onNoteVisited: (id) => visited = id,
      ));
      await tester.pumpAndSettle();

      // Tap N04 in ladder
      final n04Step = find.byKey(const Key('ladder_step_N04'));
      expect(n04Step, findsOneWidget);

      await tester.tap(n04Step);
      await tester.pumpAndSettle();

      expect(find.text('1. Dereceden Lineer Denklem'), findsOneWidget);
      expect(find.textContaining('Denklem dengede bir terazidir'), findsOneWidget);
      expect(visited, 'N04');
    });
  });
}
