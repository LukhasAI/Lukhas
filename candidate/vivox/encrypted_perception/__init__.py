"""
VIVOX.EVRN - Encrypted Visual Recognition Node
Handles encrypted perception with ethical privacy preservation
"""
import streamlit as st

from typing import Optional

from .anomaly_detection import AnomalyDetector, AnomalyType, SignificanceAnalyzer
from .ethical_perception import (
    EthicalPerceptionFilter,
    NonDecodableTransform,
    PrivacyPreservingVision,
)
from .sensory_integration import MotionDetector, MultimodalFusion, TextureAnalyzer
from .vector_encryption import EncryptionProtocol, PerceptualEncryptor, VectorSignature
from .vivox_evrn_core import (
    AnomalySignature,
    EncryptedPerception,
    EthicalSignificance,
    PerceptualVector,
    VIVOXEncryptedPerceptionNode,
)


# Main factory function
def create_vivox_evrn_system(
    encryption_key: Optional[bytes] = None,
    ethical_constraints: Optional[dict] = None,
    integration_interfaces: Optional[dict] = None,
) -> VIVOXEncryptedPerceptionNode:
    """
    Create a complete VIVOX.EVRN system

    Args:
        encryption_key: Encryption key for perceptual vectors
        ethical_constraints: Ethical boundaries for perception
        integration_interfaces: Connections to other VIVOX modules

    Returns:
        Fully configured VIVOX.EVRN system
    """
    return VIVOXEncryptedPerceptionNode(
        encryption_key=encryption_key,
        ethical_constraints=ethical_constraints,
        integration_interfaces=integration_interfaces,
    )


__all__ = [
    # Core classes
    "VIVOXEncryptedPerceptionNode",
    "PerceptualVector",
    "EncryptedPerception",
    "AnomalySignature",
    "EthicalSignificance",
    # Encryption
    "PerceptualEncryptor",
    "VectorSignature",
    "EncryptionProtocol",
    # Anomaly detection
    "AnomalyDetector",
    "AnomalyType",
    "SignificanceAnalyzer",
    # Ethical perception
    "EthicalPerceptionFilter",
    "PrivacyPreservingVision",
    "NonDecodableTransform",
    # Sensory integration
    "TextureAnalyzer",
    "MotionDetector",
    "MultimodalFusion",
    # Factory
    "create_vivox_evrn_system",
]
