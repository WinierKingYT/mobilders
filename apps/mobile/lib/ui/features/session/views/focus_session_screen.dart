import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../core/app_theme.dart';
import '../../root_pedagogy/number_line_balance_canvas.dart';
import 'unit_circle_canvas.dart';
import 'dynamic_tangent_canvas.dart';
import 'riemann_integral_canvas.dart';
import '../view_models/focus_session_view_model.dart';
import '../widgets/socratic_hint_dialog.dart';

/// Full interactive mobile screen for the Focus Kernel multi-topic cognitive session.
class FocusSessionScreen extends StatefulWidget {
  final FocusSessionViewModel? viewModel;
  final String? topicId;
  final int? a;
  final int? b;
  final int? c;
  final String? comparator;
  final int? divisorRoot;
  final int? x0;

  const FocusSessionScreen({
    super.key,
    this.viewModel,
    this.topicId,
    this.a,
    this.b,
    this.c,
    this.comparator,
    this.divisorRoot,
    this.x0,
  });

  @override
  State<FocusSessionScreen> createState() => _FocusSessionScreenState();
}

class _FocusSessionScreenState extends State<FocusSessionScreen> {
  late final TextEditingController _inputController;
  late final FocusNode _inputFocusNode;
  bool _hideTimer = false;

  @override
  void initState() {
    super.initState();
    _inputController = TextEditingController();
    _inputFocusNode = FocusNode();

    // Auto-start episode if not already started
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final vm = widget.viewModel ?? context.read<FocusSessionViewModel>();
      if (vm.episodeId == null && !vm.isSubmitting) {
        vm.startEpisode(
          topicId: widget.topicId ?? 'CT-QF1',
          a: widget.a,
          b: widget.b,
          c: widget.c,
          comparator: widget.comparator,
          divisorRoot: widget.divisorRoot,
          x0: widget.x0,
        );
      }
    });
  }

  @override
  void dispose() {
    _inputController.dispose();
    _inputFocusNode.dispose();
    super.dispose();
  }

  void _handleSubmit(FocusSessionViewModel vm) {
    final text = _inputController.text.trim();
    if (text.isEmpty || vm.isSubmitting) return;

    HapticFeedbackService().selectionClick();

    if (vm.isAwaitingOriginalSelfCorrection) {
      vm.submitOriginalSelfCorrection(text);
    } else if (vm.isRepairing) {
      // Parse integers if list or submit string
      if (text.contains(',')) {
        final parts = text.split(',').map((s) => int.tryParse(s.trim()) ?? s.trim()).toList();
        vm.submitRepairWork(parts);
      } else {
        vm.submitRepairWork(text);
      }
    } else if (vm.isAwaitingTransfer) {
      if (text.contains(',')) {
        final parts = text.split(',').map((s) => int.tryParse(s.trim()) ?? s.trim()).toList();
        vm.submitTransferWork(parts);
      } else {
        vm.submitTransferWork(text);
      }
    } else {
      vm.submitStageAttempt(text);
    }

    _inputController.clear();
  }

  void _openMicroSandbox(BuildContext context, FocusSessionViewModel vm) {
    HapticFeedbackService().mediumImpact();
    RootCanvasMode initialMode = RootCanvasMode.balanceScale;
    if (vm.topicId == 'CT-INEQ1') {
      initialMode = RootCanvasMode.numberLine;
    } else if (vm.topicId == 'CT-LIN1') {
      initialMode = RootCanvasMode.balanceScale;
    } else if (vm.topicId == 'CT-PAR1') {
      initialMode = RootCanvasMode.numberLine;
    } else if (vm.topicId == 'CT-POLY1') {
      initialMode = RootCanvasMode.pieFraction;
    } else {
      initialMode = RootCanvasMode.balanceScale;
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0F172A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
          top: 12,
          left: 12,
          right: 12,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              NumberLineBalanceCanvas(initialMode: initialMode),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _openUnitCircleModal(BuildContext context) {
    HapticFeedbackService().selectionClick();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0F172A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
          top: 12,
          left: 12,
          right: 12,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const UnitCircleCanvas(initialAngle: 30.0),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _openDynamicTangentModal(BuildContext context, FocusSessionViewModel vm) {
    HapticFeedbackService().selectionClick();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0F172A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
          top: 12,
          left: 12,
          right: 12,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              DynamicTangentCanvas(
                initialX0: (vm.x0 ?? vm.divisorRoot ?? 1).toDouble(),
                initialH: 1.0,
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _openRiemannModal(BuildContext context) {
    HapticFeedbackService().selectionClick();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0F172A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
          top: 12,
          left: 12,
          right: 12,
        ),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const RiemannIntegralCanvas(),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _openSocraticHint(BuildContext context, FocusSessionViewModel vm) {
    HapticFeedbackService().lightImpact();
    SocraticHintDialog.show(
      context,
      targetEquation: vm.targetEquationLatex,
    );
  }

  @override
  Widget build(BuildContext context) {
    return widget.viewModel != null
        ? ChangeNotifierProvider<FocusSessionViewModel>.value(
            value: widget.viewModel!,
            child: _buildBody(context),
          )
        : _buildBody(context);
  }

  Widget _buildBody(BuildContext context) {
    return Consumer<FocusSessionViewModel>(
      builder: (context, vm, _) {
        return Scaffold(
          backgroundColor: AppColors.zenBg,
          body: SafeArea(
            child: Column(
              children: [
                // 1. Top Minimalist Header
                _buildHeader(context, vm),

                // 2. Stage Stepper Bar
                _buildStageStepper(vm),

                // 3. Feedback / Error Banner
                if (vm.errorMessage != null || vm.feedbackMessage != null)
                  _buildNotificationBanner(vm),

                // 4. Main Scrollable Focus Content
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    child: Column(
                      children: [
                        // Target Equation Obsidian Card
                        _buildTargetEquationCard(vm),
                        const SizedBox(height: 16),

                        // Phase Specific Body Card
                        _buildPhaseSpecificBody(vm),
                      ],
                    ),
                  ),
                ),

                // 5. Input Dock (Zero Layout Shift)
                if (!vm.isCompleted && !vm.isProbing)
                  _buildInputDock(vm),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeader(BuildContext context, FocusSessionViewModel vm) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppColors.textMuted, size: 20),
                onPressed: () => Navigator.of(context).maybePop(),
                tooltip: 'Geri',
              ),
              const SizedBox(width: 4),
              Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Color(0xFF38BDF8),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                'FOCUS KERNEL (${vm.topicId})',
                style: const TextStyle(
                  color: Color(0xFF38BDF8),
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                ),
              ),
            ],
          ),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.06),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  'Seq #${vm.currentSequence}',
                  style: const TextStyle(
                    color: AppColors.textMuted,
                    fontSize: 11,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
              const SizedBox(width: 4),
              IconButton(
                key: const Key('focus_toggle_calm_timer_btn'),
                icon: Icon(
                  _hideTimer ? Icons.spa_outlined : Icons.timer_outlined,
                  color: _hideTimer ? const Color(0xFF34D399) : const Color(0xFF38BDF8),
                  size: 20,
                ),
                tooltip: _hideTimer ? 'Süreyi Göster' : 'Süreyi Gizle (Sakin Seans)',
                onPressed: () {
                  HapticFeedbackService().selectionClick();
                  setState(() => _hideTimer = !_hideTimer);
                },
              ),
              if (_hideTimer) ...[
                const SizedBox(width: 4),
                Container(
                  key: const Key('focus_calm_mode_badge'),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFF065F46).withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: const Color(0xFF10B981)),
                  ),
                  child: const Text(
                    '🧘 Sakin Mod',
                    style: TextStyle(
                      color: Color(0xFF34D399),
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
              IconButton(
                icon: const Icon(Icons.toys_rounded, color: Colors.amberAccent, size: 20),
                tooltip: 'Mikro-Kum Havuzu',
                onPressed: () => _openMicroSandbox(context, vm),
              ),
              IconButton(
                icon: const Icon(Icons.lightbulb_rounded, color: Color(0xFF38BDF8), size: 20),
                tooltip: 'Sokratik İskele',
                onPressed: () => _openSocraticHint(context, vm),
              ),
              if (vm.topicId == 'CT-TRIG1')
                IconButton(
                  icon: const Icon(Icons.change_circle_outlined, color: Color(0xFF38BDF8), size: 20),
                  tooltip: 'Birim Çember',
                  onPressed: () => _openUnitCircleModal(context),
                ),
              if (vm.topicId == 'CT-DERIV1')
                IconButton(
                  icon: const Icon(Icons.show_chart_rounded, color: Color(0xFF38BDF8), size: 20),
                  tooltip: 'Dinamik Teğet Simülatörü',
                  onPressed: () => _openDynamicTangentModal(context, vm),
                ),
              if (vm.topicId == 'CT-INT1')
                IconButton(
                  icon: const Icon(Icons.area_chart_rounded, color: Color(0xFF38BDF8), size: 20),
                  tooltip: 'Riemann İntegral Simülatörü',
                  onPressed: () => _openRiemannModal(context),
                ),
              const SizedBox(width: 4),
              IconButton(
                icon: Icon(
                  vm.isZenMode ? Icons.fullscreen_exit_rounded : Icons.fullscreen_rounded,
                  color: vm.isZenMode ? const Color(0xFF38BDF8) : AppColors.textMuted,
                  size: 24,
                ),
                tooltip: 'Zen Modu',
                onPressed: vm.toggleZenMode,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStageStepper(FocusSessionViewModel vm) {
    final List<Map<String, String>> stages;
    if (vm.topicId == 'CT-LIN1') {
      stages = [
        {'id': 'S1_ISOLATE_TERM', 'label': '1. Terim'},
        {'id': 'S2_ISOLATE_VARIABLE', 'label': '2. Katsayı'},
        {'id': 'S3_VERIFY_SOLUTION', 'label': '3. Doğrulama'},
      ];
    } else if (vm.topicId == 'CT-INEQ1') {
      stages = [
        {'id': 'S1_ISOLATE_TERM', 'label': '1. Terim'},
        {'id': 'S2_DIRECTION_AWARE_DIVISION', 'label': '2. Yön Korumalı'},
      ];
    } else if (vm.topicId == 'CT-PAR1') {
      stages = [
        {'id': 'S1_CALCULATE_R', 'label': '1. r = -b/2a'},
        {'id': 'S2_CALCULATE_K', 'label': '2. k = f(r)'},
        {'id': 'S3_EXTREMUM_CLASSIFICATION', 'label': '3. Ekstremum'},
      ];
    } else if (vm.topicId == 'CT-POLY1') {
      stages = [
        {'id': 'S1_ROOT_OF_DIVISOR', 'label': '1. Bölen Kökü'},
        {'id': 'S2_EVALUATE_REMAINDER', 'label': '2. Kalan P(d)'},
      ];
    } else if (vm.topicId == 'CT-TRIG1') {
      stages = [
        {'id': 'S1_ISOLATE_TRIG_VALUE', 'label': '1. Oran'},
        {'id': 'S2_DETERMINE_PRINCIPAL_ANGLE', 'label': '2. Esas Açı'},
        {'id': 'S3_DETERMINE_SECONDARY_ROOT', 'label': '3. İkincil Kök'},
      ];
    } else if (vm.topicId == 'CT-LOG1') {
      stages = [
        {'id': 'S1_EXPONENTIAL_CONVERSION', 'label': '1. Üstel Biçim'},
        {'id': 'S2_ISOLATE_VARIABLE', 'label': '2. Değişken x'},
        {'id': 'S3_VERIFY_DOMAIN_CONSTRAINT', 'label': '3. Tanım Kümesi'},
      ];
    } else if (vm.topicId == 'CT-LIM1') {
      stages = [
        {'id': 'S1_EVALUATE_LIMIT_FORM', 'label': '1. Belirsizlik (0/0)'},
        {'id': 'S2_SIMPLIFY_EXPRESSION', 'label': '2. Sadeleştirme'},
        {'id': 'S3_COMPUTE_FINAL_LIMIT', 'label': '3. Limit Değeri'},
      ];
    } else if (vm.topicId == 'CT-DERIV1') {
      stages = [
        {'id': 'S1_COMPUTE_DERIVATIVE', 'label': '1. f\'(x) Türev'},
        {'id': 'S2_EVALUATE_SLOPE', 'label': '2. m = f\'(x0)'},
        {'id': 'S3_DETERMINE_TANGENT_LINE', 'label': '3. Teğet Doğrusu'},
      ];
    } else if (vm.topicId == 'CT-INT1') {
      stages = [
        {'id': 'S1_FIND_ANTIDERIVATIVE', 'label': '1. F(x) Ters Türev'},
        {'id': 'S2_APPLY_LIMITS', 'label': '2. F(b) - F(a)'},
        {'id': 'S3_COMPUTE_DEFINITE_INTEGRAL', 'label': '3. Belirli İntegral'},
      ];
    } else {
      stages = [
        {'id': 'S1_FACTOR', 'label': '1. Çarpan'},
        {'id': 'S2_BRANCH', 'label': '2. Dal'},
        {'id': 'S3_SOLVE_FACTOR_EQUATIONS', 'label': '3. Çözüm'},
        {'id': 'S4_COMPLETE_SOLUTION_SET', 'label': '4. Küme'},
      ];
    }

    final currentStage = vm.currentStage;
    final isCompleted = vm.isCompleted;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: stages.map((st) {
          final id = st['id']!;
          final label = st['label']!;
          final isCurrent = currentStage == id && !isCompleted;
          final isPast = isCompleted || _stageOrder(currentStage) > _stageOrder(id);

          return Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 4),
              decoration: BoxDecoration(
                color: isCurrent
                    ? const Color(0xFF38BDF8).withValues(alpha: 0.15)
                    : isPast
                        ? const Color(0xFF10B981).withValues(alpha: 0.12)
                        : Colors.transparent,
                borderRadius: BorderRadius.circular(6),
                border: isCurrent
                    ? Border.all(color: const Color(0xFF38BDF8), width: 1)
                    : null,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (isPast)
                    const Icon(Icons.check_circle_rounded, color: Color(0xFF10B981), size: 12)
                  else if (isCurrent)
                    const Icon(Icons.play_arrow_rounded, color: Color(0xFF38BDF8), size: 12),
                  const SizedBox(width: 4),
                  Text(
                    label,
                    style: TextStyle(
                      color: isCurrent
                          ? const Color(0xFF38BDF8)
                          : isPast
                              ? const Color(0xFF10B981)
                              : AppColors.textMuted,
                      fontSize: 10,
                      fontWeight: isCurrent ? FontWeight.bold : FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  int _stageOrder(String stage) {
    switch (stage) {
      case 'S1_FACTOR':
      case 'S1_ISOLATE_TERM':
      case 'S1_CALCULATE_R':
      case 'S1_ROOT_OF_DIVISOR':
      case 'S1_ISOLATE_TRIG_VALUE':
      case 'S1_EXPONENTIAL_CONVERSION':
      case 'S1_EVALUATE_LIMIT_FORM':
      case 'S1_COMPUTE_DERIVATIVE':
      case 'S1_FIND_ANTIDERIVATIVE':
        return 1;
      case 'S2_BRANCH':
      case 'S2_ISOLATE_VARIABLE':
      case 'S2_DIRECTION_AWARE_DIVISION':
      case 'S2_CALCULATE_K':
      case 'S2_EVALUATE_REMAINDER':
      case 'S2_DETERMINE_PRINCIPAL_ANGLE':
      case 'S2_SIMPLIFY_EXPRESSION':
      case 'S2_EVALUATE_SLOPE':
      case 'S2_APPLY_LIMITS':
        return 2;
      case 'S3_SOLVE_FACTOR_EQUATIONS':
      case 'S3_VERIFY_SOLUTION':
      case 'S3_EXTREMUM_CLASSIFICATION':
      case 'S3_DETERMINE_SECONDARY_ROOT':
      case 'S3_VERIFY_DOMAIN_CONSTRAINT':
      case 'S3_COMPUTE_FINAL_LIMIT':
      case 'S3_DETERMINE_TANGENT_LINE':
      case 'S3_COMPUTE_DEFINITE_INTEGRAL':
        return 3;
      case 'S4_COMPLETE_SOLUTION_SET':
        return 4;
      default:
        return 0;
    }
  }

  Widget _buildNotificationBanner(FocusSessionViewModel vm) {
    final isError = vm.errorMessage != null;
    final message = vm.errorMessage ?? vm.feedbackMessage!;
    final isTriumph = !isError && (
      message.contains('Harika') ||
      message.contains('Başarılı') ||
      message.contains('Tebrikler') ||
      message.contains('kaptın') ||
      message.contains('Doğru') ||
      message.contains('Tamamlandı')
    );
    final color = isError
        ? const Color(0xFFEF4444)
        : (isTriumph ? const Color(0xFF10B981) : const Color(0xFF38BDF8));

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Icon(
            isError
                ? Icons.error_outline_rounded
                : (isTriumph ? Icons.stars_rounded : Icons.info_outline_rounded),
            color: color,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w500),
            ),
          ),
          if (isError)
            IconButton(
              icon: const Icon(Icons.close, size: 14, color: AppColors.textMuted),
              onPressed: vm.clearError,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
            ),
        ],
      ),
    );
  }

  Widget _buildTargetEquationCard(FocusSessionViewModel vm) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: AppColors.zenSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.4),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'HEDEF FORMÜL (${vm.topicId})',
                style: const TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              _buildPhaseBadge(vm.currentPhase),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            MathTypography.toPrettyMath(vm.targetEquationLatex),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 26,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPhaseBadge(String phase) {
    Color color;
    String label;
    switch (phase) {
      case 'COMPLETED':
        color = const Color(0xFF10B981);
        label = 'TAMAMLANDI';
        break;
      case 'PROBING':
        color = const Color(0xFFF59E0B);
        label = 'TEŞHİS PROBU';
        break;
      case 'REPAIRING':
        color = const Color(0xFFEF4444);
        label = 'MÜDAHALE';
        break;
      case 'AWAITING_ORIGINAL_SELF_CORRECTION':
        color = const Color(0xFF8B5CF6);
        label = 'ÖZ-DÜZELTME';
        break;
      case 'AWAITING_TRANSFER':
        color = const Color(0xFF06B6D4);
        label = 'TRANSFER GÖREVİ';
        break;
      default:
        color = const Color(0xFF38BDF8);
        label = 'ÇALIŞMA ALANI';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildPhaseSpecificBody(FocusSessionViewModel vm) {
    if (vm.isCompleted) {
      return _buildCompletedCard(vm);
    }
    if (vm.isProbing) {
      return _buildProbingCard(vm);
    }
    if (vm.isRepairing) {
      return _buildRepairingCard(vm);
    }
    if (vm.isAwaitingOriginalSelfCorrection) {
      return _buildSelfCorrectionCard(vm);
    }
    if (vm.isAwaitingTransfer) {
      return _buildTransferCard(vm);
    }
    return _buildWorkspaceStageGuidance(vm);
  }

  Widget _buildWorkspaceStageGuidance(FocusSessionViewModel vm) {
    String title;
    String instruction;
    String example;

    switch (vm.currentStage) {
      case 'S1_FACTOR':
        title = 'Aşama 1: Faktör Çiftini Bulun';
        instruction =
            'Toplamı ${vm.b}, çarpımı ${vm.c} olan iki tam sayıyı virgülle ayırarak girin.';
        example = 'Örnek: 2, 3';
        break;
      case 'S2_BRANCH':
        title = 'Aşama 2: Çarpan Denklemlerine Ayırın';
        instruction = 'Bulduğunuz çarpanlarla denklemi iki ayrı sıfır eşitliğine bölün.';
        example = 'Örnek: x+2=0 or x+3=0';
        break;
      case 'S3_SOLVE_FACTOR_EQUATIONS':
        title = 'Aşama 3: Kökleri Çözün';
        instruction = 'Ayrılan iki 1. derece denklemin x köklerini hesaplayın.';
        example = 'Örnek: x=-2, x=-3';
        break;
      case 'S4_COMPLETE_SOLUTION_SET':
        title = 'Aşama 4: Çözüm Kümesini Tamamlayın';
        instruction = 'Her iki kökü nihai çözüm kümesi biçiminde ifade edin.';
        example = 'Örnek: x=-2, x=-3 veya {-2, -3}';
        break;
      case 'S1_ISOLATE_TERM':
        title = 'Aşama 1: Terimi Yalıtın';
        instruction = vm.topicId == 'CT-INEQ1'
            ? 'Sabit terimi diğer tarafa geçirerek ${vm.a}x terimini yalnız bırakın.'
            : 'Terazi modelinde sabit terimi karşı tarafa geçirerek ${vm.a}x terimini yalıtın.';
        example = vm.topicId == 'CT-INEQ1'
            ? 'Örnek: ${vm.a}x ${vm.comparator} ${vm.c - vm.b}'
            : 'Örnek: ${vm.a}x = ${vm.c - vm.b}';
        break;
      case 'S2_ISOLATE_VARIABLE':
        title = 'Aşama 2: Katsayıyı Bölün';
        instruction = 'Her iki tarafı x katsayısına (${vm.a}) bölerek x değerini bulun.';
        example = 'Örnek: x = ${(vm.c - vm.b) ~/ (vm.a == 0 ? 1 : vm.a)}';
        break;
      case 'S2_DIRECTION_AWARE_DIVISION':
        title = 'Aşama 2: Yön Korumalı Bölme';
        instruction = vm.a < 0
            ? 'Negatif sayıya (${vm.a}) böldüğünüz için eşitsizliğin yönünü ters çevirin!'
            : 'Her iki tarafı ${vm.a} sayısına bölerek x aralığını bulun.';
        example = vm.a < 0
            ? 'Örnek: x >= ${(vm.c - vm.b) ~/ (vm.a == 0 ? 1 : vm.a)}'
            : 'Örnek: x <= ${(vm.c - vm.b) ~/ (vm.a == 0 ? 1 : vm.a)}';
        break;
      case 'S3_VERIFY_SOLUTION':
        title = 'Aşama 3: Çözümü Doğrulayın';
        instruction = 'Bulduğunuz x çözümünü teyit edin.';
        example = 'Örnek: ${(vm.c - vm.b) ~/ (vm.a == 0 ? 1 : vm.a)}';
        break;
      case 'S1_CALCULATE_R':
        title = 'Aşama 1: Tepe Noktası Apsisi (r)';
        instruction = 'r = -b / (2a) formülüyle parabolün tepe noktası apsisini bulun.';
        example = 'Örnek: r = 2 veya 2';
        break;
      case 'S2_CALCULATE_K':
        title = 'Aşama 2: Tepe Noktası Ordinatı (k)';
        instruction = 'Bulunan r değerini fonksiyonda yerine yazarak (k = f(r)) tepe noktası ordinatını bulun.';
        example = 'Örnek: k = -1 veya -1';
        break;
      case 'S3_EXTREMUM_CLASSIFICATION':
        title = 'Aşama 3: Ekstremum Karakteri';
        instruction = 'Başkatsayı a işaretine bakarak k ordinatının minimum mu maksimum mu olduğunu belirtin.';
        example = 'Örnek: minimum veya maksimum';
        break;
      case 'S1_ROOT_OF_DIVISOR':
        title = 'Aşama 1: Böleni Sıfıra Eşitleyin';
        instruction = 'Bölen (x - d) = 0 denklemini çözerek yerine yazılacak kök x değerini bulun.';
        example = 'Örnek: x = 1 veya 1';
        break;
      case 'S2_EVALUATE_REMAINDER':
        title = 'Aşama 2: Kalanı Hesaplayın (P(d))';
        instruction = 'Bulunan kökü P(x) polinomunda yerine koyarak kalanı (P(d)) hesaplayın.';
        example = 'Örnek: kalan = 0 veya 0';
        break;
      case 'S1_ISOLATE_TRIG_VALUE':
        title = 'Aşama 1: Trigonometrik Oranı Yalıtın';
        instruction = 'Denklemdeki sin(x) veya cos(x) terimini yalnız bırakarak değerini bulun.';
        example = 'Örnek: 1/2 veya 0.5';
        break;
      case 'S2_DETERMINE_PRINCIPAL_ANGLE':
        title = 'Aşama 2: 1. Bölgedeki Esas Açıyı Bulun';
        instruction = 'Birim çember üzerinde bu orana karşılık gelen [0, 90] derece aralığındaki açıyı bulun.';
        example = 'Örnek: x = 30 veya 30';
        break;
      case 'S3_DETERMINE_SECONDARY_ROOT':
        title = 'Aşama 3: 2. Bölgedeki Simetrik Kökü Bulun';
        instruction = 'sin(180° - x) simetrisini kullanarak [0, 360) aralığındaki ikinci kökü bulun.';
        example = 'Örnek: x = 150 veya 150';
        break;
      case 'S1_EXPONENTIAL_CONVERSION':
        title = 'Aşama 1: Üstel Biçime Dönüştürün';
        instruction = 'log_b(y) = k eşitliğini b^k üssünü hesaplayarak cebirsel ifadeye çevirin.';
        example = 'Örnek: power = 8 veya 8';
        break;
      case 'S3_VERIFY_DOMAIN_CONSTRAINT':
        title = 'Aşama 3: Tanım Kümesi Doğrulaması';
        instruction = 'Bulunan x değerini logaritma içi fonksiyonda kontrol edin: argüman > 0 mı?';
        example = 'Örnek: gecerli veya gecersiz';
        break;
      case 'S1_EVALUATE_LIMIT_FORM':
        title = 'Aşama 1: Belirsizlik Tespiti';
        instruction = 'x = ${vm.a} limit noktasını fonksiyonda yerine yazarak belirsizlik biçimini tespit edin.';
        example = 'Örnek: 0/0 veya indeterminate';
        break;
      case 'S2_SIMPLIFY_EXPRESSION':
        title = 'Aşama 2: Çarpanlara Ayırarak Sadeleştirin';
        instruction = 'Paydaki iki kare farkını (x - ${vm.a})(x + ${vm.a}) olarak açıp (x - ${vm.a}) çarpanını sadeleştirin.';
        example = 'Örnek: x + ${vm.a}';
        break;
      case 'S3_COMPUTE_FINAL_LIMIT':
        title = 'Aşama 3: Limit Değerini Hesaplayın';
        instruction = 'Sadeleşmiş ifadede x yerine ${vm.a} koyarak nihai reel limit sonucunu bulun.';
        example = 'Örnek: ${vm.a * 2}';
        break;
      case 'S1_COMPUTE_DERIVATIVE':
        title = 'Aşama 1: Polinom Türevini Bulun';
        instruction = 'f(x) fonksiyonuna kuvvet kuralını uygulayarak türev f\'(x) ifadesini elde edin.';
        example = 'Örnek: 2x + ${vm.b} veya f\'(x) = 2x + ${vm.b}';
        break;
      case 'S2_EVALUATE_SLOPE':
        final x0Val = vm.x0 ?? vm.divisorRoot ?? 1;
        final slopeVal = 2 * vm.a * x0Val + vm.b;
        title = 'Aşama 2: Teğet Eğimi (m)';
        instruction = 'x0 = $x0Val apsisini f\'(x) fonksiyonunda yerine koyarak m eğimini hesaplayın.';
        example = 'Örnek: m = $slopeVal veya $slopeVal';
        break;
      case 'S3_DETERMINE_TANGENT_LINE':
        title = 'Aşama 3: Teğet Doğrusu Denklemi';
        instruction = 'y - y0 = m(x - x0) noktalı eğim formülüyle açık teğet doğrusu denklemini yazın.';
        example = 'Örnek: y = 4x - 1';
        break;
      case 'S1_FIND_ANTIDERIVATIVE':
        title = 'Aşama 1: Ters Türev F(x) İfadesini Bulun';
        instruction = 'İntegral kuvvet kuralını uygulayarak primitive F(x) fonksiyonunu bulun.';
        example = 'Örnek: x^2 veya x^2 + C';
        break;
      case 'S2_APPLY_LIMITS':
        title = 'Aşama 2: Sınırları Yerine Koyun F(b) - F(a)';
        instruction = 'Kalkülüsün Temel Teoremi uyarınca üst sınır ve alt sınır değerlerinin farkını hesaplayın.';
        example = 'Örnek: 9 - 0 veya 9';
        break;
      case 'S3_COMPUTE_DEFINITE_INTEGRAL':
        title = 'Aşama 3: Belirli İntegral / Net Alan Değerini Hesaplayın';
        instruction = 'Elde edilen sayısal net alan değerini girin.';
        example = 'Örnek: 9 veya 9.0';
        break;
      default:
        title = 'Cebirsel Adım';
        instruction = 'Lütfen bir sonraki matematiksel adımı yazın.';
        example = '';
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.zenSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.lightbulb_outline_rounded, color: Color(0xFF38BDF8), size: 18),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            instruction,
            style: const TextStyle(color: AppColors.textMuted, fontSize: 13, height: 1.4),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: Colors.black.withValues(alpha: 0.3),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              example,
              style: const TextStyle(
                color: Color(0xFF38BDF8),
                fontSize: 12,
                fontFamily: 'monospace',
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton.icon(
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  visualDensity: VisualDensity.compact,
                ),
                icon: const Icon(Icons.toys_outlined, size: 14, color: Colors.amberAccent),
                label: const Text('Mikro-Kum Havuzu', style: TextStyle(color: Colors.amberAccent, fontSize: 11)),
                onPressed: () => _openMicroSandbox(context, vm),
              ),
              const SizedBox(width: 8),
              TextButton.icon(
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  visualDensity: VisualDensity.compact,
                ),
                icon: const Icon(Icons.lightbulb_outline_rounded, size: 14, color: Color(0xFF38BDF8)),
                label: const Text('Sokratik İpucu', style: TextStyle(color: Color(0xFF38BDF8), fontSize: 11)),
                onPressed: () => _openSocraticHint(context, vm),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProbingCard(FocusSessionViewModel vm) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1B4B).withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.psychology_rounded, color: Color(0xFFF59E0B), size: 20),
              SizedBox(width: 8),
              Text(
                'Sokratik Teşhis Probu (PR-F2-01)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Text(
            'Faktör çifti seçerken toplam ve çarpım kısıtlarını nasıl incelersin?',
            style: TextStyle(color: Color(0xFFE2E8F0), fontSize: 13, height: 1.4),
          ),
          const SizedBox(height: 16),
          _buildProbeOptionButton(vm, 'Hem çarpımı hem toplamı birlikte sağlarım', 'BOTH'),
          const SizedBox(height: 8),
          _buildProbeOptionButton(vm, 'Yalnızca çarpımın işaretini tuttururum', 'PRODUCT_ONLY'),
          const SizedBox(height: 8),
          _buildProbeOptionButton(vm, 'Yalnızca toplamın işaretini tuttururum', 'SUM_ONLY'),
          const SizedBox(height: 8),
          _buildProbeOptionButton(vm, 'Diğer yöntem', 'OTHER'),
        ],
      ),
    );
  }

  Widget _buildProbeOptionButton(FocusSessionViewModel vm, String label, String code) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          backgroundColor: const Color(0xFF0F172A),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.12)),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          alignment: Alignment.centerLeft,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
        onPressed: vm.isSubmitting ? null : () => vm.submitProbeOption(code),
        child: Row(
          children: [
            Container(
              width: 20,
              height: 20,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF38BDF8).withValues(alpha: 0.15),
              ),
              child: Text(
                code[0],
                style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRepairingCard(FocusSessionViewModel vm) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF7F1D1D).withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFEF4444).withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.build_circle_outlined, color: Color(0xFFEF4444), size: 20),
              SizedBox(width: 8),
              Text(
                'Kavram Sağlamlaştırma Müdahalesi (IT-F2-01)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            'Toplamı ${vm.b}, çarpımı ${vm.c} olan iki sayıyı dikkatle belirle. Örneğin (2, 3) hem 2+3=${vm.b} hem 2*3=${vm.c} şartını sağlar.',
            style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 13, height: 1.4),
          ),
          const SizedBox(height: 12),
          const Text(
            'Aşağıdaki girdi alanına doğru faktör çiftini (Örn: 2, 3) gir ve gönder.',
            style: TextStyle(color: AppColors.textMuted, fontSize: 12),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(color: Colors.amberAccent.withValues(alpha: 0.5)),
                    padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  icon: const Icon(Icons.toys_rounded, color: Colors.amberAccent, size: 16),
                  label: const Text('Mikro-Kum Havuzu', style: TextStyle(color: Colors.amberAccent, fontSize: 11)),
                  onPressed: () => _openMicroSandbox(context, vm),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(color: const Color(0xFF38BDF8).withValues(alpha: 0.5)),
                    padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  icon: const Icon(Icons.lightbulb_rounded, color: Color(0xFF38BDF8), size: 16),
                  label: const Text('Sokratik İpucu', style: TextStyle(color: Color(0xFF38BDF8), fontSize: 11)),
                  onPressed: () => _openSocraticHint(context, vm),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSelfCorrectionCard(FocusSessionViewModel vm) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF581C87).withValues(alpha: 0.25),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF8B5CF6).withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.restart_alt_rounded, color: Color(0xFF8B5CF6), size: 20),
              SizedBox(width: 8),
              Text(
                'Orijinal Adımı Düzeltme (Öz-Düzeltme)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            'Harika! Müdahale adımını başarıyla anladın. Şimdi orijinal problemine dönerek (${MathTypography.toPrettyMath(vm.targetEquationLatex)}) doğru faktör çiftini gir.',
            style: const TextStyle(color: Color(0xFFDDD6FE), fontSize: 13, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildTransferCard(FocusSessionViewModel vm) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF0E7490).withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF06B6D4).withValues(alpha: 0.3)),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.swap_horiz_rounded, color: Color(0xFF06B6D4), size: 20),
              SizedBox(width: 8),
              Text(
                'Transfer Görevi (Kalıcılık Doğrulama)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 10),
          Text(
            'Yeni denklem: x² + 7x + 12 = 0\nÇarpımı 12, toplamı 7 olan çarpan çiftini girin (Örn: 3, 4).',
            style: TextStyle(color: Color(0xFFCFFAFE), fontSize: 13, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletedCard(FocusSessionViewModel vm) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF064E3B).withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4)),
      ),
      child: Column(
        children: [
          const Icon(Icons.check_circle_outline_rounded, color: Color(0xFF10B981), size: 54),
          const SizedBox(height: 12),
          const Text(
            'Odak Seansı Başarıyla Tamamlandı!',
            style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'Tüm adımlar ve kavram kısıtları sunucu tarafında tam olarak doğrulandı.',
            style: TextStyle(color: Color(0xFFA7F3D0), fontSize: 13),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: () => vm.startEpisode(),
              icon: const Icon(Icons.replay_rounded, size: 18),
              label: const Text('Yeni CT-QF1 Seansı Başlat'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputDock(FocusSessionViewModel vm) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        border: Border(top: BorderSide(color: Colors.white.withValues(alpha: 0.08))),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _inputController,
              focusNode: _inputFocusNode,
              style: const TextStyle(color: Colors.white, fontSize: 15, fontFamily: 'monospace'),
              decoration: InputDecoration(
                hintText: 'Adımınızı buraya yazın...',
                hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 14),
                filled: true,
                fillColor: const Color(0xFF1E293B),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              onSubmitted: (_) => _handleSubmit(vm),
            ),
          ),
          const SizedBox(width: 8),
          IconButton.filled(
            style: IconButton.styleFrom(
              backgroundColor: const Color(0xFF38BDF8),
              foregroundColor: Colors.black,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              padding: const EdgeInsets.all(12),
            ),
            onPressed: vm.isSubmitting ? null : () => _handleSubmit(vm),
            icon: vm.isSubmitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                  )
                : const Icon(Icons.arrow_upward_rounded, size: 20),
          ),
        ],
      ),
    );
  }
}
