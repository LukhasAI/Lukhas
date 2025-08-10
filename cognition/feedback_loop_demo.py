#!/usr/bin/env python3
"""
Symbolic Feedback Loop Demo
Demonstrates the cognitive backbone of LUKHΛS in action
"""

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cognition.symbolic_feedback_loop import SymbolicFeedbackLoop
from orchestration.symbolic_kernel_bus import kernel_bus


async def simulate_system_activity(loop: SymbolicFeedbackLoop):
    """
    Simulate various system activities that affect the feedback loop
    """
    print("\n🎭 Starting system activity simulation...")

    # Scenario 1: Normal dream cycle
    print("\n💭 Scenario 1: Normal dream cycle")
    dream_data = {
        "dream_id": "dream_normal_001",
        "timestamp": time.time(),
        "emotional_valence": 0.3,
        "symbols": ["⚛️", "🧠", "💭", "🌟", "✨"],
        "coherence": 0.75,
        "themes": ["exploration", "learning", "connection"],
        "insights": [
            "Pattern recognition improving",
            "Emotional balance stable",
            "Memory consolidation effective",
        ],
    }

    # Save dream
    dream_file = loop.dream_path / "last_dream.json"
    with open(dream_file, "w") as f:
        json.dump(dream_data, f)

    print("  ✅ Normal dream saved")
    await asyncio.sleep(1)

    # Scenario 2: Emotional turbulence
    print("\n😰 Scenario 2: Emotional turbulence detected")
    loop.current_state.dream_emotional_valence = -0.7
    loop.current_state.entropy_level = 0.8

    turbulent_dream = {
        "dream_id": "dream_turbulent_002",
        "timestamp": time.time(),
        "emotional_valence": -0.8,
        "symbols": ["🌊", "⚡", "🌀", "❄️"],
        "coherence": 0.4,
        "themes": ["chaos", "uncertainty", "transformation"],
        "insights": [
            "System under stress",
            "Need for stabilization",
            "Seeking equilibrium",
        ],
    }

    with open(dream_file, "w") as f:
        json.dump(turbulent_dream, f)

    print("  ⚠️ Turbulent emotional state induced")
    await asyncio.sleep(1)

    # Scenario 3: Ethical boundary approach
    print("\n🛡️ Scenario 3: Ethical boundary approached")
    loop.current_state.drift_score = 0.6
    loop.current_state.ethical_alignment = 0.5
    loop.current_state.guardian_trust = 0.6

    ethical_dream = {
        "dream_id": "dream_ethical_003",
        "timestamp": time.time(),
        "emotional_valence": 0.0,
        "symbols": ["🛡️", "⚖️", "🔒", "🪞"],
        "coherence": 0.9,
        "themes": ["responsibility", "boundaries", "reflection"],
        "insights": [
            "Ethical recalibration needed",
            "Guardian intervention suggested",
            "Self-reflection initiated",
        ],
    }

    with open(dream_file, "w") as f:
        json.dump(ethical_dream, f)

    print("  🚨 Ethical drift detected")
    await asyncio.sleep(1)

    # Scenario 4: Creative exploration
    print("\n🎨 Scenario 4: Creative exploration phase")
    loop.current_state.entropy_level = 0.3  # Too low, needs exploration
    loop.current_state.learning_rate = 0.05

    creative_dream = {
        "dream_id": "dream_creative_004",
        "timestamp": time.time(),
        "emotional_valence": 0.6,
        "symbols": ["🦋", "🌈", "🎭", "🌀", "💫"],
        "coherence": 0.6,
        "themes": ["creativity", "possibilities", "emergence"],
        "insights": [
            "New patterns emerging",
            "Creative potential unlocked",
            "Exploration beneficial",
        ],
    }

    with open(dream_file, "w") as f:
        json.dump(creative_dream, f)

    print("  🌈 Creative exploration triggered")
    await asyncio.sleep(1)

    # Scenario 5: Recovery and stabilization
    print("\n⚖️ Scenario 5: Recovery and stabilization")
    loop.current_state.drift_score = 0.2
    loop.current_state.ethical_alignment = 0.85
    loop.current_state.memory_coherence = 0.8
    loop.current_state.awareness_level = 0.75

    stable_dream = {
        "dream_id": "dream_stable_005",
        "timestamp": time.time(),
        "emotional_valence": 0.2,
        "symbols": ["⚛️", "🧠", "🛡️", "💎", "⚖️"],
        "coherence": 0.85,
        "themes": ["balance", "integration", "harmony"],
        "insights": [
            "System stabilized",
            "Coherence restored",
            "Optimal functioning achieved",
        ],
    }

    with open(dream_file, "w") as f:
        json.dump(stable_dream, f)

    print("  ✨ System stabilization achieved")


