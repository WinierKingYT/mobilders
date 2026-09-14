class DiagnosticBug {
  final String? bugId;
  final String severity;
  final String category;
  final String description;
  final String remediationDirective;
  final String? offendingTerm;

  const DiagnosticBug({
    this.bugId,
    required this.severity,
    required this.category,
    required this.description,
    required this.remediationDirective,
    this.offendingTerm,
  });

  factory DiagnosticBug.fromJson(Map<String, dynamic> json) {
    return DiagnosticBug(
      bugId: json['bug_id'] as String?,
      severity: json['severity'] as String? ?? 'WARNING',
      category: json['category'] as String? ?? 'ALGEBRAIC',
      description: json['description'] as String? ?? '',
      remediationDirective: json['remediation_directive'] as String? ?? '',
      offendingTerm: json['offending_term'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'bug_id': bugId,
      'severity': severity,
      'category': category,
      'description': description,
      'remediation_directive': remediationDirective,
      'offending_term': offendingTerm,
    };
  }
}
