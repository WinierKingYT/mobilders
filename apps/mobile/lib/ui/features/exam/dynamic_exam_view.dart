import 'package:flutter/material.dart';

class ExamChoice {
  final String text;
  final bool isCorrect;
  final String? bugId;
  final String? distractorRationale;

  const ExamChoice({
    required this.text,
    required this.isCorrect,
    this.bugId,
    this.distractorRationale,
  });
}

class ExamQuestion {
  final String id;
  final String prompt;
  final List<ExamChoice> choices;
  final int correctIndex;

  const ExamQuestion({
    required this.id,
    required this.prompt,
    required this.choices,
    required this.correctIndex,
  });
}

class DynamicExamView extends StatefulWidget {
  final String examTitle;
  final List<ExamQuestion> questions;
  final int timeMinutes;
  final ValueChanged<Map<int, int>>? onExamCompleted;

  const DynamicExamView({
    super.key,
    required this.examTitle,
    required this.questions,
    this.timeMinutes = 20,
    this.onExamCompleted,
  });

  @override
  State<DynamicExamView> createState() => _DynamicExamViewState();
}

class _DynamicExamViewState extends State<DynamicExamView> {
  int _currentIndex = 0;
  final Map<int, int> _answers = {}; // questionIndex -> choiceIndex
  bool _isFinished = false;

  void _finishExam() {
    setState(() {
      _isFinished = true;
    });
    widget.onExamCompleted?.call(_answers);
  }

