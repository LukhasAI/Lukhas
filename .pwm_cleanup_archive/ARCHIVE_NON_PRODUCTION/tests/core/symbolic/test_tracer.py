import unittest

from core.symbolic.tracer import SymbolicTracer


class TestSymbolicTracer(unittest.TestCase):

    def test_get_trail(self):
        tracer = SymbolicTracer()
        trail_id = tracer.start_trail("test prompt")
        tracer.trace("TestAgent", "TestEvent", {"foo": "bar"}, trail_id)
        trail = tracer.get_trail(trail_id)
        self.assertIsNotNone(trail)
        self.assertEqual(len(trail.traces), 1)
        self.assertEqual(trail.traces[0].agent, "TestAgent")

    def test_end_trail(self):
        tracer = SymbolicTracer()
        trail_id = tracer.start_trail("test prompt")
        tracer.trace("TestAgent", "TestEvent", {"foo": "bar"}, trail_id)
        trail = tracer.end_trail(trail_id, "test conclusion")
        self.assertIsNotNone(trail)
        self.assertEqual(trail.final_conclusion, "test conclusion")
        self.assertIsNone(tracer.get_trail(trail_id))


if __name__ == "__main__":
    unittest.main()
