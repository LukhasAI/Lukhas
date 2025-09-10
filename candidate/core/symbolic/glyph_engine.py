"""Symbolic glyph generation utilities.

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

This module handles GLYPH creation and symbolic evaluation logic.
"""
import hashlib
import json
import math
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

# ΛTAG: glyph_engine


def generate_glyph(state_dict: dict[str, Any]) -> str:
    """Generate a glyph from a state dictionary.

    Parameters
    ----------
    state_dict: Dict[str, Any]
        Input symbolic state metrics.

    Returns
    -------
    str
        A unique glyph representation of the state.
    """
    # DONE: implement glyph generation logic (# ΛTAG: glyph_generation)

    # Extract core components for glyph generation
    timestamp = state_dict.get("timestamp", datetime.now(timezone.utc).isoformat())
    state_dict.get("user_id", "anonymous")
    tier_level = state_dict.get("tier_level", 0)

    # Create a deterministic hash from state components
    state_json = json.dumps(state_dict, sort_keys=True, default=str)
    state_hash = hashlib.sha256(state_json.encode()).hexdigest()

    # Generate symbolic representation based on tier and hash
    # Using Unicode symbols to create visually distinct glyphs
    tier_symbols = [
        "○",  # ○ - Public (0)
        "●",  # ● - Authenticated (1)
        "▲",  # ▲ - Elevated (2)
        "★",  # ★ - Privileged (3)
        "♦",  # ♦ - Admin (4)
        "Λ",  # Λ - System (5)
    ]

    # Select base symbol based on tier
    base_symbol = tier_symbols[min(tier_level, len(tier_symbols) - 1)]

    # Create glyph pattern from hash (first 8 chars)
    hash_segment = state_hash[:8]

    # Convert to visual pattern
    pattern_parts = []
    for i in range(0, 8, 2):
        hex_val = int(hash_segment[i : i + 2], 16)
        # Map to different Unicode block elements
        if hex_val < 64:
            pattern_parts.append("░")  # ░ light shade
        elif hex_val < 128:
            pattern_parts.append("▒")  # ▒ medium shade
        elif hex_val < 192:
            pattern_parts.append("▓")  # ▓ dark shade
        else:
            pattern_parts.append("█")  # █ full block

    # Construct final glyph
    pattern = "".join(pattern_parts)
    glyph = f"{base_symbol}[{pattern}]Λ"

    # Add temporal marker if recent (within last hour)
    if "timestamp" in state_dict:
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if (datetime.now(timezone.utc) - ts).total_seconds() < 3600:
                glyph += "◎"  # ◎ recent activity marker
        except BaseException:
            pass

    return glyph


def evaluate_entropy(vector: Sequence[float]) -> float:
    """Evaluate Shannon entropy for a numeric vector."""
    if not vector:
        return 0.0
    total = float(sum(vector))
    if total == 0:
        return 0.0
    probabilities = [v / total for v in vector]
    return -sum(p * math.log2(p) for p in probabilities if p > 0)


def evaluate_resonance(symbolic_vector: Sequence[float]) -> float:
    """Evaluate resonance patterns in symbolic vector.

    Resonance indicates alignment or coherence in the symbolic space.

    Parameters
    ----------
    symbolic_vector: Sequence[float]
        Vector of symbolic values to analyze.

    Returns
    -------
    float
        Resonance score between 0.0 (no resonance) and 1.0 (perfect resonance).
    """
    # DONE: implement resonance evaluation (# ΛTAG: resonance_eval)

    if not symbolic_vector or len(symbolic_vector) < 2:
        return 0.0

    # Calculate autocorrelation as measure of resonance
    n = len(symbolic_vector)
    mean = sum(symbolic_vector) / n

    # Normalize the vector
    normalized = [x - mean for x in symbolic_vector]

    # Calculate variance
    variance = sum(x**2 for x in normalized) / n
    if variance == 0:
        return 1.0  # Perfect resonance (all values identical)

    # Calculate autocorrelation at different lags
    max_lag = min(n // 2, 10)  # Limit lag to reasonable range
    correlations = []

    for lag in range(1, max_lag + 1):
        correlation = sum(normalized[i] * normalized[i - lag] for i in range(lag, n)) / (n - lag)
        correlations.append(abs(correlation / variance))

    # Resonance score is the maximum correlation found
    resonance = max(correlations) if correlations else 0.0

    # Apply sigmoid transformation to get value between 0 and 1
    return 2 / (1 + math.exp(-3 * resonance)) - 1


def detect_attractors(
    symbolic_history: Sequence[Sequence[float]],
) -> list[dict[str, Any]]:
    """Detect attractor patterns in symbolic history.

    Attractors are recurring patterns or states that the system tends toward.

    Parameters
    ----------
    symbolic_history: Sequence[Sequence[float]]
        Historical sequence of symbolic vectors.

    Returns
    -------
    List[Dict[str, Any]]
        List of detected attractors with their properties.
    """
    # DONE: implement attractor detection (# ΛTAG: attractor_detection)

    if not symbolic_history or len(symbolic_history) < 3:
        return []

    attractors = []

    # Convert sequences to hashable tuples for pattern detection
    history_tuples = [tuple(round(x, 3) for x in vec) for vec in symbolic_history]

    # Find recurring patterns
    pattern_counts = {}
    pattern_positions = {}

    for i, pattern in enumerate(history_tuples):
        if pattern in pattern_counts:
            pattern_counts[pattern] += 1
            pattern_positions[pattern].append(i)
        else:
            pattern_counts[pattern] = 1
            pattern_positions[pattern] = [i]

    # Identify attractors (patterns that appear multiple times)
    for pattern, count in pattern_counts.items():
        if count >= 2:  # Minimum 2 occurrences to be an attractor
            positions = pattern_positions[pattern]

            # Calculate average return time
            if len(positions) > 1:
                intervals = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
                avg_return_time = sum(intervals) / len(intervals)
            else:
                avg_return_time = 0

            # Calculate strength (frequency relative to history length)
            strength = count / len(symbolic_history)

            # Calculate stability (how consistent the return intervals are)
            if len(intervals) > 1:
                interval_variance = sum((x - avg_return_time) ** 2 for x in intervals) / len(intervals)
                stability = 1 / (1 + interval_variance)
            else:
                stability = 0.5

            attractors.append(
                {
                    "pattern": list(pattern),
                    "occurrences": count,
                    "strength": strength,
                    "average_return_time": avg_return_time,
                    "stability": stability,
                    "positions": positions,
                    "entropy": evaluate_entropy(pattern) if pattern else 0.0,
                }
            )

    # Sort by strength (most dominant attractors first)
    attractors.sort(key=lambda x: x["strength"], reverse=True)

    return attractors