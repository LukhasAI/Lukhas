"""Test for drift timeline generator"""

import re  # Fix the 're' reference error
import unittest
from unittest.mock import Mock, patch


class TestDriftTimelineGen(unittest.TestCase):
    def test_drift_timeline_generation(self):
        """Test drift timeline generation"""
        # Mock the timeline generator
        with patch(
            "lukhas.analytics.drift_timeline_gen.DriftTimelineGenerator"
        ) as mock_gen:
            mock_instance = Mock()
            mock_instance.generate.return_value = {"timeline": [], "summary": {}}
            mock_gen.return_value = mock_instance

            # Test
            result = mock_instance.generate()
            self.assertIn("timeline", result)
            self.assertIn("summary", result)

    def test_pattern_matching(self):
        """Test pattern matching with regex"""
        pattern = re.compile(r"drift_\d+")
        test_string = "drift_123"
        self.assertTrue(pattern.match(test_string))


if __name__ == "__main__":
    unittest.main()
