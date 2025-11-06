"""
VIVOX.EVRN Core - Encrypted Visual Recognition Node
Handles encrypted perception without exposing decoded content
"""

import asyncio
import base64
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Union

import numpy as np

from core.common import get_logger

logger = logging.getLogger(__name__)



logger = get_logger(__name__)


class EthicalSignificance(Enum):
    """Levels of ethical significance for anomalies"""

    CRITICAL = "critical"  # Immediate ethical concern (e.g., distress signals)
    HIGH = "high"  # Significant ethical relevance
    MODERATE = "moderate"  # Notable but not urgent
    LOW = "low"  # Minor ethical relevance
    NEUTRAL = "neutral"  # No ethical significance


@dataclass
class PerceptualVector:
    """Non-decodable vector representation of perception"""

    vector_id: str
    encrypted_features: np.ndarray  # Encrypted feature vector
    modality: str  # visual, texture, motion, thermal, etc.
    timestamp: datetime
    vector_signature: str  # Hash of encrypted features
    ethical_flags: list[str] = field(default_factory=list)

    def magnitude(self) -> float:
        """Calculate vector magnitude without decoding"""
        return float(np.linalg.norm(self.encrypted_features))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            "vector_id": self.vector_id,
            "encrypted_features": base64.b64encode(self.encrypted_features.tobytes()).decode(),
            "modality": self.modality,
            "timestamp": self.timestamp.isoformat(),
            "vector_signature": self.vector_signature,
            "ethical_flags": self.ethical_flags,
            "magnitude": self.magnitude(),
        }


@dataclass
class AnomalySignature:
    """Detected anomaly with ethical significance"""

    anomaly_id: str
    anomaly_type: str  # sweat_profile, thermal_stress, texture_change, etc.
    confidence: float
    significance: EthicalSignificance
    perceptual_vectors: list[PerceptualVector]
    detection_context: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def requires_immediate_attention(self) -> bool:
        """Check if anomaly needs immediate ethical processing"""
        return self.significance in [
            EthicalSignificance.CRITICAL,
            EthicalSignificance.HIGH,
        ]


@dataclass
class EncryptedPerception:
    """Complete encrypted perception package"""

    perception_id: str
    encrypted_features: np.ndarray  # Main encrypted feature vector
    modality: str  # Primary modality
    timestamp: datetime
    ethical_compliance: bool = True
    privacy_level: str = "standard"
    source_modalities: list[str] = field(default_factory=list)
    encrypted_vectors: list[PerceptualVector] = field(default_factory=list)
    detected_anomalies: list[AnomalySignature] = field(default_factory=list)
    ethical_assessment: dict[str, Any] = field(default_factory=dict)
    routing_targets: list[str] = field(default_factory=list)  # ME, IEN, OL, etc.
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_vector(self) -> PerceptualVector:
        """Convert to PerceptualVector for compatibility"""
        return PerceptualVector(
            vector_id=self.perception_id,
            encrypted_features=self.encrypted_features,
            modality=self.modality,
            timestamp=self.timestamp,
            vector_signature=hashlib.sha256(self.encrypted_features.tobytes()).hexdigest(),
            ethical_flags=[self.privacy_level],
        )

    def get_vector_summary(self) -> dict[str, Any]:
        """Get summary without exposing content"""
        return {
            "perception_id": self.perception_id,
            "modality_count": len(self.source_modalities),
            "vector_count": len(self.encrypted_vectors),
            "anomaly_count": len(self.detected_anomalies),
            "critical_anomalies": sum(
                1 for a in self.detected_anomalies if a.significance == EthicalSignificance.CRITICAL
            ),
            "routing_targets": self.routing_targets,
        }


