import unittest

from memory.core_memory.fold_engine import (
    MemoryFold,
    MemoryPriority,
    MemoryType,
)
from memory.core_memory.memory_introspection_engine import (
    MemoryIntrospectionEngine,
)


class TestMemoryIntrospectionEngine(unittest.TestCase):
    def test_compute_fold_metrics(self):
        fold = MemoryFold("k1", "data", MemoryType.EPISODIC, MemoryPriority.MEDIUM)
        engine = MemoryIntrospectionEngine()
        metrics = engine.compute_fold_metrics(fold)
        self.assertEqual(metrics["key"], "k1")
        self.assertIn("driftScore", metrics)

    def test_introspect(self):
        fold1 = MemoryFold("k1", "d1", MemoryType.EPISODIC, MemoryPriority.MEDIUM)
        fold2 = MemoryFold("k2", "d2", MemoryType.SEMANTIC, MemoryPriority.MEDIUM)
        engine = MemoryIntrospectionEngine()
        result = engine.introspect([fold1, fold2])
        self.assertEqual(result["fold_count"], 2)
        self.assertIn("average_drift", result)


if __name__ == "__main__":
    unittest.main()
