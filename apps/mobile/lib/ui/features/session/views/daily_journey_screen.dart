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
import '../../analytics/views/cognitive_health_atlas_screen.dart';
import '../../../../core/localization.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../touchpad/math_touchpad.dart';
import '../view_models/session_view_model.dart';

enum DailyPhase {
  warmup,      // Phase 1: 3 min (Spaced Retrieval)
  diagnostic,  // Phase 2: 4 min (CAT ZPD Placement)
  problemBoard,// Phase 3: 10 min (Al-Khwarizmi & Socratic Board)
  reflection,  // Phase 4: 3 min (Metacognitive Calibration)
  completed,   // Circadian Sleep Lock Active
}

class DailyJourneyScreen extends StatefulWidget {
  const DailyJourneyScreen({super.key});

  @override
  State<DailyJourneyScreen> createState() => _DailyJourneyScreenState();
}

class _DailyJourneyScreenState extends State<DailyJourneyScreen> {
  DailyPhase _currentPhase = DailyPhase.warmup;
  bool _showScratchpad = false;
  bool _showGeometricCanvas = false;
  bool _showUnitCircleCanvas = false;
  bool _showTangentCanvas = false;
  bool _showRiemannCanvas = false;
  double _confidenceLevel = 0.85;
  int? _selectedWarmupOption;

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
              const Spacer(),
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
                  onPressed: () {
                    HapticFeedbackService().selectionClick();
                    setState(() => _showGeometricCanvas = !_showGeometricCanvas);
                  },
                ),
              // Unit Circle Canvas Toggle Button (Hedef 5)
              if (_currentPhase == DailyPhase.problemBoard)
                IconButton(
                  icon: Icon(
                    Icons.change_circle_outlined,
                    color: _showUnitCircleCanvas ? const Color(0xFFF59E0B) : const Color(0xFF94A3B8),
                  ),
                  tooltip: "Birim Çember Kanvası",
                  onPressed: () {
                    HapticFeedbackService().selectionClick();
                    setState(() => _showUnitCircleCanvas = !_showUnitCircleCanvas);
                  },
                ),
              // Dynamic Tangent Canvas Toggle Button (Hedef 6)
              if (_currentPhase == DailyPhase.problemBoard)
                IconButton(
                  icon: Icon(
                    Icons.show_chart_rounded,
                    color: _showTangentCanvas ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
                  ),
                  tooltip: "Dinamik Teğet Eğimi (Türev)",
                  onPressed: () {
                    HapticFeedbackService().selectionClick();
                    setState(() => _showTangentCanvas = !_showTangentCanvas);
                  },
                ),
              // Riemann Integral Canvas Toggle Button (Hedef 7)
              if (_currentPhase == DailyPhase.problemBoard)
                IconButton(
                  icon: Icon(
                    Icons.area_chart_rounded,
                    color: _showRiemannCanvas ? const Color(0xFF10B981) : const Color(0xFF94A3B8),
                  ),
                  tooltip: "Riemann İntegral Kanvası",
                  onPressed: () {
                    HapticFeedbackService().selectionClick();
                    setState(() => _showRiemannCanvas = !_showRiemannCanvas);
                  },
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
              // Accessibility & Curriculum Settings Button
              IconButton(
                icon: const Icon(
                  Icons.tune_rounded,
                  color: Color(0xFF38BDF8),
                ),
                tooltip: "Erişilebilirlik & Müfredat Ayarları",
                onPressed: () {
                  HapticFeedbackService().selectionClick();
                  _showSettingsModal(context);
                },
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

  Widget _buildPhaseContent() {
    switch (_currentPhase) {
      case DailyPhase.warmup:
        return _buildWarmupView();
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
            if (_showGeometricCanvas)
              const Padding(
                padding: EdgeInsets.all(12),
                child: AlKhwarizmiCanvas(bCoefficient: 6.0),
              ),
            if (_showUnitCircleCanvas)
              const Padding(
                padding: EdgeInsets.all(12),
                child: UnitCircleCanvas(),
              ),
            if (_showTangentCanvas)
              const Padding(
                padding: EdgeInsets.all(12),
                child: DynamicTangentCanvas(),
              ),
            if (_showRiemannCanvas)
              const Padding(
                padding: EdgeInsets.all(12),
                child: RiemannIntegralCanvas(),
              ),
            const Expanded(
              child: SessionScreen(),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: const Color(0xFF0F172A),
              child: Row(
                children: [
                  const Spacer(),
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
          ],
        );
      case DailyPhase.reflection:
        return _buildReflectionView();
      case DailyPhase.completed:
        return _buildCircadianLockView();
    }
  }

  Widget _buildWarmupView() {
    final options = [4, 6, 8, 10];
    final isCorrect = _selectedWarmupOption == 8;

    return Padding(
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
            child: const Text(
              "Hatırlama Sorusu: 3(x - 4) = 12 ise x kaçtır?",
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 4 Interactive Options
          Row(
            children: options.map((opt) {
              final isSelected = _selectedWarmupOption == opt;
              Color bg = const Color(0xFF1E293B);
              Color border = const Color(0xFF334155);
              if (isSelected) {
                if (opt == 8) {
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
                      if (opt == 8) {
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
                          ? "Harika! 3(8 - 4) = 3(4) = 12. Bilişsel hazırlık tamamlandı!"
                          : "3(x - 4) = 12 ise x - 4 = 4 olmalı. Tekrar dene!",
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
              setState(() => _currentPhase = DailyPhase.diagnostic);
            },
            child: const Text("Isınmayı Tamamla -> CAT Teşhise Başla"),
          ),
        ],
      ),
    );
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

  Widget _buildReflectionView() {
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
                  "Zihinsel Güven Skoru: %${(_confidenceLevel * 100).toInt()}",
                  style: const TextStyle(
                    color: Color(0xFF38BDF8),
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Slider(
                  value: _confidenceLevel,
                  min: 0.0,
                  max: 1.0,
                  divisions: 20,
                  activeColor: const Color(0xFF38BDF8),
                  inactiveColor: const Color(0xFF334155),
                  onChanged: (val) {
                    HapticFeedbackService().selectionClick();
                    setState(() => _confidenceLevel = val);
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
              setState(() => _currentPhase = DailyPhase.completed);
            },
            child: const Text("Seansı Tamamla ve Kilitle"),
          ),
        ],
      ),
    );
  }

  Widget _buildCircadianLockView() {
    return Padding(
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
        ],
      ),
    );
  }

  void _showSettingsModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF0F172A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Consumer<SessionViewModel>(
          builder: (context, sessionVm, _) {
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.tune_rounded, color: Color(0xFF38BDF8)),
                        const SizedBox(width: 8),
                        const Expanded(
                          child: Text(
                            "Erişilebilirlik & Müfredat Ayarları",
                            style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, color: Colors.white60, size: 20),
                          onPressed: () => Navigator.pop(ctx),
                        ),
                      ],
                    ),
                    const Divider(color: Color(0xFF1E293B)),

                    // ADHD Tunnel Focus Mode Toggle
                    SwitchListTile(
                      value: sessionVm.isTunnelFocusMode,
                      activeColor: const Color(0xFF38BDF8),
                      title: const Text("DEHB Tünel Odak Modu", style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                      subtitle: const Text("Obsidyen siyahı ve yüksek kontrast ile dikkat dağıtıcıları sıfırlar.", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                      onChanged: (_) {
                        HapticFeedbackService().selectionClick();
                        sessionVm.toggleTunnelFocusMode();
                      },
                    ),

                    // Dyscalculia Visual Aids Toggle
                    SwitchListTile(
                      value: sessionVm.isDyscalculiaHelper,
                      activeColor: const Color(0xFF10B981),
                      title: const Text("Diskalkuli Görsel Desteği", style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                      subtitle: const Text("Uzamsal sayı çizgisi ve renk kodlu cebirsel terim rozetleri.", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                      onChanged: (_) {
                        HapticFeedbackService().selectionClick();
                        sessionVm.toggleDyscalculiaHelper();
                      },
                    ),

                    const SizedBox(height: 12),
                    const Text("Girdi Modu & Çizim Tuvali", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _buildInputModeOption(
                          label: "Touchpad",
                          icon: Icons.grid_view_rounded,
                          mode: InputMode.touchpad,
                          selectedMode: sessionVm.inputMode,
                          onSelect: () {
                            HapticFeedbackService().modeSwitch();
                            sessionVm.setInputMode(InputMode.touchpad);
                          },
                        ),
                        const SizedBox(width: 8),
                        _buildInputModeOption(
                          label: "Klavye",
                          icon: Icons.keyboard_outlined,
                          mode: InputMode.virtualKeyboard,
                          selectedMode: sessionVm.inputMode,
                          onSelect: () {
                            HapticFeedbackService().modeSwitch();
                            sessionVm.setInputMode(InputMode.virtualKeyboard);
                          },
                        ),
                        const SizedBox(width: 8),
                        _buildInputModeOption(
                          label: "Çizim (İnk)",
                          icon: Icons.draw_rounded,
                          mode: InputMode.inkingCanvas,
                          selectedMode: sessionVm.inputMode,
                          onSelect: () {
                            HapticFeedbackService().modeSwitch();
                            sessionVm.setInputMode(InputMode.inkingCanvas);
                          },
                        ),
                      ],
                    ),

                    const SizedBox(height: 12),
                    const Text("Müfredat Standardı", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),

                    // Curriculum Standard Dropdown
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: DropdownButton<CurriculumType>(
                        value: AppLocalization.currentCurriculum,
                        dropdownColor: const Color(0xFF1E293B),
                        isExpanded: true,
                        underline: const SizedBox(),
                        style: const TextStyle(color: Colors.white, fontSize: 13),
                        items: CurriculumType.values.map((type) {
                          return DropdownMenuItem<CurriculumType>(
                            value: type,
                            child: Text(type.displayName),
                          );
                        }).toList(),
                        onChanged: (newType) {
                          if (newType != null) {
                            setState(() {
                              AppLocalization.setCurriculum(newType);
                            });
                          }
                        },
                      ),
                    ),

                    const SizedBox(height: 16),
                    // Offline Queue Status
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            sessionVm.pendingOfflineCount > 0 ? Icons.cloud_off : Icons.cloud_done,
                            color: sessionVm.pendingOfflineCount > 0 ? const Color(0xFFF59E0B) : const Color(0xFF10B981),
                            size: 20,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              sessionVm.pendingOfflineCount > 0
                                  ? "${sessionVm.pendingOfflineCount} adım çevrimdışı kuyrukta bekliyor"
                                  : "Tüm adımlar bulutla senkronize",
                              style: const TextStyle(color: Colors.white70, fontSize: 12),
                            ),
                          ),
                          if (sessionVm.pendingOfflineCount > 0)
                            TextButton(
                              onPressed: () => sessionVm.syncPendingOfflineSteps(),
                              child: const Text("Eşzamanla", style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12)),
                            ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildInputModeOption({
    required String label,
    required IconData icon,
    required InputMode mode,
    required InputMode selectedMode,
    required VoidCallback onSelect,
  }) {
    final isSelected = mode == selectedMode;
    return Expanded(
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onSelect,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF38BDF8).withValues(alpha: 0.2) : const Color(0xFF1E293B),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Column(
            children: [
              Icon(icon, size: 18, color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8)),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                  color: isSelected ? Colors.white : const Color(0xFF94A3B8),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
