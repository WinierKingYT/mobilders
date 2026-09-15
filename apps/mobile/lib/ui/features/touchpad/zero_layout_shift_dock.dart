import 'package:flutter/material.dart';
import '../../core/app_theme.dart';
import '../../../core/services/haptic_feedback_service.dart';
import 'math_touchpad.dart';

class ZeroLayoutShiftDock extends StatelessWidget {
  final InputMode currentMode;
  final ValueChanged<InputMode> onModeChanged;
  final Widget child;
  final double dockHeight;
  final VoidCallback? onToggleZenMode;
  final bool isZenModeActive;

  const ZeroLayoutShiftDock({
    super.key,
    required this.currentMode,
    required this.onModeChanged,
    required this.child,
    this.dockHeight = 310.0,
    this.onToggleZenMode,
    this.isZenModeActive = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: dockHeight,
      decoration: BoxDecoration(
        color: AppColors.bgSurface,
        border: Border(
          top: BorderSide(
            color: isZenModeActive
                ? const Color(0xFF38BDF8).withValues(alpha: 0.4)
                : AppColors.bgCard,
            width: 1.5,
          ),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.max,
        children: [
          // Tactical Mode Switcher Ribbon (Zero Layout Shift header)
          _buildModeRibbon(context),
          const Divider(height: 1, color: AppColors.bgCard),
          // Fluid Animated Container with Spring Curve
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 260),
              switchInCurve: const Cubic(0.175, 0.885, 0.32, 1.25), // Spring easeOutBack curve
              switchOutCurve: Curves.easeInQuad,
              transitionBuilder: (Widget widgetChild, Animation<double> animation) {
                return FadeTransition(
                  opacity: animation,
                  child: SlideTransition(
                    position: Tween<Offset>(
                      begin: const Offset(0.0, 0.04),
                      end: Offset.zero,
                    ).animate(animation),
                    child: widgetChild,
                  ),
                );
              },
              child: KeyedSubtree(
                key: ValueKey<InputMode>(currentMode),
                child: child,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModeRibbon(BuildContext context) {
    return Container(
      height: 38,
      padding: const EdgeInsets.symmetric(horizontal: 10),
      color: AppColors.bgPrimary.withValues(alpha: 0.6),
      child: Row(
        children: [
          _modePill(
            label: 'Touchpad',
            icon: Icons.grid_view_rounded,
            mode: InputMode.touchpad,
          ),
          const SizedBox(width: 6),
          _modePill(
            label: 'Klavye',
            icon: Icons.keyboard_outlined,
            mode: InputMode.virtualKeyboard,
          ),
          const SizedBox(width: 6),
          _modePill(
            label: 'El Yazısı',
            icon: Icons.draw_rounded,
            mode: InputMode.inkingCanvas,
          ),
          const Spacer(),
          if (onToggleZenMode != null)
            InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () {
                HapticFeedbackService().modeSwitch();
                onToggleZenMode!();
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: isZenModeActive
                      ? const Color(0xFF38BDF8).withValues(alpha: 0.25)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: isZenModeActive
                        ? const Color(0xFF38BDF8)
                        : AppColors.textMuted.withValues(alpha: 0.3),
                    width: 1,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.self_improvement_rounded,
                      size: 14,
                      color: isZenModeActive ? const Color(0xFF38BDF8) : AppColors.textMuted,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Zen',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: isZenModeActive ? const Color(0xFF38BDF8) : AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _modePill({
    required String label,
    required IconData icon,
    required InputMode mode,
  }) {
    final bool isSelected = currentMode == mode;

    return InkWell(
      borderRadius: BorderRadius.circular(6),
      onTap: () {
        if (!isSelected) {
          HapticFeedbackService().selectionClick();
          onModeChanged(mode);
        }
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.accentPrimary.withValues(alpha: 0.2) : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(
            color: isSelected ? AppColors.accentPrimary : Colors.transparent,
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 14,
              color: isSelected ? AppColors.accentPrimary : AppColors.textMuted,
            ),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? Colors.white : AppColors.textMuted,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
