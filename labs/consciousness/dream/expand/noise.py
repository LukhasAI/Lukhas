"""
Noise injection for symbolic/emotional dream space.
Opt-in only: disabled by default for safety.
"""
import os
import random
from typing import Dict

LEVEL = os.getenv("LUKHAS_NOISE_LEVEL", "off")  # off|low|med|high
INTENSITY = {"low": 0.05, "med": 0.15, "high": 0.3}.get(LEVEL, 0.0)

def inject_noise(em: Dict[str, float]) -> Dict[str, float]:
    """
    Inject controlled noise into emotion vector.

    Safety guarantees:
    - Disabled by default (INTENSITY=0.0)
    - Values clamped to [0,1] range
    - Original dict unchanged
    """
    if INTENSITY <= 0:
        return em

    noisy_em = {}
    for k, v in em.items():
        noise = random.uniform(-INTENSITY, INTENSITY)
        noisy_value = v + noise
        # Clamp to valid range
        noisy_em[k] = max(0.0, min(1.0, noisy_value))

    return noisy_em

def get_noise_config() -> Dict[str, any]:
    """Get current noise configuration for debugging."""
    return {
        "level": LEVEL,
        "intensity": INTENSITY,
        "enabled": INTENSITY > 0
    }

def validate_noise_output(original: Dict[str, float], noisy: Dict[str, float]) -> bool:
    """
    Validate that noise injection maintains safety constraints.

    Returns True if output is safe, False otherwise.
    """
    # Check same keys
    if set(original.keys()) != set(noisy.keys()):
        return False

    # Check value ranges
    for k, v in noisy.items():
        if not (0.0 <= v <= 1.0):
            return False

        # Check noise is within expected bounds
        if INTENSITY > 0:
            max_change = INTENSITY
            if abs(v - original[k]) > max_change + 0.001:  # Small epsilon for float precision
                return False

    return True
