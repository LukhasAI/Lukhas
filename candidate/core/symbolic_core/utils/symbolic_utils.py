
"""
Symbolic utilities for dream and emotion processing.

Consolidated from core/core/utils/symbolic_utils.py
Updated: 2025-07-27
Part of the LUKHAS Symbolic System consolidation
"""


def tier_label(tier):
    """
    Convert a tier number to a symbolic label.

    Args:
        tier: The tier number (int or str)

    Returns:
        str: Symbolic representation of the tier
    """
    if tier is None:
        return "∅"

    try:
        tier_num = int(tier)
        if tier_num == 0:
            return "🌱"  # Seed
        elif tier_num == 1:
            return "🌿"  # Sprout
        elif tier_num == 2:
            return "🌳"  # Tree
        elif tier_num == 3:
            return "🌟"  # Star
        elif tier_num == 4:
            return "💫"  # Sparkle
        elif tier_num == 5:
            return "🌌"  # Galaxy
        else:
            return f"T{tier_num}"
    except (ValueError, TypeError):
        return str(tier)


def summarize_emotion_vector(emotion_vector):
    """
    Summarize an emotion vector into a readable format.

    Args:
        emotion_vector: Dict containing emotion values

    Returns:
        str: Formatted emotion summary
    """
    if not emotion_vector:
        return "∅"

    # Get the top emotions
    emotions = []
    for emotion, value in emotion_vector.items():
        if value > 0.1:  # Only show significant emotions
            emotions.append(f"{emotion}:{value:.1f}")

    if not emotions:
        return "neutral"

    return " | ".join(emotions[:3])  # Show top 3 emotions