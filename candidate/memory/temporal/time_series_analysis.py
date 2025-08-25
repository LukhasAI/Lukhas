"""
Time Series Analysis for Temporal Memory
========================================
This module provides utilities for analyzing time series data from memory events.
"""

from typing import Any, Dict, List
import numpy as np

class TimeSeriesAnalyzer:
    """
    A simulated system for analyzing time series data from memory events.
    """

    def detect_trends(self, time_series: List[float]) -> Dict[str, Any]:
        """
        Simulates detecting trends in a time series.
        A real implementation would use statistical methods like moving averages
        or regression analysis.
        """
        if len(time_series) < 2:
            return {"trend": "insufficient_data"}

        # Simple trend detection based on the slope of a line between first and last points
        slope = (time_series[-1] - time_series[0]) / len(time_series)

        trend = "stable"
        if slope > 0.1:
            trend = "upward"
        elif slope < -0.1:
            trend = "downward"

        return {"trend": trend, "slope": slope}

    def find_anomalies(self, time_series: List[float], threshold: float = 2.0) -> List[int]:
        """
        Simulates finding anomalies in a time series using standard deviation.
        """
        if len(time_series) < 5:
            return [] # Not enough data for meaningful analysis

        mean = np.mean(time_series)
        std_dev = np.std(time_series)

        anomalies = []
        for i, value in enumerate(time_series):
            if abs(value - mean) > threshold * std_dev:
                anomalies.append(i)

        return anomalies

    def forecast(self, time_series: List[float], steps: int = 5) -> List[float]:
        """
        Simulates forecasting future values using a simple linear extrapolation.
        """
        if len(time_series) < 2:
            return [0.0] * steps

        # Use the last two points to extrapolate
        last_value = time_series[-1]
        previous_value = time_series[-2]
        growth_rate = last_value - previous_value

        forecast = []
        current_value = last_value
        for _ in range(steps):
            current_value += growth_rate
            forecast.append(current_value)

        return forecast
