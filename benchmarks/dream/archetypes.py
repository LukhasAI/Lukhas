"""
Archetypal Taxonomy for Dream System Analysis.
Classifies emotional patterns using Jungian archetypal categories.
"""
import statistics
from typing import Any, Dict, List, Tuple

# Archetypal emotion mappings based on Jungian psychology
ARCHETYPES = {
    "hero": {
        "primary_emotions": ["confidence", "joy", "curiosity"],
        "secondary_emotions": ["trust"],
        "opposed_emotions": ["fear", "sadness"],
        "description": "Confident, optimistic, forward-moving energy"
    },
    "shadow": {
        "primary_emotions": ["fear", "anger", "sadness"],
        "secondary_emotions": ["surprise"],
        "opposed_emotions": ["confidence", "joy", "trust"],
        "description": "Dark, repressed, or negative emotional aspects"
    },
    "trickster": {
        "primary_emotions": ["surprise", "curiosity"],
        "secondary_emotions": ["joy"],
        "opposed_emotions": ["sadness", "fear"],
        "description": "Playful, unpredictable, transformative energy"
    },
    "sage": {
        "primary_emotions": ["confidence", "curiosity", "trust"],
        "secondary_emotions": [],
        "opposed_emotions": ["anger", "fear"],
        "description": "Wise, knowing, contemplative energy"
    },
    "innocent": {
        "primary_emotions": ["joy", "trust", "surprise"],
        "secondary_emotions": ["curiosity"],
        "opposed_emotions": ["anger", "sadness"],
        "description": "Pure, optimistic, trusting energy"
    },
    "explorer": {
        "primary_emotions": ["curiosity", "confidence"],
        "secondary_emotions": ["surprise", "joy"],
        "opposed_emotions": ["fear", "sadness"],
        "description": "Adventurous, seeking, boundary-pushing energy"
    },
    "caregiver": {
        "primary_emotions": ["trust", "joy"],
        "secondary_emotions": ["confidence"],
        "opposed_emotions": ["anger", "fear"],
        "description": "Nurturing, protective, empathetic energy"
    },
    "warrior": {
        "primary_emotions": ["confidence", "anger"],
        "secondary_emotions": ["surprise"],
        "opposed_emotions": ["fear", "sadness"],
        "description": "Fierce, determined, combative energy"
    },
    "lover": {
        "primary_emotions": ["joy", "trust"],
        "secondary_emotions": ["surprise", "curiosity"],
        "opposed_emotions": ["anger", "sadness"],
        "description": "Passionate, connecting, emotional energy"
    },
    "rebel": {
        "primary_emotions": ["anger", "surprise"],
        "secondary_emotions": ["confidence"],
        "opposed_emotions": ["trust", "fear"],
        "description": "Revolutionary, disruptive, transforming energy"
    }
}

# Canonical emotion keys for consistency
CANONICAL_EMOTIONS = ["confidence", "curiosity", "joy", "fear", "anger", "sadness", "surprise", "trust"]

def classify_archetype(emotion_vector: Dict[str, float], threshold: float = 0.6) -> List[Tuple[str, float]]:
    """
    Classify emotional vector into archetypal categories.

    Args:
        emotion_vector: Dictionary of emotion names to values (0.0-1.0)
        threshold: Minimum score to consider an archetype match

    Returns:
        List of (archetype_name, score) tuples, sorted by score descending
    """
    archetype_scores = []

    for archetype_name, archetype_data in ARCHETYPES.items():
        score = calculate_archetype_score(emotion_vector, archetype_data)
        if score >= threshold:
            archetype_scores.append((archetype_name, score))

    # Sort by score descending
    archetype_scores.sort(key=lambda x: x[1], reverse=True)
    return archetype_scores

def calculate_archetype_score(emotion_vector: Dict[str, float], archetype_data: Dict[str, Any]) -> float:
    """
    Calculate how well an emotion vector matches an archetype.

    Args:
        emotion_vector: Dictionary of emotion names to values
        archetype_data: Archetype definition with primary/secondary/opposed emotions

    Returns:
        Score between 0.0 and 1.0 indicating match strength
    """
    # Normalize emotion vector to canonical keys
    normalized_emotions = {}
    for emotion in CANONICAL_EMOTIONS:
        normalized_emotions[emotion] = emotion_vector.get(emotion, 0.0)

    # Calculate component scores
    primary_score = 0.0
    secondary_score = 0.0
    opposition_penalty = 0.0

    # Primary emotions (weighted heavily)
    primary_emotions = archetype_data.get("primary_emotions", [])
    if primary_emotions:
        primary_values = [normalized_emotions[emotion] for emotion in primary_emotions]
        primary_score = statistics.mean(primary_values) * 0.6

    # Secondary emotions (moderate weight)
    secondary_emotions = archetype_data.get("secondary_emotions", [])
    if secondary_emotions:
        secondary_values = [normalized_emotions[emotion] for emotion in secondary_emotions]
        secondary_score = statistics.mean(secondary_values) * 0.3

    # Opposition penalty (reduces score for conflicting emotions)
    opposed_emotions = archetype_data.get("opposed_emotions", [])
    if opposed_emotions:
        opposed_values = [normalized_emotions[emotion] for emotion in opposed_emotions]
        opposition_penalty = statistics.mean(opposed_values) * 0.2

    # Calculate final score
    total_score = primary_score + secondary_score - opposition_penalty
    return max(0.0, min(1.0, total_score))

