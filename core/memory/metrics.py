"""Pluggable drift metrics for memory comparison."""
from typing import Callable, Dict, Any
import numpy as np


# Type alias for drift functions
DriftFunction = Callable[[Any, Any], float]

# Global registry of drift metrics
_drift_registry: Dict[str, DriftFunction] = {}


def register_drift_fn(name: str, fn: DriftFunction) -> None:
    """
    Register a drift metric function.

    Args:
        name: Name of the drift metric
        fn: Function that takes two objects and returns drift score (0.0 to 1.0)
    """
    _drift_registry[name] = fn


def measure_drift(name: str, a: Any, b: Any) -> float:
    """
    Measure drift between two objects using a registered metric.

    Args:
        name: Name of the registered drift metric
        a: First object
        b: Second object

    Returns:
        Drift score (0.0 = no drift, 1.0 = maximum drift)

    Raises:
        KeyError: If metric name is not registered
    """
    if name not in _drift_registry:
        raise KeyError(f"Drift metric '{name}' not registered. Available: {list(_drift_registry.keys())}")

    return _drift_registry[name](a, b)


def get_registered_metrics() -> list[str]:
    """Get list of all registered metric names."""
    return list(_drift_registry.keys())


# Default metrics

def cosine_drift(a: Any, b: Any) -> float:
    """
    Compute drift using cosine distance.

    Args:
        a: First vector (list, array, or dict with numeric values)
        b: Second vector

    Returns:
        Cosine drift score (0.0 = identical, 1.0 = orthogonal)
    """
    # Convert inputs to numpy arrays
    vec_a = _to_vector(a)
    vec_b = _to_vector(b)

    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector dimensions must match: {len(vec_a)} != {len(vec_b)}")

    # Compute cosine similarity
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 1.0  # Maximum drift if either vector is zero

    cosine_similarity = dot_product / (norm_a * norm_b)

    # Convert to drift (0 = similar, 1 = different)
    drift = (1.0 - cosine_similarity) / 2.0
    return float(np.clip(drift, 0.0, 1.0))


def euclidean_drift(a: Any, b: Any) -> float:
    """
    Compute drift using normalized Euclidean distance.

    Args:
        a: First vector
        b: Second vector

    Returns:
        Normalized Euclidean drift score
    """
    vec_a = _to_vector(a)
    vec_b = _to_vector(b)

    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector dimensions must match: {len(vec_a)} != {len(vec_b)}")

    distance = np.linalg.norm(vec_a - vec_b)

    # Normalize by vector dimension for consistency
    normalized_distance = distance / np.sqrt(len(vec_a))

    return float(np.clip(normalized_distance, 0.0, 1.0))


def hamming_drift(a: Any, b: Any) -> float:
    """
    Compute drift using Hamming distance (for discrete/categorical data).

    Args:
        a: First sequence
        b: Second sequence

    Returns:
        Hamming drift score (proportion of differing elements)
    """
    seq_a = _to_sequence(a)
    seq_b = _to_sequence(b)

    if len(seq_a) != len(seq_b):
        raise ValueError(f"Sequence lengths must match: {len(seq_a)} != {len(seq_b)}")

    if len(seq_a) == 0:
        return 0.0

    differences = sum(1 for x, y in zip(seq_a, seq_b) if x != y)
    drift = differences / len(seq_a)

    return float(drift)


def _to_vector(obj: Any) -> np.ndarray:
    """Convert object to numpy array."""
    if isinstance(obj, np.ndarray):
        return obj
    elif isinstance(obj, (list, tuple)):
        return np.array(obj, dtype=float)
    elif isinstance(obj, dict):
        # Convert dict values to vector (sorted by keys for consistency)
        sorted_values = [obj[k] for k in sorted(obj.keys())]
        return np.array(sorted_values, dtype=float)
    else:
        raise TypeError(f"Cannot convert {type(obj)} to vector")


def _to_sequence(obj: Any) -> list:
    """Convert object to sequence."""
    if isinstance(obj, (list, tuple)):
        return list(obj)
    elif isinstance(obj, str):
        return list(obj)
    elif isinstance(obj, dict):
        return list(obj.values())
    else:
        raise TypeError(f"Cannot convert {type(obj)} to sequence")


# Register default metrics
register_drift_fn("cosine", cosine_drift)
register_drift_fn("euclidean", euclidean_drift)
register_drift_fn("hamming", hamming_drift)


if __name__ == "__main__":
    # Demonstration
    print("=== Drift Metrics Registry Demo ===\n")

    # Show registered metrics
    print(f"Registered metrics: {get_registered_metrics()}\n")

    # Test cosine drift
    vec1 = [1.0, 2.0, 3.0, 4.0]
    vec2 = [1.1, 2.1, 2.9, 4.2]
    vec3 = [4.0, 3.0, 2.0, 1.0]

    print("Cosine Drift:")
    print(f"  vec1 vs vec2 (similar): {measure_drift('cosine', vec1, vec2):.4f}")
    print(f"  vec1 vs vec3 (different): {measure_drift('cosine', vec1, vec3):.4f}\n")

    # Test Euclidean drift
    print("Euclidean Drift:")
    print(f"  vec1 vs vec2 (similar): {measure_drift('euclidean', vec1, vec2):.4f}")
    print(f"  vec1 vs vec3 (different): {measure_drift('euclidean', vec1, vec3):.4f}\n")

    # Test Hamming drift
    seq1 = "ABCDEF"
    seq2 = "ABCDEG"  # 1 difference
    seq3 = "XYZWUV"  # All different

    print("Hamming Drift:")
    print(f"  seq1 vs seq2 (1 diff): {measure_drift('hamming', seq1, seq2):.4f}")
    print(f"  seq1 vs seq3 (all diff): {measure_drift('hamming', seq1, seq3):.4f}\n")

    # Register custom metric
    def manhattan_drift(a, b):
        vec_a = _to_vector(a)
        vec_b = _to_vector(b)
        distance = np.sum(np.abs(vec_a - vec_b))
        return float(np.clip(distance / len(vec_a), 0.0, 1.0))

    register_drift_fn("manhattan", manhattan_drift)
    print(f"After registering 'manhattan': {get_registered_metrics()}")
    print(f"Manhattan drift (vec1 vs vec2): {measure_drift('manhattan', vec1, vec2):.4f}")
