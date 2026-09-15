import 'package:flutter/material.dart';

enum ProofCanvasMode {
  truthTable,
  induction,
  deduction,
}

enum InductionStage {
  baseCase,
  hypothesis,
  inductiveStep,
}

class ProofCanvas extends StatefulWidget {
  final ProofCanvasMode initialMode;

  const ProofCanvas({
    super.key,
    this.initialMode = ProofCanvasMode.truthTable,
  });

  @override
  State<ProofCanvas> createState() => _ProofCanvasState();
}

class _ProofCanvasState extends State<ProofCanvas> {
  late ProofCanvasMode _mode;

  // Truth Table State
  bool _propP = true;
  bool _propQ = true;

  // Induction State
  InductionStage _inductionStage = InductionStage.baseCase;
  int _dominoProgress = 1;

  // Deduction / Contradiction State
  String _selectedDeductionRule = "Modus Ponens";

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode;
  }

  bool get _andResult => _propP && _propQ;
  bool get _orResult => _propP || _propQ;
  bool get _impliesResult => (!_propP) || _propQ;
  bool get _iffResult => _propP == _propQ;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3.0,
      margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 12.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16.0)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Mode Selector
            SegmentedButton<ProofCanvasMode>(
              segments: const [
                ButtonSegment(
                  value: ProofCanvasMode.truthTable,
                  label: Text("Doğruluk Tablosu"),
                  icon: Icon(Icons.table_chart),
                ),
                ButtonSegment(
                  value: ProofCanvasMode.induction,
                  label: Text("Tümevarım"),
                  icon: Icon(Icons.stairs),
                ),
                ButtonSegment(
                  value: ProofCanvasMode.deduction,
                  label: Text("İspat Tahtası"),
                  icon: Icon(Icons.psychology),
                ),
              ],
              selected: {_mode},
              onSelectionChanged: (newSelection) {
                setState(() {
                  _mode = newSelection.first;
                });
              },
            ),
            const SizedBox(height: 14.0),

            if (_mode == ProofCanvasMode.truthTable) _buildTruthTableSection(),
            if (_mode == ProofCanvasMode.induction) _buildInductionSection(),
            if (_mode == ProofCanvasMode.deduction) _buildDeductionSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildTruthTableSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            FilterChip(
              key: const Key("chip_toggle_p"),
              label: Text("p: ${_propP ? '1 (D)' : '0 (Y)'}"),
              selected: _propP,
              onSelected: (val) => setState(() => _propP = val),
            ),
            FilterChip(
              key: const Key("chip_toggle_q"),
              label: Text("q: ${_propQ ? '1 (D)' : '0 (Y)'}"),
              selected: _propQ,
              onSelected: (val) => setState(() => _propQ = val),
            ),
          ],
        ),
        const SizedBox(height: 12.0),
        Table(
          border: TableBorder.all(color: Colors.grey.shade300, width: 1.0),
          children: [
            TableRow(
              decoration: BoxDecoration(color: Colors.blueGrey.shade100),
              children: const [
                Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text("p ∧ q", textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text("p ∨ q", textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text("p ⇒ q", textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text("p ⇔ q", textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            TableRow(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(_andResult ? "1" : "0", textAlign: TextAlign.center),
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(_orResult ? "1" : "0", textAlign: TextAlign.center),
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(
                    _impliesResult ? "1" : "0",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: _impliesResult ? Colors.green.shade800 : Colors.red.shade800,
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(_iffResult ? "1" : "0", textAlign: TextAlign.center),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 10.0),
        Container(
          padding: const EdgeInsets.all(8.0),
          decoration: BoxDecoration(
            color: Colors.amber.shade50,
            borderRadius: BorderRadius.circular(8.0),
            border: Border.all(color: Colors.amber.shade200),
          ),
          child: const Text(
            "Kritik İlke: p ⇒ q önermesi yalnızca 1 ⇒ 0 durumunda 0 (yanlış) olur. Öncül yanlışsa (0) sonuç daima doğrudur (1).",
            style: TextStyle(fontSize: 11.0, color: Colors.brown),
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }

  Widget _buildInductionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          "İspat Hedefi: 1 + 2 + ... + n = n(n+1)/2",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 10.0),

        // Stage 1
        ListTile(
          key: const Key("tile_stage_base"),
          leading: Icon(
            _inductionStage.index >= 0 ? Icons.check_circle : Icons.radio_button_unchecked,
            color: Colors.green,
          ),
          title: const Text("Aşama 1: Taban Adımı P(1)"),
          subtitle: const Text("n = 1 için: Sol = 1, Sağ = 1(2)/2 = 1. Doğrulandı!"),
        ),
        // Stage 2
        ListTile(
          key: const Key("tile_stage_hypothesis"),
          leading: Icon(
            _inductionStage.index >= 1 ? Icons.check_circle : Icons.radio_button_unchecked,
            color: _inductionStage.index >= 1 ? Colors.green : Colors.grey,
          ),
          title: const Text("Aşama 2: Tümevarım Hipotezi P(k)"),
          subtitle: const Text("n = k için doğru kabul edilsin: 1+...+k = k(k+1)/2"),
        ),
        // Stage 3
        ListTile(
          key: const Key("tile_stage_step"),
          leading: Icon(
            _inductionStage.index >= 2 ? Icons.check_circle : Icons.radio_button_unchecked,
            color: _inductionStage.index >= 2 ? Colors.green : Colors.grey,
          ),
          title: const Text("Aşama 3: Geçiş Adımı P(k+1)"),
          subtitle: const Text("k(k+1)/2 + (k+1) = (k+1)(k+2)/2 cebirsel türetimi."),
        ),
        const SizedBox(height: 10.0),

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text("Zincirleme İlerleme: n = $_dominoProgress"),
            ElevatedButton.icon(
              key: const Key("btn_next_induction_stage"),
              icon: const Icon(Icons.arrow_forward),
              label: const Text("Sonraki Adım"),
              onPressed: () {
                setState(() {
                  if (_inductionStage == InductionStage.baseCase) {
                    _inductionStage = InductionStage.hypothesis;
                  } else if (_inductionStage == InductionStage.hypothesis) {
                    _inductionStage = InductionStage.inductiveStep;
                  }
                  _dominoProgress++;
                });
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildDeductionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DropdownButton<String>(
          key: const Key("dropdown_deduction_rule"),
          value: _selectedDeductionRule,
          isExpanded: true,
          items: const [
            DropdownMenuItem(value: "Modus Ponens", child: Text("Modus Ponens (Öncülü Olumlama)")),
            DropdownMenuItem(value: "Modus Tollens", child: Text("Modus Tollens (Sonucu Yadsıma)")),
            DropdownMenuItem(value: "Çelişki ile İspat", child: Text("Çelişki ile İspat (Reductio ad Absurdum)")),
          ],
          onChanged: (val) {
            if (val != null) {
              setState(() => _selectedDeductionRule = val);
            }
          },
        ),
        const SizedBox(height: 10.0),
        Container(
          padding: const EdgeInsets.all(12.0),
          decoration: BoxDecoration(
            color: Colors.purple.shade50,
            borderRadius: BorderRadius.circular(10.0),
            border: Border.all(color: Colors.purple.shade200),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("Kural: $_selectedDeductionRule", style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6.0),
              if (_selectedDeductionRule == "Modus Ponens")
                const Text("Öncüller: [p, p ⇒ q]\nSonuç: Zorunlu olarak q doğrudur."),
              if (_selectedDeductionRule == "Modus Tollens")
                const Text("Öncüller: [¬q, p ⇒ q]\nSonuç: Zorunlu olarak ¬p doğrudur."),
              if (_selectedDeductionRule == "Çelişki ile İspat")
                const Text("Adım 1: Hükmün değilini (¬p) doğru varsay.\nAdım 2: Mantıksal çıkarımlarla bir çelişkiye (q ∧ ¬q) ulaş.\nSonuç: Varsayım imkansızdır, dolayısıyla p doğrudur."),
            ],
          ),
        ),
      ],
    );
  }
}
