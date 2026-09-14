import 'dart:math' as math;
import 'package:flutter/material.dart';

enum RiemannMethod {
  left,
  right,
  midpoint,
  trapezoid,
}

enum IntegralFunctionType {
  parabola,
  invertedParabola,
  sineShifted,
}

class RiemannIntegralPainter extends CustomPainter {
  final IntegralFunctionType funcType;
  final RiemannMethod method;
  final int n;
  final double a;
  final double b;

  RiemannIntegralPainter({
    required this.funcType,
    required this.method,
    required this.n,
    required this.a,
    required this.b,
  });

  double _f(double x) {
    switch (funcType) {
      case IntegralFunctionType.parabola:
        return 0.5 * x * x;
      case IntegralFunctionType.invertedParabola:
        return 2.5 - 0.4 * x * x;
      case IntegralFunctionType.sineShifted:
        return math.sin(x) + 1.2;
    }
  }

  @override
  void paint(Canvas canvas, Size size) {
    final origin = Offset(size.width * 0.15, size.height * 0.78);
    final scaleX = (size.width * 0.75) / (b - a + 0.8);
    final scaleY = (size.height * 0.65) / 3.2;

    Offset toScreen(double x, double y) {
      return Offset(origin.dx + (x - a) * scaleX, origin.dy - y * scaleY);
    }

    // 1. Grid
    final gridPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.06)
      ..strokeWidth = 1.0;

    for (double gx = -0.5; gx <= (b - a) + 0.8; gx += 0.5) {
      final p1 = toScreen(a + gx, -0.5);
      final p2 = toScreen(a + gx, 3.2);
      canvas.drawLine(p1, p2, gridPaint);
    }
    for (double gy = 0.0; gy <= 3.2; gy += 0.5) {
      final p1 = toScreen(a - 0.5, gy);
      final p2 = toScreen(b + 0.5, gy);
      canvas.drawLine(p1, p2, gridPaint);
    }

    // 2. Axes
    final axisPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.25)
      ..strokeWidth = 1.5;

    canvas.drawLine(toScreen(a - 0.4, 0), toScreen(b + 0.6, 0), axisPaint);
    canvas.drawLine(toScreen(0, -0.3), toScreen(0, 3.0), axisPaint);

    _drawText(canvas, "x", toScreen(b + 0.5, -0.2), 11, Colors.white54);
    _drawText(canvas, "y", toScreen(0.1, 2.9), 11, Colors.white54);

    // 3. Riemann Rectangles / Trapezoids
    final dx = (b - a) / n;
    final rectFillPaint = Paint()
      ..color = _getMethodColor(method).withValues(alpha: 0.22)
      ..style = PaintingStyle.fill;

    final rectBorderPaint = Paint()
      ..color = _getMethodColor(method).withValues(alpha: 0.75)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    for (int i = 0; i < n; i++) {
      final xLeft = a + i * dx;
      final xRight = a + (i + 1) * dx;

      if (method == RiemannMethod.trapezoid) {
        final yLeft = _f(xLeft);
        final yRight = _f(xRight);
        final p0 = toScreen(xLeft, 0);
        final p1 = toScreen(xLeft, yLeft);
        final p2 = toScreen(xRight, yRight);
        final p3 = toScreen(xRight, 0);

        final trapPath = Path()
          ..moveTo(p0.dx, p0.dy)
          ..lineTo(p1.dx, p1.dy)
          ..lineTo(p2.dx, p2.dy)
          ..lineTo(p3.dx, p3.dy)
          ..close();

        canvas.drawPath(trapPath, rectFillPaint);
        canvas.drawPath(trapPath, rectBorderPaint);
      } else {
        double evalX;
        switch (method) {
          case RiemannMethod.left:
            evalX = xLeft;
            break;
          case RiemannMethod.right:
            evalX = xRight;
            break;
          case RiemannMethod.midpoint:
            evalX = xLeft + 0.5 * dx;
            break;
          default:
            evalX = xLeft;
        }

        final height = _f(evalX);
        final topLeft = toScreen(xLeft, height);
        final bottomRight = toScreen(xRight, 0);
        final rect = Rect.fromPoints(topLeft, bottomRight);

        canvas.drawRect(rect, rectFillPaint);
        canvas.drawRect(rect, rectBorderPaint);

        // Mark sample point on curve
        if (n <= 16) {
          final samplePoint = toScreen(evalX, height);
          final dotPaint = Paint()
            ..color = _getMethodColor(method)
            ..style = PaintingStyle.fill;
          canvas.drawCircle(samplePoint, 3.0, dotPaint);
        }
      }
    }

    // 4. Function Curve
    final curvePath = Path();
    bool first = true;
    for (double x = a - 0.2; x <= b + 0.4; x += 0.03) {
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
      ..strokeWidth = 2.8
      ..strokeCap = StrokeCap.round;
    canvas.drawPath(curvePath, curvePaint);

    // 5. Boundary Lines a and b
    final boundaryPaint = Paint()
      ..color = Colors.amberAccent.withValues(alpha: 0.6)
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;

    canvas.drawLine(toScreen(a, 0), toScreen(a, _f(a)), boundaryPaint);
    canvas.drawLine(toScreen(b, 0), toScreen(b, _f(b)), boundaryPaint);

    _drawText(canvas, "a=${a.toStringAsFixed(1)}", toScreen(a - 0.1, -0.25), 10, Colors.amberAccent);
    _drawText(canvas, "b=${b.toStringAsFixed(1)}", toScreen(b - 0.1, -0.25), 10, Colors.amberAccent);
  }

  Color _getMethodColor(RiemannMethod m) {
    switch (m) {
      case RiemannMethod.left:
        return const Color(0xFF60A5FA); // blue
      case RiemannMethod.right:
        return const Color(0xFFF59E0B); // amber
      case RiemannMethod.midpoint:
        return const Color(0xFF34D399); // emerald
      case RiemannMethod.trapezoid:
        return const Color(0xFFA78BFA); // purple
    }
  }

  void _drawText(Canvas canvas, String text, Offset offset, double fontSize, Color color) {
    final textSpan = TextSpan(
      text: text,
      style: TextStyle(
        color: color,
        fontSize: fontSize,
        fontWeight: FontWeight.w500,
      ),
    );
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant RiemannIntegralPainter oldDelegate) {
    return oldDelegate.funcType != funcType ||
        oldDelegate.method != method ||
        oldDelegate.n != n ||
        oldDelegate.a != a ||
        oldDelegate.b != b;
  }
}

