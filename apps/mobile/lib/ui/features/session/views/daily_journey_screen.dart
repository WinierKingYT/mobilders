import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../diagnostic/views/diagnostic_screen.dart';
import '../../diagnostic/view_models/diagnostic_view_model.dart';
import 'session_screen.dart';
import 'scratchpad_overlay.dart';
import 'al_khwarizmi_canvas.dart';
import '../../analytics/views/cognitive_health_atlas_screen.dart';
import '../../../../core/localization.dart';
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
  double _confidenceLevel = 0.85;

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
                  onPressed: () => setState(() => _showScratchpad = !_showScratchpad),
                ),
              // Al-Khwarizmi Tile Canvas Toggle Button
              if (_currentPhase == DailyPhase.problemBoard)
                IconButton(
                  icon: Icon(
                    Icons.architecture,
                    color: _showGeometricCanvas ? const Color(0xFF10B981) : const Color(0xFF94A3B8),
                  ),
                  tooltip: "El-Harezmi Karoları",
                  onPressed: () => setState(() => _showGeometricCanvas = !_showGeometricCanvas),
                ),
              // Cognitive Health & Atlas Button
              IconButton(
                icon: const Icon(
                  Icons.account_tree_outlined,
                  color: Color(0xFF10B981),
                ),
                tooltip: "Bilişsel Sağlık & Cebir Atlası",
                onPressed: () {
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
                onPressed: () => _showSettingsModal(context),
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
            if (vm.currentItem == null && !vm.isLoading && vm.errorMessage == null) {
              WidgetsBinding.instance.addPostFrameCallback((_) {
                vm.loadFirstItem();
              });
            }
            return const DiagnosticScreen();
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
                    onPressed: () => setState(() => _currentPhase = DailyPhase.reflection),
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
          const SizedBox(height: 28),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
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
          const SizedBox(height: 32),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            onPressed: () => setState(() => _currentPhase = DailyPhase.diagnostic),
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
            onPressed: () => setState(() => _currentPhase = DailyPhase.problemBoard),
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
                  onChanged: (val) => setState(() => _confidenceLevel = val),
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
            onPressed: () => setState(() => _currentPhase = DailyPhase.completed),
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
                        const Text(
                          "Erişilebilirlik & Müfredat Ayarları",
                          style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        const Spacer(),
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
                      onChanged: (_) => sessionVm.toggleTunnelFocusMode(),
                    ),

                    // Dyscalculia Visual Aids Toggle
                    SwitchListTile(
                      value: sessionVm.isDyscalculiaHelper,
                      activeColor: const Color(0xFF10B981),
                      title: const Text("Diskalkuli Görsel Desteği", style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                      subtitle: const Text("Uzamsal sayı çizgisi ve renk kodlu cebirsel terim rozetleri.", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                      onChanged: (_) => sessionVm.toggleDyscalculiaHelper(),
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
}
