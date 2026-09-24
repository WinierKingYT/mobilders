import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import '../../ui/features/vault/mistake_autopsy_view.dart';
import 'engine_api_service.dart';

/// Service managing real cognitive mistakes and misconceptions made by the student.
/// Follows the Zero-Fabrication principle: starts empty, records only actual mistakes.
/// Provides asynchronous local disk persistence and optional API synchronization.
class MistakeVaultService extends ChangeNotifier {
  static final MistakeVaultService _instance = MistakeVaultService._internal();
  factory MistakeVaultService({String? storageFilePath}) {
    if (storageFilePath != null && _instance.storageFilePath != storageFilePath) {
      _instance.storageFilePath = storageFilePath;
      _instance._loadFromDisk();
    }
    return _instance;
  }
  static MistakeVaultService get instance => _instance;

  MistakeVaultService._internal();

  final List<MistakeAutopsyItem> _mistakes = [];
  String? storageFilePath;
  bool _isSyncing = false;

  List<MistakeAutopsyItem> get mistakes => List.unmodifiable(_mistakes);

  bool get isEmpty => _mistakes.isEmpty;
  int get count => _mistakes.length;
  bool get isSyncing => _isSyncing;

  /// Explicitly loads stored mistakes from disk (useful in async setup or tests).
  Future<void> load() async {
    await _loadFromDisk();
    notifyListeners();
  }

  /// Explicitly flushes current mistakes to disk.
  Future<void> saveToDisk() async {
    await _persistToDisk();
  }

  /// Records an actual misconception detected during a session.
  void recordMistake({
    required String bugId,
    required String nodeId,
    required String problem,
    required String offendingStep,
    required String correctPrinciple,
    double initialStabilityDays = 0.5,
  }) {
    // Avoid duplicate open entries for the exact same bug & problem
    final existingIndex = _mistakes.indexWhere(
      (m) => m.bugId == bugId && m.problem == problem && m.status != 'cured',
    );

    if (existingIndex != -1) {
      // Already present in vault as active/open mistake
      return;
    }

    final newMistake = MistakeAutopsyItem(
      id: 'm_${DateTime.now().millisecondsSinceEpoch}_${_mistakes.length + 1}',
      bugId: bugId,
      nodeId: nodeId,
      problem: problem,
      offendingStep: offendingStep,
      correctPrinciple: correctPrinciple,
      status: 'open',
      stabilityDays: initialStabilityDays,
      isDue: true,
    );

    _mistakes.add(newMistake);
    _persistToDisk();
    notifyListeners();
  }

  /// Updates the lifecycle status of a mistake item ('open' -> 'in_remediation' -> 'cured').
  void updateMistakeStatus(String id, String newStatus) {
    final index = _mistakes.indexWhere((m) => m.id == id);
    if (index != -1) {
      final current = _mistakes[index];
      _mistakes[index] = MistakeAutopsyItem(
        id: current.id,
        bugId: current.bugId,
        nodeId: current.nodeId,
        problem: current.problem,
        offendingStep: current.offendingStep,
        correctPrinciple: current.correctPrinciple,
        status: newStatus,
        stabilityDays: newStatus == 'cured' ? current.stabilityDays * 2.5 : current.stabilityDays,
        isDue: newStatus != 'cured',
      );
      _persistToDisk();
      notifyListeners();
    }
  }

  /// Clears all mistakes (e.g. for testing or profile reset).
  void clearMistakes({bool persist = true}) {
    _mistakes.clear();
    if (persist) {
      _persistToDisk();
    }
    notifyListeners();
  }

