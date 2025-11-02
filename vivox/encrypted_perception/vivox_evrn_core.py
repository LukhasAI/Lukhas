"""
VIVOX.EVRN Core - Encrypted Visual Recognition Node
Handles encrypted perception without exposing decoded content
"""

import logging
import asyncio
import base64
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Union
import numpy as np
from core.common import get_logger
        from core.interfaces.dependency_injection import get_service
        from .ethical_perception import EthicalPerceptionFilter
        from .vector_encryption import PerceptualEncryptor
        try:
            from .anomaly_detection import AnomalyDetector
            try:
            from scipy.ndimage import gaussian_filter
                try:

logger = logging.getLogger(__name__)

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
        if consent == "none":
            return "maximum"
        elif consent == "implicit":
            return "high"
        elif consent == "explicit":
            return "standard"

        # Default to high privacy
        return "high"

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
