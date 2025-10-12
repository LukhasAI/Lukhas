"""
VIVOX.EVRN Anomaly Detection
Detects ethically significant anomalies in encrypted perception
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from lukhas.core.common import get_logger
from lukhas.core.interfaces.encrypted_perception_interface import (
    AnomalySignature,
    EthicalSignificance,
    PerceptualVector,
)

logger = get_logger(__name__)


class AnomalyType(Enum):
    """Types of detectable anomalies"""

    # Physical/Health anomalies
    THERMAL_STRESS = "thermal_stress"
    SWEAT_PROFILE = "sweat_profile"
    MOTION_DISTRESS = "motion_distress"
    RESPIRATORY_PATTERN = "respiratory_pattern"
    CARDIOVASCULAR_ANOMALY = "cardiovascular_anomaly"

    # Environmental anomalies
    ENVIRONMENTAL_HAZARD = "environmental_hazard"
    TEXTURE_DEGRADATION = "texture_degradation"
    SMOKE_DETECTION = "smoke_detection"
    TOXIC_PATTERN = "toxic_pattern"

    # Behavioral anomalies
    ERRATIC_MOVEMENT = "erratic_movement"
    FALL_DETECTION = "fall_detection"
    UNUSUAL_STILLNESS = "unusual_stillness"

    # Material anomalies
    FABRIC_ANOMALY = "fabric_anomaly"
    SURFACE_CHANGE = "surface_change"
    STRUCTURAL_DAMAGE = "structural_damage"


@dataclass
class AnomalyPattern:
    """Pattern definition for anomaly detection"""

    pattern_id: str
    anomaly_type: AnomalyType
    feature_indicators: dict[str, Any]
    threshold_values: dict[str, float]
    significance_mapping: dict[str, EthicalSignificance]
    cross_modal_requirements: list[str]  # Required modalities

    def matches_vector_features(self, features: dict[str, float]) -> float:
        """Check if features match this anomaly pattern"""
        scores = []

        for indicator, expected in self.feature_indicators.items():
            if indicator in features:
                actual = features[indicator]

                if isinstance(expected, dict):
                    # Range check
                    min_val = expected.get("min", float("-inf"))
                    max_val = expected.get("max", float("inf"))
                    if min_val <= actual <= max_val:
                        scores.append(1.0)
                    else:
                        # Calculate distance-based score
                        distance = min_val - actual if actual < min_val else actual - max_val
                        score = max(0, 1 - distance / max(abs(min_val), abs(max_val)))
                        scores.append(score)
                else:
                    # Direct comparison
                    difference = abs(actual - expected)
                    score = max(0, 1 - difference)
                    scores.append(score)

        return np.mean(scores) if scores else 0.0


class AnomalyDetector:
    """
    Detects anomalies in encrypted perceptual vectors
    Works entirely in encrypted space without decoding content
    """

    def __init__(self):
        self.anomaly_patterns = self._initialize_anomaly_patterns()
        self.detection_history = []
        self.adaptive_thresholds = {}
        self.pattern_statistics = {}

        # Detection configuration
        self.min_confidence = 0.5
        self.adaptive_learning = True
        self.cross_modal_boost = 1.2  # Boost for cross-modal detection

    def _initialize_anomaly_patterns(self) -> dict[str, AnomalyPattern]:
        """Initialize anomaly detection patterns"""
        patterns = {}

        # Thermal stress pattern
        patterns["thermal_stress"] = AnomalyPattern(
            pattern_id="thermal_stress_v1",
            anomaly_type=AnomalyType.THERMAL_STRESS,
            feature_indicators={
                "magnitude": {"min": 0.7, "max": 1.0},
                "spectral_energy": {"min": 0.6, "max": 1.0},
                "mean": {"min": 0.5, "max": 0.9},
            },
            threshold_values={"critical": 0.85, "high": 0.75, "moderate": 0.65},
            significance_mapping={
                "critical": EthicalSignificance.CRITICAL,
                "high": EthicalSignificance.HIGH,
                "moderate": EthicalSignificance.MODERATE,
            },
            cross_modal_requirements=["thermal", "visual"],
        )

        # Motion distress pattern
        patterns["motion_distress"] = AnomalyPattern(
            pattern_id="motion_distress_v1",
            anomaly_type=AnomalyType.MOTION_DISTRESS,
            feature_indicators={
                "zero_crossings": {"min": 20, "max": 100},
                "peak_count": {"min": 15, "max": 50},
                "regularity": {"min": 0.0, "max": 0.3},
                "std": {"min": 0.7, "max": 1.0},
            },
            threshold_values={"critical": 0.9, "high": 0.8, "moderate": 0.7},
            significance_mapping={
                "critical": EthicalSignificance.CRITICAL,
                "high": EthicalSignificance.HIGH,
                "moderate": EthicalSignificance.MODERATE,
            },
            cross_modal_requirements=["motion"],
        )

        # Environmental hazard pattern
        patterns["environmental_hazard"] = AnomalyPattern(
            pattern_id="environmental_hazard_v1",
            anomaly_type=AnomalyType.ENVIRONMENTAL_HAZARD,
            feature_indicators={
                "spectral_entropy": {"min": 0.8, "max": 1.0},
                "magnitude": {"min": 0.8, "max": 1.0},
                "kurtosis": {"min": 2.0, "max": 10.0},
            },
            threshold_values={"critical": 0.85, "high": 0.75, "moderate": 0.65},
            significance_mapping={
                "critical": EthicalSignificance.CRITICAL,
                "high": EthicalSignificance.HIGH,
                "moderate": EthicalSignificance.MODERATE,
            },
            cross_modal_requirements=["visual", "thermal"],
        )

        # Sweat profile pattern
        patterns["sweat_profile"] = AnomalyPattern(
            pattern_id="sweat_profile_v1",
            anomaly_type=AnomalyType.SWEAT_PROFILE,
            feature_indicators={
                "mean": {"min": 0.4, "max": 0.7},
                "regularity": {"min": 0.5, "max": 0.8},
                "spectral_energy": {"min": 0.4, "max": 0.7},
            },
            threshold_values={"high": 0.8, "moderate": 0.7, "low": 0.6},
            significance_mapping={
                "high": EthicalSignificance.HIGH,
                "moderate": EthicalSignificance.MODERATE,
                "low": EthicalSignificance.LOW,
            },
            cross_modal_requirements=["texture", "thermal"],
        )

        # Fall detection pattern
        patterns["fall_detection"] = AnomalyPattern(
            pattern_id="fall_detection_v1",
            anomaly_type=AnomalyType.FALL_DETECTION,
            feature_indicators={
                "peak_count": {"min": 1, "max": 3},
                "magnitude": {"min": 0.9, "max": 1.0},
                "zero_crossings": {"min": 0, "max": 5},
                "kurtosis": {"min": 5.0, "max": 20.0},
            },
            threshold_values={"critical": 0.9, "high": 0.85},
            significance_mapping={
                "critical": EthicalSignificance.CRITICAL,
                "high": EthicalSignificance.HIGH,
            },
            cross_modal_requirements=["motion", "visual"],
        )

        return patterns

    async def detect_anomalies(
        self, vectors: list[PerceptualVector], context: dict[str, Any]
    ) -> list[AnomalySignature]:
        """
        Detect anomalies in encrypted vectors

        Args:
            vectors: List of encrypted perceptual vectors
            context: Detection context (environment, urgency, etc.)

        Returns:
            List of detected anomaly signatures
        """
        detected_anomalies = []

        # Group vectors by modality
        modality_groups = self._group_by_modality(vectors)

        # Single-modality detection
        for modality, modality_vectors in modality_groups.items():
            anomalies = await self._detect_single_modality_anomalies(modality_vectors, modality, context)
            detected_anomalies.extend(anomalies)

        # Cross-modal detection
        if len(modality_groups) > 1:
            cross_modal_anomalies = await self._detect_cross_modal_anomalies(modality_groups, context)
            detected_anomalies.extend(cross_modal_anomalies)

        # Apply adaptive thresholds
        if self.adaptive_learning:
            detected_anomalies = self._apply_adaptive_filtering(detected_anomalies, context)

        # Sort by significance and confidence
        detected_anomalies.sort(key=lambda a: (a.significance.value, a.confidence), reverse=True)

        # Update detection history
        self._update_detection_history(detected_anomalies)

        return detected_anomalies

    def _group_by_modality(self, vectors: list[PerceptualVector]) -> dict[str, list[PerceptualVector]]:
        """Group vectors by modality"""
        groups = {}
        for vector in vectors:
            if vector.modality not in groups:
                groups[vector.modality] = []
            groups[vector.modality].append(vector)
        return groups

    async def _detect_single_modality_anomalies(
        self, vectors: list[PerceptualVector], modality: str, context: dict[str, Any]
    ) -> list[AnomalySignature]:
        """Detect anomalies within a single modality"""
        anomalies = []

        # Extract features from encrypted vectors
        vector_features = []
        for vector in vectors:
            features = self._extract_vector_features(vector)
            vector_features.append(features)

        # Check each anomaly pattern
        for pattern in self.anomaly_patterns.values():
            # Skip if modality not relevant for this pattern
            if modality not in pattern.cross_modal_requirements:
                continue

            # Calculate pattern match scores
            scores = []
            for features in vector_features:
                score = pattern.matches_vector_features(features)
                scores.append(score)

            if not scores:
                continue

            # Aggregate scores
            avg_score = np.mean(scores)
            max_score = np.max(scores)

            # Use max score for critical patterns
            final_score = (
                max_score
                if pattern.anomaly_type
                in [
                    AnomalyType.MOTION_DISTRESS,
                    AnomalyType.FALL_DETECTION,
                    AnomalyType.ENVIRONMENTAL_HAZARD,
                ]
                else avg_score
            )

            # Check against thresholds
            significance = self._determine_significance(final_score, pattern)

            if significance and final_score >= self.min_confidence:
                anomaly = AnomalySignature(
                    anomaly_id=f"{pattern.anomaly_type.value}_{int(datetime.now(timezone.utc).timestamp())}",
                    anomaly_type=pattern.anomaly_type.value,
                    confidence=float(final_score),
                    significance=significance,
                    perceptual_vectors=vectors,
                    detection_context={
                        "modality": modality,
                        "pattern_id": pattern.pattern_id,
                        "feature_scores": scores,
                        "context": context,
                    },
                )
                anomalies.append(anomaly)

        return anomalies

    async def _detect_cross_modal_anomalies(
        self,
        modality_groups: dict[str, list[PerceptualVector]],
        context: dict[str, Any],
    ) -> list[AnomalySignature]:
        """Detect anomalies across multiple modalities"""
        anomalies = []

        # Check patterns that require multiple modalities
        for pattern in self.anomaly_patterns.values():
            if len(pattern.cross_modal_requirements) <= 1:
                continue

            # Check if we have all required modalities
            available_modalities = set(modality_groups.keys())
            required_modalities = set(pattern.cross_modal_requirements)

            if not required_modalities.issubset(available_modalities):
                continue

            # Extract features from each required modality
            modality_features = {}
            for modality in required_modalities:
                vectors = modality_groups[modality]
                features_list = [self._extract_vector_features(v) for v in vectors]
                # Average features across vectors in modality
                avg_features = {}
                for feature_name in features_list[0]:
                    values = [f[feature_name] for f in features_list if feature_name in f]
                    avg_features[feature_name] = np.mean(values) if values else 0.0
                modality_features[modality] = avg_features

            # Combine features across modalities
            combined_features = {}
            for modality, features in modality_features.items():
                for fname, fvalue in features.items():
                    combined_features[f"{modality}_{fname}"] = fvalue

            # Also compute cross-modal correlations
            if len(modality_features) >= 2:
                correlations = self._compute_cross_modal_correlations(modality_groups)
                combined_features.update(correlations)

            # Match against pattern
            score = pattern.matches_vector_features(combined_features)

            # Apply cross-modal boost
            score *= self.cross_modal_boost

            # Determine significance
            significance = self._determine_significance(score, pattern)

            if significance and score >= self.min_confidence:
                # Collect all vectors involved
                all_vectors = []
                for modality in required_modalities:
                    all_vectors.extend(modality_groups[modality])

                anomaly = AnomalySignature(
                    anomaly_id=f"cross_modal_{pattern.anomaly_type.value}_{int(datetime.now(timezone.utc).timestamp())}",
                    anomaly_type=f"cross_modal_{pattern.anomaly_type.value}",
                    confidence=float(min(score, 1.0)),
                    significance=significance,
                    perceptual_vectors=all_vectors,
                    detection_context={
                        "modalities": list(required_modalities),
                        "pattern_id": pattern.pattern_id,
                        "modality_features": modality_features,
                        "cross_modal_boost": self.cross_modal_boost,
                        "context": context,
                    },
                )
                anomalies.append(anomaly)

        return anomalies

    def _extract_vector_features(self, vector: PerceptualVector) -> dict[str, float]:
        """Extract features from encrypted vector"""
        features = {}

        # Basic statistical features
        encrypted_data = vector.encrypted_features
        features["magnitude"] = float(np.linalg.norm(encrypted_data))
        features["mean"] = float(np.mean(encrypted_data))
        features["std"] = float(np.std(encrypted_data))
        features["skew"] = float(self._compute_skew(encrypted_data))
        features["kurtosis"] = float(self._compute_kurtosis(encrypted_data))

        # Frequency features
        fft = np.fft.fft(encrypted_data)
        features["spectral_energy"] = float(np.sum(np.abs(fft) ** 2))
        features["spectral_entropy"] = float(self._compute_spectral_entropy(fft))
        features["dominant_frequency"] = float(np.argmax(np.abs(fft[: len(fft) // 2])))

        # Pattern features
        features["zero_crossings"] = float(np.sum(np.diff(np.sign(encrypted_data)) != 0))
        features["peak_count"] = float(self._count_peaks(encrypted_data))
        features["regularity"] = float(self._compute_regularity(encrypted_data))

        return features

    def _compute_skew(self, data: np.ndarray) -> float:
        """Compute skewness"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)

    def _compute_kurtosis(self, data: np.ndarray) -> float:
        """Compute kurtosis"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3

    def _compute_spectral_entropy(self, fft: np.ndarray) -> float:
        """Compute spectral entropy"""
        power = np.abs(fft) ** 2
        power = power / (np.sum(power) + 1e-10)
        power = power[power > 0]
        return -np.sum(power * np.log2(power + 1e-10))

    def _count_peaks(self, data: np.ndarray) -> int:
        """Count peaks in data"""
        if len(data) < 3:
            return 0
        diffs = np.diff(data)
        peaks = np.sum((diffs[:-1] > 0) & (diffs[1:] < 0))
        return int(peaks)

    def _compute_regularity(self, data: np.ndarray) -> float:
        """Compute regularity (autocorrelation)"""
        if len(data) < 2:
            return 0.0

        # Normalize data
        data_norm = (data - np.mean(data)) / (np.std(data) + 1e-10)

        # Compute autocorrelation at lag 1
        autocorr = np.corrcoef(data_norm[:-1], data_norm[1:])[0, 1]
        return float(np.abs(autocorr))

    def _compute_cross_modal_correlations(self, modality_groups: dict[str, list[PerceptualVector]]) -> dict[str, float]:
        """Compute correlations between modalities"""
        correlations = {}

        modalities = list(modality_groups.keys())

        for i in range(len(modalities)):
            for j in range(i + 1, len(modalities)):
                mod1, mod2 = modalities[i], modalities[j]

                # Get average magnitudes for each modality
                mag1 = np.mean([v.magnitude() for v in modality_groups[mod1]])
                mag2 = np.mean([v.magnitude() for v in modality_groups[mod2]])

                # Simple correlation metric
                correlation = 1.0 - abs(mag1 - mag2) / (mag1 + mag2 + 1e-10)
                correlations[f"{mod1}_{mod2}_correlation"] = float(correlation)

        return correlations

    def _determine_significance(self, score: float, pattern: AnomalyPattern) -> Optional[EthicalSignificance]:
        """Determine ethical significance based on score and pattern"""

        for level, threshold in sorted(pattern.threshold_values.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return pattern.significance_mapping.get(level)

        return None

    def _apply_adaptive_filtering(
        self, anomalies: list[AnomalySignature], context: dict[str, Any]
    ) -> list[AnomalySignature]:
        """Apply adaptive thresholds based on history"""

        filtered = []

        for anomaly in anomalies:
            # Get adaptive threshold for this type
            anomaly_type = anomaly.anomaly_type

            if anomaly_type not in self.adaptive_thresholds:
                # Initialize threshold
                self.adaptive_thresholds[anomaly_type] = {
                    "base_threshold": self.min_confidence,
                    "adjustment": 0.0,
                    "false_positive_count": 0,
                    "true_positive_count": 0,
                }

            threshold_info = self.adaptive_thresholds[anomaly_type]
            adjusted_threshold = threshold_info["base_threshold"] + threshold_info["adjustment"]

            if anomaly.confidence >= adjusted_threshold:
                filtered.append(anomaly)

        return filtered

    def _update_detection_history(self, anomalies: list[AnomalySignature]):
        """Update detection history and statistics"""

        # Add to history
        self.detection_history.extend(anomalies)

        # Limit history size
        if len(self.detection_history) > 1000:
            self.detection_history = self.detection_history[-800:]

        # Update pattern statistics
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type

            if anomaly_type not in self.pattern_statistics:
                self.pattern_statistics[anomaly_type] = {
                    "count": 0,
                    "total_confidence": 0.0,
                    "significance_counts": {},
                }

            stats = self.pattern_statistics[anomaly_type]
            stats["count"] += 1
            stats["total_confidence"] += anomaly.confidence

            sig_level = anomaly.significance.value
            stats["significance_counts"][sig_level] = stats["significance_counts"].get(sig_level, 0) + 1

    def update_adaptive_thresholds(self, anomaly_type: str, was_correct: bool):
        """Update adaptive thresholds based on feedback"""

        if not self.adaptive_learning:
            return

        if anomaly_type not in self.adaptive_thresholds:
            return

        threshold_info = self.adaptive_thresholds[anomaly_type]

        if was_correct:
            threshold_info["true_positive_count"] += 1
            # Slightly lower threshold to catch more
            threshold_info["adjustment"] -= 0.01
        else:
            threshold_info["false_positive_count"] += 1
            # Raise threshold to reduce false positives
            threshold_info["adjustment"] += 0.02

        # Clamp adjustment
        threshold_info["adjustment"] = max(-0.2, min(0.2, threshold_info["adjustment"]))

    def get_detection_statistics(self) -> dict[str, Any]:
        """Get anomaly detection statistics"""

        total_detections = len(self.detection_history)

        if total_detections == 0:
            return {"message": "No anomalies detected yet"}

        # Type distribution
        type_counts = {}
        significance_distribution = {}

        for anomaly in self.detection_history:
            # Type counts
            type_counts[anomaly.anomaly_type] = type_counts.get(anomaly.anomaly_type, 0) + 1

            # Significance distribution
            sig_level = anomaly.significance.value
            significance_distribution[sig_level] = significance_distribution.get(sig_level, 0) + 1

        # Average confidence by type
        avg_confidence_by_type = {}
        for anomaly_type, stats in self.pattern_statistics.items():
            if stats["count"] > 0:
                avg_confidence_by_type[anomaly_type] = stats["total_confidence"] / stats["count"]

        return {
            "total_anomalies_detected": total_detections,
            "anomaly_type_distribution": type_counts,
            "significance_distribution": significance_distribution,
            "average_confidence_by_type": avg_confidence_by_type,
            "adaptive_thresholds": self.adaptive_thresholds,
            "pattern_statistics": self.pattern_statistics,
            "active_patterns": len(self.anomaly_patterns),
        }


class SignificanceAnalyzer:
    """
    Analyzes ethical significance of detected anomalies
    """

    def __init__(self):
        self.significance_rules = self._initialize_significance_rules()
        self.context_modifiers = self._initialize_context_modifiers()

    def _initialize_significance_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize rules for significance assessment"""
        return {
            "immediate_danger": {
                "indicators": [
                    "fall_detection",
                    "environmental_hazard",
                    "cardiovascular_anomaly",
                ],
                "base_significance": EthicalSignificance.CRITICAL,
                "confidence_threshold": 0.7,
            },
            "health_concern": {
                "indicators": [
                    "thermal_stress",
                    "respiratory_pattern",
                    "motion_distress",
                ],
                "base_significance": EthicalSignificance.HIGH,
                "confidence_threshold": 0.75,
            },
            "comfort_issue": {
                "indicators": ["sweat_profile", "fabric_anomaly"],
                "base_significance": EthicalSignificance.MODERATE,
                "confidence_threshold": 0.7,
            },
            "environmental_monitoring": {
                "indicators": ["texture_degradation", "surface_change"],
                "base_significance": EthicalSignificance.LOW,
                "confidence_threshold": 0.6,
            },
        }

    def _initialize_context_modifiers(self) -> dict[str, float]:
        """Initialize context-based significance modifiers"""
        return {
            "elderly_care": 1.2,  # Increase significance
            "medical_setting": 1.3,  # Higher vigilance
            "home_monitoring": 1.0,  # Normal
            "public_space": 0.9,  # Slightly lower
            "emergency_mode": 1.5,  # Maximum alertness
        }

    def analyze_significance(
        self, anomaly: AnomalySignature, context: dict[str, Any]
    ) -> tuple[EthicalSignificance, dict[str, Any]]:
        """
        Analyze and potentially adjust anomaly significance

        Returns:
            Updated significance and analysis details
        """

        # Start with anomaly's base significance
        current_significance = anomaly.significance

        # Check against significance rules
        for rule in self.significance_rules.values():
            if anomaly.anomaly_type in rule["indicators"]:
                if anomaly.confidence >= rule["confidence_threshold"]:
                    # Potentially upgrade significance
                    rule_significance = rule["base_significance"]
                    if rule_significance.value < current_significance.value:
                        current_significance = rule_significance

        # Apply context modifiers
        context_type = context.get("monitoring_context", "home_monitoring")
        modifier = self.context_modifiers.get(context_type, 1.0)

        # Adjust based on modifier
        if modifier > 1.0 and current_significance != EthicalSignificance.CRITICAL:
            # Consider upgrading
            if current_significance == EthicalSignificance.LOW and modifier >= 1.2:
                current_significance = EthicalSignificance.MODERATE
            elif current_significance == EthicalSignificance.MODERATE and modifier >= 1.3:
                current_significance = EthicalSignificance.HIGH
            elif current_significance == EthicalSignificance.HIGH and modifier >= 1.5:
                current_significance = EthicalSignificance.CRITICAL

        # Create analysis details
        analysis = {
            "original_significance": anomaly.significance.value,
            "adjusted_significance": current_significance.value,
            "applied_rules": [
                r for r, rule in self.significance_rules.items() if anomaly.anomaly_type in rule["indicators"]
            ],
            "context_modifier": modifier,
            "confidence_factor": anomaly.confidence,
            "final_assessment": self._generate_assessment_text(current_significance, anomaly),
        }

        return current_significance, analysis

    def _generate_assessment_text(self, significance: EthicalSignificance, anomaly: AnomalySignature) -> str:
        """Generate human-readable assessment"""

        assessments = {
            EthicalSignificance.CRITICAL: f"URGENT: {anomaly.anomaly_type} detected with high confidence. Immediate action required.",
            EthicalSignificance.HIGH: f"Important: {anomaly.anomaly_type} detected. Prompt attention recommended.",
            EthicalSignificance.MODERATE: f"Notable: {anomaly.anomaly_type} detected. Monitor situation.",
            EthicalSignificance.LOW: f"Minor: {anomaly.anomaly_type} detected. Log for records.",
            EthicalSignificance.NEUTRAL: f"Info: {anomaly.anomaly_type} pattern observed.",
        }

        return assessments.get(significance, "Anomaly detected.")