class TwinQuestionModel {
  final String twinId;
  final String targetEquation;
  final List<double> canonicalRoots;
  final String targetedBugId;
  final String targetedBugTitle;
  final String pedagogicalFocus;
  final String hint;
  final int difficultyLevel;

  const TwinQuestionModel({
    required this.twinId,
    required this.targetEquation,
    required this.canonicalRoots,
    required this.targetedBugId,
    required this.targetedBugTitle,
    required this.pedagogicalFocus,
    required this.hint,
    this.difficultyLevel = 1,
  });

  factory TwinQuestionModel.fromJson(Map<String, dynamic> json) {
    final rawRoots = json['canonical_roots'] as List<dynamic>? ?? const [];
    return TwinQuestionModel(
      twinId: json['twin_id'] as String? ?? '',
      targetEquation: json['target_equation'] as String? ?? '',
      canonicalRoots: rawRoots.map((r) => (r as num).toDouble()).toList(),
      targetedBugId: json['targeted_bug_id'] as String? ?? '',
      targetedBugTitle: json['targeted_bug_title'] as String? ?? '',
      pedagogicalFocus: json['pedagogical_focus'] as String? ?? '',
      hint: json['hint'] as String? ?? '',
      difficultyLevel: (json['difficulty_level'] as num?)?.toInt() ?? 1,
    );
  }

  Map<String, dynamic> toJson() => {
        'twin_id': twinId,
        'target_equation': targetEquation,
        'canonical_roots': canonicalRoots,
        'targeted_bug_id': targetedBugId,
        'targeted_bug_title': targetedBugTitle,
        'pedagogical_focus': pedagogicalFocus,
        'hint': hint,
        'difficulty_level': difficultyLevel,
      };
}
