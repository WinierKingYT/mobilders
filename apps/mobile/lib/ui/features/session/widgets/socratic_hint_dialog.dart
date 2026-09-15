import 'package:flutter/material.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../core/app_theme.dart';

enum SocraticDialogStage {
  empathy,
  grounding,
  selfDiscovery,
  resolved,
}

class SocraticHintData {
  final String title;
  final String empathyMessage;
  final String groundingExample;
  final String discoveryQuestion;
  final List<String> expectedKeywords;
  final String guidanceIfStuck;

  const SocraticHintData({
    required this.title,
    required this.empathyMessage,
    required this.groundingExample,
    required this.discoveryQuestion,
    required this.expectedKeywords,
    required this.guidanceIfStuck,
  });

  static SocraticHintData forEquation(String equation) {
    final lower = equation.toLowerCase();
    if (lower.contains('<') || lower.contains('>') || lower.contains('<=') || lower.contains('>=')) {
      return const SocraticHintData(
        title: 'Eşitsizlikte Negatif Sayıya Bölme',
        empathyMessage: 'Harika ilerliyorsun, sona çok yaklaştın! Sakin bir nefes al, buradaki kritik eşiği birlikte aşalım.',
        groundingExample: 'Sayı doğrusunda 2 < 5 olduğunu biliyoruz. Peki iki tarafı -1 ile çarparsak -2 ve -5 sayılarından hangisi daha sağda (büyük) kalır?',
        discoveryQuestion: 'Sayı doğrusunda -2, -5\'in sağındadır; yani -2 > -5 olur! Öyleyse bir eşitsizliği negatif bir sayıya böldüğümüzde eşitsizlik yönü hakkında ne söyleyebilirsin?',
        expectedKeywords: ['yön', 'ters', 'döner', 'değiş', 'büyük', 'flip', 'reverse'],
        guidanceIfStuck: 'İpucu: Negatif tarafa geçince küçük sayı sıfıra daha yakın olur. Eşitsizlik işareti ters mi dönmeli?',
      );
    }
    if (lower.contains('-(') || lower.contains('- (')) {
      return const SocraticHintData(
        title: 'Parantez Önündeki Eksi İşaretini Dağıtma',
        empathyMessage: 'Çok iyi odaklandın, parantezli ifadelere gayet hakimsin! Şimdi işaret detayını birlikte yakalayalım.',
        groundingExample: 'Parantezin önündeki eksi, içerideki her terimi (-1) ile çarpmak demektir: -(a + b) = (-1)·a + (-1)·b.',
        discoveryQuestion: 'Öyleyse -(x - 4) ifadesinde eksi içeri dağıtıldığında hem x hem de -4 işaretleri nasıl değişir?',
        expectedKeywords: ['artı', '+4', 'eksi', 'işaret', 'değiş', '-x+4', '+ 4'],
        guidanceIfStuck: 'İpucu: Eksi ile eksinin çarpımı pozitiftir. -4 parantezden çıkınca hangi işareti alır?',
      );
    }
    if (lower.contains('/')) {
      return const SocraticHintData(
        title: 'Kesirlerde Payda Eşitleme',
        empathyMessage: 'Harika geldin! Rasyonel ifadeler bazen kalabalık görünür ama mantığı çok sadedir.',
        groundingExample: 'Yarım elma ile çeyrek elmayı toplamak için ikisini de çeyrek cinsinden (aynı birimle) ifade ederiz: 1/2 + 1/4 = 2/4 + 1/4.',
        discoveryQuestion: 'Paydaları farklı olan kesirleri tek bir kesir çizgisi altında toplamak için ilk olarak neyi eşitlemeliyiz?',
        expectedKeywords: ['payda', 'ortak', 'kat', 'ekok', 'okek', 'eşitle', 'genişlet'],
        guidanceIfStuck: 'İpucu: Kesirlerin altındaki sayıları ortak bir katta buluşturmamız gerekir.',
      );
    }
    // Default equation balance
    return const SocraticHintData(
      title: 'Terazi Modelinde Karşıya Terim Geçirme',
      empathyMessage: 'Çok iyi gidiyorsun, bilinmeyeni yalnız bırakma yolunda sona bir adım kaldı!',
      groundingExample: 'Dengede duran bir terazi düşün: Sol kefede x + 6 kg, sağda 14 kg var. Dengeyi bozmadan x\'i yalnız bırakmak için iki taraftan da 6 kg çıkarırız.',
      discoveryQuestion: 'Bir sayıyı eşitliğin diğer tarafına geçirdiğimizde terazinin dengesini korumak için sayının işareti neye dönüşür?',
      expectedKeywords: ['eksi', 'ters', 'zıt', 'işaret', 'değiş', '-', 'çıkar'],
      guidanceIfStuck: 'İpucu: Teraziye eklenen fazlalığı yok etmek için zıt işlem yaparız. Artı ise karşıya ne geçer?',
    );
  }
}

