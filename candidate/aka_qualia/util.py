#!/usr/bin/env python3
"""
Aka Qualia Utilities (C4.2)
============================

Helper functions for proto-qualia vector operations, similarity computation,
and data transformations used by the memory system.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple


def to_proto_vec(proto: dict[str, Any]) -> list[float]:
    """
    Convert ProtoQualia dict to fixed 5-dimensional vector.

    Vector format: [tone, arousal, clarity, embodiment, narrative_gravity]
    Used for vector similarity operations in PostgreSQL and app-side computation.

    Args:
        proto: ProtoQualia dictionary with numeric fields

    Returns:
        5-dimensional vector as list of floats

    Example:
        >>> proto = {"tone": 0.5, "arousal": 0.8, "clarity": 0.7, "embodiment": 0.6, "narrative_gravity": 0.9}
        >>> to_proto_vec(proto)
        [0.5, 0.8, 0.7, 0.6, 0.9]
    """
    return [
        float(proto.get("tone", 0.0)),
        float(proto.get("arousal", 0.0)),
        float(proto.get("clarity", 0.0)),
        float(proto.get("embodiment", 0.0)),
        float(proto.get("narrative_gravity", 0.0)),
    ]


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Used for SQLite fallback when pgvector is not available.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity in range [-1, 1] where 1 = identical, -1 = opposite

    Example:
        >>> cosine_similarity([1, 0, 0], [1, 0, 0])
        1.0
        >>> cosine_similarity([1, 0, 0], [-1, 0, 0])
        -1.0
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")

    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    # Compute magnitudes
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5

    # Handle zero vectors
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def euclidean_distance(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute Euclidean distance between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Euclidean distance (lower = more similar)
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")

    return sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5


def find_similar_scenes(
    target_proto: dict[str, Any],
    scene_list: list[dict[str, Any]],
    similarity_threshold: float = 0.7,
    max_results: int = 10,
) -> list[tuple[dict[str, Any], float]]:
    """
    Find similar scenes using proto-qualia vector similarity.

    SQLite fallback for when pgvector is not available.

    Args:
        target_proto: Target ProtoQualia to find similar scenes for
        scene_list: List of scenes with 'proto' field
        similarity_threshold: Minimum cosine similarity to include
        max_results: Maximum number of results to return

    Returns:
        List of (scene, similarity_score) tuples ordered by similarity desc
    """
    target_vec = to_proto_vec(target_proto)
    results = []

    for scene in scene_list:
        scene_vec = to_proto_vec(scene["proto"])
        similarity = cosine_similarity(target_vec, scene_vec)

        if similarity >= similarity_threshold:
            results.append((scene, similarity))

    # Sort by similarity descending and limit results
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:max_results]


def compute_proto_hash(proto: dict[str, Any], precision: int = 3) -> str:
    """
    Compute stable hash of proto-qualia for deduplication.

    Args:
        proto: ProtoQualia dictionary
        precision: Decimal precision for numeric fields

    Returns:
        SHA256 hex hash of normalized proto-qualia
    """
    # Normalize numeric fields to fixed precision
    normalized = {}
    for key, value in proto.items():
        if isinstance(value, (int, float)):
            normalized[key] = round(float(value), precision)
        else:
            normalized[key] = value

    # Convert to canonical JSON and hash
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def extract_affect_energy(proto: dict[str, Any]) -> float:
    """
    Extract total affective energy from proto-qualia for conservation tracking.

    Implementation matches ProtoQualia.energy_signature() method.

    Args:
        proto: ProtoQualia dictionary

    Returns:
        Total affective energy as float
    """
    tone = abs(float(proto.get("tone", 0.0)))
    arousal = float(proto.get("arousal", 0.0))
    clarity = float(proto.get("clarity", 0.0))
    embodiment = float(proto.get("embodiment", 0.0))

    return tone + arousal + clarity + embodiment


def validate_proto_bounds(proto: dict[str, Any]) -> list[str]:
    """
    Validate proto-qualia field bounds.

    Args:
        proto: ProtoQualia dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required numeric fields
    required_fields = {
        "tone": (-1.0, 1.0),
        "arousal": (0.0, 1.0),
        "clarity": (0.0, 1.0),
        "embodiment": (0.0, 1.0),
        "narrative_gravity": (0.0, 1.0),
    }

    for field, (min_val, max_val) in required_fields.items():
        value = proto.get(field)
        if value is None:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(value, (int, float)):
            errors.append(f"Field {field} must be numeric, got {type(value).__name__}")
        elif not (min_val <= value <= max_val):
            errors.append(f"Field {field}={value} out of bounds [{min_val}, {max_val}]")

    # Check colorfield format
    colorfield = proto.get("colorfield")
    if colorfield and not isinstance(colorfield, str):
        errors.append(f"colorfield must be string, got {type(colorfield).__name__}")
    elif colorfield and "/" not in colorfield:
        errors.append("colorfield must contain '/' separator (e.g., 'aka/red')")

    return errors


def compute_drift_phi(
    current_proto: dict[str, Any], previous_proto: Optional[dict[str, Any]] = None, time_delta_seconds: float = 1.0
) -> float:
    """
    Compute temporal coherence drift between consecutive proto-qualia states.

    Lower values indicate better temporal coherence.

    Args:
        current_proto: Current proto-qualia state
        previous_proto: Previous proto-qualia state (None for first scene)
        time_delta_seconds: Time elapsed between states

    Returns:
        Drift phi value (0.0 = perfect coherence, 1.0 = maximum drift)
    """
    if previous_proto is None:
        # First scene - perfect coherence by definition
        return 1.0

    current_vec = to_proto_vec(current_proto)
    previous_vec = to_proto_vec(previous_proto)

    # Compute vector distance normalized by time
    distance = euclidean_distance(current_vec, previous_vec)

    # Normalize by maximum possible distance and time
    max_distance = 5.0**0.5  # sqrt(1^2 + 1^2 + 1^2 + 1^2 + 1^2) for max bounds
    time_factor = min(time_delta_seconds / 60.0, 1.0)  # Normalize to minutes, cap at 1

    drift_phi = (distance / max_distance) * time_factor
    return max(0.0, min(drift_phi, 1.0))  # Cap between 0 and 1


# Constants for vector operations
PROTO_DIMENSION = 5
PROTO_FIELD_ORDER = ["tone", "arousal", "clarity", "embodiment", "narrative_gravity"]
PROTO_BOUNDS = {
    "tone": (-1.0, 1.0),
    "arousal": (0.0, 1.0),
    "clarity": (0.0, 1.0),
    "embodiment": (0.0, 1.0),
    "narrative_gravity": (0.0, 1.0),
}
