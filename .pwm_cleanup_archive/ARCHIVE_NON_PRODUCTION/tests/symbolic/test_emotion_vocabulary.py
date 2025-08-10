"""
Tests for the Emotion Vocabulary.
"""

import unittest

from symbolic.vocabularies.emotion_vocabulary import (
    EMOTION_VOCABULARY,
    get_emotion_symbol,
    get_guardian_weight,
)


class TestEmotionVocabulary(unittest.TestCase):

    def test_vocabulary_completeness(self):
        """Ensure the vocabulary meets standards."""
        for key, entry in EMOTION_VOCABULARY.items():
            self.assertIn("emoji", entry)
            self.assertIn("symbol", entry)
            self.assertIn("meaning", entry)
            self.assertIn("resonance", entry)
            self.assertIn("guardian_weight", entry)
            self.assertIsInstance(entry["guardian_weight"], float)
            self.assertTrue(0.0 <= entry["guardian_weight"] <= 1.0)
            self.assertIsInstance(entry["contexts"], list)

    def test_get_emotion_symbol(self):
        """Test the get_emotion_symbol function."""
        self.assertEqual(get_emotion_symbol("joy"), "😊")
        self.assertEqual(get_emotion_symbol("sadness"), "😢")
        self.assertEqual(get_emotion_symbol("anger"), "😠")
        self.assertEqual(get_emotion_symbol("fear"), "😨")
        self.assertEqual(get_emotion_symbol("unknown"), "❓")

    def test_get_guardian_weight(self):
        """Test the get_guardian_weight function."""
        self.assertEqual(get_guardian_weight("joy"), 0.1)
        self.assertEqual(get_guardian_weight("sadness"), 0.4)
        self.assertEqual(get_guardian_weight("anger"), 0.7)
        self.assertEqual(get_guardian_weight("fear"), 0.6)
        self.assertEqual(get_guardian_weight("unknown"), 0.5)


if __name__ == "__main__":
    unittest.main()
