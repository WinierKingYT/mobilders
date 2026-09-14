import 'package:flutter/material.dart';

class DrawingStroke {
  final List<Offset> points;
  final Color color;
  final double strokeWidth;

  DrawingStroke({
    required this.points,
    required this.color,
    required this.strokeWidth,
  });
}

class ScratchpadPainter extends CustomPainter {
  final List<DrawingStroke> strokes;
  final DrawingStroke? currentStroke;

  ScratchpadPainter({
    required this.strokes,
    this.currentStroke,
  });

  @override
  void paint(Canvas canvas, Size size) {
    for (final stroke in strokes) {
      _drawStroke(canvas, stroke);
    }
    if (currentStroke != null) {
      _drawStroke(canvas, currentStroke!);
    }
  }

  void _drawStroke(Canvas canvas, DrawingStroke stroke) {
    if (stroke.points.isEmpty) return;

    final paint = Paint()
      ..color = stroke.color
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..strokeWidth = stroke.strokeWidth
      ..style = PaintingStyle.stroke;

    if (stroke.points.length == 1) {
      canvas.drawCircle(stroke.points.first, stroke.strokeWidth / 2, paint);
      return;
    }

    final path = Path();
    path.moveTo(stroke.points.first.dx, stroke.points.first.dy);
    for (int i = 1; i < stroke.points.length; i++) {
      path.lineTo(stroke.points[i].dx, stroke.points[i].dy);
    }
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant ScratchpadPainter oldDelegate) => true;
}

class ScratchpadOverlay extends StatefulWidget {
  final VoidCallback onClose;

  const ScratchpadOverlay({
    super.key,
    required this.onClose,
  });

  @override
  State<ScratchpadOverlay> createState() => _ScratchpadOverlayState();
}

class _ScratchpadOverlayState extends State<ScratchpadOverlay> {
  final List<DrawingStroke> _strokes = [];
  DrawingStroke? _currentStroke;
  Color _selectedColor = const Color(0xFFF8FAFC);
  double _strokeWidth = 3.0;

  final List<Color> _palette = const [
    Color(0xFFF8FAFC), // White/Slate
    Color(0xFF38BDF8), // Sky Blue
    Color(0xFF10B981), // Emerald Green
    Color(0xFFF59E0B), // Amber
    Color(0xFFF43F5E), // Rose
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xF0090D16), // Deep Dark Transparent Overlay
      child: SafeArea(
        child: Column(
          children: [
            // Header Controls
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Color(0xFF1E293B))),
              ),
              child: Row(
                children: [
                  const Icon(Icons.gesture, color: Color(0xFF38BDF8), size: 20),
                  const SizedBox(width: 8),
                  const Text(
                    "Serbest Karalama (Scratchpad)",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Spacer(),
                  // Undo
                  IconButton(
                    icon: const Icon(Icons.undo, color: Color(0xFF94A3B8), size: 20),
                    tooltip: "Geri Al",
                    onPressed: _strokes.isNotEmpty
                        ? () {
                            setState(() {
                              _strokes.removeLast();
                            });
                          }
                        : null,
                  ),
                  // Clear
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: Color(0xFFF43F5E), size: 20),
                    tooltip: "Temizle",
                    onPressed: _strokes.isNotEmpty
                        ? () {
                            setState(() {
                              _strokes.clear();
                            });
                          }
                        : null,
                  ),
                  // Close
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white, size: 22),
                    tooltip: "Kapat",
                    onPressed: widget.onClose,
                  ),
                ],
              ),
            ),

            // Drawing Area
            Expanded(
              child: GestureDetector(
                onPanStart: (details) {
                  setState(() {
                    _currentStroke = DrawingStroke(
                      points: [details.localPosition],
                      color: _selectedColor,
                      strokeWidth: _strokeWidth,
                    );
                  });
                },
                onPanUpdate: (details) {
                  setState(() {
                    _currentStroke?.points.add(details.localPosition);
                  });
                },
                onPanEnd: (details) {
                  setState(() {
                    if (_currentStroke != null) {
                      _strokes.add(_currentStroke!);
                      _currentStroke = null;
                    }
                  });
                },
                child: CustomPaint(
                  painter: ScratchpadPainter(
                    strokes: _strokes,
                    currentStroke: _currentStroke,
                  ),
                  size: Size.infinite,
                ),
              ),
            ),

            // Color Palette Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: const BoxDecoration(
                color: Color(0xFF0F172A),
                border: Border(top: BorderSide(color: Color(0xFF1E293B))),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ..._palette.map((color) {
                    final isSelected = color == _selectedColor;
                    return GestureDetector(
                      onTap: () => setState(() => _selectedColor = color),
                      child: Container(
                        margin: const EdgeInsets.symmetric(horizontal: 8),
                        width: 26,
                        height: 26,
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: isSelected ? Colors.white : Colors.transparent,
                            width: 2.5,
                          ),
                          boxShadow: isSelected
                              ? [
                                  BoxShadow(
                                    color: color.withValues(alpha: 0.5),
                                    blurRadius: 8,
                                    spreadRadius: 2,
                                  ),
                                ]
                              : null,
                        ),
                      ),
                    );
                  }),
                  const SizedBox(width: 16),
                  // Stroke width toggle
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        _strokeWidth = _strokeWidth == 3.0 ? 6.0 : 3.0;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        _strokeWidth == 3.0 ? "İnce" : "Kalın",
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
