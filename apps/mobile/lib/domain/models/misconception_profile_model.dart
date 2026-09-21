class MisconceptionNode {
  final String bugId;
  final String title;
  final String categoryId;
  final String categoryTitle;
  final String cognitiveCause;
  final String remediationDirective;
  final String correctPrinciple;
  final int frequency;
  final int openCount;
  final int inRemediationCount;
  final int curedCount;
  final String status; // 'critical', 'warning', 'in_remediation', 'cured', 'clean'
  final String? lastOffendingStep;
  final String? lastProblem;
  final double avgStabilityDays;

  const MisconceptionNode({
    required this.bugId,
    required this.title,
    required this.categoryId,
    required this.categoryTitle,
    required this.cognitiveCause,
    required this.remediationDirective,
    required this.correctPrinciple,
    required this.frequency,
    required this.openCount,
    required this.inRemediationCount,
    required this.curedCount,
    required this.status,
    this.lastOffendingStep,
    this.lastProblem,
    required this.avgStabilityDays,
  });

  bool get isCritical => status == 'critical';
  bool get isWarning => status == 'warning';
  bool get isInRemediation => status == 'in_remediation';
  bool get isCured => status == 'cured';
  bool get isClean => status == 'clean';

  factory MisconceptionNode.fromJson(Map<String, dynamic> json) {
    return MisconceptionNode(
      bugId: json['bug_id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      categoryId: json['category_id'] as String? ?? 'GENEL_CEBIR',
      categoryTitle: json['category_title'] as String? ?? 'Genel Cebir',
      cognitiveCause: json['cognitive_cause'] as String? ?? '',
      remediationDirective: json['remediation_directive'] as String? ?? '',
      correctPrinciple: json['correct_principle'] as String? ?? '',
      frequency: (json['frequency'] as num?)?.toInt() ?? 0,
      openCount: (json['open_count'] as num?)?.toInt() ?? 0,
      inRemediationCount: (json['in_remediation_count'] as num?)?.toInt() ?? 0,
      curedCount: (json['cured_count'] as num?)?.toInt() ?? 0,
      status: json['status'] as String? ?? 'clean',
      lastOffendingStep: json['last_offending_step'] as String?,
      lastProblem: json['last_problem'] as String?,
      avgStabilityDays: (json['avg_stability_days'] as num?)?.toDouble() ?? 0.5,
    );
  }

  Map<String, dynamic> toJson() => {
        'bug_id': bugId,
        'title': title,
        'category_id': categoryId,
        'category_title': categoryTitle,
        'cognitive_cause': cognitiveCause,
        'remediation_directive': remediationDirective,
        'correct_principle': correctPrinciple,
        'frequency': frequency,
        'open_count': openCount,
        'in_remediation_count': inRemediationCount,
        'cured_count': curedCount,
        'status': status,
        'last_offending_step': lastOffendingStep,
        'last_problem': lastProblem,
        'avg_stability_days': avgStabilityDays,
      };
}

class MisconceptionCategory {
  final String categoryId;
  final String categoryTitle;
  final int totalMistakes;
  final int activeMistakes;
  final int curedMistakes;
  final List<MisconceptionNode> nodes;

  const MisconceptionCategory({
    required this.categoryId,
    required this.categoryTitle,
    required this.totalMistakes,
    required this.activeMistakes,
    required this.curedMistakes,
    required this.nodes,
  });

  factory MisconceptionCategory.fromJson(Map<String, dynamic> json) {
    final rawNodes = json['nodes'] as List<dynamic>? ?? const [];
    return MisconceptionCategory(
      categoryId: json['category_id'] as String? ?? '',
      categoryTitle: json['category_title'] as String? ?? '',
      totalMistakes: (json['total_mistakes'] as num?)?.toInt() ?? 0,
      activeMistakes: (json['active_mistakes'] as num?)?.toInt() ?? 0,
      curedMistakes: (json['cured_mistakes'] as num?)?.toInt() ?? 0,
      nodes: rawNodes
          .map((n) => MisconceptionNode.fromJson(n as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'category_id': categoryId,
        'category_title': categoryTitle,
        'total_mistakes': totalMistakes,
        'active_mistakes': activeMistakes,
        'cured_mistakes': curedMistakes,
        'nodes': nodes.map((n) => n.toJson()).toList(),
      };
}

class MisconceptionProfileResponse {
  final String userId;
  final int totalRecordedMistakes;
  final int totalCured;
  final double overallCureRate;
  final List<MisconceptionNode> topRecurringTraps;
  final List<MisconceptionCategory> categories;

  const MisconceptionProfileResponse({
    required this.userId,
    required this.totalRecordedMistakes,
    required this.totalCured,
    required this.overallCureRate,
    required this.topRecurringTraps,
    required this.categories,
  });

  factory MisconceptionProfileResponse.fromJson(Map<String, dynamic> json) {
    final rawTraps = json['top_recurring_traps'] as List<dynamic>? ?? const [];
    final rawCats = json['categories'] as List<dynamic>? ?? const [];

    return MisconceptionProfileResponse(
      userId: json['user_id'] as String? ?? '',
      totalRecordedMistakes: (json['total_recorded_mistakes'] as num?)?.toInt() ?? 0,
      totalCured: (json['total_cured'] as num?)?.toInt() ?? 0,
      overallCureRate: (json['overall_cure_rate'] as num?)?.toDouble() ?? 0.0,
      topRecurringTraps: rawTraps
          .map((t) => MisconceptionNode.fromJson(t as Map<String, dynamic>))
          .toList(),
      categories: rawCats
          .map((c) => MisconceptionCategory.fromJson(c as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'user_id': userId,
        'total_recorded_mistakes': totalRecordedMistakes,
        'total_cured': totalCured,
        'overall_cure_rate': overallCureRate,
        'top_recurring_traps': topRecurringTraps.map((t) => t.toJson()).toList(),
        'categories': categories.map((c) => c.toJson()).toList(),
      };
}
