import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'engine_api_service.dart';

/// Single offline solution step event awaiting idempotent server synchronization.
/// Compliant with 23-OFFLINE-STATE-AND-SYNC-SPECIFICATION.md
class UnsyncedStepEvent {
  final String clientMsgId;
  final String sessionId;
  final String nodeId;
  final int stepNumber;
  final String userExpression;
  final String targetEquation;
  final String? previousStep;
  final DateTime clientTimestamp;
  final int elapsedMs;
  final double currentPl;
  int retryCount;
  bool isSynced;
  String? syncError;

  UnsyncedStepEvent({
    required this.clientMsgId,
    required this.sessionId,
    required this.nodeId,
    required this.stepNumber,
    required this.userExpression,
    required this.targetEquation,
    this.previousStep,
    required this.clientTimestamp,
    this.elapsedMs = 0,
    this.currentPl = 0.20,
    this.retryCount = 0,
    this.isSynced = false,
    this.syncError,
  });

  Map<String, dynamic> toJson() => {
    'client_msg_id': clientMsgId,
    'session_id': sessionId,
    'node_id': nodeId,
    'step_number': stepNumber,
    'user_expression': userExpression,
    'target_equation': targetEquation,
    if (previousStep != null) 'previous_step': previousStep,
    'client_timestamp': clientTimestamp.toIso8601String(),
    'elapsed_ms': elapsedMs,
    'current_p_l': currentPl,
    'retry_count': retryCount,
    'is_synced': isSynced,
    if (syncError != null) 'sync_error': syncError,
  };

  factory UnsyncedStepEvent.fromJson(Map<String, dynamic> json) => UnsyncedStepEvent(
    clientMsgId: json['client_msg_id'] as String,
    sessionId: json['session_id'] as String,
    nodeId: json['node_id'] as String? ?? 'N15',
    stepNumber: json['step_number'] as int? ?? 1,
    userExpression: json['user_expression'] as String,
    targetEquation: json['target_equation'] as String,
    previousStep: json['previous_step'] as String?,
    clientTimestamp: DateTime.tryParse(json['client_timestamp'] as String? ?? '') ?? DateTime.now(),
    elapsedMs: json['elapsed_ms'] as int? ?? 0,
    currentPl: (json['current_p_l'] as num?)?.toDouble() ?? 0.20,
    retryCount: json['retry_count'] as int? ?? 0,
    isSynced: json['is_synced'] as bool? ?? false,
    syncError: json['sync_error'] as String?,
  );
}

/// Offline Focus Attempt event awaiting idempotent server synchronization.
class UnsyncedFocusAttemptEvent {
  final String clientMsgId;
  final String episodeId;
  final int expectedSequence;
  final String rawAttempt;
  final String inputKind;
  final DateTime clientTimestamp;
  int retryCount;
  bool isSynced;
  String? syncError;

  UnsyncedFocusAttemptEvent({
    required this.clientMsgId,
    required this.episodeId,
    required this.expectedSequence,
    required this.rawAttempt,
    this.inputKind = 'equation_rewrite',
    required this.clientTimestamp,
    this.retryCount = 0,
    this.isSynced = false,
    this.syncError,
  });

  Map<String, dynamic> toJson() => {
    'client_msg_id': clientMsgId,
    'episode_id': episodeId,
    'expected_sequence': expectedSequence,
    'raw_attempt': rawAttempt,
    'input_kind': inputKind,
    'client_timestamp': clientTimestamp.toIso8601String(),
    'retry_count': retryCount,
    'is_synced': isSynced,
    if (syncError != null) 'sync_error': syncError,
  };

  factory UnsyncedFocusAttemptEvent.fromJson(Map<String, dynamic> json) =>
      UnsyncedFocusAttemptEvent(
        clientMsgId: json['client_msg_id'] as String,
        episodeId: json['episode_id'] as String,
        expectedSequence: json['expected_sequence'] as int? ?? 0,
        rawAttempt: json['raw_attempt'] as String,
        inputKind: json['input_kind'] as String? ?? 'equation_rewrite',
        clientTimestamp: DateTime.tryParse(json['client_timestamp'] as String? ?? '') ?? DateTime.now(),
        retryCount: json['retry_count'] as int? ?? 0,
        isSynced: json['is_synced'] as bool? ?? false,
        syncError: json['sync_error'] as String?,
      );
}

