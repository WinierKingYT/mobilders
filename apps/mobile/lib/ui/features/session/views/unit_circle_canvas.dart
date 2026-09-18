import 'dart:math' as math;
import 'package:flutter/material.dart';

class UnitCirclePainter extends CustomPainter {
  final double angleDegrees;

  UnitCirclePainter({required this.angleDegrees});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) * 0.38;

    final axisPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.3)
      ..strokeWidth = 1.5;

    // 1. Draw X and Y Axes
    canvas.drawLine(Offset(10, center.dy), Offset(size.width - 10, center.dy), axisPaint);
    canvas.drawLine(Offset(center.dx, 10), Offset(center.dx, size.height - 10), axisPaint);

    _drawText(canvas, "cos (x)", Offset(size.width - 24, center.dy + 12), 11, const Color(0xFF38BDF8));
    _drawText(canvas, "sin (y)", Offset(center.dx + 26, 14), 11, const Color(0xFF10B981));

    // 2. Draw Unit Circle
    final circlePaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.15)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    canvas.drawCircle(center, radius, circlePaint);

    // 3. Compute Angle and Coordinates
    final rad = angleDegrees * math.pi / 180.0;
    final cosVal = math.cos(rad);
    final sinVal = math.sin(rad);

    // Screen coordinates: Y is inverted
    final pX = center.dx + cosVal * radius;
    final pY = center.dy - sinVal * radius;
    final pOffset = Offset(pX, pY);

    // 4. Angle Arc
    final arcPaint = Paint()
      ..color = const Color(0xFFF59E0B).withValues(alpha: 0.4)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    final arcRect = Rect.fromCircle(center: center, radius: radius * 0.25);
    canvas.drawArc(arcRect, 0, -rad, false, arcPaint);

    // 5. Projection Lines
    // cos(theta): cyan line along x axis
    final cosPaint = Paint()
      ..color = const Color(0xFF38BDF8)
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(center, Offset(pX, center.dy), cosPaint);

    // sin(theta): emerald line along projection
    final sinPaint = Paint()
      ..color = const Color(0xFF10B981)
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(pX, center.dy), pOffset, sinPaint);

    // Dashed ray from origin to P(theta)
    final hypPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.8)
      ..strokeWidth = 2.0;
    canvas.drawLine(center, pOffset, hypPaint);

    // Point P(theta)
    final dotPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;
    canvas.drawCircle(pOffset, 5.0, dotPaint);

    final dotRingPaint = Paint()
      ..color = const Color(0xFFF59E0B)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    canvas.drawCircle(pOffset, 7.0, dotRingPaint);
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
  bool shouldRepaint(covariant UnitCirclePainter oldDelegate) {
    return oldDelegate.angleDegrees != angleDegrees;
  }
}

class UnitCircleCanvas extends StatefulWidget {
  final double initialAngle;
  final ValueChanged<double>? onAngleChanged;

  const UnitCircleCanvas({
    super.key,
    this.initialAngle = 45.0,
    this.onAngleChanged,
  });

  @override
  State<UnitCircleCanvas> createState() => _UnitCircleCanvasState();
}

class _UnitCircleCanvasState extends State<UnitCircleCanvas> {
  late double _angleDegrees;

  @override
  void initState() {
    super.initState();
    _angleDegrees = widget.initialAngle;
  }

  String _getQuadrantName(double deg) {
    final norm = deg % 360.0;
    if (norm >= 0 && norm < 90) return "1. Bölge (+, +)";
    if (norm >= 90 && norm < 180) return "2. Bölge (-, +)";
    if (norm >= 180 && norm < 270) return "3. Bölge (-, -)";
    return "4. Bölge (+, -)";
  }

  String _getRadianLabel(double deg) {
    final norm = deg.round() % 360;
    if (norm == 0) return "0 rad";
    if (norm == 30) return "π/6 rad";
    if (norm == 45) return "π/4 rad";
    if (norm == 60) return "π/3 rad";
    if (norm == 90) return "π/2 rad";
    if (norm == 180) return "π rad";
    if (norm == 270) return "3π/2 rad";
    if (norm == 360) return "2π rad";
    return "${(norm * math.pi / 180.0).toStringAsFixed(2)} rad";
  }

  @override
  Widget build(BuildContext context) {
    final rad = _angleDegrees * math.pi / 180.0;
    final cosVal = math.cos(rad);
    final sinVal = math.sin(rad);
    final tanVal = (cosVal.abs() < 1e-4) ? null : math.tan(rad);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Row(
            children: [
              const Icon(Icons.circle_outlined, color: Color(0xFF38BDF8), size: 20),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  "İnteraktif Birim Çember Kanvası",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  _getQuadrantName(_angleDegrees),
                  style: const TextStyle(
                    color: Color(0xFFF59E0B),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Unit Circle Visual Area
          SizedBox(
            height: 220,
            child: CustomPaint(
              painter: UnitCirclePainter(angleDegrees: _angleDegrees),
              size: Size.infinite,
            ),
          ),

          const SizedBox(height: 12),

          // Angle Slider and Labels
          Row(
            children: [
              Text(
                "${_angleDegrees.toStringAsFixed(0)}°",
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                "(${_getRadianLabel(_angleDegrees)})",
                style: const TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 12,
                ),
              ),
              Expanded(
                child: Slider(
                  value: _angleDegrees,
                  min: 0.0,
                  max: 360.0,
                  divisions: 72,
                  activeColor: const Color(0xFF38BDF8),
                  inactiveColor: const Color(0xFF334155),
                  onChanged: (val) {
                    setState(() {
                      _angleDegrees = val;
                    });
                    widget.onAngleChanged?.call(val);
                  },
                ),
              ),
            ],
          ),

          // Preset Buttons
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [0.0, 30.0, 45.0, 60.0, 90.0, 180.0, 270.0].map((preset) {
                final isSelected = (_angleDegrees - preset).abs() < 1.0;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(
                      "${preset.toInt()}°",
                      style: TextStyle(
                        fontSize: 11,
                        color: isSelected ? Colors.black : Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    selected: isSelected,
                    selectedColor: const Color(0xFF38BDF8),
                    backgroundColor: const Color(0xFF1E293B),
                    onSelected: (_) {
                      setState(() {
                        _angleDegrees = preset;
                      });
                      widget.onAngleChanged?.call(preset);
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 12),

          // Values Readout Box
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMetric(
                  "cos θ (Apsis)",
                  cosVal.toStringAsFixed(3),
                  const Color(0xFF38BDF8),
                ),
                _buildMetric(
                  "sin θ (Ordinat)",
                  sinVal.toStringAsFixed(3),
                  const Color(0xFF10B981),
                ),
                _buildMetric(
                  "tan θ (Eğim)",
                  tanVal != null ? tanVal.toStringAsFixed(3) : "Tanımsız",
                  const Color(0xFFF59E0B),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetric(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF94A3B8),
            fontSize: 10,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 13,
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }
}
