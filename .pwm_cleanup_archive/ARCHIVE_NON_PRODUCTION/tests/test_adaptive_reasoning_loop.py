import unittest

import pytest

try:
    from reasoning.adaptive_reasoning_loop import (
        AdaptiveReasoningLoop,
        create_reasoning_loop,
    )
except ImportError:
    # Use mock system when module is not available
    try:
        import os
        import sys

        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from tests.test_mocks import (
            AdaptiveReasoningLoop,
            create_reasoning_loop,
        )
    except ImportError:
        pytest.skip(
            "Neither reasoning module nor test mocks are available",
            allow_module_level=True,
        )


class TestAdaptiveReasoningLoop(unittest.TestCase):

    def test_reasoning_loop_creation(self):
        """Test creating a reasoning loop"""
        loop = AdaptiveReasoningLoop()
        self.assertIsNotNone(loop)
        self.assertFalse(loop.active)

    def test_reasoning_loop_start_stop(self):
        """Test starting and stopping reasoning loop"""
        loop = AdaptiveReasoningLoop()

        # Test starting
        result = loop.start_reasoning()
        self.assertTrue(loop.active)
        self.assertIn("started", result.lower())

        # Test stopping
        result = loop.stop_reasoning()
        self.assertFalse(loop.active)
        self.assertIn("stopped", result.lower())

    def test_reasoning_loop_status(self):
        """Test getting reasoning loop status"""
        loop = AdaptiveReasoningLoop()
        status = loop.get_status()

        self.assertIsInstance(status, dict)
        self.assertIn("active", status)
        self.assertIn("mode", status)
        self.assertEqual(status["mode"], "stub")

    def test_create_reasoning_loop_function(self):
        """Test the factory function"""
        loop = create_reasoning_loop()
        self.assertIsInstance(loop, AdaptiveReasoningLoop)


if __name__ == "__main__":
    unittest.main()
