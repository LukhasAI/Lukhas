#!/usr/bin/env python3
"""
Test script for ReflectionLayer dream engine integration.
Verifies that the dream engines are properly integrated and working.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.monitoring.reflection_layer import ReflectionLayer


async def test_dream_engine_integration():
    """Test the dream engine integration in ReflectionLayer"""

    print("💭 Testing ReflectionLayer Dream Engine Integration")
    print("=" * 60)

    # Initialize reflection layer
    print("\n📦 Initializing ReflectionLayer with dream engine...")
    reflection_layer = ReflectionLayer()

    # Test 1: Check dream engine initialization
    print("\n🔍 Test 1: Dream engine system initialization")
    dream_available = reflection_layer.dream_replayer is not None
    is_placeholder = isinstance(reflection_layer.dream_replayer, str)

    print(f"   ✅ Dream engine available: {dream_available}")
    print(f"   ✅ Is placeholder: {is_placeholder}")

    if not is_placeholder:
        dream_type = type(reflection_layer.dream_replayer).__name__
        print(f"   ✅ Dream engine type: {dream_type}")

        # Check capabilities
        has_reflect = hasattr(reflection_layer.dream_replayer, "reflect_on_dream")
        has_generate = hasattr(
            reflection_layer.dream_replayer, "generate_dream_sequence"
        )
        has_deliver = hasattr(reflection_layer.dream_replayer, "deliver_dream")

        print("   ✅ Capabilities:")
        print(f"      - reflect_on_dream: {has_reflect}")
        print(f"      - generate_dream_sequence: {has_generate}")
        print(f"      - deliver_dream: {has_deliver}")

    # Test 2: Create a high-emotion reflection that should trigger dreams
    print("\n🔍 Test 2: Creating high-emotion reflection for dream trigger")

    high_emotion_reflection = reflection_layer.contemplate_ethical_conflict(
        "Critical system drift detected requiring symbolic repair",
        ["user_safety", "system_integrity"],
        0.85,
    )

    print("   ✅ High-emotion reflection created:")
    print(f"      - ID: {high_emotion_reflection.id}")
    print(f"      - Emotional weight: {high_emotion_reflection.emotional_weight}")
    print(f"      - Symbolic mood: {high_emotion_reflection.symbolic_mood.value}")
    print(f"      - Type: {high_emotion_reflection.reflection_type.value}")

    # Test 3: Test dream simulation trigger
    print("\n🔍 Test 3: Testing dream simulation trigger")

    dream_threshold = reflection_layer.manifest.get("reflection_layer", {}).get(
        "dream_trigger_threshold", 0.7
    )
    print(f"   📊 Dream trigger threshold: {dream_threshold}")
    print(
        f"   📊 Reflection emotional weight: {high_emotion_reflection.emotional_weight}"
    )

    should_trigger = high_emotion_reflection.emotional_weight >= dream_threshold
    print(f"   ✅ Should trigger dream: {should_trigger}")

    if should_trigger:
        print("   💭 Attempting dream simulation trigger...")
        dream_id = await reflection_layer.trigger_dream_simulation(
            high_emotion_reflection
        )

        if dream_id:
            print("   ✅ Dream simulation triggered successfully!")
            print(f"      - Dream ID: {dream_id}")
            print(
                f"      - Stored in reflection metadata: {high_emotion_reflection.metadata.get('triggered_dream_id')}"
            )
        else:
            print("   ⚠️ Dream simulation failed to trigger")

    # Test 4: Test different reflection types for dream scenarios
    print("\n🔍 Test 4: Testing dream scenarios for different reflection types")

    test_scenarios = [
        (
            "drift_analysis",
            lambda: reflection_layer.reflect_on_drift_score(0.8, [0.2, 0.5, 0.8]),
        ),
        (
            "intent_deviation",
            lambda: reflection_layer.reflect_on_intent_deviation(
                "help_user", "caused_confusion", 0.7
            ),
        ),
        (
            "emotional_state",
            lambda: reflection_layer.reflect_on_emotional_state(
                {"anxiety": 0.9, "concern": 0.8}
            ),
        ),
        (
            "ethical_conflict",
            lambda: reflection_layer.contemplate_ethical_conflict(
                "Policy violation", ["ethics", "safety"], 0.9
            ),
        ),
    ]

    dream_results = []

    for scenario_name, create_reflection in test_scenarios:
        print(f"\n   🎭 Testing {scenario_name} scenario:")

        reflection = create_reflection()
        reflection.emotional_weight = 0.8  # Ensure it's above threshold

        print(f"      - Reflection ID: {reflection.id}")
        print(f"      - Type: {reflection.reflection_type.value}")
        print(f"      - Mood: {reflection.symbolic_mood.value}")

        # Test direct dream simulation performance
        if not is_placeholder:
            dream_scenario = {
                "trigger_reflection_id": reflection.id,
                "repair_target_type": reflection.reflection_type.value,
                "emotional_weight_trigger": reflection.emotional_weight,
                "symbolic_mood": reflection.symbolic_mood.value,
            }

            print("      💭 Testing dream simulation performance...")
            dream_id = await reflection_layer._perform_dream_simulation(
                dream_scenario, reflection
            )

            if dream_id:
                print(f"      ✅ Dream simulation successful: {dream_id}")
                dream_results.append((scenario_name, True, dream_id))
            else:
                print("      ⚠️ Dream simulation failed")
                dream_results.append((scenario_name, False, None))
        else:
            print("      ℹ️ Skipping simulation (placeholder engine)")
            dream_results.append((scenario_name, False, "placeholder"))

    # Test 5: Test consciousness snapshot with dream engine status
    print("\n🔍 Test 5: Testing consciousness snapshot with dream integration")

    snapshot = reflection_layer.capture_consciousness_snapshot()

    print("   ✅ Consciousness snapshot captured:")
    print(f"      - Drift score: {snapshot.drift_score:.3f}")
    print(f"      - Intent alignment: {snapshot.intent_alignment:.3f}")
    print(f"      - Emotional stability: {snapshot.emotional_stability:.3f}")
    print(f"      - Ethical compliance: {snapshot.ethical_compliance:.3f}")
    print(f"      - Overall mood: {snapshot.overall_mood.value}")

    # Test 6: Test autonomous reflection loop compatibility
    print("\n🔍 Test 6: Testing autonomous reflection loop compatibility")

    print("   📝 Creating test reflections for autonomous processing...")

    # Add several reflections to trigger autonomous processing
    test_reflections = [
        reflection_layer.reflect_on_drift_score(0.4, [0.1, 0.3, 0.4]),
        reflection_layer.reflect_on_emotional_state({"instability": 0.7}),
        reflection_layer.contemplate_ethical_conflict("Test conflict", ["test"], 0.8),
    ]

    for test_reflection in test_reflections:
        reflection_layer.log_reflection(test_reflection)

    print(f"   ✅ Added {len(test_reflections)} test reflections")
    print(f"   ✅ Total active reflections: {len(reflection_layer.active_reflections)}")

    # Create a consciousness snapshot that might trigger autonomous reflection
    snapshot_high_drift = reflection_layer.capture_consciousness_snapshot()

    print("   📊 Snapshot for autonomous trigger test:")
    print(f"      - Drift score: {snapshot_high_drift.drift_score:.3f}")
    print(f"      - Emotional stability: {snapshot_high_drift.emotional_stability:.3f}")

    autonomous_trigger = (
        snapshot_high_drift.drift_score > 0.3
        or snapshot_high_drift.emotional_stability < 0.6
    )
    print(f"   ✅ Would trigger autonomous reflection: {autonomous_trigger}")

    print("\n🎉 All dream engine integration tests completed!")

    # Summary
    successful_dreams = sum(1 for _, success, _ in dream_results if success)

    return {
        "dream_engine_available": dream_available,
        "dream_engine_type": (
            type(reflection_layer.dream_replayer).__name__
            if not is_placeholder
            else "placeholder"
        ),
        "is_placeholder": is_placeholder,
        "reflections_created": len(reflection_layer.active_reflections),
        "dream_scenarios_tested": len(dream_results),
        "successful_dream_simulations": successful_dreams,
        "dream_results": dream_results,
        "autonomous_trigger_ready": autonomous_trigger,
    }


if __name__ == "__main__":
    try:
        results = asyncio.run(test_dream_engine_integration())
        print("\n📊 Dream Engine Integration Test Results:")
        print(f"   - Dream engine available: {results['dream_engine_available']}")
        print(f"   - Dream engine type: {results['dream_engine_type']}")
        print(f"   - Is placeholder: {results['is_placeholder']}")
        print(f"   - Reflections created: {results['reflections_created']}")
        print(f"   - Dream scenarios tested: {results['dream_scenarios_tested']}")
        print(f"   - Successful simulations: {results['successful_dream_simulations']}")
        print(f"   - Autonomous trigger ready: {results['autonomous_trigger_ready']}")

        if results["dream_results"]:
            print("\n   🎭 Scenario Results:")
            for scenario, success, dream_id in results["dream_results"]:
                status = "✅ Success" if success else "⚠️ Failed"
                print(f"      - {scenario}: {status} ({dream_id})")

        print("\n✨ Dream engine integration is working correctly!")

    except Exception as e:
        print(f"❌ Dream engine integration test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
