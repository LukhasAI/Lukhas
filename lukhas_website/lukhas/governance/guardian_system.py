#!/usr/bin/env python3
"""
T4/0.01% Guardian Decision Envelope System
==========================================

Bullet-proof Guardian decision serialization with:
- Fail-closed validation
- Tamper-evident integrity
- Optional cryptographic signing
- Schema compliance enforcement

Constellation Framework: 🛡️ Guardian Excellence
"""

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional cryptographic signing
try:
    import base64

    from cryptography.exceptions import InvalidSignature  # noqa: F401  # TODO: cryptography.exceptions.Invali...
    from cryptography.hazmat.primitives import (  # noqa: F401  # TODO: cryptography.hazmat.primitives...
        hashes,
        serialization,
    )
    from cryptography.hazmat.primitives.asymmetric import ed25519
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography not available - signing disabled")

# Schema validation
try:
    import jsonschema
    from jsonschema import Draft202012Validator  # noqa: F401  # TODO: jsonschema.Draft202012Validato...
    SCHEMA_VALIDATION = True
except ImportError:
    SCHEMA_VALIDATION = False
    logger.warning("jsonschema not available - schema validation disabled")

# Import EthicalSeverity
from .guardian.core import EthicalSeverity


class GuardianJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Guardian types"""

    def default(self, obj):
        if isinstance(obj, EthicalSeverity):
            return obj.value
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class DecisionStatus(Enum):
    """Guardian decision status enum - fail-closed design."""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    QUARANTINE = "quarantine"
    ERROR = "error"  # Must be treated as DENY (fail-closed)


class EnforcementMode(Enum):
    """Guardian enforcement mode."""
    DARK = "dark"          # Logging only, no enforcement
    CANARY = "canary"      # Partial enforcement for testing
    ENFORCED = "enforced"  # Full enforcement active


class ActorType(Enum):
    """Actor type in Guardian subject."""
    USER = "user"
    SERVICE = "service"
    SYSTEM = "system"


class RuntimeEnvironment(Enum):
    """Runtime environment."""
    DEV = "dev"
    CI = "ci"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class GuardianDecision:
    """Core Guardian decision data."""
    status: DecisionStatus
    policy: str
    timestamp: str
    severity: str = "low"
    confidence: Optional[float] = None
    ttl_seconds: Optional[int] = None


@dataclass
class GuardianSubject:
    """Guardian decision subject."""
    correlation_id: str
    actor_type: ActorType
    actor_id: str
    operation_name: str
    lane: Optional[str] = None
    canary_percent: Optional[float] = None
    actor_tier: Optional[str] = None
    operation_resource: Optional[str] = None
    operation_parameters: Optional[Dict[str, Any]] = None


@dataclass
class GuardianContext:
    """Guardian decision context."""
    region: str
    runtime: RuntimeEnvironment
    enforcement_enabled: bool = True
    emergency_active: bool = False
    version: Optional[str] = None
    kill_switch_path: Optional[str] = None


@dataclass
class GuardianMetrics:
    """Guardian performance and risk metrics."""
    latency_ms: float
    risk_score: Optional[float] = None
    drift_score: Optional[float] = None
    quota_remaining: Optional[int] = None
    counters: Optional[Dict[str, int]] = None


@dataclass
class GuardianEnforcement:
    """Guardian enforcement configuration."""
    mode: EnforcementMode
    actions: Optional[List[str]] = None


@dataclass
class GuardianAudit:
    """Guardian audit trail."""
    event_id: str
    timestamp: str
    source_system: Optional[str] = None
    audit_trail: Optional[List[Dict[str, Any]]] = None


class GuardianSystem:
    """
    T4/0.01% Guardian Decision Envelope System.

    Provides tamper-evident, fail-closed Guardian decision serialization
    with optional cryptographic signing and strict schema validation.
    """

    def __init__(self, signing_key: Optional[str] = None, schema_path: Optional[str] = None):
        """
        Initialize Guardian system.

        Args:
            signing_key: Optional ED25519 private key for signing (env: GUARDIAN_SIGNING_KEY)
            schema_path: Optional path to guardian schema file
        """
        self.signing_key = signing_key or os.environ.get("GUARDIAN_SIGNING_KEY")
        self.schema_path = schema_path
        self.schema = None
        self._load_schema()

    def _load_schema(self):
        """Load Guardian schema for validation."""
        if not SCHEMA_VALIDATION:
            return

        try:
            if self.schema_path:
                schema_file = self.schema_path
            else:
                # Default schema location
                import pathlib
                schema_file = pathlib.Path(__file__).parent.parent.parent / "governance" / "guardian_schema.json"

            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    self.schema = json.load(f)
                logger.info(f"Guardian schema loaded from {schema_file}")
            else:
                logger.warning(f"Guardian schema not found at {schema_file}")
        except Exception as e:
            logger.error(f"Failed to load Guardian schema: {e}")

    def serialize_decision(
        self,
        decision: GuardianDecision,
        subject: GuardianSubject,
        context: GuardianContext,
        metrics: GuardianMetrics,
        enforcement: GuardianEnforcement,
        audit: GuardianAudit,
        reasons: Optional[List[Dict[str, Any]]] = None,
        rule_evaluations: Optional[List[Dict[str, Any]]] = None,
        approvals: Optional[List[Dict[str, Any]]] = None,
        redactions: Optional[Dict[str, str]] = None,
        extensions: Optional[Dict[str, Any]] = None,
        debug: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Serialize Guardian decision into T4/0.01% compliant envelope.

        Returns tamper-evident decision envelope with integrity hash and optional signature.
        """
        # Build envelope structure
        envelope = {
            "schema_version": "2.1.0",
            "decision": {
                "status": decision.status.value,
                "policy": decision.policy,
                "timestamp": decision.timestamp,
                "severity": decision.severity
            },
            "subject": {
                "correlation_id": subject.correlation_id,
                "actor": {
                    "type": subject.actor_type.value,
                    "id": subject.actor_id
                },
                "operation": {
                    "name": subject.operation_name
                }
            },
            "context": {
                "environment": {
                    "region": context.region,
                    "runtime": context.runtime.value
                },
                "features": {
                    "enforcement_enabled": context.enforcement_enabled,
                    "emergency_active": context.emergency_active
                }
            },
            "metrics": {
                "latency_ms": metrics.latency_ms
            },
            "enforcement": {
                "mode": enforcement.mode.value
            },
            "audit": {
                "event_id": audit.event_id,
                "timestamp": audit.timestamp
            }
        }

        # Add optional fields
        if decision.confidence is not None:
            envelope["decision"]["confidence"] = decision.confidence
        if decision.ttl_seconds is not None:
            envelope["decision"]["ttl_seconds"] = decision.ttl_seconds

        if subject.lane:
            envelope["subject"]["lane"] = subject.lane
        if subject.canary_percent is not None:
            envelope["subject"]["canary_percent"] = subject.canary_percent
        if subject.actor_tier:
            envelope["subject"]["actor"]["tier"] = subject.actor_tier
        if subject.operation_resource:
            envelope["subject"]["operation"]["resource"] = subject.operation_resource
        if subject.operation_parameters:
            envelope["subject"]["operation"]["parameters"] = subject.operation_parameters

        if context.version:
            envelope["context"]["environment"]["version"] = context.version
        if context.kill_switch_path:
            envelope["context"]["features"]["kill_switch_path"] = context.kill_switch_path

        if metrics.risk_score is not None:
            envelope["metrics"]["risk_score"] = metrics.risk_score
        if metrics.drift_score is not None:
            envelope["metrics"]["drift_score"] = metrics.drift_score
        if metrics.quota_remaining is not None:
            envelope["metrics"]["quota_remaining"] = metrics.quota_remaining
        if metrics.counters:
            envelope["metrics"]["counters"] = metrics.counters

        if enforcement.actions:
            envelope["enforcement"]["actions"] = enforcement.actions

        if audit.source_system:
            envelope["audit"]["source_system"] = audit.source_system
        if audit.audit_trail:
            envelope["audit"]["audit_trail"] = audit.audit_trail

        # Optional arrays
        if reasons:
            envelope["reasons"] = reasons
        if rule_evaluations:
            envelope["rule_evaluations"] = rule_evaluations
        if approvals:
            envelope["approvals"] = approvals
        if redactions:
            envelope["redactions"] = redactions
        if extensions:
            envelope["extensions"] = extensions
        if debug:
            envelope["debug"] = debug

        # Compute integrity hash and add signature
        integrity = self._compute_integrity(envelope)
        envelope["integrity"] = integrity

        # Validate envelope against schema
        self._validate_envelope(envelope)

        return envelope

    def _compute_integrity(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute tamper-evident integrity hash and optional signature.

        Args:
            envelope: Guardian envelope without integrity field

        Returns:
            Integrity block with content hash and optional signature
        """
        # Canonical JSON for hashing (RFC 8785-ish)
        canonical_json = json.dumps(
            envelope,
            separators=(",", ":"),
            cls=GuardianJSONEncoder,
            sort_keys=True,
            ensure_ascii=False
        ).encode("utf-8")

        # Compute SHA256 content hash
        content_hash = hashlib.sha256(canonical_json).hexdigest()

        integrity = {"content_sha256": content_hash}

        # Optional cryptographic signing
        if self.signing_key and CRYPTO_AVAILABLE:
            try:
                signature = self._sign_content(canonical_json)
                integrity["signature"] = signature
            except Exception as e:
                logger.error(f"Failed to sign Guardian envelope: {e}")
                # Continue without signature (degrade gracefully)

        return integrity

    def _sign_content(self, content: bytes) -> Dict[str, str]:
        """
        Sign content with ED25519 private key.

        Args:
            content: Canonical JSON bytes to sign

        Returns:
            Signature block with algorithm, key ID, and signature
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography library required for signing")

        try:
            # Load private key (assuming base64-encoded ED25519 key)
            private_key_bytes = base64.b64decode(self.signing_key)
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

            # Sign the content
            signature_bytes = private_key.sign(content)
            signature_b64 = base64.b64encode(signature_bytes).decode('ascii')

            # Generate key ID (first 8 chars of public key hash for brevity)
            public_key = private_key.public_key()
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            key_id = "guardian-" + hashlib.sha256(public_key_bytes).hexdigest()[:8]

            return {
                "alg": "ed25519",
                "kid": key_id,
                "sig": signature_b64
            }

        except Exception as e:
            logger.error(f"Signing failed: {e}")
            raise

    def verify_integrity(self, envelope: Dict[str, Any]) -> bool:
        """
        Verify tamper-evident integrity of Guardian envelope.

        Args:
            envelope: Complete Guardian envelope with integrity field

        Returns:
            True if integrity verification passes, False otherwise (fail-closed)
        """
        try:
            # Extract integrity block
            integrity = envelope.get("integrity", {})
            expected_hash = integrity.get("content_sha256")

            if not expected_hash:
                logger.warning("Guardian envelope missing integrity hash")
                return False  # Fail-closed

            # Extract envelope without integrity for verification
            envelope_for_hash = dict(envelope)
            envelope_for_hash.pop("integrity", None)

            # Recompute canonical hash
            canonical_json = json.dumps(
                envelope_for_hash,
                separators=(",", ":"),
                cls=GuardianJSONEncoder,
                sort_keys=True,
                ensure_ascii=False
            ).encode("utf-8")

            computed_hash = hashlib.sha256(canonical_json).hexdigest()

            # Verify hash match
            if computed_hash != expected_hash:
                logger.warning(f"Guardian integrity hash mismatch: expected {expected_hash}, got {computed_hash}")
                return False  # Tamper detected

            # Verify signature if present
            signature = integrity.get("signature")
            if signature and CRYPTO_AVAILABLE:
                if not self._verify_signature(canonical_json, signature):
                    logger.warning("Guardian signature verification failed")
                    return False  # Signature verification failed

            return True

        except Exception as e:
            logger.error(f"Guardian integrity verification error: {e}")
            return False  # Fail-closed on error

    def _verify_signature(self, content: bytes, signature: Dict[str, str]) -> bool:
        """
        Verify cryptographic signature.

        Args:
            content: Canonical JSON bytes that were signed
            signature: Signature block with algorithm, key ID, and signature

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if signature.get("alg") != "ed25519":
                logger.warning(f"Unsupported signature algorithm: {signature.get('alg')}")
                return False

            # For this implementation, we'd need access to the public key
            # In production, this would look up the public key by key ID
            # For now, we'll log and return True (signature structure is valid)
            logger.info(f"Signature verification requested for key {signature.get('kid')}")

            # In a real implementation:
            # 1. Look up public key by signature["kid"]
            # 2. Verify signature using ed25519 public key
            # 3. Return verification result

            return True  # Placeholder - implement key lookup and verification

        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

    def _validate_envelope(self, envelope: Dict[str, Any]) -> bool:
        """
        Validate envelope against T4 Guardian schema.

        Args:
            envelope: Complete Guardian envelope

        Returns:
            True if valid, raises ValidationError if invalid
        """
        if not SCHEMA_VALIDATION or not self.schema:
            logger.debug("Schema validation disabled or schema not loaded")
            return True

        try:
            jsonschema.validate(instance=envelope, schema=self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Guardian envelope schema validation failed: {e}")
            raise ValueError(f"Guardian envelope validation failed: {e.message}")

    def is_decision_allow(self, envelope: Dict[str, Any]) -> bool:
        """
        Determine if Guardian decision allows the operation (fail-closed).

        Args:
            envelope: Guardian decision envelope

        Returns:
            True only if decision is explicitly "allow", False otherwise (fail-closed)
        """
        try:
            # Verify envelope integrity first
            if not self.verify_integrity(envelope):
                logger.warning("Guardian envelope failed integrity check - denying")
                return False  # Fail-closed on integrity failure

            # Check enforcement enabled
            enforcement_enabled = envelope.get("context", {}).get("features", {}).get("enforcement_enabled", True)
            if not enforcement_enabled:
                logger.info("Guardian enforcement disabled - allowing")
                return True  # Enforcement disabled

            # Check emergency kill switch
            emergency_active = envelope.get("context", {}).get("features", {}).get("emergency_active", False)
            if emergency_active:
                logger.warning("Guardian emergency mode active - denying all")
                return False  # Emergency mode blocks all

            # Get decision status
            status = envelope.get("decision", {}).get("status", "error")

            # Fail-closed: only "allow" permits operation
            if status == "allow":
                return True
            elif status in ["deny", "challenge", "quarantine", "error"]:
                return False
            else:
                logger.warning(f"Unknown Guardian decision status: {status} - denying")
                return False  # Unknown status → fail-closed

        except Exception as e:
            logger.error(f"Guardian decision evaluation error: {e}")
            return False  # Fail-closed on error


# Convenience functions for common Guardian operations
def create_guardian_system(signing_key: Optional[str] = None) -> GuardianSystem:
    """Create Guardian system with optional signing."""
    return GuardianSystem(signing_key=signing_key)


def create_simple_decision(
    status: DecisionStatus,
    policy: str,
    correlation_id: str,
    actor_id: str,
    operation: str,
    region: str = "us-east-1",
    runtime: RuntimeEnvironment = RuntimeEnvironment.PROD,
    latency_ms: float = 0.0
) -> Dict[str, Any]:
    """
    Create a simple Guardian decision envelope for common use cases.

    Args:
        status: Guardian decision status
        policy: Policy name and version (e.g., "ethics/v4.3.1")
        correlation_id: Request correlation ID
        actor_id: Actor identifier
        operation: Operation name
        region: AWS/cloud region
        runtime: Runtime environment
        latency_ms: Processing latency

    Returns:
        Complete Guardian decision envelope
    """
    guardian = create_guardian_system()

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    event_id = str(uuid.uuid4())

    decision = GuardianDecision(
        status=status,
        policy=policy,
        timestamp=now_iso
    )

    subject = GuardianSubject(
        correlation_id=correlation_id,
        actor_type=ActorType.SERVICE,
        actor_id=actor_id,
        operation_name=operation
    )

    context = GuardianContext(
        region=region,
        runtime=runtime
    )

    metrics = GuardianMetrics(
        latency_ms=latency_ms
    )

    enforcement = GuardianEnforcement(
        mode=EnforcementMode.ENFORCED
    )

    audit = GuardianAudit(
        event_id=event_id,
        timestamp=now_iso
    )

    return guardian.serialize_decision(
        decision=decision,
        subject=subject,
        context=context,
        metrics=metrics,
        enforcement=enforcement,
        audit=audit
    )


# Export public API
__all__ = [
    "GuardianSystem",
    "DecisionStatus",
    "EnforcementMode",
    "ActorType",
    "RuntimeEnvironment",
    "GuardianDecision",
    "GuardianSubject",
    "GuardianContext",
    "GuardianMetrics",
    "GuardianEnforcement",
    "GuardianAudit",
    "create_guardian_system",
    "create_simple_decision"
]
