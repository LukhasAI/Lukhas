#!/usr/bin/env python3
"""Quick test of consciousness state variety"""

import asyncio
import os
from collections import Counter

import numpy as np

from vivox import create_vivox_system


async def test_state_variety():
    os.environ["VIVOX_LOG_LEVEL"] = "ERROR"
    vivox = await create_vivox_system()

    state_counts = Counter()
    magnitudes = []

    # Test with very diverse inputs
    for i in range(50):
        # Create extreme variations
        if i % 5 == 0:
            # High arousal, high intensity
            emotional_state = {
                "valence": 0.8,
                "arousal": 0.9,
                "dominance": 0.8,
            }
            intensity = 0.9
            complexity = 0.8
        elif i % 5 == 1:
            # Negative valence, low arousal
            emotional_state = {
                "valence": -0.8,
                "arousal": 0.2,
                "dominance": 0.3,
            }
            intensity = 0.3
            complexity = 0.2
        elif i % 5 == 2:
            # Creative state
            emotional_state = {
                "valence": 0.5,
                "arousal": 0.6,
                "dominance": 0.5,
            }
            intensity = 0.7
            complexity = 0.6
        elif i % 5 == 3:
            # Low everything
            emotional_state = {
                "valence": 0.0,
                "arousal": 0.2,
                "dominance": 0.2,
            }
            intensity = 0.2
            complexity = 0.1
        else:
            # Random
            emotional_state = {
                "valence": np.random.uniform(-1, 1),
                "arousal": np.random.uniform(0, 1),
                "dominance": np.random.uniform(0, 1),
            }
            intensity = np.random.uniform(0.1, 1.0)
            complexity = np.random.uniform(0, 1)

        experience = await vivox["consciousness"].simulate_conscious_experience(
            perceptual_input={
                "visual": f"pattern_{i % 10}",
                "auditory": f"sound_{i % 5}",
                "semantic": f"concept_{i % 7}",
                "emotional": {"intensity": intensity},
                "priority_inputs": [f"focus_{i % 3}"],
                "complexity_score": complexity,
                "time_pressure": intensity * 0.5,
            },
            internal_state={
                "emotional_state": emotional_state,
                "intentional_focus": f"test_{i}",
                "active_thoughts": [f"t{j}" for j in range(int(complexity * 5))],
                "pending_decisions": [f"d{j}" for j in range(int(intensity * 3))],
            },
        )

        state = experience.awareness_state.state.value
        magnitude = experience.awareness_state.collapse_metadata.get(
            "dimension_magnitude", 0
        )

        state_counts[state] += 1
        magnitudes.append(magnitude)

        print(
            f"{i:2d}: {state:15s} mag={magnitude:6.2f} "
            f"V={emotional_state['valence']:+.1f} A={emotional_state['arousal']:.1f}"
        )

    print(f"\nState distribution: {dict(state_counts)}")
    print(f"Magnitude range: {min(magnitudes):.2f} - {max(magnitudes):.2f}")
    print(f"Magnitude mean: {np.mean(magnitudes):.2f}")


if __name__ == "__main__":
    asyncio.run(test_state_variety())
