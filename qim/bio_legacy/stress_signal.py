"""
Symbolic Mood Regulator: Stress Signal
----------------------------------------

Inspired by: Cortisol
Function: Alerts during high symbolic drift
Triggers: High drift, unexpected errors, negative feedback
Suppresses: Calm, relaxation

# ΛTAG: hormone, symbolic-regulation, mood, drift
# ΛMODULE: inner_rhythm
# ΛORIGIN_AGENT: Jules-04
"""


# LUKHAS_TAG: hormonal_feedback
class StressSignal:
    """Represents the symbolic hormone Cortisol."""

    def __init__(self, level: float = 0.5):
        self.level = level

    def __repr__(self):
        return f"StressSignal(level={self.level})"


def weight_modulator(
    signal_type: str, affect_vector: dict[str, float]
) -> dict[str, float]:
    """
    Modulates the weights of the symbolic hormones based on the signal type and affect vector.

    Args:
        signal_type: The type of signal.
        affect_vector: A dictionary of affect signals and their intensities.

    Returns:
        A dictionary of the modulated hormone weights.
    """
    weights = {
        "stress": 0.5,
    }

    if signal_type == "drift":
        weights["stress"] += affect_vector.get("drift", 0.0) * 0.1

    return weights
