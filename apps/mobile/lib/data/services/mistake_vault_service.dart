import 'package:flutter/foundation.dart';
import '../../ui/features/vault/mistake_autopsy_view.dart';

/// Service managing real cognitive mistakes and misconceptions made by the student.
/// Follows the Zero-Fabrication principle: starts empty, records only actual mistakes.
class MistakeVaultService extends ChangeNotifier {
  static final MistakeVaultService _instance = MistakeVaultService._internal();
  factory MistakeVaultService() => _instance;
  static MistakeVaultService get instance => _instance;

  MistakeVaultService._internal();

  final List<MistakeAutopsyItem> _mistakes = [];

  List<MistakeAutopsyItem> get mistakes => List.unmodifiable(_mistakes);

  bool get isEmpty => _mistakes.isEmpty;
  int get count => _mistakes.length;

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
      notifyListeners();
    }
  }

  /// Clears all mistakes (e.g. for testing or profile reset).
  void clearMistakes() {
    _mistakes.clear();
    notifyListeners();
  }
}
