import 'package:flutter/material.dart';
import '../../../data/services/engine_api_service.dart';

class ScannedNotebookStep {
  final int stepIndex;
  final String latex;
  final bool isValid;
  final String? bugId;
  final String? errorReason;

  const ScannedNotebookStep({
    required this.stepIndex,
    required this.latex,
    required this.isValid,
    this.bugId,
    this.errorReason,
  });

  factory ScannedNotebookStep.fromJson(Map<String, dynamic> json) {
    return ScannedNotebookStep(
      stepIndex: json['step_index'] as int? ?? 1,
      latex: json['latex'] as String? ?? (json['raw_text'] as String? ?? ''),
      isValid: json['is_valid'] as bool? ?? true,
      bugId: json['diagnostic_bug_id'] as String?,
      errorReason: json['error_reason'] as String?,
    );
  }
}

class NotebookPresetScenario {
  final String label;
  final String problem;
  final String rawText;
  final String dagNodeId;
  final String dagNodeTitle;
  final List<ScannedNotebookStep> defaultSteps;
  final String defaultHint;

  const NotebookPresetScenario({
    required this.label,
    required this.problem,
    required this.rawText,
    required this.dagNodeId,
    required this.dagNodeTitle,
    required this.defaultSteps,
    required this.defaultHint,
  });
}

const List<NotebookPresetScenario> defaultNotebookPresets = [
  NotebookPresetScenario(
    label: "Tam Kare",
    problem: "(x + 3)² = 25",
    rawText: "(x + 3)^2 = 25\nx^2 + 9 = 25",
    dagNodeId: "N19",
    dagNodeTitle: "Kuadratik Denklemler",
    defaultSteps: [
      ScannedNotebookStep(
        stepIndex: 1,
        latex: "x² + 9 = 25",
        isValid: false,
        bugId: "BUG-QUAD-03",
        errorReason: "Tam kare açılımında 2ab (orta terim) ihmal edildi.",
      ),
    ],
    defaultHint: "1. adımda tam kare açılımı yaparken (a + b)² kuralındaki çarpımın iki katı (2ab) terimini tekrar kontrol etmek ister misin?",
  ),
  NotebookPresetScenario(
    label: "İntegral +C",
    problem: r"\int 2x \, dx",
    rawText: "integrate(2*x, x)\nx^2",
    dagNodeId: "N111",
    dagNodeTitle: "Belirsiz İntegral",
    defaultSteps: [
      ScannedNotebookStep(
        stepIndex: 1,
        latex: "x²",
        isValid: false,
        bugId: "BUG-INT-01",
        errorReason: "Belirsiz integralde integrasyon sabiti (+C) unutuldu.",
      ),
    ],
    defaultHint: "1. adımda belirsiz integrali tamamlarken integrasyon sabiti olan (+ C)'yi eklemeyi unuttun mu?",
  ),
  NotebookPresetScenario(
    label: "Zincir Kuralı",
    problem: r"((3x + 1)²)'",
    rawText: "diff((3*x + 1)^2, x)\n2*(3*x + 1)",
    dagNodeId: "N94",
    dagNodeTitle: "Türevde Zincir Kuralı",
    defaultSteps: [
      ScannedNotebookStep(
        stepIndex: 1,
        latex: "2*(3x + 1)",
        isValid: false,
        bugId: "BUG-CALC-01",
        errorReason: "Bileşke fonksiyon türevinde iç türev (3) ihmal edildi.",
      ),
    ],
    defaultHint: "1. adımda bileşke fonksiyonun türevini alırken iç fonksiyonun türevini (zincir kuralı) çarpan olarak ekledin mi?",
  ),
  NotebookPresetScenario(
    label: "Eşitsizlik Yönü",
    problem: "-3x ≤ 9",
    rawText: "-3*x <= 9\nx <= -3",
    dagNodeId: "N08",
    dagNodeTitle: "Doğrusal Eşitsizlikler",
    defaultSteps: [
      ScannedNotebookStep(
        stepIndex: 1,
        latex: "x ≤ -3",
        isValid: false,
        bugId: "BUG-QUAD-06",
        errorReason: "Negatif sayıya bölerken eşitsizlik yönü değiştirilmedi.",
      ),
    ],
    defaultHint: "1. adımda eşitsizliğin her iki tarafını negatif bir sayıya bölerken eşitsizlik yönünün ne olması gerektiğini düşünelim mi?",
  ),
  NotebookPresetScenario(
    label: "Hatasız Çözüm",
    problem: "x² + 6x + 5 = 0",
    rawText: "x^2 + 6*x + 5 = 0\n(x + 3)^2 - 4 = 0\n(x + 3)^2 = 4",
    dagNodeId: "N19",
    dagNodeTitle: "Tam Kareye Tamamlama",
    defaultSteps: [
      ScannedNotebookStep(
        stepIndex: 1,
        latex: "(x + 3)² - 4 = 0",
        isValid: true,
      ),
      ScannedNotebookStep(
        stepIndex: 2,
        latex: "(x + 3)² = 4",
        isValid: true,
      ),
    ],
    defaultHint: "Harika bir akıl yürütme! Defterindeki tüm adımlar matematiksel olarak tamamen doğru. Şimdi bu bulduğun ara adımlardan hareketle sonuca nasıl ulaşacağını açıklar mısın?",
  ),
];

