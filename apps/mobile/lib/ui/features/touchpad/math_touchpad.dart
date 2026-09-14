import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/app_theme.dart';

enum InputMode {
  touchpad,
  virtualKeyboard,
}

class MathTouchpad extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSubmit;
  final InputMode inputMode;
  final ValueChanged<InputMode> onModeChanged;
  final bool isSubmitting;

  const MathTouchpad({
    super.key,
    required this.controller,
    required this.onSubmit,
    required this.inputMode,
    required this.onModeChanged,
    this.isSubmitting = false,
  });

  void _insertText(String text) {
    HapticFeedback.lightImpact();
    final value = controller.value;
    final selection = value.selection;
    final start = selection.start >= 0 ? selection.start : value.text.length;
    final end = selection.end >= 0 ? selection.end : value.text.length;

    final newText = value.text.replaceRange(start, end, text);
    controller.value = TextEditingValue(
      text: newText,
      selection: TextSelection.collapsed(offset: start + text.length),
    );
  }

  void _backspace() {
    HapticFeedback.lightImpact();
    final value = controller.value;
    final selection = value.selection;
    final start = selection.start >= 0 ? selection.start : value.text.length;
    final end = selection.end >= 0 ? selection.end : value.text.length;

    if (start != end) {
      final newText = value.text.replaceRange(start, end, '');
      controller.value = TextEditingValue(
        text: newText,
        selection: TextSelection.collapsed(offset: start),
      );
    } else if (start > 0) {
      // Check if deleting multi-char tokens like "x^2" or "sqrt("
      String toDelete = value.text.substring(0, start);
      int deleteLength = 1;
      if (toDelete.endsWith('sqrt(')) {
        deleteLength = 5;
      } else if (toDelete.endsWith('x^2')) {
        deleteLength = 3;
      } else if (toDelete.endsWith(' = ')) {
        deleteLength = 3;
      }

      final newText = value.text.replaceRange(start - deleteLength, start, '');
      controller.value = TextEditingValue(
        text: newText,
        selection: TextSelection.collapsed(offset: start - deleteLength),
      );
    }
  }

  void _clear() {
    HapticFeedback.mediumImpact();
    controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    if (inputMode == InputMode.virtualKeyboard) {
      return _buildKeyboardMode(context);
    }
    return _buildTouchpadGrid(context);
  }

  Widget _buildKeyboardMode(BuildContext context) {
    return Container(
      color: AppColors.bgSurface,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.grid_view_rounded, color: AppColors.accentPrimary),
                tooltip: 'Matematik Touchpadine Geç',
                onPressed: () => onModeChanged(InputMode.touchpad),
              ),
              Expanded(
                child: TextField(
                  controller: controller,
                  autofocus: true,
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 18,
                    fontFamily: 'monospace',
                  ),
                  decoration: InputDecoration(
                    hintText: 'Cebirsel adımı yazın (örn: 2x + 6 = 10)...',
                    hintStyle: const TextStyle(color: AppColors.textMuted),
                    filled: true,
                    fillColor: AppColors.bgPrimary,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  ),
                  onSubmitted: (_) => onSubmit(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: isSubmitting ? null : onSubmit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.accentPrimary,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                child: isSubmitting
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.arrow_forward_rounded, color: Colors.white),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTouchpadGrid(BuildContext context) {
    return Container(
      color: AppColors.bgSurface,
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Row 1: Math Variables & Functions
          _buildRow([
            _key('x', () => _insertText('x'), flex: 1),
            _key('x²', () => _insertText('x^2'), flex: 1),
            _key('√', () => _insertText('sqrt('), flex: 1),
            _key('±', () => _insertText('+-'), flex: 1),
            _actionKey('C', _clear, color: AppColors.accentError.withOpacity(0.2), textColor: AppColors.accentError),
          ]),
          const SizedBox(height: 6),

          // Row 2: Operators & Equation signs
          _buildRow([
            _key('(', () => _insertText('('), isOp: true),
            _key(')', () => _insertText(')'), isOp: true),
            _key('=', () => _insertText(' = '), isOp: true),
            _key('+', () => _insertText(' + '), isOp: true),
            _key('-', () => _insertText(' - '), isOp: true),
          ]),
          const SizedBox(height: 6),

          // Row 3: Numpad 7, 8, 9, *, /
          _buildRow([
            _key('7', () => _insertText('7')),
            _key('8', () => _insertText('8')),
            _key('9', () => _insertText('9')),
            _key('×', () => _insertText(' * '), isOp: true),
            _key('÷', () => _insertText(' / '), isOp: true),
          ]),
          const SizedBox(height: 6),

          // Row 4: Numpad 4, 5, 6, 0, Backspace
          _buildRow([
            _key('4', () => _insertText('4')),
            _key('5', () => _insertText('5')),
            _key('6', () => _insertText('6')),
            _key('0', () => _insertText('0')),
            _actionKey('⌫', _backspace, icon: Icons.backspace_outlined),
          ]),
          const SizedBox(height: 6),

          // Row 5: Numpad 1, 2, 3, Switch Mode, Submit
          _buildRow([
            _key('1', () => _insertText('1')),
            _key('2', () => _insertText('2')),
            _key('3', () => _insertText('3')),
            _actionKey(
              '⌨',
              () => onModeChanged(InputMode.virtualKeyboard),
              icon: Icons.keyboard_outlined,
              tooltip: 'Serbest Klavyeye Geç',
            ),
            _submitKey(),
          ]),
        ],
      ),
    );
  }

  Widget _buildRow(List<Widget> children) {
    return Row(
      children: children
          .map((child) => Expanded(child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 3),
                child: child,
              )))
          .toList(),
    );
  }

  Widget _key(String label, VoidCallback onPressed, {int flex = 1, bool isOp = false}) {
    return SizedBox(
      height: 48,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: isOp ? AppColors.touchpadOpBg : AppColors.touchpadKeyBg,
          foregroundColor: AppColors.touchpadKeyText,
          elevation: 1,
          padding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: isOp ? 18 : 20,
            fontWeight: FontWeight.w600,
            fontFamily: isOp ? null : 'monospace',
          ),
        ),
      ),
    );
  }

  Widget _actionKey(
    String label,
    VoidCallback onPressed, {
    IconData? icon,
    Color? color,
    Color? textColor,
    String? tooltip,
  }) {
    return SizedBox(
      height: 48,
      child: Tooltip(
        message: tooltip ?? '',
        child: ElevatedButton(
          onPressed: onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: color ?? AppColors.touchpadOpBg,
            foregroundColor: textColor ?? AppColors.touchpadKeyText,
            elevation: 1,
            padding: EdgeInsets.zero,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          ),
          child: icon != null
              ? Icon(icon, size: 20)
              : Text(
                  label,
                  style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                ),
        ),
      ),
    );
  }

  Widget _submitKey() {
    return SizedBox(
      height: 48,
      child: ElevatedButton(
        onPressed: isSubmitting ? null : onSubmit,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.touchpadActionBg,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: EdgeInsets.zero,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        child: isSubmitting
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              )
            : const Icon(Icons.arrow_forward_rounded, size: 22),
      ),
    );
  }
}
