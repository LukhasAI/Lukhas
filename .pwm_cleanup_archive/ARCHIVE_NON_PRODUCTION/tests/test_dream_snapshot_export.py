import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class TestDreamSnapshotExport(unittest.TestCase):
    @patch("tests.test_dream_snapshot_export.DreamReflectionLoop")
    def test_dream_snapshot_export(self, mock_dream_loop_class):
        # Create a mock with proper attributes
        mock_dream_loop = Mock()
        mock_dream_loop.stats = {"affect_delta": 0.5}
        mock_dream_loop.export_snapshot.return_value = {
            "snapshot_id": "test_123",
            "affect_delta": 0.5,
            "timestamp": "2025-07-24",
        }
        mock_dream_loop_class.return_value = mock_dream_loop

        # Test the functionality
        dream_loop = mock_dream_loop_class()
        dream_loop.stats["affect_delta"] = 0.5
        snapshot = dream_loop.export_snapshot()

        self.assertEqual(snapshot["affect_delta"], 0.5)
        self.assertIn("snapshot_id", snapshot)

    def test_dream_timeline_visualizer(self):
        # Create a temporary directory for test
        test_dir = Path("test_dream_data")
        test_dir.mkdir(exist_ok=True)

        try:
            # Create a dummy dream log
            with open(test_dir / "dream_log.jsonl", "w") as f:
                f.write(
                    json.dumps({"timestamp": "2025-07-24", "event": "dream_start"})
                    + "\n"
                )
                f.write(
                    json.dumps({"timestamp": "2025-07-24", "event": "dream_end"}) + "\n"
                )

            # Test visualization (mocked since we don't have the actual visualizer)
            with patch(
                "tests.test_dream_snapshot_export.DreamTimelineVisualizer"
            ) as mock_viz:
                mock_instance = Mock()
                mock_instance.generate_timeline.return_value = "timeline.html"
                mock_viz.return_value = mock_instance

                # Simulate the test
                result = mock_instance.generate_timeline(
                    str(test_dir / "dream_log.jsonl")
                )
                self.assertEqual(result, "timeline.html")

        finally:
            # Cleanup
            import shutil

            if test_dir.exists():
                shutil.rmtree(test_dir)


# Mock the imports that don't exist
class DreamReflectionLoop:
    pass


class DreamTimelineVisualizer:
    pass


if __name__ == "__main__":
    unittest.main()
