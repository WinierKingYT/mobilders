class StepPsychometricsModel {
  final double bktPosteriorPl;
  final double bktNextPl;
  final double? ddmDriftRate;
  final double? ddmBoundarySeparation;
  final String? ddmCognitiveState;

  const StepPsychometricsModel({
    required this.bktPosteriorPl,
    required this.bktNextPl,
    this.ddmDriftRate,
    this.ddmBoundarySeparation,
    this.ddmCognitiveState,
  });

  factory StepPsychometricsModel.fromJson(Map<String, dynamic> json) {
    return StepPsychometricsModel(
      bktPosteriorPl: (json['bkt_posterior_p_l'] as num?)?.toDouble() ?? 0.20,
      bktNextPl: (json['bkt_next_p_l'] as num?)?.toDouble() ?? 0.20,
      ddmDriftRate: (json['ddm_drift_rate'] as num?)?.toDouble(),
      ddmBoundarySeparation: (json['ddm_boundary_separation'] as num?)?.toDouble(),
      ddmCognitiveState: json['ddm_cognitive_state'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'bkt_posterior_p_l': bktPosteriorPl,
      'bkt_next_p_l': bktNextPl,
      'ddm_drift_rate': ddmDriftRate,
      'ddm_boundary_separation': ddmBoundarySeparation,
      'ddm_cognitive_state': ddmCognitiveState,
    };
  }
}
