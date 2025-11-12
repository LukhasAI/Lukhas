#!/usr/bin/env python3
"""
MATRIZ Confidence Calibration Node

Calibrates confidence levels to match actual performance.
Detects and corrects overconfidence and underconfidence.

Example: "Stated 90% confidence but only 70% accuracy → Overconfident, calibrate down"
"""

import time
import uuid
from typing import Any, Dict, List
from dataclasses import dataclass

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class CalibrationResult:
    """Result of confidence calibration."""
    original_confidence: float
    actual_performance: float
    calibration_error: float
    calibrated_confidence: float
    calibration_direction: str  # overconfident, underconfident, well_calibrated


class ConfidenceCalibrationNode(CognitiveNode):
    """
    Calibrates confidence to match actual performance.

    Capabilities:
    - Calibration error detection
    - Confidence adjustment
    - Performance tracking
    - Overconfidence/underconfidence correction
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_confidence_calibration",
            capabilities=[
                "confidence_calibration",
                "calibration_error_detection",
                "confidence_adjustment",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calibrate confidence levels.

        Args:
            input_data: Dict containing:
                - predictions: List of predictions with stated confidence
                - actual_outcomes: Actual outcomes for validation
                - calibration_history: Historical calibration data
                - target_calibration: Target calibration error

        Returns:
            Dict with calibration results, adjustments, and MATRIZ node
        """
        start_time = time.time()

        predictions = input_data.get("predictions", [])
        actual_outcomes = input_data.get("actual_outcomes", [])
        calibration_history = input_data.get("calibration_history", [])
        target_calibration = input_data.get("target_calibration", 0.1)

        # Calibrate each prediction
        calibrations = self._calibrate_predictions(
            predictions,
            actual_outcomes,
            calibration_history
        )

        # Calculate overall calibration metrics
        metrics = self._calculate_metrics(calibrations)

        # Determine calibration quality
        quality = self._assess_calibration_quality(metrics, target_calibration)

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics)

        # Compute confidence
        confidence = self._compute_confidence(calibrations, calibration_history)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.7 + metrics.get("overall_error", 0) * 0.3),
            novelty=max(0.1, 0.3),
            utility=min(1.0, 1.0 - metrics.get("overall_error", 0))
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="confidence_calibration_update",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "AWARENESS",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "prediction_count": len(predictions)
            },
            "calibrations": [
                {
                    "original_confidence": c.original_confidence,
                    "actual_performance": c.actual_performance,
                    "calibration_error": c.calibration_error,
                    "calibrated_confidence": c.calibrated_confidence,
                    "calibration_direction": c.calibration_direction
                }
                for c in calibrations
            ],
            "metrics": metrics,
            "quality": quality,
            "recommendations": recommendations
        }

        return {
            "answer": {
                "calibrations": matriz_node["calibrations"],
                "metrics": metrics,
                "quality": quality,
                "recommendations": recommendations
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        if "metrics" not in output["answer"]:
            return False

        return True

    def _calibrate_predictions(
        self,
        predictions: List[dict],
        actual_outcomes: List[dict],
        calibration_history: List[dict]
    ) -> List[CalibrationResult]:
        """Calibrate each prediction."""
        calibrations = []

        for i, pred in enumerate(predictions):
            pred_id = pred.get("id", f"pred_{i}")
            original_confidence = pred.get("confidence", 0.5)

            # Find actual outcome
            actual = next(
                (o for o in actual_outcomes if o.get("id") == pred_id),
                None
            )

            if actual:
                # Determine actual performance
                actual_performance = self._determine_performance(pred, actual)

                # Calculate calibration error
                calibration_error = abs(original_confidence - actual_performance)

                # Calibrate confidence
                calibrated_confidence = self._adjust_confidence(
                    original_confidence,
                    actual_performance,
                    calibration_history
                )

                # Determine direction
                direction = self._determine_direction(
                    original_confidence,
                    actual_performance
                )

                calibrations.append(
                    CalibrationResult(
                        original_confidence=original_confidence,
                        actual_performance=actual_performance,
                        calibration_error=calibration_error,
                        calibrated_confidence=calibrated_confidence,
                        calibration_direction=direction
                    )
                )

        return calibrations

    def _determine_performance(self, prediction: dict, actual: dict) -> float:
        """Determine actual performance of prediction."""
        # Check if prediction was correct
        pred_value = prediction.get("value")
        actual_value = actual.get("value")

        if pred_value == actual_value:
            return 1.0  # Perfect prediction
        elif pred_value is None or actual_value is None:
            return 0.5  # Unknown
        else:
            # Partial credit based on closeness
            if isinstance(pred_value, (int, float)) and isinstance(actual_value, (int, float)):
                error = abs(pred_value - actual_value)
                max_error = max(abs(pred_value), abs(actual_value), 1.0)
                return max(0.0, 1.0 - error / max_error)
            else:
                return 0.0  # Wrong prediction

    def _adjust_confidence(
        self,
        original_confidence: float,
        actual_performance: float,
        calibration_history: List[dict]
    ) -> float:
        """Adjust confidence based on performance."""
        # Simple approach: move confidence toward actual performance

        # Calculate historical bias
        historical_bias = self._calculate_historical_bias(calibration_history)

        # Adjustment factor (how much to adjust)
        adjustment_factor = 0.3  # 30% adjustment

        # Direction of adjustment
        error = original_confidence - actual_performance

        # Adjust
        adjustment = adjustment_factor * (error + historical_bias)
        calibrated = original_confidence - adjustment

        return max(0.0, min(1.0, calibrated))

    def _calculate_historical_bias(self, calibration_history: List[dict]) -> float:
        """Calculate historical calibration bias."""
        if not calibration_history:
            return 0.0

        # Average overconfidence/underconfidence
        recent = calibration_history[-20:]  # Last 20 calibrations

        total_bias = sum(
            h.get("stated_confidence", 0.5) - h.get("actual_performance", 0.5)
            for h in recent
        )

        return total_bias / len(recent)

    def _determine_direction(
        self,
        original_confidence: float,
        actual_performance: float
    ) -> str:
        """Determine calibration direction."""
        error = original_confidence - actual_performance

        if abs(error) < 0.1:
            return "well_calibrated"
        elif error > 0.1:
            return "overconfident"
        else:
            return "underconfident"

    def _calculate_metrics(self, calibrations: List[CalibrationResult]) -> dict:
        """Calculate overall calibration metrics."""
        if not calibrations:
            return {
                "overall_error": 0.0,
                "overconfidence_rate": 0.0,
                "underconfidence_rate": 0.0,
                "well_calibrated_rate": 0.0
            }

        # Overall calibration error
        overall_error = sum(c.calibration_error for c in calibrations) / len(calibrations)

        # Direction rates
        overconfident = sum(
            1 for c in calibrations
            if c.calibration_direction == "overconfident"
        )
        underconfident = sum(
            1 for c in calibrations
            if c.calibration_direction == "underconfident"
        )
        well_calibrated = sum(
            1 for c in calibrations
            if c.calibration_direction == "well_calibrated"
        )

        total = len(calibrations)

        return {
            "overall_error": overall_error,
            "overconfidence_rate": overconfident / total,
            "underconfidence_rate": underconfident / total,
            "well_calibrated_rate": well_calibrated / total
        }

    def _assess_calibration_quality(self, metrics: dict, target_error: float) -> str:
        """Assess overall calibration quality."""
        overall_error = metrics.get("overall_error", 0.5)

        if overall_error <= target_error:
            return "excellent"
        elif overall_error <= target_error * 2:
            return "good"
        elif overall_error <= target_error * 3:
            return "fair"
        else:
            return "poor"

    def _generate_recommendations(self, metrics: dict) -> List[str]:
        """Generate calibration recommendations."""
        recommendations = []

        overconfidence_rate = metrics.get("overconfidence_rate", 0.0)
        underconfidence_rate = metrics.get("underconfidence_rate", 0.0)
        overall_error = metrics.get("overall_error", 0.0)

        # Overconfidence
        if overconfidence_rate > 0.5:
            recommendations.append(
                "Reduce confidence levels - showing systematic overconfidence"
            )

        # Underconfidence
        if underconfidence_rate > 0.5:
            recommendations.append(
                "Increase confidence levels - showing systematic underconfidence"
            )

        # High error
        if overall_error > 0.3:
            recommendations.append(
                "Significant calibration error - review confidence estimation methods"
            )

        # Well calibrated
        if metrics.get("well_calibrated_rate", 0.0) > 0.7:
            recommendations.append(
                "Calibration is good - maintain current confidence estimation"
            )

        return recommendations

    def _compute_confidence(
        self,
        calibrations: List[CalibrationResult],
        calibration_history: List[dict]
    ) -> float:
        """Compute confidence in calibration."""
        # More data = higher confidence

        base_confidence = min(1.0, 0.5 + len(calibration_history) * 0.01)

        # Boost if calibration is stable
        if len(calibrations) >= 10:
            avg_error = sum(c.calibration_error for c in calibrations) / len(calibrations)
            stability = 1.0 - avg_error
            stability_boost = stability * 0.3

            return min(1.0, base_confidence + stability_boost)

        return base_confidence
