import 'package:flutter/material.dart';
import '../../../core/app_theme.dart';
import '../../../../domain/models/solution_step.dart';
import '../../touchpad/instant_math_sanitizer.dart';
import '../../touchpad/math_touchpad.dart';
import '../../touchpad/zero_layout_shift_dock.dart';
import '../view_models/session_view_model.dart';

/// Zen Focus Overlay: Completely distraction-free, high-contrast math working environment
class ZenFocusOverlay extends StatelessWidget {
  final SessionViewModel viewModel;
  final TextEditingController inputController;
  final VoidCallback onExitZen;
  final VoidCallback onSubmit;

  const ZenFocusOverlay({
    super.key,
    required this.viewModel,
    required this.inputController,
    required this.onExitZen,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.zenBg,
      body: SafeArea(
        child: Column(
          children: [
            // Zen Header (Minimalist exit & focus badge)
            _buildHeader(context),

            // Zen Focus Stage (Target Formula & Rainbow Live Step)
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 12),
                    // Target Equation Obsidian Card
                    _buildTargetEquationCard(),
                    const SizedBox(height: 24),

                    // Past Steps Mini Breadcrumbs
                    if (viewModel.steps.isNotEmpty)
                      _buildStepsBreadcrumb(viewModel.steps),

                    const SizedBox(height: 24),

                    // Current Active Step (Glowing focus ring + Rainbow Brackets)
                    _buildActiveStepCard(),
                  ],
                ),
              ),
            ),

            // Bottom Zero Layout Shift Input Dock
            ZeroLayoutShiftDock(
              currentMode: viewModel.inputMode,
              onModeChanged: viewModel.setInputMode,
              isZenModeActive: true,
              onToggleZenMode: onExitZen,
              child: MathTouchpad(
                controller: inputController,
                inputMode: viewModel.inputMode,
                onModeChanged: viewModel.setInputMode,
                onSubmit: onSubmit,
                isSubmitting: viewModel.isSubmitting,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Color(0xFF38BDF8),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              const Text(
                'ZEN ODAK MODU',
                style: TextStyle(
                  color: Color(0xFF38BDF8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                ),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.close_rounded, color: AppColors.textMuted, size: 22),
            tooltip: 'Zen Modundan Çık',
            onPressed: onExitZen,
          ),
        ],
      ),
    );
  }

  Widget _buildTargetEquationCard() {
    final prettyTarget = MathTypography.toPrettyMath(viewModel.targetEquation);

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
      decoration: BoxDecoration(
        color: AppColors.zenSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.08),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.5),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          const Text(
            'HEDEF FORMÜL',
            style: TextStyle(
              color: AppColors.textMuted,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.4,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            prettyTarget,
            textAlign: TextAlign.center,
            style: MathTypography.formulaDisplay,
          ),
        ],
      ),
    );
  }

  Widget _buildStepsBreadcrumb(List<SolutionStep> steps) {
    return Wrap(
      spacing: 8,
      runSpacing: 6,
      alignment: WrapAlignment.center,
      children: steps.map((s) {
        final isValid = s.isValid;
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: isValid
                ? AppColors.accentCorrect.withValues(alpha: 0.15)
                : AppColors.accentError.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isValid ? AppColors.accentCorrect : AppColors.accentError,
              width: 0.8,
            ),
          ),
          child: Text(
            MathTypography.toPrettyMath(s.userExpression),
            style: TextStyle(
              fontSize: 13,
              fontFamily: 'monospace',
              fontWeight: FontWeight.w600,
              color: isValid ? AppColors.accentCorrect : AppColors.accentError,
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildActiveStepCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      decoration: BoxDecoration(
        color: AppColors.zenSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppColors.zenGlow.withValues(alpha: 0.5),
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.zenGlow.withValues(alpha: 0.12),
            blurRadius: 18,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Adım ${viewModel.steps.length + 1}',
                style: const TextStyle(
                  color: AppColors.zenGlow,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.0,
                ),
              ),
              const Spacer(),
              const Text(
                'Anlık Sanity Kontrollü',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 10,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ValueListenableBuilder<TextEditingValue>(
            valueListenable: inputController,
            builder: (context, value, _) {
              if (value.text.isEmpty) {
                return const Text(
                  'Adımınızı yazın...',
                  style: TextStyle(
                    fontSize: 20,
                    fontFamily: 'monospace',
                    color: AppColors.textMuted,
                  ),
                );
              }

              final spans = InstantMathSanitizer.buildRainbowSpans(
                value.text,
                defaultStyle: const TextStyle(
                  fontSize: 22,
                  fontFamily: 'monospace',
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
              );

              return RichText(
                text: TextSpan(children: spans),
              );
            },
          ),
        ],
      ),
    );
  }
}
