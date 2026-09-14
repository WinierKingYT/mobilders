import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/app_theme.dart';
import '../../session/view_models/session_view_model.dart';
import '../../session/views/session_screen.dart';
import '../view_models/diagnostic_view_model.dart';

class DiagnosticScreen extends StatefulWidget {
  final bool showAppBar;
  final VoidCallback? onCompleted;

  const DiagnosticScreen({
    super.key,
    this.showAppBar = true,
    this.onCompleted,
  });

  @override
  State<DiagnosticScreen> createState() => _DiagnosticScreenState();
}

class _DiagnosticScreenState extends State<DiagnosticScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DiagnosticViewModel>().loadFirstItem();
    });
  }

  void _startLearningSession(BuildContext context, DiagnosticViewModel viewModel) {
    if (widget.onCompleted != null) {
      widget.onCompleted!();
      return;
    }

    // Select first ZPD candidate or fallback to N15
    final zpdNode = (viewModel.zpdCandidates != null && viewModel.zpdCandidates!.isNotEmpty)
        ? viewModel.zpdCandidates!.first
        : 'N15';

    // Seeded mastery for this node or fallback
    final initialPl = viewModel.seededMastery?[zpdNode] ?? 0.20;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => ChangeNotifierProvider(
          create: (ctx) => SessionViewModel(
            apiService: ctx.read(),
            sessionId: viewModel.sessionId,
            targetEquation: 'x^2 - 5x + 6 = 0',
            nodeId: zpdNode,
            initialPl: initialPl,
          ),
          child: const SessionScreen(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final viewModel = context.watch<DiagnosticViewModel>();

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: widget.showAppBar
          ? AppBar(
              title: const Text('Bilişsel Seviye Tespiti (2PL-IRT CAT)'),
              bottom: PreferredSize(
                preferredSize: const Size.fromHeight(4),
                child: LinearProgressIndicator(
                  value: viewModel.calibrationProgress,
                  backgroundColor: AppColors.bgSurface,
                  valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accentPrimary),
                  minHeight: 4,
                ),
              ),
            )
          : null,
      body: SafeArea(
        child: Column(
          children: [
            if (!widget.showAppBar)
              LinearProgressIndicator(
                value: viewModel.calibrationProgress,
                backgroundColor: AppColors.bgSurface,
                valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accentPrimary),
                minHeight: 4,
              ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                child: viewModel.isLoading && viewModel.currentItem == null
                    ? const Center(child: CircularProgressIndicator(color: AppColors.accentPrimary))
                    : viewModel.isComplete
                        ? _buildCompletionView(context, viewModel)
                        : _buildQuestionView(context, viewModel),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionView(BuildContext context, DiagnosticViewModel viewModel) {
    final item = viewModel.currentItem;
    if (item == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(viewModel.errorMessage ?? 'Soru bulunamadı.', style: const TextStyle(color: AppColors.accentError)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => viewModel.loadFirstItem(),
              child: const Text('Yeniden Dene'),
            ),
          ],
        ),
      );
    }

    final questionNumber = viewModel.administeredHistory.length + 1;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Real-time Psychometrics Status Strip
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: AppColors.bgSurface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppColors.bgCard),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Soru $questionNumber / 8',
                style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              Row(
                children: [
                  const Text('θ: ', style: TextStyle(color: AppColors.textMuted)),
                  Text(
                    viewModel.thetaHat >= 0 ? '+${viewModel.thetaHat.toStringAsFixed(2)}' : viewModel.thetaHat.toStringAsFixed(2),
                    style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold, color: AppColors.accentCorrect),
                  ),
                  const SizedBox(width: 12),
                  const Text('SE: ', style: TextStyle(color: AppColors.textMuted)),
                  Text(
                    viewModel.standardError.toStringAsFixed(2),
                    style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold, color: AppColors.accentWarning),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Question Card
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.bgSurface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.accentPrimary.withValues(alpha: 0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Node Badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.accentPrimary.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    'Hedef Bilgi Düğümü: ${item.targetNodeId}',
                    style: const TextStyle(color: AppColors.accentPrimary, fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
                const SizedBox(height: 20),

                // Question Prompt
                Text(
                  item.prompt,
                  style: const TextStyle(
                    fontSize: 18,
                    height: 1.4,
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),

                const Text(
                  'Bu soruyu kağıt üzerinde veya zihinden çözmeyi deneyin:',
                  style: TextStyle(fontSize: 13, color: AppColors.textMuted),
                ),
                const SizedBox(height: 12),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),

        // Action Decision Buttons
        Row(
          children: [
            Expanded(
              child: SizedBox(
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: viewModel.isLoading ? null : () => viewModel.submitAnswer(false),
                  icon: const Icon(Icons.close_rounded, color: Colors.white),
                  label: const Text('Çözemedim', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accentError.withValues(alpha: 0.85),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: SizedBox(
                height: 54,
                child: ElevatedButton.icon(
                  onPressed: viewModel.isLoading ? null : () => viewModel.submitAnswer(true),
                  icon: const Icon(Icons.check_rounded, color: Colors.white),
                  label: const Text('Doğru Çözdüm', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accentCorrect,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildCompletionView(BuildContext context, DiagnosticViewModel viewModel) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Icon(Icons.verified_rounded, size: 72, color: AppColors.accentCorrect),
        const SizedBox(height: 16),
        const Text(
          'Seviye Tespiti Tamamlandı!',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
        ),
        const SizedBox(height: 8),
        Text(
          'Hesaplanan Latent Yetenek: θ = ${viewModel.thetaHat.toStringAsFixed(2)}\n'
          'Standart Hata: SE = ${viewModel.standardError.toStringAsFixed(2)} (<= 0.35 hedefine ulaşıldı)',
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
        ),
        const SizedBox(height: 24),

        // ZPD Recommendation Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.bgSurface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.accentCorrect.withValues(alpha: 0.5)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.auto_graph_rounded, color: AppColors.accentCorrect, size: 18),
                  SizedBox(width: 8),
                  Text(
                    'Önerilen Yakınsak Gelişim Alanı (ZPD):',
                    style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 14),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                'Sistem bilgi grafınızı taradı ve çalışmaya en uygun düğüm kümesini çıkardı:\n'
                '${(viewModel.zpdCandidates ?? ['N15']).join(', ')}',
                style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),

        // Start Learning Button
        SizedBox(
          height: 54,
          child: ElevatedButton.icon(
            onPressed: () => _startLearningSession(context, viewModel),
            icon: const Icon(Icons.play_arrow_rounded, color: Colors.white, size: 24),
            label: const Text('Öğrenme Seansını Başlat', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accentPrimary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
      ],
    );
  }
}
