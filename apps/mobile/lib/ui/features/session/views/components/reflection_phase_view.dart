import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../../../../core/services/haptic_feedback_service.dart';
import '../../../../../data/services/mistake_vault_service.dart';
import '../../../atlas/living_knowledge_atlas_view.dart';
import '../../../math_lab/views/math_lab_hub_screen.dart';
import '../../../vault/mistake_autopsy_view.dart';

class ReflectionPhaseView extends StatefulWidget {
  final VoidCallback onCompleted;

  const ReflectionPhaseView({
    super.key,
    required this.onCompleted,
  });

  @override
  State<ReflectionPhaseView> createState() => _ReflectionPhaseViewState();
}

class _ReflectionPhaseViewState extends State<ReflectionPhaseView> {
  double _confidenceLevel = 0.85;

  @override
  Widget build(BuildContext context) {
    final safeConfidence = _confidenceLevel.isFinite && !_confidenceLevel.isNaN
        ? math.max(0.0, math.min(1.0, _confidenceLevel))
        : 0.85;
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Icon(Icons.psychology, color: Color(0xFFF59E0B), size: 48),
          const SizedBox(height: 16),
          const Text(
            "Faz 4: Metabilişsel Kalibrasyon (3 Dk)",
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            "Brier Proper Scoring kuralına göre çözüm adımlarındaki kendi güven düzeyini değerlendir:",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: [
                Text(
                  "Zihinsel Güven Skoru: %${(safeConfidence * 100).toInt()}",
                  style: const TextStyle(
                    color: Color(0xFF38BDF8),
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Slider(
                  value: safeConfidence,
                  min: 0.0,
                  max: 1.0,
                  divisions: 20,
                  activeColor: const Color(0xFF38BDF8),
                  inactiveColor: const Color(0xFF334155),
                  onChanged: (val) {
                    if (val.isFinite && !val.isNaN) {
                      HapticFeedbackService().selectionClick();
                      setState(() => _confidenceLevel = math.max(0.0, math.min(1.0, val)));
                    }
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF59E0B),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            onPressed: () {
              HapticFeedbackService().stepSuccess();
              widget.onCompleted();
            },
            child: const Text("Seansı Tamamla ve Kilitle"),
          ),
        ],
      ),
    );
  }
}

class CircadianLockView extends StatelessWidget {
  final void Function(int tabIndex)? onNavigateToTab;

  const CircadianLockView({
    super.key,
    this.onNavigateToTab,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.nightlight_round, color: Color(0xFF818CF8), size: 64),
          const SizedBox(height: 20),
          const Text(
            "20 Dakikalık Günlük Seans Tamamlandı!",
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          const Text(
            "Walker & Stickgold sirkadiyen konsolidasyon bariyeri devrede. NREM/REM uykusu gerçekleşmeden aynı gün içinde yapılan ek tekrarlar hafıza stabilitesine katkı sağlamaz.",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 14, height: 1.5),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF312E81)),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.lock_clock, color: Color(0xFF818CF8), size: 20),
                SizedBox(width: 10),
                Text(
                  "Sirkadiyen Kilit: 14 Saat Aktif",
                  style: TextStyle(color: Color(0xFFC7D2FE), fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
          const Text(
            "Seans kilitli olsa da diğer bilişsel merkezleri serbestçe keşfedebilirsiniz:",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
          ),
          const SizedBox(height: 16),
          // Hub Navigation Action Buttons
          _buildCircadianActionTile(
            key: const Key('circadian_to_atlas_button'),
            title: "Zihin Atlasını İncele (246 Düğüm)",
            subtitle: "Öğrenme rotanı, ZPD sınırlarını ve düğüm ustalıklarını keşfet.",
            icon: Icons.hub_outlined,
            accentColor: const Color(0xFF10B981),
            onTap: () {
              HapticFeedbackService().selectionClick();
              if (onNavigateToTab != null) {
                onNavigateToTab!(1);
              } else {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const Scaffold(body: SafeArea(child: LivingKnowledgeAtlasView()))),
                );
              }
            },
          ),
          const SizedBox(height: 10),
          _buildCircadianActionTile(
            key: const Key('circadian_to_math_lab_button'),
            title: "Matematik Laboratuvarında Çalış",
            subtitle: "El-Harezmi, Birim Çember, Türev ve Riemann kanvaslarını serbestçe dene.",
            icon: Icons.architecture,
            accentColor: const Color(0xFF38BDF8),
            onTap: () {
              HapticFeedbackService().selectionClick();
              if (onNavigateToTab != null) {
                onNavigateToTab!(2);
              } else {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const MathLabHubScreen()),
                );
              }
            },
          ),
          const SizedBox(height: 10),
          _buildCircadianActionTile(
            key: const Key('circadian_to_vault_button'),
            title: "Hata Kasası & Bilişsel Analiz",
            subtitle: "Geçmiş hata otopsilerini incele ve Paas bilişsel yük eğrilerini gör.",
            icon: Icons.biotech_rounded,
            accentColor: const Color(0xFFF43F5E),
            onTap: () {
              HapticFeedbackService().selectionClick();
              if (onNavigateToTab != null) {
                onNavigateToTab!(3);
              } else {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => MistakeAutopsyView(
                      mistakes: MistakeVaultService.instance.mistakes,
                      onStartBossBattle: () => HapticFeedbackService().stepSuccess(),
                    ),
                  ),
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildCircadianActionTile({
    required Key key,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color accentColor,
    required VoidCallback onTap,
  }) {
    return InkWell(
      key: key,
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF334155)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: accentColor.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: accentColor, size: 22),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded, color: Color(0xFF64748B), size: 14),
          ],
        ),
      ),
    );
  }
}
