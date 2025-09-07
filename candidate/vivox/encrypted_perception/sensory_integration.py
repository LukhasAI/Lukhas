import logging
from datetime import timezone
import streamlit as st
logger = logging.getLogger(__name__)
"""
VIVOX.EVRN Sensory Integration
Processes multiple sensory modalities while maintaining encryption
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np

from candidate.core.common import get_logger

from .anomaly_detection import AnomalyDetector
from .vector_encryption import PerceptualEncryptor
from .vivox_evrn_core import EncryptedPerception, PerceptualVector

logger = get_logger(__name__, timezone)


class SensoryModality(Enum):
    """Types of sensory input"""

    VISUAL = "visual"
    THERMAL = "thermal"
    TEXTURE = "texture"
    MOTION = "motion"
    AUDIO = "audio"
    ENVIRONMENTAL = "environmental"


@dataclass
class TextureFeatures:
    """Features extracted from texture analysis"""

    roughness: float
    smoothness: float
    regularity: float
    complexity: float
    contrast: float
    homogeneity: float

    def to_vector(self) -> np.ndarray:
        """Convert to feature vector"""
        return np.array(
            [
                self.roughness,
                self.smoothness,
                self.regularity,
                self.complexity,
                self.contrast,
                self.homogeneity,
            ]
        )


@dataclass
class MotionFeatures:
    """Features extracted from motion analysis"""

    velocity: float
    acceleration: float
    jerk: float
    direction_changes: int
    trajectory_complexity: float
    stability: float

    def to_vector(self) -> np.ndarray:
        """Convert to feature vector"""
        return np.array(
            [
                self.velocity,
                self.acceleration,
                self.jerk,
                float(self.direction_changes),
                self.trajectory_complexity,
                self.stability,
            ]
        )


class TextureAnalyzer:
    """
    Analyzes texture patterns in encrypted space
    Detects fabric quality, surface anomalies, material degradation
    """

    def __init__(self, encryptor: Optional[PerceptualEncryptor] = None):
        self.encryptor = encryptor or PerceptualEncryptor()
        self.texture_patterns = self._initialize_texture_patterns()
        self.analysis_cache = {}

    def _initialize_texture_patterns(self) -> dict[str, Any]:
        """Initialize texture pattern library"""
        return {
            "fabric_smooth": {
                "roughness": (0.0, 0.3),
                "smoothness": (0.7, 1.0),
                "regularity": (0.8, 1.0),
            },
            "fabric_rough": {
                "roughness": (0.7, 1.0),
                "smoothness": (0.0, 0.3),
                "complexity": (0.6, 1.0),
            },
            "synthetic_material": {
                "homogeneity": (0.8, 1.0),
                "regularity": (0.7, 1.0),
                "contrast": (0.2, 0.5),
            },
            "natural_fabric": {
                "complexity": (0.5, 0.8),
                "homogeneity": (0.3, 0.7),
                "regularity": (0.4, 0.7),
            },
            "damaged_texture": {
                "roughness": (0.8, 1.0),
                "regularity": (0.0, 0.3),
                "homogeneity": (0.0, 0.4),
            },
        }

    async def analyze_texture(
        self, encrypted_data: np.ndarray, context: dict[str, Any]
    ) -> tuple[TextureFeatures, dict[str, Any]]:
        """
        Analyze texture from encrypted perceptual data

        Args:
            encrypted_data: Encrypted sensory input
            context: Analysis context

        Returns:
            Texture features and analysis metadata
        """
        # Extract encrypted features
        features = self._extract_texture_features(encrypted_data)

        # Match against known patterns
        pattern_matches = self._match_texture_patterns(features)

        # Detect anomalies
        anomalies = self._detect_texture_anomalies(features, context)

        # Create metadata
        metadata = {
            "pattern_matches": pattern_matches,
            "anomalies": anomalies,
            "confidence": self._calculate_confidence(features),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return features, metadata

    def _extract_texture_features(self, encrypted_data: np.ndarray) -> TextureFeatures:
        """Extract texture features from encrypted data"""

        # Compute spatial frequency analysis
        fft_2d = np.fft.fft2(encrypted_data.reshape(-1, int(np.sqrt(len(encrypted_data)))))
        power_spectrum = np.abs(fft_2d) ** 2

        # Roughness from high-frequency components
        high_freq = power_spectrum[len(power_spectrum) // 2 :, len(power_spectrum[0]) // 2 :]
        roughness = float(np.mean(high_freq) / (np.mean(power_spectrum) + 1e-10))

        # Smoothness from low-frequency dominance
        low_freq = power_spectrum[: len(power_spectrum) // 4, : len(power_spectrum[0]) // 4]
        smoothness = float(np.mean(low_freq) / (np.mean(power_spectrum) + 1e-10))

        # Regularity from autocorrelation
        autocorr = np.correlate(encrypted_data, encrypted_data, mode="same")
        regularity = float(np.std(autocorr) / (np.mean(autocorr) + 1e-10))

        # Complexity from entropy
        hist, _ = np.histogram(encrypted_data, bins=32)
        hist = hist / (np.sum(hist) + 1e-10)
        hist = hist[hist > 0]
        complexity = float(-np.sum(hist * np.log2(hist + 1e-10)) / np.log2(32))

        # Contrast from range
        contrast = float(np.ptp(encrypted_data) / (np.max(np.abs(encrypted_data)) + 1e-10))

        # Homogeneity from variance
        homogeneity = float(1.0 / (1.0 + np.var(encrypted_data)))

        return TextureFeatures(
            roughness=np.clip(roughness, 0, 1),
            smoothness=np.clip(smoothness, 0, 1),
            regularity=np.clip(regularity, 0, 1),
            complexity=np.clip(complexity, 0, 1),
            contrast=np.clip(contrast, 0, 1),
            homogeneity=np.clip(homogeneity, 0, 1),
        )

    def _match_texture_patterns(self, features: TextureFeatures) -> dict[str, float]:
        """Match features against known texture patterns"""
        matches = {}

        feature_dict = {
            "roughness": features.roughness,
            "smoothness": features.smoothness,
            "regularity": features.regularity,
            "complexity": features.complexity,
            "contrast": features.contrast,
            "homogeneity": features.homogeneity,
        }

        for pattern_name, pattern_def in self.texture_patterns.items():
            score = 0.0
            count = 0

            for feature_name, (min_val, max_val) in pattern_def.items():
                if feature_name in feature_dict:
                    value = feature_dict[feature_name]
                    if min_val <= value <= max_val:
                        score += 1.0
                    else:
                        # Partial score based on distance
                        if value < min_val:
                            score += max(0, 1 - (min_val - value) / min_val)
                        else:
                            score += max(0, 1 - (value - max_val) / (1 - max_val))
                    count += 1

            if count > 0:
                matches[pattern_name] = score / count

        return matches

    def _detect_texture_anomalies(self, features: TextureFeatures, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Detect anomalies in texture"""
        anomalies = []

        # Check for extreme values
        if features.roughness > 0.9 and features.regularity < 0.2:
            anomalies.append(
                {
                    "type": "severe_degradation",
                    "confidence": 0.8,
                    "features": {
                        "roughness": features.roughness,
                        "regularity": features.regularity,
                    },
                }
            )

        if features.homogeneity < 0.1:
            anomalies.append(
                {
                    "type": "material_inconsistency",
                    "confidence": 0.7,
                    "features": {"homogeneity": features.homogeneity},
                }
            )

        # Check for unusual combinations
        if features.smoothness > 0.8 and features.complexity > 0.8:
            anomalies.append(
                {
                    "type": "synthetic_anomaly",
                    "confidence": 0.6,
                    "features": {
                        "smoothness": features.smoothness,
                        "complexity": features.complexity,
                    },
                }
            )

        return anomalies

    def _calculate_confidence(self, features: TextureFeatures) -> float:
        """Calculate analysis confidence"""
        # Confidence based on feature consistency
        feature_values = features.to_vector()

        # Check if features are within expected ranges
        valid_count = np.sum((feature_values >= 0) & (feature_values <= 1))
        range_confidence = valid_count / len(feature_values)

        # Check feature correlation consistency
        correlation_confidence = 1.0 - np.std(feature_values)

        return float((range_confidence + correlation_confidence) / 2)


