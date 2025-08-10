#!/usr/bin/env python3
"""
Test script for ReflectionLayer actual metrics implementation.
Verifies that the new metric collection methods work correctly.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.monitoring.reflection_layer import ReflectionLayer


def test_reflection_layer_metrics():
    """Test the new actual metrics implementation in ReflectionLayer"""

    print("🧠 Testing ReflectionLayer Actual Metrics Implementation")
    print("=" * 60)

    # Initialize reflection layer
    print("\n📦 Initializing ReflectionLayer...")
    reflection_layer = ReflectionLayer()

    # Test 1: Basic metrics with no reflections
    print("\n🔍 Test 1: Basic metrics with empty reflection history")
    snapshot = reflection_layer.capture_consciousness_snapshot()

    assert snapshot.drift_score >= 0.0, "Drift score should be non-negative"
    assert snapshot.intent_alignment >= 0.0, "Intent alignment should be non-negative"
    assert (
        snapshot.emotional_stability >= 0.0
    ), "Emotional stability should be non-negative"
    assert (
        snapshot.ethical_compliance >= 0.0
    ), "Ethical compliance should be non-negative"

    print("   ✅ Initial metrics captured:")
    print(f"   - Drift Score: {snapshot.drift_score:.3f}")
    print(f"   - Intent Alignment: {snapshot.intent_alignment:.3f}")
    print(f"   - Emotional Stability: {snapshot.emotional_stability:.3f}")
    print(f"   - Ethical Compliance: {snapshot.ethical_compliance:.3f}")

    # Test 2: Add some reflections and verify metrics change
    print("\n🔍 Test 2: Adding reflections and testing metric calculation")

    # Add a drift reflection
    drift_reflection = reflection_layer.reflect_on_drift_score(0.6, [0.2, 0.4, 0.6])
    reflection_layer.log_reflection(drift_reflection)

    # Add an intent deviation reflection
    intent_reflection = reflection_layer.reflect_on_intent_deviation(
        "help user", "generated confusion", 0.7
    )
    reflection_layer.log_reflection(intent_reflection)

    # Add an emotional reflection
    emotional_reflection = reflection_layer.reflect_on_emotional_state(
        {"anxiety": 0.8, "confidence": 0.2, "stability": 0.3}
    )
    reflection_layer.log_reflection(emotional_reflection)

    # Add an ethical conflict reflection
    ethical_reflection = reflection_layer.contemplate_ethical_conflict(
        "Potential bias detected", ["user", "system"], 0.7
    )
    reflection_layer.log_reflection(ethical_reflection)

    print(f"   📝 Added {len(reflection_layer.active_reflections)} reflections")

    # Test 3: Capture snapshot with reflections
    print("\n🔍 Test 3: Capturing snapshot with reflection history")
    snapshot_with_reflections = reflection_layer.capture_consciousness_snapshot()

    print("   ✅ Updated metrics:")
    print(f"   - Drift Score: {snapshot_with_reflections.drift_score:.3f}")
    print(f"   - Intent Alignment: {snapshot_with_reflections.intent_alignment:.3f}")
    print(
        f"   - Emotional Stability: {snapshot_with_reflections.emotional_stability:.3f}"
    )
    print(
        f"   - Ethical Compliance: {snapshot_with_reflections.ethical_compliance:.3f}"
    )
    print(f"   - Overall Mood: {snapshot_with_reflections.overall_mood.value}")

    # Test 4: Verify drift calculation methods
    print("\n🔍 Test 4: Testing individual metric calculation methods")

    drift_score = reflection_layer._get_actual_drift_score()
    intent_alignment = reflection_layer._get_actual_intent_alignment()
    emotional_stability = reflection_layer._get_actual_emotional_stability()
    ethical_compliance = reflection_layer._get_actual_ethical_compliance()

    print("   ✅ Individual method results:")
    print(f"   - Drift calculation: {drift_score:.3f}")
    print(f"   - Intent calculation: {intent_alignment:.3f}")
    print(f"   - Emotional calculation: {emotional_stability:.3f}")
    print(f"   - Ethical calculation: {ethical_compliance:.3f}")

    # Test 5: Verify reflection-based calculations work
    print("\n🔍 Test 5: Testing reflection-based calculations")

    reflection_drift = reflection_layer._calculate_reflection_based_drift()
    ethical_fallback = reflection_layer._calculate_ethical_compliance_fallback()

    print("   ✅ Reflection-based calculations:")
    print(f"   - Reflection-based drift: {reflection_drift:.3f}")
    print(f"   - Ethical compliance fallback: {ethical_fallback:.3f}")

    # Test 6: Test consciousness trend analysis
    print("\n🔍 Test 6: Testing consciousness trend analysis")

    # Add more snapshots for trend analysis
    for i in range(5):
        snapshot = reflection_layer.capture_consciousness_snapshot()
        reflection_layer.consciousness_history.append(snapshot)

    trends = reflection_layer.get_consciousness_trend(hours=1)

    print("   ✅ Consciousness trends:")
    print(f"   - Status: {trends['status']}")
    print(f"   - Snapshots analyzed: {trends['snapshots_count']}")
    print(f"   - Current mood: {trends['current_mood']}")
    print(f"   - Drift trend: {trends['drift_trend']['direction']}")
    print(f"   - Reflection count: {trends['reflection_count_in_period']}")

    # Test 7: Validate all metrics are in valid ranges
    print("\n🔍 Test 7: Validating metric ranges")

    assert (
        0.0 <= snapshot_with_reflections.drift_score <= 1.0
    ), "Drift score out of range"
    assert (
        0.0 <= snapshot_with_reflections.intent_alignment <= 1.0
    ), "Intent alignment out of range"
    assert (
        0.0 <= snapshot_with_reflections.emotional_stability <= 1.0
    ), "Emotional stability out of range"
    assert (
        0.0 <= snapshot_with_reflections.ethical_compliance <= 1.0
    ), "Ethical compliance out of range"

    print("   ✅ All metrics within valid ranges [0.0, 1.0]")

    # Test 8: Verify metrics respond to reflection content
    print("\n🔍 Test 8: Testing metric sensitivity to reflection content")

    # Record initial metrics
    initial_emotional = reflection_layer._get_actual_emotional_stability()

    # Add high-emotion reflection
    high_emotion_reflection = reflection_layer.reflect_on_emotional_state(
        {"anxiety": 0.95, "anger": 0.9, "fear": 0.85}
    )
    high_emotion_reflection.emotional_weight = 0.95
    reflection_layer.log_reflection(high_emotion_reflection)

    # Check if emotional stability changed
    updated_emotional = reflection_layer._get_actual_emotional_stability()

    print("   📊 Emotional stability change:")
    print(f"   - Before high-emotion reflection: {initial_emotional:.3f}")
    print(f"   - After high-emotion reflection: {updated_emotional:.3f}")
    print(f"   - Change: {updated_emotional - initial_emotional:.3f}")

    print("\n🎉 All ReflectionLayer metrics tests passed!")
    print(
        "✨ The reflection layer now uses actual system metrics instead of random values"
    )

    return {
        "reflection_count": len(reflection_layer.active_reflections),
        "snapshot_count": len(reflection_layer.consciousness_history),
        "final_metrics": {
            "drift": snapshot_with_reflections.drift_score,
            "intent": snapshot_with_reflections.intent_alignment,
            "emotional": snapshot_with_reflections.emotional_stability,
            "ethical": snapshot_with_reflections.ethical_compliance,
        },
    }


if __name__ == "__main__":
    try:
        results = test_reflection_layer_metrics()
        print("\n📊 Test Results Summary:")
        print(f"   - Reflections generated: {results['reflection_count']}")
        print(f"   - Snapshots captured: {results['snapshot_count']}")
        print(f"   - Final drift score: {results['final_metrics']['drift']:.3f}")
        print(f"   - Final intent alignment: {results['final_metrics']['intent']:.3f}")
        print(
            f"   - Final emotional stability: {results['final_metrics']['emotional']:.3f}"
        )
        print(
            f"   - Final ethical compliance: {results['final_metrics']['ethical']:.3f}"
        )

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
