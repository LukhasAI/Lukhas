"""
Cross-dream resonance modeling (opt-in).
Maintains emotional continuity across dream selections.
"""
import os, math
from typing import Dict, Optional

ENABLED = os.getenv("LUKHAS_DREAM_RESONANCE", "0") == "1"
DECAY = float(os.getenv("LUKHAS_RESONANCE_DECAY", "0.9"))

class ResonanceField:
    """
    Maintains emotional resonance across dream selections.

    Safety guarantees:
    - Disabled by default
    - Decay factor prevents runaway amplification
    - Values always clamped to [0,1] range
    """

    def __init__(self):
        self.last_vector: Optional[Dict[str, float]] = None
        self.history: list = []  # For debugging/analysis

    def apply(self, em: Dict[str, float]) -> Dict[str, float]:
        """
        Apply resonance blending to emotion vector.

        Args:
            em: Current emotion vector

        Returns:
            Blended emotion vector with resonance from previous selection
        """
        if not ENABLED or self.last_vector is None:
            self.last_vector = em.copy()
            self._record_history(em, em, "initial")
            return em

        # Blend with previous vector using decay factor
        blended = {}
        for k in em.keys():
            # Weighted blend: decay * previous + (1-decay) * current
            previous_value = self.last_vector.get(k, 0.0)
            current_value = em.get(k, 0.0)
            blended_value = DECAY * previous_value + (1.0 - DECAY) * current_value

            # Ensure value stays in valid range
            blended[k] = max(0.0, min(1.0, blended_value))

        self.last_vector = blended.copy()
        self._record_history(em, blended, "resonance")
        return blended

    def _record_history(self, original: Dict[str, float], blended: Dict[str, float], event_type: str):
        """Record history for debugging/analysis."""
        if len(self.history) > 100:  # Limit history size
            self.history.pop(0)

        self.history.append({
            "type": event_type,
            "original": original.copy(),
            "blended": blended.copy(),
            "decay_factor": DECAY,
            "enabled": ENABLED
        })

    def reset(self):
        """Reset resonance field state."""
        self.last_vector = None
        self.history.clear()

    def get_state(self) -> Dict[str, any]:
        """Get current resonance field state for debugging."""
        return {
            "enabled": ENABLED,
            "decay_factor": DECAY,
            "has_previous": self.last_vector is not None,
            "last_vector": self.last_vector.copy() if self.last_vector else None,
            "history_length": len(self.history)
        }

    def validate_resonance(self, original: Dict[str, float], resonant: Dict[str, float]) -> bool:
        """
        Validate that resonance application maintains safety constraints.

        Returns True if output is safe, False otherwise.
        """
        if not ENABLED:
            return original == resonant

        # Check same keys
        if set(original.keys()) != set(resonant.keys()):
            return False

        # Check value ranges
        for k, v in resonant.items():
            if not (0.0 <= v <= 1.0):
                return False

        # Check decay behavior if we have previous vector
        if self.last_vector is not None:
            for k in original.keys():
                expected_min = min(original[k], self.last_vector.get(k, 0.0))
                expected_max = max(original[k], self.last_vector.get(k, 0.0))

                # Resonant value should be between original and previous
                if not (expected_min <= resonant[k] <= expected_max):
                    return False

        return True

def create_resonance_field() -> ResonanceField:
    """Factory function to create resonance field."""
    return ResonanceField()

def get_resonance_config() -> Dict[str, any]:
    """Get current resonance configuration."""
    return {
        "enabled": ENABLED,
        "decay_factor": DECAY,
        "safe_range": DECAY >= 0.1 and DECAY <= 0.99  # Reasonable decay range
    }

def simulate_resonance_decay(initial_value: float, steps: int) -> list[float]:
    """
    Simulate resonance decay over time for analysis.

    Args:
        initial_value: Starting emotion value
        steps: Number of steps to simulate

    Returns:
        List of values showing decay progression
    """
    if not ENABLED:
        return [initial_value] * steps

    values = [initial_value]
    current = initial_value

    for _ in range(steps - 1):
        # Simulate no new input (value = 0) to see pure decay
        current = DECAY * current + (1.0 - DECAY) * 0.0
        values.append(current)

    return values