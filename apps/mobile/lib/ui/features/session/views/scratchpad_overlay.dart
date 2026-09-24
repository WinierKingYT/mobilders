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

    final validPoints = stroke.points
        .where((p) => p.dx.isFinite && !p.dx.isNaN && p.dy.isFinite && !p.dy.isNaN)
        .toList();
    if (validPoints.isEmpty) return;

    final paint = Paint()
      ..color = stroke.color
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..strokeWidth = stroke.strokeWidth
      ..style = PaintingStyle.stroke;

    if (validPoints.length == 1) {
      canvas.drawCircle(validPoints.first, stroke.strokeWidth / 2, paint);
      return;
    }

    final path = Path();
    path.moveTo(validPoints.first.dx, validPoints.first.dy);
    for (int i = 1; i < validPoints.length; i++) {
      path.lineTo(validPoints[i].dx, validPoints[i].dy);
    }
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant ScratchpadPainter oldDelegate) => true;
}

class ScratchpadOverlay extends StatefulWidget {
  final VoidCallback onClose;
  final bool initialPassThrough;
  final ValueChanged<bool>? onPassThroughChanged;

  const ScratchpadOverlay({
    super.key,
    required this.onClose,
    this.initialPassThrough = false,
    this.onPassThroughChanged,
  });

  @override
  State<ScratchpadOverlay> createState() => _ScratchpadOverlayState();
}

class _ScratchpadOverlayState extends State<ScratchpadOverlay> {
  static const int maxStrokes = 50; // Azami 50 vuruş sınırlandırması (Ring Buffer)
  static const int maxPointsPerStroke = 2000;

  final List<DrawingStroke> _strokes = [];
  final List<DrawingStroke> _redoStack = [];
  DrawingStroke? _currentStroke;
  Color _selectedColor = const Color(0xFFF8FAFC);
  double _strokeWidth = 3.0;
  late bool _isPassThrough;

  final List<Color> _palette = const [
    Color(0xFFF8FAFC), // White/Slate
    Color(0xFF38BDF8), // Sky Blue
    Color(0xFF10B981), // Emerald Green
    Color(0xFFF59E0B), // Amber
    Color(0xFFF43F5E), // Rose
  ];

  @override
  void initState() {
    super.initState();
    _isPassThrough = widget.initialPassThrough;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: _isPassThrough ? null : const Color(0xF0090D16), // Transparan veya Deep Dark Overlay
      child: SafeArea(
        child: Column(
          children: [
            // Header Controls
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: _isPassThrough ? const Color(0xEE0F172A) : null,
                border: const Border(bottom: BorderSide(color: Color(0xFF1E293B))),
              ),
              child: Row(
                children: [
                  const Icon(Icons.gesture, color: Color(0xFF38BDF8), size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Flexible(
                          child: Text(
                            "Serbest Karalama (Scratchpad)",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (_isPassThrough) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(color: const Color(0xFF10B981)),
                            ),
                            child: const Text(
                              "Geçirgen Mod",
                              style: TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  // Pass-Through (Geçirgen Mod) Toggle
                  IconButton(
                    key: const Key('scratchpad_passthrough_toggle'),
                    icon: Icon(
                      _isPassThrough ? Icons.touch_app : Icons.draw,
                      color: _isPassThrough ? const Color(0xFF10B981) : const Color(0xFF38BDF8),
                      size: 20,
                    ),
                    tooltip: _isPassThrough ? "Çizim Moduna Geç" : "Geçirgen Mod (Alttaki Katmana Dokun)",
                    onPressed: () {
                      setState(() {
                        _isPassThrough = !_isPassThrough;
                        widget.onPassThroughChanged?.call(_isPassThrough);
                      });
                    },
                  ),
                  // Undo
                  IconButton(
                    icon: const Icon(Icons.undo, color: Color(0xFF94A3B8), size: 20),
                    tooltip: "Geri Al",
                    onPressed: _strokes.isNotEmpty
                        ? () {
                            setState(() {
                              _redoStack.add(_strokes.removeLast());
                            });
                          }
                        : null,
                  ),
                  // Redo
                  IconButton(
                    key: const Key('scratchpad_redo_button'),
                    icon: Icon(
                      Icons.redo,
                      color: _redoStack.isNotEmpty ? const Color(0xFF94A3B8) : Colors.white24,
                      size: 20,
                    ),
                    tooltip: "Yinele",
                    onPressed: _redoStack.isNotEmpty
                        ? () {
                            setState(() {
                              if (_strokes.length >= maxStrokes) {
                                _strokes.removeAt(0);
                              }
                              _strokes.add(_redoStack.removeLast());
                            });
                          }
                        : null,
                  ),
                  // Clear
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: Color(0xFFF43F5E), size: 20),
                    tooltip: "Temizle",
                    onPressed: (_strokes.isNotEmpty || _redoStack.isNotEmpty)
                        ? () {
                            setState(() {
                              _strokes.clear();
                              _redoStack.clear();
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
              child: IgnorePointer(
                ignoring: _isPassThrough,
                child: GestureDetector(
                  key: const Key('scratchpad_drawing_area'),
                  behavior: HitTestBehavior.opaque,
                  onPanStart: (details) {
                    final pos = details.localPosition;
                    if (!pos.dx.isFinite || !pos.dy.isFinite) return;
                    setState(() {
                      _currentStroke = DrawingStroke(
                        points: [pos],
                        color: _selectedColor,
                        strokeWidth: _strokeWidth,
                      );
                    });
                  },
                  onPanUpdate: (details) {
                    final pos = details.localPosition;
                    if (!pos.dx.isFinite || !pos.dy.isFinite) return;
                    if ((_currentStroke?.points.length ?? 0) >= maxPointsPerStroke) return;
                    setState(() {
                      _currentStroke?.points.add(pos);
                    });
                  },
                  onPanEnd: (details) {
                    setState(() {
                      if (_currentStroke != null) {
                        if (_strokes.length >= maxStrokes) {
                          _strokes.removeAt(0);
                        }
                        _strokes.add(_currentStroke!);
                        _redoStack.clear();
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
            ),

            // Color Palette Bar (Sadece çizim modunda görünür, geçirgen modda gizlenir)
            if (!_isPassThrough)
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
