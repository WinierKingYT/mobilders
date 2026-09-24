import 'package:flutter/material.dart';
import '../../../../../core/services/haptic_feedback_service.dart';

class WarmupQuestion {
  final String prompt;
  final List<int> options;
  final int correctOption;
  final String successFeedback;
  final String retryFeedback;
  final String? ruleCardTitle;
  final String? ruleCardContent;

  const WarmupQuestion({
    required this.prompt,
    required this.options,
    required this.correctOption,
    required this.successFeedback,
    required this.retryFeedback,
    this.ruleCardTitle,
    this.ruleCardContent,
  });
}

class WarmupPhaseView extends StatefulWidget {
  final VoidCallback onCompleted;
  final WarmupQuestion? question;

  static const List<WarmupQuestion> defaultWarmupBank = [
    WarmupQuestion(
      prompt: "Hatırlama Sorusu: 3(x - 4) = 12 ise x kaçtır?",
      options: [4, 6, 8, 10],
      correctOption: 8,
      successFeedback: "Harika! 3(8 - 4) = 3(4) = 12. Bilişsel hazırlık tamamlandı!",
      retryFeedback: "3(x - 4) = 12 ise x - 4 = 4 olmalı. Tekrar dene!",
      ruleCardTitle: "Parantez Dağılma ve Sadeleştirme Kuralı",
      ruleCardContent: "a(x - b) = c denkleminde önce iki tarafı a'ya bölerek (x - b = c/a) veya a'yı dağıtarak (ax - ab = c) çözüme ulaşabilirsin.",
    ),
    WarmupQuestion(
      prompt: "Hatırlama Sorusu: 2(x + 3) = 16 ise x kaçtır?",
      options: [3, 5, 7, 9],
      correctOption: 5,
      successFeedback: "Harika! 2(5 + 3) = 2(8) = 16. Bilişsel hazırlık tamamlandı!",
      retryFeedback: "2(x + 3) = 16 ise x + 3 = 8 olmalı. Tekrar dene!",
      ruleCardTitle: "Çarpanı Sadeleştirme",
      ruleCardContent: "İki tarafı 2'ye böl: x + 3 = 8, ardından +3'ü karşıya -3 olarak geçir: x = 5.",
    ),
    WarmupQuestion(
      prompt: "Hatırlama Sorusu: 4(x - 2) = 20 ise x kaçtır?",
      options: [5, 6, 7, 8],
      correctOption: 7,
      successFeedback: "Harika! 4(7 - 2) = 4(5) = 20. Bilişsel hazırlık tamamlandı!",
      retryFeedback: "4(x - 2) = 20 ise x - 2 = 5 olmalı. Tekrar dene!",
      ruleCardTitle: "Doğrusal Önkoşul Mantığı",
      ruleCardContent: "4(x - 2) = 20 -> x - 2 = 5 -> x = 7.",
    ),
    WarmupQuestion(
      prompt: "Hatırlama Sorusu: 5(x + 1) = 35 ise x kaçtır?",
      options: [4, 6, 8, 10],
      correctOption: 6,
      successFeedback: "Harika! 5(6 + 1) = 5(7) = 35. Bilişsel hazırlık tamamlandı!",
      retryFeedback: "5(x + 1) = 35 ise x + 1 = 7 olmalı. Tekrar dene!",
      ruleCardTitle: "Çarpım ve Toplam İzolasyonu",
      ruleCardContent: "x + 1 = 35 / 5 = 7 -> x = 6.",
    ),
  ];

  const WarmupPhaseView({
    super.key,
    required this.onCompleted,
    this.question,
  });

  @override
  State<WarmupPhaseView> createState() => _WarmupPhaseViewState();
}

class _WarmupPhaseViewState extends State<WarmupPhaseView> {
  int? _selectedWarmupOption;
  bool _isRuleCardExpanded = false;

  WarmupQuestion get _currentQuestion =>
      widget.question ?? WarmupPhaseView.defaultWarmupBank.first;

