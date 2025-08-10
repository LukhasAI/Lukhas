import unittest

from symbolic.vocabularies.emotion_vocabulary import (
    EMOTION_VOCABULARY,
    get_emotion_symbol,
    get_guardian_weight,
)


class TestEmotionVocabulary(unittest.TestCase):

    def test_get_emotion_symbol(self):
        """Test retrieving an emotion's emoji symbol."""
        self.assertEqual(get_emotion_symbol("joy"), "😊")
        self.assertEqual(get_emotion_symbol("sadness"), "😢")
        self.assertEqual(get_emotion_symbol("anger"), "😠")
        self.assertEqual(get_emotion_symbol("fear"), "😨")
        self.assertEqual(get_emotion_symbol("nonexistent"), "❓")

    def test_get_guardian_weight(self):
        """Test retrieving an emotion's guardian weight."""
        self.assertEqual(get_guardian_weight("joy"), 0.1)
        self.assertEqual(get_guardian_weight("sadness"), 0.4)
        self.assertEqual(get_guardian_weight("anger"), 0.7)
        self.assertEqual(get_guardian_weight("fear"), 0.6)
        self.assertEqual(get_guardian_weight("nonexistent"), 0.5)

    def test_vocabulary_structure(self):
        """Test the structure of the emotion vocabulary."""
        for emotion, data in EMOTION_VOCABULARY.items():
            self.assertIn("emoji", data)
            self.assertIn("symbol", data)
            self.assertIn("meaning", data)
            self.assertIn("resonance", data)
            self.assertIn("guardian_weight", data)
            self.assertIn("contexts", data)
            self.assertIsInstance(data["emoji"], str)
            self.assertIsInstance(data["symbol"], str)
            self.assertIsInstance(data["meaning"], str)
            self.assertIsInstance(data["resonance"], str)
            self.assertIsInstance(data["guardian_weight"], float)
            self.assertIsInstance(data["contexts"], list)


if __name__ == "__main__":
    unittest.main()
