"""
LUKHAS Confidence Calibration - Adaptive Calibration System

Provides:
- Temperature scaling for confidence calibration
- Platt scaling for probability calibration
- Expected Calibration Error (ECE) tracking
- Continuous learning and parameter fitting
"""

from collections import deque
from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class CalibrationMetrics:
    """Metrics for calibration quality"""

    expected_calibration_error: float
    max_calibration_error: float
    brier_score: float
    log_loss: float
    num_predictions: int
    temperature: float
    platt_a: float
    platt_b: float


class AdaptiveConfidenceCalibrator:
    """
    Adaptive confidence calibration using temperature and Platt scaling

    Features:
    - Temperature scaling: adjusts logit scale
    - Platt scaling: logistic regression on logits
    - Continuous parameter fitting using recent predictions
    - ECE (Expected Calibration Error) tracking
    """

    def __init__(self, window_size: int = 1000, num_bins: int = 10, refit_interval: int = 100):
        """
        Initialize adaptive calibrator

        Args:
            window_size: Number of recent predictions to keep for calibration
            num_bins: Number of bins for ECE calculation
            refit_interval: How often to refit calibration parameters
        """
        self.window_size = window_size
        self.num_bins = num_bins
        self.refit_interval = refit_interval

        # Calibration parameters
        self.temperature: float = 1.0
        self.platt_a: float = 1.0
        self.platt_b: float = 0.0

        # Recent predictions and outcomes
        self.recent_predictions: deque = deque(maxlen=window_size)
        self.recent_outcomes: deque = deque(maxlen=window_size)

        # Metrics
        self.prediction_count = 0

    def calibrate(self, raw_confidence: float) -> float:
        """
        Calibrate a raw confidence score

        Args:
            raw_confidence: Raw confidence score (0-1)

        Returns:
            Calibrated confidence score (0-1)
        """
        eps = 1e-9
        raw_confidence = np.clip(raw_confidence, eps, 1 - eps)

        # Convert to logit
        logit = np.log(raw_confidence / (1 - raw_confidence))

        # Apply temperature scaling
        scaled_logit = logit / max(self.temperature, 1e-3)

        # Apply Platt scaling
        platt_logit = self.platt_a * scaled_logit + self.platt_b

        # Convert back to probability
        calibrated = 1.0 / (1.0 + np.exp(-platt_logit))

        return float(np.clip(calibrated, eps, 1 - eps))

    def record_prediction(self, raw_confidence: float, outcome: float):
        """
        Record a prediction and its outcome for calibration

        Args:
            raw_confidence: Raw confidence score that was predicted
            outcome: Actual outcome (0 or 1 for binary, 0-1 for probabilistic)
        """
        self.recent_predictions.append(raw_confidence)
        self.recent_outcomes.append(outcome)
        self.prediction_count += 1

        # Refit calibration parameters periodically
        if len(self.recent_predictions) % self.refit_interval == 0:
            self._recompute_calibration()

    def _recompute_calibration(self):
        """
        Fit temperature and Platt parameters on the recent window.
        Lightweight gradient steps to reduce NLL while avoiding instability.
        """
        if len(self.recent_predictions) < 50:
            return

        eps = 1e-6
        xs = np.clip(np.array(self.recent_predictions, dtype=float), eps, 1 - eps)
        ys = np.array(self.recent_outcomes, dtype=float)

        # Temperature scaling
        logits = np.log(xs / (1 - xs))
        T = max(self.temperature, 0.5)
        for _ in range(25):
            p = 1.0 / (1.0 + np.exp(-logits / max(T, 1e-3)))
            grad = np.sum((p - ys) * logits) / (max(T, 1e-3) ** 2 * (len(xs) + eps))
            T = max(0.1, T - 0.1 * grad)
        self.temperature = float(T)

        # Platt scaling: logistic regression on logits
        a, b = float(self.platt_a), float(self.platt_b)
        for _ in range(50):
            z = a * logits + b
            p = 1.0 / (1.0 + np.exp(-z))
            g_a = np.sum((p - ys) * logits) / (len(xs) + eps)
            g_b = np.sum(p - ys) / (len(xs) + eps)
            a -= 0.1 * g_a
            b -= 0.1 * g_b
        self.platt_a, self.platt_b = float(a), float(b)

    def compute_ece(self) -> float:
        """
        Compute Expected Calibration Error on recent predictions

        Returns:
            ECE score (lower is better, 0 is perfect calibration)
        """
        if len(self.recent_predictions) < 10:
            return 0.0

        predictions = np.array(self.recent_predictions)
        outcomes = np.array(self.recent_outcomes)

        # Calibrate all predictions
        calibrated_predictions = np.array([self.calibrate(p) for p in predictions])

        # Bin predictions
        bin_edges = np.linspace(0, 1, self.num_bins + 1)
        ece = 0.0

        for i in range(self.num_bins):
            bin_mask = (calibrated_predictions >= bin_edges[i]) & (calibrated_predictions < bin_edges[i + 1])
            if i == self.num_bins - 1:  # Include upper edge in last bin
                bin_mask = bin_mask | (calibrated_predictions == 1.0)

            if np.sum(bin_mask) > 0:
                bin_confidence = np.mean(calibrated_predictions[bin_mask])
                bin_accuracy = np.mean(outcomes[bin_mask])
                bin_weight = np.sum(bin_mask) / len(predictions)
                ece += bin_weight * abs(bin_confidence - bin_accuracy)

        return float(ece)

    def compute_brier_score(self) -> float:
        """
        Compute Brier score on recent predictions

        Returns:
            Brier score (lower is better, 0 is perfect)
        """
        if len(self.recent_predictions) < 10:
            return 0.0

        predictions = np.array(self.recent_predictions)
        outcomes = np.array(self.recent_outcomes)

        calibrated_predictions = np.array([self.calibrate(p) for p in predictions])
        brier = np.mean((calibrated_predictions - outcomes) ** 2)

        return float(brier)

    def compute_log_loss(self) -> float:
        """
        Compute log loss (cross-entropy) on recent predictions

        Returns:
            Log loss (lower is better, 0 is perfect)
        """
        if len(self.recent_predictions) < 10:
            return 0.0

        eps = 1e-15
        predictions = np.array(self.recent_predictions)
        outcomes = np.array(self.recent_outcomes)

        calibrated_predictions = np.array([self.calibrate(p) for p in predictions])
        calibrated_predictions = np.clip(calibrated_predictions, eps, 1 - eps)

        log_loss = -np.mean(
            outcomes * np.log(calibrated_predictions) + (1 - outcomes) * np.log(1 - calibrated_predictions)
        )

        return float(log_loss)

    def get_metrics(self) -> CalibrationMetrics:
        """
        Get comprehensive calibration metrics

        Returns:
            CalibrationMetrics object with all metrics
        """
        ece = self.compute_ece()
        brier = self.compute_brier_score()
        log_loss = self.compute_log_loss()

        # Compute max calibration error
        mce = 0.0
        if len(self.recent_predictions) >= 10:
            predictions = np.array(self.recent_predictions)
            outcomes = np.array(self.recent_outcomes)
            calibrated_predictions = np.array([self.calibrate(p) for p in predictions])

            bin_edges = np.linspace(0, 1, self.num_bins + 1)
            for i in range(self.num_bins):
                bin_mask = (calibrated_predictions >= bin_edges[i]) & (calibrated_predictions < bin_edges[i + 1])
                if i == self.num_bins - 1:
                    bin_mask = bin_mask | (calibrated_predictions == 1.0)

                if np.sum(bin_mask) > 0:
                    bin_confidence = np.mean(calibrated_predictions[bin_mask])
                    bin_accuracy = np.mean(outcomes[bin_mask])
                    mce = max(mce, abs(bin_confidence - bin_accuracy))

        return CalibrationMetrics(
            expected_calibration_error=ece,
            max_calibration_error=mce,
            brier_score=brier,
            log_loss=log_loss,
            num_predictions=len(self.recent_predictions),
            temperature=self.temperature,
            platt_a=self.platt_a,
            platt_b=self.platt_b,
        )

    def reset(self):
        """Reset calibration state"""
        self.temperature = 1.0
        self.platt_a = 1.0
        self.platt_b = 0.0
        self.recent_predictions.clear()
        self.recent_outcomes.clear()
        self.prediction_count = 0

    def export_state(self) -> Dict:
        """Export calibration state for persistence"""
        return {
            "temperature": self.temperature,
            "platt_a": self.platt_a,
            "platt_b": self.platt_b,
            "window_size": self.window_size,
            "num_bins": self.num_bins,
            "prediction_count": self.prediction_count,
            "recent_predictions": list(self.recent_predictions),
            "recent_outcomes": list(self.recent_outcomes),
        }

    def import_state(self, state: Dict):
        """Import calibration state from persistence"""
        self.temperature = state.get("temperature", 1.0)
        self.platt_a = state.get("platt_a", 1.0)
        self.platt_b = state.get("platt_b", 0.0)
        self.window_size = state.get("window_size", self.window_size)
        self.num_bins = state.get("num_bins", self.num_bins)
        self.prediction_count = state.get("prediction_count", 0)

        recent_preds = state.get("recent_predictions", [])
        recent_outs = state.get("recent_outcomes", [])

        self.recent_predictions = deque(recent_preds, maxlen=self.window_size)
        self.recent_outcomes = deque(recent_outs, maxlen=self.window_size)