class RiemannIntegralCanvas extends StatefulWidget {
  final int initialN;
  final RiemannMethod initialMethod;
  final IntegralFunctionType initialFunc;

  const RiemannIntegralCanvas({
    super.key,
    this.initialN = 8,
    this.initialMethod = RiemannMethod.midpoint,
    this.initialFunc = IntegralFunctionType.parabola,
  });

  @override
  State<RiemannIntegralCanvas> createState() => _RiemannIntegralCanvasState();
}

class _RiemannIntegralCanvasState extends State<RiemannIntegralCanvas> {
  late int _n;
  late RiemannMethod _method;
  late IntegralFunctionType _funcType;
  final double _a = 0.0;
  final double _b = 2.0;

  @override
  void initState() {
    super.initState();
    _n = widget.initialN;
    _method = widget.initialMethod;
    _funcType = widget.initialFunc;
  }

  double _f(double x) {
    switch (_funcType) {
      case IntegralFunctionType.parabola:
        return 0.5 * x * x;
      case IntegralFunctionType.invertedParabola:
        return 2.5 - 0.4 * x * x;
      case IntegralFunctionType.sineShifted:
        return math.sin(x) + 1.2;
    }
  }

  double _calculateExactArea() {
    switch (_funcType) {
      case IntegralFunctionType.parabola:
        // int_0^2 0.5 x^2 dx = [0.5/3 * x^3]_0^2 = 8 / 6 = 4/3 ~ 1.33333
        return 4.0 / 3.0;
      case IntegralFunctionType.invertedParabola:
        // int_0^2 (2.5 - 0.4 x^2) dx = 2.5*2 - 0.4/3 * 8 = 5.0 - 1.06667 = 3.93333
        return 5.0 - (0.4 / 3.0) * 8.0;
      case IntegralFunctionType.sineShifted:
        // int_0^2 (sin(x) + 1.2) dx = [-cos(x) + 1.2x]_0^2 = (-cos(2) + 2.4) - (-1 + 0) = 3.4 - cos(2)
        return 3.4 - math.cos(2.0);
    }
  }

  double _calculateRiemannSum() {
    final dx = (_b - _a) / _n;
    double sum = 0.0;

    for (int i = 0; i < _n; i++) {
      final xLeft = _a + i * dx;
      final xRight = _a + (i + 1) * dx;

      if (_method == RiemannMethod.trapezoid) {
        sum += 0.5 * (_f(xLeft) + _f(xRight)) * dx;
      } else {
        double evalX;
        switch (_method) {
          case RiemannMethod.left:
            evalX = xLeft;
            break;
          case RiemannMethod.right:
            evalX = xRight;
            break;
          case RiemannMethod.midpoint:
            evalX = xLeft + 0.5 * dx;
            break;
          default:
            evalX = xLeft;
        }
        sum += _f(evalX) * dx;
      }
    }
    return sum;
  }

