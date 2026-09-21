import 'package:flutter/material.dart';

/// ADHD / Anxiety-Free Flexible Rhythm Micro-Break Pacer.
/// Replaces anxiety-inducing ticking countdowns with a breathing rhythm
/// and non-punitive micro-rest suggestions.
class FlexibleRhythmPacer extends StatefulWidget {
  final VoidCallback? onMicroBreakTriggered;

  const FlexibleRhythmPacer({
    super.key,
    this.onMicroBreakTriggered,
  });

  @override
  State<FlexibleRhythmPacer> createState() => _FlexibleRhythmPacerState();
}

class _FlexibleRhythmPacerState extends State<FlexibleRhythmPacer>
    with SingleTickerProviderStateMixin {
  late AnimationController _breathingController;
  late Animation<double> _breathingAnimation;

  @override
  void initState() {
    super.initState();
    _breathingController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat(reverse: true);

    _breathingAnimation = Tween<double>(begin: 0.85, end: 1.15).animate(
      CurvedAnimation(parent: _breathingController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _breathingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF1E293B)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          ScaleTransition(
            scale: _breathingAnimation,
            child: Container(
              width: 10,
              height: 10,
              decoration: const BoxDecoration(
                color: Color(0xFF38BDF8), // Calming sky blue
                shape: BoxShape.circle,
              ),
            ),
          ),
          const SizedBox(width: 8),
          const Text(
            "Doğal Ritim",
            style: TextStyle(
              color: Color(0xFF94A3B8),
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
