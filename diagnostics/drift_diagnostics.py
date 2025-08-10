import json
import logging
import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Dict

logger = logging.getLogger(__name__)


def calculate_drift_score(values: Sequence[float]) -> float:
    """Compute average absolute difference between sequential values.

    # ΛTAG: drift
    """
    if not values or len(values) < 2:
        return 0.0

    deltas = [abs(b - a) for a, b in zip(values, values[1:])]
    score = sum(deltas) / len(deltas)
    logger.debug("Calculated drift score: %s", score)
    return score


def generate_entropy_map_from_memory(memory: Mapping[str, int]) -> Dict[str, float]:
    """Create entropy contribution per memory element using Shannon entropy.

    # ΛTAG: entropy
    """
    total = float(sum(memory.values()))
    if total == 0:
        return {}

    entropy_map = {}
    for key, count in memory.items():
        p = count / total
        entropy_map[key] = -p * math.log2(p)
    logger.debug("Generated entropy map: %s", entropy_map)
    return entropy_map


def detect_collapse_points(entropy_map: Mapping[str, float], threshold: float = 0.1) -> Iterable[str]:
    """Identify keys where entropy contribution falls below the threshold.

    # ΛTAG: collapse
    """
    collapse = [k for k, v in entropy_map.items() if v < threshold]
    logger.debug("Detected collapse points at threshold %s: %s", threshold, collapse)
    return collapse


def get_diagnostics_summary(values: Sequence[float], memory: Mapping[str, int], threshold: float = 0.1) -> str:
    """Return diagnostics summary as JSON string for API consumption.

    # ΛTAG: drift
    """
    # TODO: Integrate glyph heatmap support
    drift_score = calculate_drift_score(values)
    entropy_map = generate_entropy_map_from_memory(memory)
    collapse_points = list(detect_collapse_points(entropy_map, threshold))

    summary = {
        "driftScore": drift_score,
        "entropyMap": entropy_map,
        "collapsePoints": collapse_points,
    }
    logger.debug("Diagnostics summary generated: %s", summary)
    return json.dumps(summary)
