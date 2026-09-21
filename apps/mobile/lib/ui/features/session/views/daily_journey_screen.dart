import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../diagnostic/views/diagnostic_screen.dart';
import '../../diagnostic/view_models/diagnostic_view_model.dart';
import 'session_screen.dart';
import 'scratchpad_overlay.dart';
import 'al_khwarizmi_canvas.dart';
import 'unit_circle_canvas.dart';
import 'dynamic_tangent_canvas.dart';
import 'riemann_integral_canvas.dart';
import 'interactive_coordinate_canvas.dart';
import 'euclidean_canvas.dart';
import '../../scanner/math_scanner_view.dart';
import '../../modeling/problem_modeling_view.dart';
import '../../analytics/views/cognitive_health_atlas_screen.dart';
import '../../vault/mistake_autopsy_view.dart';
import '../../../../data/services/mistake_vault_service.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../view_models/session_view_model.dart';
import 'components/warmup_phase_view.dart';
import 'components/reflection_phase_view.dart';
import 'components/session_settings_modal.dart';
import 'components/focus_topic_selection_modal.dart';
import '../../touchpad/math_touchpad.dart';

enum DailyPhase {
  warmup,      // Phase 1: 3 min (Spaced Retrieval)
  diagnostic,  // Phase 2: 4 min (CAT ZPD Placement)
  problemBoard,// Phase 3: 10 min (Al-Khwarizmi & Socratic Board)
  reflection,  // Phase 4: 3 min (Metacognitive Calibration)
  completed,   // Circadian Sleep Lock Active
}

enum ActiveVisualCanvas {
  none,
  geometric,
  unitCircle,
  tangent,
  riemann,
  coordinate,
  euclidean,
}

class DailyJourneyScreen extends StatefulWidget {
  final void Function(int tabIndex)? onNavigateToTab;
  final DailyPhase initialPhase;

  const DailyJourneyScreen({
    super.key,
    this.onNavigateToTab,
    this.initialPhase = DailyPhase.warmup,
  });

  @override
  State<DailyJourneyScreen> createState() => _DailyJourneyScreenState();
}

class _DailyJourneyScreenState extends State<DailyJourneyScreen> {
  late DailyPhase _currentPhase;
  bool _showScratchpad = false;
  ActiveVisualCanvas _activeCanvas = ActiveVisualCanvas.none;

  @override
  void initState() {
    super.initState();
    _currentPhase = widget.initialPhase;
  }

  bool get _showGeometricCanvas => _activeCanvas == ActiveVisualCanvas.geometric;
  bool get _showUnitCircleCanvas => _activeCanvas == ActiveVisualCanvas.unitCircle;
  bool get _showTangentCanvas => _activeCanvas == ActiveVisualCanvas.tangent;
  bool get _showRiemannCanvas => _activeCanvas == ActiveVisualCanvas.riemann;
  bool get _showCoordinateCanvas => _activeCanvas == ActiveVisualCanvas.coordinate;
  bool get _showEuclideanCanvas => _activeCanvas == ActiveVisualCanvas.euclidean;