  @override
  Widget build(BuildContext context) {
    final exactArea = _calculateExactArea();
    final approxArea = _calculateRiemannSum();
    final deltaA = (approxArea - exactArea).abs();
    final isConverged = deltaA < 0.05;

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
            // Title & Convergence Badge
            Row(
              children: [
                Expanded(
                  child: Row(
                    children: [
                      const Icon(Icons.area_chart, color: Color(0xFF38BDF8), size: 20),
                      const SizedBox(width: 8),
                      const Flexible(
                        child: Text(
                          "Riemann İntegral & Alan Simülatörü",
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isConverged
                        ? const Color(0xFF10B981).withValues(alpha: 0.2)
                        : const Color(0xFFF59E0B).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isConverged ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                      width: 1,
                    ),
                  ),
                  child: Text(
                    isConverged ? "Yakınsadı (Limit!)" : "ΔA Yaklaşıyor",
                    style: TextStyle(
                      color: isConverged ? const Color(0xFF34D399) : const Color(0xFFFBBF24),
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Function Selector Chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildFunctionChip("f(x) = 0.5x²", IntegralFunctionType.parabola),
                  const SizedBox(width: 8),
                  _buildFunctionChip("f(x) = 2.5 - 0.4x²", IntegralFunctionType.invertedParabola),
                  const SizedBox(width: 8),
                  _buildFunctionChip("f(x) = sin(x) + 1.2", IntegralFunctionType.sineShifted),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Method Selector Chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildMethodChip("Sol Toplam", RiemannMethod.left),
                  const SizedBox(width: 8),
                  _buildMethodChip("Sağ Toplam", RiemannMethod.right),
                  const SizedBox(width: 8),
                  _buildMethodChip("Orta Nokta", RiemannMethod.midpoint),
                  const SizedBox(width: 8),
                  _buildMethodChip("Yamuk Kuralı", RiemannMethod.trapezoid),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Canvas Display
            Container(
              height: 220,
              width: double.infinity,
              decoration: BoxDecoration(
                color: const Color(0xFF020617),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF1E293B)),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: CustomPaint(
                  painter: RiemannIntegralPainter(
                    funcType: _funcType,
                    method: _method,
                    n: _n,
                    a: _a,
                    b: _b,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 14),

            // Metrics Display (Riemann Sum, Exact Area, Error)
            Row(
              children: [
                Expanded(
                  child: _buildMetricBox(
                    "Riemann Toplamı (S_n)",
                    approxArea.toStringAsFixed(4),
                    const Color(0xFF38BDF8),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildMetricBox(
                    "Tam Alan (∫ f dx)",
                    exactArea.toStringAsFixed(4),
                    const Color(0xFF34D399),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildMetricBox(
                    "Hata Payı (|ΔA|)",
                    deltaA.toStringAsFixed(4),
                    isConverged ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Partition Slider (n)
            Row(
              children: [
                Text(
                  "Bölüntü Sayısı (n = $_n)",
                  style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Text(
                  "Δx = ${((_b - _a) / _n).toStringAsFixed(3)}",
                  style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 11, fontFamily: "monospace"),
                ),
              ],
            ),
            SliderTheme(
              data: SliderTheme.of(context).copyWith(
                activeTrackColor: const Color(0xFF38BDF8),
                inactiveTrackColor: const Color(0xFF334155),
                thumbColor: const Color(0xFF38BDF8),
                overlayColor: const Color(0xFF38BDF8).withValues(alpha: 0.2),
              ),
              child: Slider(
                value: _n.toDouble(),
                min: 2,
                max: 64,
                divisions: 31,
                label: "n = $_n",
                onChanged: (val) {
                  setState(() {
                    _n = val.round();
                  });
                },
              ),
            ),

            // Quick Preset Chips (n = 4, 16, 64)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildNPresetChip("n = 4 (Kaba)", 4),
                const SizedBox(width: 8),
                _buildNPresetChip("n = 16 (Dengeli)", 16),
                const SizedBox(width: 8),
                _buildNPresetChip("n = 64 (Limit)", 64),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFunctionChip(String label, IntegralFunctionType type) {
    final isSelected = _funcType == type;
    return ChoiceChip(
      label: Text(label, style: TextStyle(color: isSelected ? Colors.white : Colors.white60, fontSize: 11)),
      selected: isSelected,
      selectedColor: const Color(0xFF0284C7),
      backgroundColor: const Color(0xFF1E293B),
      onSelected: (selected) {
        if (selected) {
          setState(() {
            _funcType = type;
          });
        }
      },
    );
  }

  Widget _buildMethodChip(String label, RiemannMethod m) {
    final isSelected = _method == m;
    return ChoiceChip(
      label: Text(label, style: TextStyle(color: isSelected ? Colors.white : Colors.white60, fontSize: 11)),
      selected: isSelected,
      selectedColor: const Color(0xFF0D9488),
      backgroundColor: const Color(0xFF1E293B),
      onSelected: (selected) {
        if (selected) {
          setState(() {
            _method = m;
          });
        }
      },
    );
  }

  Widget _buildNPresetChip(String label, int count) {
    final isSelected = _n == count;
    return ActionChip(
      label: Text(label, style: TextStyle(color: isSelected ? Colors.white : Colors.white70, fontSize: 11)),
      backgroundColor: isSelected ? const Color(0xFF38BDF8).withValues(alpha: 0.3) : const Color(0xFF1E293B),
      side: BorderSide(
        color: isSelected ? const Color(0xFF38BDF8) : Colors.transparent,
      ),
      onPressed: () {
        setState(() {
          _n = count;
        });
      },
    );
  }

  Widget _buildMetricBox(String title, String value, Color accentColor) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF020617),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(color: Colors.white54, fontSize: 10),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              color: accentColor,
              fontSize: 14,
              fontWeight: FontWeight.bold,
              fontFamily: "monospace",
            ),
          ),
        ],
      ),
    );
  }
}