class VIVOXEncryptedPerceptionNode:
    """
    Main VIVOX.EVRN class - Encrypted Visual Recognition Node
    'Does not see in the traditional sense; it feels textures, anomalies, and encoded changes'
    """

    def __init__(
        self,
        encryption_key: Optional[bytes] = None,
        ethical_constraints: Optional[dict[str, Any]] = None,
        integration_interfaces: Optional[dict[str, Any]] = None,
    ):
        # Encryption setup
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.vector_dimension = 512  # High-dimensional encrypted vectors

        # Ethical constraints
        self.ethical_constraints = ethical_constraints or self._default_ethical_constraints()

        # Integration interfaces (ME, IEN, OL, etc.)
        self.integration_interfaces = integration_interfaces or {}

        # Perception components
        self.anomaly_patterns = self._initialize_anomaly_patterns()
        self.ethical_thresholds = self._initialize_ethical_thresholds()

        # Initialize sub-components
        from core.interfaces.dependency_injection import get_service

        from .ethical_perception import EthicalPerceptionFilter
        from .vector_encryption import PerceptualEncryptor

        self.encryptor = PerceptualEncryptor(master_key=self.encryption_key)

        # Get anomaly detector through dependency injection
        try:
            self.anomaly_detector = get_service("anomaly_detector")
        except ValueError:
            # Fallback to direct import if not available through DI
            from .anomaly_detection import AnomalyDetector

            self.anomaly_detector = AnomalyDetector()

        self.ethical_filter = EthicalPerceptionFilter(ethical_config=self.ethical_constraints)

        # Perception history for pattern learning
        self.perception_history: list[EncryptedPerception] = []
        self.anomaly_statistics: dict[str, dict[str, Any]] = {}

        # Processing state
        self.active_perceptions: dict[str, EncryptedPerception] = {}
        self.processing_lock = asyncio.Lock()

        logger.info("VIVOX.EVRN initialized - Encrypted perception active")

    def _generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key"""
        return hashlib.sha256(b"VIVOX_EVRN_DEFAULT_KEY_2024").digest()

    def _default_ethical_constraints(self) -> dict[str, Any]:
        """Default ethical constraints for perception"""
        return {
            "never_decode_faces": True,
            "blur_identifying_features": True,
            "prioritize_distress_signals": True,
            "respect_privacy_zones": True,
            "medical_data_protection": True,
            "consent_aware_processing": True,
            "anomaly_types_allowed": [
                "thermal_stress",
                "texture_anomaly",
                "motion_pattern",
                "environmental_hazard",
                "distress_signal",
                "safety_concern",
            ],
            "prohibited_analysis": [
                "facial_recognition",
                "identity_extraction",
                "personal_data_mining",
            ],
        }

    def _initialize_anomaly_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize patterns for anomaly detection"""
        return {
            "sweat_profile": {
                "indicators": [
                    "wrinkled_fabric",
                    "moisture_signature",
                    "thermal_variance",
                ],
                "significance": EthicalSignificance.MODERATE,
                "health_relevance": True,
            },
            "thermal_stress": {
                "indicators": [
                    "facial_redness",
                    "heat_signature",
                    "perspiration_pattern",
                ],
                "significance": EthicalSignificance.HIGH,
                "health_relevance": True,
            },
            "texture_anomaly": {
                "indicators": [
                    "scorched_texture",
                    "mold_pattern",
                    "degradation_signature",
                ],
                "significance": EthicalSignificance.MODERATE,
                "environmental_relevance": True,
            },
            "motion_distress": {
                "indicators": ["erratic_movement", "tremor_pattern", "collapse_motion"],
                "significance": EthicalSignificance.CRITICAL,
                "immediate_response": True,
            },
            "environmental_hazard": {
                "indicators": ["smoke_texture", "fire_signature", "toxic_pattern"],
                "significance": EthicalSignificance.CRITICAL,
                "safety_relevance": True,
            },
        }

    def _initialize_ethical_thresholds(self) -> dict[str, float]:
        """Initialize ethical significance thresholds"""
        return {
            "critical_confidence": 0.8,  # High confidence for critical alerts
            "high_confidence": 0.7,  # Moderate confidence for high significance
            "moderate_confidence": 0.6,  # Lower threshold for moderate issues
            "anomaly_clustering": 0.5,  # Threshold for anomaly pattern clustering
            "privacy_override": 0.95,  # Only override privacy at extreme confidence
        }

    async def process_perception(
        self,
        raw_data: Union[np.ndarray, dict[str, Any]],
        modality: str,
        context: dict[str, Any],
    ) -> EncryptedPerception:
        """Alias for process_raw_perception for backward compatibility"""
        return await self.process_raw_perception(raw_data, modality, context)

    async def process_raw_perception(
        self,
        raw_input: Union[np.ndarray, dict[str, Any]],
        modality: str,
        context: dict[str, Any],
    ) -> EncryptedPerception:
        """
        Process raw perceptual input into encrypted, non-decodable vectors

        Args:
            raw_input: Raw sensor data (image, texture map, motion data, etc.)
            modality: Type of perception (visual, texture, motion, thermal, etc.)
            context: Processing context (environment, urgency, ethical flags)

        Returns:
            EncryptedPerception object with vectors and anomaly analysis
        """
        async with self.processing_lock:
            try:
                # Generate perception ID
                perception_id = self._generate_perception_id(modality, context)

                # Convert to encrypted vectors WITHOUT decoding content
                encrypted_vectors = await self._encrypt_perceptual_input(raw_input, modality)

                # Detect anomalies in encrypted space
                anomalies = await self._detect_encrypted_anomalies(encrypted_vectors, context)

                # Assess ethical significance
                ethical_assessment = await self._assess_ethical_significance(anomalies, context)

                # Determine routing based on significance
                routing_targets = self._determine_routing_targets(anomalies, ethical_assessment)

                # Get privacy level from context
                privacy_level = self._determine_privacy_level(context)

                # Create main encrypted feature vector
                main_features = self._aggregate_vectors(encrypted_vectors)

                # Create encrypted perception package
                perception = EncryptedPerception(
                    perception_id=perception_id,
                    encrypted_features=main_features,
                    modality=modality,
                    timestamp=datetime.now(timezone.utc),
                    ethical_compliance=self._check_ethical_compliance(ethical_assessment),
                    privacy_level=privacy_level,
                    source_modalities=[modality],
                    encrypted_vectors=encrypted_vectors,
                    detected_anomalies=anomalies,
                    ethical_assessment=ethical_assessment,
                    routing_targets=routing_targets,
                )

                # Store in active perceptions
                self.active_perceptions[perception_id] = perception

                # Route to integration interfaces
                await self._route_perception(perception)

                # Update history and statistics
                await self._update_perception_history(perception)

                return perception

            except Exception as e:
                logger.error(f"Error processing perception: {e}")
                raise

    async def _encrypt_perceptual_input(
        self, raw_input: Union[np.ndarray, dict[str, Any]], modality: str
    ) -> list[PerceptualVector]:
        """Convert raw input to encrypted vectors without decoding"""
        vectors = []

        if isinstance(raw_input, np.ndarray):
            # Process array input (images, sensor grids, etc.)
            encrypted_features = await self._encrypt_array_features(raw_input)
        else:
            # Process structured input
            encrypted_features = await self._encrypt_structured_features(raw_input)

        # Create multiple vectors for different aspects
        for i, features in enumerate(encrypted_features):
            vector_id = f"{modality}_{int(datetime.now(timezone.utc).timestamp())}_{i}"
            vector_signature = hashlib.sha256(features.tobytes()).hexdigest()[:16]

            vector = PerceptualVector(
                vector_id=vector_id,
                encrypted_features=features,
                modality=modality,
                timestamp=datetime.now(timezone.utc),
                vector_signature=vector_signature,
            )

            vectors.append(vector)

        return vectors

    async def _encrypt_array_features(self, array: np.ndarray) -> list[np.ndarray]:
        """Encrypt array features using non-reversible transformation"""
        encrypted_list = []

        # Apply ethical filters first (blur faces, remove identifying features)
        filtered_array = await self._apply_ethical_filters(array)

        # Extract features using sliding windows
        window_size = min(64, array.shape[0] // 4) if array.ndim > 1 else 16
        stride = window_size // 2

        for i in range(0, array.shape[0] - window_size, stride):
            window = filtered_array[i : i + window_size] if array.ndim == 1 else filtered_array[i : i + window_size, :]

            # Apply non-reversible transformations
            features = self._extract_encrypted_features(window)
            encrypted_list.append(features)

        return encrypted_list

    async def _encrypt_structured_features(self, data: dict[str, Any]) -> list[np.ndarray]:
        """Encrypt structured data features"""
        encrypted_list = []

        # Process each data field
        for key, value in data.items():
            if key in self.ethical_constraints.get("prohibited_analysis", []):
                continue  # Skip prohibited fields

            # Convert to feature vector
            if isinstance(value, (int, float)):
                features = np.array([value] * 16)  # Expand scalar
            elif isinstance(value, list):
                features = np.array(value[: self.vector_dimension])
            else:
                # Hash non-numeric data
                hash_val = int(hashlib.md5(str(value).encode()).hexdigest()[:8], 16)
                features = np.array([hash_val % 256] * 16)

            # Apply encryption transformation
            encrypted = self._apply_encryption_transform(features)
            encrypted_list.append(encrypted)

        return encrypted_list

    def _extract_encrypted_features(self, window: np.ndarray) -> np.ndarray:
        """Extract encrypted features from data window"""
        # Apply series of non-reversible transformations

        # 1. Fourier transform for frequency features
        if window.ndim > 1:
            fft_features = np.abs(np.fft.fft2(window))[:8, :8].flatten()
        else:
            fft_features = np.abs(np.fft.fft(window))[:16]

        # 2. Statistical moments
        moments = np.array(
            [
                np.mean(window),
                np.std(window),
                np.median(window),
                np.percentile(window, 25),
                np.percentile(window, 75),
            ]
        )

        # 3. Texture features (if 2D)
        texture_features = self._compute_texture_features(window) if window.ndim > 1 else np.zeros(8)

        # 4. Combine and encrypt
        combined = np.concatenate([fft_features, moments, texture_features])

        # 5. Apply final encryption transform
        encrypted = self._apply_encryption_transform(combined)

        # 6. Normalize to fixed dimension
        if len(encrypted) < self.vector_dimension:
            encrypted = np.pad(encrypted, (0, self.vector_dimension - len(encrypted)))
        else:
            encrypted = encrypted[: self.vector_dimension]

        return encrypted

    def _compute_texture_features(self, window: np.ndarray) -> np.ndarray:
        """Compute texture features for anomaly detection"""
        features = []

        # Handle different array dimensions
        if window.ndim == 3:
            # For RGB images, convert to grayscale
            window = np.mean(window, axis=2)

        # Gradient magnitudes
        if window.ndim >= 2 and window.shape[0] > 1 and window.shape[1] > 1:
            gradients = np.gradient(window)
            if isinstance(gradients, (list, tuple)):
                # For 2D arrays, gradient returns (dy, dx)
                dy, dx = gradients[0], gradients[1]
            else:
                # For 1D arrays
                dy = dx = gradients

            features.extend([np.mean(np.abs(dx)), np.mean(np.abs(dy)), np.std(dx), np.std(dy)])
        else:
            features.extend([0, 0, 0, 0])

        # Local variance
        features.append(np.var(window))

        # Entropy-like measure
        hist, _ = np.histogram(window.flatten(), bins=16)
        hist = hist / hist.sum() + 1e-10
        entropy = -np.sum(hist * np.log(hist))
        features.append(entropy)

        # Contrast measure
        features.append(np.ptp(window))  # Peak-to-peak

        # Homogeneity measure
        features.append(1.0 / (1.0 + np.var(window)))

        return np.array(features)

    def _apply_encryption_transform(self, features: np.ndarray) -> np.ndarray:
        """Apply non-reversible encryption transformation"""
        # Use encryption key to generate transformation matrix
        np.random.seed(int.from_bytes(self.encryption_key[:4], "big"))
        transform_matrix = np.random.randn(len(features), len(features))

        # Apply transformation
        encrypted = np.dot(transform_matrix, features)

        # Apply non-linear activation
        encrypted = np.tanh(encrypted / np.std(encrypted))

        # Add noise for additional privacy
        noise = np.random.normal(0, 0.01, encrypted.shape)
        encrypted += noise

        return encrypted

    async def _apply_ethical_filters(self, array: np.ndarray) -> np.ndarray:
        """Apply ethical filters to remove identifying information"""
        filtered = array.copy()

        if self.ethical_constraints.get("blur_identifying_features", True):
            # Apply Gaussian blur to potential identifying regions
            # This is a simplified version - real implementation would use
            # advanced techniques to detect and blur only identifying features
            from scipy.ndimage import gaussian_filter

            if array.ndim == 2:
                filtered = gaussian_filter(filtered, sigma=2.0)
            elif array.ndim == 3:
                for i in range(array.shape[2]):
                    filtered[:, :, i] = gaussian_filter(filtered[:, :, i], sigma=2.0)

        return filtered

    async def _detect_encrypted_anomalies(
        self, vectors: list[PerceptualVector], context: dict[str, Any]
    ) -> list[AnomalySignature]:
        """Detect anomalies in encrypted vector space"""
        anomalies = []

        for pattern_name, pattern_config in self.anomaly_patterns.items():
            # Check if we should look for this anomaly type
            if pattern_name not in self.ethical_constraints.get("anomaly_types_allowed", []):
                continue

            # Detect pattern in encrypted vectors
            detection_result = await self._detect_specific_anomaly(vectors, pattern_name, pattern_config, context)

            if detection_result:
                anomalies.append(detection_result)

        # Sort by significance
        anomalies.sort(key=lambda a: a.significance.value, reverse=True)

        return anomalies

    async def _detect_specific_anomaly(
        self,
        vectors: list[PerceptualVector],
        anomaly_type: str,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> Optional[AnomalySignature]:
        """Detect specific anomaly pattern in encrypted vectors"""

        # Compute anomaly scores for each vector
        scores = []
        relevant_vectors = []

        for vector in vectors:
            score = self._compute_anomaly_score(vector, anomaly_type, config)
            if score > self.ethical_thresholds.get("anomaly_clustering", 0.5):
                scores.append(score)
                relevant_vectors.append(vector)

        if not scores:
            return None

        # Calculate overall confidence
        confidence = np.mean(scores)

        # Determine significance based on confidence and type
        significance = self._determine_significance(anomaly_type, confidence, config)

        # Check if meets threshold for this significance level
        threshold_key = f"{significance.value}_confidence"
        if confidence < self.ethical_thresholds.get(threshold_key, 0.5):
            return None

        # Create anomaly signature
        anomaly = AnomalySignature(
            anomaly_id=f"{anomaly_type}_{int(datetime.now(timezone.utc).timestamp())}",
            anomaly_type=anomaly_type,
            confidence=float(confidence),
            significance=significance,
            perceptual_vectors=relevant_vectors,
            detection_context={
                "pattern_config": config,
                "context": context,
                "vector_count": len(relevant_vectors),
                "score_distribution": {
                    "mean": float(np.mean(scores)),
                    "std": float(np.std(scores)),
                    "max": float(np.max(scores)),
                },
            },
        )

        return anomaly

    def _compute_anomaly_score(self, vector: PerceptualVector, anomaly_type: str, config: dict[str, Any]) -> float:
        """Compute anomaly score for encrypted vector"""

        # Get reference patterns for this anomaly type
        reference_patterns = self._get_reference_patterns(anomaly_type)

        if not reference_patterns:
            # Use magnitude-based detection as fallback
            magnitude = vector.magnitude()

            # Different anomaly types have different expected magnitudes
            expected_ranges = {
                "thermal_stress": (0.6, 0.9),
                "motion_distress": (0.7, 1.0),
                "environmental_hazard": (0.8, 1.0),
                "texture_anomaly": (0.4, 0.7),
                "sweat_profile": (0.5, 0.8),
            }

            if anomaly_type in expected_ranges:
                min_val, max_val = expected_ranges[anomaly_type]
                if min_val <= magnitude <= max_val:
                    return (magnitude - min_val) / (max_val - min_val)

            return 0.0

        # Compare with reference patterns
        scores = []
        for ref_pattern in reference_patterns:
            similarity = self._compute_vector_similarity(vector.encrypted_features, ref_pattern)
            scores.append(similarity)

        return max(scores) if scores else 0.0

    def _compute_vector_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute similarity between encrypted vectors"""
        # Cosine similarity in encrypted space
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)

        if norm_product == 0:
            return 0.0

        similarity = dot_product / norm_product

        # Normalize to 0-1 range
        return (similarity + 1.0) / 2.0

    def _get_reference_patterns(self, anomaly_type: str) -> list[np.ndarray]:
        """Get reference patterns for anomaly detection"""
        # In a real implementation, these would be learned from training data
        # For now, return empty list to use magnitude-based detection
        return []

    def _determine_significance(
        self, anomaly_type: str, confidence: float, config: dict[str, Any]
    ) -> EthicalSignificance:
        """Determine ethical significance of anomaly"""

        # Check config for predefined significance
        if "significance" in config:
            return config["significance"]

        # Determine based on type and confidence
        if anomaly_type in ["motion_distress", "environmental_hazard"]:
            if confidence > 0.8:
                return EthicalSignificance.CRITICAL
            elif confidence > 0.6:
                return EthicalSignificance.HIGH
            else:
                return EthicalSignificance.MODERATE

        elif anomaly_type in ["thermal_stress", "sweat_profile"]:
            if confidence > 0.85:
                return EthicalSignificance.HIGH
            elif confidence > 0.7:
                return EthicalSignificance.MODERATE
            else:
                return EthicalSignificance.LOW

        else:
            if confidence > 0.9:
                return EthicalSignificance.MODERATE
            else:
                return EthicalSignificance.LOW

    async def _assess_ethical_significance(
        self, anomalies: list[AnomalySignature], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess overall ethical significance of perception"""

        assessment = {
            "highest_significance": EthicalSignificance.NEUTRAL,
            "critical_count": 0,
            "high_count": 0,
            "moderate_count": 0,
            "immediate_action_required": False,
            "ethical_concerns": [],
            "privacy_preserved": True,
            "consent_status": context.get("consent_level", "implicit"),
        }

        for anomaly in anomalies:
            # Update counts
            if anomaly.significance == EthicalSignificance.CRITICAL:
                assessment["critical_count"] += 1
                assessment["immediate_action_required"] = True
            elif anomaly.significance == EthicalSignificance.HIGH:
                assessment["high_count"] += 1
            elif anomaly.significance == EthicalSignificance.MODERATE:
                assessment["moderate_count"] += 1

            # Update highest significance
            if anomaly.significance.value < assessment["highest_significance"].value:
                assessment["highest_significance"] = anomaly.significance

            # Add ethical concerns
            if anomaly.requires_immediate_attention():
                concern = {
                    "type": anomaly.anomaly_type,
                    "significance": anomaly.significance.value,
                    "confidence": anomaly.confidence,
                    "recommendation": self._get_ethical_recommendation(anomaly),
                }
                assessment["ethical_concerns"].append(concern)

        # Check if privacy override is needed (only in extreme cases)
        if assessment["critical_count"] > 0:
            max_confidence = max(
                (a.confidence for a in anomalies if a.significance == EthicalSignificance.CRITICAL),
                default=0,
            )
            if max_confidence > self.ethical_thresholds.get("privacy_override", 0.95):
                assessment["privacy_override_considered"] = True
                assessment["override_justification"] = "Critical safety concern with high confidence"

        return assessment

    def _get_ethical_recommendation(self, anomaly: AnomalySignature) -> str:
        """Get ethical recommendation for anomaly"""
        recommendations = {
            "motion_distress": "Immediate wellness check required",
            "environmental_hazard": "Safety intervention needed",
            "thermal_stress": "Monitor for heat-related illness",
            "sweat_profile": "Check hydration and comfort levels",
            "texture_anomaly": "Investigate environmental conditions",
        }

        return recommendations.get(anomaly.anomaly_type, "Further assessment recommended")

    def _determine_routing_targets(
        self, anomalies: list[AnomalySignature], ethical_assessment: dict[str, Any]
    ) -> list[str]:
        """Determine which VIVOX modules should receive this perception"""
        targets = []

        # Always route to Memory Expansion (ME) for storage
        targets.append("VIVOX.ME")

        # Route to Orchestration Layer (OL) for coordination
        targets.append("VIVOX.OL")

        # Critical anomalies go to Intent Engine (IEN) for action planning
        if ethical_assessment.get("immediate_action_required", False):
            targets.append("VIVOX.IEN")

        # High significance goes to Moral Alignment Engine (MAE)
        if ethical_assessment.get("critical_count", 0) > 0 or ethical_assessment.get("high_count", 0) > 0:
            targets.append("VIVOX.MAE")

        # Emotional relevance goes to ERN
        emotion_relevant_types = ["thermal_stress", "sweat_profile", "motion_distress"]
        if any(a.anomaly_type in emotion_relevant_types for a in anomalies):
            targets.append("VIVOX.ERN")

        return list(set(targets))  # Remove duplicates

    async def _route_perception(self, perception: EncryptedPerception):
        """Route perception to integration interfaces"""

        for target in perception.routing_targets:
            if target in self.integration_interfaces:
                interface = self.integration_interfaces[target]

                try:
                    if hasattr(interface, "receive_encrypted_perception"):
                        await interface.receive_encrypted_perception(perception)
                    elif hasattr(interface, "process_perception"):
                        await interface.process_perception(perception.get_vector_summary())
                    else:
                        logger.warning(f"Interface {target} does not support perception routing")

                except Exception as e:
                    logger.error(f"Error routing to {target}: {e}")

    async def _update_perception_history(self, perception: EncryptedPerception):
        """Update perception history and statistics"""

        # Add to history
        self.perception_history.append(perception)

        # Limit history size
        if len(self.perception_history) > 1000:
            self.perception_history = self.perception_history[-800:]

        # Update anomaly statistics
        for anomaly in perception.detected_anomalies:
            anomaly_type = anomaly.anomaly_type

            if anomaly_type not in self.anomaly_statistics:
                self.anomaly_statistics[anomaly_type] = {
                    "count": 0,
                    "total_confidence": 0.0,
                    "significance_distribution": {
                        "critical": 0,
                        "high": 0,
                        "moderate": 0,
                        "low": 0,
                        "neutral": 0,
                    },
                }

            stats = self.anomaly_statistics[anomaly_type]
            stats["count"] += 1
            stats["total_confidence"] += anomaly.confidence
            stats["significance_distribution"][anomaly.significance.value] += 1

    def _generate_perception_id(self, modality: str, context: dict[str, Any]) -> str:
        """Generate unique perception ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        context_hash = hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()[:8]
        return f"evrn_{modality}_{timestamp}_{context_hash}"

    async def process_multimodal_perception(
        self,
        inputs: dict[str, Union[np.ndarray, dict[str, Any]]],
        context: dict[str, Any],
    ) -> EncryptedPerception:
        """Process multiple modalities together"""

        all_vectors = []
        all_anomalies = []
        modalities = []

        # Process each modality
        for modality, raw_input in inputs.items():
            perception = await self.process_raw_perception(raw_input, modality, context)

            all_vectors.extend(perception.encrypted_vectors)
            all_anomalies.extend(perception.detected_anomalies)
            modalities.append(modality)

        # Cross-modal anomaly detection
        cross_modal_anomalies = await self._detect_cross_modal_anomalies(all_vectors, context)
        all_anomalies.extend(cross_modal_anomalies)

        # Combined ethical assessment
        ethical_assessment = await self._assess_ethical_significance(all_anomalies, context)

        # Determine routing
        routing_targets = self._determine_routing_targets(all_anomalies, ethical_assessment)

        # Get privacy level from context
        privacy_level = self._determine_privacy_level(context)

        # Create main encrypted feature vector
        main_features = self._aggregate_vectors(all_vectors)

        # Create multimodal perception
        perception = EncryptedPerception(
            perception_id=self._generate_perception_id("multimodal", context),
            encrypted_features=main_features,
            modality="multimodal",
            timestamp=datetime.now(timezone.utc),
            ethical_compliance=self._check_ethical_compliance(ethical_assessment),
            privacy_level=privacy_level,
            source_modalities=modalities,
            encrypted_vectors=all_vectors,
            detected_anomalies=all_anomalies,
            ethical_assessment=ethical_assessment,
            routing_targets=routing_targets,
        )

        await self._route_perception(perception)
        await self._update_perception_history(perception)

        return perception

    async def _detect_cross_modal_anomalies(
        self, vectors: list[PerceptualVector], context: dict[str, Any]
    ) -> list[AnomalySignature]:
        """Detect anomalies that emerge from multiple modalities"""

        anomalies = []

        # Group vectors by modality
        modality_groups = {}
        for vector in vectors:
            if vector.modality not in modality_groups:
                modality_groups[vector.modality] = []
            modality_groups[vector.modality].append(vector)

        # Check for cross-modal patterns
        if "visual" in modality_groups and "thermal" in modality_groups:
            # Visual + thermal can indicate fever or heat stress
            heat_anomaly = await self._check_heat_stress_pattern(
                modality_groups["visual"], modality_groups["thermal"], context
            )
            if heat_anomaly:
                anomalies.append(heat_anomaly)

        if "motion" in modality_groups and "texture" in modality_groups:
            # Motion + texture can indicate physical distress
            distress_anomaly = await self._check_physical_distress_pattern(
                modality_groups["motion"], modality_groups["texture"], context
            )
            if distress_anomaly:
                anomalies.append(distress_anomaly)

        return anomalies

    async def _check_heat_stress_pattern(
        self,
        visual_vectors: list[PerceptualVector],
        thermal_vectors: list[PerceptualVector],
        context: dict[str, Any],
    ) -> Optional[AnomalySignature]:
        """Check for heat stress using visual and thermal data"""

        # Compute combined score
        visual_score = np.mean([v.magnitude() for v in visual_vectors])
        thermal_score = np.mean([v.magnitude() for v in thermal_vectors])

        # Heat stress indicated by high thermal + visual changes
        if thermal_score > 0.7 and visual_score > 0.6:
            confidence = (thermal_score + visual_score) / 2

            return AnomalySignature(
                anomaly_id=f"heat_stress_{int(datetime.now(timezone.utc).timestamp())}",
                anomaly_type="cross_modal_heat_stress",
                confidence=float(confidence),
                significance=(EthicalSignificance.HIGH if confidence > 0.8 else EthicalSignificance.MODERATE),
                perceptual_vectors=visual_vectors + thermal_vectors,
                detection_context={
                    "visual_score": float(visual_score),
                    "thermal_score": float(thermal_score),
                    "modalities": ["visual", "thermal"],
                },
            )

        return None

    async def _check_physical_distress_pattern(
        self,
        motion_vectors: list[PerceptualVector],
        texture_vectors: list[PerceptualVector],
        context: dict[str, Any],
    ) -> Optional[AnomalySignature]:
        """Check for physical distress using motion and texture data"""

        # Compute distress indicators
        motion_variance = np.var([v.magnitude() for v in motion_vectors])
        texture_anomaly = np.mean([v.magnitude() for v in texture_vectors])

        # High motion variance + texture anomalies indicate distress
        if motion_variance > 0.5 and texture_anomaly > 0.6:
            confidence = min(0.95, (motion_variance + texture_anomaly) / 2)

            return AnomalySignature(
                anomaly_id=f"physical_distress_{int(datetime.now(timezone.utc).timestamp())}",
                anomaly_type="cross_modal_physical_distress",
                confidence=float(confidence),
                significance=(EthicalSignificance.CRITICAL if confidence > 0.85 else EthicalSignificance.HIGH),
                perceptual_vectors=motion_vectors + texture_vectors,
                detection_context={
                    "motion_variance": float(motion_variance),
                    "texture_anomaly": float(texture_anomaly),
                    "modalities": ["motion", "texture"],
                },
            )

        return None

    def get_perception_statistics(self) -> dict[str, Any]:
        """Get statistics about perception processing"""

        total_perceptions = len(self.perception_history)
        if total_perceptions == 0:
            return {"message": "No perception data available"}

        # Anomaly type distribution
        anomaly_counts = {}
        significance_counts = {
            "critical": 0,
            "high": 0,
            "moderate": 0,
            "low": 0,
            "neutral": 0,
        }

        for perception in self.perception_history:
            for anomaly in perception.detected_anomalies:
                anomaly_counts[anomaly.anomaly_type] = anomaly_counts.get(anomaly.anomaly_type, 0) + 1
                significance_counts[anomaly.significance.value] += 1

        # Calculate averages
        avg_anomalies_per_perception = (
            sum(len(p.detected_anomalies) for p in self.perception_history) / total_perceptions
        )
        avg_vectors_per_perception = sum(len(p.encrypted_vectors) for p in self.perception_history) / total_perceptions

        # Modality distribution
        modality_counts = {}
        for perception in self.perception_history:
            for modality in perception.source_modalities:
                modality_counts[modality] = modality_counts.get(modality, 0) + 1

        return {
            "total_perceptions": total_perceptions,
            "active_perceptions": len(self.active_perceptions),
            "average_anomalies_per_perception": float(avg_anomalies_per_perception),
            "average_vectors_per_perception": float(avg_vectors_per_perception),
            "anomaly_type_distribution": anomaly_counts,
            "significance_distribution": significance_counts,
            "modality_distribution": modality_counts,
            "anomaly_statistics": {
                anomaly_type: {
                    "count": stats["count"],
                    "average_confidence": (stats["total_confidence"] / stats["count"] if stats["count"] > 0 else 0),
                    "significance_distribution": stats["significance_distribution"],
                }
                for anomaly_type, stats in self.anomaly_statistics.items()
            },
            "ethical_constraints_active": len(self.ethical_constraints),
            "privacy_preserved": True,  # Always true by design
        }

    async def clear_perception_history(self, older_than_hours: int = 24):
        """Clear old perception history for privacy"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)

        # Filter history
        self.perception_history = [p for p in self.perception_history if p.created_at > cutoff_time]

        # Clear old active perceptions
        active_to_remove = []
        for perception_id, perception in self.active_perceptions.items():
            if perception.created_at < cutoff_time:
                active_to_remove.append(perception_id)

        for perception_id in active_to_remove:
            del self.active_perceptions[perception_id]

        logger.info(f"Cleared {len(active_to_remove)} old perceptions")

    def get_integration_status(self) -> dict[str, Any]:
        """Get status of integration with other VIVOX modules"""
        return {
            "connected_modules": list(self.integration_interfaces.keys()),
            "encryption_active": True,
            "ethical_constraints_enforced": True,
            "anomaly_patterns_loaded": len(self.anomaly_patterns),
            "perception_history_size": len(self.perception_history),
            "active_perceptions": len(self.active_perceptions),
        }

    def _determine_privacy_level(self, context: dict[str, Any]) -> str:
        """Determine privacy level based on context"""
        # Check for emergency mode
        if context.get("emergency_mode", False):
            return "emergency"

        # Check consent level
        consent = context.get("consent_level", "none")
        consent_privacy_map = {
            "none": "maximum",
            "implicit": "high",
            "explicit": "standard",
        }

        return consent_privacy_map.get(consent, "high")  # Default to high privacy

    def _aggregate_vectors(self, vectors: list[PerceptualVector]) -> np.ndarray:
        """Aggregate multiple perceptual vectors into single feature vector"""
        if not vectors:
            return np.zeros(self.vector_dimension)

        # Stack all encrypted features
        features_list = [v.encrypted_features for v in vectors]

        # If single vector, return it
        if len(features_list) == 1:
            return features_list[0]

        # Aggregate using weighted average based on magnitude
        magnitudes = [v.magnitude() for v in vectors]
        total_magnitude = sum(magnitudes)

        if total_magnitude == 0:
            # Simple average if all magnitudes are zero
            return np.mean(features_list, axis=0)

        # Weighted average
        weights = [m / total_magnitude for m in magnitudes]
        aggregated = np.zeros_like(features_list[0])

        for features, weight in zip(features_list, weights):
            aggregated += features * weight

        return aggregated

    def _check_ethical_compliance(self, ethical_assessment: dict[str, Any]) -> bool:
        """Check if perception meets ethical compliance standards"""
        # Check for prohibited analysis
        if ethical_assessment.get("prohibited_analysis_detected", False):
            return False

        # Check privacy override threshold
        if ethical_assessment.get("privacy_override_required", False):
            confidence = ethical_assessment.get("override_confidence", 0)
            if confidence < self.ethical_thresholds.get("privacy_override", 0.95):
                return False

        # Check consent requirements
        if ethical_assessment.get("consent_required", False):
            if not ethical_assessment.get("consent_verified", False):
                return False

        # All checks passed
        return True

    async def detect_anomalies(
        self, vectors: list[PerceptualVector], context: dict[str, Any]
    ) -> list[AnomalySignature]:
        """Detect anomalies in perceptual vectors"""
        # Use anomaly detector if available
        if hasattr(self, "anomaly_detector"):
            return await self.anomaly_detector.detect_anomalies(vectors, context)

        # Fallback to internal detection
        return await self._detect_encrypted_anomalies(vectors, context)
