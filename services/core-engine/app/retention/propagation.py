"""
Part-Whole Nilpotent DAG Memory Propagation Engine.
Implements the analytical matrix operator P = (I - gamma * A)^(-1) (gamma = 0.80)
to automatically propagate memory stability increments from complex compound tasks
down to their prerequisite cognitive components across the Knowledge DAG.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import numpy as np
from app.graph.knowledge_dag import KnowledgeDAG


class PartWholePropagator:
    """
    Propagates memory stability updates across the Knowledge DAG.
    Solves P = (I - gamma * A)^(-1) where A is the strictly upper-triangular
    nilpotent dependency matrix of prerequisites.
    """

    DEFAULT_GAMMA = 0.80  # Depth decay multiplier: 0.80^depth

    def __init__(self, dag: Optional[KnowledgeDAG] = None, gamma: float = DEFAULT_GAMMA):
        self.dag = dag if dag is not None else KnowledgeDAG()
        self.gamma = gamma

        # Extract ordered node ids from topological sort
        self.node_ids: List[str] = self.dag.topological_sort()
        self.num_nodes: int = len(self.node_ids)
        self.node_to_idx: Dict[str, int] = {node_id: idx for idx, node_id in enumerate(self.node_ids)}

        # Build adjacency matrix A and propagation matrix P
        self.a_matrix: np.ndarray = self._build_adjacency_matrix()
        self.p_matrix: np.ndarray = self._compute_propagation_matrix()

    def _build_adjacency_matrix(self) -> np.ndarray:
        """
        Builds normalized prerequisite adjacency matrix A.
        A[i, j] > 0 if node i is a direct prerequisite of node j.
        Columns sum to <= 1.0.
        """
        a = np.zeros((self.num_nodes, self.num_nodes), dtype=np.float64)

        for j_id, j_idx in self.node_to_idx.items():
            node = self.dag.nodes.get(j_id)
            if not node:
                continue

            all_prereqs = list(set(node.strict_prereqs + node.soft_prereqs))
            prereqs = [p for p in all_prereqs if p in self.node_to_idx]
            if not prereqs:
                continue

            weight = 1.0 / float(len(prereqs))
            for p_id in prereqs:
                i_idx = self.node_to_idx[p_id]
                a[i_idx, j_idx] = weight

        return a

    def _compute_propagation_matrix(self) -> np.ndarray:
        """
        Computes P = (I - gamma * A)^(-1).
        Since A is nilpotent (DAG), (I - gamma * A) is guaranteed to be non-singular
        with determinant 1.0.
        """
        eye = np.eye(self.num_nodes, dtype=np.float64)
        m = eye - (self.gamma * self.a_matrix)
        # Analytical inversion
        p = np.linalg.inv(m)
        return p

    def get_propagation_weights(self, target_node_id: str) -> Dict[str, float]:
        """
        Returns the stability propagation multipliers P[:, j] for a given practiced node.
        Example: Practicing N15 gives N15: 1.0, N14: 0.40, N01: 0.12, etc.
        """
        if target_node_id not in self.node_to_idx:
            raise KeyError(f"Node '{target_node_id}' not found in Knowledge DAG")

        j_idx = self.node_to_idx[target_node_id]
        column = self.p_matrix[:, j_idx]

        weights = {}
        for node_id, i_idx in self.node_to_idx.items():
            w = float(column[i_idx])
            if w > 1e-4:
                weights[node_id] = round(w, 4)

        return weights

    def propagate_stability_increment(
        self,
        target_node_id: str,
        delta_stability: float,
        current_stabilities: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Applies impulse increment delta_stability to target_node_id and propagates
        to all ancestors via delta_S = P * u.
        Returns the updated stabilities dictionary.
        """
        if delta_stability <= 0.0:
            return dict(current_stabilities)

        weights = self.get_propagation_weights(target_node_id)
        updated = dict(current_stabilities)

        for node_id, weight in weights.items():
            current_s = updated.get(node_id, 1.0)
            increment = delta_stability * weight
            updated[node_id] = round(current_s + increment, 4)

        return updated
