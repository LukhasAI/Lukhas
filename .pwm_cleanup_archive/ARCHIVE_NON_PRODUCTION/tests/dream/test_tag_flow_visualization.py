import unittest

from dream.dream_director import direct_dream_flow
from dream.tag_debug import trace_tag_flow


class TestTagFlowVisualization(unittest.IsolatedAsyncioTestCase):
    async def test_tag_flow_metrics(self):
        snapshots = [{"note": "a", "tag": "alpha"}, {"note": "b", "tag": "beta"}]
        dream_data = await direct_dream_flow(snapshots)
        self.assertIn("tags", dream_data)
        self.assertIn("metrics", dream_data)
        debug = trace_tag_flow(dream_data)
        self.assertEqual(debug["tags"], ["alpha", "beta", "dream_generated"])
        self.assertIn("driftScore", debug)
        self.assertIn("convergence", debug)
        self.assertGreaterEqual(debug["convergence"], 0.0)
        self.assertLessEqual(debug["convergence"], 1.0)


if __name__ == "__main__":
    unittest.main()
