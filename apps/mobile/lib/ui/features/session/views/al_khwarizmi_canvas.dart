import 'package:flutter/material.dart';

class AlKhwarizmiPainter extends CustomPainter {
  final double bCoefficient;
  final bool isCompleted;

  AlKhwarizmiPainter({
    required this.bCoefficient,
    required this.isCompleted,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (size.width <= 0 || size.height <= 0) return;
    final center = Offset(size.width / 2, size.height / 2 - 10);
    const xSize = 130.0;
    final safeB = (bCoefficient.isNaN || bCoefficient.isInfinite) ? 6.0 : bCoefficient;
    final bHalf = (safeB / 2.0).abs() * 22.0; // Visual scaling

    final xSquareLeft = center.dx - (xSize + bHalf) / 2;
    final xSquareTop = center.dy - (xSize + bHalf) / 2;

    // 1. Draw x^2 Square
    final xSquareRect = Rect.fromLTWH(xSquareLeft, xSquareTop, xSize, xSize);
    final xSquarePaint = Paint()
      ..color = const Color(0xFF2563EB).withValues(alpha: 0.85) // Blue
      ..style = PaintingStyle.fill;
    canvas.drawRRect(RRect.fromRectAndRadius(xSquareRect, const Radius.circular(6)), xSquarePaint);

    final borderPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;
    canvas.drawRRect(RRect.fromRectAndRadius(xSquareRect, const Radius.circular(6)), borderPaint);

    _drawText(canvas, "x²", Offset(xSquareRect.center.dx, xSquareRect.center.dy), 18, Colors.white);

    // 2. Draw Right (b/2)*x Rectangle
    final rightRect = Rect.fromLTWH(xSquareLeft + xSize + 4, xSquareTop, bHalf, xSize);
    final rectPaint = Paint()
      ..color = const Color(0xFF059669).withValues(alpha: 0.85) // Emerald
      ..style = PaintingStyle.fill;
    canvas.drawRRect(RRect.fromRectAndRadius(rightRect, const Radius.circular(6)), rectPaint);
    canvas.drawRRect(RRect.fromRectAndRadius(rightRect, const Radius.circular(6)), borderPaint);

    _drawText(canvas, "${(safeB/2).toStringAsFixed(1)}x", rightRect.center, 12, Colors.white);

    // 3. Draw Bottom (b/2)*x Rectangle
    final bottomRect = Rect.fromLTWH(xSquareLeft, xSquareTop + xSize + 4, xSize, bHalf);
    canvas.drawRRect(RRect.fromRectAndRadius(bottomRect, const Radius.circular(6)), rectPaint);
    canvas.drawRRect(RRect.fromRectAndRadius(bottomRect, const Radius.circular(6)), borderPaint);

    _drawText(canvas, "${(safeB/2).toStringAsFixed(1)}x", bottomRect.center, 12, Colors.white);

    // 4. Draw Missing Corner (b/2)^2
    final cornerRect = Rect.fromLTWH(xSquareLeft + xSize + 4, xSquareTop + xSize + 4, bHalf, bHalf);
    if (isCompleted) {
      final cornerPaint = Paint()
        ..color = const Color(0xFFD97706) // Amber Completed
        ..style = PaintingStyle.fill;
      canvas.drawRRect(RRect.fromRectAndRadius(cornerRect, const Radius.circular(6)), cornerPaint);
      _drawText(canvas, "+${((safeB/2)*(safeB/2)).toStringAsFixed(1)}", cornerRect.center, 12, Colors.white);
    } else {
      // Dashed Outline for Missing Piece
      final dashedPaint = Paint()
        ..color = const Color(0xFFF59E0B)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;
      canvas.drawRRect(RRect.fromRectAndRadius(cornerRect, const Radius.circular(6)), dashedPaint);
      _drawText(canvas, "?", cornerRect.center, 14, const Color(0xFFF59E0B));
    }
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
  bool shouldRepaint(covariant AlKhwarizmiPainter oldDelegate) {
    return oldDelegate.bCoefficient != bCoefficient || oldDelegate.isCompleted != isCompleted;
  }
}

class AlKhwarizmiCanvas extends StatefulWidget {
  final double bCoefficient;
  final VoidCallback? onCompleteToggled;

  const AlKhwarizmiCanvas({
    super.key,
    this.bCoefficient = 6.0,
    this.onCompleteToggled,
  });

  @override
  State<AlKhwarizmiCanvas> createState() => _AlKhwarizmiCanvasState();
}

class _AlKhwarizmiCanvasState extends State<AlKhwarizmiCanvas> {
  bool _isCompleted = false;

  @override
  void didUpdateWidget(covariant AlKhwarizmiCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.bCoefficient != widget.bCoefficient) {
      setState(() {
        _isCompleted = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final safeB = (widget.bCoefficient.isNaN || widget.bCoefficient.isInfinite) ? 6.0 : widget.bCoefficient;
    final bHalf = safeB / 2.0;
    final bSquared = bHalf * bHalf;

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
              const Icon(Icons.architecture, color: Color(0xFF38BDF8), size: 20),
              const SizedBox(width: 8),
              const Text(
                "El-Harezmi Geometrik Alan Karoları",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Spacer(),
              // Toggle Completion Button
              TextButton.icon(
                onPressed: () {
                  setState(() {
                    _isCompleted = !_isCompleted;
                  });
                  widget.onCompleteToggled?.call();
                },
                icon: Icon(
                  _isCompleted ? Icons.check_circle : Icons.add_circle_outline,
                  color: _isCompleted ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                  size: 16,
                ),
                label: Text(
                  _isCompleted ? "Tam Kare" : "Eksik Parça",
                  style: TextStyle(
                    color: _isCompleted ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Canvas View
          SizedBox(
            height: 220,
            child: CustomPaint(
              painter: AlKhwarizmiPainter(
                bCoefficient: widget.bCoefficient,
                isCompleted: _isCompleted,
              ),
              size: Size.infinite,
            ),
          ),

          const SizedBox(height: 12),

          // Mathematical Dynamic Formula
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  _isCompleted
                      ? "Alan: (x + ${bHalf.toStringAsFixed(0)})² = x² + ${widget.bCoefficient.toStringAsFixed(0)}x + ${bSquared.toStringAsFixed(0)}"
                      : "Mevcut: x² + ${widget.bCoefficient.toStringAsFixed(0)}x  (Kareyi tamamlamak için +${bSquared.toStringAsFixed(0)} ekle)",
                  style: TextStyle(
                    color: _isCompleted ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
                    fontSize: 13,
                    fontFamily: 'monospace',
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
