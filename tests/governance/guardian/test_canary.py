"""
Unit tests for the canary enforcement logic.
"""

import unittest
from unittest.mock import patch
from lukhas.governance.guardian.canary import is_canary_enforced, get_canary_metrics

class TestCanaryEnforcement(unittest.TestCase):
    def test_canary_enforced_at_100_percent(self):
        """
        Test that canary mode is always enforced at 100%
        """
        results = [is_canary_enforced(100.0) for _ in range(100)]
        self.assertTrue(all(results))

    def test_canary_not_enforced_at_0_percent(self):
        """
        Test that canary mode is never enforced at 0%
        """
        results = [is_canary_enforced(0.0) for _ in range(100)]
        self.assertFalse(any(results))

    @patch('random.uniform', return_value=5.0)
    def test_canary_enforced_below_threshold(self, mock_uniform):
        """
        Test that canary mode is enforced when the random number is below the threshold.
        """
        self.assertTrue(is_canary_enforced(10.0))

    @patch('random.uniform', return_value=15.0)
    def test_canary_not_enforced_above_threshold(self, mock_uniform):
        """
        Test that canary mode is not enforced when the random number is above the threshold.
        """
        self.assertFalse(is_canary_enforced(10.0))

    def test_get_canary_metrics(self):
        """
        Test that the canary metrics are returned correctly.
        """
        metrics = get_canary_metrics()
        self.assertIn("canary_requests_total", metrics)
        self.assertIn("canary_enforced_total", metrics)

if __name__ == '__main__':
    unittest.main()