  /// Synchronizes local vault with backend CognitiveMistakeVault.
  Future<void> syncWithApi(EngineApiService apiService, String userId) async {
    if (_isSyncing) return;
    _isSyncing = true;
    notifyListeners();

    try {
      final remoteList = await apiService.fetchVaultMistakes(userId);
      for (final raw in remoteList) {
        final id = raw['mistake_id'] as String? ?? '';
        final bugId = raw['bug_id'] as String? ?? '';
        final problem = raw['problem_statement'] as String? ?? '';
        final status = raw['status'] as String? ?? 'open';
        final stability = (raw['dsr_state']?['stability'] as num?)?.toDouble() ?? 0.5;

        final existingIdx = _mistakes.indexWhere((m) => m.id == id || (m.bugId == bugId && m.problem == problem));
        if (existingIdx != -1) {
          _mistakes[existingIdx] = MistakeAutopsyItem(
            id: id.isNotEmpty ? id : _mistakes[existingIdx].id,
            bugId: _mistakes[existingIdx].bugId,
            nodeId: _mistakes[existingIdx].nodeId,
            problem: _mistakes[existingIdx].problem,
            offendingStep: _mistakes[existingIdx].offendingStep,
            correctPrinciple: _mistakes[existingIdx].correctPrinciple,
            status: status,
            stabilityDays: stability,
            isDue: status != 'cured',
          );
        } else {
          _mistakes.add(MistakeAutopsyItem(
            id: id.isNotEmpty ? id : 'm_${DateTime.now().millisecondsSinceEpoch}_${_mistakes.length + 1}',
            bugId: bugId,
            nodeId: raw['node_id'] as String? ?? '',
            problem: problem,
            offendingStep: raw['offending_step'] as String? ?? '',
            correctPrinciple: raw['correct_principle'] as String? ?? '',
            status: status,
            stabilityDays: stability,
            isDue: status != 'cured',
          ));
        }
      }
      await _persistToDisk();
    } catch (e) {
      debugPrint("MistakeVaultService sync warning: $e");
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }

  Future<void> _persistToDisk() async {
    if (storageFilePath == null) return;
    try {
      final file = File(storageFilePath!);
      await file.parent.create(recursive: true);
      final listJson = _mistakes.map((m) => m.toJson()).toList();
      final tempFile = File('${storageFilePath!}.tmp');
      await tempFile.writeAsString(jsonEncode(listJson), flush: true);
      if (await tempFile.exists()) {
        try {
          if (await file.exists()) {
            await file.delete();
          }
          await tempFile.rename(file.path);
        } catch (_) {
          try {
            await file.writeAsString(jsonEncode(listJson), flush: true);
            if (await tempFile.exists()) {
              await tempFile.delete();
            }
          } catch (_) {}
        }
      }
    } catch (e) {
      debugPrint("MistakeVaultService persist warning: $e");
    }
  }

  Future<void> _loadFromDisk() async {
    if (storageFilePath == null) return;
    try {
      final file = File(storageFilePath!);
      String content = '';
      if (await file.exists()) {
        content = await file.readAsString();
      } else {
        final tempFile = File('${storageFilePath!}.tmp');
        if (await tempFile.exists()) {
          content = await tempFile.readAsString();
        }
      }

      if (content.isNotEmpty) {
        dynamic decoded;
        try {
          decoded = jsonDecode(content);
        } catch (jsonErr) {
          debugPrint("MistakeVaultService main json parse failed, trying temp: $jsonErr");
          final tempFile = File('${storageFilePath!}.tmp');
          if (await tempFile.exists()) {
            final tempContent = await tempFile.readAsString();
            if (tempContent.isNotEmpty) {
              decoded = jsonDecode(tempContent);
            }
          }
        }

        if (decoded is List) {
          _mistakes.clear();
          for (final item in decoded) {
            try {
              if (item is Map<String, dynamic>) {
                _mistakes.add(MistakeAutopsyItem.fromJson(item));
              } else if (item is Map) {
                _mistakes.add(MistakeAutopsyItem.fromJson(Map<String, dynamic>.from(item)));
              }
            } catch (err) {
              // Corrupt record isolated: skip bad record and preserve all valid records
              debugPrint("MistakeVaultService corrupt record isolated: $err");
            }
          }
        }
      }
    } catch (e) {
      debugPrint("MistakeVaultService load warning: $e");
    }
  }
}
