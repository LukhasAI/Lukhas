"""
Symbolic Mood Regulator: Curiosity Spark
----------------------------------------

Inspired by: Dopamine
Function: Drives exploration & anticipation
Triggers: Novelty, unexpected rewards, new information
Suppresses: Apathy, boredom

# ΛTAG: hormone, symbolic-regulation, mood, drift
# ΛMODULE: inner_rhythm
# ΛORIGIN_AGENT: Jules-04
"""

from typing import Dict

#LUKHAS_TAG: hormonal_feedback
class CuriositySpark:
    """Represents the symbolic hormone Dopamine."""
    def __init__(self, level: float = 0.5):
        self.level = level

    def __repr__(self):
        return f"CuriositySpark(level={self.level})"

def weight_modulator(signal_type: str, affect_vector: Dict[str, float]) -> Dict[str, float]:
    """
    Modulates the weights of the symbolic hormones based on the signal type and affect vector.

    Args:
        signal_type: The type of signal.
        affect_vector: A dictionary of affect signals and their intensities.

    Returns:
        A dictionary of the modulated hormone weights.
    """
    weights = {
        "curiosity": 0.5,
    }

    if signal_type == "novelty":
        weights["curiosity"] += affect_vector.get("novelty", 0.0) * 0.1

    return weights
