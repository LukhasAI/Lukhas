from typing import Any, Dict, List
import numpy as np

from .bio_symbolic_objects import BioSymbolicPattern, SymbolicRepresentationType


class SymbolicRepresenter:
    def apply_symbolic_representations(
        self, patterns: List[BioSymbolicPattern]
    ) -> Dict[str, Any]:
        """Apply symbolic mathematical representations to biological patterns"""

        symbolic_data = {}

        for pattern in patterns:
            if pattern.symbolic_representation == SymbolicRepresentationType.VECTOR_SPACE:
                # Represent as high-dimensional vector
                vector_dim = len(pattern.frequency_components) + len(
                    pattern.amplitude_envelope
                )
                vector_repr = pattern.frequency_components + pattern.amplitude_envelope
                symbolic_data[f"vector_{pattern.pattern_id}"] = {
                    "type": "vector_space",
                    "dimension": vector_dim,
                    "vector": vector_repr,
                    "norm": np.linalg.norm(vector_repr) if vector_repr else 0.0,
                }

            elif pattern.symbolic_representation == SymbolicRepresentationType.GRAPH_TOPOLOGY:
                # Represent as graph structure
                nodes = list(pattern.adaptation_coefficients.keys())
                edges = [
                    (nodes[i], nodes[j])
                    for i in range(len(nodes))
                    for j in range(i + 1, len(nodes))
                ]
                symbolic_data[f"graph_{pattern.pattern_id}"] = {
                    "type": "graph_topology",
                    "nodes": nodes,
                    "edges": edges,
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "density": (
                        len(edges) / (len(nodes) * (len(nodes) - 1) / 2)
                        if len(nodes) > 1
                        else 0.0
                    ),
                }

            elif (
                pattern.symbolic_representation
                == SymbolicRepresentationType.GEOMETRIC_MANIFOLD
            ):
                # Represent as manifold structure
                manifold_dim = min(3, len(pattern.coherence_matrix))  # 3D manifold max
                curvature = self._calculate_manifold_curvature(pattern.coherence_matrix)
                symbolic_data[f"manifold_{pattern.pattern_id}"] = {
                    "type": "geometric_manifold",
                    "dimension": manifold_dim,
                    "curvature": curvature,
                    "coherence_matrix": pattern.coherence_matrix,
                }

        return symbolic_data

    def _calculate_manifold_curvature(self, coherence_matrix: List[List[float]]) -> float:
        """Calculate approximate manifold curvature from coherence matrix"""
        if not coherence_matrix or not coherence_matrix[0]:
            return 0.0

        # Simple curvature estimate based on coherence variation
        flat_values = [val for row in coherence_matrix for val in row]
        if not flat_values:
            return 0.0

        mean_coherence = sum(flat_values) / len(flat_values)
        variance = sum((val - mean_coherence) ** 2 for val in flat_values) / len(
            flat_values
        )

        # Higher variance implies higher curvature
        return min(1.0, variance * 10)
