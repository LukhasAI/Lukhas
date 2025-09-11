#!/usr/bin/env python3
"""
LUKHAS Endocrine System Demonstration
Shows how the hormone system modulates system behavior
"""

import asyncio
import os
import sys

from lukhas.core.endocrine import get_endocrine_system

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def demonstrate_endocrine_system():
    """Demonstrate the endocrine system capabilities"""
    print("=" * 60)
    print("LUKHAS ENDOCRINE SYSTEM DEMONSTRATION")
    print("=" * 60)

    system = get_endocrine_system()

    # 1. Show initial hormone levels
    print("\n🧪 Initial Hormone Levels:")
    initial_levels = system.get_hormone_levels()
    for hormone, level in initial_levels.items():
        print(f"  {hormone}: {level:.2f}")

    # 2. Show initial profile
    print("\n📊 Initial System Profile:")
    profile = system.get_hormone_profile()
    print(f"  State: {profile['dominant_state']}")
    print(f"  Summary: {profile['summary']}")

    # 3. Simulate stress event
    print("\n⚡ Simulating Stress Event (intensity: 0.7)")
    system.trigger_stress_response(0.7)

    # Show immediate hormone changes
    stress_levels = system.get_hormone_levels()
    print("\n  Hormone changes:")
    print(f"    Cortisol: {initial_levels['cortisol']:.2f} → {stress_levels['cortisol']:.2f}")
    print(f"    Adrenaline: {initial_levels['adrenaline']:.2f} → {stress_levels['adrenaline']:.2f}")

    # Show effects
    effects = system._calculate_effects()
    print("\n  System effects:")
    print(f"    Stress level: {effects['stress_level']:.2f}")
    print(f"    Alertness: {effects['alertness']:.2f}")
    print(f"    Neuroplasticity: {effects['neuroplasticity']:.2f}")

    # 4. Start the system for continuous updates
    print("\n🔄 Starting endocrine system...")
    await system.start()

    # Let stress hormones affect the system
    await asyncio.sleep(2.0)

    # 5. Show how stress affects mood hormones
    print("\n😰 After 2 seconds of stress:")
    current_profile = system.get_hormone_profile()
    print(f"  State: {current_profile['dominant_state']}")
    print(f"  Mood valence: {current_profile['effects']['mood_valence']:.2f}")
    print(f"  Emotional stability: {current_profile['effects']['emotional_stability']:.2f}")

    # 6. Trigger social bonding to counteract stress
    print("\n🤝 Triggering Social Bonding (intensity: 0.6)")
    system.trigger_social_bonding(0.6)

    await asyncio.sleep(1.0)

    bonding_profile = system.get_hormone_profile()
    print(f"\n  New state: {bonding_profile['dominant_state']}")
    print(f"  Oxytocin level: {bonding_profile['levels']['oxytocin']:.2f}")
    print(f"  Social engagement: {bonding_profile['effects']['social_engagement']:.2f}")
    print(f"  Trust level: {bonding_profile['effects']['trust_level']:.2f}")

    # 7. Simulate task completion with reward
    print("\n🎉 Task Completed - Triggering Reward (intensity: 0.8)")
    system.trigger_reward_response(0.8)

    await asyncio.sleep(1.0)

    reward_profile = system.get_hormone_profile()
    print(f"\n  Dopamine level: {reward_profile['levels']['dopamine']:.2f}")
    print(f"  Motivation: {reward_profile['effects']['motivation']:.2f}")
    print(f"  Summary: {reward_profile['summary']}")

    # 8. Prepare for rest
    print("\n😴 End of Day - Triggering Rest Cycle (intensity: 0.7)")
    system.trigger_rest_cycle(0.7)

    await asyncio.sleep(1.0)

    rest_profile = system.get_hormone_profile()
    print(f"\n  Melatonin level: {rest_profile['levels']['melatonin']:.2f}")
    print(f"  GABA level: {rest_profile['levels']['gaba']:.2f}")
    print(f"  Processing speed: {rest_profile['effects']['processing_speed']:.2f}")
    print(f"  Rest need: {rest_profile['effects']['rest_need']:.2f}")

    # 9. Show neuroplasticity throughout the day
    print("\n🧠 Neuroplasticity Analysis:")
    print(f"  Current neuroplasticity: {rest_profile['effects']['neuroplasticity']:.2f}")
    print("  Factors affecting neuroplasticity:")
    print(f"    - Stress (cortisol): {rest_profile['levels']['cortisol']:.2f} (inhibits)")
    print(f"    - Mood (dopamine/serotonin): {rest_profile['effects']['mood_valence']:.2f} (enhances)")
    print(f"    - Rest (melatonin): {rest_profile['levels']['melatonin']:.2f} (crucial)")

    # 10. Show effect history
    print("\n📜 Effect History:")
    for i, event in enumerate(system.effect_history[-5:], 1):
        print(f"  {i}. {event['type']} (intensity: {event['intensity']})")
        print(f"     Hormones affected: {', '.join(event['hormones_affected'])}")

    # Stop the system
    await system.stop()
    print("\n🛑 Endocrine system stopped")

    # Final summary
    print("\n" + "=" * 60)
    print("The endocrine system provides biological-style behavioral")
    print("modulation through hormone interactions, affecting:")
    print("- Stress response and adaptation")
    print("- Mood and motivation")
    print("- Social bonding and trust")
    print("- Learning capacity (neuroplasticity)")
    print("- Rest and recovery cycles")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demonstrate_endocrine_system())