/// Socratic Hint Dialog (Bölüm 2 - Takılma Anında Sokratik Metot Anlatımı)
/// Enforces Zero-Leakage: Never gives away the solution root.
/// Leads the student through 3 interactive steps: Empathy -> Grounding -> Self-Discovery.
class SocraticHintDialog extends StatefulWidget {
  final String targetEquation;
  final VoidCallback? onResolved;

  const SocraticHintDialog({
    super.key,
    required this.targetEquation,
    this.onResolved,
  });

  static Future<void> show(BuildContext context, {required String targetEquation, VoidCallback? onResolved}) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
        child: SocraticHintDialog(
          targetEquation: targetEquation,
          onResolved: onResolved,
        ),
      ),
    );
  }

  @override
  State<SocraticHintDialog> createState() => _SocraticHintDialogState();
}

class _SocraticHintDialogState extends State<SocraticHintDialog> {
  late SocraticHintData _data;
  SocraticDialogStage _stage = SocraticDialogStage.empathy;
  final TextEditingController _discoveryController = TextEditingController();
  String? _feedbackMessage;
  bool _isError = false;

  @override
  void initState() {
    super.initState();
    _data = SocraticHintData.forEquation(widget.targetEquation);
  }

  @override
  void dispose() {
    _discoveryController.dispose();
    super.dispose();
  }

  void _nextStage() {
    HapticFeedbackService().selectionClick();
    setState(() {
      if (_stage == SocraticDialogStage.empathy) {
        _stage = SocraticDialogStage.grounding;
      } else if (_stage == SocraticDialogStage.grounding) {
        _stage = SocraticDialogStage.selfDiscovery;
      }
    });
  }

