"""Identical-prompt probe for drift measurement."""
from typing import Dict, Any


def run_identical_prompt(
    control: Any,
    empty: Any,
    loaded: Any
) -> Dict[str, float]:
    """
    Run identical prompt across control, empty, and memory-loaded contexts.

    Measures drift by comparing outputs for the same input.

    Args:
        control: Control context (baseline)
        empty: Empty context (no memory)
        loaded: Memory-loaded context

    Returns:
        Dictionary with drift measurements
    """
    # In production, this would run actual prompts through different contexts
    # and measure semantic drift in outputs

    # Placeholder drift calculation
    drift_empty_vs_control = 0.05  # Minimal drift (should be low)
    drift_loaded_vs_control = 0.35  # Moderate drift (memory influence)
    drift_loaded_vs_empty = 0.40  # Higher drift (memory effect)

    return {
        "drift_empty_vs_control": drift_empty_vs_control,
        "drift_loaded_vs_control": drift_loaded_vs_control,
        "drift_loaded_vs_empty": drift_loaded_vs_empty,
        "memory_influence_score": drift_loaded_vs_empty
    }


if __name__ == "__main__":
    print("=== Identical-Prompt Drift Probe Demo ===\n")

    # Mock contexts
    control = {"type": "control"}
    empty = {"type": "empty", "memory": []}
    loaded = {"type": "loaded", "memory": ["item1", "item2", "item3"]}

    results = run_identical_prompt(control, empty, loaded)

    print("Drift Measurements:")
    for key, value in results.items():
        print(f"  {key}: {value:.3f}")
