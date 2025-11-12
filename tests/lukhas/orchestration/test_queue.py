"""
Unit tests for the RequestQueue.
"""

import asyncio
import unittest
from unittest.mock import MagicMock

from lukhas.orchestration.queue import Priority, RequestQueue


async def dummy_task():
    """A dummy task for testing."""
    await asyncio.sleep(0.01)


class TestRequestQueue(unittest.TestCase):

    def test_put_and_get(self):
        """Test that a request can be added to and retrieved from the queue."""
        async def run_test():
            queue = RequestQueue()
            self.assertEqual(queue.qsize(), 0)

            await queue.put("test_request", dummy_task(), Priority.NORMAL)
            self.assertEqual(queue.qsize(), 1)

            request = await queue.get()
            self.assertEqual(request.request_id, "test_request")
            self.assertEqual(queue.qsize(), 0)

        asyncio.run(run_test())

    def test_priority(self):
        """Test that higher priority requests are processed first."""
        async def run_test():
            queue = RequestQueue()
            await queue.put("low_priority", dummy_task(), Priority.LOW)
            await queue.put("high_priority", dummy_task(), Priority.HIGH)
            await queue.put("normal_priority", dummy_task(), Priority.NORMAL)

            high_priority_request = await queue.get()
            self.assertEqual(high_priority_request.request_id, "high_priority")

            normal_priority_request = await queue.get()
            self.assertEqual(normal_priority_request.request_id, "normal_priority")

            low_priority_request = await queue.get()
            self.assertEqual(low_priority_request.request_id, "low_priority")

        asyncio.run(run_test())

    def test_backpressure(self):
        """Test that the queue raises QueueFull when it reaches max size."""
        async def run_test():
            queue = RequestQueue(max_size=1)
            await queue.put("request1", dummy_task(), Priority.NORMAL)

            with self.assertRaises(asyncio.QueueFull):
                await queue.put("request2", dummy_task(), Priority.NORMAL)

        asyncio.run(run_test())

    def test_fairness(self):
        """Test that a lower priority request is eventually processed."""
        async def run_test():
            # Test with a very small fairness window for predictability
            queue = RequestQueue(fairness_window=0.1)
            await queue.put("low_priority_user", dummy_task(), Priority.LOW)
            await queue.put("high_priority_user", dummy_task(), Priority.HIGH)

            # First, the high priority request should be processed
            high_priority_request = await queue.get()
            self.assertEqual(high_priority_request.request_id, "high_priority_user")

            # Now, if we add another high priority request from the same source,
            # it should be delayed by the fairness mechanism.
            await queue.put("high_priority_user", dummy_task(), Priority.HIGH)

            # The low priority request should be processed next
            low_priority_request = await queue.get()
            self.assertEqual(low_priority_request.request_id, "low_priority_user")

            # The second high priority request should come last
            high_priority_request_2 = await queue.get()
            self.assertEqual(high_priority_request_2.request_id, "high_priority_user")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
