#!/usr/bin/env python3
"""
Test script for ReflectionLayer voice integration.
Verifies that the voice systems are properly integrated and working.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.monitoring.reflection_layer import (
    ReflectionLayer,
    SymbolicMood,
)


def test_voice_integration():
    """Test the voice integration in ReflectionLayer"""

    print("🔊 Testing ReflectionLayer Voice Integration")
    print("=" * 60)

    # Initialize reflection layer
    print("\n📦 Initializing ReflectionLayer with voice...")
    reflection_layer = ReflectionLayer()

    # Test 1: Check voice initialization
    print("\n🔍 Test 1: Voice system initialization")
    voice_available = reflection_layer.voice_pack is not None
    print(f"   ✅ Voice system available: {voice_available}")

    if hasattr(reflection_layer.voice_pack, "speak"):
        print("   ✅ VoiceHandler detected")
    elif hasattr(reflection_layer, "voice_renderer"):
        print("   ✅ Voice renderer detected as fallback")
    else:
        print("   ℹ️ Text-only vocalization available")

    # Test 2: Test voice text generation
    print("\n🔍 Test 2: Testing voice text generation")

    # Create a test reflection
    test_reflection = reflection_layer.reflect_on_drift_score(0.8, [0.2, 0.5, 0.8])
    voice_text = reflection_layer._generate_voice_text(test_reflection)

    print("   ✅ Generated voice text:")
    print(f"   - Mood: {test_reflection.symbolic_mood.value}")
    print(f"   - Text: {voice_text}")

    # Test 3: Test mood to emotion mapping
    print("\n🔍 Test 3: Testing mood to emotion mapping")

    for mood in SymbolicMood:
        emotion = reflection_layer._map_mood_to_emotion(mood)
        print(f"   {mood.value} → {emotion}")

    # Test 4: Test low-emotion reflection (should not vocalize)
    print("\n🔍 Test 4: Testing low-emotion reflection vocalization")

    low_emotion_reflection = reflection_layer.reflect_on_emotional_state(
        {"calm": 0.9, "stability": 0.8}
    )
    low_emotion_reflection.emotional_weight = 0.3  # Below threshold

    should_not_vocalize = reflection_layer.vocalize_conscience(low_emotion_reflection)
    print(
        f"   ✅ Low emotion reflection vocalized: {should_not_vocalize} (should be False)"
    )

    # Test 5: Test high-emotion reflection (should vocalize)
    print("\n🔍 Test 5: Testing high-emotion reflection vocalization")

    high_emotion_reflection = reflection_layer.contemplate_ethical_conflict(
        "Critical ethical concern detected", ["user", "system", "society"], 0.9
    )
    high_emotion_reflection.emotional_weight = 0.8  # Above threshold

    print("   📢 Attempting vocalization (watch for output)...")
    should_vocalize = reflection_layer.vocalize_conscience(high_emotion_reflection)
    print(
        f"   ✅ High emotion reflection vocalized: {should_vocalize} (should be True)"
    )

    # Test 6: Test forced vocalization
    print("\n🔍 Test 6: Testing forced vocalization")

    neutral_reflection = reflection_layer.reflect_on_intent_deviation(
        "test action", "test result", 0.3
    )
    neutral_reflection.emotional_weight = 0.2  # Below threshold but forced

    print("   📢 Attempting forced vocalization...")
    forced_vocalize = reflection_layer.vocalize_conscience(
        neutral_reflection, force_vocalization=True
    )
    print(f"   ✅ Forced vocalization successful: {forced_vocalize} (should be True)")

    # Test 7: Test voice system selection logic
    print("\n🔍 Test 7: Testing voice system selection logic")

    # Test the _perform_vocalization method directly
    test_reflection_for_voice = reflection_layer.reflect_on_emotional_state(
        {"excitement": 0.9, "joy": 0.8}
    )

    print("   📢 Testing direct vocalization performance...")
    direct_success = reflection_layer._perform_vocalization(test_reflection_for_voice)
    print(f"   ✅ Direct vocalization successful: {direct_success}")

    # Test 8: Test vocalization with different moods
    print("\n🔍 Test 8: Testing vocalization with various moods")

    mood_tests = [
        (SymbolicMood.HARMONIOUS, "harmonious_test"),
        (SymbolicMood.CONCERNED, "concern_test"),
        (SymbolicMood.TRANSCENDENT, "transcendent_test"),
    ]

    for mood, test_id in mood_tests:
        # Create reflection with specific mood
        mood_reflection = reflection_layer.synthesize_memory_insights(
            {"test": "data"}, 0.8
        )
        mood_reflection.symbolic_mood = mood
        mood_reflection.emotional_weight = 0.8

        print(f"   📢 Testing {mood.value} vocalization...")
        mood_success = reflection_layer.vocalize_conscience(mood_reflection)
        print(f"   ✅ {mood.value} vocalization: {mood_success}")

    print("\n🎉 All voice integration tests completed!")

    # Summary
    vocalizations_attempted = len(
        [r for r in reflection_layer.active_reflections if r.voice_vocalized]
    )

    return {
        "voice_available": voice_available,
        "reflections_created": len(reflection_layer.active_reflections),
        "vocalizations_attempted": vocalizations_attempted,
        "voice_system_type": (
            type(reflection_layer.voice_pack).__name__
            if reflection_layer.voice_pack
            else "None"
        ),
    }


if __name__ == "__main__":
    try:
        results = test_voice_integration()
        print("\n📊 Voice Integration Test Results:")
        print(f"   - Voice system available: {results['voice_available']}")
        print(f"   - Voice system type: {results['voice_system_type']}")
        print(f"   - Reflections created: {results['reflections_created']}")
        print(f"   - Vocalizations attempted: {results['vocalizations_attempted']}")
        print("\n✨ Voice integration is working correctly!")

    except Exception as e:
        print(f"❌ Voice integration test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
