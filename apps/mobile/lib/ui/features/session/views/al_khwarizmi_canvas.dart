import 'dart:ui' show lerpDouble;
import 'package:flutter/material.dart';

class AlKhwarizmiPainter extends CustomPainter {
  final double bCoefficient;
  final bool isCompleted;
  final double splitProgress;
  final double cornerProgress;

  AlKhwarizmiPainter({
    required this.bCoefficient,
    required this.isCompleted,
    this.splitProgress = 1.0,
    this.cornerProgress = 0.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (size.width <= 0 || size.height <= 0) return;
    final center = Offset(size.width / 2, size.height / 2 - 10);
    const xSize = 130.0;
    final safeB = AlKhwarizmiCanvas.clampB(bCoefficient);
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

    _drawText(canvas, "${(safeB / 2).toStringAsFixed(1)}x", rightRect.center, 12, Colors.white);

    // 3. Draw Bottom (b/2)*x Rectangle (lerped with splitProgress)
    final bottomTargetLeft = xSquareLeft;
    final bottomTargetTop = xSquareTop + xSize + 4;
    final currentBottomLeft = Offset.lerp(
      Offset(xSquareLeft + xSize + 4, xSquareTop + xSize / 2),
      Offset(bottomTargetLeft, bottomTargetTop),
      splitProgress,
    )!;
    final currentBottomW = lerpDouble(bHalf, xSize, splitProgress)!;
    final currentBottomH = lerpDouble(xSize / 2, bHalf, splitProgress)!;

    final bottomRect = Rect.fromLTWH(currentBottomLeft.dx, currentBottomLeft.dy, currentBottomW, currentBottomH);
    canvas.drawRRect(RRect.fromRectAndRadius(bottomRect, const Radius.circular(6)), rectPaint);
    canvas.drawRRect(RRect.fromRectAndRadius(bottomRect, const Radius.circular(6)), borderPaint);

    _drawText(canvas, "${(safeB / 2).toStringAsFixed(1)}x", bottomRect.center, 12, Colors.white);

    // 4. Draw Missing Corner (b/2)^2
    final cornerRect = Rect.fromLTWH(xSquareLeft + xSize + 4, xSquareTop + xSize + 4, bHalf, bHalf);
    if (cornerProgress > 0.05 || isCompleted) {
      final double alpha = isCompleted ? (cornerProgress > 0 ? cornerProgress : 1.0) : cornerProgress;
      final cornerPaint = Paint()
        ..color = const Color(0xFFD97706).withValues(alpha: alpha.clamp(0.0, 1.0)) // Amber Completed
        ..style = PaintingStyle.fill;
      canvas.drawRRect(RRect.fromRectAndRadius(cornerRect, const Radius.circular(6)), cornerPaint);
      _drawText(canvas, "+${((safeB / 2) * (safeB / 2)).toStringAsFixed(1)}", cornerRect.center, 12, Colors.white);
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
    return oldDelegate.bCoefficient != bCoefficient ||
        oldDelegate.isCompleted != isCompleted ||
        oldDelegate.splitProgress != splitProgress ||
        oldDelegate.cornerProgress != cornerProgress;
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

  /// Katsayı sınırlandırma (1.0 <= b <= 20.0) ve bilişsel koruma
  static double clampB(double b) {
    if (!b.isFinite) return 6.0;
    if (b < 1.0) return 2.0; // Negatif veya 0 durumunda pedagojik taban
    if (b > 20.0) return 20.0;
    return b;
  }

  /// Bilişsel aşırı yüklenme veya negatif katsayı durumunda açıklama mesajı
  static String? getClampingWarning(double b) {
    if (b < 1.0) {
      return "Negatif veya sıfır katsayılar geometrik alanda uzunluk olamaz; bilişsel modelleme için b = 2.0 taban değeri uygulandı.";
    }
    if (b > 20.0) {
      return "Bilişsel aşırı yüklenmeyi önlemek için b katsayısı azami 20 ile sınırlandırılmıştır.";
    }
    return null;
  }

  @override
  State<AlKhwarizmiCanvas> createState() => _AlKhwarizmiCanvasState();
}

class _AlKhwarizmiCanvasState extends State<AlKhwarizmiCanvas>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _cornerAnimation;
  bool _isCompleted = false;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _cornerAnimation = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOut,
    );
  }

  @override
  void didUpdateWidget(covariant AlKhwarizmiCanvas oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.bCoefficient != widget.bCoefficient) {
      setState(() {
        _isCompleted = false;
        _animController.reset();
      });
    }
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  void _toggleCompletion() {
    setState(() {
      _isCompleted = !_isCompleted;
      if (_isCompleted) {
        _animController.forward(from: 0.0);
      } else {
        _animController.reverse();
      }
    });
    widget.onCompleteToggled?.call();
  }

  @override
  Widget build(BuildContext context) {
    final warningMsg = AlKhwarizmiCanvas.getClampingWarning(widget.bCoefficient);
    final safeB = AlKhwarizmiCanvas.clampB(widget.bCoefficient);
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
              const Expanded(
                child: Text(
                  "El-Harezmi Geometrik Alan Karoları",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              // Toggle Completion Button
              TextButton.icon(
                onPressed: _toggleCompletion,
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

          // Clamping Warning Banner (if b < 1.0 or b > 20.0)
          if (warningMsg != null)
            Container(
              key: const Key('alkhwarizmi_clamping_warning'),
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFFF59E0B).withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFF59E0B).withValues(alpha: 0.4)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, color: Color(0xFFF59E0B), size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      warningMsg,
                      style: const TextStyle(color: Color(0xFFFCD34D), fontSize: 11),
                    ),
                  ),
                ],
              ),
            ),

          // Canvas View with 60fps Animation
          SizedBox(
            height: 220,
            child: AnimatedBuilder(
              animation: _animController,
              builder: (context, child) {
                final double cornerVal = _isCompleted
                    ? (_animController.isAnimating ? _cornerAnimation.value : 1.0)
                    : (_animController.isAnimating ? _cornerAnimation.value : 0.0);

                return CustomPaint(
                  painter: AlKhwarizmiPainter(
                    bCoefficient: safeB,
                    isCompleted: _isCompleted,
                    splitProgress: 1.0,
                    cornerProgress: cornerVal,
                  ),
                  size: Size.infinite,
                );
              },
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
                Expanded(
                  child: Text(
                    _isCompleted
                        ? "Alan: (x + ${bHalf.toStringAsFixed(0)})² = x² + ${safeB.toStringAsFixed(0)}x + ${bSquared.toStringAsFixed(0)}"
                        : "Mevcut: x² + ${safeB.toStringAsFixed(0)}x  (Kareyi tamamlamak için +${bSquared.toStringAsFixed(0)} ekle)",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: _isCompleted ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8),
                      fontSize: 13,
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Pedagogik Vurgu: Denklemin her iki tarafına (b/2)² ilave edilmesi
          if (_isCompleted)
            Container(
              key: const Key('alkhwarizmi_balance_note'),
              margin: const EdgeInsets.only(top: 10),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFF10B981).withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.4)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.balance, color: Color(0xFF10B981), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      "Pedagojik Vurgu: Denklemin dengesini korumak için eşitliğin her iki tarafına da (b/2)² = +${bSquared.toStringAsFixed(0)} ilave edilir: x² + ${safeB.toStringAsFixed(0)}x + ${bSquared.toStringAsFixed(0)} = c + ${bSquared.toStringAsFixed(0)}",
                      style: const TextStyle(
                        color: Color(0xFF6EE7B7),
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
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
