import unittest
from unittest.mock import MagicMock

from dream.dream_feedback_propagator import DreamFeedbackPropagator

from emotion.mood_regulation.mood_regulator import MoodRegulator
from memory.core_memory.emotional_memory import EmotionalMemory


class TestDreamFeedbackPropagator(unittest.TestCase):
    def test_propagate_calls_mood_regulator_and_applies_adjustment(self):
        memory = EmotionalMemory()
        regulator = MoodRegulator(memory)

        # Mock the adjust_baseline_from_drift method to return a specific adjustment
        mock_adjustment = {"emotional_context": {"sadness": 0.2, "fear": 0.1}}
        regulator.adjust_baseline_from_drift = MagicMock(return_value=mock_adjustment)

        propagator = DreamFeedbackPropagator(memory, regulator)

        dream = {
            "affect_trace": {"total_drift": 0.9, "affect_delta": 0.8},
            "emotional_context": {"joy": 0.5},
        }

        propagator.propagate(dream)

        # Verify that adjust_baseline_from_drift was called correctly
        regulator.adjust_baseline_from_drift.assert_called_once_with(0.9, 0.8)

        # Verify that the emotional context was adjusted
        self.assertAlmostEqual(dream["emotional_context"]["joy"], 0.5)
        self.assertAlmostEqual(dream["emotional_context"]["sadness"], 0.2)
        self.assertAlmostEqual(dream["emotional_context"]["fear"], 0.1)


if __name__ == "__main__":
    unittest.main()
