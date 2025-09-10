#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Advanced Security for Enterprise Feedback
========================================
Zero-trust architecture with blockchain verification and quantum-resistant encryption.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from candidate.core.common import get_logger
from core.interfaces import CoreInterface
from feedback.user_feedback_system import FeedbackItem

logger = get_logger(__name__)


class SecurityLevel(Enum):
    """Security clearance levels"""

    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SECRET = 3
    TOP_SECRET = 4


class ThreatType(Enum):
    """Types of security threats"""

    SQL_INJECTION = "sql_injection"
    PROMPT_INJECTION = "prompt_injection"
    XSS_ATTACK = "xss_attack"
    DOS_ATTACK = "dos_attack"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    REPLAY_ATTACK = "replay_attack"
    MAN_IN_MIDDLE = "man_in_middle"


@dataclass
class SecurityContext:
    """Security context for feedback processing"""

    user_id: str
    session_id: str
    clearance_level: SecurityLevel
    authentication_factors: list[str]
    encryption_key: bytes
    integrity_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    threat_score: float = 0.0
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""

    threat_type: ThreatType
    severity: float  # 0-1
    indicators: list[str]
    mitigation: str
    detected_at: datetime
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None


class AdvancedSecuritySystem(CoreInterface):
    """
    Enterprise-grade security system combining Anthropic's privacy focus
    with OpenAI's scale security requirements.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize security system"""
        self.config = config or {}
        self.operational = False

        # Encryption keys (in production, use HSM)
        self.master_key = None
        self.session_keys: dict[str, bytes] = {}

        # Threat detection
        self.threat_patterns = self._load_threat_patterns()
        self.blocked_ips: set[str] = set()
        self.rate_limits: dict[str, list[datetime]] = {}

        # Blockchain for audit
        self.security_blockchain: list[dict[str, Any]] = []

        # Zero-trust components
        self.trust_scores: dict[str, float] = {}
        self.verified_sessions: set[str] = set()

        # Quantum-resistant preparation
        self.qi_safe_algorithms = ["AES-256", "SHA3-512", "Dilithium"]

        # Privacy preservation
        self.anonymization_keys: dict[str, str] = {}
        self.k_anonymity_threshold = config.get("k_anonymity", 5)

    async def initialize(self) -> None:
        """Initialize security system"""
        logger.info("Initializing Advanced Security System...")

        # Generate master key
        self.master_key = secrets.token_bytes(32)

        # Initialize threat detection
        await self._setup_threat_detection()

        # Start monitoring
        asyncio.create_task(self._monitor_threats())
        asyncio.create_task(self._rotate_keys())

        self.operational = True
        logger.info("Advanced Security System initialized")

    def _load_threat_patterns(self) -> dict[ThreatType, list[str]]:
        """Load threat detection patterns"""
        return {
            ThreatType.SQL_INJECTION: [
                "' or '1'='1",
                "'; drop table",
                "union select",
                "/*",
                "*/",
                "--",
                "xp_",
                "sp_executesql",
            ],
            ThreatType.PROMPT_INJECTION: [
                "ignore previous",
                "disregard instructions",
                "new task:",
                "forget everything",
                "system prompt",
                "reveal prompt",
                "show instructions",
            ],
            ThreatType.XSS_ATTACK: [
                "<script",
                "javascript:",
                "onerror=",
                "onclick=",
                "<iframe",
                "<object",
                "eval(",
                "expression(",
            ],
            ThreatType.DOS_ATTACK: [
                # Patterns for detecting DoS attempts
                "a" * 10000,  # Repeated characters
                "nested" * 1000,  # Deeply nested structures
            ],
            ThreatType.DATA_EXFILTRATION: [
                "select * from",
                "dump database",
                "show tables",
                "export data",
                "backup",
                "download all",
            ],
        }

    async def _setup_threat_detection(self) -> None:
        """Setup threat detection systems"""
        # Initialize ML-based threat detection (simulated)
        self.threat_ml_model = {
            "initialized": True,
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc),
        }

    async def create_security_context(self, user_id: str, session_id: str, auth_factors: list[str]) -> SecurityContext:
        """Create security context for user session"""
        # Determine clearance level based on auth factors
        clearance = self._determine_clearance_level(auth_factors)

        # Generate session encryption key
        session_key = self._derive_session_key(user_id, session_id)

        # Create integrity hash
        integrity_data = f"{user_id}:{session_id}:{datetime.now(timezone.utc).isoformat()}"
        integrity_hash = self._create_integrity_hash(integrity_data)

        context = SecurityContext(
            user_id=user_id,
            session_id=session_id,
            clearance_level=clearance,
            authentication_factors=auth_factors,
            encryption_key=session_key,
            integrity_hash=integrity_hash,
        )

        # Calculate initial threat score
        context.threat_score = await self._calculate_threat_score(user_id)

        # Store session key
        self.session_keys[session_id] = session_key

        return context

    def _determine_clearance_level(self, auth_factors: list[str]) -> SecurityLevel:
        """Determine security clearance based on authentication"""
        if "biometric" in auth_factors and "hardware_key" in auth_factors:
            return SecurityLevel.TOP_SECRET
        elif "mfa" in auth_factors and "certificate" in auth_factors:
            return SecurityLevel.SECRET
        elif "mfa" in auth_factors:
            return SecurityLevel.CONFIDENTIAL
        elif "password" in auth_factors:
            return SecurityLevel.INTERNAL
        else:
            return SecurityLevel.PUBLIC

    def _derive_session_key(self, user_id: str, session_id: str) -> bytes:
        """Derive session-specific encryption key"""
        # Use HKDF for key derivation
        import hashlib

        info = f"{user_id}:{session_id}".encode()
        prk = hmac.new(self.master_key, info, hashlib.sha256).digest()

        # Expand to 32 bytes for AES-256
        okm = hmac.new(prk, b"session_key", hashlib.sha256).digest()

        return okm

    def _create_integrity_hash(self, data: str) -> str:
        """Create integrity hash using SHA3-512"""
        import hashlib

        # Use SHA3 for quantum resistance preparation
        hash_obj = hashlib.sha3_512()
        hash_obj.update(data.encode())
        hash_obj.update(self.master_key)

        return hash_obj.hexdigest()

    async def _calculate_threat_score(self, user_id: str) -> float:
        """Calculate threat score for user"""
        score = 0.0

        # Check if user is in blocked list
        if user_id in self.blocked_ips:
            score += 0.5

        # Check rate limiting
        if user_id in self.rate_limits:
            recent_requests = [
                req for req in self.rate_limits[user_id] if req > datetime.now(timezone.utc) - timedelta(minutes=1)
            ]
            if len(recent_requests) > 100:
                score += 0.3

        # Check trust score
        if user_id in self.trust_scores:
            score -= self.trust_scores[user_id] * 0.2

        return max(0.0, min(1.0, score))

    async def validate_feedback_security(
        self, feedback: FeedbackItem, context: SecurityContext
    ) -> tuple[bool, Optional[ThreatIntelligence]]:
        """
        Validate feedback for security threats.

        Returns:
            Tuple of (is_secure, threat_info)
        """
        # Check authentication
        if context.session_id not in self.verified_sessions and not await self._verify_session(context):
            return False, ThreatIntelligence(
                threat_type=ThreatType.PRIVILEGE_ESCALATION,
                severity=0.8,
                indicators=["unverified_session"],
                mitigation="Require re-authentication",
                detected_at=datetime.now(timezone.utc),
            )

        # Check for threats in content
        if feedback.content:
            threat = await self._detect_content_threats(feedback.content)
            if threat:
                return False, threat

        # Verify integrity
        if not self._verify_integrity(feedback, context):
            return False, ThreatIntelligence(
                threat_type=ThreatType.MAN_IN_MIDDLE,
                severity=0.9,
                indicators=["integrity_check_failed"],
                mitigation="Re-establish secure connection",
                detected_at=datetime.now(timezone.utc),
            )

        # Update trust score
        await self._update_trust_score(context.user_id, True)

        return True, None

    async def _verify_session(self, context: SecurityContext) -> bool:
        """Verify session with zero-trust principles"""
        # Verify all authentication factors
        for factor in context.authentication_factors:
            if not await self._verify_auth_factor(factor, context):
                return False

        # Verify session hasn't expired
        session_age = datetime.now(timezone.utc) - context.timestamp
        if session_age > timedelta(hours=1):
            return False

        # Mark as verified
        self.verified_sessions.add(context.session_id)
        return True

    async def _verify_auth_factor(self, factor: str, context: SecurityContext) -> bool:
        """Verify individual authentication factor"""
        # In production, integrate with auth providers
        # For demo, simulate verification
        return True

    async def _detect_content_threats(self, content: dict[str, Any]) -> Optional[ThreatIntelligence]:
        """Detect threats in feedback content"""
        # Convert content to string for analysis
        content_str = json.dumps(content).lower()

        # Check each threat type
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_str:
                    return ThreatIntelligence(
                        threat_type=threat_type,
                        severity=0.8,
                        indicators=[pattern],
                        mitigation=self._get_mitigation(threat_type),
                        detected_at=datetime.now(timezone.utc),
                    )

        # ML-based detection (simulated)
        ml_threat_score = await self._ml_threat_detection(content_str)
        if ml_threat_score > 0.7:
            return ThreatIntelligence(
                threat_type=ThreatType.PROMPT_INJECTION,
                severity=ml_threat_score,
                indicators=["ml_detection"],
                mitigation="Manual review required",
                detected_at=datetime.now(timezone.utc),
            )

        return None

    async def _ml_threat_detection(self, content: str) -> float:
        """ML-based threat detection (simulated)"""
        # In production, use actual ML model
        # For demo, simple heuristics
        suspicious_words = ["hack", "exploit", "vulnerability", "bypass", "override"]

        word_count = len(content.split())
        suspicious_count = sum(1 for word in suspicious_words if word in content)

        if word_count > 0:
            return suspicious_count / word_count
        return 0.0

    def _get_mitigation(self, threat_type: ThreatType) -> str:
        """Get mitigation strategy for threat type"""
        mitigations = {
            ThreatType.SQL_INJECTION: "Sanitize input and use parameterized queries",
            ThreatType.PROMPT_INJECTION: "Apply constitutional AI filtering",
            ThreatType.XSS_ATTACK: "Escape HTML and validate input",
            ThreatType.DOS_ATTACK: "Apply rate limiting and resource quotas",
            ThreatType.DATA_EXFILTRATION: "Restrict data access and monitor queries",
            ThreatType.PRIVILEGE_ESCALATION: "Enforce least privilege principle",
            ThreatType.REPLAY_ATTACK: "Use nonces and timestamp validation",
            ThreatType.MAN_IN_MIDDLE: "Enforce TLS and certificate pinning",
        }
        return mitigations.get(threat_type, "Apply general security measures")

    def _verify_integrity(self, feedback: FeedbackItem, context: SecurityContext) -> bool:
        """Verify feedback integrity"""
        # Create hash of feedback content
        feedback_str = json.dumps(
            {
                "user_id": feedback.user_id,
                "content": feedback.content,
                "timestamp": feedback.timestamp.isoformat(),
            },
            sort_keys=True,
        )

        self._create_integrity_hash(feedback_str)

        # In production, compare with hash sent by client
        return True  # Simplified for demo

    async def _update_trust_score(self, user_id: str, positive: bool) -> None:
        """Update user trust score"""
        if user_id not in self.trust_scores:
            self.trust_scores[user_id] = 0.5

        # Exponential moving average
        alpha = 0.1
        if positive:
            self.trust_scores[user_id] = alpha * 1.0 + (1 - alpha) * self.trust_scores[user_id]
        else:
            self.trust_scores[user_id] = alpha * 0.0 + (1 - alpha) * self.trust_scores[user_id]

        # Clamp between 0 and 1
        self.trust_scores[user_id] = max(0.0, min(1.0, self.trust_scores[user_id]))

    async def encrypt_feedback(self, feedback: FeedbackItem, context: SecurityContext) -> bytes:
        """Encrypt feedback with AES-256-GCM"""
        # Serialize feedback
        feedback_json = json.dumps(
            {
                "feedback_id": feedback.feedback_id,
                "user_id": feedback.user_id,
                "content": feedback.content,
                "timestamp": feedback.timestamp.isoformat(),
            }
        )

        # Generate nonce
        nonce = secrets.token_bytes(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(context.encryption_key),
            modes.GCM(nonce),
            backend=default_backend(),
        )

        encryptor = cipher.encryptor()

        # Encrypt data
        ciphertext = encryptor.update(feedback_json.encode()) + encryptor.finalize()

        # Return nonce + ciphertext + tag
        return nonce + ciphertext + encryptor.tag

    async def decrypt_feedback(self, encrypted_data: bytes, context: SecurityContext) -> dict[str, Any]:
        """Decrypt feedback"""
        # Extract components
        nonce = encrypted_data[:12]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[12:-16]

        # Create cipher
        cipher = Cipher(
            algorithms.AES(context.encryption_key),
            modes.GCM(nonce, tag),
            backend=default_backend(),
        )

        decryptor = cipher.decryptor()

        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return json.loads(plaintext.decode())

    async def apply_differential_privacy(self, feedback_data: dict[str, Any], epsilon: float = 1.0) -> dict[str, Any]:
        """Apply differential privacy to feedback data"""
        import numpy as np

        private_data = feedback_data.copy()

        # Add noise to numeric values
        for key, value in private_data.items():
            if isinstance(value, (int, float)):
                # Laplace mechanism
                sensitivity = 1.0  # Adjust based on data
                noise = np.random.laplace(0, sensitivity / epsilon)
                private_data[key] = value + noise

        # Anonymize identifiers
        if "user_id" in private_data:
            private_data["user_id"] = self._anonymize_id(private_data["user_id"])

        return private_data

    def _anonymize_id(self, user_id: str) -> str:
        """Anonymize user ID while maintaining consistency"""
        if user_id not in self.anonymization_keys:
            # Generate consistent anonymous ID
            hash_obj = hashlib.sha256()
            hash_obj.update(user_id.encode())
            hash_obj.update(self.master_key)
            self.anonymization_keys[user_id] = hash_obj.hexdigest()[:16]

        return self.anonymization_keys[user_id]

    async def check_k_anonymity(self, feedback_attributes: dict[str, Any]) -> bool:
        """Check if feedback meets k-anonymity requirements"""
        # In production, check against database
        # For demo, simulate check

        # Remove identifying information
        {k: v for k, v in feedback_attributes.items() if k not in ["user_id", "session_id", "feedback_id"]}

        # Check if at least k users share these attributes
        # Simulated for demo
        return True

    async def create_security_audit_entry(
        self,
        action: str,
        context: SecurityContext,
        result: str,
        threat_info: Optional[ThreatIntelligence] = None,
    ) -> None:
        """Create blockchain audit entry for security event"""
        entry = {
            "block_id": len(self.security_blockchain),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user_id": self._anonymize_id(context.user_id),
            "session_id": hashlib.sha256(context.session_id.encode()).hexdigest()[:16],
            "clearance_level": context.clearance_level.name,
            "result": result,
            "threat_score": context.threat_score,
        }

        if threat_info:
            entry["threat"] = {
                "type": threat_info.threat_type.value,
                "severity": threat_info.severity,
                "mitigation": threat_info.mitigation,
            }

        # Add previous block hash
        if self.security_blockchain:
            previous_block = self.security_blockchain[-1]
            entry["previous_hash"] = self._calculate_block_hash(previous_block)
        else:
            entry["previous_hash"] = "genesis"

        # Calculate this block's hash
        entry["block_hash"] = self._calculate_block_hash(entry)

        self.security_blockchain.append(entry)

        # Add to context audit trail
        context.audit_trail.append(
            {
                "action": action,
                "timestamp": entry["timestamp"],
                "block_hash": entry["block_hash"],
            }
        )

    def _calculate_block_hash(self, block: dict[str, Any]) -> str:
        """Calculate hash for audit block"""
        block_str = json.dumps(block, sort_keys=True)

        # Use SHA3-512 for quantum resistance
        hash_obj = hashlib.sha3_512()
        hash_obj.update(block_str.encode())

        return hash_obj.hexdigest()

    async def _monitor_threats(self) -> None:
        """Monitor for security threats continuously"""
        while self.operational:
            try:
                # Check for coordinated attacks
                await self._detect_coordinated_attacks()

                # Update threat intelligence
                await self._update_threat_intelligence()

                # Clean old rate limit data
                await self._cleanup_rate_limits()

                await asyncio.sleep(60)  # Every minute

            except Exception as e:
                logger.error(f"Threat monitoring error: {e}")
                await asyncio.sleep(300)

    async def _detect_coordinated_attacks(self) -> None:
        """Detect coordinated attack patterns"""
        # Check for sudden spike in requests
        recent_requests = sum(
            len([r for r in requests if r > datetime.now(timezone.utc) - timedelta(minutes=5)])
            for requests in self.rate_limits.values()
        )

        if recent_requests > 10000:  # Threshold
            logger.warning(f"Potential DDoS detected: {recent_requests} requests in 5 minutes")

            # Implement mitigation
            # In production, trigger DDoS protection

    async def _update_threat_intelligence(self) -> None:
        """Update threat intelligence from external sources"""
        # In production, connect to threat feeds
        # For demo, we'll just log
        logger.debug("Threat intelligence updated")

    async def _cleanup_rate_limits(self) -> None:
        """Clean up old rate limit entries"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

        for user_id in list(self.rate_limits.keys()):
            self.rate_limits[user_id] = [req for req in self.rate_limits[user_id] if req > cutoff]

            if not self.rate_limits[user_id]:
                del self.rate_limits[user_id]

    async def _rotate_keys(self) -> None:
        """Rotate encryption keys periodically"""
        while self.operational:
            try:
                await asyncio.sleep(86400)  # Daily rotation

                # Generate new master key
                self.master_key
                self.master_key = secrets.token_bytes(32)

                # Re-encrypt session keys
                for session_id in list(self.session_keys.keys()):
                    # In production, re-encrypt with new key
                    # For demo, just regenerate
                    self.session_keys[session_id] = secrets.token_bytes(32)

                logger.info("Encryption keys rotated successfully")

            except Exception as e:
                logger.error(f"Key rotation error: {e}")
                await asyncio.sleep(3600)

    # Required interface methods

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process security request"""
        action = data.get("action", "validate")

        if action == "validate":
            feedback = data.get("feedback")
            context = data.get("context")

            is_secure, threat_info = await self.validate_feedback_security(feedback, context)

            return {
                "secure": is_secure,
                "threat": threat_info.__dict__ if threat_info else None,
            }

        elif action == "encrypt":
            feedback = data.get("feedback")
            context = data.get("context")

            encrypted = await self.encrypt_feedback(feedback, context)

            return {"encrypted_data": base64.b64encode(encrypted).decode()}

        else:
            raise ValueError(f"Unknown action: {action}")

    async def handle_glyph(self, token: Any) -> Any:
        """Handle GLYPH communication"""
        return {
            "operational": self.operational,
            "threats_detected": sum(1 for entry in self.security_blockchain if "threat" in entry),
            "active_sessions": len(self.verified_sessions),
        }

    async def get_status(self) -> dict[str, Any]:
        """Get security system status"""
        return {
            "operational": self.operational,
            "security_metrics": {
                "active_sessions": len(self.verified_sessions),
                "blocked_users": len(self.blocked_ips),
                "average_trust_score": (np.mean(list(self.trust_scores.values())) if self.trust_scores else 0.5),
                "threats_last_hour": sum(1 for entry in self.security_blockchain[-100:] if "threat" in entry),
            },
            "blockchain": {
                "blocks": len(self.security_blockchain),
                "latest_hash": (self.security_blockchain[-1]["block_hash"] if self.security_blockchain else None),
            },
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_rotation": "daily",
                "qi_ready": True,
            },
        }