/// Result of a batch replay containing synced count and updated step models.
class BatchReplayResult {
  final int syncedCount;
  final List<Map<String, dynamic>> replayedSteps;
  final double? latestPl;
  final bool isTargetReached;

  BatchReplayResult({
    required this.syncedCount,
    this.replayedSteps = const [],
    this.latestPl,
    this.isTargetReached = false,
  });
}

/// Offline Event Queue Manager.
/// Stores unsynced steps locally, provides client-timestamp ordering,
/// exponential backoff retry calculations, and idempotent batch replay.
class OfflineSyncQueue extends ChangeNotifier {
  static const int maxQueueSize = 500;

  final List<UnsyncedStepEvent> _events = [];
  final List<UnsyncedFocusAttemptEvent> _focusEvents = [];
  final String? storageFilePath;
  bool _isSyncing = false;
  BatchReplayResult? _lastReplayResult;

  OfflineSyncQueue({this.storageFilePath}) {
    _loadFromDisk();
  }

  List<UnsyncedStepEvent> get pendingEvents =>
      List.unmodifiable(_events.where((e) => !e.isSynced).toList());

  int get pendingCount => _events.where((e) => !e.isSynced).length;
  bool get isSyncing => _isSyncing;
  BatchReplayResult? get lastReplayResult => _lastReplayResult;

  List<UnsyncedFocusAttemptEvent> get pendingFocusEvents =>
      List.unmodifiable(_focusEvents.where((e) => !e.isSynced).toList());

  int get pendingFocusCount => _focusEvents.where((e) => !e.isSynced).length;

  /// Explicitly loads stored events from disk (useful in async setup or tests).
  Future<void> load() async {
    await _loadFromDisk();
    notifyListeners();
  }

  /// Enqueue step to local storage and memory ledger.
  void enqueueStep(UnsyncedStepEvent event) {
    if (_events.length >= maxQueueSize) {
      _events.removeAt(0);
    }
    _events.add(event);
    _persistToDisk();
    notifyListeners();
  }

  /// Enqueue a focus attempt for offline synchronization.
  void enqueueFocusAttempt(UnsyncedFocusAttemptEvent event) {
    if (_focusEvents.length >= maxQueueSize) {
      _focusEvents.removeAt(0);
    }
    _focusEvents.add(event);
    _persistToDisk();
    notifyListeners();
  }

  /// Mark a focus attempt as synced and remove from pending queue.
  void markFocusAttemptSynced(String clientMsgId) {
    _focusEvents.removeWhere((e) => e.clientMsgId == clientMsgId);
    _persistToDisk();
    notifyListeners();
  }

  /// Calculate exponential backoff interval in seconds: 2s -> 4s -> 8s -> max 30s.
  static int calculateBackoffSeconds(int retryCount) {
    if (retryCount <= 0) return 2;
    if (retryCount >= 10) return 30; // Prevent pow(2, retryCount) numeric overflow
    return min(30, 2 * pow(2, retryCount).toInt());
  }

  /// Calculates exponential backoff with full jitter to avoid the Thundering Herd problem.
  /// Generates a randomized backoff interval in [0, calculateBackoffSeconds(retryCount)].
  static double calculateBackoffWithJitter(int retryCount, {Random? random}) {
    final baseSeconds = calculateBackoffSeconds(retryCount);
    final rng = random ?? Random();
    return rng.nextDouble() * baseSeconds;
  }

