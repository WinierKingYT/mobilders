import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/app_theme.dart';
import '../../../../domain/models/solution_step.dart';
import '../../touchpad/math_touchpad.dart';
import '../view_models/session_view_model.dart';

class SessionScreen extends StatefulWidget {
  const SessionScreen({super.key});

  @override
  State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _handleSubmit(SessionViewModel viewModel) async {
    final text = _inputController.text;
    if (text.trim().isEmpty) return;

    final result = await viewModel.submitStep(text);
    if (result != null && mounted) {
      if (result.isValid) {
        _inputController.clear();
      }
      _scrollToBottom();
    }
  }

  @override
  Widget build(BuildContext context) {
    final viewModel = context.watch<SessionViewModel>();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          children: [
            Text(
              'Düğüm: ${viewModel.nodeId}',
              style: const TextStyle(fontSize: 13, color: AppColors.accentPrimary, letterSpacing: 1),
            ),
            const SizedBox(height: 2),
            Text(
              viewModel.targetEquation,
              style: const TextStyle(fontSize: 17, fontFamily: 'monospace', fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.lightbulb_outline_rounded, color: AppColors.accentWarning),
            tooltip: '💡 Takıldım (Sokratik İpucu)',
            onPressed: () => _showSocraticHint(context, viewModel),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(
            value: viewModel.currentPl,
            backgroundColor: AppColors.bgSurface,
            valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accentCorrect),
            minHeight: 3,
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Middle 45%: Solution Steps Whiteboard Canvas
            Expanded(
              child: viewModel.steps.isEmpty
                  ? _buildEmptyState(viewModel)
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      itemCount: viewModel.steps.length,
                      itemBuilder: (context, index) {
                        final step = viewModel.steps[index];
                        return _buildStepCard(context, step, index, viewModel);
                      },
                    ),
            ),

            // Solution Completed Banner
            if (viewModel.isTargetReached)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
                color: AppColors.accentCorrect.withOpacity(0.15),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.check_circle_rounded, color: AppColors.accentCorrect, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Tebrikler! Denklem Çözüldü.',
                      style: TextStyle(
                        color: AppColors.accentCorrect,
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
              ),

            // Active Input Live Preview Strip
            Container(
              color: AppColors.bgPrimary,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Text(
                    'Adım ${viewModel.steps.length + 1}:',
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ValueListenableBuilder<TextEditingValue>(
                      valueListenable: _inputController,
                      builder: (context, value, _) {
                        return Text(
                          value.text.isEmpty ? '...' : value.text,
                          style: TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 18,
                            color: value.text.isEmpty ? AppColors.textMuted : AppColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),

            const Divider(height: 1, color: AppColors.bgCard),

            // Bottom 40%: Dual-mode Input Area (Touchpad or Virtual Keyboard)
            MathTouchpad(
              controller: _inputController,
              inputMode: viewModel.inputMode,
              onModeChanged: viewModel.setInputMode,
              isSubmitting: viewModel.isSubmitting,
              onSubmit: () => _handleSubmit(viewModel),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(SessionViewModel viewModel) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.edit_note_rounded, size: 56, color: AppColors.textMuted.withOpacity(0.5)),
            const SizedBox(height: 12),
            const Text(
              'Çözüm Tahtası Hazır',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 6),
            Text(
              'Aşağıdaki matematik touchpadini kullanarak ilk adımı atın.\nÖrn: ${viewModel.targetEquation}',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: AppColors.textMuted),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepCard(BuildContext context, SolutionStep step, int index, SessionViewModel viewModel) {
    final bool isBug = step.detectedBug != null;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: step.isValid
              ? AppColors.accentCorrect.withOpacity(0.6)
              : isBug
                  ? AppColors.accentWarning.withOpacity(0.6)
                  : AppColors.accentError.withOpacity(0.4),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Step Header
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 10, 10, 6),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 12,
                  backgroundColor: step.isValid ? AppColors.accentCorrect : AppColors.accentWarning,
                  child: Icon(
                    step.isValid ? Icons.check : Icons.priority_high_rounded,
                    size: 14,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'Adım ${step.stepNumber}',
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textSecondary),
                ),
                const Spacer(),
                Text(
                  '${step.elapsedMs} ms',
                  style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                ),
                IconButton(
                  icon: const Icon(Icons.undo_rounded, size: 18, color: AppColors.textMuted),
                  tooltip: 'Bu adıma geri dön (Dallanmayı sıfırla)',
                  onPressed: () => viewModel.rollbackToStep(index),
                ),
              ],
            ),
          ),

          // Step Content
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
            child: Text(
              step.userExpression,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 19,
                fontWeight: FontWeight.w600,
                decoration: isBug ? TextDecoration.lineThrough : null,
                decorationColor: AppColors.accentWarning,
                color: isBug ? AppColors.accentWarning : AppColors.textPrimary,
              ),
            ),
          ),

          // Misconception Card (Mental Contrast)
          if (isBug)
            Container(
              margin: const EdgeInsets.fromLTRB(10, 8, 10, 10),
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.accentWarning.withOpacity(0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: AppColors.accentWarning, size: 16),
                      const SizedBox(width: 6),
                      Text(
                        'Kavramsal Yanılgı: ${step.detectedBug!.bugId ?? "Kural Dışı"}',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: AppColors.accentWarning,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    step.detectedBug!.description,
                    style: const TextStyle(fontSize: 13, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '💡 Sokratik Yönlendirme: ${step.detectedBug!.remediationDirective}',
                    style: const TextStyle(
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                      color: AppColors.accentCorrect,
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 6),
        ],
      ),
    );
  }

  void _showSocraticHint(BuildContext context, SessionViewModel viewModel) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.bgSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.lightbulb_rounded, color: AppColors.accentWarning),
                  SizedBox(width: 8),
                  Text(
                    'Sokratik İpucu Düzeyi 1',
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                'Hedef denklem: ${viewModel.targetEquation}\n'
                'Tüm terimleri bir tarafta toplayıp sağ tarafı sıfır yapmayı düşündün mü?',
                style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
              ),
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerRight,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(backgroundColor: AppColors.accentPrimary),
                  child: const Text('Anladım, Denedim', style: TextStyle(color: Colors.white)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
