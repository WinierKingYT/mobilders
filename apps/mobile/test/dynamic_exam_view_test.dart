import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
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

  group('EngineApiService Dynamic Exam & Trap Question Tests', () {
    test('generateDynamicExam calls /api/v1/exam/generate and parses exam', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, equals('POST'));
        expect(request.url.path, equals('/api/v1/exam/generate'));
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['section'], equals('TYT_MATEMATIK'));
        expect(body['question_count'], equals(5));

        return http.Response(
          jsonEncode({
            'exam_id': 'ex_123',
            'title': 'TYT Deneme Sınavı',
            'section': 'TYT_MATEMATIK',
            'questions': [
              {
                'question_id': 'q1',
                'node_id': 'N27',
                'type': 'algebra',
                'prompt': 'x² - 5x + 6 = 0',
                'choices': [],
                'correct_choice_index': 0,
              }
            ],
            'total_time_minutes': 10,
            'target_theta': 0.5,
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final res = await api.generateDynamicExam(
        section: 'TYT_MATEMATIK',
        questionCount: 5,
        targetTheta: 0.5,
      );

      expect(res['exam_id'], equals('ex_123'));
      expect((res['questions'] as List).length, equals(1));
    });

    test('gradeDynamicExam calls /api/v1/exam/grade and parses diagnostic report', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, equals('POST'));
        expect(request.url.path, equals('/api/v1/exam/grade'));
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        expect(body['answers'], isNotNull);

        return http.Response(
          jsonEncode({
            'total_questions': 2,
            'correct': 1,
            'incorrect': 1,
            'empty': 0,
            'net_score': 0.75,
            'percentage': 50.0,
            'traps_triggered': [
              {
                'question_index': 2,
                'bug_id': 'BUG-CALC-01',
                'distractor_rationale': 'İç türev unutuldu',
              }
            ],
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final res = await api.gradeDynamicExam(
        exam: {'exam_id': 'ex_123'},
        answers: {0: 0, 1: 1},
      );

      expect(res['correct'], equals(1));
      expect(res['traps_triggered'], isNotEmpty);
      expect(res['traps_triggered'][0]['bug_id'], equals('BUG-CALC-01'));
    });

    test('exportDynamicExam calls /api/v1/exam/export for LaTeX and HTML', () async {
      final mockClient = MockClient((request) async {
        final body = jsonDecode(request.body) as Map<String, dynamic>;
        final format = body['format'] as String;
        return http.Response(
          jsonEncode({
            'format': format,
            'content': format == 'latex' ? r'\documentclass{article}' : '<!DOCTYPE html>',
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      });

      final api = EngineApiService(client: mockClient);
      final resHtml = await api.exportDynamicExam(exam: {'exam_id': 'ex_1'}, format: 'html');
      expect(resHtml['content'], contains('<!DOCTYPE html>'));

      final resTex = await api.exportDynamicExam(exam: {'exam_id': 'ex_1'}, format: 'latex');
      expect(resTex['content'], contains(r'\documentclass'));
    });

    test('generateTargetedTrapQuestion and verifyTrapQuestion call correct endpoints', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path == '/api/v1/exam/question/targeted') {
          return http.Response(
            jsonEncode({
              'question_id': 'q_target',
              'type': 'calculus',
              'choices': [
                {'text': 'Choice A', 'is_correct': true},
                {'text': 'Choice B', 'is_correct': false, 'bug_id': 'BUG-CALC-01'},
              ],
            }),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        } else if (request.url.path == '/api/v1/exam/question/verify') {
          return http.Response(
            jsonEncode({
              'is_valid': true,
              'has_formal_proof': true,
              'zero_false_positives': true,
            }),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final api = EngineApiService(client: mockClient);
      final q = await api.generateTargetedTrapQuestion(bugId: 'BUG-CALC-01', seed: 42);
      expect(q['question_id'], equals('q_target'));

      final proof = await api.verifyTrapQuestion(q);
      expect(proof['is_valid'], isTrue);
      expect(proof['zero_false_positives'], isTrue);
    });
  });
}