  /// Replays pending events against the EngineApiService and returns full batch details.
  Future<BatchReplayResult> replayBatch(EngineApiService apiService) async {
    final pending = _events.where((e) => !e.isSynced).toList();
    if (pending.isEmpty || _isSyncing) {
      return BatchReplayResult(syncedCount: 0);
    }

    _isSyncing = true;
    notifyListeners();

    // Sort chronologically by client-timestamp (CRDT requirement)
    pending.sort((a, b) => a.clientTimestamp.compareTo(b.clientTimestamp));

    int syncedCount = 0;
    List<Map<String, dynamic>> replayedSteps = [];
    double? latestPl;
    bool isTargetReached = false;

    try {
      final payloadEvents = pending.map((e) => e.toJson()).toList();
      final sessionId = pending.first.sessionId;

      final res = await apiService.replayOfflineBatch(
        sessionId: sessionId,
        events: payloadEvents,
      );

      final returnedSynced = res['synced_count'] as int? ?? 0;
      latestPl = (res['latest_p_l'] as num?)?.toDouble();
      isTargetReached = res['is_target_reached'] as bool? ?? false;

      final rawSteps = res['replayed_steps'] as List<dynamic>?;
      if (rawSteps != null) {
        replayedSteps = rawSteps
            .whereType<Map<String, dynamic>>()
            .toList();
      }

      if (returnedSynced > 0) {
        for (int i = 0; i < min(returnedSynced, pending.length); i++) {
          pending[i].isSynced = true;
        }
        syncedCount = returnedSynced;
        _events.removeWhere((e) => e.isSynced);
        await _persistToDisk();
      }
    } catch (err) {
      // Network still offline or error occurred; record retry and calculate backoff
      for (final event in pending) {
        event.retryCount += 1;
        event.syncError = err.toString();
      }
      await _persistToDisk();
    } finally {
      _isSyncing = false;
      notifyListeners();
    }

    final result = BatchReplayResult(
      syncedCount: syncedCount,
      replayedSteps: replayedSteps,
      latestPl: latestPl,
      isTargetReached: isTargetReached,
    );
    _lastReplayResult = result;
    return result;
  }

  /// Replays pending events against the EngineApiService in chronological order.
  Future<int> replayQueue(EngineApiService apiService) async {
    final result = await replayBatch(apiService);
    return result.syncedCount;
  }

  Future<void> clearQueue() async {
    _events.clear();
    _focusEvents.clear();
    await _persistToDisk();
    notifyListeners();
  }

  bool _isPersisting = false;
  bool _needsAnotherPersist = false;

  Future<void> _persistToDisk() async {
    if (storageFilePath == null) return;
    if (_isPersisting) {
      _needsAnotherPersist = true;
      return;
    }
    _isPersisting = true;
    try {
      do {
        _needsAnotherPersist = false;
        final file = File(storageFilePath!);
        await file.parent.create(recursive: true);
        final tmpFile = File('${file.path}.tmp');
        final payload = {
          'events': _events.map((e) => e.toJson()).toList(),
          'focus_events': _focusEvents.map((e) => e.toJson()).toList(),
        };
        await tmpFile.writeAsString(jsonEncode(payload), flush: true);
        if (await file.exists()) {
          await file.delete();
        }
        await tmpFile.rename(file.path);
      } while (_needsAnotherPersist);
    } catch (e) {
      debugPrint("OfflineSyncQueue persist warning: $e");
    } finally {
      _isPersisting = false;
    }
  }

  Future<void>? _loadFuture;

  Future<void> _loadFromDisk() async {
    if (storageFilePath == null) return;
    if (_loadFuture != null) return _loadFuture!;
    final completer = Completer<void>();
    _loadFuture = completer.future;
    try {
      final file = File(storageFilePath!);
      final tmpFile = File('${file.path}.tmp');
      File fileToRead = file;

      if (!await file.exists() && await tmpFile.exists()) {
        try {
          await tmpFile.rename(file.path);
          fileToRead = file;
        } catch (_) {
          fileToRead = tmpFile;
        }
      }

      if (await fileToRead.exists()) {
        final content = await fileToRead.readAsString();
        if (content.isNotEmpty) {
          try {
            final decoded = jsonDecode(content);
            _events.clear();
            _focusEvents.clear();
            if (decoded is List) {
              // Backwards compatibility with flat list of steps
              for (final item in decoded) {
                _events.add(UnsyncedStepEvent.fromJson(item as Map<String, dynamic>));
              }
            } else if (decoded is Map<String, dynamic>) {
              if (decoded['events'] is List) {
                for (final item in decoded['events']) {
                  _events.add(UnsyncedStepEvent.fromJson(item as Map<String, dynamic>));
                }
              }
              if (decoded['focus_events'] is List) {
                for (final item in decoded['focus_events']) {
                  _focusEvents.add(
                    UnsyncedFocusAttemptEvent.fromJson(item as Map<String, dynamic>),
                  );
                }
              }
            }
          } on FormatException catch (fe) {
            debugPrint("OfflineSyncQueue corrupt JSON detected: $fe");
            try {
              final bakFile = File('${file.path}.corrupt.bak');
              await bakFile.writeAsString(content, flush: true);
            } catch (_) {}
            _events.clear();
            _focusEvents.clear();
          }
        }
      }
    } catch (e) {
      debugPrint("OfflineSyncQueue load warning: $e");
    } finally {
      completer.complete();
      _loadFuture = null;
    }
  }
}