def analyze_snapshot_archetypes(snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze archetypal patterns in a collection of snapshots.

    Args:
        snapshots: List of snapshot dictionaries with emotional_context

    Returns:
        Analysis dictionary with archetypal statistics
    """
    snapshot_archetypes = []
    archetype_frequencies = {name: 0 for name in ARCHETYPES.keys()}
    archetype_scores = {name: [] for name in ARCHETYPES.keys()}

    for snapshot in snapshots:
        if "emotional_context" not in snapshot:
            continue

        emotion_vector = snapshot["emotional_context"]
        if not isinstance(emotion_vector, dict):
            continue

        # Classify this snapshot
        classifications = classify_archetype(emotion_vector, threshold=0.4)

        snapshot_analysis = {
            "snapshot_name": snapshot.get("name", "unknown"),
            "archetypes": classifications,
            "dominant_archetype": classifications[0] if classifications else None
        }
        snapshot_archetypes.append(snapshot_analysis)

        # Update frequency counts and scores
        for archetype_name, score in classifications:
            archetype_frequencies[archetype_name] += 1
            archetype_scores[archetype_name].append(score)

    # Calculate aggregate statistics
    total_snapshots = len(snapshot_archetypes)

    archetype_stats = {}
    for archetype_name in ARCHETYPES.keys():
        frequency = archetype_frequencies[archetype_name]
        scores = archetype_scores[archetype_name]

        archetype_stats[archetype_name] = {
            "frequency": frequency,
            "percentage": frequency / total_snapshots if total_snapshots > 0 else 0.0,
            "avg_score": statistics.mean(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "description": ARCHETYPES[archetype_name]["description"]
        }

    # Find dominant archetypes
    dominant_archetypes = sorted(
        archetype_stats.items(),
        key=lambda x: x[1]["frequency"],
        reverse=True
    )[:3]

    return {
        "total_snapshots": total_snapshots,
        "snapshot_archetypes": snapshot_archetypes,
        "archetype_statistics": archetype_stats,
        "dominant_archetypes": dominant_archetypes,
        "diversity_index": calculate_archetypal_diversity(archetype_frequencies)
    }

def calculate_archetypal_diversity(frequencies: Dict[str, int]) -> float:
    """
    Calculate Shannon diversity index for archetypal distribution.

    Args:
        frequencies: Dictionary of archetype names to frequency counts

    Returns:
        Diversity index (0.0 = no diversity, higher = more diverse)
    """
    total = sum(frequencies.values())
    if total == 0:
        return 0.0

    # Calculate Shannon entropy
    entropy = 0.0
    for frequency in frequencies.values():
        if frequency > 0:
            proportion = frequency / total
            entropy -= proportion * (proportion ** 0.5)  # Simplified diversity measure

    return entropy

def suggest_archetypal_balance(current_stats: Dict[str, Any], target_balance: str = "balanced") -> Dict[str, Any]:
    """
    Suggest improvements for archetypal balance in dream system.

    Args:
        current_stats: Current archetypal statistics from analyze_snapshot_archetypes
        target_balance: Desired balance type ("balanced", "heroic", "exploratory", etc.)

    Returns:
        Recommendations for improving archetypal balance
    """
    recommendations = []
    target_distributions = {
        "balanced": {name: 1.0 / len(ARCHETYPES) for name in ARCHETYPES.keys()},
        "heroic": {"hero": 0.4, "explorer": 0.2, "warrior": 0.2, "sage": 0.1, "innocent": 0.1},
        "exploratory": {"explorer": 0.3, "trickster": 0.2, "hero": 0.2, "sage": 0.15, "innocent": 0.15},
        "nurturing": {"caregiver": 0.3, "innocent": 0.2, "lover": 0.2, "sage": 0.15, "hero": 0.15},
        "transformative": {"trickster": 0.25, "rebel": 0.25, "warrior": 0.2, "hero": 0.15, "explorer": 0.15}
    }

    target_dist = target_distributions.get(target_balance, target_distributions["balanced"])
    current_dist = {
        name: stats["percentage"]
        for name, stats in current_stats["archetype_statistics"].items()
    }

    # Identify over/under-represented archetypes
    for archetype_name, target_pct in target_dist.items():
        current_pct = current_dist.get(archetype_name, 0.0)
        difference = target_pct - current_pct

        if abs(difference) > 0.05:  # 5% threshold
            if difference > 0:
                recommendations.append({
                    "action": "increase",
                    "archetype": archetype_name,
                    "current_percentage": current_pct,
                    "target_percentage": target_pct,
                    "difference": difference,
                    "primary_emotions": ARCHETYPES[archetype_name]["primary_emotions"],
                    "suggestion": f"Increase {archetype_name} representation by emphasizing {', '.join(ARCHETYPES[archetype_name]['primary_emotions'])}"
                })
            else:
                recommendations.append({
                    "action": "decrease",
                    "archetype": archetype_name,
                    "current_percentage": current_pct,
                    "target_percentage": target_pct,
                    "difference": difference,
                    "suggestion": f"Reduce {archetype_name} over-representation"
                })

    return {
        "target_balance": target_balance,
        "current_diversity": current_stats["diversity_index"],
        "recommendations": recommendations,
        "overall_balance_score": calculate_balance_score(current_dist, target_dist)
    }

def calculate_balance_score(current: Dict[str, float], target: Dict[str, float]) -> float:
    """
    Calculate how well current distribution matches target.

    Returns:
        Score between 0.0 and 1.0 (1.0 = perfect match)
    """
    total_error = 0.0
    for archetype in target.keys():
        current_val = current.get(archetype, 0.0)
        target_val = target.get(archetype, 0.0)
        total_error += abs(current_val - target_val)

    # Convert error to score (lower error = higher score)
    max_possible_error = 2.0  # Maximum possible sum of absolute differences
    balance_score = 1.0 - (total_error / max_possible_error)
    return max(0.0, balance_score)

def create_archetypal_test_case(archetype_name: str, intensity: float = 0.8) -> Dict[str, Any]:
    """
    Create a test case that strongly represents a specific archetype.

    Args:
        archetype_name: Name of archetype to create
        intensity: How strongly to express the archetype (0.0-1.0)

    Returns:
        Test case dictionary with emotional context
    """
    if archetype_name not in ARCHETYPES:
        raise ValueError(f"Unknown archetype: {archetype_name}")

    archetype_data = ARCHETYPES[archetype_name]
    emotion_vector = {}

    # Initialize all emotions to baseline
    for emotion in CANONICAL_EMOTIONS:
        emotion_vector[emotion] = 0.3

    # Enhance primary emotions
    for emotion in archetype_data["primary_emotions"]:
        emotion_vector[emotion] = intensity

    # Moderate enhancement for secondary emotions
    for emotion in archetype_data["secondary_emotions"]:
        emotion_vector[emotion] = intensity * 0.6

    # Reduce opposed emotions
    for emotion in archetype_data["opposed_emotions"]:
        emotion_vector[emotion] = max(0.0, 0.3 - intensity * 0.4)

    return {
        "name": f"{archetype_name}_test_case",
        "emotional_context": emotion_vector,
        "timestamp": 100.0,
        "content": f"Test case for {archetype_name} archetype",
        "metadata": {
            "archetype": archetype_name,
            "intensity": intensity,
            "synthetic": True
        }
    }

if __name__ == "__main__":
    # Example usage and validation
    print("Archetypal Taxonomy System")
    print("=" * 30)

    # Test archetype classification
    test_emotion = {
        "confidence": 0.9,
        "joy": 0.8,
        "curiosity": 0.7,
        "fear": 0.1,
        "anger": 0.0,
        "sadness": 0.1,
        "surprise": 0.4,
        "trust": 0.6
    }

    classifications = classify_archetype(test_emotion)
    print("Test emotion vector classifications:")
    for archetype, score in classifications:
        print(f"  {archetype}: {score:.3f}")

    # Generate test cases for all archetypes
    print("\nGenerated archetypal test cases:")
    for archetype_name in ARCHETYPES.keys():
        test_case = create_archetypal_test_case(archetype_name)
        classifications = classify_archetype(test_case["emotional_context"])
        top_match = classifications[0] if classifications else ("none", 0.0)
        print(f"  {archetype_name}: top match = {top_match[0]} ({top_match[1]:.3f})")

    print(f"\nArchetypal system ready with {len(ARCHETYPES)} archetypes.")
