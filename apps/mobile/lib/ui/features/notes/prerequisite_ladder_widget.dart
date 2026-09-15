import 'package:flutter/material.dart';
import '../../../core/services/haptic_feedback_service.dart';
import '../../core/app_theme.dart';

class PrerequisiteStepItem {
  final String nodeId;
  final String title;
  final int level;

  const PrerequisiteStepItem({
    required this.nodeId,
    required this.title,
    this.level = 0,
  });
}

/// Prerequisite Ladder Widget (Bölüm 3 - Geriye Doğru Zincirlenmiş Yaşayan Ders Notları)
/// Renders a clickable, visual prerequisite chain leading from root concepts up to active node.
class PrerequisiteLadderWidget extends StatelessWidget {
  final List<PrerequisiteStepItem> chain;
  final String activeNodeId;
  final ValueChanged<String>? onSelectNode;

  const PrerequisiteLadderWidget({
    super.key,
    required this.chain,
    required this.activeNodeId,
    this.onSelectNode,
  });

  @override
  Widget build(BuildContext context) {
    if (chain.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      key: const Key('prerequisite_ladder'),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF38BDF8).withValues(alpha: 0.3),
          width: 1.0,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.stairs_rounded, size: 16, color: Color(0xFF38BDF8)),
              SizedBox(width: 8),
              Text(
                'Önkoşul Merdiveni',
                style: TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF38BDF8),
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: List.generate(chain.length, (index) {
                final item = chain[index];
                final isActive = item.nodeId == activeNodeId;
                final isLast = index == chain.length - 1;

                return Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    InkWell(
                      key: Key('ladder_step_${item.nodeId}'),
                      borderRadius: BorderRadius.circular(8),
                      onTap: () {
                        HapticFeedbackService().selectionClick();
                        onSelectNode?.call(item.nodeId);
                      },
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: isActive
                              ? const Color(0xFF6366F1).withValues(alpha: 0.3)
                              : const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: isActive
                                ? const Color(0xFF818CF8)
                                : const Color(0xFF334155),
                            width: isActive ? 1.5 : 1.0,
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              item.nodeId,
                              style: TextStyle(
                                fontSize: 10.5,
                                fontWeight: FontWeight.bold,
                                color: isActive ? const Color(0xFF38BDF8) : AppColors.textMuted,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              item.title,
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
                                color: isActive ? Colors.white : AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    if (!isLast)
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 6),
                        child: Icon(
                          Icons.arrow_forward_rounded,
                          size: 14,
                          color: Color(0xFF64748B),
                        ),
                      ),
                  ],
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}
