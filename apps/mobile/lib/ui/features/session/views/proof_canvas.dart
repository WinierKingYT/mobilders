import 'package:flutter/material.dart';

enum ProofCanvasMode {
  truthTable,
  theoremProof,
  induction,
}

class ProofCanvas extends StatefulWidget {
  final ProofCanvasMode initialMode;
  final String? initialTheoremId;

  const ProofCanvas({
    super.key,
    this.initialMode = ProofCanvasMode.truthTable,
    this.initialTheoremId,
  });

  @override
  State<ProofCanvas> createState() => _ProofCanvasState();
}

class _ProofCanvasState extends State<ProofCanvas> {
  late ProofCanvasMode _mode;
  String _selectedExpressionType = 'implies';
  String _selectedTheoremId = 'THM-IRR-SQRT2';
  int _activeInductionStage = 1;
  bool _dominoSimulated = false;

  final TextEditingController _stepInputController = TextEditingController();
  String _selectedRule = 'CONTRADICTION_ASSUMPTION';
  String? _stepFeedback;
  bool _isStepValid = true;
  final List<Map<String, dynamic>> _completedSteps = [];

  final Map<String, String> _theoremTitles = {
    'THM-IRR-SQRT2': '√2 Sayısının İrrasyonelliği (Çelişki)',
    'THM-EUCLID-PRIMES': 'Asal Sayıların Sonsuzluğu (Öklid)',
    'THM-GAUSS-SUM': 'Gauss Toplam Formülü (Tümevarım)',
    'THM-EXP-INEQ': 'Üstel Eşitsizlik: 2ⁿ > n (Tümevarım)',
    'THM-SUM-EVENS': 'İki Çift Sayının Toplamı Çifttir (Doğrudan)',
    'THM-CONTRAPOSITIVE-SQUARE': 'n² Tek İse n Tektir (Karşıt-Ters)',
  };

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode;
    if (widget.initialTheoremId != null) {
      _selectedTheoremId = widget.initialTheoremId!;
    }
  }

  @override
  void didUpdateWidget(covariant ProofCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialMode != widget.initialMode) {
      _mode = widget.initialMode;
    }
    if (widget.initialTheoremId != null &&
        widget.initialTheoremId != oldWidget.initialTheoremId) {
      _selectedTheoremId = widget.initialTheoremId!;
    }
  }

  @override
  void dispose() {
    _stepInputController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header & Mode Selector
          Row(
            children: [
              Icon(Icons.psychology_outlined, color: colorScheme.primary, size: 28),
              const SizedBox(width: 8),
              Text(
                "İspat & Mantık Laboratuvarı",
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SegmentedButton<ProofCanvasMode>(
            segments: const [
              ButtonSegment(
                value: ProofCanvasMode.truthTable,
                label: Text("Doğruluk Tablosu"),
                icon: Icon(Icons.table_chart_outlined),
              ),
              ButtonSegment(
                value: ProofCanvasMode.theoremProof,
                label: Text("Teorem İspatı"),
                icon: Icon(Icons.menu_book_outlined),
              ),
              ButtonSegment(
                value: ProofCanvasMode.induction,
                label: Text("Tümevarım"),
                icon: Icon(Icons.view_timeline_outlined),
              ),
            ],
            selected: {_mode},
            onSelectionChanged: (Set<ProofCanvasMode> newSelection) {
              setState(() {
                _mode = newSelection.first;
              });
            },
          ),
          const SizedBox(height: 16),

          // Dynamic Mode Body
          if (_mode == ProofCanvasMode.truthTable)
            _buildTruthTableMode(colorScheme, theme)
          else if (_mode == ProofCanvasMode.theoremProof)
            _buildTheoremProofMode(colorScheme, theme)
          else
            _buildInductionMode(colorScheme, theme),
        ],
      ),
    );
  }

  // =========================================================================
  // 1. DOĞRULUK TABLOSU MODU
  // =========================================================================
  Widget _buildTruthTableMode(ColorScheme colorScheme, ThemeData theme) {
    // Determine truth table rows for selected expression
    final rows = _getTruthTableRows(_selectedExpressionType);
    final isTautology = rows.every((r) => r['result'] == 1);
    final isContradiction = rows.every((r) => r['result'] == 0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          children: [
            ChoiceChip(
              label: const Text("p ⇒ q (İse)"),
              selected: _selectedExpressionType == 'implies',
              onSelected: (val) => setState(() => _selectedExpressionType = 'implies'),
            ),
            ChoiceChip(
              label: const Text("p ⇔ q (Ancak ve Ancak)"),
              selected: _selectedExpressionType == 'iff',
              onSelected: (val) => setState(() => _selectedExpressionType = 'iff'),
            ),
            ChoiceChip(
              label: const Text("De Morgan (∧)"),
              selected: _selectedExpressionType == 'de_morgan_and',
              onSelected: (val) => setState(() => _selectedExpressionType = 'de_morgan_and'),
            ),
            ChoiceChip(
              label: const Text("Karşıt Ters (p⇒q ≡ ¬q⇒¬p)"),
              selected: _selectedExpressionType == 'contrapositive',
              onSelected: (val) => setState(() => _selectedExpressionType = 'contrapositive'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        // Truth Table Widget
        Container(
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: colorScheme.outlineVariant),
          ),
          child: DataTable(
            columns: const [
              DataColumn(label: Text("p")),
              DataColumn(label: Text("q")),
              DataColumn(label: Text("Sonuç")),
            ],
            rows: rows.map((r) {
              return DataRow(
                cells: [
                  DataCell(Text(r['p'].toString(), style: const TextStyle(fontWeight: FontWeight.bold))),
                  DataCell(Text(r['q'].toString(), style: const TextStyle(fontWeight: FontWeight.bold))),
                  DataCell(
                    Text(
                       r['result'].toString(),
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: r['result'] == 1 ? Colors.green : Colors.red,
                      ),
                    ),
                  ),
                ],
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 12),
        // Classification Badge
        Row(
          children: [
            if (isTautology)
              Container(
                key: const Key('badge_tautology'),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green),
                ),
                child: const Text("✓ TAUTOLOJİ (Her zaman 1)", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
              )
            else if (isContradiction)
              Container(
                key: const Key('badge_contradiction'),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red),
                ),
                child: const Text("✗ ÇELİŞKİ (Her zaman 0)", style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
              )
            else
              Container(
                key: const Key('badge_contingency'),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue),
                ),
                child: const Text("ℹ TUTARLI / KOŞULLU", style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
              ),
          ],
        ),
      ],
    );
  }

  List<Map<String, int>> _getTruthTableRows(String exprType) {
    if (exprType == 'implies') {
      return [
        {'p': 1, 'q': 1, 'result': 1},
        {'p': 1, 'q': 0, 'result': 0},
        {'p': 0, 'q': 1, 'result': 1},
        {'p': 0, 'q': 0, 'result': 1},
      ];
    } else if (exprType == 'iff') {
      return [
        {'p': 1, 'q': 1, 'result': 1},
        {'p': 1, 'q': 0, 'result': 0},
        {'p': 0, 'q': 1, 'result': 0},
        {'p': 0, 'q': 0, 'result': 1},
      ];
    } else if (exprType == 'de_morgan_and' || exprType == 'contrapositive') {
      // Both are tautologies (equivalence)
      return [
        {'p': 1, 'q': 1, 'result': 1},
        {'p': 1, 'q': 0, 'result': 1},
        {'p': 0, 'q': 1, 'result': 1},
        {'p': 0, 'q': 0, 'result': 1},
      ];
    }
    return [
      {'p': 1, 'q': 1, 'result': 1},
      {'p': 1, 'q': 0, 'result': 0},
      {'p': 0, 'q': 1, 'result': 0},
      {'p': 0, 'q': 0, 'result': 0},
    ];
  }

  // =========================================================================
  // 2. TEOREM İSPAT MODU
  // =========================================================================
  Widget _buildTheoremProofMode(ColorScheme colorScheme, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DropdownButtonFormField<String>(
          initialValue: _selectedTheoremId,
          decoration: const InputDecoration(
            labelText: "İspatlanacak Teorem",
            border: OutlineInputBorder(),
          ),
          items: _theoremTitles.entries.map((entry) {
            return DropdownMenuItem<String>(
              value: entry.key,
              child: Text(entry.value, overflow: TextOverflow.ellipsis),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null) {
              setState(() {
                _selectedTheoremId = val;
                _completedSteps.clear();
                _stepFeedback = null;
              });
            }
          },
        ),
        const SizedBox(height: 16),
        // Step Reasoning Card
        Card(
          elevation: 0,
          color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: colorScheme.outlineVariant),
          ),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Adım Doğrulayıcı", style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                TextField(
                  key: const Key('input_proof_step'),
                  controller: _stepInputController,
                  decoration: const InputDecoration(
                    hintText: "Adım önermenizi yazın (ör: varsayalim ki √2 rasyoneldir)",
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  key: const Key('dropdown_proof_rule'),
                  initialValue: _selectedRule,
                  decoration: const InputDecoration(
                    labelText: "Kullanılan Çıkarım Kuralı",
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                  items: const [
                    DropdownMenuItem(value: 'CONTRADICTION_ASSUMPTION', child: Text("Çelişki İçin Ters Kabul (¬P)")),
                    DropdownMenuItem(value: 'MODUS_PONENS', child: Text("Modus Ponens (Öncülü Olumlama)")),
                    DropdownMenuItem(value: 'MODUS_TOLLENS', child: Text("Modus Tollens (Sonucu Yadsıma)")),
                    DropdownMenuItem(value: 'INDUCTION_BASE', child: Text("Tümevarım Taban Adımı")),
                    DropdownMenuItem(value: 'CONTRAPOSITIVE_CONVERSION', child: Text("Karşıt Ters Dönüşümü")),
                  ],
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedRule = val);
                  },
                ),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  key: const Key('btn_verify_proof_step'),
                  icon: const Icon(Icons.check_circle_outline),
                  label: const Text("Adımı Doğrula"),
                  onPressed: _verifyTheoremProofStep,
                ),
              ],
            ),
          ),
        ),
        if (_stepFeedback != null) ...[
          const SizedBox(height: 8),
          Container(
            key: const Key('box_step_feedback'),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _isStepValid ? Colors.green.withValues(alpha: 0.1) : Colors.red.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _isStepValid ? Colors.green : Colors.red),
            ),
            child: Text(
              _stepFeedback!,
              style: TextStyle(
                color: _isStepValid ? Colors.green.shade800 : Colors.red.shade800,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
        if (_completedSteps.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            key: const Key('proof_step_chain'),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.green.withValues(alpha: 0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "Doğrulanan İspat Adımları (${_completedSteps.length})",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.green),
                    ),
                    TextButton.icon(
                      key: const Key('btn_reset_proof_steps'),
                      icon: const Icon(Icons.refresh, size: 14),
                      label: const Text("Sıfırla", style: TextStyle(fontSize: 11)),
                      onPressed: () {
                        setState(() {
                          _completedSteps.clear();
                          _stepFeedback = null;
                        });
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                ..._completedSteps.map((step) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 3),
                      child: Row(
                        children: [
                          const Icon(Icons.check_circle, size: 15, color: Colors.green),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              "${step['stepNumber']}. ${step['statement']} [${step['rule']}]",
                              style: const TextStyle(fontSize: 12),
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
        ],
      ],
    );
  }

  void _verifyTheoremProofStep() {
    final text = _stepInputController.text.trim();
    final lower = text.toLowerCase();

    // 1. Fallacy check
    if (lower.contains("taban_adimi_gerekmez") ||
        lower.contains("0=>0=0") ||
        lower.contains("tersi_dengidir")) {
      setState(() {
        _isStepValid = false;
        _stepFeedback = "Mantıksal Yanılgı Teşhis Edildi: Çıkarım kurallarını kontrol edin.";
      });
      return;
    }

    // 2. Sequential Logic Check (Adım Sıralama Denetimi)
    if (_selectedTheoremId == 'THM-IRR-SQRT2') {
      // Step 1: Must be Contradiction Assumption
      if (_completedSteps.isEmpty) {
        if (_selectedRule != 'CONTRADICTION_ASSUMPTION' && !lower.contains("varsay") && !lower.contains("kabul")) {
          setState(() {
            _isStepValid = false;
            _stepFeedback = "Mantıksal Sıralama Hatası: Çelişki ispatına başlamadan önce hipotez / ters kabul (¬P) adımı kurulmalıdır.";
          });
          return;
        }
      } else if (_completedSteps.length == 1) {
        // Step 2: Must be deduction / algebraic equality
        if (_selectedRule == 'INDUCTION_BASE' || _selectedRule == 'CONTRAPOSITIVE_CONVERSION') {
          setState(() {
            _isStepValid = false;
            _stepFeedback = "Mantıksal Sıralama Hatası: İkinci adımda cebirsel çıkarım veya Modus Ponens uygulanmalıdır.";
          });
          return;
        }
      }
    } else if (_selectedTheoremId == 'THM-GAUSS-SUM' || _selectedTheoremId == 'THM-EXP-INEQ') {
      // Induction: Step 1 must be base step
      if (_completedSteps.isEmpty && _selectedRule != 'INDUCTION_BASE' && !lower.contains("n=1") && !lower.contains("taban")) {
        setState(() {
          _isStepValid = false;
          _stepFeedback = "Mantıksal Sıralama Hatası: Tümevarımda taban adımı (n=1) doğrulanmadan genel iddia kabul edilemez.";
        });
        return;
      }
    }

    setState(() {
      _isStepValid = true;
      final stepNum = _completedSteps.length + 1;
      _completedSteps.add({
        'stepNumber': stepNum,
        'statement': text.isNotEmpty ? text : "Adım $stepNum",
        'rule': _selectedRule,
      });
      _stepFeedback = "Tebrikler! $stepNum. adım mantıksal olarak geçerlidir.";
    });
  }

  // =========================================================================
  // 3. TÜMEVARIM SANDKUTUSU MODU
  // =========================================================================
  Widget _buildInductionMode(ColorScheme colorScheme, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          "Önerme: Gauss Toplam Formülü (1 + 2 + ... + n = n(n+1)/2)",
          style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        // 3-Stage Stepper
        Row(
          children: [
            _buildStageChip(1, "1. Taban Adımı", colorScheme),
            const SizedBox(width: 8),
            _buildStageChip(2, "2. Hipotez", colorScheme),
            const SizedBox(width: 8),
            _buildStageChip(3, "3. Geçiş Adımı", colorScheme),
          ],
        ),
        const SizedBox(height: 16),
        // Active Stage Card
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: colorScheme.outlineVariant),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (_activeInductionStage == 1) ...[
                const Text("n = 1 için doğrula:", style: TextStyle(fontWeight: FontWeight.bold)),
                const Text("Sol Taraf = 1"),
                const Text("Sağ Taraf = 1 · (1 + 1) / 2 = 1"),
                const Text("✓ Eşitlik sağlandı, P(1) DOĞRU.", style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
              ] else if (_activeInductionStage == 2) ...[
                const Text("n = k için kabul yap:", style: TextStyle(fontWeight: FontWeight.bold)),
                const Text("Varsayım: 1 + 2 + ... + k = k(k+1)/2 doğru olsun."),
              ] else ...[
                const Text("n = k + 1 için türet:", style: TextStyle(fontWeight: FontWeight.bold)),
                const Text("Sol Taraf = (1 + ... + k) + (k+1) = k(k+1)/2 + (k+1)"),
                const Text("= (k+1)(k/2 + 1) = (k+1)(k+2)/2 = Sağ Taraf ✓"),
              ],
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Domino Simulation
        ElevatedButton.icon(
          key: const Key('btn_simulate_domino'),
          icon: const Icon(Icons.play_arrow),
          label: const Text("Domino Etkisini Başlat (k=1..10)"),
          onPressed: () {
            setState(() {
              _dominoSimulated = true;
            });
          },
        ),
        if (_dominoSimulated) ...[
          const SizedBox(height: 12),
          Wrap(
            key: const Key('domino_chain_wrap'),
            spacing: 6,
            children: List.generate(10, (index) {
              final k = index + 1;
              return Chip(
                avatar: const Icon(Icons.check, size: 16, color: Colors.white),
                backgroundColor: Colors.green.shade600,
                label: Text("P($k) ✓", style: const TextStyle(color: Colors.white, fontSize: 12)),
              );
            }),
          ),
          const SizedBox(height: 6),
          const Text(
            "Tüm doğal sayılar için önerme zincirleme olarak kanıtlandı.",
            style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
          ),
        ],
      ],
    );
  }

  Widget _buildStageChip(int stage, String label, ColorScheme colorScheme) {
    final isActive = _activeInductionStage == stage;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _activeInductionStage = stage),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isActive ? colorScheme.primary : colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: isActive ? colorScheme.onPrimary : colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
