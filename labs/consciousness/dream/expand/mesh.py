"""
Simulated collective dreaming (multi-agent).
Aggregates emotional contexts across multiple agents.
"""
import os
import statistics
from typing import Any, Dict, List, Optional

ENABLED = os.getenv("LUKHAS_MULTI_AGENT", "0") == "1"
AGGREGATION_METHOD = os.getenv("LUKHAS_MESH_AGGREGATION", "mean")  # mean|median|max|min
MIN_AGENTS = int(os.getenv("LUKHAS_MESH_MIN_AGENTS", "2"))

def mesh_align(agent_snapshots: List[List[Dict[str, Any]]]) -> Dict[str, float]:
    """
    Aggregate emotional contexts across multiple agents.

    Args:
        agent_snapshots: List of snapshot lists, one per agent

    Returns:
        Aggregated emotional context dict

    Safety guarantees:
    - Disabled by default
    - Transparent aggregation methods
    - Values bounded to [0,1] range
    - Requires minimum agent count
    """
    if not ENABLED:
        return {}

    if len(agent_snapshots) < MIN_AGENTS:
        return {}

    # Collect all emotional contexts
    all_emotions = {}

    for agent_idx, agent_snaps in enumerate(agent_snapshots):
        for snap_idx, snapshot in enumerate(agent_snaps):
            if "emotional_context" not in snapshot:
                continue

            emotion_context = snapshot["emotional_context"]
            if not isinstance(emotion_context, dict):
                continue

            for emotion_key, emotion_value in emotion_context.items():
                if emotion_key not in all_emotions:
                    all_emotions[emotion_key] = []

                # Validate emotion value
                try:
                    value = float(emotion_value)
                    value = max(0.0, min(1.0, value))  # Clamp to valid range
                    all_emotions[emotion_key].append(value)
                except (ValueError, TypeError):
                    continue  # Skip invalid values

    # Aggregate using specified method
    aggregated = {}
    for emotion_key, values in all_emotions.items():
        if not values:
            continue

        if AGGREGATION_METHOD == "mean":
            aggregated[emotion_key] = statistics.mean(values)
        elif AGGREGATION_METHOD == "median":
            aggregated[emotion_key] = statistics.median(values)
        elif AGGREGATION_METHOD == "max":
            aggregated[emotion_key] = max(values)
        elif AGGREGATION_METHOD == "min":
            aggregated[emotion_key] = min(values)
        else:
            # Default to mean for unknown methods
            aggregated[emotion_key] = statistics.mean(values)

        # Ensure final values are in valid range
        aggregated[emotion_key] = max(0.0, min(1.0, aggregated[emotion_key]))

    return aggregated

def mesh_consensus(agent_selections: List[str], agent_confidences: List[float] = None) -> Optional[str]:
    """
    Determine consensus selection across multiple agents.

    Args:
        agent_selections: List of selected snapshot names from each agent
        agent_confidences: Optional confidence weights for each agent

    Returns:
        Consensus selection name, or None if no clear consensus
    """
    if not ENABLED or not agent_selections:
        return None

    if agent_confidences is None:
        agent_confidences = [1.0] * len(agent_selections)

    if len(agent_selections) != len(agent_confidences):
        return None  # Mismatched lengths

    # Weighted voting
    vote_weights = {}
    for selection, confidence in zip(agent_selections, agent_confidences):
        if selection not in vote_weights:
            vote_weights[selection] = 0.0
        vote_weights[selection] += confidence

    if not vote_weights:
        return None

    # Find selection with highest weighted vote
    consensus_selection = max(vote_weights.keys(), key=lambda k: vote_weights[k])
    return consensus_selection

def analyze_mesh_diversity(agent_snapshots: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Analyze diversity in multi-agent emotional contexts.

    Returns:
        Dictionary with diversity metrics
    """
    if not ENABLED:
        return {"enabled": False}

    if len(agent_snapshots) < MIN_AGENTS:
        return {"error": "Insufficient agents for analysis"}

    # Collect emotion values for diversity analysis
    emotion_diversity = {}
    agent_count = len(agent_snapshots)

    for emotion_key in ["confidence", "curiosity", "joy", "fear", "anger", "sadness", "surprise", "trust"]:
        values_by_agent = []

        for agent_snaps in agent_snapshots:
            agent_values = []
            for snapshot in agent_snaps:
                if "emotional_context" in snapshot and emotion_key in snapshot["emotional_context"]:
                    try:
                        value = float(snapshot["emotional_context"][emotion_key])
                        agent_values.append(max(0.0, min(1.0, value)))
                    except (ValueError, TypeError):
                        continue

            if agent_values:
                values_by_agent.append(statistics.mean(agent_values))

        if len(values_by_agent) >= 2:
            emotion_diversity[emotion_key] = {
                "mean": statistics.mean(values_by_agent),
                "std_dev": statistics.stdev(values_by_agent),
                "range": max(values_by_agent) - min(values_by_agent),
                "agent_count": len(values_by_agent)
            }

    # Overall diversity metrics
    overall_diversity = 0.0
    if emotion_diversity:
        avg_std_dev = statistics.mean([metrics["std_dev"] for metrics in emotion_diversity.values()])
        overall_diversity = avg_std_dev

    return {
        "enabled": True,
        "agent_count": agent_count,
        "emotion_diversity": emotion_diversity,
        "overall_diversity": overall_diversity,
        "aggregation_method": AGGREGATION_METHOD
    }

def validate_mesh_output(agent_snapshots: List[List[Dict[str, Any]]],
                        aggregated: Dict[str, float]) -> bool:
    """
    Validate that mesh aggregation produces safe output.

    Returns True if output is safe, False otherwise.
    """
    if not ENABLED:
        return len(aggregated) == 0

    # Check value ranges
    for emotion_key, value in aggregated.items():
        if not (0.0 <= value <= 1.0):
            return False

    # Check that aggregated values are reasonable given input
    # (i.e., not outside the range of input values)
    input_ranges = {}
    for agent_snaps in agent_snapshots:
        for snapshot in agent_snaps:
            if "emotional_context" not in snapshot:
                continue
            for emotion_key, emotion_value in snapshot["emotional_context"].items():
                try:
                    value = float(emotion_value)
                    value = max(0.0, min(1.0, value))
                    if emotion_key not in input_ranges:
                        input_ranges[emotion_key] = [value, value]  # [min, max]
                    else:
                        input_ranges[emotion_key][0] = min(input_ranges[emotion_key][0], value)
                        input_ranges[emotion_key][1] = max(input_ranges[emotion_key][1], value)
                except (ValueError, TypeError):
                    continue

    # Validate aggregated values are within input ranges
    for emotion_key, aggregated_value in aggregated.items():
        if emotion_key in input_ranges:
            min_input, max_input = input_ranges[emotion_key]
            if not (min_input <= aggregated_value <= max_input):
                return False

    return True

def get_mesh_config() -> Dict[str, Any]:
    """Get current mesh configuration."""
    return {
        "enabled": ENABLED,
        "aggregation_method": AGGREGATION_METHOD,
        "min_agents": MIN_AGENTS,
        "valid_methods": ["mean", "median", "max", "min"]
    }