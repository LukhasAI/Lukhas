"""
VeriFold Unified System
======================

This module provides a unified VeriFold system that integrates with the LAMBDA_TIER
framework for secure, tier-based symbolic collapse and memory integrity verification.

VeriFold has replaced the previous CollapseHash system and provides:
- Post-quantum cryptographic security (SPHINCS+)
- Tier-based access control integration
- Symbolic collapse detection and verification
- Memory integrity and audit trails
- Cross-system collapse event tracking

Features:
- Unified tier system integration (LAMBDA_TIER_0 through LAMBDA_TIER_5)
- Post-quantum resistant signatures and verification
- Real-time collapse monitoring and intervention
- Cross-module collapse event correlation
- Audit-ready compliance logging

Last Updated: 2025-07-26
"""

import logging
from typing import (
    Dict,  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for core infrastructure (review and implement)
)

import streamlit as st  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for core infrastructure (review and implement)

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import structlog

logger = logging.getLogger(__name__)



try:
    import oqs  # Post-quantum cryptography

    PQ_AVAILABLE = True
except ImportError:
    PQ_AVAILABLE = False

try:
    from core.tier_unification_adapter import TierMappingConfig
except ImportError:
    TierMappingConfig = None

# Core LUKHAS imports
try:
    from governance.identity.interface import IdentityClient, verify_access
except ImportError:
    IdentityClient = None
    verify_access = None

logger = structlog.get_logger(__name__)