class MathScannerView extends StatefulWidget {
  final String initialProblem;
  final List<ScannedNotebookStep>? initialSteps;
  final String? initialSocraticHint;
  final String dagNodeId;
  final String dagNodeTitle;
  final EngineApiService? apiService;

  const MathScannerView({
    super.key,
    this.initialProblem = "(x + 3)² = 25",
    this.initialSteps,
    this.initialSocraticHint,
    this.dagNodeId = "N19",
    this.dagNodeTitle = "Kuadratik Denklemler & Diskriminant",
    this.apiService,
  });

  @override
  State<MathScannerView> createState() => _MathScannerViewState();
}

class _MathScannerViewState extends State<MathScannerView> with SingleTickerProviderStateMixin {
  late AnimationController _scanController;
  bool _isFlashOn = false;
  bool _isProcessing = false;
  bool _hasScanned = false;
  late NotebookPresetScenario _selectedPreset;
  late String _currentProblem;
  late String _currentDagNodeId;
  late String _currentDagNodeTitle;
  late List<ScannedNotebookStep> _steps;
  late String _socraticHint;

  @override
  void initState() {
    super.initState();
    _scanController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _selectedPreset = defaultNotebookPresets[0];
    _currentProblem = widget.initialProblem;
    _currentDagNodeId = widget.dagNodeId;
    _currentDagNodeTitle = widget.dagNodeTitle;

    _steps = widget.initialSteps ?? _selectedPreset.defaultSteps;
    _socraticHint = widget.initialSocraticHint ?? _selectedPreset.defaultHint;
  }

  @override
  void dispose() {
    _scanController.dispose();
    super.dispose();
  }

  void _selectPreset(NotebookPresetScenario preset) {
    setState(() {
      _selectedPreset = preset;
      _currentProblem = preset.problem;
      _currentDagNodeId = preset.dagNodeId;
      _currentDagNodeTitle = preset.dagNodeTitle;
      _steps = preset.defaultSteps;
      _socraticHint = preset.defaultHint;
      _hasScanned = false;
    });
  }

  Future<void> _triggerScan() async {
    setState(() {
      _isProcessing = true;
    });

    if (widget.apiService != null) {
      try {
        final res = await widget.apiService!.scanAndDiagnoseNotebook(
          rawTextOverride: _selectedPreset.rawText,
          targetProblem: _selectedPreset.problem,
        );
        if (mounted) {
          _scanController.stop();
          final stepsRaw = res['segmented_steps'] as List<dynamic>? ?? [];
          setState(() {
            _currentProblem = res['problem_statement'] as String? ?? _selectedPreset.problem;
            _currentDagNodeId = res['dag_node_id'] as String? ?? _selectedPreset.dagNodeId;
            _currentDagNodeTitle = res['dag_node_title'] as String? ?? _selectedPreset.dagNodeTitle;
            _steps = stepsRaw.map((e) => ScannedNotebookStep.fromJson(e as Map<String, dynamic>)).toList();
            _socraticHint = res['socratic_hint'] as String? ?? _selectedPreset.defaultHint;
            _isProcessing = false;
            _hasScanned = true;
          });
          return;
        }
      } catch (_) {
        // Fallback to local preset data on error or offline
      }
    }

    await Future.delayed(const Duration(milliseconds: 100));
    if (mounted) {
      _scanController.stop();
      setState(() {
        _isProcessing = false;
        _hasScanned = true;
      });
    }
  }

