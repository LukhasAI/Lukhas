import unittest

from memory import FoldEntropyVisualizer


class TestFoldEntropyVisualizer(unittest.TestCase):
    def setUp(self):
        self.viz = FoldEntropyVisualizer()
        self.data = [
            ("t1", 0.1),
            ("t2", 0.5),
            ("t3", 0.9),
        ]

    def test_render_ascii_chart(self):
        chart = self.viz.render_ascii_chart(self.data)
        self.assertIn("t1", chart)
        self.assertIn("0.10", chart)
        self.assertIn("█", chart)

    def test_render_mermaid_timeline(self):
        mermaid = self.viz.render_mermaid_timeline(self.data)
        self.assertTrue(mermaid.startswith("graph LR"))
        self.assertIn("t2", mermaid)
        self.assertIn("Δ=0.50", mermaid)


if __name__ == "__main__":
    unittest.main()
