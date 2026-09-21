import 'package:flutter/material.dart';
import '../../../../core/services/haptic_feedback_service.dart';

/// Cognitive Hesitation Whisper Bubble (Bölüm 1 - Bilişsel Öğretim Manifestosu)
/// Appears when student pauses for 8-10 seconds without typing.
/// Delivers a warm, non-condescending 1-sentence prompt to unblock cognitive deadlock.
class HesitationWhisperBubble extends StatelessWidget {
  final String whisperMessage;
  final VoidCallback? onDismiss;
  final VoidCallback? onTapAction;

  const HesitationWhisperBubble({
    super.key,
    required this.whisperMessage,
    this.onDismiss,
    this.onTapAction,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeOutCubic,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1B4B).withValues(alpha: 0.90), // Deep Indigo Tint
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: const Color(0xFF818CF8).withValues(alpha: 0.6), // Light Indigo border
          width: 1.5,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6366F1).withValues(alpha: 0.18),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: const Color(0xFF6366F1).withValues(alpha: 0.25),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.psychology_alt_rounded,
              color: Color(0xFFA5B4FC),
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: InkWell(
              onTap: () {
                HapticFeedbackService().selectionClick();
                onTapAction?.call();
              },
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text(
                  whisperMessage,
                  key: const Key('hesitation_whisper_text'),
                  style: const TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFFE0E7FF),
                    height: 1.35,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 6),
          IconButton(
            key: const Key('hesitation_whisper_dismiss'),
            icon: const Icon(Icons.close_rounded, size: 18, color: Color(0xFF94A3B8)),
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
            tooltip: 'İpucunu kapat',
            onPressed: () {
              HapticFeedbackService().selectionClick();
              onDismiss?.call();
            },
          ),
        ],
      ),
    );
  }
}
