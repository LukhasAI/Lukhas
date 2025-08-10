"""
Tests for the RedirectForecaster.
"""

import unittest

from dream.stability.redirect_forecaster import RedirectForecaster


class TestRedirectForecaster(unittest.TestCase):
    """
    Tests for the RedirectForecaster.
    """

    def setUp(self):
        """
        Set up the tests.
        """
        self.forecaster = RedirectForecaster()

    def test_forecast_no_drift(self):
        """
        Test that forecast returns a low score when there is no drift.
        """
        historical_drift = [0.1, 0.1, 0.1, 0.1, 0.1]
        forecast = self.forecaster.forecast(historical_drift)
        self.assertLess(forecast["forecast_score"], 0.5)
        self.assertFalse(forecast["predicted_redirect"])

    def test_forecast_with_drift(self):
        """
        Test that forecast returns a high score when there is drift.
        """
        historical_drift = [0.8, 0.9, 0.8, 0.9, 0.8]
        forecast = self.forecaster.forecast(historical_drift)
        self.assertGreater(forecast["forecast_score"], 0.4)
        self.assertFalse(forecast["predicted_redirect"])

    def test_forecast_increasing_drift(self):
        """
        Test that forecast returns a high score when there is increasing drift.
        """
        historical_drift = [0.1, 0.2, 0.3, 0.4, 0.5]
        forecast = self.forecaster.forecast(historical_drift)
        self.assertGreater(forecast["forecast_score"], 0.2)
        self.assertFalse(forecast["predicted_redirect"])


if __name__ == "__main__":
    unittest.main()
