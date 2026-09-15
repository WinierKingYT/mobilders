import 'package:flutter/services.dart';

enum HapticType {
  lightImpact,
  mediumImpact,
  heavyImpact,
  selectionClick,
  vibrate,
}

class HapticFeedbackService {
  static final HapticFeedbackService _instance = HapticFeedbackService._internal();
  factory HapticFeedbackService() => _instance;
  HapticFeedbackService._internal();

  bool isEnabled = true;

  /// Hook for unit and widget testing to verify triggers without hardware.
  void Function(HapticType type)? testListener;
  final List<HapticType> triggeredHistory = [];

  Future<void> keyPress() async {
    await _trigger(HapticType.lightImpact, HapticFeedback.lightImpact);
  }

  Future<void> stepSuccess() async {
    await _trigger(HapticType.mediumImpact, () async {
      await HapticFeedback.mediumImpact();
    });
  }

  Future<void> stepError() async {
    await _trigger(HapticType.heavyImpact, HapticFeedback.heavyImpact);
  }

  Future<void> selectionClick() async {
    await _trigger(HapticType.selectionClick, HapticFeedback.selectionClick);
  }

  Future<void> modeSwitch() async {
    await _trigger(HapticType.mediumImpact, HapticFeedback.mediumImpact);
  }

  Future<void> clearAction() async {
    await _trigger(HapticType.heavyImpact, HapticFeedback.heavyImpact);
  }

  Future<void> _trigger(HapticType type, Future<void> Function() hapticCall) async {
    if (!isEnabled) return;
    triggeredHistory.add(type);
    testListener?.call(type);
    try {
      await hapticCall();
    } catch (_) {
      // Gracefully ignore on unsupported devices or test environments
    }
  }

  void clearHistory() {
    triggeredHistory.clear();
  }
}