  void _resetScanner() {
    _scanController.repeat(reverse: true);
    setState(() {
      _hasScanned = false;
      _isProcessing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF0F172A),
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFF334155)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title & Shield Header
            Row(
              children: [
                const Icon(Icons.document_scanner, color: Color(0xFF38BDF8), size: 22),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    "Sokratik Soru & Defter Kamerası",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF10B981), width: 1),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.shield, color: Color(0xFF34D399), size: 12),
                      SizedBox(width: 4),
                      Text(
                        "Anti-Photomath (Sıfır Sızıntı)",
                        style: TextStyle(color: Color(0xFF34D399), fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Preset Scenarios Selector
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: defaultNotebookPresets.map((preset) {
                  final isSelected = _selectedPreset.label == preset.label;
                  return Padding(
                    padding: const EdgeInsets.only(right: 6.0),
                    child: ChoiceChip(
                      label: Text(preset.label),
                      selected: isSelected,
                      onSelected: (_) => _selectPreset(preset),
                      selectedColor: const Color(0xFF0284C7),
                      backgroundColor: const Color(0xFF1E293B),
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : Colors.white70,
                        fontSize: 11,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                      side: BorderSide(
                        color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 10),

            // Viewfinder or Scanned Results
            if (!_hasScanned) _buildViewfinder(context) else _buildDiagnosticResults(),

            const SizedBox(height: 14),

            // Bottom Action Controls
            if (!_hasScanned)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconButton(
                    icon: Icon(_isFlashOn ? Icons.flash_on : Icons.flash_off, color: Colors.white70),
                    tooltip: "Flaş",
                    onPressed: () {
                      setState(() {
                        _isFlashOn = !_isFlashOn;
                      });
                    },
                  ),
                  GestureDetector(
                    onTap: _triggerScan,
                    child: Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFF0284C7),
                        border: Border.all(color: Colors.white, width: 3),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF38BDF8).withValues(alpha: 0.4),
                            blurRadius: 10,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: _isProcessing
                          ? const Center(
                              child: SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              ),
                            )
                          : const Icon(Icons.camera_alt, color: Colors.white, size: 28),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.photo_library, color: Colors.white70),
                    tooltip: "Galeriden Yükle",
                    onPressed: _triggerScan,
                  ),
                ],
              )
            else
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white70,
                        side: const BorderSide(color: Color(0xFF475569)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      icon: const Icon(Icons.refresh, size: 18),
                      label: const Text("Yeni Fotoğraf Çek"),
                      onPressed: _resetScanner,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0284C7),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      icon: const Icon(Icons.auto_awesome, size: 18),
                      label: const Text("Bu Adımı Düzelt"),
                      onPressed: () {},
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildViewfinder(BuildContext context) {
    return Container(
      height: 220,
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFF020617),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Alignment Corner Brackets
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Container(
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.5), width: 1.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(
                  "Defterdeki matematiksel adımları\nbu çerçevenin içine hizalayınız",
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white.withValues(alpha: 0.6), fontSize: 12),
                ),
              ),
            ),
          ),

          // Animated Scanline
          AnimatedBuilder(
            animation: _scanController,
            builder: (context, child) {
              return Positioned(
                top: 25 + _scanController.value * 170,
                left: 20,
                right: 20,
                child: Container(
                  height: 2,
                  decoration: BoxDecoration(
                    color: const Color(0xFF38BDF8),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF38BDF8).withValues(alpha: 0.8),
                        blurRadius: 6,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildDiagnosticResults() {
    final hasError = _steps.any((s) => !s.isValid);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Problem Header & DAG Node Badge
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFF1E293B),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF334155)),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("Tespit Edilen Soru:", style: TextStyle(color: Colors.white54, fontSize: 10)),
                    const SizedBox(height: 2),
                    Text(
                      _currentProblem,
                      style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold, fontFamily: "monospace"),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF0284C7).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: const Color(0xFF0284C7)),
                ),
                child: Text(
                  "$_currentDagNodeId: $_currentDagNodeTitle",
                  style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Segmented Steps
        const Text("Defterdeki Çözüm Adımları:", style: TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        ..._steps.map((step) => _buildStepRow(step)),

        const SizedBox(height: 10),

        // Socratic Inquiry Bubble
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: hasError
                ? const Color(0xFFF59E0B).withValues(alpha: 0.12)
                : const Color(0xFF10B981).withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: hasError ? const Color(0xFFF59E0B).withValues(alpha: 0.4) : const Color(0xFF10B981).withValues(alpha: 0.4),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                hasError ? Icons.psychology : Icons.celebration,
                color: hasError ? const Color(0xFFFBBF24) : const Color(0xFF34D399),
                size: 22,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      hasError ? "Sokratik Düşünme Sorusu:" : "Harika Başarı!",
                      style: TextStyle(
                        color: hasError ? const Color(0xFFFBBF24) : const Color(0xFF34D399),
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _socraticHint,
                      style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.3),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStepRow(ScannedNotebookStep step) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: step.isValid
            ? const Color(0xFF020617)
            : const Color(0xFF7F1D1D).withValues(alpha: 0.25),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: step.isValid ? const Color(0xFF1E293B) : const Color(0xFFEF4444).withValues(alpha: 0.6),
        ),
      ),
      child: Row(
        children: [
          Icon(
            step.isValid ? Icons.check_circle : Icons.error_outline,
            color: step.isValid ? const Color(0xFF10B981) : const Color(0xFFEF4444),
            size: 18,
          ),
          const SizedBox(width: 8),
          Text(
            "Adım ${step.stepIndex}:",
            style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.bold),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              step.latex,
              style: TextStyle(
                color: step.isValid ? Colors.white : const Color(0xFFFCA5A5),
                fontSize: 13,
                fontFamily: "monospace",
                fontWeight: step.isValid ? FontWeight.normal : FontWeight.bold,
              ),
            ),
          ),
          if (step.bugId != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: const Color(0xFFEF4444).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: const Color(0xFFEF4444)),
              ),
              child: Text(
                step.bugId!,
                style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ),
        ],
      ),
    );
  }
}
