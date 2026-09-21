import 'dart:math' as math;
import 'package:flutter/material.dart';

enum ProbabilityCanvasMode {
  venn,
  tree,
  monteCarlo,
}

enum VennRegionHighlight {
  all,
  intersection,
  union,
  onlyA,
  onlyB,
  complement,
}

class CountingTreeVennCanvas extends StatefulWidget {
  final ProbabilityCanvasMode initialMode;
  final double probA;
  final double probB;
  final double probIntersection;

  const CountingTreeVennCanvas({
    super.key,
    this.initialMode = ProbabilityCanvasMode.venn,
    this.probA = 0.5,
    this.probB = 0.4,
    this.probIntersection = 0.2,
  });

  @override
  State<CountingTreeVennCanvas> createState() => _CountingTreeVennCanvasState();
}

class _CountingTreeVennCanvasState extends State<CountingTreeVennCanvas> {
  late ProbabilityCanvasMode _mode;
  VennRegionHighlight _vennHighlight = VennRegionHighlight.intersection;

  // Monte Carlo State
  int _monteCarloTrials = 10000;
  double? _observedProb;
  final double _theoreticalProb = 0.5;
  bool _isSimulating = false;

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode;
  }

  @override
  void didUpdateWidget(covariant CountingTreeVennCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialMode != widget.initialMode) {
      _mode = widget.initialMode;
    }
  }

  void _runSimulation() {
    if (_isSimulating) return;
    setState(() {
      _isSimulating = true;
    });

    final random = math.Random();
    int successes = 0;
    final trials = math.max(10, _monteCarloTrials);
    for (int i = 0; i < trials; i++) {
      if (random.nextDouble() < _theoreticalProb) {
        successes++;
      }
    }

    if (mounted) {
      setState(() {
        _observedProb = successes / trials;
        _isSimulating = false;
      });
    }
  }

  double get _probUnion {
    final pa = widget.probA.isNaN || widget.probA.isInfinite ? 0.0 : widget.probA;
    final pb = widget.probB.isNaN || widget.probB.isInfinite ? 0.0 : widget.probB;
    final pInter = widget.probIntersection.isNaN || widget.probIntersection.isInfinite ? 0.0 : widget.probIntersection;
    final u = pa + pb - pInter;
    return math.max(0.0, math.min(1.0, u));
  }

  double get _probConditional {
    final pb = widget.probB.isNaN || widget.probB.isInfinite ? 0.0 : widget.probB;
    final pInter = widget.probIntersection.isNaN || widget.probIntersection.isInfinite ? 0.0 : widget.probIntersection;
    if (pb <= 0) return 0.0;
    final c = pInter / pb;
    return math.max(0.0, math.min(1.0, c));
  }

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
            Row(
              children: [
                Expanded(
                  child: SegmentedButton<ProbabilityCanvasMode>(
                    segments: const [
                      ButtonSegment(
                        value: ProbabilityCanvasMode.venn,
                        label: Text("Venn Şeması"),
                        icon: Icon(Icons.bubble_chart),
                      ),
                      ButtonSegment(
                        value: ProbabilityCanvasMode.tree,
                        label: Text("Ağaç Diyagramı"),
                        icon: Icon(Icons.account_tree),
                      ),
                      ButtonSegment(
                        value: ProbabilityCanvasMode.monteCarlo,
                        label: Text("Monte Carlo"),
                        icon: Icon(Icons.casino),
                      ),
                    ],
                    selected: {_mode},
                    onSelectionChanged: (newSelection) {
                      setState(() {
                        _mode = newSelection.first;
                      });
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12.0),

            // Content per Mode
            if (_mode == ProbabilityCanvasMode.venn) _buildVennSection(),
            if (_mode == ProbabilityCanvasMode.tree) _buildTreeSection(),
            if (_mode == ProbabilityCanvasMode.monteCarlo)
              _buildMonteCarloSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildVennSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Region Highlight Chips
        Wrap(
          spacing: 8.0,
          children: [
            ChoiceChip(
              key: const Key("chip_intersection"),
              label: const Text("A ∩ B (Kesişim)"),
              selected: _vennHighlight == VennRegionHighlight.intersection,
              onSelected: (val) {
                if (val) {
                  setState(() =>
                      _vennHighlight = VennRegionHighlight.intersection);
                }
              },
            ),
            ChoiceChip(
              key: const Key("chip_union"),
              label: const Text("A ∪ B (Birleşim)"),
              selected: _vennHighlight == VennRegionHighlight.union,
              onSelected: (val) {
                if (val) {
                  setState(() => _vennHighlight = VennRegionHighlight.union);
                }
              },
            ),
            ChoiceChip(
              key: const Key("chip_only_a"),
              label: const Text("A \\ B (Sadece A)"),
              selected: _vennHighlight == VennRegionHighlight.onlyA,
              onSelected: (val) {
                if (val) {
                  setState(() => _vennHighlight = VennRegionHighlight.onlyA);
                }
              },
            ),
          ],
        ),
        const SizedBox(height: 8.0),

        // Venn Canvas
        Container(
          height: 180,
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12.0),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: RepaintBoundary(
            child: CustomPaint(
              painter: _VennPainter(
                highlight: _vennHighlight,
                probA: widget.probA,
                probB: widget.probB,
                probIntersection: widget.probIntersection,
              ),
            ),
          ),
        ),
        const SizedBox(height: 10.0),

        // Formula Card
        Container(
          padding: const EdgeInsets.all(10.0),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(8.0),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "P(A ∪ B) = P(A) + P(B) - P(A ∩ B) = ${_probUnion.toStringAsFixed(2)}",
                style: const TextStyle(
                    fontWeight: FontWeight.bold, fontSize: 13.0),
              ),
              const SizedBox(height: 4.0),
              Text(
                "Koşullu: P(A | B) = P(A ∩ B) / P(B) = ${_probConditional.toStringAsFixed(2)}",
                style: const TextStyle(fontSize: 12.0, color: Colors.blueGrey),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTreeSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          height: 190,
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12.0),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: RepaintBoundary(
            child: CustomPaint(
              painter: _TreePainter(),
            ),
          ),
        ),
        const SizedBox(height: 8.0),
        const Text(
          "Çarpma Kuralı: Bir dal boyunca olasılıklar art arda çarpılır.",
          style: TextStyle(fontSize: 12.0, fontStyle: FontStyle.italic),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildMonteCarloSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text("Deneme Sayısı (N): $_monteCarloTrials"),
            ElevatedButton.icon(
              key: const Key("btn_run_monte_carlo"),
              icon: const Icon(Icons.play_arrow),
              label: const Text("Simüle Et"),
              onPressed: _isSimulating ? null : _runSimulation,
            ),
          ],
        ),
        Slider(
          value: _monteCarloTrials.toDouble(),
          min: 1000,
          max: 100000,
          divisions: 99,
          label: "$_monteCarloTrials",
          onChanged: (val) {
            setState(() {
              _monteCarloTrials = val.round();
            });
          },
        ),
        const SizedBox(height: 8.0),
        Container(
          padding: const EdgeInsets.all(12.0),
          decoration: BoxDecoration(
            color: Colors.teal.shade50,
            borderRadius: BorderRadius.circular(10.0),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      const Text("Teorik P(Tura)",
                          style: TextStyle(fontSize: 12.0)),
                      Text(
                        _theoreticalProb.toStringAsFixed(3),
                        style: const TextStyle(
                            fontSize: 18.0, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  Column(
                    children: [
                      const Text("Deneysel P(Gözlenen)",
                          style: TextStyle(fontSize: 12.0)),
                      Text(
                        _observedProb != null
                            ? _observedProb!.toStringAsFixed(4)
                            : "—",
                        style: TextStyle(
                          fontSize: 18.0,
                          fontWeight: FontWeight.bold,
                          color: _observedProb != null
                              ? Colors.teal.shade900
                              : Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              if (_observedProb != null) ...[
                const SizedBox(height: 6.0),
                Text(
                  "Fark (Sapma): ${(_observedProb! - _theoreticalProb).abs().toStringAsFixed(4)}",
                  style: const TextStyle(
                      fontSize: 12.0, fontWeight: FontWeight.w600),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _VennPainter extends CustomPainter {
  final VennRegionHighlight highlight;
  final double probA;
  final double probB;
  final double probIntersection;

  _VennPainter({
    required this.highlight,
    required this.probA,
    required this.probB,
    required this.probIntersection,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final borderPaint = Paint()
      ..color = Colors.blueGrey
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    final fillAPaint = Paint()
      ..color = (highlight == VennRegionHighlight.union ||
              highlight == VennRegionHighlight.onlyA)
          ? Colors.blue.withValues(alpha: 0.35)
          : Colors.blue.withValues(alpha: 0.15)
      ..style = PaintingStyle.fill;

    final fillBPaint = Paint()
      ..color = (highlight == VennRegionHighlight.union ||
              highlight == VennRegionHighlight.onlyB)
          ? Colors.red.withValues(alpha: 0.35)
          : Colors.red.withValues(alpha: 0.15)
      ..style = PaintingStyle.fill;

    final radius = size.height * 0.38;
    final centerA = Offset(size.width * 0.38, size.height * 0.5);
    final centerB = Offset(size.width * 0.62, size.height * 0.5);

    // Draw circles
    canvas.drawCircle(centerA, radius, fillAPaint);
    canvas.drawCircle(centerB, radius, fillBPaint);
    canvas.drawCircle(centerA, radius, borderPaint);
    canvas.drawCircle(centerB, radius, borderPaint);

    // If intersection highlight
    if (highlight == VennRegionHighlight.intersection) {
      final intersectPaint = Paint()
        ..color = Colors.purple.withValues(alpha: 0.55)
        ..style = PaintingStyle.fill;
      canvas.save();
      final pathA = Path()
        ..addOval(Rect.fromCircle(center: centerA, radius: radius));
      final pathB = Path()
        ..addOval(Rect.fromCircle(center: centerB, radius: radius));
      final intersectPath =
          Path.combine(PathOperation.intersect, pathA, pathB);
      canvas.drawPath(intersectPath, intersectPaint);
      canvas.restore();
    }

    // Text labels
    _drawText(canvas, "A (${probA.toStringAsFixed(2)})",
        Offset(centerA.dx - 45, centerA.dy));
    _drawText(canvas, "B (${probB.toStringAsFixed(2)})",
        Offset(centerB.dx + 15, centerB.dy));
    _drawText(canvas, probIntersection.toStringAsFixed(2),
        Offset(size.width * 0.5 - 12, size.height * 0.5 - 8));
  }

  void _drawText(Canvas canvas, String text, Offset offset) {
    final textSpan = TextSpan(
      text: text,
      style: const TextStyle(
          color: Colors.black87, fontSize: 11.0, fontWeight: FontWeight.bold),
    );
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant _VennPainter oldDelegate) =>
      oldDelegate.highlight != highlight ||
      oldDelegate.probA != probA ||
      oldDelegate.probB != probB ||
      oldDelegate.probIntersection != probIntersection;
}

class _TreePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final branchPaint = Paint()
      ..color = Colors.blueGrey
      ..strokeWidth = 2.0;

    final root = Offset(20, size.height * 0.5);
    final b1 = Offset(size.width * 0.45, size.height * 0.25);
    final b2 = Offset(size.width * 0.45, size.height * 0.75);

    // Stage 1 branches
    canvas.drawLine(root, b1, branchPaint);
    canvas.drawLine(root, b2, branchPaint);

    // Stage 2 branches
    final l1 = Offset(size.width * 0.85, size.height * 0.12);
    final l2 = Offset(size.width * 0.85, size.height * 0.38);
    final l3 = Offset(size.width * 0.85, size.height * 0.62);
    final l4 = Offset(size.width * 0.85, size.height * 0.88);

    canvas.drawLine(b1, l1, branchPaint);
    canvas.drawLine(b1, l2, branchPaint);
    canvas.drawLine(b2, l3, branchPaint);
    canvas.drawLine(b2, l4, branchPaint);

    // Labels
    _drawText(canvas, "Yazı (1/2)", Offset(size.width * 0.2, size.height * 0.28));
    _drawText(canvas, "Tura (1/2)", Offset(size.width * 0.2, size.height * 0.65));
    _drawText(canvas, "Y (1/2) -> P(YY)=1/4", Offset(l1.dx - 10, l1.dy - 6));
    _drawText(canvas, "T (1/2) -> P(YT)=1/4", Offset(l2.dx - 10, l2.dy - 6));
    _drawText(canvas, "Y (1/2) -> P(TY)=1/4", Offset(l3.dx - 10, l3.dy - 6));
    _drawText(canvas, "T (1/2) -> P(TT)=1/4", Offset(l4.dx - 10, l4.dy - 6));
  }

  void _drawText(Canvas canvas, String text, Offset offset) {
    final textSpan = TextSpan(
      text: text,
      style: const TextStyle(
          color: Colors.black87, fontSize: 10.0, fontWeight: FontWeight.w600),
    );
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant _TreePainter oldDelegate) => false;
}
