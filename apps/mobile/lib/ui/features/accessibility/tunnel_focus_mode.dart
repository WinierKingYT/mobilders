import 'package:flutter/material.dart';

/// ADHD Accessibility: Tunnel Focus Mode Container.
/// Eliminates visual noise, background sidebars, graphs, and multi-panel distractions
/// down to a single high-contrast (WCAG AAA >= 7:1) cognitive focus tunnel.
class TunnelFocusContainer extends StatelessWidget {
  final bool isTunnelModeEnabled;
  final VoidCallback onToggleTunnelMode;
  final Widget child;
  final String activeGoalText;

  const TunnelFocusContainer({
    super.key,
    required this.isTunnelModeEnabled,
    required this.onToggleTunnelMode,
    required this.child,
    this.activeGoalText = "Şu Anki Hedef: Eşitliğin her iki tarafını sadeleştir",
  });

  @override
  Widget build(BuildContext context) {
    if (!isTunnelModeEnabled) {
      return Column(
        children: [
          // Banner allowing to turn on Tunnel Mode
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            color: const Color(0xFF0F172A),
            child: Row(
              children: [
                const Icon(Icons.center_focus_strong, color: Color(0xFF38BDF8), size: 16),
                const SizedBox(width: 8),
                const Text(
                  "DEHB / Dikkat Odaklama Modu",
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                ),
                const Spacer(),
                TextButton(
                  onPressed: onToggleTunnelMode,
                  child: const Text(
                    "Tünel Görüşünü Aç",
                    style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
          Expanded(child: child),
        ],
      );
    }

    // High Contrast WCAG AAA Pure Black Obsidian Theme
    return Container(
      color: const Color(0xFF050811), // Obsidian Black (#050811)
      child: SafeArea(
        child: Column(
          children: [
            // Focused Minimalist Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Color(0xFF1E293B), width: 1.5)),
              ),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Color(0xFF10B981), // Pulsing focus dot
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      activeGoalText,
                      style: const TextStyle(
                        color: Color(0xFFFFFFFF), // Pure White WCAG AAA (Contrast > 15:1)
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.fullscreen_exit_rounded, color: Color(0xFF94A3B8), size: 22),
                    tooltip: "Tünel Modundan Çık",
                    onPressed: onToggleTunnelMode,
                  ),
                ],
              ),
            ),

            // Isolated Focus Body
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: child,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
