import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from emotion.affect_stagnation_detector import AffectStagnationDetector
from memory.core_memory.emotional_memory import EmotionalMemory


class TestEmotionFeedback(unittest.TestCase):

    def setUp(self):
        self.emotional_memory = EmotionalMemory()
        self.stagnation_detector = AffectStagnationDetector(self.emotional_memory)

    def test_emotional_stagnation_simulation(self):
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

        # Check for stagnation
        with patch(
            "time.time",
            return_value=self.emotional_memory.last_history_update_ts + 3600 * 25,
        ):
            with patch.object(
                self.emotional_memory, "affect_vector_velocity", return_value=0.0
            ):
                stagnation = self.stagnation_detector.check_for_stagnation()

        self.assertIsNotNone(stagnation)
        self.assertTrue(stagnation["stagnation"])
        self.assertEqual(stagnation["symbol"], "⏳")
        self.assertIn("Emotional stagnation detected: joy", stagnation["trigger"])


if __name__ == "__main__":
    unittest.main()
