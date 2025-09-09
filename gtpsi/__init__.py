"""
GTΨ (Gesture Token Psi) - Edge-Based Gesture Recognition
======================================================
Optional MFA/consent factor using gesture recognition for high-risk actions.

System-wide guardrails applied:
1. Store only hashed kinematic features + salt, never raw strokes
2. Edge-first processing - recognition happens on device
3. Time-locked approvals (≤60s) for specific actions
4. Complete audit trail for all gesture approvals
5. Cannot be bypassed for high-risk operations

ACK GUARDRAILS
"""

import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class GestureType(Enum):
    """Supported gesture types"""

    STROKE = "stroke"  # Finger/stylus stroke pattern
    TAP_SEQUENCE = "tap_seq"  # Tap rhythm pattern
    SWIPE_PATTERN = "swipe"  # Multi-finger swipe pattern
    SIGNATURE = "signature"  # Digital signature stroke


class RiskLevel(Enum):
    """Risk levels requiring GTΨ approval"""

    LOW = "low"  # No GTΨ required
    MEDIUM = "medium"  # Optional GTΨ
    HIGH = "high"  # GTΨ required
    CRITICAL = "critical"  # GTΨ + additional verification required


class GestureFeatures(BaseModel):
    """Hashed kinematic features (never raw gesture data)"""

    feature_hash: str = Field(..., description="Hashed kinematic features")
    salt: str = Field(..., description="Random salt for hashing")
    gesture_type: GestureType = Field(..., description="Type of gesture")
    feature_count: int = Field(..., description="Number of features extracted")
    quality_score: float = Field(..., description="Gesture quality (0.0-1.0)")
    timestamp: datetime = Field(..., description="When features were extracted")


class GestureChallenge(BaseModel):
    """Server-generated gesture challenge"""

    challenge_id: str = Field(..., description="Unique challenge identifier")
    lid: str = Field(..., description="Canonical ΛID")
    action: str = Field(..., description="Action requiring approval")
    action_context: dict[str, Any] = Field(..., description="Action-specific context")
    required_gesture_type: GestureType = Field(..., description="Required gesture type")
    expires_at: datetime = Field(..., description="Challenge expiration")
    nonce: str = Field(..., description="Cryptographic nonce")


class GestureApproval(BaseModel):
    """GTΨ approval record for specific action"""

    approval_id: str = Field(..., description="Unique approval identifier")
    challenge_id: str = Field(..., description="Associated challenge")
    lid: str = Field(..., description="User who approved")
    action: str = Field(..., description="Approved action")
    action_context: dict[str, Any] = Field(..., description="Specific action context")
    gesture_features: GestureFeatures = Field(..., description="Gesture used for approval")
    approved_at: datetime = Field(..., description="Approval timestamp")
    expires_at: datetime = Field(..., description="Approval expiration (≤60s)")
    used: bool = Field(False, description="Whether approval has been consumed")
    used_at: Optional[datetime] = Field(None, description="When approval was used")


# High-risk actions that require GTΨ approval
HIGH_RISK_ACTIONS = {
    "send_email": {
        "description": "Send email on behalf of user",
        "risk_level": RiskLevel.HIGH,
        "max_approval_seconds": 30,
    },
    "cloud.move.files": {
        "description": "Move files between cloud services",
        "risk_level": RiskLevel.HIGH,
        "max_approval_seconds": 60,
    },
    "share_link_public": {
        "description": "Share file/folder with public link",
        "risk_level": RiskLevel.CRITICAL,
        "max_approval_seconds": 20,
    },
    "delete_files": {
        "description": "Permanently delete files",
        "risk_level": RiskLevel.CRITICAL,
        "max_approval_seconds": 15,
    },
    "grant_admin_scope": {
        "description": "Grant administrative capabilities",
        "risk_level": RiskLevel.CRITICAL,
        "max_approval_seconds": 10,
    },
}


class GestureRecognizer(ABC):
    """
    Abstract base class for edge-based gesture recognizers.

    Implementation must run on-device and never transmit raw gesture data.
    Only hashed kinematic features are sent to server.
    """

    @abstractmethod
    def extract_features(self, raw_gesture_data: Any) -> list[float]:
        """Extract kinematic features from raw gesture data"""
        pass

    @abstractmethod
    def hash_features(self, features: list[float], salt: str) -> str:
        """Hash features with salt for privacy"""
        pass

    @abstractmethod
    def calculate_quality_score(self, features: list[float]) -> float:
        """Calculate gesture quality score (0.0-1.0)"""
        pass


class EdgeGestureProcessor:
    """
    Edge-first gesture processing that preserves privacy.

    Processes gestures on-device and only sends hashed features to server.
    Never stores or transmits raw stroke data.
    """

    def __init__(self, recognizer: GestureRecognizer):
        self.recognizer = recognizer

    def process_gesture(self, raw_gesture_data: Any, gesture_type: GestureType) -> GestureFeatures:
        """
        Process raw gesture and return hashed features.

        Args:
            raw_gesture_data: Raw gesture input (coordinates, timing, pressure)
            gesture_type: Type of gesture being processed

        Returns:
            GestureFeatures with hashed data only
        """
        # Extract kinematic features
        features = self.recognizer.extract_features(raw_gesture_data)

        # Generate random salt
        salt = secrets.token_urlsafe(32)

        # Hash features with salt
        feature_hash = self.recognizer.hash_features(features, salt)

        # Calculate quality
        quality_score = self.recognizer.calculate_quality_score(features)

        return GestureFeatures(
            feature_hash=feature_hash,
            salt=salt,
            gesture_type=gesture_type,
            feature_count=len(features),
            quality_score=quality_score,
            timestamp=datetime.now(timezone.utc),
        )


def requires_gtpsi_approval(action: str) -> bool:
    """Check if action requires GTΨ approval"""
    return action in HIGH_RISK_ACTIONS


def get_action_risk_level(action: str) -> RiskLevel:
    """Get risk level for action"""
    if action in HIGH_RISK_ACTIONS:
        return HIGH_RISK_ACTIONS[action]["risk_level"]
    return RiskLevel.LOW


def get_max_approval_time(action: str) -> int:
    """Get maximum approval time for action (seconds)"""
    if action in HIGH_RISK_ACTIONS:
        return HIGH_RISK_ACTIONS[action]["max_approval_seconds"]
    return 300  # Default 5 minutes


__all__ = [
    "HIGH_RISK_ACTIONS",
    "EdgeGestureProcessor",
    "GestureApproval",
    "GestureChallenge",
    "GestureFeatures",
    "GestureRecognizer",
    "GestureType",
    "RiskLevel",
    "get_action_risk_level",
    "get_max_approval_time",
    "requires_gtpsi_approval",
]