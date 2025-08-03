"""Service analysis utilities for microservice architectures.


#TAG:memory
#TAG:causal
#TAG:neuroplastic
#TAG:colony


Addresses REALITY_TODO tasks 9 and 12.

Provides functions to evaluate digital friction from inter-service
communication and to compute a modularity score based on coupling.
"""

from __future__ import annotations


from typing import Sequence, List

# ΛTAG: digital_friction


def compute_digital_friction(
    num_calls: int, serialization_cost: float, average_latency: float
) -> float:

    """Estimate digital friction from network communication.

    Parameters
    ----------
    num_calls: int
        Number of inter-service calls made.
    serialization_cost: float
        Cost in milliseconds to serialize/deserialize payloads.
    average_latency: float
        Average network latency per call in milliseconds.

    Returns
    -------
    float
        Estimated friction score between 0 and 1.
    """
    if num_calls <= 0:
        return 0.0

    cost = num_calls * (serialization_cost + average_latency)
    # Normalize with a simple heuristic where 10000ms total cost == 1.0
    score = min(cost / 10000.0, 1.0)
    return score



# ΛTAG: modularity_score


def compute_modularity_score(
    num_services: int, coupling_matrix: Sequence[Sequence[float]]
) -> float:

    """Compute a modularity score based on service coupling.

    A lower average coupling results in a higher modularity score.
    The score is normalized between 0 and 1.
    """
    if num_services <= 0:
        return 0.0
    if not coupling_matrix:
        return 1.0

    # Calculate average coupling excluding self-coupling
    total = 0.0
    count = 0
    for i, row in enumerate(coupling_matrix):
        for j, val in enumerate(row):
            if i == j:
                continue
            total += abs(val)
            count += 1
    if count == 0:
        return 1.0

    avg_coupling = total / count
    score = max(0.0, 1.0 - avg_coupling)
    return score



__all__ = ["compute_digital_friction", "compute_modularity_score"]
