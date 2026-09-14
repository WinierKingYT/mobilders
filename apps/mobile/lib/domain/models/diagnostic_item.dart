class DiagnosticItem {
  final String itemId;
  final String targetNodeId;
  final String prompt;
  final double difficultyB;
  final double discriminationA;

  const DiagnosticItem({
    required this.itemId,
    required this.targetNodeId,
    required this.prompt,
    required this.difficultyB,
    required this.discriminationA,
  });

  factory DiagnosticItem.fromJson(Map<String, dynamic> json) {
    return DiagnosticItem(
      itemId: json['item_id'] as String,
      targetNodeId: json['target_node_id'] as String,
      prompt: json['prompt'] as String,
      difficultyB: (json['difficulty_b'] as num).toDouble(),
      discriminationA: (json['discrimination_a'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'item_id': itemId,
      'target_node_id': targetNodeId,
      'prompt': prompt,
      'difficulty_b': difficultyB,
      'discrimination_a': discriminationA,
    };
  }
}

class DiagnosticSubmitResult {
  final double thetaHat;
  final double standardError;
  final bool isComplete;
  final DiagnosticItem? nextItem;
  final Map<String, double>? seededMastery;
  final List<String>? zpdCandidates;

  const DiagnosticSubmitResult({
    required this.thetaHat,
    required this.standardError,
    required this.isComplete,
    this.nextItem,
    this.seededMastery,
    this.zpdCandidates,
  });

  factory DiagnosticSubmitResult.fromJson(Map<String, dynamic> json) {
    return DiagnosticSubmitResult(
      thetaHat: (json['theta_hat'] as num).toDouble(),
      standardError: (json['standard_error'] as num).toDouble(),
      isComplete: json['is_complete'] as bool? ?? false,
      nextItem: json['next_item'] != null
          ? DiagnosticItem.fromJson(json['next_item'] as Map<String, dynamic>)
          : null,
      seededMastery: (json['seeded_mastery'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toDouble()),
      ),
      zpdCandidates: (json['zpd_candidates'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList(),
    );
  }
}