class MotionDetector:
    """
    Detects and analyzes motion patterns in encrypted space
    Identifies erratic movement, falls, unusual stillness
    """

    def __init__(self, encryptor: Optional[PerceptualEncryptor] = None):
        self.encryptor = encryptor or PerceptualEncryptor()
        self.motion_patterns = self._initialize_motion_patterns()
        self.motion_history = []
        self.max_history = 100

    def _initialize_motion_patterns(self) -> dict[str, Any]:
        """Initialize motion pattern library"""
        return {
            "normal_walking": {
                "velocity": (0.3, 0.7),
                "acceleration": (0.0, 0.3),
                "stability": (0.7, 1.0),
                "direction_changes": (0, 5),
            },
            "running": {
                "velocity": (0.7, 1.0),
                "acceleration": (0.2, 0.6),
                "stability": (0.5, 0.8),
                "jerk": (0.3, 0.7),
            },
            "fall_event": {
                "acceleration": (0.8, 1.0),
                "jerk": (0.8, 1.0),
                "stability": (0.0, 0.2),
                "trajectory_complexity": (0.0, 0.3),
            },
            "unusual_stillness": {
                "velocity": (0.0, 0.05),
                "acceleration": (0.0, 0.01),
                "direction_changes": (0, 1),
            },
            "erratic_movement": {
                "jerk": (0.7, 1.0),
                "direction_changes": (10, 100),
                "stability": (0.0, 0.3),
                "trajectory_complexity": (0.8, 1.0),
            },
        }

    async def detect_motion(
        self,
        encrypted_sequence: list[np.ndarray],
        time_delta: float,
        context: dict[str, Any],
    ) -> tuple[MotionFeatures, dict[str, Any]]:
        """
        Analyze motion from encrypted perceptual sequence

        Args:
            encrypted_sequence: Time series of encrypted vectors
            time_delta: Time between samples
            context: Detection context

        Returns:
            Motion features and detection metadata
        """
        # Extract motion features
        features = self._extract_motion_features(encrypted_sequence, time_delta)

        # Match against patterns
        pattern_matches = self._match_motion_patterns(features)

        # Detect critical events
        critical_events = self._detect_critical_motion_events(features, pattern_matches)

        # Update history
        self._update_motion_history(features)

        # Create metadata
        metadata = {
            "pattern_matches": pattern_matches,
            "critical_events": critical_events,
            "confidence": self._calculate_motion_confidence(features),
            "time_delta": time_delta,
            "sequence_length": len(encrypted_sequence),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return features, metadata

    def _extract_motion_features(self, sequence: list[np.ndarray], time_delta: float) -> MotionFeatures:
        """Extract motion features from encrypted sequence"""

        if len(sequence) < 2:
            return MotionFeatures(0, 0, 0, 0, 0, 1.0)

        # Convert to trajectory
        positions = np.array([self._estimate_position(vec) for vec in sequence])

        # Velocity estimation
        velocities = np.diff(positions, axis=0) / time_delta
        avg_velocity = float(np.mean(np.linalg.norm(velocities, axis=1)))

        # Acceleration estimation
        if len(velocities) > 1:
            accelerations = np.diff(velocities, axis=0) / time_delta
            avg_acceleration = float(np.mean(np.linalg.norm(accelerations, axis=1)))
        else:
            avg_acceleration = 0.0

        # Jerk estimation
        if len(velocities) > 2:
            jerks = np.diff(accelerations, axis=0) / time_delta
            avg_jerk = float(np.mean(np.linalg.norm(jerks, axis=1)))
        else:
            avg_jerk = 0.0

        # Direction changes
        if len(velocities) > 1:
            directions = velocities / (np.linalg.norm(velocities, axis=1, keepdims=True) + 1e-10)
            direction_changes = np.sum(np.linalg.norm(np.diff(directions, axis=0), axis=1) > 0.5)
        else:
            direction_changes = 0

        # Trajectory complexity
        if len(positions) > 2:
            # Use spectral entropy of trajectory
            fft = np.fft.fft(positions.flatten())
            power = np.abs(fft) ** 2
            power = power / (np.sum(power) + 1e-10)
            power = power[power > 0]
            trajectory_complexity = float(-np.sum(power * np.log2(power + 1e-10)) / np.log2(len(power)))
        else:
            trajectory_complexity = 0.0

        # Stability (inverse of variance)
        position_variance = np.var(positions)
        stability = float(1.0 / (1.0 + position_variance))

        return MotionFeatures(
            velocity=np.clip(avg_velocity, 0, 1),
            acceleration=np.clip(avg_acceleration, 0, 1),
            jerk=np.clip(avg_jerk, 0, 1),
            direction_changes=int(direction_changes),
            trajectory_complexity=np.clip(trajectory_complexity, 0, 1),
            stability=np.clip(stability, 0, 1),
        )

    def _estimate_position(self, encrypted_vector: np.ndarray) -> np.ndarray:
        """Estimate position from encrypted vector"""
        # Extract positional features without decryption
        # This is a simplified approach using statistical properties

        # Use first few components as proxy for position
        position_dims = min(3, len(encrypted_vector))
        position = encrypted_vector[:position_dims]

        # Normalize to unit space
        return position / (np.linalg.norm(position) + 1e-10)

    def _match_motion_patterns(self, features: MotionFeatures) -> dict[str, float]:
        """Match features against motion patterns"""
        matches = {}

        feature_dict = {
            "velocity": features.velocity,
            "acceleration": features.acceleration,
            "jerk": features.jerk,
            "direction_changes": features.direction_changes,
            "trajectory_complexity": features.trajectory_complexity,
            "stability": features.stability,
        }

        for pattern_name, pattern_def in self.motion_patterns.items():
            score = 0.0
            count = 0

            for feature_name, expected in pattern_def.items():
                if feature_name in feature_dict:
                    value = feature_dict[feature_name]

                    if isinstance(expected, tuple):
                        min_val, max_val = expected
                        if min_val <= value <= max_val:
                            score += 1.0
                        else:
                            # Distance-based partial score
                            if value < min_val:
                                score += max(0, 1 - (min_val - value) / (min_val + 1))
                            else:
                                score += max(0, 1 - (value - max_val) / (max_val + 1))
                    count += 1

            if count > 0:
                matches[pattern_name] = score / count

        return matches

    def _detect_critical_motion_events(
        self, features: MotionFeatures, pattern_matches: dict[str, float]
    ) -> list[dict[str, Any]]:
        """Detect critical motion events"""
        events = []

        # Fall detection
        if pattern_matches.get("fall_event", 0) > 0.7:
            events.append(
                {
                    "type": "fall_detected",
                    "severity": "critical",
                    "confidence": pattern_matches["fall_event"],
                    "features": {
                        "acceleration": features.acceleration,
                        "jerk": features.jerk,
                        "stability": features.stability,
                    },
                }
            )

        # Unusual stillness detection
        if pattern_matches.get("unusual_stillness", 0) > 0.8:
            # Check history for sudden change
            if self.motion_history and self.motion_history[-1].velocity > 0.3:
                events.append(
                    {
                        "type": "sudden_stillness",
                        "severity": "high",
                        "confidence": pattern_matches["unusual_stillness"],
                        "features": {
                            "velocity": features.velocity,
                            "previous_velocity": self.motion_history[-1].velocity,
                        },
                    }
                )

        # Erratic movement detection
        if pattern_matches.get("erratic_movement", 0) > 0.6:
            events.append(
                {
                    "type": "erratic_movement",
                    "severity": "moderate",
                    "confidence": pattern_matches["erratic_movement"],
                    "features": {
                        "jerk": features.jerk,
                        "direction_changes": features.direction_changes,
                        "trajectory_complexity": features.trajectory_complexity,
                    },
                }
            )

        return events

    def _update_motion_history(self, features: MotionFeatures):
        """Update motion history"""
        self.motion_history.append(features)

        # Limit history size
        if len(self.motion_history) > self.max_history:
            self.motion_history = self.motion_history[-self.max_history :]

    def _calculate_motion_confidence(self, features: MotionFeatures) -> float:
        """Calculate motion detection confidence"""
        # Base confidence on feature consistency
        feature_values = features.to_vector()

        # Remove direction changes from normalization
        normalized_features = feature_values[:3]  # velocity, acceleration, jerk
        normalized_features = np.append(normalized_features, feature_values[4:])  # trajectory_complexity, stability

        # Check physical plausibility
        physics_confidence = 1.0

        # Velocity should be reasonable
        if features.velocity > 1.0:
            physics_confidence *= 0.8

        # Acceleration should be consistent with velocity
        if features.acceleration > features.velocity * 2:
            physics_confidence *= 0.7

        # Jerk should be consistent with acceleration
        if features.jerk > features.acceleration * 2:
            physics_confidence *= 0.7

        # Feature range confidence
        range_confidence = np.mean((normalized_features >= 0) & (normalized_features <= 1))

        return float((physics_confidence + range_confidence) / 2)


class MultimodalFusion:
    """
    Fuses information from multiple sensory modalities
    Creates unified perception while maintaining encryption
    """

    def __init__(
        self,
        encryptor: Optional[PerceptualEncryptor] = None,
        anomaly_detector: Optional[AnomalyDetector] = None,
    ):
        self.encryptor = encryptor or PerceptualEncryptor()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.fusion_weights = self._initialize_fusion_weights()
        self.modality_correlations = {}

    def _initialize_fusion_weights(self) -> dict[str, dict[str, float]]:
        """Initialize fusion weights for different scenarios"""
        return {
            "default": {
                SensoryModality.VISUAL.value: 0.3,
                SensoryModality.THERMAL.value: 0.2,
                SensoryModality.TEXTURE.value: 0.2,
                SensoryModality.MOTION.value: 0.2,
                SensoryModality.AUDIO.value: 0.1,
            },
            "safety_critical": {
                SensoryModality.MOTION.value: 0.4,
                SensoryModality.THERMAL.value: 0.3,
                SensoryModality.VISUAL.value: 0.2,
                SensoryModality.AUDIO.value: 0.1,
            },
            "comfort_monitoring": {
                SensoryModality.THERMAL.value: 0.35,
                SensoryModality.TEXTURE.value: 0.35,
                SensoryModality.MOTION.value: 0.2,
                SensoryModality.VISUAL.value: 0.1,
            },
            "environmental": {
                SensoryModality.ENVIRONMENTAL.value: 0.4,
                SensoryModality.THERMAL.value: 0.3,
                SensoryModality.VISUAL.value: 0.2,
                SensoryModality.AUDIO.value: 0.1,
            },
        }

    async def fuse_modalities(
        self,
        perceptual_vectors: list[PerceptualVector],
        fusion_strategy: str = "default",
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[EncryptedPerception, dict[str, Any]]:
        """
        Fuse multiple sensory modalities into unified perception

        Args:
            perceptual_vectors: Vectors from different modalities
            fusion_strategy: Fusion strategy to use
            context: Fusion context

        Returns:
            Fused encrypted perception and metadata
        """
        if not perceptual_vectors:
            raise ValueError("No perceptual vectors provided for fusion")

        # Group by modality
        modality_groups = self._group_by_modality(perceptual_vectors)

        # Calculate cross-modal correlations
        correlations = self._calculate_cross_modal_correlations(modality_groups)
        self.modality_correlations = correlations

        # Apply fusion weights
        weights = self.fusion_weights.get(fusion_strategy, self.fusion_weights["default"])

        # Perform weighted fusion
        fused_vector = self._weighted_fusion(modality_groups, weights)

        # Detect cross-modal anomalies
        anomalies = await self._detect_cross_modal_anomalies(modality_groups, correlations)

        # Create fused perception
        fused_perception = EncryptedPerception(
            perception_id=f"fused_{datetime.now(timezone.utc).timestamp()}",
            encrypted_features=fused_vector,
            modality="multimodal",
            timestamp=datetime.now(timezone.utc),
            ethical_compliance=True,  # Ethical compliance is enforced at encryption level
            privacy_level="maximum",
        )

        # Create metadata
        metadata = {
            "fusion_strategy": fusion_strategy,
            "modalities_fused": list(modality_groups.keys()),
            "cross_modal_correlations": correlations,
            "anomalies_detected": anomalies,
            "fusion_confidence": self._calculate_fusion_confidence(correlations),
            "vector_count": len(perceptual_vectors),
        }

        return fused_perception, metadata

    def _group_by_modality(self, vectors: list[PerceptualVector]) -> dict[str, list[PerceptualVector]]:
        """Group vectors by modality"""
        groups = {}
        for vector in vectors:
            if vector.modality not in groups:
                groups[vector.modality] = []
            groups[vector.modality].append(vector)
        return groups

    def _calculate_cross_modal_correlations(
        self, modality_groups: dict[str, list[PerceptualVector]]
    ) -> dict[str, float]:
        """Calculate correlations between modalities"""
        correlations = {}
        modalities = list(modality_groups.keys())

        for i in range(len(modalities)):
            for j in range(i + 1, len(modalities)):
                mod1, mod2 = modalities[i], modalities[j]

                # Get representative vectors
                vec1 = self._get_representative_vector(modality_groups[mod1])
                vec2 = self._get_representative_vector(modality_groups[mod2])

                # Calculate correlation in encrypted space
                correlation = self._encrypted_correlation(vec1, vec2)
                correlations[f"{mod1}_{mod2}"] = correlation

        return correlations

    def _get_representative_vector(self, vectors: list[PerceptualVector]) -> np.ndarray:
        """Get representative vector for modality"""
        if len(vectors) == 1:
            return vectors[0].encrypted_features

        # Average vectors
        stacked = np.stack([v.encrypted_features for v in vectors])
        return np.mean(stacked, axis=0)

    def _encrypted_correlation(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate correlation in encrypted space"""
        # Normalize vectors
        norm1 = vec1 / (np.linalg.norm(vec1) + 1e-10)
        norm2 = vec2 / (np.linalg.norm(vec2) + 1e-10)

        # Cosine similarity
        similarity = np.dot(norm1, norm2)

        # Map to correlation coefficient range
        return float((similarity + 1) / 2)

    def _weighted_fusion(
        self,
        modality_groups: dict[str, list[PerceptualVector]],
        weights: dict[str, float],
    ) -> np.ndarray:
        """Perform weighted fusion of modalities"""
        fused = None
        total_weight = 0

        for modality, vectors in modality_groups.items():
            if modality in weights:
                weight = weights[modality]

                # Get representative vector
                rep_vector = self._get_representative_vector(vectors)

                if fused is None:
                    fused = weight * rep_vector
                else:
                    fused += weight * rep_vector

                total_weight += weight

        # Normalize by total weight
        if total_weight > 0:
            fused = fused / total_weight

        # Re-encrypt to ensure privacy
        fused, _ = self.encryptor.encrypt_vector(fused)

        return fused

    async def _detect_cross_modal_anomalies(
        self,
        modality_groups: dict[str, list[PerceptualVector]],
        correlations: dict[str, float],
    ) -> list[dict[str, Any]]:
        """Detect anomalies across modalities"""
        anomalies = []

        # Check for unusual correlation patterns
        for correlation_key, correlation_value in correlations.items():
            modalities = correlation_key.split("_")

            # Thermal-Motion correlation check
            if "thermal" in modalities and "motion" in modalities:
                if correlation_value > 0.8:  # High correlation
                    anomalies.append(
                        {
                            "type": "thermal_motion_correlation",
                            "severity": "high",
                            "correlation": correlation_value,
                            "interpretation": "High activity with thermal stress",
                        }
                    )

            # Visual-Texture mismatch
            if "visual" in modalities and "texture" in modalities:
                if correlation_value < 0.2:  # Low correlation
                    anomalies.append(
                        {
                            "type": "visual_texture_mismatch",
                            "severity": "moderate",
                            "correlation": correlation_value,
                            "interpretation": "Visual and texture data inconsistent",
                        }
                    )

        # Check individual modality anomalies
        for modality, vectors in modality_groups.items():
            if self.anomaly_detector:
                modality_anomalies = await self.anomaly_detector.detect_anomalies(vectors, {"modality": modality})

                for anomaly in modality_anomalies:
                    if anomaly.confidence > 0.7:
                        anomalies.append(
                            {
                                "type": f"{modality}_anomaly",
                                "severity": anomaly.significance.value,
                                "confidence": anomaly.confidence,
                                "details": anomaly.anomaly_type,
                            }
                        )

        return anomalies

    def _calculate_fusion_confidence(self, correlations: dict[str, float]) -> float:
        """Calculate confidence in fusion result"""
        if not correlations:
            return 0.5

        # Base confidence on correlation consistency
        correlation_values = list(correlations.values())

        # High variance in correlations indicates inconsistency
        correlation_variance = np.var(correlation_values)
        consistency_score = 1.0 / (1.0 + correlation_variance)

        # Average correlation indicates overall agreement
        avg_correlation = np.mean(correlation_values)

        # Combine scores
        confidence = (consistency_score + avg_correlation) / 2

        return float(np.clip(confidence, 0, 1))

    def get_fusion_statistics(self) -> dict[str, Any]:
        """Get statistics about fusion performance"""
        return {
            "available_strategies": list(self.fusion_weights.keys()),
            "last_correlations": self.modality_correlations,
            "supported_modalities": [m.value for m in SensoryModality],
        }


class SensoryCalibrator:
    """
    Calibrates sensory inputs for consistent encryption
    Ensures different sensors produce compatible encrypted vectors
    """

    def __init__(self):
        self.calibration_params = {}
        self.calibration_history = []

    def calibrate_sensor(
        self, sensor_id: str, raw_samples: list[np.ndarray], modality: SensoryModality
    ) -> dict[str, Any]:
        """
        Calibrate a sensor based on sample data

        Args:
            sensor_id: Unique sensor identifier
            raw_samples: Sample readings from sensor
            modality: Sensor modality type

        Returns:
            Calibration parameters
        """
        # Analyze sample statistics
        samples_array = np.array(raw_samples)

        calibration = {
            "sensor_id": sensor_id,
            "modality": modality.value,
            "offset": np.mean(samples_array, axis=0),
            "scale": np.std(samples_array, axis=0) + 1e-10,
            "range": {
                "min": np.min(samples_array, axis=0),
                "max": np.max(samples_array, axis=0),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store calibration
        self.calibration_params[sensor_id] = calibration
        self.calibration_history.append(calibration)

        return calibration

    def apply_calibration(self, sensor_id: str, raw_data: np.ndarray) -> np.ndarray:
        """Apply calibration to raw sensor data"""
        if sensor_id not in self.calibration_params:
            # Return uncalibrated data
            return raw_data

        calibration = self.calibration_params[sensor_id]

        # Apply calibration transform
        calibrated = (raw_data - calibration["offset"]) / calibration["scale"]

        return calibrated