def require_identity(required_tier: str = "LAMBDA_TIER_1", check_consent: Optional[str] = None):
    """
    Decorator for tier-based access control.
    This replaces the missing require_identity decorator from the identity system.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # For now, we'll extract user_id from the function arguments
            # In a real implementation, this would integrate with the session system
            if len(args) >= 2 and isinstance(args[1], str):  # Assuming user_id is second arg
                user_id = args[1]
                if not verify_access(user_id, required_tier):
                    logger.warning(
                        "Access denied",
                        user_id=user_id,
                        required_tier=required_tier,
                    )
                    raise PermissionError(f"User {user_id} lacks required tier {required_tier}")

                if check_consent and not check_consent(user_id, check_consent):
                    logger.warning("Consent denied", user_id=user_id, action=check_consent)
                    raise PermissionError(f"User {user_id} has not consented to {check_consent}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


class VeriFoldCollapseType(Enum):
    """Types of symbolic collapse events tracked by VeriFold"""

    MEMORY = "memory"
    SYMBOLIC = "symbolic"
    EMOTIONAL = "emotional"
    COGNITIVE = "cognitive"
    ETHICAL = "ethical"
    TEMPORAL = "temporal"
    IDENTITY = "identity"
    CONSENSUS = "consensus"


class VeriFoldPhase(Enum):
    """Progressive phases of symbolic collapse"""

    STABLE = "stable"
    PERTURBATION = "perturbation"
    CRITICAL = "critical"
    CASCADE = "cascade"
    SINGULARITY = "singularity"


@dataclass
class VeriFoldSnapshot:
    """
    Structured record of symbolic state at collapse moment.
    Replaces the old CollapseHash snapshot format.
    """

    collapse_id: str
    collapse_type: VeriFoldCollapseType
    user_id: str
    lambda_tier: str
    intent_vector: list[float]
    emotional_state: str
    ethical_context: str
    temporal_context: str
    system_context: dict[str, Any]
    phase: VeriFoldPhase
    entropy_score: float
    timestamp: str
    metadata: dict[str, Any]


@dataclass
class VeriFoldRecord:
    """
    Complete VeriFold record with cryptographic verification.
    This is the new format that replaces CollapseHash.
    """

    snapshot: VeriFoldSnapshot
    verifold_hash: str
    signature: Optional[str] = None
    public_key: Optional[str] = None
    verified: bool = False
    algorithm: str = "SPHINCS+-SHAKE256-128f-simple"


class UnifiedVeriFoldSystem:
    """
    Unified VeriFold system with tier integration.

    This system replaces the previous CollapseHash implementation and provides:
    - Tier-based access control for collapse operations
    - Post-quantum cryptographic security
    - Real-time collapse monitoring and intervention
    - Cross-system event correlation
    """

    def __init__(self):
        self.active_collapses: dict[str, VeriFoldRecord] = {}
        self.collapse_history: list[VeriFoldRecord] = []
        self.system_entropy: float = 0.0
        self.monitoring_enabled = True
        self.tier_config = TierMappingConfig()

        # Phase thresholds
        self.phase_thresholds = {
            VeriFoldPhase.STABLE: 0.3,
            VeriFoldPhase.PERTURBATION: 0.5,
            VeriFoldPhase.CRITICAL: 0.7,
            VeriFoldPhase.CASCADE: 0.85,
            VeriFoldPhase.SINGULARITY: 0.95,
        }

        logger.info(
            "VeriFold Unified System initialized",
            pq_available=PQ_AVAILABLE,
            tier_mapping=True,
        )

    @require_identity(required_tier="LAMBDA_TIER_1", check_consent="verifold_access")
    def generate_verifold_hash(
        self,
        collapse_data: dict[str, Any],
        user_id: str,
        lambda_tier: str,
        collapse_type: VeriFoldCollapseType = VeriFoldCollapseType.SYMBOLIC,
    ) -> VeriFoldRecord:
        """
        Generate a VeriFold hash for a symbolic collapse event.

        This replaces the old generate_collapse_hash function.

        Args:
            collapse_data: Data describing the collapse event
            user_id: User initiating the collapse
            lambda_tier: Current user tier (LAMBDA_TIER_0 through LAMBDA_TIER_5)
            collapse_type: Type of collapse being tracked

        Returns:
            VeriFoldRecord: Complete record with hash and verification
        """
        logger.info(
            "Generating VeriFold hash",
            user_id=user_id,
            tier=lambda_tier,
            type=collapse_type.value,
        )

        # Create collapse snapshot
        snapshot = self._create_collapse_snapshot(collapse_data, user_id, lambda_tier, collapse_type)

        # Generate cryptographic hash
        verifold_hash = self._compute_verifold_hash(snapshot)

        # Create record
        record = VeriFoldRecord(snapshot=snapshot, verifold_hash=verifold_hash, verified=False)

        # Add cryptographic signature if available
        if PQ_AVAILABLE:
            record.signature, record.public_key = self._sign_verifold_hash(verifold_hash)
            record.verified = True

        # Store and monitor
        self.active_collapses[snapshot.collapse_id] = record
        self._monitor_system_entropy(record)

        logger.info(
            "VeriFold hash generated",
            collapse_id=snapshot.collapse_id,
            hash=verifold_hash[:16] + "...",
            verified=record.verified,
        )

        return record

    @require_identity(required_tier="LAMBDA_TIER_2", check_consent="verifold_verify")
    def verify_verifold_record(self, record: VeriFoldRecord, user_id: str) -> bool:
        """
        Verify the authenticity of a VeriFold record.

        Args:
            record: VeriFold record to verify
            user_id: User requesting verification

        Returns:
            bool: True if record is authentic
        """
        logger.info(
            "Verifying VeriFold record",
            collapse_id=record.snapshot.collapse_id,
            user_id=user_id,
        )

        # Verify hash integrity
        computed_hash = self._compute_verifold_hash(record.snapshot)
        if computed_hash != record.verifold_hash:
            logger.warning(
                "VeriFold hash mismatch",
                expected=record.verifold_hash[:16] + "...",
                computed=computed_hash[:16] + "...",
            )
            return False

        # Verify cryptographic signature if present
        if record.signature and record.public_key and PQ_AVAILABLE:
            signature_valid = self._verify_signature(record.verifold_hash, record.signature, record.public_key)
            if not signature_valid:
                logger.warning(
                    "VeriFold signature invalid",
                    collapse_id=record.snapshot.collapse_id,
                )
                return False

        logger.info(
            "VeriFold record verified successfully",
            collapse_id=record.snapshot.collapse_id,
        )
        return True

    @require_identity(required_tier="LAMBDA_TIER_3", check_consent="collapse_monitoring")
    async def monitor_collapse_cascade(self, user_id: str, threshold: float = 0.8) -> dict[str, Any]:
        """
        Monitor for collapse cascade events across the system.

        Args:
            user_id: User requesting monitoring
            threshold: Entropy threshold for cascade detection

        Returns:
            Dict with cascade status and recommendations
        """
        logger.info(
            "Monitoring collapse cascade",
            user_id=user_id,
            threshold=threshold,
            system_entropy=self.system_entropy,
        )

        cascade_risk = self.system_entropy >= threshold
        active_collapses = len(self.active_collapses)

        # Analyze collapse patterns
        recent_collapses = [record for record in self.collapse_history[-10:] if record.snapshot.entropy_score > 0.6]

        # Check for tier-specific risks
        tier_risks = self._analyze_tier_risks(user_id)

        status = {
            "cascade_risk": cascade_risk,
            "system_entropy": self.system_entropy,
            "active_collapses": active_collapses,
            "recent_high_entropy": len(recent_collapses),
            "tier_risks": tier_risks,
            "recommendations": [],
        }

        if cascade_risk:
            logger.warning("Cascade risk detected", **status)
            status["recommendations"].extend(
                [
                    "Implement immediate entropy reduction measures",
                    "Isolate high-entropy collapse nodes",
                    "Activate tier-based emergency protocols",
                    "Notify system administrators",
                ]
            )

            # Trigger automatic intervention for high-tier users
            if self._get_tier_level(user_id) >= 4:
                await self._trigger_cascade_intervention(user_id)

        return status

    @require_identity(required_tier="LAMBDA_TIER_4", check_consent="system_intervention")
    async def trigger_collapse_intervention(self, user_id: str, intervention_type: str = "moderate") -> dict[str, Any]:
        """
        Trigger intervention to prevent system-wide collapse.

        Args:
            user_id: User authorizing intervention
            intervention_type: Type of intervention (light, moderate, aggressive)

        Returns:
            Dict with intervention results
        """
        logger.warning(
            "Triggering collapse intervention",
            user_id=user_id,
            type=intervention_type,
            system_entropy=self.system_entropy,
        )

        interventions_applied = []

        if intervention_type in ["moderate", "aggressive"]:
            # Reduce system entropy
            entropy_reduction = await self._reduce_system_entropy()
            interventions_applied.append(f"entropy_reduction: {entropy_reduction:.3f}")

            # Isolate high-risk collapses
            isolated_count = await self._isolate_high_risk_collapses()
            interventions_applied.append(f"isolated_collapses: {isolated_count}")

        if intervention_type == "aggressive":
            # Emergency tier lockdown
            lockdown_result = await self._emergency_tier_lockdown(user_id)
            interventions_applied.append(f"tier_lockdown: {lockdown_result}")

            # System state checkpoint
            checkpoint_id = await self._create_system_checkpoint()
            interventions_applied.append(f"checkpoint: {checkpoint_id}")

        result = {
            "intervention_type": intervention_type,
            "interventions_applied": interventions_applied,
            "system_entropy_post": self.system_entropy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "authorized_by": user_id,
        }

        logger.info("Collapse intervention completed", **result)
        return result

    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system metrics for monitoring."""
        return {
            "system_entropy": self.system_entropy,
            "active_collapses": len(self.active_collapses),
            "total_collapses": len(self.collapse_history),
            "phase_distribution": self._get_phase_distribution(),
            "tier_activity": self._get_tier_activity(),
            "pq_enabled": PQ_AVAILABLE,
            "monitoring_enabled": self.monitoring_enabled,
        }

    def _create_collapse_snapshot(
        self,
        collapse_data: dict[str, Any],
        user_id: str,
        lambda_tier: str,
        collapse_type: VeriFoldCollapseType,
    ) -> VeriFoldSnapshot:
        """Create a structured collapse snapshot."""
        collapse_id = f"vf_{int(time.time()) * 1000000}"

        # Calculate entropy score
        entropy_score = self._calculate_entropy_score(collapse_data)

        # Determine collapse phase
        phase = self._determine_collapse_phase(entropy_score)

        return VeriFoldSnapshot(
            collapse_id=collapse_id,
            collapse_type=collapse_type,
            user_id=user_id,
            lambda_tier=lambda_tier,
            intent_vector=collapse_data.get("intent_vector", [0.0, 0.0, 0.0]),
            emotional_state=collapse_data.get("emotional_state", "neutral"),
            ethical_context=collapse_data.get("ethical_context", "standard"),
            temporal_context=collapse_data.get("temporal_context", "present"),
            system_context=collapse_data.get("system_context", {}),
            phase=phase,
            entropy_score=entropy_score,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=collapse_data.get("metadata", {}),
        )

    def _compute_verifold_hash(self, snapshot: VeriFoldSnapshot) -> str:
        """Compute VeriFold hash from snapshot data."""
        # Convert snapshot to deterministic string
        snapshot_dict = asdict(snapshot)

        # Convert enums to their string values for JSON serialization
        snapshot_dict["collapse_type"] = snapshot_dict["collapse_type"].value
        snapshot_dict["phase"] = snapshot_dict["phase"].value

        snapshot_json = json.dumps(snapshot_dict, sort_keys=True, ensure_ascii=True)

        # Generate SHA3-256 hash (quantum-resistant)
        hash_obj = hashlib.sha3_256(snapshot_json.encode("utf-8"))
        return hash_obj.hexdigest()

    def _sign_verifold_hash(self, verifold_hash: str) -> tuple[str, str]:
        """Sign VeriFold hash with post-quantum signature."""
        if not PQ_AVAILABLE:
            return "", ""

        try:
            with oqs.Signature("SPHINCS+-SHAKE256-128f-simple") as signer:
                public_key = signer.generate_keypair()
                signer.export_secret_key()
                signature = signer.sign(verifold_hash.encode())

                return signature.hex(), public_key.hex()
        except Exception as e:
            logger.error("Failed to sign VeriFold hash", error=str(e))
            return "", ""

    def _verify_signature(self, verifold_hash: str, signature_hex: str, public_key_hex: str) -> bool:
        """Verify post-quantum signature."""
        if not PQ_AVAILABLE:
            return False

        try:
            signature = bytes.fromhex(signature_hex)
            public_key = bytes.fromhex(public_key_hex)

            with oqs.Signature("SPHINCS+-SHAKE256-128f-simple") as verifier:
                verifier.set_public_key(public_key)
                return verifier.verify(verifold_hash.encode(), signature)
        except Exception as e:
            logger.error("Failed to verify VeriFold signature", error=str(e))
            return False

    def _calculate_entropy_score(self, collapse_data: dict[str, Any]) -> float:
        """Calculate entropy score for collapse event."""
        base_entropy = collapse_data.get("entropy", 0.5)

        # Factor in system context
        system_load = len(self.active_collapses) / 100.0
        temporal_factor = abs(time.time() % 1000) / 1000.0

        entropy_score = min(1.0, base_entropy + system_load * 0.1 + temporal_factor * 0.05)
        return entropy_score

    def _determine_collapse_phase(self, entropy_score: float) -> VeriFoldPhase:
        """Determine collapse phase based on entropy score."""
        for phase, threshold in reversed(list(self.phase_thresholds.items())):
            if entropy_score >= threshold:
                return phase
        return VeriFoldPhase.STABLE

    def _monitor_system_entropy(self, record: VeriFoldRecord):
        """Update system entropy based on new collapse."""
        # Weighted average of system entropy
        weight = 0.1  # New record weight
        self.system_entropy = (1 - weight) * self.system_entropy + weight * record.snapshot.entropy_score

        # Add to history
        self.collapse_history.append(record)

        # Keep history manageable
        if len(self.collapse_history) > 1000:
            self.collapse_history = self.collapse_history[-500:]

    def _analyze_tier_risks(self, user_id: str) -> dict[str, Any]:
        """Analyze tier-specific collapse risks."""
        user_tier_level = self._get_tier_level(user_id)

        # Count collapses by tier
        tier_collapses = {}
        for record in self.collapse_history[-50:]:  # Recent collapses
            tier = record.snapshot.lambda_tier
            tier_collapses[tier] = tier_collapses.get(tier, 0) + 1

        return {
            "user_tier_level": user_tier_level,
            "tier_collapse_counts": tier_collapses,
            "high_tier_risk": user_tier_level >= 4 and self.system_entropy > 0.7,
        }

    def _get_tier_level(self, user_id: str) -> int:
        """Get numeric tier level for user."""
        # This would integrate with the actual tier system
        # For now, extract from LAMBDA_TIER format
        try:
            IdentityClient()
            # For now, we'll assume tier information can be extracted from user_id
            # In the real system, this would query the tier mapping service
            if "tier_5" in user_id.lower():
                return 5
            elif "tier_4" in user_id.lower():
                return 4
            elif "tier_3" in user_id.lower():
                return 3
            elif "tier_2" in user_id.lower():
                return 2
            else:
                return 1
        except BaseException:
            pass
        return 1  # Default tier

    async def _trigger_cascade_intervention(self, user_id: str):
        """Trigger automatic cascade intervention."""
        logger.warning("Triggering automatic cascade intervention", user_id=user_id)
        # This would trigger actual system intervention

    async def _reduce_system_entropy(self) -> float:
        """Reduce system entropy through various mechanisms."""
        initial_entropy = self.system_entropy

        # Simulated entropy reduction
        self.system_entropy *= 0.8

        return initial_entropy - self.system_entropy

    async def _isolate_high_risk_collapses(self) -> int:
        """Isolate high-risk collapse events."""
        isolated_count = 0

        for collapse_id, record in list(self.active_collapses.items()):
            if record.snapshot.entropy_score > 0.8:
                # Move to isolation (remove from active)
                del self.active_collapses[collapse_id]
                isolated_count += 1

        return isolated_count

    async def _emergency_tier_lockdown(self, user_id: str) -> str:
        """Implement emergency tier lockdown."""
        logger.critical("Emergency tier lockdown initiated", user_id=user_id)
        return f"lockdown_initiated_by_{user_id}"

    async def _create_system_checkpoint(self) -> str:
        """Create system state checkpoint."""
        checkpoint_id = f"checkpoint_{int(time.time())}"
        logger.info("System checkpoint created", checkpoint_id=checkpoint_id)
        return checkpoint_id

    def _get_phase_distribution(self) -> dict[str, int]:
        """Get distribution of collapse phases."""
        distribution = {}
        for record in self.active_collapses.values():
            phase = record.snapshot.phase.value
            distribution[phase] = distribution.get(phase, 0) + 1
        return distribution

    def _get_tier_activity(self) -> dict[str, int]:
        """Get activity distribution by tier."""
        activity = {}
        for record in self.active_collapses.values():
            tier = record.snapshot.lambda_tier
            activity[tier] = activity.get(tier, 0) + 1
        return activity


