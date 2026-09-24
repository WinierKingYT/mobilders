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
              const Expanded(
                child: Text(
                  "Görsel Sayı Çizgisi (Diskalkuli Desteği)",
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11, fontWeight: FontWeight.w600),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 6),
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
              letterSpacing: 1.2,
              fontFamily: 'monospace',
            ),
          ),
        );
      }).toList(),
    );
  }
}

/// Place-value color constants engineered specifically for dyscalculic learners
/// to reduce perceptual crowding and visual grouping fatigue.
class DyscalculiaPlaceValueColors {
  static const Color thousands = Color(0xFFA855F7); // Purple (Binler)
  static const Color hundreds = Color(0xFF38BDF8);  // Cyan/Sky Blue (Yüzler)
  static const Color tens = Color(0xFFF59E0B);      // Amber/Turuncu (Onlar)
  static const Color units = Color(0xFF10B981);     // Emerald/Yeşil (Birler)
  static const Color decimal = Color(0xFFEC4899);   // Pink (Ondalık)

  /// Returns distinct color according to digit index from right (0-indexed: 0=units, 1=tens, 2=hundreds, 3=thousands)
  static Color getColorForDigit(int digitIndexFromRight) {
    switch (digitIndexFromRight % 4) {
      case 0:
        return units;
      case 1:
        return tens;
      case 2:
        return hundreds;
      case 3:
        return thousands;
      default:
        return units;
    }
  }
}

/// Dyscalculia Number Formatter & Display Widget
/// Applies distinct place-value colors to each digit and enforces letter-spacing: 1.2
/// to eliminate digit inversion, crowding, and dyslexic number swapping.
class DyscalculiaNumberView extends StatelessWidget {
  final String numberString;
  final double fontSize;
  final bool enablePlaceValueColoring;

  const DyscalculiaNumberView({
    super.key,
    required this.numberString,
    this.fontSize = 22.0,
    this.enablePlaceValueColoring = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!enablePlaceValueColoring) {
      return Text(
        numberString,
        style: TextStyle(
          fontSize: fontSize,
          letterSpacing: 1.2,
          fontFamily: 'monospace',
          fontWeight: FontWeight.bold,
          color: const Color(0xFFF8FAFC),
        ),
      );
    }

    final chars = numberString.split('');
    final digitsOnly = chars.where((c) => RegExp(r'[0-9]').hasMatch(c)).toList();
    int digitIdx = digitsOnly.length - 1;

    final spans = <TextSpan>[];
    for (int i = 0; i < chars.length; i++) {
      final ch = chars[i];
      if (RegExp(r'[0-9]').hasMatch(ch)) {
        final color = DyscalculiaPlaceValueColors.getColorForDigit(digitIdx);
        spans.add(TextSpan(
          text: ch,
          style: TextStyle(
            color: color,
            fontSize: fontSize,
            letterSpacing: 1.2,
            fontFamily: 'monospace',
            fontWeight: FontWeight.bold,
          ),
        ));
        digitIdx--;
      } else {
        spans.add(TextSpan(
          text: ch,
          style: TextStyle(
            color: const Color(0xFF94A3B8),
            fontSize: fontSize,
            letterSpacing: 1.2,
            fontFamily: 'monospace',
            fontWeight: FontWeight.bold,
          ),
        ));
      }
    }

    return RichText(
      text: TextSpan(children: spans),
    );
  }
}
