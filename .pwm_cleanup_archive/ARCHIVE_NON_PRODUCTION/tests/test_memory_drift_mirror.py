import json
import os
import unittest

from memory.core_memory.memory_drift_mirror import MemoryDriftMirror
from memory.core_memory.memory_drift_tracker import MemoryDriftTracker


class TestMemoryDriftMirror(unittest.TestCase):

    def setUp(self):
        self.drift_log_path = "test_drift_log.jsonl"
        self.classification_log_path = "test_drift_classifications.jsonl"
        self.tracker = MemoryDriftTracker(log_file_path=self.drift_log_path)
        self.mirror = MemoryDriftMirror(
            drift_log_path=self.drift_log_path,
            classification_log_path=self.classification_log_path,
        )

    def tearDown(self):
        if os.path.exists(self.drift_log_path):
            os.remove(self.drift_log_path)
        if os.path.exists(self.classification_log_path):
            os.remove(self.classification_log_path)

    def test_stable_sequence(self):
        """
        Tests that a stable sequence is correctly classified.
        """
        # Create a stable sequence
        for i in range(5):
            self.tracker.track_drift(
                {"snapshot_id": f"s{i}"},
                {"snapshot_id": f"p{i}"},
                entropy_delta=0.1 - i * 0.01,
            )

        self.mirror.analyze_drift()

        with open(self.classification_log_path) as f:
            classification = json.loads(f.readline())
            self.assertEqual(classification["type"], "stable")

    def test_looping_sequence(self):
        """
        Tests that a looping sequence is correctly classified.
        """
        # Create a looping sequence
        for i in range(5):
            self.tracker.track_drift(
                {"snapshot_id": f"s{i}"},
                {"snapshot_id": f"p{i}"},
                entropy_delta=0.1 if i % 2 == 0 else 0.2,
            )

        self.mirror.analyze_drift()

        with open(self.classification_log_path) as f:
            classification = json.loads(f.readline())
            self.assertEqual(classification["type"], "looping")

    def test_collapse_risk_sequence(self):
        """
        Tests that a collapse risk sequence is correctly classified.
        """
        # Create a collapse risk sequence
        for i in range(5):
            self.tracker.track_drift(
                {"snapshot_id": f"s{i}"}, {"snapshot_id": f"p{i}"}, entropy_delta=0.9
            )

        self.mirror.analyze_drift()

        with open(self.classification_log_path) as f:
            classification = json.loads(f.readline())
            self.assertEqual(classification["type"], "collapse risk")


if __name__ == "__main__":
    unittest.main()
