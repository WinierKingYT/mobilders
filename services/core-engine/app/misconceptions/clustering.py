"""
Unsupervised Error Clustering Engine for Diagnostic Misconception Discovery.
Clusters unexpected student step errors into semantic misconception groups.
Ref: Document 08 (Error and Misconception Engine).
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict
import numpy as np


class UnsupervisedErrorClusterer:
    """
    Groups unexpected student erroneous inputs based on AST structure,
    token composition, and mathematical transformations.
    """

    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters

    def _extract_features(self, error_str: str, prev_str: str) -> np.ndarray:
        """
        Extracts a normalized 8-dimensional structural feature vector from an algebraic error.
        1. Has inequality symbol (<, >, <=, >=)
        2. Has negative sign (-)
        3. Has square / exponent (**2, ^2)
        4. Has parentheses
        5. Has square root (sqrt)
        6. Length ratio between error_str and prev_str
        7. Relative count of digits
        8. Has interval brackets ([, ], (, ))
        """
        clean_err = error_str.strip()
        clean_prev = prev_str.strip() if prev_str else clean_err

        f1 = 1.0 if any(op in clean_err for op in ["<", ">", "<=", ">="]) else 0.0
        f2 = 1.0 if "-" in clean_err else 0.0
        f3 = 1.0 if any(sq in clean_err for sq in ["**2", "^2", "²"]) else 0.0
        f4 = 1.0 if ("(" in clean_err and ")" in clean_err) else 0.0
        f5 = 1.0 if "sqrt" in clean_err or "√" in clean_err else 0.0
        len_ratio = len(clean_err) / max(1.0, float(len(clean_prev)))
        f6 = float(np.clip(len_ratio, 0.1, 3.0))
        digit_count = len(re.findall(r"\d", clean_err))
        f7 = float(np.clip(digit_count / max(1.0, float(len(clean_err))), 0.0, 1.0))
        f8 = 1.0 if any(b in clean_err for b in ["[", "]", "∪", "veya", "or"]) else 0.0

        return np.array([f1, f2, f3, f4, f5, f6, f7, f8], dtype=np.float64)

    def cluster_errors(
        self,
        error_records: List[Dict[str, str]],
    ) -> Dict[int, Dict[str, Any]]:
        """
        Clusters error records: [{"user_step": "...", "previous_step": "...", "student_id": "..."}]
        Returns clusters with cluster_id, exemplar expressions, size, and candidate label.
        """
        if not error_records:
            return {}

        X = np.array([
            self._extract_features(r["user_step"], r.get("previous_step", ""))
            for r in error_records
        ])

        k = min(self.n_clusters, len(error_records))
        if k <= 1:
            return {
                0: {
                    "cluster_id": 0,
                    "count": len(error_records),
                    "exemplars": [r["user_step"] for r in error_records[:3]],
                    "candidate_rule": "GENERAL_UNCLASSIFIED",
                }
            }

        # K-Means clustering algorithm
        np.random.seed(42)
        indices = np.random.choice(len(X), size=k, replace=False)
        centroids = X[indices, :].copy()

        labels = np.zeros(len(X), dtype=int)
        for _ in range(15):
            # Assign nearest centroid
            dists = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
            new_labels = np.argmin(dists, axis=1)

            if np.array_equal(labels, new_labels):
                break
            labels = new_labels

            # Recompute centroids
            for c_id in range(k):
                members = X[labels == c_id]
                if len(members) > 0:
                    centroids[c_id] = np.mean(members, axis=0)

        # Assemble summary
        clusters = {}
        for c_id in range(k):
            member_indices = [i for i, lbl in enumerate(labels) if lbl == c_id]
            exemplars = [error_records[i]["user_step"] for i in member_indices[:5]]

            # Heuristic label inference based on centroid features
            cent = centroids[c_id]
            if cent[0] > 0.5 and cent[1] > 0.5:
                label = "INEQUALITY_SIGN_REVERSAL_CANDIDATE"
            elif cent[7] > 0.4:
                label = "INTERVAL_BOUNDARY_INVERSION_CANDIDATE"
            elif cent[2] > 0.5 and cent[3] > 0.5:
                label = "DOUBLE_ROOT_TRANSFORMATION_CANDIDATE"
            elif cent[1] > 0.4 and cent[6] > 0.3:
                label = "PARABOLA_VERTEX_SIGN_CANDIDATE"
            else:
                label = f"CLUSTER_PATTERN_{c_id+1}"

            clusters[c_id] = {
                "cluster_id": c_id,
                "count": len(member_indices),
                "exemplars": exemplars,
                "candidate_rule": label,
                "centroid": [round(float(val), 3) for val in cent],
            }

        return clusters