  @override
  Widget build(BuildContext context) {
    final question = _currentQuestion;
    final options = question.options;
    final isCorrect = _selectedWarmupOption == question.correctOption;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Icon(Icons.fitness_center, color: Color(0xFF38BDF8), size: 48),
          const SizedBox(height: 16),
          const Text(
            "Faz 1: Bilişsel Isınma (3 Dakika)",
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            "FSRS-4.5 aralıklı tekrar algoritması, doğrusal önkoşul hafızasını canlı tutmak için zihnini hazırlıyor.",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF334155)),
            ),
            child: Text(
              question.prompt,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          if (question.ruleCardTitle != null && question.ruleCardContent != null) ...[
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: _isRuleCardExpanded
                      ? const Color(0xFF38BDF8)
                      : const Color(0xFF334155),
                ),
              ),
              child: Column(
                children: [
                  InkWell(
                    key: const Key('warmup_rule_card_toggle'),
                    borderRadius: BorderRadius.circular(10),
                    onTap: () {
                      HapticFeedbackService().selectionClick();
                      setState(() => _isRuleCardExpanded = !_isRuleCardExpanded);
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.lightbulb_outline,
                            color: Color(0xFFFBBF24),
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              "💡 Hızlı Hatırla: ${question.ruleCardTitle!}",
                              style: const TextStyle(
                                color: Color(0xFFF1F5F9),
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          Icon(
                            _isRuleCardExpanded
                                ? Icons.keyboard_arrow_up
                                : Icons.keyboard_arrow_down,
                            color: const Color(0xFF94A3B8),
                            size: 20,
                          ),
                        ],
                      ),
                    ),
                  ),
                  if (_isRuleCardExpanded)
                    Padding(
                      key: const Key('warmup_rule_card_content'),
                      padding: const EdgeInsets.only(left: 12, right: 12, bottom: 12),
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFF475569)),
                        ),
                        child: Text(
                          question.ruleCardContent!,
                          style: const TextStyle(
                            color: Color(0xFFCBD5E1),
                            fontSize: 12,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 16),

          // Interactive Options
          Row(
            children: options.map((opt) {
              final isSelected = _selectedWarmupOption == opt;
              Color bg = const Color(0xFF1E293B);
              Color border = const Color(0xFF334155);
              if (isSelected) {
                if (opt == question.correctOption) {
                  bg = const Color(0xFF065F46);
                  border = const Color(0xFF10B981);
                } else {
                  bg = const Color(0xFF7F1D1D);
                  border = const Color(0xFFEF4444);
                }
              }
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(8),
                    onTap: () {
                      if (opt == question.correctOption) {
                        HapticFeedbackService().stepSuccess();
                      } else {
                        HapticFeedbackService().keyPress();
                      }
                      setState(() => _selectedWarmupOption = opt);
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      decoration: BoxDecoration(
                        color: bg,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: border, width: isSelected ? 2 : 1),
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        "x = $opt",
                        style: TextStyle(
                          color: isSelected ? Colors.white : const Color(0xFFE2E8F0),
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),

          if (_selectedWarmupOption != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isCorrect ? const Color(0xFF064E3B) : const Color(0xFF450A0A),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: isCorrect ? const Color(0xFF10B981) : const Color(0xFFEF4444)),
              ),
              child: Row(
                children: [
                  Icon(
                    isCorrect ? Icons.check_circle : Icons.info_outline,
                    color: isCorrect ? const Color(0xFF34D399) : const Color(0xFFF87171),
                    size: 18,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      isCorrect
                          ? question.successFeedback
                          : question.retryFeedback,
                      style: TextStyle(
                        color: isCorrect ? const Color(0xFFA7F3D0) : const Color(0xFFFECACA),
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: isCorrect ? const Color(0xFF10B981) : const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            onPressed: () {
              HapticFeedbackService().selectionClick();
              widget.onCompleted();
            },
            child: const Text("Isınmayı Tamamla -> CAT Teşhise Başla"),
          ),
        ],
      ),
    );
  }
}