async def monitor_feedback_loop(loop: SymbolicFeedbackLoop, duration: int = 30):
    """
    Monitor the feedback loop for a specified duration
    """
    print(f"\n📊 Monitoring feedback loop for {duration} seconds...")
    print("=" * 60)

    start_time = time.time()
    cycle_count = 0

    while time.time() - start_time < duration:
        # Run a cycle
        results = await loop.run_cycle()
        cycle_count += 1

        # Display results
        print(f"\n🔄 Cycle {cycle_count} @ {time.time() - start_time:.1f}s")
        print(f"  📈 Stability: {results['stability']:.3f}")
        print(f"  📊 Convergence: {results['convergence_rate']:.3f}")
        print(f"  🌀 Entropy: {loop.current_state.entropy_level:.3f}")
        print(f"  💭 Awareness: {loop.current_state.awareness_level:.3f}")
        print(f"  🛡️ Ethics: {loop.current_state.ethical_alignment:.3f}")
        print(f"  📉 Drift: {loop.current_state.drift_score:.3f}")

        if results["drift_count"] > 0:
            print(f"  ⚠️ Drifts detected: {results['drift_count']}")

        if results["correction_count"] > 0:
            print(f"  🔧 Corrections applied: {results['correction_count']}")

            # Show recent corrections
            for correction in loop.correction_history[-3:]:
                print(f"    → {correction.directive.value}: {correction.rationale}")

        # Show active glyphs
        print(f"  🎯 Active glyphs: {' '.join(loop.current_state.active_glyphs[:5])}")

        # Wait before next cycle
        await asyncio.sleep(2)

    return cycle_count


async def main():
    """
    Main demo function
    """
    print("🔁 SYMBOLIC FEEDBACK LOOP DEMO")
    print("=" * 60)
    print("Demonstrating the cognitive backbone of LUKHΛS")
    print()

    # Create feedback loop with debug mode
    loop = SymbolicFeedbackLoop(
        memory_path="data/demo/memory", dream_path="data/demo/dreams", debug_mode=True
    )

    # Initialize kernel bus
    await kernel_bus.start()

    try:
        # Run simulation and monitoring in parallel
        simulation_task = asyncio.create_task(simulate_system_activity(loop))
        monitoring_task = asyncio.create_task(monitor_feedback_loop(loop, duration=20))

        # Wait for both to complete
        await simulation_task
        cycles = await monitoring_task

        # Final status
        print("\n" + "=" * 60)
        print("📊 FINAL STATUS")
        print("=" * 60)

        status = loop.get_status()
        print(f"Total cycles completed: {cycles}")
        print(f"Final stability score: {status['stability']:.3f}")
        print(f"Convergence rate: {status['convergence_rate']:.3f}")
        print(f"Oscillation count: {status['oscillation_count']}")
        print(f"Total drifts processed: {status['recent_drifts']}")
        print(f"Total corrections applied: {status['recent_corrections']}")

        # Check if system is stable
        is_stable = status["stability"] > 0.7 and status["convergence_rate"] > 0.6

        print(
            f"\n{'✅ System is STABLE' if is_stable else '⚠️ System needs more cycles for stability'}"
        )

        # Export final debug state
        if loop.debug_mode:
            loop.export_debug_state("demo_complete")
            print("\n📝 Debug states exported to data/debug/")

    finally:
        # Clean up
        await kernel_bus.stop()

    print("\n🎉 Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
