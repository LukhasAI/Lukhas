import unittest

from emotion.mood_regulation.mood_entropy_tracker import MoodEntropyTracker


class TestMoodEntropyTracker(unittest.TestCase):
    def test_entropy_empty(self):
        tracker = MoodEntropyTracker()
        self.assertEqual(tracker.get_entropy(), 0.0)

    def test_entropy_single_value(self):
        tracker = MoodEntropyTracker()
        tracker.log_mood(0.5)
        self.assertEqual(tracker.get_entropy(), 0.0)

    def test_entropy_multiple_values(self):
        tracker = MoodEntropyTracker()
        for v in [0.1, 0.1, 0.9, 0.9]:
            tracker.log_mood(v)
        # Two values, equal probability: entropy = 1.0
        self.assertAlmostEqual(tracker.get_entropy(), 1.0, places=3)

    def test_entropy_varied(self):
        tracker = MoodEntropyTracker()
        for v in [0.1, 0.1, 0.1, 0.9]:
            tracker.log_mood(v)
        # 0.1: 75%, 0.9: 25% -> entropy < 1.0
        entropy = tracker.get_entropy()
        self.assertTrue(0.0 < entropy < 1.0)


if __name__ == "__main__":
    unittest.main()
