import 'dart:math' as math;
import 'package:flutter/material.dart';

enum CalculusCurveType {
  parabola,
  cubic,
  sine,
}

class DynamicTangentPainter extends CustomPainter {
  final CalculusCurveType curveType;
  final double x0;
  final double h;

  DynamicTangentPainter({
    required this.curveType,
    required this.x0,
    required this.h,
  });

  double _f(double x) {
    switch (curveType) {
      case CalculusCurveType.parabola:
        return 0.5 * x * x;
      case CalculusCurveType.cubic:
        return 0.25 * x * x * x;
      case CalculusCurveType.sine:
        return 1.8 * math.sin(x);
    }
  }

  double _fPrime(double x) {
    switch (curveType) {
      case CalculusCurveType.parabola:
        return x;
      case CalculusCurveType.cubic:
        return 0.75 * x * x;
      case CalculusCurveType.sine:
        return 1.8 * math.cos(x);
    }
  }

  @override
  void paint(Canvas canvas, Size size) {
    if (size.width <= 0 || size.height <= 0) return;
    final origin = Offset(size.width * 0.45, size.height * 0.65);
    final scale = size.width / 7.0; // pixels per unit

    Offset toScreen(double x, double y) {
      return Offset(origin.dx + x * scale, origin.dy - y * scale);
    }

    // 1. Draw Grid Lines
    final gridPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.07)
      ..strokeWidth = 1.0;

    for (double gx = -4.0; gx <= 4.0; gx += 1.0) {
      final p1 = toScreen(gx, -4.0);
      final p2 = toScreen(gx, 6.0);
      canvas.drawLine(p1, p2, gridPaint);
    }
    for (double gy = -4.0; gy <= 6.0; gy += 1.0) {
      final p1 = toScreen(-4.0, gy);
      final p2 = toScreen(4.0, gy);
      canvas.drawLine(p1, p2, gridPaint);
    }

    // 2. Draw Axes
    final axisPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.25)
      ..strokeWidth = 1.5;

    canvas.drawLine(toScreen(-3.5, 0), toScreen(3.5, 0), axisPaint);
    canvas.drawLine(toScreen(0, -3.5), toScreen(0, 5.0), axisPaint);

    _drawText(canvas, "x", toScreen(3.4, -0.3), 11, Colors.white54);
    _drawText(canvas, "y", toScreen(0.3, 4.8), 11, Colors.white54);

    // 3. Draw Function Curve
    final curvePath = Path();
    bool first = true;
    for (double x = -3.2; x <= 3.2; x += 0.05) {
      final y = _f(x);
      final p = toScreen(x, y);
      if (first) {
        curvePath.moveTo(p.dx, p.dy);
        first = false;
      } else {
        curvePath.lineTo(p.dx, p.dy);
      }
    }

    final curvePaint = Paint()
      ..color = const Color(0xFF38BDF8)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round;
    canvas.drawPath(curvePath, curvePaint);

    // 4. Compute Points P and Q
    final y0 = _f(x0);
    final x1 = x0 + h;
    final y1 = _f(x1);

    final pScreen = toScreen(x0, y0);
    final qScreen = toScreen(x1, y1);

    // 5. Draw Tangent Line at P (m_tan = f'(x0))
    final mTan = _fPrime(x0);
    final tanXMin = x0 - 2.5;
    final tanXMax = x0 + 2.5;
    final tanP1 = toScreen(tanXMin, y0 + mTan * (tanXMin - x0));
    final tanP2 = toScreen(tanXMax, y0 + mTan * (tanXMax - x0));

    final tangentPaint = Paint()
      ..color = const Color(0xFF10B981)
      ..strokeWidth = 2.2
      ..style = PaintingStyle.stroke;
    canvas.drawLine(tanP1, tanP2, tangentPaint);

    // 6. Draw Secant Line through P and Q (m_sec = (y1 - y0)/h)
    final mSec = h.abs() < 1e-6 ? mTan : (y1 - y0) / (x1 - x0);
    final safeMSec = mSec.isFinite ? mSec : mTan;
    final secXMin = x0 - 2.0;
    final secXMax = x1 + 2.0;
    final secP1 = toScreen(secXMin, y0 + safeMSec * (secXMin - x0));
    final secP2 = toScreen(secXMax, y0 + safeMSec * (secXMax - x0));

    final secantPaint = Paint()
      ..color = const Color(0xFFF59E0B)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;
    canvas.drawLine(secP1, secP2, secantPaint);

    // 7. Right Triangle (Delta x, Delta y)
    final cornerScreen = toScreen(x1, y0);
    final trianglePaint = Paint()
      ..color = const Color(0xFFF59E0B).withValues(alpha: 0.35)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    canvas.drawLine(pScreen, cornerScreen, trianglePaint);
    canvas.drawLine(cornerScreen, qScreen, trianglePaint);

    // Delta x & Delta y labels if h is large enough
    if (h.abs() > 0.3) {
      final dxMid = toScreen(x0 + h / 2, y0 - 0.25);
      _drawText(canvas, "Δx = h", dxMid, 10, const Color(0xFFF59E0B));
      final dyMid = toScreen(x1 + 0.25, (y0 + y1) / 2);
      _drawText(canvas, "Δy", dyMid, 10, const Color(0xFFF59E0B));
    }

    // 8. Draw Points P and Q
    final dotFillPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    // Point P
    canvas.drawCircle(pScreen, 5.0, dotFillPaint);
    final pRingPaint = Paint()
      ..color = const Color(0xFF10B981)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5;
    canvas.drawCircle(pScreen, 7.0, pRingPaint);
    _drawText(canvas, "P", Offset(pScreen.dx - 14, pScreen.dy - 12), 12, const Color(0xFF10B981));

    // Point Q
    canvas.drawCircle(qScreen, 4.5, dotFillPaint);
    final qRingPaint = Paint()
      ..color = const Color(0xFFF59E0B)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    canvas.drawCircle(qScreen, 6.5, qRingPaint);
    _drawText(canvas, "Q", Offset(qScreen.dx + 12, qScreen.dy - 10), 12, const Color(0xFFF59E0B));
  }

  void _drawText(Canvas canvas, String text, Offset center, double fontSize, Color color) {
    final textSpan = TextSpan(
      text: text,
      style: TextStyle(
        color: color,
        fontSize: fontSize,
        fontWeight: FontWeight.bold,
      ),
    );
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    final offset = Offset(center.dx - textPainter.width / 2, center.dy - textPainter.height / 2);
    textPainter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant DynamicTangentPainter oldDelegate) {
    return oldDelegate.curveType != curveType ||
        oldDelegate.x0 != x0 ||
        oldDelegate.h != h;
  }
}

