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

  static const int maxHistoryLength = 100;

  bool isEnabled = true;

  /// Hardware actuator protection: minimum duration (ms) between consecutive haptic pulses.
  /// Throttling prevents tactile saturation, coil heating, and battery drain on high-frequency tapping.
  int throttleIntervalMs = 40;
  DateTime? _lastTriggerTime;
  int throttledCount = 0;

  /// Hook for unit and widget testing to verify triggers without hardware.
  void Function(HapticType type)? testListener;
  final List<HapticType> triggeredHistory = [];

  Future<void> keyPress({bool force = false}) async {
    await _trigger(HapticType.lightImpact, HapticFeedback.lightImpact, bypassThrottling: force);
  }

  Future<void> stepSuccess({bool force = false}) async {
    await _trigger(HapticType.mediumImpact, () async {
      await HapticFeedback.mediumImpact();
    }, bypassThrottling: force);
  }

  Future<void> stepError({bool force = true}) async {
    // Critical errors bypass throttling by default to ensure urgent feedback to student
    await _trigger(HapticType.heavyImpact, HapticFeedback.heavyImpact, bypassThrottling: force);
  }

  Future<void> selectionClick({bool force = false}) async {
    await _trigger(HapticType.selectionClick, HapticFeedback.selectionClick, bypassThrottling: force);
  }

  Future<void> modeSwitch({bool force = false}) async {
    await _trigger(HapticType.mediumImpact, HapticFeedback.mediumImpact, bypassThrottling: force);
  }

  Future<void> clearAction({bool force = false}) async {
    await _trigger(HapticType.heavyImpact, HapticFeedback.heavyImpact, bypassThrottling: force);
  }

  Future<void> lightImpact({bool force = false}) async {
    await _trigger(HapticType.lightImpact, HapticFeedback.lightImpact, bypassThrottling: force);
  }

  Future<void> mediumImpact({bool force = false}) async {
    await _trigger(HapticType.mediumImpact, HapticFeedback.mediumImpact, bypassThrottling: force);
  }

  Future<void> heavyImpact({bool force = false}) async {
    await _trigger(HapticType.heavyImpact, HapticFeedback.heavyImpact, bypassThrottling: force);
  }

  Future<void> _trigger(
    HapticType type,
    Future<void> Function() hapticCall, {
    bool bypassThrottling = false,
  }) async {
    if (!isEnabled) return;

    final now = DateTime.now();
    if (!bypassThrottling && throttleIntervalMs > 0 && _lastTriggerTime != null) {
      final elapsedMs = now.difference(_lastTriggerTime!).inMilliseconds;
      if (elapsedMs < throttleIntervalMs) {
        throttledCount++;
        return; // Throttled to protect hardware and avoid tactile fatigue
      }
    }

    _lastTriggerTime = now;
    triggeredHistory.add(type);
    if (triggeredHistory.length > maxHistoryLength) {
      triggeredHistory.removeAt(0);
    }
    testListener?.call(type);
    try {
      await hapticCall();
    } catch (_) {
      // Gracefully ignore on unsupported devices or test environments
    }
  }

  void clearHistory() {
    triggeredHistory.clear();
    throttledCount = 0;
    _lastTriggerTime = null;
  }
}
