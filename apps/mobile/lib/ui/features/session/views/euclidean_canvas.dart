import 'dart:math' as math;
import 'package:flutter/material.dart';

enum EuclideanShapePreset {
  isosceles,
  rightTriangle,
  trapezoid,
  circleTangent,
}

class EuclideanCanvas extends StatefulWidget {
  final EuclideanShapePreset initialPreset;
  final bool initialShowAuxiliary;

  const EuclideanCanvas({
    super.key,
    this.initialPreset = EuclideanShapePreset.isosceles,
    this.initialShowAuxiliary = false,
  });

  @override
  State<EuclideanCanvas> createState() => _EuclideanCanvasState();
}

class _EuclideanCanvasState extends State<EuclideanCanvas> {
  late EuclideanShapePreset _preset;
  late bool _showAuxiliary;

  @override
  void initState() {
    super.initState();
    _preset = widget.initialPreset;
    _showAuxiliary = widget.initialShowAuxiliary;
  }

  @override
  void didUpdateWidget(covariant EuclideanCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialPreset != widget.initialPreset) {
      _preset = widget.initialPreset;
    }
    if (oldWidget.initialShowAuxiliary != widget.initialShowAuxiliary) {
      _showAuxiliary = widget.initialShowAuxiliary;
    }
  }

  String get _presetTitle {
    switch (_preset) {
      case EuclideanShapePreset.isosceles:
        return "İkizkenar Üçgen";
      case EuclideanShapePreset.rightTriangle:
        return "Dik Üçgen (Hipotenüs)";
      case EuclideanShapePreset.trapezoid:
        return "Yamuk";
      case EuclideanShapePreset.circleTangent:
        return "Çember & Teğet Doğrusu";
    }
  }

  String get _auxiliaryHint {
    switch (_preset) {
      case EuclideanShapePreset.isosceles:
        return "Sokratik İpucu: Tepe noktasından tabana bir yükseklik indir. Bu dikme tabanı iki eşit parçaya böler ve Pisagor kurmanı sağlar.";
      case EuclideanShapePreset.rightTriangle:
        return "Sokratik İpucu: Dik köşeden hipotenüse bir kenarortay çiz. Muhteşem Üçlü kuralı gereği kenarortay ayrılan parçalara eşittir.";
      case EuclideanShapePreset.trapezoid:
        return "Sokratik İpucu: Üst köşeden karşı yan kenara paralel çizerek şekli paralelkenar ve üçgene dönüştür.";
      case EuclideanShapePreset.circleTangent:
        return "Sokratik İpucu: Çember merkezini teğet noktasına birleştir. Yarıçap doğrusu teğete değme noktasında daima diktir (r ⊥ d).";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Preset Chips
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
          child: Row(
            children: [
              ChoiceChip(
                key: const Key("preset_isosceles"),
                label: const Text("İkizkenar Üçgen"),
                selected: _preset == EuclideanShapePreset.isosceles,
                onSelected: (val) {
                  if (val) setState(() => _preset = EuclideanShapePreset.isosceles);
                },
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                key: const Key("preset_right"),
                label: const Text("Dik Üçgen"),
                selected: _preset == EuclideanShapePreset.rightTriangle,
                onSelected: (val) {
                  if (val) setState(() => _preset = EuclideanShapePreset.rightTriangle);
                },
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                key: const Key("preset_trapezoid"),
                label: const Text("Yamuk"),
                selected: _preset == EuclideanShapePreset.trapezoid,
                onSelected: (val) {
                  if (val) setState(() => _preset = EuclideanShapePreset.trapezoid);
                },
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                key: const Key("preset_circle"),
                label: const Text("Çember & Teğet"),
                selected: _preset == EuclideanShapePreset.circleTangent,
                onSelected: (val) {
                  if (val) setState(() => _preset = EuclideanShapePreset.circleTangent);
                },
              ),
            ],
          ),
        ),

        // Socratic Hint & Action Banner
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
          padding: const EdgeInsets.all(12.0),
          decoration: BoxDecoration(
            color: const Color(0xFF1E293B),
            borderRadius: BorderRadius.circular(10.0),
            border: Border.all(color: Colors.cyan.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _presetTitle,
                    style: const TextStyle(
                      color: Colors.cyanAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  OutlinedButton.icon(
                    key: const Key("btn_toggle_auxiliary"),
                    icon: Icon(
                      _showAuxiliary ? Icons.visibility_off : Icons.architecture,
                      size: 16,
                      color: _showAuxiliary ? Colors.amberAccent : Colors.cyanAccent,
                    ),
                    label: Text(
                      _showAuxiliary ? "Ek Çizimi Gizle" : "Ek Çizimi Göster",
                      style: TextStyle(
                        fontSize: 12,
                        color: _showAuxiliary ? Colors.amberAccent : Colors.cyanAccent,
                      ),
                    ),
                    onPressed: () {
                      setState(() {
                        _showAuxiliary = !_showAuxiliary;
                      });
                    },
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                _auxiliaryHint,
                key: const Key("hint_banner"),
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12.5,
                  height: 1.35,
                ),
              ),
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
                key: const Key("euclidean_canvas"),
                painter: _EuclideanPainter(
                  preset: _preset,
                  showAuxiliary: _showAuxiliary,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _EuclideanPainter extends CustomPainter {
  final EuclideanShapePreset preset;
  final bool showAuxiliary;

  _EuclideanPainter({
    required this.preset,
    required this.showAuxiliary,
  });

  @override
  void paint(Canvas canvas, Size size) {
    switch (preset) {
      case EuclideanShapePreset.isosceles:
        _paintIsosceles(canvas, size);
        break;
      case EuclideanShapePreset.rightTriangle:
        _paintRightTriangle(canvas, size);
        break;
      case EuclideanShapePreset.trapezoid:
        _paintTrapezoid(canvas, size);
        break;
      case EuclideanShapePreset.circleTangent:
        _paintCircleTangent(canvas, size);
        break;
    }
  }

  void _paintIsosceles(Canvas canvas, Size size) {
    final top = Offset(size.width / 2.0, size.height * 0.18);
    final left = Offset(size.width * 0.18, size.height * 0.82);
    final right = Offset(size.width * 0.82, size.height * 0.82);
    final midBase = Offset((left.dx + right.dx) / 2.0, left.dy);

    final fillPaint = Paint()
      ..color = Colors.cyan.withValues(alpha: 0.1)
      ..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..color = Colors.cyanAccent
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final path = Path()
      ..moveTo(top.dx, top.dy)
      ..lineTo(left.dx, left.dy)
      ..lineTo(right.dx, right.dy)
      ..close();

    canvas.drawPath(path, fillPaint);
    canvas.drawPath(path, strokePaint);

    // Equal side tick marks
    _drawTick(canvas, Offset((top.dx + left.dx) / 2.0, (top.dy + left.dy) / 2.0), Colors.white70);
    _drawTick(canvas, Offset((top.dx + right.dx) / 2.0, (top.dy + right.dy) / 2.0), Colors.white70);

    // Auxiliary Altitude
    if (showAuxiliary) {
      final auxPaint = Paint()
        ..color = Colors.amberAccent
        ..strokeWidth = 2.0
        ..style = PaintingStyle.stroke;
      _drawDashedLine(canvas, top, midBase, auxPaint);
      _drawRightAngleMarker(canvas, midBase, true);
    }
  }

  void _paintRightTriangle(Canvas canvas, Size size) {
    final vertexA = Offset(size.width * 0.22, size.height * 0.22); // 90° vertex
    final vertexB = Offset(size.width * 0.22, size.height * 0.80);
    final vertexC = Offset(size.width * 0.82, size.height * 0.80);
    final midHyp = Offset((vertexA.dx + vertexC.dx) / 2.0, (vertexA.dy + vertexC.dy) / 2.0);

    final path = Path()
      ..moveTo(vertexA.dx, vertexA.dy)
      ..lineTo(vertexB.dx, vertexB.dy)
      ..lineTo(vertexC.dx, vertexC.dy)
      ..close();

    final fillPaint = Paint()
      ..color = Colors.indigo.withValues(alpha: 0.15)
      ..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..color = Colors.lightBlueAccent
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    canvas.drawPath(path, fillPaint);
    canvas.drawPath(path, strokePaint);
    _drawRightAngleMarker(canvas, vertexB, false);

    // Auxiliary Median to Hypotenuse (Muhteşem Üçlü)
    if (showAuxiliary) {
      final auxPaint = Paint()
        ..color = Colors.amberAccent
        ..strokeWidth = 2.0;
      _drawDashedLine(canvas, vertexB, midHyp, auxPaint);
      // Mark midHyp
      canvas.drawCircle(midHyp, 4.0, Paint()..color = Colors.amberAccent);
    }
  }

  void _paintTrapezoid(Canvas canvas, Size size) {
    final topLeft = Offset(size.width * 0.35, size.height * 0.25);
    final topRight = Offset(size.width * 0.65, size.height * 0.25);
    final bottomLeft = Offset(size.width * 0.15, size.height * 0.80);
    final bottomRight = Offset(size.width * 0.85, size.height * 0.80);

    final path = Path()
      ..moveTo(topLeft.dx, topLeft.dy)
      ..lineTo(topRight.dx, topRight.dy)
      ..lineTo(bottomRight.dx, bottomRight.dy)
      ..lineTo(bottomLeft.dx, bottomLeft.dy)
      ..close();

    final fillPaint = Paint()
      ..color = Colors.teal.withValues(alpha: 0.12)
      ..style = PaintingStyle.fill;
    final strokePaint = Paint()
      ..color = Colors.tealAccent
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    canvas.drawPath(path, fillPaint);
    canvas.drawPath(path, strokePaint);

    // Auxiliary Parallel Line from topRight to bottom
    if (showAuxiliary) {
      final parallelBottom = Offset(
        topRight.dx - (topLeft.dx - bottomLeft.dx),
        bottomRight.dy,
      );
      final auxPaint = Paint()
        ..color = Colors.amberAccent
        ..strokeWidth = 2.0;
      _drawDashedLine(canvas, topRight, parallelBottom, auxPaint);
    }
  }

  void _paintCircleTangent(Canvas canvas, Size size) {
    final center = Offset(size.width * 0.45, size.height * 0.45);
    const double radius = 70.0;
    final tangentPoint = Offset(center.dx, center.dy + radius);

    // Circle
    final circlePaint = Paint()
      ..color = Colors.purpleAccent.withValues(alpha: 0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    canvas.drawCircle(center, radius, circlePaint);
    canvas.drawCircle(center, 4.0, Paint()..color = Colors.purpleAccent);

    // Tangent horizontal line
    final tangentLinePaint = Paint()
      ..color = Colors.greenAccent
      ..strokeWidth = 2.0;
    canvas.drawLine(
      Offset(tangentPoint.dx - 120, tangentPoint.dy),
      Offset(tangentPoint.dx + 120, tangentPoint.dy),
      tangentLinePaint,
    );

    canvas.drawCircle(tangentPoint, 5.0, Paint()..color = Colors.greenAccent);

    // Auxiliary Radius connecting center to tangent point
    if (showAuxiliary) {
      final auxPaint = Paint()
        ..color = Colors.amberAccent
        ..strokeWidth = 2.0;
      _drawDashedLine(canvas, center, tangentPoint, auxPaint);
      _drawRightAngleMarker(canvas, tangentPoint, true);
    }
  }

  void _drawDashedLine(Canvas canvas, Offset p1, Offset p2, Paint paint) {
    const double dashWidth = 5.0;
    const double dashSpace = 4.0;
    final double dx = p2.dx - p1.dx;
    final double dy = p2.dy - p1.dy;
    final double distance = math.sqrt(dx * dx + dy * dy);
    if (distance <= 0.0 || !distance.isFinite) return;
    final double unitX = dx / distance;
    final double unitY = dy / distance;

    double currentDist = 0.0;
    while (currentDist < distance) {
      final double endDist = math.min(currentDist + dashWidth, distance);
      canvas.drawLine(
        Offset(p1.dx + unitX * currentDist, p1.dy + unitY * currentDist),
        Offset(p1.dx + unitX * endDist, p1.dy + unitY * endDist),
        paint,
      );
      currentDist += dashWidth + dashSpace;
    }
  }

  void _drawTick(Canvas canvas, Offset point, Color color) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2.0;
    canvas.drawLine(
      Offset(point.dx - 4, point.dy - 4),
      Offset(point.dx + 4, point.dy + 4),
      paint,
    );
  }

  void _drawRightAngleMarker(Canvas canvas, Offset corner, bool vertical) {
    final paint = Paint()
      ..color = Colors.amberAccent
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;
    const double size = 10.0;
    final path = Path();
    if (vertical) {
      path.moveTo(corner.dx - size, corner.dy);
      path.lineTo(corner.dx - size, corner.dy - size);
      path.lineTo(corner.dx, corner.dy - size);
    } else {
      path.moveTo(corner.dx + size, corner.dy);
      path.lineTo(corner.dx + size, corner.dy - size);
      path.lineTo(corner.dx, corner.dy - size);
    }
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _EuclideanPainter oldDelegate) {
    return oldDelegate.preset != preset || oldDelegate.showAuxiliary != showAuxiliary;
  }
}
