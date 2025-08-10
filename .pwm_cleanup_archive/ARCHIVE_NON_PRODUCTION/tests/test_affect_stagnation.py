# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: tests/emotion/test_affect_stagnation.py
# MODULE: tests.emotion.test_affect_stagnation
# DESCRIPTION: Tests for the affect stagnation detection system.
# DEPENDENCIES: unittest, numpy
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - DO NOT DISTRIBUTE
# ═══════════════════════════════════════════════════════════════════════════

import unittest
from unittest.mock import MagicMock

from emotion.affect_stagnation_detector import (
    AffectStagnationDetector,  # CLAUDE_EDIT_v0.1: Fixed to absolute imports
)
from memory.core_memory.emotional_memory import EmotionalMemory


class TestAffectStagnation(unittest.TestCase):

    def setUp(self):
        self.emotional_memory = EmotionalMemory()
        # Mock the drift tracker's record_drift method
        self.emotional_memory.drift_tracker.record_drift = MagicMock()
        self.stagnation_detector = AffectStagnationDetector(
            self.emotional_memory, {"stagnation_threshold_hours": 1}
        )

    def test_stagnation_detection(self):
        """
        Tests that the AffectStagnationDetector correctly detects emotional stagnation.
        """
        # No stagnation initially
        self.assertIsNone(self.stagnation_detector.check_for_stagnation())

        # Simulate a period of no emotional change
        self.stagnation_detector.last_affect_change_ts -= 3700  # More than 1 hour ago

        stagnation_alert = self.stagnation_detector.check_for_stagnation()

        self.assertIsNotNone(stagnation_alert)
        self.assertTrue(stagnation_alert["stagnation"])
        self.assertEqual(stagnation_alert["symbol"], "🧊")
        self.assertIn(
            "No significant affect change for over 1 hours.",
            stagnation_alert["trigger"],
        )
        self.assertTrue(stagnation_alert["recovery_needed"])

    def test_no_stagnation_with_affect_change(self):
        """
        Tests that the AffectStagnationDetector does not detect stagnation when there is affect change.
        """
        # Simulate an emotional change
        self.emotional_memory.process_experience(
            experience_content={"type": "text", "text": "a happy event"},
            explicit_emotion_values={"joy": 0.8},
            event_intensity=0.7,
        )

        self.assertIsNone(self.stagnation_detector.check_for_stagnation())


if __name__ == "__main__":
    unittest.main()
