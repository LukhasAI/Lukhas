"""Test ProphetPredictor basic forecasting."""

import pandas as pd

from tools.prediction import ProphetPredictor


def test_basic_forecast():
    data = pd.DataFrame(
        {
            "ds": pd.date_range("2025-01-01", periods=6, freq="D"),
            "y": [0, 1, 2, 3, 4, 5],
        }
    )
    predictor = ProphetPredictor()
    predictor.fit(data)
    forecast = predictor.predict(periods=2)
    assert len(forecast) == 8
    assert "yhat" in forecast.columns
