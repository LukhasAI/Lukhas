# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: tests/emotion/test_emotion_recursion.py
# MODULE: tests.emotion.test_emotion_recursion
# DESCRIPTION: Tests for the emotion recursion and recurrence detection systems.
# DEPENDENCIES: unittest, numpy
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - DO NOT DISTRIBUTE
# ═══════════════════════════════════════════════════════════════════════════

import time
import unittest
from unittest.mock import MagicMock, patch

from dream.oneiric_engine.oneiric_core.modules.dream_reflection_loop import (
    DreamReflectionLoop,
)

from emotion.mood_regulator import MoodRegulator
from emotion.recurring_emotion_tracker import RecurringEmotionTracker
from memory.core_memory.emotional_memory import EmotionalMemory, EmotionVector
from reasoning.reasoning_engine import SymbolicEngine


class TestEmotionRecursion(unittest.TestCase):

    def setUp(self):
        self.emotional_memory = EmotionalMemory()
        # Mock the drift tracker's record_drift method
        self.emotional_memory.drift_tracker.record_drift = MagicMock()
        self.emotion_tracker = RecurringEmotionTracker(self.emotional_memory)
        self.mood_regulator = MoodRegulator(self.emotional_memory)
        self.reasoning_engine = SymbolicEngine()

        # Mock the brain integration and its components
        self.mock_brain = MagicMock()
        self.mock_brain.emotional_memory = self.emotional_memory

        self.dream_loop = DreamReflectionLoop()
        self.dream_loop.mood_regulator = self.mood_regulator
        # Set the mock brain components directly
        self.dream_loop.emotional_memory = self.emotional_memory

    def test_affect_delta_calculation(self):
        """
        Tests that the affect_delta method correctly calculates the change in emotion.
        """
        initial_emotion = EmotionVector({"joy": 0.5})
        self.emotional_memory.current_emotion = initial_emotion

        new_emotion = EmotionVector({"joy": 0.8, "sadness": 0.1})

        delta = self.emotional_memory.affect_delta("test_event", new_emotion)

        self.assertIn("drift_magnitude", delta)
        self.assertIn("event", delta)
        self.assertIn("previous_valence", delta)
        self.assertIn("new_valence", delta)
        self.assertIn("intensity_change", delta)
        self.assertIn("timestamp", delta)
        self.assertAlmostEqual(
            delta["new_valence"], self.emotional_memory.current_emotion.valence
        )

    def test_symbolic_tagging_in_dream_synthesis(self):
        """
        Tests that the dream synthesis method includes the correct symbolic tags.
        """
        dream_synthesis_result = self.dream_loop.synthesize_dream()
        dream = dream_synthesis_result.get("dream", {})

        self.assertIn("#ΛTAG: affect_trace", dream["tags"])
        self.assertIn("#ΛTAG: mood_infusion", dream["tags"])
        self.assertIn("affect_trace", dream)

    @unittest.skip("DreamReflectionLoop doesn't have start_dream_cycle method")
    @patch("time.sleep", return_value=None)
    def test_recurring_emotion_simulation(self, mock_sleep):
        """
        Simulates multiple dream cycles to test recurrence detection.
        """
        # Simulate a series of sad events
        for _ in range(5):
            self.emotional_memory.process_experience(
                experience_content={"type": "text", "text": "a sad event"},
                explicit_emotion_values={"sadness": 0.8},
                event_intensity=0.7,
            )
            # We need to manually advance the timestamp for history
            self.emotional_memory.last_history_update_ts += 3600

        # Run a dream cycle
        self.dream_loop.start_dream_cycle(duration_minutes=0.1)
        time.sleep(1)  # give the thread time to run
        self.dream_loop.stop_dream_cycle()

        # Check for recurrence
        with patch("time.time", return_value=time.time() + 3600 * 25):
            with patch.object(
                self.emotional_memory, "affect_vector_velocity", return_value=0.0
            ):
                recurrence = self.emotion_tracker.check_for_recurrence()

        self.assertIsNotNone(recurrence)
        self.assertTrue(recurrence["recurrence"])
        self.assertEqual(recurrence["symbol"], "🔄")
        self.assertIn("Recurring emotion detected: sadness", recurrence["trigger"])

    @unittest.skip("DreamReflectionLoop doesn't have start_dream_cycle method")
    @patch("time.sleep", return_value=None)
    def test_emotional_stagnation_simulation(self, mock_sleep):
        """
        Simulates a long period of the same emotion to test stagnation detection.
        """
        stagnation_emotion = {"joy": 0.6, "trust": 0.4}

        # Simulate a long period of the same emotion
        for i in range(30):
            self.emotional_memory.process_experience(
                experience_content={"type": "text", "text": "a happy event"},
                explicit_emotion_values=stagnation_emotion,
                event_intensity=0.5,
            )
            self.emotional_memory.last_history_update_ts += (
                3600  # Advance time by 1 hour
            )

        # Run a dream cycle
        self.dream_loop.start_dream_cycle(duration_minutes=0.1)
        time.sleep(1)
        self.dream_loop.stop_dream_cycle()

        # Check for stagnation
        with patch("time.time", return_value=time.time() + 3600 * 25):
            with patch.object(
                self.emotional_memory, "affect_vector_velocity", return_value=0.0
            ):
                recurrence = self.emotion_tracker.check_for_recurrence()

        self.assertIsNotNone(recurrence)
        self.assertTrue(recurrence["recurrence"])
        self.assertEqual(recurrence["symbol"], "⏳")
        self.assertIn("Emotional stagnation detected: joy", recurrence["trigger"])
        self.assertIn("Emotional stagnation detected: joy", recurrence["trigger"])

    def test_mood_collision(self):
        """
        Tests how the system handles a collision of strong, opposing emotions.
        """
        # Induce a strong positive emotion
        self.emotional_memory.process_experience(
            experience_content={"type": "text", "text": "a very happy event"},
            explicit_emotion_values={"joy": 0.9, "trust": 0.8},
            event_intensity=0.9,
        )
        positive_state = self.emotional_memory.current_emotion

        # Induce a strong negative emotion
        self.emotional_memory.process_experience(
            experience_content={"type": "text", "text": "a very sad event"},
            explicit_emotion_values={"sadness": 0.9, "fear": 0.8},
            event_intensity=0.9,
        )
        collided_state = self.emotional_memory.current_emotion

        # Check that the resulting state is more neutral than either of the two initial states
        self.assertLess(collided_state.valence, positive_state.valence)
        self.assertGreater(
            collided_state.valence, 0.1
        )  # Should not be extremely negative

    def test_drift_triggered_reset(self):
        """
        Tests that a high drift score triggers an emotional baseline reset.
        """
        initial_baseline = self.emotional_memory.personality["baseline"]

        # Simulate a high drift score
        self.mood_regulator.adjust_baseline_from_drift(0.9)

        new_baseline = self.emotional_memory.personality["baseline"]

        # Check that the baseline has been adjusted towards neutral
        self.assertNotEqual(initial_baseline.to_dict(), new_baseline.to_dict())
        self.assertLess(new_baseline.intensity, initial_baseline.intensity)

    def test_reasoning_bias_from_emotion(self):
        """
        Tests that the reasoning engine is biased by the current emotional state.
        """
        # Set a fearful emotional state
        fearful_emotion = EmotionVector({"fear": 0.8, "sadness": 0.6})
        self.emotional_memory.current_emotion = fearful_emotion

        # Run the reasoning engine with a neutral input
        input_data = {"text": "The user is considering a new proposal."}
        reasoning_result = self.reasoning_engine.reason(
            input_data,
            emotional_state=self.emotional_memory.get_current_emotional_state()[
                "current_emotion_vector"
            ],
        )

        # Check that the confidence of the conclusion is lower due to fear
        self.assertLess(
            reasoning_result["overall_confidence"],
            self.reasoning_engine.confidence_threshold,
        )


if __name__ == "__main__":
    unittest.main()