  void _toggleCanvas(ActiveVisualCanvas canvas) {
    HapticFeedbackService().selectionClick();
    setState(() {
      if (_activeCanvas == canvas) {
        _activeCanvas = ActiveVisualCanvas.none;
      } else {
        _activeCanvas = canvas;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF090D16),
      body: Stack(
        children: [
          SafeArea(
            child: Column(
              children: [
                // Top 20-Min Session Header
                _buildSessionProgressHeader(),

                // Offline Pending Sync Notification Banner
                _buildOfflineSyncBanner(),

                // Active Phase Body
                Expanded(
                  child: _buildPhaseContent(),
                ),
              ],
            ),
          ),

          // Floating Scratchpad Overlay
          if (_showScratchpad)
            Positioned.fill(
              child: ScratchpadOverlay(
                onClose: () => setState(() => _showScratchpad = false),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildSessionProgressHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: const BoxDecoration(
        color: Color(0xFF0F172A),
        border: Border(bottom: BorderSide(color: Color(0xFF1E293B))),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.timer_outlined, color: Color(0xFF38BDF8), size: 18),
              const SizedBox(width: 8),
              const Text(
                "20 Dk Günlük Bilişsel Seans",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  reverse: true,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Scratchpad Trigger Button
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          icon: Icon(
                            Icons.edit_note,
                            color: _showScratchpad ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "Karalama Tuvali",
                          onPressed: () {
                            HapticFeedbackService().selectionClick();
                            setState(() => _showScratchpad = !_showScratchpad);
                          },
                        ),
                      // Al-Khwarizmi Tile Canvas Toggle Button
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          icon: Icon(
                            Icons.architecture,
                            color: _showGeometricCanvas ? const Color(0xFF10B981) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "El-Harezmi Karoları",
                          onPressed: () => _toggleCanvas(ActiveVisualCanvas.geometric),
                        ),
                      // Unit Circle Canvas Toggle Button (Hedef 5)
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          icon: Icon(
                            Icons.change_circle_outlined,
                            color: _showUnitCircleCanvas ? const Color(0xFFF59E0B) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "Birim Çember Kanvası",
                          onPressed: () => _toggleCanvas(ActiveVisualCanvas.unitCircle),
                        ),
                      // Dynamic Tangent Canvas Toggle Button (Hedef 6)
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          icon: Icon(
                            Icons.show_chart_rounded,
                            color: _showTangentCanvas ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "Dinamik Teğet Eğimi (Türev)",
                          onPressed: () => _toggleCanvas(ActiveVisualCanvas.tangent),
                        ),
                      // Riemann Integral Canvas Toggle Button (Hedef 7)
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          icon: Icon(
                            Icons.area_chart_rounded,
                            color: _showRiemannCanvas ? const Color(0xFF10B981) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "Riemann İntegral Kanvası",
                          onPressed: () => _toggleCanvas(ActiveVisualCanvas.riemann),
                        ),
                      // Interactive Coordinate Canvas Toggle Button (Hedef 10)
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          key: const Key('toggle_coordinate_canvas_button'),
                          icon: Icon(
                            Icons.grid_4x4_rounded,
                            color: _showCoordinateCanvas ? const Color(0xFF6366F1) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "Analitik Koordinat & Vektör Kanvası",
                          onPressed: () => _toggleCanvas(ActiveVisualCanvas.coordinate),
                        ),
                      // Euclidean & Auxiliary Line Canvas Toggle Button (Hedef 11)
                      if (_currentPhase == DailyPhase.problemBoard)
                        IconButton(
                          key: const Key('toggle_euclidean_canvas_button'),
                          icon: Icon(
                            Icons.architecture_rounded,
                            color: _showEuclideanCanvas ? const Color(0xFFF43F5E) : const Color(0xFF94A3B8),
                          ),
                          tooltip: "Sentetik Öklid & Ek Çizim Kanvası",
                          onPressed: () => _toggleCanvas(ActiveVisualCanvas.euclidean),
                        ),
                      // Vector Inking Canvas Quick Toggle Button
                      if (_currentPhase == DailyPhase.problemBoard)
                        Consumer<SessionViewModel>(
                          builder: (context, vm, _) {
                            final isInking = vm.inputMode == InputMode.inkingCanvas;
                            return IconButton(
                              icon: Icon(
                                Icons.draw_rounded,
                                color: isInking ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
                              ),
                              tooltip: "Vektör Çizim Tuvali",
                              onPressed: () {
                                HapticFeedbackService().modeSwitch();
                                vm.setInputMode(isInking ? InputMode.touchpad : InputMode.inkingCanvas);
                              },
                            );
                          },
                        ),
                      // Cognitive Health & Atlas Button
                      IconButton(
                        icon: const Icon(
                          Icons.account_tree_outlined,
                          color: Color(0xFF10B981),
                        ),
                        tooltip: "Bilişsel Sağlık & Cebir Atlası",
                        onPressed: () {
                          HapticFeedbackService().selectionClick();
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => const CognitiveHealthAtlasScreen(),
                            ),
                          );
                        },
                      ),
                      // Math Scanner & Notebook Vision Camera Button (Hedef 8)
                      IconButton(
                        icon: const Icon(
                          Icons.camera_alt_outlined,
                          color: Color(0xFF38BDF8),
                        ),
                        tooltip: "Sokratik Defter & Soru Kamerası",
                        onPressed: () {
                          HapticFeedbackService().selectionClick();
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => const Scaffold(
                                body: SafeArea(child: MathScannerView()),
                              ),
                            ),
                          );
                        },
                      ),
                      // Story Problem Modeling & Socratic Scaffold (Hedef 9)
                      IconButton(
                        key: const Key('header_problem_modeling_button'),
                        icon: const Icon(
                          Icons.auto_stories_outlined,
                          color: Color(0xFFF59E0B),
                        ),
                        tooltip: "Yeni Nesil Hikayeli Problem Modelleme",
                        onPressed: () {
                          HapticFeedbackService().selectionClick();
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => const Scaffold(
                                body: SafeArea(child: ProblemModelingView()),
                              ),
                            ),
                          );
                        },
                      ),
                      // Cognitive Mistake Vault & Weakness Hunter Button (Hedef 12)
                      IconButton(
                        key: const Key('header_mistake_vault_button'),
                        icon: const Icon(
                          Icons.biotech_rounded,
                          color: Color(0xFFF43F5E),
                        ),
                        tooltip: "Bilişsel Hata Kasası & Zaaf Avcısı",
                        onPressed: () {
                          HapticFeedbackService().selectionClick();
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => MistakeAutopsyView(
                                mistakes: MistakeVaultService.instance.mistakes,
                                onStartBossBattle: () {
                                  HapticFeedbackService().stepSuccess();
                                },
                              ),
                            ),
                          );
                        },
                      ),
                      // Focus Kernel Multi-Topic Cognitive Session Button
                      IconButton(
                        key: const Key('header_focus_session_button'),
                        icon: const Icon(
                          Icons.psychology_outlined,
                          color: Color(0xFF38BDF8),
                        ),
                        tooltip: "Focus Kernel: Bilişsel Seanslar",
                        onPressed: () {
                          HapticFeedbackService().selectionClick();
                          showFocusTopicSelectionModal(context);
                        },
                      ),
                      // Accessibility & Curriculum Settings Button
                      IconButton(
                        icon: const Icon(
                          Icons.tune_rounded,
                          color: Color(0xFF38BDF8),
                        ),
                        tooltip: "Erişilebilirlik & Müfredat Ayarları",
                        onPressed: () {
                          HapticFeedbackService().selectionClick();
                          showSessionSettingsModal(context);
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // 4-Phase Step Indicator
          Row(
            children: [
              _buildStepIndicator("1. Isınma", DailyPhase.warmup),
              _buildStepDivider(),
              _buildStepIndicator("2. Teşhis", DailyPhase.diagnostic),
              _buildStepDivider(),
              _buildStepIndicator("3. Tahta", DailyPhase.problemBoard),
              _buildStepDivider(),
              _buildStepIndicator("4. Kapanış", DailyPhase.reflection),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator(String title, DailyPhase phase) {
    final isCurrent = _currentPhase == phase;
    final isDone = _currentPhase.index > phase.index;

    Color color = const Color(0xFF64748B);
    if (isCurrent) color = const Color(0xFF38BDF8);
    if (isDone) color = const Color(0xFF10B981);

    return Expanded(
      child: Column(
        children: [
          Container(
            height: 4,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: isCurrent ? FontWeight.w700 : FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepDivider() {
    return const SizedBox(width: 4);
  }

  Widget _buildActiveCanvasWidget() {
    switch (_activeCanvas) {
      case ActiveVisualCanvas.geometric:
        return const AlKhwarizmiCanvas(bCoefficient: 6.0);
      case ActiveVisualCanvas.unitCircle:
        return const UnitCircleCanvas();
      case ActiveVisualCanvas.tangent:
        return const DynamicTangentCanvas();
      case ActiveVisualCanvas.riemann:
        return const RiemannIntegralCanvas();
      case ActiveVisualCanvas.coordinate:
        return const InteractiveCoordinateCanvas();
      case ActiveVisualCanvas.euclidean:
        return const EuclideanCanvas();
      case ActiveVisualCanvas.none:
        return const SizedBox.shrink();
    }
  }

  Widget _buildPhaseContent() {
    switch (_currentPhase) {
      case DailyPhase.warmup:
        return WarmupPhaseView(
          onCompleted: () => setState(() => _currentPhase = DailyPhase.diagnostic),
        );
      case DailyPhase.diagnostic:
        return Consumer<DiagnosticViewModel>(
          builder: (context, vm, child) {
            if (vm.isComplete) {
              return _buildDiagnosticCompletedView();
            }
            return DiagnosticScreen(
              showAppBar: false,
              onCompleted: () => setState(() => _currentPhase = DailyPhase.problemBoard),
            );
          },
        );
      case DailyPhase.problemBoard:
        return Column(
          children: [
            if (_activeCanvas != ActiveVisualCanvas.none)
              ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 280),
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: _buildActiveCanvasWidget(),
                  ),
                ),
              ),
            const Expanded(
              child: SessionScreen(),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: const Color(0xFF0F172A),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                physics: const BouncingScrollPhysics(),
                child: Row(
                  children: [
                    OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFFF59E0B),
                        side: const BorderSide(color: Color(0xFFF59E0B)),
                      ),
                      onPressed: () {
                        HapticFeedbackService().selectionClick();
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => const Scaffold(
                              body: SafeArea(child: ProblemModelingView()),
                            ),
                          ),
                        );
                      },
                      icon: const Icon(Icons.auto_stories_outlined, size: 16),
                      label: const Text("Modelleme İskelesi"),
                    ),
                    const SizedBox(width: 8),
                    OutlinedButton.icon(
                      key: const Key('focus_session_trigger_button'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF38BDF8),
                        side: const BorderSide(color: Color(0xFF38BDF8)),
                      ),
                      onPressed: () {
                        HapticFeedbackService().selectionClick();
                        showFocusTopicSelectionModal(context);
                      },
                      icon: const Icon(Icons.psychology_outlined, size: 16),
                      label: const Text("Focus Seansı"),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF10B981),
                        foregroundColor: Colors.white,
                      ),
                      onPressed: () {
                        HapticFeedbackService().selectionClick();
                        setState(() => _currentPhase = DailyPhase.reflection);
                      },
                      icon: const Icon(Icons.arrow_forward, size: 16),
                      label: const Text("Metabilişsel Kapanışa Geç"),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      case DailyPhase.reflection:
        return ReflectionPhaseView(
          onCompleted: () => setState(() => _currentPhase = DailyPhase.completed),
        );
      case DailyPhase.completed:
        return CircadianLockView(
          onNavigateToTab: widget.onNavigateToTab,
        );
    }
  }

  Widget _buildDiagnosticCompletedView() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Icon(Icons.check_circle_outline, color: Color(0xFF10B981), size: 56),
          const SizedBox(height: 16),
          const Text(
            "CAT Teşhisi Tamamlandı!",
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            "Yetenek düzeyin SE <= 0.35 hassasiyetle hesaplandı ve Cebir Atlası üzerindeki 20 düğüm tohumlandı.",
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF10B981),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            onPressed: () {
              HapticFeedbackService().selectionClick();
              setState(() => _currentPhase = DailyPhase.problemBoard);
            },
            child: const Text("Çözüm Tahtasına İlerle (10 Dk)"),
          ),
        ],
      ),
    );
  }

  Widget _buildOfflineSyncBanner() {
    final SessionViewModel vm;
    try {
      vm = Provider.of<SessionViewModel>(context);
    } catch (_) {
      return const SizedBox.shrink();
    }
    if (vm.pendingOfflineCount == 0) return const SizedBox.shrink();
    return Container(
      color: const Color(0xFFF59E0B).withValues(alpha: 0.18),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Row(
        children: [
          const Icon(Icons.cloud_off, color: Color(0xFFF59E0B), size: 16),
          const SizedBox(width: 8),
          Text(
            '${vm.pendingOfflineCount} işlem çevrimdışı kuyrukta bekliyor',
            style: const TextStyle(color: Color(0xFFF59E0B), fontSize: 12, fontWeight: FontWeight.w600),
          ),
          const Spacer(),
          TextButton(
            onPressed: () => vm.syncPendingOfflineSteps(),
            child: const Text('Şimdi Senkronize Et', style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12)),
          ),
        ],
      ),
    );
  }
}
