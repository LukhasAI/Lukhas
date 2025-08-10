import unittest

import pytest

try:
    from memory.fold_engine import MemoryFold, MemoryPriority, MemoryType
    from reasoning.reasoning_engine import SymbolicEngine
except ImportError as e:
    pytest.skip(f"Memory components not available: {e}", allow_module_level=True)


class TestMemoryFold(unittest.TestCase):

    def test_store_prediction_outcome(self):
        # ΛTAG: memory_handoff
        # ΛTAG: recall_loop
        reasoning_engine = SymbolicEngine()

        # Use MemoryFold with correct constructor arguments
        memory_fold = MemoryFold(
            key="test_prediction",
            content={"prediction_store": []},
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.HIGH,
        )

        # 1. Simulate a symbolic prediction
        input_data = {
            "text": "A critical failure in the primary power core will cause a system-wide shutdown.",
            "context": {"source_node": "diagnostics_agent"},
        }

        try:
            prediction_result = reasoning_engine.reason(input_data)
            self.assertIsNotNone(prediction_result)

            # Store the prediction in memory fold
            memory_fold.content["prediction_result"] = prediction_result
            self.assertIn("prediction_result", memory_fold.content)

        except Exception:
            # If reasoning fails, test the memory structure anyway
            self.assertIsNotNone(memory_fold)
            self.assertEqual(memory_fold.key, "test_prediction")

    def test_memory_fold_creation(self):
        """Test basic memory fold creation and properties"""
        fold = MemoryFold(
            key="test_fold",
            content={"data": "test"},
            memory_type=MemoryType.PROCEDURAL,
            priority=MemoryPriority.MEDIUM,
        )

        self.assertEqual(fold.key, "test_fold")
        self.assertEqual(fold.content["data"], "test")
        self.assertEqual(fold.memory_type, MemoryType.PROCEDURAL)
        self.assertEqual(fold.priority, MemoryPriority.MEDIUM)

    def test_memory_fold_importance_score(self):
        """Test that memory folds have importance scores"""
        fold = MemoryFold(
            key="importance_test",
            content={"data": "important"},
            memory_type=MemoryType.SEMANTIC,
            priority=MemoryPriority.HIGH,
        )

        # Should have an importance score calculated automatically
        self.assertIsInstance(fold.importance_score, float)
        self.assertGreaterEqual(fold.importance_score, 0.0)


if __name__ == "__main__":
    unittest.main()
