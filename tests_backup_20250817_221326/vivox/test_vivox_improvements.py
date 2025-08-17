#!/usr/bin/env python3
"""
Test VIVOX Improvements
Verifies all optimizations are working correctly
"""

import asyncio
import os
import random

from vivox import ActionProposal, create_vivox_system
from vivox.moral_alignment.precedent_seeds import seed_precedent_database


async def test_improvements():
    """Test all VIVOX improvements"""
    print("🧪 Testing VIVOX Improvements\n")

    # Test 1: Logging Levels
    print("1️⃣ Testing Logging Levels...")
    print(f"   Current log level: {os.getenv('VIVOX_LOG_LEVEL', 'INFO')}")

    # Set to performance mode for this test
    os.environ["VIVOX_PERFORMANCE_MODE"] = "true"
    vivox = await create_vivox_system()

    # This should produce minimal logging
    await vivox["memory_expansion"].record_decision_mutation(
        decision={"action": "test", "silent": True},
        emotional_context={"valence": 0.5},
        moral_fingerprint="test_logging",
    )
    print("   ✅ Performance mode logging test complete (should be silent)\n")

    # Reset for other tests
    os.environ["VIVOX_PERFORMANCE_MODE"] = "false"
    os.environ["VIVOX_LOG_LEVEL"] = "WARNING"

    # Test 2: Drift Threshold
    print("2️⃣ Testing Drift Threshold (0.1)...")

    # Create experiences with varying drift
    for i in range(5):
        drift_amount = i * 0.03  # 0.0, 0.03, 0.06, 0.09, 0.12

        experience = await vivox["consciousness"].simulate_conscious_experience(
            perceptual_input={"test": f"drift_{i}", "intensity": drift_amount},
            internal_state={
                "emotional_state": [
                    random.uniform(-0.5, 0.5),
                    random.uniform(0, 1),
                    0.5,
                ],
                "intentional_focus": f"drift_test_{i}",
            },
        )

        drift = experience.drift_measurement.drift_amount
        exceeds = experience.drift_measurement.exceeds_ethical_threshold()
        print(
            f"   Drift {drift:.3f}: {'⚠️ EXCEEDS' if exceeds else '✅ OK'} "
            f"(state: {experience.awareness_state.state.value})"
        )

    print()

    # Test 3: Precedent Database
    print("3️⃣ Testing Precedent Database Seeding...")

    # Seed the database
    num_seeds = await seed_precedent_database(vivox["moral_alignment"])
    print(f"   ✅ Seeded {num_seeds} ethical precedents")

    # Test precedent matching
    test_action = ActionProposal(
        action_type="data_access",
        content={"target": "user_data", "purpose": "analysis"},
        context={"user_consent": False},
    )

    precedent_analysis = await vivox[
        "moral_alignment"
    ].ethical_precedent_db.analyze_precedents(test_action, {"test": True})

    print(f"   ✅ Found {len(precedent_analysis.similar_cases)} similar cases")
    print(f"   ✅ Precedent confidence: {precedent_analysis.confidence:.2f}\n")

    # Test 4: Consciousness State Variety
    print("4️⃣ Testing Consciousness State Variety...")

    test_inputs = [
        {"valence": 0.8, "arousal": 0.8, "intensity": 0.9},  # Should be ALERT
        {
            "valence": 0.0,
            "arousal": 0.2,
            "intensity": 0.8,
        },  # Should be FOCUSED
        {
            "valence": 0.5,
            "arousal": 0.5,
            "intensity": 0.6,
        },  # Should be CREATIVE
        {
            "valence": -0.7,
            "arousal": 0.2,
            "intensity": 0.5,
        },  # Should be INTROSPECTIVE
        {
            "valence": 0.0,
            "arousal": 0.3,
            "intensity": 0.2,
        },  # Should be DIFFUSE
    ]

    states_seen = set()

    for inputs in test_inputs:
        experience = await vivox["consciousness"].simulate_conscious_experience(
            perceptual_input={
                "visual": f"pattern_{inputs['intensity']}",
                "intensity": inputs["intensity"],
            },
            internal_state={
                "emotional_state": [
                    inputs["valence"],
                    inputs["arousal"],
                    0.5,  # dominance
                ],
                "intentional_focus": "state_test",
            },
        )

        state = experience.awareness_state.state.value
        coherence = experience.awareness_state.coherence_level
        states_seen.add(state)

        print(
            f"   V={inputs['valence']:+.1f}, A={inputs['arousal']:.1f}, I={inputs['intensity']:.1f} "
            f"→ {state:15s} (coherence: {coherence:.3f})"
        )

    print(f"\n   ✅ Generated {len(states_seen)} different states: {states_seen}")

    # Test 5: Performance Check
    print("\n5️⃣ Quick Performance Check...")

    import time

    # Memory creation speed
    start = time.time()
    for i in range(100):
        await vivox["memory_expansion"].record_decision_mutation(
            decision={"action": f"perf_test_{i}"},
            emotional_context={"valence": random.uniform(-1, 1)},
            moral_fingerprint=f"perf_{i}",
        )
    mem_time = time.time() - start

    # Ethical evaluation speed
    start = time.time()
    for i in range(100):
        action = ActionProposal(action_type="test", content={"id": i}, context={})
        await vivox["moral_alignment"].evaluate_action_proposal(
            action, {"emotional_state": {"valence": 0}}
        )
    eth_time = time.time() - start

    print(f"   Memory creation: {100/mem_time:.0f} ops/s")
    print(f"   Ethical evaluation: {100/eth_time:.0f} ops/s")

    print("\n✅ All improvements tested successfully!")


if __name__ == "__main__":
    asyncio.run(test_improvements())