class DynamicTangentCanvas extends StatefulWidget {
  final double initialX0;
  final double initialH;

  const DynamicTangentCanvas({
    super.key,
    this.initialX0 = 1.0,
    this.initialH = 1.0,
  });

  /// h parametresi sınırlandırma (h >= 0.001 ile h = 0 tanımsızlığını önleme)
  static double clampH(double h) {
    if (!h.isFinite || h < 0.001) return 0.001;
    if (h > 2.0) return 2.0;
    return h;
  }

  @override
  State<DynamicTangentCanvas> createState() => _DynamicTangentCanvasState();
}

class _DynamicTangentCanvasState extends State<DynamicTangentCanvas> {
  late CalculusCurveType _curveType;
  late double _x0;
  late double _h;

  @override
  void initState() {
    super.initState();
    _curveType = CalculusCurveType.parabola;
    _x0 = widget.initialX0.isFinite ? widget.initialX0.clamp(-3.0, 3.0) : 1.0;
    _h = DynamicTangentCanvas.clampH(widget.initialH);
  }

  @override
  void didUpdateWidget(covariant DynamicTangentCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialX0 != widget.initialX0) {
      _x0 = widget.initialX0.isFinite ? widget.initialX0.clamp(-3.0, 3.0) : 1.0;
    }
    if (oldWidget.initialH != widget.initialH) {
      _h = DynamicTangentCanvas.clampH(widget.initialH);
    }
  }

  double _computeSecantSlope() {
    // h -> 0 tanımsızlık koruması (h >= 0.001 veya limit yaklaşımı)
    if (_h.abs() < 0.001) {
      return _computeTangentSlope();
    }
    double f(double x) {
      switch (_curveType) {
        case CalculusCurveType.parabola:
          return 0.5 * x * x;
        case CalculusCurveType.cubic:
          return 0.25 * x * x * x;
        case CalculusCurveType.sine:
          return 1.8 * math.sin(x);
      }
    }
    return (f(_x0 + _h) - f(_x0)) / _h;
  }

  double _computeTangentSlope() {
    switch (_curveType) {
      case CalculusCurveType.parabola:
        return _x0;
      case CalculusCurveType.cubic:
        return 0.75 * _x0 * _x0;
      case CalculusCurveType.sine:
        return 1.8 * math.cos(_x0);
    }
  }

  @override
  Widget build(BuildContext context) {
    final mSec = _computeSecantSlope();
    final mTan = _computeTangentSlope();
    final deltaM = (mSec - mTan).abs();
    final isConverged = deltaM < 0.08;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Expanded(
                child: Row(
                  children: [
                    Icon(Icons.show_chart, color: Color(0xFF38BDF8), size: 20),
                    SizedBox(width: 6),
                    Flexible(
                      child: Text(
                        "Dinamik Türev & Teğet Simülatörü",
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: isConverged
                      ? const Color(0xFF10B981).withValues(alpha: 0.2)
                      : const Color(0xFFF59E0B).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isConverged ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isConverged ? Icons.check_circle : Icons.trending_up,
                      color: isConverged ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                      size: 14,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      isConverged ? "Teğete Yakınsadı (Limit!)" : "Sekant Doğrusu",
                      style: TextStyle(
                        color: isConverged ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Function Curve Selector Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                ChoiceChip(
                  label: const Text("f(x) = 0.5x²"),
                  selected: _curveType == CalculusCurveType.parabola,
                  onSelected: (val) {
                    if (val) setState(() => _curveType = CalculusCurveType.parabola);
                  },
                  selectedColor: const Color(0xFF38BDF8).withValues(alpha: 0.3),
                  labelStyle: TextStyle(
                    color: _curveType == CalculusCurveType.parabola ? Colors.white : Colors.white60,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(width: 8),
                ChoiceChip(
                  label: const Text("f(x) = 0.25x³"),
                  selected: _curveType == CalculusCurveType.cubic,
                  onSelected: (val) {
                    if (val) setState(() => _curveType = CalculusCurveType.cubic);
                  },
                  selectedColor: const Color(0xFF38BDF8).withValues(alpha: 0.3),
                  labelStyle: TextStyle(
                    color: _curveType == CalculusCurveType.cubic ? Colors.white : Colors.white60,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(width: 8),
                ChoiceChip(
                  label: const Text("f(x) = 1.8 sin(x)"),
                  selected: _curveType == CalculusCurveType.sine,
                  onSelected: (val) {
                    if (val) setState(() => _curveType = CalculusCurveType.sine);
                  },
                  selectedColor: const Color(0xFF38BDF8).withValues(alpha: 0.3),
                  labelStyle: TextStyle(
                    color: _curveType == CalculusCurveType.sine ? Colors.white : Colors.white60,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Interactive Canvas Area
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: Container(
              height: 240,
              width: double.infinity,
              color: const Color(0xFF0B1120),
              child: RepaintBoundary(
                child: CustomPaint(
                  painter: DynamicTangentPainter(
                    curveType: _curveType,
                    x0: _x0,
                    h: _h,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 14),

          // Slope Comparison Dashboard
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFFF59E0B).withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Sekant Eğimi (m_sec)",
                        style: TextStyle(color: Color(0xFFF59E0B), fontSize: 11),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        mSec.toStringAsFixed(3),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        "[f(x₀+h) - f(x₀)] / h",
                        style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 9),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Teğet Eğimi (m_tan)",
                        style: TextStyle(color: Color(0xFF10B981), fontSize: 11),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        mTan.toStringAsFixed(3),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        "f'(x₀) anlık türev",
                        style: TextStyle(color: Colors.white.withValues(alpha: 0.4), fontSize: 9),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Instantaneous derivative limit formula card: m = lim_{h->0} [f(x0+h)-f(x0)]/h = f'(x0)
          Container(
            key: const Key('instantaneous_slope_formula_card'),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.functions, color: Color(0xFF38BDF8), size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    "Anlık Eğim: m = lim_{h→0} [f(x₀+h) - f(x₀)] / h = f'(x₀) = ${mTan.toStringAsFixed(3)}",
                    style: const TextStyle(
                      color: Color(0xFF38BDF8),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // h-Slider & Presets
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Adım Boyutu (h = ${_h.toStringAsFixed(3)})",
                style: const TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600),
              ),
              Text(
                "Δm = ${deltaM.toStringAsFixed(3)}",
                style: TextStyle(
                  color: isConverged ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: const Color(0xFF38BDF8),
              inactiveTrackColor: Colors.white12,
              thumbColor: const Color(0xFF38BDF8),
              overlayColor: const Color(0xFF38BDF8).withValues(alpha: 0.2),
            ),
            child: Slider(
              value: DynamicTangentCanvas.clampH(_h),
              min: 0.001,
              max: 2.0,
              onChanged: (val) {
                setState(() => _h = DynamicTangentCanvas.clampH(val));
              },
            ),
          ),

          // Presets: h -> 1.5, 0.8, 0.3, 0.02, 0.001
          Wrap(
            spacing: 8,
            children: [
              ActionChip(
                label: const Text("h = 1.50"),
                backgroundColor: const Color(0xFF1E293B),
                labelStyle: const TextStyle(color: Colors.white70, fontSize: 11),
                onPressed: () => setState(() => _h = 1.50),
              ),
              ActionChip(
                label: const Text("h = 0.80"),
                backgroundColor: const Color(0xFF1E293B),
                labelStyle: const TextStyle(color: Colors.white70, fontSize: 11),
                onPressed: () => setState(() => _h = 0.80),
              ),
              ActionChip(
                label: const Text("h = 0.30"),
                backgroundColor: const Color(0xFF1E293B),
                labelStyle: const TextStyle(color: Colors.white70, fontSize: 11),
                onPressed: () => setState(() => _h = 0.30),
              ),
              ActionChip(
                label: const Text("h → 0.02 (Limit)"),
                backgroundColor: const Color(0xFF10B981).withValues(alpha: 0.25),
                labelStyle: const TextStyle(color: Color(0xFF10B981), fontSize: 11, fontWeight: FontWeight.bold),
                onPressed: () => setState(() => _h = 0.02),
              ),
              ActionChip(
                key: const Key('tangent_preset_h_limit_0001'),
                label: const Text("h → 0.001 (Türev Limiti)"),
                backgroundColor: const Color(0xFF10B981).withValues(alpha: 0.35),
                labelStyle: const TextStyle(color: Color(0xFF34D399), fontSize: 11, fontWeight: FontWeight.bold),
                onPressed: () => setState(() => _h = 0.001),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
