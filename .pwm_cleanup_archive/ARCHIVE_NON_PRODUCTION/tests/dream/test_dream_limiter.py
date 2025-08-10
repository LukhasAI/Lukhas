import sys
import types
import unittest

if "structlog" not in sys.modules:
    stub = types.ModuleType("structlog")
    stub.get_logger = lambda *a, **kw: types.SimpleNamespace(
        info=lambda *a, **kw: None, debug=lambda *a, **kw: None
    )
    sys.modules["structlog"] = stub

import importlib.util
from pathlib import Path

module_path = (
    Path(__file__).resolve().parents[2]
    / "lukhas/creativity/dream_systems/dream_limiter.py"
)
spec = importlib.util.spec_from_file_location("dream_limiter", module_path)
dream_limiter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dream_limiter)
DreamLimiter = dream_limiter.DreamLimiter
DreamLimiterConfig = dream_limiter.DreamLimiterConfig


class TestDreamLimiter(unittest.TestCase):
    def test_limiter_filters_recursion(self):
        cfg = DreamLimiterConfig(window_size=5, recursion_threshold=0.6)
        limiter = DreamLimiter(cfg)
        dreams = [{"emotion_vector": {"sadness": 0.9}} for _ in range(5)]
        filtered = limiter.filter_dreams(dreams)
        self.assertLess(len(filtered), len(dreams))
        self.assertGreaterEqual(len(filtered), 3)

    def test_limiter_allows_novelty(self):
        cfg = DreamLimiterConfig(window_size=5, recursion_threshold=0.6)
        limiter = DreamLimiter(cfg)
        dreams = [
            {"emotion_vector": {"joy": 0.8}},
            {"emotion_vector": {"sadness": 0.7}},
            {"emotion_vector": {"joy": 0.6}},
            {"emotion_vector": {"trust": 0.5}},
        ]
        filtered = limiter.filter_dreams(dreams)
        self.assertEqual(len(filtered), len(dreams))


if __name__ == "__main__":
    unittest.main()
