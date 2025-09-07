"""
Module: redirect_forecaster.py
Author: Jules 03
Date: 2025-07-19
Description: Predicts the likelihood of a dream redirect being needed in the next cycle.
"""
from typing import Any, Dict, List, Optional

import numpy as np
import streamlit as st


class RedirectForecaster:
    """
    Analyzes historical snapshot drift data and predicts the likelihood of a
    redirection being needed in the next cycle.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initializes the RedirectForecaster.

        Args:
            config (Optional[Dict[str, Any]], optional): Configuration options. Defaults to None.
        """
        self.config = config or {}
        self.history_weight = self.config.get("history_weight", 0.5)
        self.volatility_weight = self.config.get("volatility_weight", 0.5)

    def forecast(self, historical_drift: list[float]) -> dict[str, Any]:
        """
        Predicts the likelihood of a redirect being needed in the next cycle.

        Args:
            historical_drift (List[float]): A list of historical drift scores.

        Returns:
            Dict[str, Any]: A forecast vector.
        """
        if not historical_drift:
            return {
                "forecast_score": 0.0,
                "predicted_redirect": False,
                "cause_weights": {},
            }

        mean_drift = np.mean(historical_drift)
        drift_volatility = np.std(historical_drift)

        forecast_score = (self.history_weight * mean_drift) + (self.volatility_weight * drift_volatility)
        predicted_redirect = forecast_score > 0.5

        cause_weights = {
            "mean_drift": mean_drift,
            "drift_volatility": drift_volatility,
        }

        return {
            "forecast_score": forecast_score,
            "predicted_redirect": predicted_redirect,
            "cause_weights": cause_weights,
        }
