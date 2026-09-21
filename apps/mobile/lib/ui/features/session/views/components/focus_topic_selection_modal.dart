import 'package:flutter/material.dart';
import '../../../../../core/services/haptic_feedback_service.dart';
import '../../../../../data/services/focus_api_service.dart';
import '../../view_models/focus_session_view_model.dart';
import '../focus_session_screen.dart';

void showFocusTopicSelectionModal(BuildContext context) {
  showModalBottomSheet(
    context: context,
    backgroundColor: const Color(0xFF0F172A),
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.psychology_outlined, color: Color(0xFF38BDF8), size: 24),
                    const SizedBox(width: 10),
                    const Text(
                      'Focus Kernel: Pedagojik Konu Seçimi',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white70, size: 20),
                      onPressed: () => Navigator.of(ctx).pop(),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-QF1',
                  title: '2. Dereceden Denklem Çarpanlara Ayırma',
                  subtitle: 'x² + 5x + 6 = 0 (Çarpan, Dal, Çözüm Kümeleri)',
                  icon: Icons.functions,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-QF1',
                          b: 5,
                          c: 6,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-LIN1',
                  title: '1. Dereceden Doğrusal Denklem & Terazi Modeli',
                  subtitle: '2x + 4 = 10 (Terim Yalıtımı, Katsayı Bölme)',
                  icon: Icons.balance,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-LIN1',
                          a: 2,
                          b: 4,
                          c: 10,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-INEQ1',
                  title: '1. Dereceden Doğrusal Eşitsizlikler',
                  subtitle: '-3x + 5 ≤ 14 (Negatif Bölmede Yön Değiştirme)',
                  icon: Icons.compare_arrows,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-INEQ1',
                          a: -3,
                          b: 5,
                          c: 14,
                          comparator: '<=',
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-PAR1',
                  title: 'Paraboller & Tepe Noktası (r, k)',
                  subtitle: 'f(x) = x² - 4x + 3 (r = -b/2a, k = f(r), Ekstremum)',
                  icon: Icons.show_chart,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-PAR1',
                          a: 1,
                          b: -4,
                          c: 3,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-POLY1',
                  title: 'Polinomlar & Kalan Teoremi',
                  subtitle: 'P(x) = x² + 2x - 3, Bölen: x - 1 (Kök & Kalan P(d))',
                  icon: Icons.calculate_outlined,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-POLY1',
                          a: 1,
                          b: 2,
                          c: -3,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-TRIG1',
                  title: 'Trigonometri & Birim Çember',
                  subtitle: '2sin(x) - 1 = 0 (Oran, 1. Bölge Açısı, 2. Bölge Simetrik Kökü)',
                  icon: Icons.change_circle_outlined,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-TRIG1',
                          a: 2,
                          b: 0,
                          c: 1,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-LOG1',
                  title: 'Logaritma & Tanım Kümesi',
                  subtitle: 'log₂(x - 3) = 3 (Üstel Dönüşüm, Kök Çözümü, Tanım Doğrulama)',
                  icon: Icons.auto_graph,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-LOG1',
                          a: 2,
                          b: 3,
                          c: 3,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-LIM1',
                  title: 'Limit & 0/0 Belirsizliği',
                  subtitle: 'lim_{x→2} (x² - 4)/(x - 2) (Belirsizlik, Sadeleştirme, Reel Limit)',
                  icon: Icons.functions_rounded,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-LIM1',
                          a: 2,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-DERIV1',
                  title: 'Polinom Türevi & Teğet Doğrusu',
                  subtitle: 'f(x) = x² + 2x + 1, x₀ = 1 (Kuvvet Kuralı, Eğim, Teğet Denklemi)',
                  icon: Icons.show_chart_rounded,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-DERIV1',
                          a: 1,
                          b: 2,
                          c: 1,
                          x0: 1,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 10),
                _buildTopicTile(
                  ctx: ctx,
                  topicId: 'CT-INT1',
                  title: 'Belirli İntegral & Alan Hesabı',
                  subtitle: '∫₀³ (2x) dx (Ters Türev, Sınırlar F(b)-F(a), Net Alan)',
                  icon: Icons.area_chart_rounded,
                  onTap: () {
                    Navigator.of(ctx).pop();
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => FocusSessionScreen(
                          topicId: 'CT-INT1',
                          a: 2,
                          b: 0,
                          c: 3,
                          divisorRoot: 0,
                          viewModel: FocusSessionViewModel(apiService: FocusApiService()),
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      );
    },
  );
}

Widget _buildTopicTile({
  required BuildContext ctx,
  required String topicId,
  required String title,
  required String subtitle,
  required IconData icon,
  required VoidCallback onTap,
}) {
  return InkWell(
    onTap: () {
      HapticFeedbackService().selectionClick();
      onTap();
    },
    borderRadius: BorderRadius.circular(12),
    child: Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B).withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF38BDF8).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: const Color(0xFF38BDF8), size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_right, color: Color(0xFF94A3B8), size: 18),
        ],
      ),
    ),
  );
}
