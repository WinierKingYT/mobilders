import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personal_learning_engine/ui/features/exam/dynamic_exam_view.dart';

void main() {
  final testQuestions = [
    const ExamQuestion(
      id: "q1",
      prompt: "x² - 5x + 6 = 0 denkleminin kökleri nedir?",
      choices: [
        ExamChoice(text: "x = 2 veya x = 3", isCorrect: true),
        ExamChoice(
          text: "x = -2 veya x = -3",
          isCorrect: false,
          bugId: "BUG-QUAD-05",
          distractorRationale: "İşaret hatası tuzağı",
        ),
        ExamChoice(text: "x = 2", isCorrect: false, bugId: "BUG-QUAD-02"),
      ],
      correctIndex: 0,
    ),
    const ExamQuestion(
      id: "q2",
      prompt: "f(x) = (3x + 2)⁴ türevi nedir?",
      choices: [
        ExamChoice(
          text: "4(3x + 2)³",
          isCorrect: false,
          bugId: "BUG-CALC-01",
          distractorRationale: "İç türev unutuldu",
        ),
        ExamChoice(text: "12(3x + 2)³", isCorrect: true),
      ],
      correctIndex: 1,
    ),
  ];

  testWidgets('DynamicExamView renders questions and navigates properly',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: DynamicExamView(
          examTitle: "TYT Deneme Sınavı",
          questions: testQuestions,
          timeMinutes: 20,
        ),
      ),
    );

    // 1. Verify view and timer
    expect(find.byKey(const Key('dynamic_exam_view')), findsOneWidget);
    expect(find.text("TYT Deneme Sınavı"), findsOneWidget);
    expect(find.byKey(const Key('exam_timer')), findsOneWidget);

    // 2. First question prompt
    expect(find.text("Soru 1 / 2"), findsOneWidget);
    expect(find.textContaining("x² - 5x + 6 = 0"), findsOneWidget);

    // 3. Select Choice A on Question 1
    await tester.tap(find.byKey(const Key('choice_0')));
    await tester.pumpAndSettle();

    // 4. Click Next
    await tester.tap(find.byKey(const Key('btn_next_question')));
    await tester.pumpAndSettle();

    expect(find.text("Soru 2 / 2"), findsOneWidget);
    expect(find.textContaining("f(x) = (3x + 2)⁴"), findsOneWidget);
  });

  testWidgets('DynamicExamView finishes exam and shows cognitive trap diagnostic report',
      (WidgetTester tester) async {
    Map<int, int>? completedAnswers;

    await tester.pumpWidget(
      MaterialApp(
        home: DynamicExamView(
          examTitle: "TYT Deneme Sınavı",
          questions: testQuestions,
          onExamCompleted: (answers) {
            completedAnswers = answers;
          },
        ),
      ),
    );

    // Answer Q1 with Choice 1 (BUG-QUAD-05 trap!)
    await tester.tap(find.byKey(const Key('choice_1')));
    await tester.pumpAndSettle();

    // Finish Exam
    await tester.tap(find.byKey(const Key('btn_finish_exam')));
    await tester.pumpAndSettle();

    // Verify Result Screen
    expect(find.byKey(const Key('exam_result_view')), findsOneWidget);
    expect(find.text("Bilişsel Deneme Teşhis Raporu"), findsOneWidget);

    // Verify Cognitive Traps section detected BUG-QUAD-05
    expect(find.byKey(const Key('traps_triggered_section')), findsOneWidget);
    expect(find.text("BUG-QUAD-05"), findsOneWidget);
    expect(find.text("İşaret hatası tuzağı"), findsOneWidget);

    expect(completedAnswers, isNotNull);
    expect(completedAnswers![0], 1);
  });
}
