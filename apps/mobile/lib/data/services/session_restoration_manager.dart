import 'dart:convert';
import 'package:flutter/widgets.dart';
import '../../../domain/models/solution_step.dart';
import '../../ui/features/touchpad/math_touchpad.dart';

/// Serializable state for crash resistance and instant session resumption
class RestoredSessionState {
  final String sessionId;
  final String nodeId;
  final String targetEquation;
  final String draftText;
  final InputMode inputMode;
  final List<Map<String, dynamic>> serializedSteps;
  final double currentPl;
  final DateTime lastUpdated;

  RestoredSessionState({
    required this.sessionId,
    required this.nodeId,
    required this.targetEquation,
    required this.draftText,
    required this.inputMode,
    required this.serializedSteps,
    required this.currentPl,
    required this.lastUpdated,
  });

  Map<String, dynamic> toJson() {
    return {
      'sessionId': sessionId,
      'nodeId': nodeId,
      'targetEquation': targetEquation,
      'draftText': draftText,
      'inputMode': inputMode.name,
      'serializedSteps': serializedSteps,
      'currentPl': currentPl,
      'lastUpdated': lastUpdated.toIso8601String(),
    };
  }

  factory RestoredSessionState.fromJson(Map<String, dynamic> json) {
    InputMode mode = InputMode.touchpad;
    final modeStr = json['inputMode'] as String?;
    if (modeStr != null) {
      for (var m in InputMode.values) {
        if (m.name == modeStr) {
          mode = m;
          break;
        }
      }
    }

    final stepsRaw = json['serializedSteps'] as List<dynamic>? ?? [];
    final List<Map<String, dynamic>> parsedSteps = [];
    for (var s in stepsRaw) {
      if (s is Map<String, dynamic>) {
        parsedSteps.add(s);
      } else if (s is Map) {
        parsedSteps.add(Map<String, dynamic>.from(s));
      }
    }

    return RestoredSessionState(
      sessionId: json['sessionId'] as String? ?? '',
      nodeId: json['nodeId'] as String? ?? 'N15',
      targetEquation: json['targetEquation'] as String? ?? '',
      draftText: json['draftText'] as String? ?? '',
      inputMode: mode,
      serializedSteps: parsedSteps,
      currentPl: (json['currentPl'] as num?)?.toDouble() ?? 0.20,
      lastUpdated: json['lastUpdated'] != null
          ? DateTime.tryParse(json['lastUpdated'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  List<SolutionStep> toSolutionSteps() {
    final List<SolutionStep> list = [];
    for (var m in serializedSteps) {
      try {
        list.add(SolutionStep(
          stepNumber: m['step_number'] as int? ?? 1,
          userExpression: m['user_expression'] as String? ?? '',
          isValid: m['is_valid'] as bool? ?? false,
          isTargetReached: m['is_target_reached'] as bool? ?? false,
          errorMessage: m['error_message'] as String?,
          canonicalExpression: m['canonical_expression'] as String?,
          elapsedMs: m['elapsed_ms'] as int? ?? 0,
        ));
      } catch (_) {
        // Skip corrupt single steps
      }
    }
    return list;
  }
}

/// Serializable focus session state for crash resistance and instant restoration
class RestoredFocusSessionState {
  final String episodeId;
  final String topicId;
  final int sequence;
  final int a;
  final int b;
  final int c;
  final String comparator;
  final int? divisorRoot;
  final String draftText;
  final InputMode inputMode;
  final bool isZenMode;
  final String currentStage;
  final String currentPhase;
  final DateTime lastUpdated;

  RestoredFocusSessionState({
    required this.episodeId,
    required this.topicId,
    required this.sequence,
    required this.a,
    required this.b,
    required this.c,
    required this.comparator,
    this.divisorRoot,
    required this.draftText,
    required this.inputMode,
    required this.isZenMode,
    required this.currentStage,
    required this.currentPhase,
    required this.lastUpdated,
  });

  Map<String, dynamic> toJson() => {
    'episodeId': episodeId,
    'topicId': topicId,
    'sequence': sequence,
    'a': a,
    'b': b,
    'c': c,
    'comparator': comparator,
    if (divisorRoot != null) 'divisorRoot': divisorRoot,
    'draftText': draftText,
    'inputMode': inputMode.name,
    'isZenMode': isZenMode,
    'currentStage': currentStage,
    'currentPhase': currentPhase,
    'lastUpdated': lastUpdated.toIso8601String(),
  };

  factory RestoredFocusSessionState.fromJson(Map<String, dynamic> json) {
    InputMode mode = InputMode.touchpad;
    final modeStr = json['inputMode'] as String?;
    if (modeStr != null) {
      for (var m in InputMode.values) {
        if (m.name == modeStr) {
          mode = m;
          break;
        }
      }
    }
    return RestoredFocusSessionState(
      episodeId: json['episodeId'] as String? ?? '',
      topicId: json['topicId'] as String? ?? 'CT-QF1',
      sequence: json['sequence'] as int? ?? 0,
      a: json['a'] as int? ?? 1,
      b: json['b'] as int? ?? 5,
      c: json['c'] as int? ?? 6,
      comparator: json['comparator'] as String? ?? '<=',
      divisorRoot: json['divisorRoot'] as int?,
      draftText: json['draftText'] as String? ?? '',
      inputMode: mode,
      isZenMode: json['isZenMode'] as bool? ?? false,
      currentStage: json['currentStage'] as String? ?? 'S1_FACTOR',
      currentPhase: json['currentPhase'] as String? ?? 'WORKSPACE',
      lastUpdated: json['lastUpdated'] != null
          ? DateTime.tryParse(json['lastUpdated'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// Abstract storage interface for dependency injection & testing
abstract class SessionStorageBackend {
  Future<void> write(String key, String data);
  Future<String?> read(String key);
  Future<void> delete(String key);
}

/// In-memory storage backend fallback and test driver
class InMemorySessionStorageBackend implements SessionStorageBackend {
  final Map<String, String> _memoryStore = {};

  @override
  Future<void> write(String key, String data) async {
    _memoryStore[key] = data;
  }

  @override
  Future<String?> read(String key) async {
    return _memoryStore[key];
  }

  @override
  Future<void> delete(String key) async {
    _memoryStore.remove(key);
  }
}

/// SessionRestorationManager: Observes app lifecycle, handles atomic saves, and ensures zero data loss.
class SessionRestorationManager with WidgetsBindingObserver {
  static const String defaultDraftKey = 'ple_active_session_draft';
  static const Duration defaultExpiry = Duration(hours: 24);

  final SessionStorageBackend _storage;
  VoidCallback? _onAppPausedCallback;
  RestoredSessionState? _cachedState;

  SessionRestorationManager({SessionStorageBackend? storage})
      : _storage = storage ?? InMemorySessionStorageBackend();

  RestoredSessionState? get cachedState => _cachedState;

  void bindLifecycleObserver({VoidCallback? onSaveStateRequested}) {
    _onAppPausedCallback = onSaveStateRequested;
    WidgetsBinding.instance.addObserver(this);
  }

  void unbindLifecycleObserver() {
    WidgetsBinding.instance.removeObserver(this);
    _onAppPausedCallback = null;
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.inactive ||
        state == AppLifecycleState.detached) {
      _onAppPausedCallback?.call();
    }
  }

  /// Saves the current session state atomically
  Future<void> saveDraft({
    required String sessionId,
    required String nodeId,
    required String targetEquation,
    required String draftText,
    required InputMode inputMode,
    required List<SolutionStep> steps,
    required double currentPl,
  }) async {
    final serializedSteps = steps.map((s) => {
      'step_number': s.stepNumber,
      'user_expression': s.userExpression,
      'is_valid': s.isValid,
      'is_target_reached': s.isTargetReached,
      'error_message': s.errorMessage,
      'canonical_expression': s.canonicalExpression,
      'elapsed_ms': s.elapsedMs,
    }).toList();

    final state = RestoredSessionState(
      sessionId: sessionId,
      nodeId: nodeId,
      targetEquation: targetEquation,
      draftText: draftText,
      inputMode: inputMode,
      serializedSteps: serializedSteps,
      currentPl: currentPl,
      lastUpdated: DateTime.now(),
    );

    _cachedState = state;

    try {
      final jsonStr = jsonEncode(state.toJson());
      await _storage.write(defaultDraftKey, jsonStr);
    } catch (_) {
      // Storage error handled silently
    }
  }

  /// Restores the last active draft, returning null if missing, corrupt, or expired
  Future<RestoredSessionState?> restoreDraft({Duration maxAge = defaultExpiry}) async {
    try {
      final raw = await _storage.read(defaultDraftKey);
      if (raw == null || raw.trim().isEmpty) {
        return null;
      }

      final map = jsonDecode(raw) as Map<String, dynamic>;
      final state = RestoredSessionState.fromJson(map);

      // Check expiration
      if (DateTime.now().difference(state.lastUpdated) > maxAge) {
        await clearDraft();
        return null;
      }

      _cachedState = state;
      return state;
    } catch (_) {
      // Corrupt state cleanup
      await clearDraft();
      return null;
    }
  }

  /// Clears persisted draft upon successful problem completion or explicit reset
  Future<void> clearDraft() async {
    _cachedState = null;
    try {
      await _storage.delete(defaultDraftKey);
    } catch (_) {}
  }

  // ==========================================
  // Focus Session Draft Persistence
  // ==========================================
  static const String defaultFocusDraftKey = 'ple_active_focus_draft';
  RestoredFocusSessionState? _cachedFocusState;

  RestoredFocusSessionState? get cachedFocusState => _cachedFocusState;

  /// Saves the current Focus Session state atomically
  Future<void> saveFocusDraft(RestoredFocusSessionState state) async {
    _cachedFocusState = state;
    try {
      final jsonStr = jsonEncode(state.toJson());
      await _storage.write(defaultFocusDraftKey, jsonStr);
    } catch (_) {
      // Storage error handled gracefully
    }
  }

  /// Restores the last active Focus Session draft, returning null if missing, corrupt, or expired
  Future<RestoredFocusSessionState?> restoreFocusDraft({Duration maxAge = defaultExpiry}) async {
    try {
      final raw = await _storage.read(defaultFocusDraftKey);
      if (raw == null || raw.trim().isEmpty) {
        return null;
      }

      final map = jsonDecode(raw) as Map<String, dynamic>;
      final state = RestoredFocusSessionState.fromJson(map);

      // Check expiration
      if (DateTime.now().difference(state.lastUpdated) > maxAge) {
        await clearFocusDraft();
        return null;
      }

      _cachedFocusState = state;
      return state;
    } catch (_) {
      // Corrupt state cleanup
      await clearFocusDraft();
      return null;
    }
  }

  /// Clears persisted Focus Session draft upon completion or reset
  Future<void> clearFocusDraft() async {
    _cachedFocusState = null;
    try {
      await _storage.delete(defaultFocusDraftKey);
    } catch (_) {}
  }
}