  void _submitDiscovery() {
    final text = _discoveryController.text.trim().toLowerCase();
    if (text.isEmpty) return;

    final negations = ['değişmez', 'dönmez', 'aynı kalır', 'etkilenmez', 'sabit kalır'];
    final hasNegation = negations.any((n) => text.contains(n));
    final isMatched = (!hasNegation) && _data.expectedKeywords.any((kw) => text.contains(kw));

    if (isMatched) {
      HapticFeedbackService().stepSuccess();
      setState(() {
        _stage = SocraticDialogStage.resolved;
        _feedbackMessage = 'Harikasın! Bu temel kuralı kendi başına keşfettin. 🎯';
        _isError = false;
      });
      widget.onResolved?.call();
    } else {
      HapticFeedbackService().stepError();
      setState(() {
        _feedbackMessage = _data.guidanceIfStuck;
        _isError = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Bar
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFF59E0B).withValues(alpha: 0.18),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.lightbulb_rounded, color: Color(0xFFF59E0B), size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _data.title,
                      key: const Key('socratic_dialog_header'),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Hedef: ${widget.targetEquation}',
                      style: const TextStyle(fontSize: 12, color: AppColors.textMuted, fontFamily: 'monospace'),
                    ),
                  ],
                ),
              ),
              IconButton(
                key: const Key('socratic_close_button'),
                icon: const Icon(Icons.close_rounded, color: AppColors.textMuted),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Stage Indicators (1. Empati, 2. Sezgi, 3. Keşif)
          Row(
            children: [
              _buildStepPill('1. Empati', _stage == SocraticDialogStage.empathy, _stage.index > 0),
              const SizedBox(width: 6),
              _buildStepPill('2. Sezgi', _stage == SocraticDialogStage.grounding, _stage.index > 1),
              const SizedBox(width: 6),
              _buildStepPill('3. Keşif', _stage == SocraticDialogStage.selfDiscovery || _stage == SocraticDialogStage.resolved, _stage == SocraticDialogStage.resolved),
            ],
          ),

          const SizedBox(height: 18),

          // Dynamic Stage View
          if (_stage == SocraticDialogStage.empathy) ...[
            Container(
              key: const Key('socratic_empathy_view'),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF6366F1).withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
              ),
              child: Text(
                _data.empathyMessage,
                style: const TextStyle(fontSize: 14.5, color: Color(0xFFE0E7FF), height: 1.4),
              ),
            ),
            const SizedBox(height: 18),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                key: const Key('socratic_next_button'),
                onPressed: _nextStage,
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.accentPrimary),
                icon: const Icon(Icons.arrow_forward_rounded, size: 18, color: Colors.white),
                label: const Text('Sezgiye Bakalım', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ] else if (_stage == SocraticDialogStage.grounding) ...[
            Container(
              key: const Key('socratic_grounding_view'),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF0284C7).withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.3)),
              ),
              child: Text(
                _data.groundingExample,
                style: const TextStyle(fontSize: 14.5, color: Color(0xFFE0F2FE), height: 1.4),
              ),
            ),
            const SizedBox(height: 18),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                key: const Key('socratic_next_button'),
                onPressed: _nextStage,
                style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0284C7)),
                icon: const Icon(Icons.psychology_rounded, size: 18, color: Colors.white),
                label: const Text('Kuralı Keşfet', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ] else if (_stage == SocraticDialogStage.selfDiscovery) ...[
            Container(
              key: const Key('socratic_discovery_view'),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF59E0B).withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFF59E0B).withValues(alpha: 0.3)),
              ),
              child: Text(
                _data.discoveryQuestion,
                style: const TextStyle(fontSize: 14.5, color: Color(0xFFFEF3C7), height: 1.4, fontWeight: FontWeight.w500),
              ),
            ),
            if (_feedbackMessage != null) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: (_isError ? AppColors.accentWarning : AppColors.accentCorrect).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _feedbackMessage!,
                  style: TextStyle(
                    fontSize: 13,
                    color: _isError ? const Color(0xFFFDE68A) : AppColors.accentCorrect,
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    key: const Key('socratic_input_field'),
                    controller: _discoveryController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Fark ettiğin kuralı kendi cümlenle yaz...',
                      hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                      filled: true,
                      fillColor: AppColors.bgPrimary,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide.none),
                    ),
                    onSubmitted: (_) => _submitDiscovery(),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  key: const Key('socratic_submit_discovery'),
                  onPressed: _submitDiscovery,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accentCorrect,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                  child: const Text('Dene', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ] else if (_stage == SocraticDialogStage.resolved) ...[
            Container(
              key: const Key('socratic_resolved_view'),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.accentCorrect.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.accentCorrect.withValues(alpha: 0.5)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.check_circle_rounded, color: AppColors.accentCorrect, size: 22),
                      SizedBox(width: 8),
                      Text(
                        'Başardın!',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.accentCorrect),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _feedbackMessage ?? 'Harikasın! Bu temel kuralı kendi başına keşfettin.',
                    style: const TextStyle(fontSize: 14, color: AppColors.textPrimary, height: 1.35),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '+0.10 BKT Güven Bonusu Kazandın 🎯',
                    style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600, color: Color(0xFF6EE7B7)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton(
                key: const Key('socratic_next_button'),
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.accentCorrect),
                child: const Text('Çözüme Devam Et', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStepPill(String label, bool isActive, bool isPassed) {
    final Color bgColor = isPassed
        ? AppColors.accentCorrect.withValues(alpha: 0.25)
        : isActive
            ? AppColors.accentPrimary.withValues(alpha: 0.25)
            : AppColors.bgPrimary;

    final Color textColor = isPassed
        ? AppColors.accentCorrect
        : isActive
            ? const Color(0xFFA5B4FC)
            : AppColors.textMuted;

    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 6),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isActive ? AppColors.accentPrimary : Colors.transparent,
            width: 1,
          ),
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: textColor),
        ),
      ),
    );
  }
}
