import unittest

import plotly.graph_objects as go
from dream.visualization.memoryscape_viewport import DreamMemoryscapeViewport


class TestDreamMemoryscapeViewport(unittest.TestCase):
    def test_render_scene_returns_figure(self):
        viewport = DreamMemoryscapeViewport()
        dreams = [
            {"description": "init", "affect_delta": 0.1, "theta_delta": 0.2},
            {"description": "growth", "affect_delta": 0.3, "theta_delta": 0.5},
        ]
        fig = viewport.render_scene(dreams)
        self.assertIsInstance(fig, go.Figure)
        self.assertIn("Identity Drift", fig.layout.title.text)
        self.assertEqual(len(fig.data[0].x), 2)


if __name__ == "__main__":
    unittest.main()