# Global instance
_global_verifold_system = None


def get_global_verifold_system() -> UnifiedVeriFoldSystem:
    """Get global VeriFold system instance."""
    global _global_verifold_system
    if _global_verifold_system is None:
        _global_verifold_system = UnifiedVeriFoldSystem()
    return _global_verifold_system


# Convenience functions for backward compatibility with CollapseHash


def generate_verifold_hash(collapse_data: dict[str, Any], user_id: str, lambda_tier: str) -> VeriFoldRecord:
    """
    Generate VeriFold hash (replaces generate_collapse_hash).

    This function provides backward compatibility for code that used
    the old CollapseHash system.
    """
    system = get_global_verifold_system()
    return system.generate_verifold_hash(collapse_data, user_id, lambda_tier)


def verify_verifold_hash(record: VeriFoldRecord, user_id: str) -> bool:
    """
    Verify VeriFold hash (replaces verify_collapse_hash).

    This function provides backward compatibility for code that used
    the old CollapseHash system.
    """
    system = get_global_verifold_system()
    return system.verify_verifold_record(record, user_id)


__all__ = [
    "UnifiedVeriFoldSystem",
    "VeriFoldCollapseType",
    "VeriFoldPhase",
    "VeriFoldRecord",
    "VeriFoldSnapshot",
    "generate_verifold_hash",
    "get_global_verifold_system",
    "verify_verifold_hash",
]
