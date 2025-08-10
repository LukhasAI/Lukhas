"""
Tests for The Observatory.
"""

import unittest

from core.observatory import Observatory
from core.symbolic.tracer import SymbolicTracer
from memory.unified_memory_manager import EnhancedMemoryManager


class TestObservatory(unittest.IsolatedAsyncioTestCase):
    """
    Tests for The Observatory.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.tracer = SymbolicTracer()
        self.memory_manager = EnhancedMemoryManager()
        self.observatory = Observatory(self.tracer, self.memory_manager)

    def test_get_decision_trail(self):
        """
        Test retrieving a decision trail.
        """
        trail_id = self.tracer.start_trail("test prompt")
        self.tracer.trace("test_agent", "test_event", {"key": "value"}, trail_id)
        trail = self.observatory.get_decision_trail(trail_id)
        self.assertIsNotNone(trail)
        self.assertEqual(trail.trail_id, trail_id)

    async def test_query_memory_read_only(self):
        """
        Test querying memory in read-only mode.
        """
        result = await self.observatory.query_memory("test query")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["error"])

    def test_get_system_status(self):
        """
        Test getting the system status.
        """
        status = self.observatory.get_system_status()
        self.assertIn("active_decision_trails", status)
        self.assertIn("total_traces", status)
        self.assertIn("active_memory_folds", status)
        self.assertIn("read_only_mode", status)
        self.assertTrue(status["read_only_mode"])


if __name__ == "__main__":
    unittest.main()
