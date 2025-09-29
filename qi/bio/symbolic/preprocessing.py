"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧬 LUKHAS AI - BIO-PREPROCESSING COLONY
║ Advanced preprocessing for bio-symbolic coherence optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: preprocessing_colony.py
║ Path: bio/symbolic/preprocessing_colony.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS Bio-Symbolic Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════
"""
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np

from bio.core.symbolic_fallback_systems import get_fallback_manager
from lukhas.core.colonies.base_colony import BaseColony
from lukhas.core.symbolism.tags import TagPermission, TagScope

logger = logging.getLogger("ΛTRACE.bio.preprocessing", timezone)


class BioPreprocessingColony(BaseColony):
    """
    Specialized colony for bio-data preprocessing with ΛTAG propagation.
    Implements advanced signal processing and quality validation.
    """

    def __init__(self, colony_id: str = "bio_preprocessing_colony"):
        super().__init__(
            colony_id,
            capabilities=[
                "bio_normalization",
                "signal_cleaning",
                "coherence_prediction",
            ],
        )

        # Bio-signal validators
        self.bio_validators = {
            "heart_rate": {"min": 40, "max": 200, "unit": "bpm"},
            "temperature": {"min": 35.0, "max": 39.0, "unit": "°C"},
            "ph": {"min": 7.0, "max": 7.8, "unit": "pH"},
            "glucose": {"min": 50, "max": 200, "unit": "mg/dL"},
            "cortisol": {"min": 0, "max": 30, "unit": "μg/dL"},
            "atp_level": {"min": 0.0, "max": 1.0, "unit": "normalized"},
            "energy_level": {"min": 0.0, "max": 1.0, "unit": "normalized"},
        }

        # Rolling windows for temporal consistency
        self.signal_history = {signal: deque(maxlen=300) for signal in self.bio_validators}  # 5 minutes at 1Hz

        # Kalman filter states
        self.kalman_states = {}

        # Quality tags
        self.quality_tags = {
            "high": ("ΛQUALITY_HIGH", TagScope.LOCAL, TagPermission.PUBLIC, 1.0),
            "medium": ("ΛQUALITY_MEDIUM", TagScope.LOCAL, TagPermission.PUBLIC, 0.7),
            "low": ("ΛQUALITY_LOW", TagScope.LOCAL, TagPermission.PUBLIC, 0.4),
            "anomalous": ("ΛANOMALOUS", TagScope.LOCAL, TagPermission.PROTECTED, 0.1),
        }

        logger.info(f"🧬 BioPreprocessingColony '{colony_id}' initialized")

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute preprocessing task on bio-symbolic data.

        Args:
            task_id: Unique task identifier
            task_data: Raw biological data to preprocess

        Returns:
            Preprocessed data with quality tags
        """
        fallback_manager = get_fallback_manager()

        try:
            with self.tracer.trace_operation("preprocess_bio_data") as span:
                self.tracer.add_tag(span, "task_id", task_id)

                # Extract bio data
                bio_data = task_data.get("bio_data", {})

            # Stage 1: Signal Acquisition & Validation
            validated_data = await self._validate_signals(bio_data)

            # Stage 2: Noise Reduction via Kalman Filtering
            filtered_data = await self._kalman_filter(validated_data)

            # Stage 3: Outlier Detection
            outlier_scores = await self._detect_outliers(filtered_data)

            # Stage 4: Adaptive Normalization
            normalized_data = await self._adaptive_normalize(filtered_data)

            # Stage 5: Feature Enhancement
            enhanced_data = await self._enhance_features(normalized_data)

            # Stage 6: Quality Assessment
            quality_score = await self._assess_quality(enhanced_data, outlier_scores)

            # Tag the data
            quality_tag = self._assign_quality_tag(quality_score)
            self._apply_tag(*quality_tag)

            # Prepare result
            result = {
                "task_id": task_id,
                "preprocessed_data": enhanced_data,
                "quality_score": quality_score,
                "quality_tag": quality_tag[0],
                "outlier_scores": outlier_scores,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "colony_id": self.colony_id,
            }

            # Log preprocessing event
            self._log_preprocessing_event(result)

            return result

        except Exception as e:
            logger.warning(f"Preprocessing failed, activating fallback: {e!s}")
            return await fallback_manager.handle_component_failure("preprocessing", e, task_data, task_id)

    async def _validate_signals(self, bio_data: dict[str, Any]) -> dict[str, Any]:
        """Validate bio-signals against known ranges."""
        validated = {}

        for signal, value in bio_data.items():
            if signal in self.bio_validators:
                validator = self.bio_validators[signal]

                # Check range
                if validator["min"] <= value <= validator["max"]:
                    validated[signal] = value
                    # Add to history
                    self.signal_history[signal].append(value)
                else:
                    # Clamp to valid range
                    clamped = max(validator["min"], min(value, validator["max"]))
                    validated[signal] = clamped
                    logger.warning(
                        f"Signal '{signal}' out of range: {value} (clamped to {clamped} {validator['unit']})"
                    )
            else:
                # Unknown signal - pass through with warning
                validated[signal] = value
                logger.debug(f"Unknown signal type: {signal}")

        return validated

    async def _kalman_filter(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply Kalman filtering for noise reduction."""
        filtered = {}

        for signal, value in data.items():
            if signal not in self.kalman_states:
                # Initialize Kalman filter state
                self.kalman_states[signal] = {
                    "x": value,  # State estimate
                    "P": 1.0,  # Error covariance
                    "Q": 0.01,  # Process noise
                    "R": 0.1,  # Measurement noise
                }

            # Kalman filter update
            state = self.kalman_states[signal]

            # Prediction
            x_pred = state["x"]
            P_pred = state["P"] + state["Q"]

            # Update
            K = P_pred / (P_pred + state["R"])  # Kalman gain
            state["x"] = x_pred + K * (value - x_pred)
            state["P"] = (1 - K) * P_pred

            filtered[signal] = state["x"]

        return filtered

    async def _detect_outliers(self, data: dict[str, Any]) -> dict[str, float]:
        """Detect outliers using statistical methods."""
        outlier_scores = {}

        for signal, value in data.items():
            history = list(self.signal_history.get(signal, []))

            if len(history) > 10:  # Need sufficient history
                # Calculate statistics
                mean = np.mean(history)
                std = np.std(history)

                # Z-score for outlier detection
                if std > 0:
                    z_score = abs((value - mean) / std)
                    outlier_scores[signal] = min(z_score / 3.0, 1.0)  # Normalize to [0,1]
                else:
                    outlier_scores[signal] = 0.0
            else:
                # Not enough history - assume normal
                outlier_scores[signal] = 0.0

        return outlier_scores

    async def _adaptive_normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply adaptive normalization based on signal history."""
        normalized = {}

        for signal, value in data.items():
            if signal in self.bio_validators:
                validator = self.bio_validators[signal]

                # Min-max normalization to [0, 1]
                range_span = validator["max"] - validator["min"]
                if range_span > 0:
                    normalized[signal] = (value - validator["min"]) / range_span
                else:
                    normalized[signal] = 0.5
            else:
                # Pass through unknown signals
                normalized[signal] = value

        return normalized

    async def _enhance_features(self, data: dict[str, Any]) -> dict[str, Any]:
        """Enhance features using signal processing techniques."""
        enhanced = data.copy()

        # Add derived features
        if "heart_rate" in data:
            # Heart rate variability indicator
            hr_history = list(self.signal_history.get("heart_rate", []))
            if len(hr_history) > 2:
                hrv = np.std(np.diff(hr_history))
                enhanced["heart_rate_variability"] = hrv

        if "temperature" in data and "ph" in data:
            # Homeostatic balance indicator
            temp_dev = abs(data["temperature"] - 0.5)  # Normalized 37°C
            ph_dev = abs(data["ph"] - 0.5)  # Normalized 7.4
            enhanced["homeostatic_balance"] = 1.0 - (temp_dev + ph_dev) / 2

        if "cortisol" in data and "energy_level" in data:
            # Stress-energy index
            enhanced["stress_energy_index"] = (1 - data.get("cortisol", 0.5)) * data.get("energy_level", 0.5)

        return enhanced

    async def _assess_quality(self, data: dict[str, Any], outlier_scores: dict[str, float]) -> float:
        """Assess overall data quality."""
        quality_factors = []

        # Factor 1: Data completeness
        expected_signals = ["heart_rate", "temperature", "energy_level"]
        completeness = sum(1 for sig in expected_signals if sig in data) / len(expected_signals)
        quality_factors.append(completeness)

        # Factor 2: Outlier score (inverted)
        if outlier_scores:
            avg_outlier = np.mean(list(outlier_scores.values()))
            quality_factors.append(1 - avg_outlier)

        # Factor 3: Temporal consistency
        consistency_scores = []
        for signal, history in self.signal_history.items():
            if len(history) > 10 and signal in data:
                # Check if current value is consistent with recent history
                recent = list(history)[-10:]
                if np.std(recent) > 0:
                    deviation = abs(data[signal] - np.mean(recent)) / np.std(recent)
                    consistency_scores.append(1 / (1 + deviation))

        if consistency_scores:
            quality_factors.append(np.mean(consistency_scores))

        # Calculate overall quality score
        return np.mean(quality_factors) if quality_factors else 0.5

    def _assign_quality_tag(self, quality_score: float) -> tuple:
        """Assign quality tag based on score."""
        if quality_score >= 0.8:
            return self.quality_tags["high"]
        elif quality_score >= 0.6:
            return self.quality_tags["medium"]
        elif quality_score >= 0.4:
            return self.quality_tags["low"]
        else:
            return self.quality_tags["anomalous"]

    def _apply_tag(self, tag_name: str, scope: TagScope, permission: TagPermission, strength: float):
        """Apply symbolic tag to the colony state."""
        self.symbolic_carryover[tag_name] = (
            tag_name,
            scope,
            permission,
            strength,
            None,
        )
        self.tag_propagation_log.append(
            {
                "tag": tag_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "colony": self.colony_id,
                "action": "applied",
            }
        )

    def _log_preprocessing_event(self, result: dict[str, Any]):
        """Log preprocessing event for tracing."""
        event_data = {
            "colony_id": self.colony_id,
            "task_id": result["task_id"],
            "quality_score": result["quality_score"],
            "quality_tag": result["quality_tag"],
            "timestamp": result["timestamp"],
        }

        # Send to event store
        self.aggregate.raise_event("bio_preprocessing_complete", event_data)

        # Log with ΛTRACE
        logger.info(f"Preprocessed bio-data: quality={result['quality_score']:.2f}, tag={result['quality_tag']}")


# Colony instance factory
def create_preprocessing_colony(
    colony_id: Optional[str] = None,
) -> BioPreprocessingColony:
    """Create a new preprocessing colony instance."""
    return BioPreprocessingColony(colony_id or "bio_preprocessing_default")
