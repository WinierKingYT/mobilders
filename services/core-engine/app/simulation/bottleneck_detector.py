"""
Curriculum Bottleneck & Misleading Item Detector.
Analyzes synthetic cohort failure spikes, cognitive overload points, and attrition
to empirically flag and prune problematic curriculum nodes before real student deployment.
"""

from __future__ import annotations
from typing import Dict, List, Any
import numpy as np


class BottleneckDetector:
    """Statistical detector for curriculum friction points and learning roadblocks."""

    @staticmethod
    def analyze_node_trajectories(
        node_pass_rates: Dict[str, float],
        node_median_trials: Dict[str, float],
        node_overload_rates: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        bottlenecks = []

        for node_id, pass_rate in node_pass_rates.items():
            median_trials = node_median_trials.get(node_id, 3.0)
            overload_pct = node_overload_rates.get(node_id, 0.10) * 100.0

            is_bottleneck = False
            reasons = []

            # 1. Attrition condition: pass rate < 55%
            if pass_rate < 0.55:
                is_bottleneck = True
                reasons.append(f"High attrition / failure rate: {round((1.0 - pass_rate)*100, 1)}% failure.")

            # 2. Extreme effort: requires > 9 trials to reach mastery threshold
            if median_trials > 9.0:
                is_bottleneck = True
                reasons.append(f"Excessive trial count to mastery: {round(median_trials, 1)} trials.")

            # 3. Cognitive Overload: > 25% students suffer severe mental strain
            if overload_pct > 25.0:
                is_bottleneck = True
                reasons.append(f"Severe cognitive overload observed in {round(overload_pct, 1)}% of cohort.")

            if is_bottleneck:
                bottlenecks.append({
                    "node_id": node_id,
                    "pass_rate_pct": round(pass_rate * 100.0, 1),
                    "median_trials_to_master": round(median_trials, 1),
                    "cognitive_overload_pct": round(overload_pct, 1),
                    "reasons": reasons,
                    "recommended_pruning_action": (
                        "Decompose into two intermediate sub-nodes and inject Al-Khwarizmi geometric scaffolding"
                        if median_trials > 9.0 else "Recalibrate 2PL-IRT discrimination and review prerequisite tree"
                    ),
                })

        bottlenecks.sort(key=lambda b: b["pass_rate_pct"])
        return bottlenecks
