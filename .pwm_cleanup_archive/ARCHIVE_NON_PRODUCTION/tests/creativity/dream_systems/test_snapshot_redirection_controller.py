"""
Tests for the SnapshotRedirectionController.
"""

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from dream.core.dream_snapshot import DreamSnapshotStore
from dream.core.snapshot_redirection_controller import (
    SnapshotRedirectionController,
)

from memory.core_memory.emotional_memory import EmotionalMemory, EmotionVector


class TestSnapshotRedirectionController(unittest.TestCase):
    """
    Tests for the SnapshotRedirectionController.
    """

    def setUp(self):
        """
        Set up the tests.
        """
        self.emotional_memory = Mock(spec=EmotionalMemory)
        self.emotional_memory.current_emotion = EmotionVector()
        self.emotional_memory.affect_delta.return_value = {"intensity_change": 0.5}
        self.snapshot_store = Mock(spec=DreamSnapshotStore)
        self.controller = SnapshotRedirectionController(
            self.emotional_memory, self.snapshot_store
        )

    def test_check_and_redirect_no_snapshots(self):
        """
        Test that check_and_redirect returns None when there are no snapshots.
        """
        self.snapshot_store.get_recent_snapshots.return_value = []
        self.assertIsNone(self.controller.check_and_redirect("test_user"))

    def test_check_and_redirect_not_enough_snapshots(self):
        """
        Test that check_and_redirect returns None when there is only one snapshot.
        """
        self.snapshot_store.get_recent_snapshots.return_value = [
            {"timestamp": "2025-07-18T21:54:59.501408+00:00"}
        ]
        self.assertIsNone(self.controller.check_and_redirect("test_user"))

    def test_calculate_emotional_drift_no_drift(self):
        """
        Test that _calculate_emotional_drift returns a low value when there is no drift.
        """
        now = datetime.now(timezone.utc)
        snapshots = [
            {
                "timestamp": (now - timedelta(seconds=10)).isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.5}},
            },
            {
                "timestamp": now.isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.5}},
            },
        ]
        drift = self.controller._calculate_emotional_drift(snapshots)
        self.assertAlmostEqual(drift, 0.0)

    def test_calculate_emotional_drift_with_drift(self):
        """
        Test that _calculate_emotional_drift returns a higher value when there is drift.
        """
        now = datetime.now(timezone.utc)
        snapshots = [
            {
                "timestamp": (now - timedelta(seconds=10)).isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.1}},
            },
            {
                "timestamp": now.isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.9}},
            },
        ]
        drift = self.controller._calculate_emotional_drift(snapshots)
        self.assertGreater(drift, 0.0)

    def test_check_and_redirect_with_drift(self):
        """
        Test that check_and_redirect returns a new narrative when there is drift.
        """
        now = datetime.now(timezone.utc)
        self.snapshot_store.get_recent_snapshots.return_value = [
            {
                "timestamp": (now - timedelta(seconds=10)).isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.1}},
            },
            {
                "timestamp": now.isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.9}},
            },
        ]
        self.controller.drift_threshold = 0.01
        result = self.controller.check_and_redirect("test_user")
        self.assertIsNotNone(result)
        self.assertEqual(result["seed_type"], "narrative_redirection")
        self.assertEqual(result["narrative_name"], "neutral_ground")

    def test_check_and_redirect_no_drift(self):
        """
        Test that check_and_redirect returns None when there is no drift.
        """
        now = datetime.now(timezone.utc)
        self.snapshot_store.get_recent_snapshots.return_value = [
            {
                "timestamp": (now - timedelta(seconds=10)).isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.5}},
            },
            {
                "timestamp": now.isoformat(),
                "emotional_context": {"dimensions": {"joy": 0.5}},
            },
        ]
        self.controller.drift_threshold = 0.1
        self.assertIsNone(self.controller.check_and_redirect("test_user"))


if __name__ == "__main__":
    unittest.main()
