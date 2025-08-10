import unittest
from unittest.mock import Mock, patch

# Add error handling for missing modules
try:
    from trace.drift_alignment_controller import DriftAlignmentController

    from dream.dream_feedback_propagator import DreamFeedbackPropagator

    from emotion.mood_regulator import MoodRegulator
    from memory.core_memory.emotional_memory import (
        EmotionalMemory,
        EmotionVector,
    )
except ImportError as e:
    pass  # Handle import error
    print(f"Warning: Could not import required modules: {e}")
    # Create mock classes for testing
    DriftAlignmentController = Mock
    MoodRegulator = Mock
    DreamFeedbackPropagator = Mock
    EmotionalMemory = Mock
    EmotionVector = Mock


class TestMoodTuningFeedbackLoop(unittest.TestCase):
    def test_full_feedback_loop_with_high_drift(self):
        # 1. Setup
        emotional_memory = EmotionalMemory()
        # Set a known baseline
        emotional_memory.personality["baseline"] = EmotionVector(
            {"joy": 0.5, "sadness": 0.1}
        )

        mood_regulator = MoodRegulator(
            emotional_memory, config={"drift_threshold": 0.5, "adjustment_factor": 0.2}
        )
        propagator = DreamFeedbackPropagator(emotional_memory, mood_regulator)

        dream_data = {
            "affect_trace": {"total_drift": 0.9},
            "emotional_context": {"joy": 0.8},
        }

        # Mock the symbolic_affect_trace to return a controlled value
        with patch.object(emotional_memory, "symbolic_affect_trace") as mock_trace:
            mock_trace.return_value = {"affect_patterns": [{"valence_change": 0.2}]}

            # 2. Action
            propagator.propagate(dream_data)

        # 3. Verification
        # The drift (0.9) is higher than the mocked affect delta (0.2), so the controller should suggest "Apply emotional grounding".
        # This should lead to an increase in "sadness" and "fear" in the emotional context.
        self.assertIn("sadness", dream_data["emotional_context"])
        self.assertIn("fear", dream_data["emotional_context"])
        self.assertAlmostEqual(dream_data["emotional_context"]["sadness"], 0.2)
        self.assertAlmostEqual(dream_data["emotional_context"]["fear"], 0.1)

        # Also verify that the baseline emotion has been adjusted towards neutral
        new_baseline = emotional_memory.personality["baseline"]
        # The original baseline was joy: 0.5, sadness: 0.1. The adjustment factor is 0.2.
        # The new baseline should be a blend between the original and a neutral vector.
        # neutral = EmotionVector() -> joy: 0, sadness: 0
        # new_joy = 0.5 * (1-0.2) + 0 * 0.2 = 0.4
        # new_sadness = 0.1 * (1-0.2) + 0 * 0.2 = 0.08
        self.assertAlmostEqual(new_baseline.values["joy"], 0.4)
        self.assertAlmostEqual(new_baseline.values["sadness"], 0.08)


if __name__ == "__main__":
    unittest.main()
