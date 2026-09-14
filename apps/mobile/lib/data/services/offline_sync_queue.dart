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

/// Offline Event Queue Manager.
/// Stores unsynced steps locally, provides client-timestamp ordering,
/// exponential backoff retry calculations, and idempotent batch replay.
class OfflineSyncQueue extends ChangeNotifier {
  final List<UnsyncedStepEvent> _events = [];
  final String? storageFilePath;
  bool _isSyncing = false;

  OfflineSyncQueue({this.storageFilePath}) {
    _loadFromDisk();
  }

  List<UnsyncedStepEvent> get pendingEvents =>
      List.unmodifiable(_events.where((e) => !e.isSynced).toList());

  int get pendingCount => _events.where((e) => !e.isSynced).length;
  bool get isSyncing => _isSyncing;

  /// Enqueue step to local storage and memory ledger.
  void enqueueStep(UnsyncedStepEvent event) {
    _events.add(event);
    _persistToDisk();
    notifyListeners();
  }

  /// Calculate exponential backoff interval in seconds: 2s -> 4s -> 8s -> max 30s.
  static int calculateBackoffSeconds(int retryCount) {
    if (retryCount <= 0) return 2;
    return min(30, 2 * pow(2, retryCount).toInt());
  }

  /// Replays pending events against the EngineApiService in chronological order.
  Future<int> replayQueue(EngineApiService apiService) async {
    final pending = _events.where((e) => !e.isSynced).toList();
    if (pending.isEmpty || _isSyncing) return 0;

    _isSyncing = true;
    notifyListeners();

    // Sort chronologically by client-timestamp (CRDT requirement)
    pending.sort((a, b) => a.clientTimestamp.compareTo(b.clientTimestamp));

    int syncedCount = 0;
    try {
      final payloadEvents = pending.map((e) => e.toJson()).toList();
      final sessionId = pending.first.sessionId;

      final res = await apiService.replayOfflineBatch(
        sessionId: sessionId,
        events: payloadEvents,
      );

      final returnedSynced = res['synced_count'] as int? ?? 0;
      if (returnedSynced > 0) {
        for (int i = 0; i < min(returnedSynced, pending.length); i++) {
          pending[i].isSynced = true;
        }
        syncedCount = returnedSynced;
        _events.removeWhere((e) => e.isSynced);
        _persistToDisk();
      }
    } catch (err) {
      // Network still offline or error occurred; record retry and calculate backoff
      for (final event in pending) {
        event.retryCount += 1;
        event.syncError = err.toString();
      }
      _persistToDisk();
    } finally {
      _isSyncing = false;
      notifyListeners();
    }

    return syncedCount;
  }

  void clearQueue() {
    _events.clear();
    _persistToDisk();
    notifyListeners();
  }

  void _persistToDisk() {
    if (storageFilePath == null) return;
    try {
      final file = File(storageFilePath!);
      final data = _events.map((e) => e.toJson()).toList();
      file.writeAsStringSync(jsonEncode(data), flush: true);
    } catch (e) {
      debugPrint("OfflineSyncQueue persist warning: $e");
    }
  }

  void _loadFromDisk() {
    if (storageFilePath == null) return;
    try {
      final file = File(storageFilePath!);
      if (file.existsSync()) {
        final content = file.readAsStringSync();
        if (content.isNotEmpty) {
          final list = jsonDecode(content) as List<dynamic>;
          _events.clear();
          for (final item in list) {
            _events.add(UnsyncedStepEvent.fromJson(item as Map<String, dynamic>));
          }
        }
      }
    } catch (e) {
      debugPrint("OfflineSyncQueue load warning: $e");
    }
  }
}
