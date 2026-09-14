import 'package:flutter/material.dart';

/// Dyscalculia Visual Aid: Concrete Spatial Number Line with directional step displacements.
class VisualNumberLine extends StatelessWidget {
  final double currentPosition;
  final double? targetPosition;
  final double minRange;
  final double maxRange;

  const VisualNumberLine({
    super.key,
    required this.currentPosition,
    this.targetPosition,
    this.minRange = -10.0,
    this.maxRange = 10.0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.linear_scale, color: Color(0xFF38BDF8), size: 16),
              const SizedBox(width: 6),
              const Text(
                "Görsel Sayı Çizgisi (Diskalkuli Desteği)",
                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11, fontWeight: FontWeight.w600),
              ),
              const Spacer(),
              Text(
                "Konum: ${currentPosition.toInt()}",
                style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Expanded(
            child: CustomPaint(
              painter: _NumberLinePainter(
                currentPos: currentPosition,
                targetPos: targetPosition,
                minRange: minRange,
                maxRange: maxRange,
              ),
              size: Size.infinite,
            ),
          ),
        ],
      ),
    );
  }
}

class _NumberLinePainter extends CustomPainter {
  final double currentPos;
  final double? targetPos;
  final double minRange;
  final double maxRange;

  _NumberLinePainter({
    required this.currentPos,
    this.targetPos,
    required this.minRange,
    required this.maxRange,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final axisPaint = Paint()
      ..color = const Color(0xFF64748B)
      ..strokeWidth = 2.0;

    final yCenter = size.height / 2.0;
    canvas.drawLine(Offset(0, yCenter), Offset(size.width, yCenter), axisPaint);

    final rangeSpan = maxRange - minRange;
    final tickCount = (rangeSpan).toInt();

    for (int i = 0; i <= tickCount; i += 2) {
      final val = minRange + i;
      final x = (i / rangeSpan) * size.width;

      final isZero = val == 0;
      final tickHeight = isZero ? 12.0 : 6.0;

      final tickPaint = Paint()
        ..color = isZero ? const Color(0xFFF8FAFC) : const Color(0xFF475569)
        ..strokeWidth = isZero ? 2.5 : 1.5;

      canvas.drawLine(Offset(x, yCenter - tickHeight / 2), Offset(x, yCenter + tickHeight / 2), tickPaint);
    }

    // Draw active student marker
    final normX = ((currentPos - minRange) / rangeSpan).clamp(0.0, 1.0) * size.width;
    final markerPaint = Paint()
      ..color = const Color(0xFF10B981) // Emerald highlight
      ..style = PaintingStyle.fill;

    canvas.drawCircle(Offset(normX, yCenter), 6.0, markerPaint);

    // If target position is present, draw directional leap arc
    if (targetPos != null) {
      final targetX = ((targetPos! - minRange) / rangeSpan).clamp(0.0, 1.0) * size.width;
      final leapPaint = Paint()
        ..color = (targetPos! >= currentPos) ? const Color(0xFF10B981) : const Color(0xFFF43F5E)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;

      final path = Path();
      path.moveTo(normX, yCenter - 6);
      path.quadraticBezierTo((normX + targetX) / 2.0, yCenter - 22, targetX, yCenter - 6);
      canvas.drawPath(path, leapPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _NumberLinePainter oldDelegate) => true;
}

/// Dyscalculia Visual Aid: Color-coded semantic algebraic terms.
/// Minimizes numerical grouping confusion by distinguishing coefficients, variables, and signs.
class ColorCodedAlgebraicExpression extends StatelessWidget {
  final String expression;

  const ColorCodedAlgebraicExpression({
    super.key,
    required this.expression,
  });

  @override
  Widget build(BuildContext context) {
    // Simple tokenizer for quadratic elements
    final tokens = expression.split(' ');

    return Wrap(
      spacing: 4,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: tokens.map((tok) {
        Color badgeColor = const Color(0xFFF8FAFC);
        Color bgColor = Colors.transparent;

        if (tok.contains('x^2') || tok.contains('x²')) {
          badgeColor = const Color(0xFF38BDF8); // Sky Blue for quadratic terms
          bgColor = const Color(0xFF0C4A6E).withValues(alpha: 0.4);
        } else if (tok.contains('x')) {
          badgeColor = const Color(0xFFF59E0B); // Amber for linear terms
          bgColor = const Color(0xFF78350F).withValues(alpha: 0.4);
        } else if (double.tryParse(tok) != null) {
          badgeColor = const Color(0xFF10B981); // Emerald for constants
          bgColor = const Color(0xFF064E3B).withValues(alpha: 0.4);
        } else if (tok == '+' || tok == '-') {
          badgeColor = (tok == '+') ? const Color(0xFF34D399) : const Color(0xFFF87171);
        } else if (tok == '=') {
          badgeColor = const Color(0xFFA855F7); // Purple for equality
        }

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            tok,
            style: TextStyle(
              color: badgeColor,
              fontSize: 18,
              fontWeight: FontWeight.bold,
              fontFamily: 'monospace',
            ),
          ),
        );
      }).toList(),
    );
  }
}
