"""
Tests for the Symbolic Shell Archiver.
"""

import asyncio
import json
import os
import unittest

from core.colonies.reasoning_colony import ReasoningColony
from core.symbolism.archiver import SymbolicShellArchiver
from core.symbolism.tags import TagPermission, TagScope


class TestSymbolicShellArchiver(unittest.TestCase):
    """
    Tests for the Symbolic Shell Archiver.
    """

    def setUp(self):
        self.output_dir = "/tmp/lukhas_test_snapshots"
        os.makedirs(self.output_dir, exist_ok=True)
        self.colony = ReasoningColony("test_colony")
        self.archiver = SymbolicShellArchiver([self.colony], self.output_dir)

    def tearDown(self):
        for f in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, f))
        os.rmdir(self.output_dir)

    def test_create_snapshot(self):
        """
        Test that a snapshot is created correctly.
        """

        async def run_test():
            await self.colony.start()
            task_data = {
                "type": "test_task",
                "tags": {
                    "test_tag": (
                        "test_value",
                        TagScope.LOCAL,
                        TagPermission.PUBLIC,
                        None,
                    )
                },
            }
            await self.colony.execute_task("test_task", task_data)
            snapshot_file = self.archiver.create_snapshot()
            await self.colony.stop()

            self.assertTrue(os.path.exists(snapshot_file))
            with open(snapshot_file) as f:
                snapshot = json.load(f)

            self.assertIn("timestamp", snapshot)
            self.assertIn("colonies", snapshot)
            self.assertIn("test_colony", snapshot["colonies"])
            self.assertIn("symbolic_carryover", snapshot["colonies"]["test_colony"])
            self.assertIn(
                "test_tag", snapshot["colonies"]["test_colony"]["symbolic_carryover"]
            )
            self.assertEqual(
                snapshot["colonies"]["test_colony"]["symbolic_carryover"]["test_tag"][
                    0
                ],
                "test_value",
            )

        asyncio.run(run_test())

    def test_periodic_snapshots(self):
        """
        Test that snapshots are created periodically.
        """

        async def run_test():
            await self.colony.start()
            self.archiver.start(interval=0.1)
            await asyncio.sleep(0.35)
            self.archiver.stop()
            await self.colony.stop()

            self.assertGreaterEqual(len(os.listdir(self.output_dir)), 2)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