  @override
  void didUpdateWidget(covariant DynamicExamView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (_currentIndex >= widget.questions.length) {
      _currentIndex = widget.questions.isEmpty ? 0 : widget.questions.length - 1;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isFinished) {
      return _buildDiagnosticResultScreen();
    }

    if (widget.questions.isEmpty) {
      return Scaffold(
        key: const Key('dynamic_exam_view'),
        appBar: AppBar(
          title: Text(widget.examTitle, style: const TextStyle(fontSize: 15)),
          backgroundColor: const Color(0xFF0F172A),
        ),
        backgroundColor: const Color(0xFF090D16),
        body: const Center(
          child: Text("Sınavda soru bulunamadı.", style: TextStyle(color: Colors.white70)),
        ),
      );
    }

    final currentQ = widget.questions[_currentIndex];
    final chosenChoice = _answers[_currentIndex];

    return Scaffold(
      key: const Key('dynamic_exam_view'),
      appBar: AppBar(
        title: Text(widget.examTitle, style: const TextStyle(fontSize: 15)),
        backgroundColor: const Color(0xFF0F172A),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14.0),
            child: Row(
              children: [
                const Icon(Icons.timer_outlined, size: 18, color: Colors.amberAccent),
                const SizedBox(width: 4),
                Text(
                  "${widget.timeMinutes}:00",
                  key: const Key('exam_timer'),
                  style: const TextStyle(
                    color: Colors.amberAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      backgroundColor: const Color(0xFF090D16),
      body: Column(
        children: [
          // 1. Question Navigator Strip
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0),
            color: const Color(0xFF1E293B),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: List.generate(widget.questions.length, (idx) {
                  final isAnswered = _answers.containsKey(idx);
                  final isCurrent = idx == _currentIndex;

                  Color bgColor = Colors.white10;
                  if (isCurrent) {
                    bgColor = Colors.cyanAccent;
                  } else if (isAnswered) {
                    bgColor = Colors.green.withValues(alpha: 0.4);
                  }

                  return GestureDetector(
                    onTap: () => setState(() => _currentIndex = idx),
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: bgColor,
                        borderRadius: BorderRadius.circular(8),
                        border: isCurrent ? Border.all(color: Colors.white, width: 1.5) : null,
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        "${idx + 1}",
                        style: TextStyle(
                          color: isCurrent ? Colors.black : Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),

          // 2. Active Question Body
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    "Soru ${_currentIndex + 1} / ${widget.questions.length}",
                    style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(14.0),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      currentQ.prompt,
                      style: const TextStyle(color: Colors.white, fontSize: 14.5, height: 1.4),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Choices
                  ...List.generate(currentQ.choices.length, (choiceIdx) {
                    final choice = currentQ.choices[choiceIdx];
                    final isSelected = chosenChoice == choiceIdx;
                    final optionLetter = String.fromCharCode(65 + choiceIdx);

                    return GestureDetector(
                      key: Key('choice_$choiceIdx'),
                      onTap: () {
                        setState(() {
                          _answers[_currentIndex] = choiceIdx;
                        });
                      },
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 10.0),
                        padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? Colors.cyanAccent.withValues(alpha: 0.15)
                              : const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: isSelected ? Colors.cyanAccent : Colors.white12,
                            width: isSelected ? 1.5 : 1.0,
                          ),
                        ),
                        child: Row(
                          children: [
                            CircleAvatar(
                              radius: 13,
                              backgroundColor: isSelected ? Colors.cyanAccent : Colors.white12,
                              child: Text(
                                optionLetter,
                                style: TextStyle(
                                  color: isSelected ? Colors.black : Colors.white,
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                choice.text,
                                style: TextStyle(
                                  color: isSelected ? Colors.cyanAccent : Colors.white,
                                  fontSize: 13.5,
                                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),

          // 3. Bottom Action Bar
          Container(
            padding: const EdgeInsets.all(12.0),
            color: const Color(0xFF1E293B),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton(
                  key: const Key('btn_prev_question'),
                  onPressed: _currentIndex > 0
                      ? () => setState(() => _currentIndex--)
                      : null,
                  child: const Text("Önceki"),
                ),
                ElevatedButton(
                  key: const Key('btn_finish_exam'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent, foregroundColor: Colors.white),
                  onPressed: _finishExam,
                  child: const Text("Sınavı Bitir", style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                ElevatedButton(
                  key: const Key('btn_next_question'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent, foregroundColor: Colors.black),
                  onPressed: _currentIndex < widget.questions.length - 1
                      ? () => setState(() => _currentIndex++)
                      : null,
                  child: const Text("Sonraki"),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDiagnosticResultScreen() {
    int correct = 0;
    int incorrect = 0;
    int empty = 0;
    final List<Map<String, dynamic>> traps = [];

    for (int i = 0; i < widget.questions.length; i++) {
      final q = widget.questions[i];
      final chosen = _answers[i];
      if (chosen == null) {
        empty++;
      } else if (chosen == q.correctIndex) {
        correct++;
      } else {
        incorrect++;
        final choice = q.choices[chosen];
        if (choice.bugId != null) {
          traps.add({
            "qNum": i + 1,
            "bugId": choice.bugId,
            "rationale": choice.distractorRationale,
          });
        }
      }
    }

    final net = (correct - (incorrect / 4.0)).clamp(0.0, widget.questions.length.toDouble());

    return Scaffold(
      key: const Key('exam_result_view'),
      appBar: AppBar(
        title: const Text("Bilişsel Deneme Teşhis Raporu"),
        backgroundColor: const Color(0xFF0F172A),
      ),
      backgroundColor: const Color(0xFF090D16),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Net Score Card
            Container(
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.cyanAccent),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _stat("Net", net.toStringAsFixed(2), Colors.cyanAccent),
                  _stat("Doğru", "$correct", Colors.greenAccent),
                  _stat("Yanlış", "$incorrect", Colors.redAccent),
                  _stat("Boş", "$empty", Colors.white54),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Cognitive Traps Triggered Section
            const Text(
              "Tetiklenen Bilişsel Tuzaklar (Otopsi Dosyası)",
              style: TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 15),
            ),
            const SizedBox(height: 8),

            if (traps.isEmpty)
              Container(
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.4)),
                ),
                child: const Text(
                  "Tebrikler! Hiçbir bilişsel kavram tuzağına düşmedin.",
                  style: TextStyle(color: Colors.greenAccent, fontSize: 13),
                ),
              )
            else
              Container(
                key: const Key('traps_triggered_section'),
                child: Column(
                  children: traps.map((t) {
                    return Container(
                      margin: const EdgeInsets.only(bottom: 8.0),
                      padding: const EdgeInsets.all(12.0),
                      decoration: BoxDecoration(
                        color: Colors.red.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: Colors.redAccent.withValues(alpha: 0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text("Soru ${t['qNum']}: ", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(color: Colors.redAccent, borderRadius: BorderRadius.circular(4)),
                                child: Text(t['bugId'], style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(t['rationale'] ?? "", style: const TextStyle(color: Colors.white70, fontSize: 12)),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _stat(String title, String val, Color c) {
    return Column(
      children: [
        Text(val, style: TextStyle(color: c, fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(title, style: const TextStyle(color: Colors.white70, fontSize: 12)),
      ],
    );
  }
}
