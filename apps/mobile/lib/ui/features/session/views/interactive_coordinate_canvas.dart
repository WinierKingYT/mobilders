import 'dart:math' as math;
import 'package:flutter/material.dart';

enum GeometryDisplayMode {
  lineAndSlope,
  circle,
  vectors,
}

class InteractiveCoordinateCanvas extends StatefulWidget {
  final Offset initialPointA;
  final Offset initialPointB;
  final bool interactive;
  final ValueChanged<Offset>? onPointAChanged;
  final ValueChanged<Offset>? onPointBChanged;

  const InteractiveCoordinateCanvas({
    super.key,
    this.initialPointA = const Offset(1.0, 2.0),
    this.initialPointB = const Offset(5.0, 5.0),
    this.interactive = true,
    this.onPointAChanged,
    this.onPointBChanged,
  });

  @override
  State<InteractiveCoordinateCanvas> createState() =>
      _InteractiveCoordinateCanvasState();
}

class _InteractiveCoordinateCanvasState
    extends State<InteractiveCoordinateCanvas> {
  late Offset _pointA;
  late Offset _pointB;
  GeometryDisplayMode _mode = GeometryDisplayMode.lineAndSlope;

  @override
  void initState() {
    super.initState();
    _pointA = widget.initialPointA;
    _pointB = widget.initialPointB;
  }

  @override
  void didUpdateWidget(covariant InteractiveCoordinateCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialPointA != widget.initialPointA) {
      _pointA = widget.initialPointA;
    }
    if (oldWidget.initialPointB != widget.initialPointB) {
      _pointB = widget.initialPointB;
    }
  }

  double get _dx => _pointB.dx - _pointA.dx;
  double get _dy => _pointB.dy - _pointA.dy;

  double get _distance => math.sqrt(_dx * _dx + _dy * _dy);

  double? get _slope => _dx.abs() < 1e-6 ? null : _dy / _dx;

  double get _angleDeg {
    if (_slope == null) return 90.0;
    double deg = math.atan(_slope!) * 180.0 / math.pi;
    if (deg < 0) deg += 180.0;
    return deg;
  }

  double get _dotProduct => _pointA.dx * _pointB.dx + _pointA.dy * _pointB.dy;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Mode Selector
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
          child: SegmentedButton<GeometryDisplayMode>(
            segments: const [
              ButtonSegment(
                value: GeometryDisplayMode.lineAndSlope,
                label: Text("Doğru & Eğim", style: TextStyle(fontSize: 12)),
                icon: Icon(Icons.show_chart, size: 16),
              ),
              ButtonSegment(
                value: GeometryDisplayMode.circle,
                label: Text("Çember", style: TextStyle(fontSize: 12)),
                icon: Icon(Icons.circle_outlined, size: 16),
              ),
              ButtonSegment(
                value: GeometryDisplayMode.vectors,
                label: Text("Vektörler", style: TextStyle(fontSize: 12)),
                icon: Icon(Icons.arrow_outward, size: 16),
              ),
            ],
            selected: {_mode},
            onSelectionChanged: (Set<GeometryDisplayMode> selected) {
              setState(() {
                _mode = selected.first;
              });
            },
          ),
        ),

        // Metrics Banner
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
          padding: const EdgeInsets.all(10.0),
          decoration: BoxDecoration(
            color: Colors.blueGrey.shade900.withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(10.0),
            border: Border.all(color: Colors.white24, width: 0.8),
          ),
          child: Wrap(
            spacing: 14.0,
            runSpacing: 6.0,
            alignment: WrapAlignment.spaceAround,
            children: [
              Text(
                "A(${_pointA.dx.toStringAsFixed(1)}, ${_pointA.dy.toStringAsFixed(1)})",
                style: const TextStyle(
                  color: Colors.cyanAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              Text(
                "B(${_pointB.dx.toStringAsFixed(1)}, ${_pointB.dy.toStringAsFixed(1)})",
                style: const TextStyle(
                  color: Colors.amberAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              Text(
                "Uzaklık: ${_distance.toStringAsFixed(2)}",
                key: const Key("stat_distance"),
                style: const TextStyle(color: Colors.white, fontSize: 13),
              ),
              if (_mode == GeometryDisplayMode.lineAndSlope) ...[
                Text(
                  _slope == null
                      ? "Eğim: Tanımsız (Düşey)"
                      : "Eğim: ${_slope!.toStringAsFixed(2)}",
                  key: const Key("stat_slope"),
                  style: const TextStyle(
                    color: Colors.lightGreenAccent,
                    fontSize: 13,
                  ),
                ),
                Text(
                  "Açı: ${_angleDeg.toStringAsFixed(1)}°",
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ] else if (_mode == GeometryDisplayMode.circle) ...[
                Text(
                  "Yarıçap r: ${_distance.toStringAsFixed(2)}",
                  style: const TextStyle(
                    color: Colors.purpleAccent,
                    fontSize: 13,
                  ),
                ),
                Text(
                  "Alan: ${(math.pi * _distance * _distance).toStringAsFixed(1)}",
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
              ] else if (_mode == GeometryDisplayMode.vectors) ...[
                Text(
                  "u · v: ${_dotProduct.toStringAsFixed(2)}",
                  key: const Key("stat_dot"),
                  style: TextStyle(
                    color: _dotProduct.abs() < 1e-4
                        ? Colors.greenAccent
                        : Colors.orangeAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
                if (_dotProduct.abs() < 1e-4)
                  const Text(
                    "Dik Vektörler (u ⊥ v)",
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
              ],
            ],
          ),
        ),

        // Custom Paint Canvas
        Container(
          height: 260,
          margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
          decoration: BoxDecoration(
            color: const Color(0xFF0F172A),
            borderRadius: BorderRadius.circular(12.0),
            border: Border.all(color: Colors.white12),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12.0),
            child: RepaintBoundary(
              child: CustomPaint(
                key: const Key("coord_canvas"),
                painter: _CoordinatePainter(
                  pointA: _pointA,
                  pointB: _pointB,
                  mode: _mode,
                ),
              ),
            ),
          ),
        ),

        // Point B Drag / Slider Adjusters (for precise control)
        if (widget.interactive)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
            child: Column(
              children: [
                Row(
                  children: [
                    const Text("B Apsisi (x): ", style: TextStyle(fontSize: 12)),
                    Expanded(
                      child: Slider(
                        value: _pointB.dx.clamp(-6.0, 6.0),
                        min: -6.0,
                        max: 6.0,
                        divisions: 48,
                        onChanged: (val) {
                          setState(() {
                            _pointB = Offset(val, _pointB.dy);
                          });
                          widget.onPointBChanged?.call(_pointB);
                        },
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    const Text("B Ordinatı (y): ", style: TextStyle(fontSize: 12)),
                    Expanded(
                      child: Slider(
                        value: _pointB.dy.clamp(-6.0, 6.0),
                        min: -6.0,
                        max: 6.0,
                        divisions: 48,
                        onChanged: (val) {
                          setState(() {
                            _pointB = Offset(_pointB.dx, val);
                          });
                          widget.onPointBChanged?.call(_pointB);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _CoordinatePainter extends CustomPainter {
  final Offset pointA;
  final Offset pointB;
  final GeometryDisplayMode mode;

  _CoordinatePainter({
    required this.pointA,
    required this.pointB,
    required this.mode,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (size.width <= 0 || size.height <= 0) return;
    final center = Offset(size.width / 2.0, size.height / 2.0);
    const double gridSpacing = 22.0; // pixels per unit

    Offset toScreen(double x, double y) {
      return Offset(center.dx + x * gridSpacing, center.dy - y * gridSpacing);
    }

    // 1. Grid Lines
    final gridPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.05)
      ..strokeWidth = 1.0;

    for (double x = -10; x <= 10; x += 1.0) {
      canvas.drawLine(
        Offset(center.dx + x * gridSpacing, 0),
        Offset(center.dx + x * gridSpacing, size.height),
        gridPaint,
      );
    }
    for (double y = -8; y <= 8; y += 1.0) {
      canvas.drawLine(
        Offset(0, center.dy - y * gridSpacing),
        Offset(size.width, center.dy - y * gridSpacing),
        gridPaint,
      );
    }

    // 2. Axes
    final axisPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.4)
      ..strokeWidth = 1.5;

    canvas.drawLine(Offset(0, center.dy), Offset(size.width, center.dy), axisPaint);
    canvas.drawLine(Offset(center.dx, 0), Offset(center.dx, size.height), axisPaint);

    // 3. Points in Screen Coordinates
    final pA = toScreen(pointA.dx, pointA.dy);
    final pB = toScreen(pointB.dx, pointB.dy);

    if (mode == GeometryDisplayMode.lineAndSlope) {
      // Draw rise / run right triangle
      final pRight = toScreen(pointB.dx, pointA.dy);
      final trianglePaint = Paint()
        ..color = Colors.cyan.withValues(alpha: 0.15)
        ..style = PaintingStyle.fill;
      final path = Path()
        ..moveTo(pA.dx, pA.dy)
        ..lineTo(pRight.dx, pRight.dy)
        ..lineTo(pB.dx, pB.dy)
        ..close();
      canvas.drawPath(path, trianglePaint);

      final dashedPaint = Paint()
        ..color = Colors.white30
        ..strokeWidth = 1.0
        ..style = PaintingStyle.stroke;
      canvas.drawLine(pA, pRight, dashedPaint);
      canvas.drawLine(pRight, pB, dashedPaint);

      // Line connecting A and B
      final linePaint = Paint()
        ..color = Colors.lightGreenAccent
        ..strokeWidth = 2.5;
      canvas.drawLine(pA, pB, linePaint);
    } else if (mode == GeometryDisplayMode.circle) {
      // Circle centered at A with radius = distance(A, B)
      final rPixels = (pointB - pointA).distance * gridSpacing;
      if (rPixels > 0 && !rPixels.isNaN && !rPixels.isInfinite) {
        final circlePaint = Paint()
          ..color = Colors.purpleAccent.withValues(alpha: 0.3)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2.0;
        canvas.drawCircle(pA, rPixels, circlePaint);
      }

      final radiusLinePaint = Paint()
        ..color = Colors.purpleAccent
        ..strokeWidth = 1.5;
      canvas.drawLine(pA, pB, radiusLinePaint);
    } else if (mode == GeometryDisplayMode.vectors) {
      // Origin O(0,0)
      final pO = toScreen(0, 0);

      // Vector u = OA
      _drawArrow(canvas, pO, pA, Colors.cyanAccent, 2.5);
      // Vector v = OB
      _drawArrow(canvas, pO, pB, Colors.amberAccent, 2.5);

      // Projection of u onto v
      final vNormSq = pointB.dx * pointB.dx + pointB.dy * pointB.dy;
      if (vNormSq > 1e-6) {
        final dot = pointA.dx * pointB.dx + pointB.dy * pointB.dy;
        final projCoeff = dot / vNormSq;
        final projPoint = Offset(pointB.dx * projCoeff, pointB.dy * projCoeff);
        final pProj = toScreen(projPoint.dx, projPoint.dy);

        // Dashed line from A to projection
        final projDashPaint = Paint()
          ..color = Colors.white38
          ..strokeWidth = 1.0;
        canvas.drawLine(pA, pProj, projDashPaint);

        // Projection vector
        _drawArrow(canvas, pO, pProj, Colors.greenAccent, 3.0);
      }
    }

    // 4. Draw Points A and B
    final paintA = Paint()..color = Colors.cyanAccent;
    canvas.drawCircle(pA, 5.0, paintA);

    final paintB = Paint()..color = Colors.amberAccent;
    canvas.drawCircle(pB, 5.0, paintB);
  }

  void _drawArrow(Canvas canvas, Offset from, Offset to, Color color, double width) {
    if ((to - from).distance < 1e-4) return;
    final paint = Paint()
      ..color = color
      ..strokeWidth = width
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(from, to, paint);

    // Arrowhead
    final angle = math.atan2(to.dy - from.dy, to.dx - from.dx);
    const arrowSize = 10.0;
    final path = Path()
      ..moveTo(to.dx, to.dy)
      ..lineTo(
        to.dx - arrowSize * math.cos(angle - math.pi / 6),
        to.dy - arrowSize * math.sin(angle - math.pi / 6),
      )
      ..lineTo(
        to.dx - arrowSize * math.cos(angle + math.pi / 6),
        to.dy - arrowSize * math.sin(angle + math.pi / 6),
      )
      ..close();
    canvas.drawPath(path, Paint()..color = color);
  }

  @override
  bool shouldRepaint(covariant _CoordinatePainter oldDelegate) {
    return oldDelegate.pointA != pointA ||
        oldDelegate.pointB != pointB ||
        oldDelegate.mode != mode;
  }
}
