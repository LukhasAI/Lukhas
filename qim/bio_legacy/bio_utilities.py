"""
Consolidated module for better performance
"""

import random

from .bio_affect_model import SADNESS_THRESHOLD


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
    weights = {"stress": 0.5}
    if signal_type == "drift":
        weights["stress"] += affect_vector.get("drift", 0.0) * 0.1
    return weights


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
    weights = {"curiosity": 0.5}
    if signal_type == "novelty":
        weights["curiosity"] += affect_vector.get("novelty", 0.0) * 0.1
    return weights


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
    weights = {"resilience": 0.5}
    if signal_type == "recovery":
        weights["resilience"] += affect_vector.get("recovery", 0.0) * 0.1
    return weights


def fatigue_level() -> float:
    """Return the simulated cellular fatigue level between 0.0 and 1.0."""
    return random.uniform(0.0, 1.0)


def inject_narrative_repair(
    narrative: str, emotions: dict[str, float], *, threshold: float = SADNESS_THRESHOLD
) -> str:
    """Inject narrative repair elements if sadness exceeds threshold."""
    sadness = emotions.get("sadness", 0.0)
    if sadness > threshold:
        repair_phrase = " A healing warmth resolves lingering sorrow."
        return narrative + repair_phrase
    return narrative


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
    weights = {"stability": 0.5}
    if signal_type == "success":
        weights["stability"] += affect_vector.get("success", 0.0) * 0.1
    return weights


class StressSignal:
    """Represents the symbolic hormone Cortisol."""

    def __init__(self, level: float = 0.5):
        self.level = level

    def __repr__(self):
        return f"StressSignal(level={self.level})"


class CuriositySpark:
    """Represents the symbolic hormone Dopamine."""

    def __init__(self, level: float = 0.5):
        self.level = level

    def __repr__(self):
        return f"CuriositySpark(level={self.level})"


class ResilienceBoost:
    """Represents the symbolic hormone Endorphins."""

    def __init__(self, level: float = 0.5):
        self.level = level

    def __repr__(self):
        return f"ResilienceBoost(level={self.level})"


class ProteinSynthesizer:
    """Simple symbolic protein synthesizer."""

    def __init__(self, base_rate: float = 1.0):
        self.base_rate = base_rate

    async def synthesize(self, blueprint: dict[str, float]) -> dict[str, float]:
        """Synthesize proteins from a blueprint."""
        proteins = {
            name: amount * self.base_rate for (name, amount) in blueprint.items()
        }
        logger.debug(f"Synthesized proteins: {proteins}")
        return proteins


class StabilityAnchor:
    """Represents the symbolic hormone Serotonin."""

    def __init__(self, level: float = 0.5):
        self.level = level

    def __repr__(self):
        return f"StabilityAnchor(level={self.level})"
