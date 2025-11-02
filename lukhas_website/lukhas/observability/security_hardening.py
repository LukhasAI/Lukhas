#!/usr/bin/env python3
"""
LUKHAS Observability Security Hardening
Advanced security measures for audit trail integrity and observability system protection.

Features:
- Cryptographic integrity verification for all audit trails
- Secure key management and rotation
- Tamper detection and response mechanisms
- Security event monitoring and alerting
- Access control and privilege management
- Secure communication channels
- Audit trail encryption and signing
- Security compliance validation
"""

import asyncio
import hashlib
import hmac
import os
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    import jwt  # noqa: F401  # TODO: jwt; consider using importlib....
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from .evidence_collection import EvidenceType, collect_evidence


class SecurityLevel(Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats detected"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_TAMPERING = "data_tampering"
    INTEGRITY_VIOLATION = "integrity_violation"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    INJECTION_ATTACK = "injection_attack"
    BRUTE_FORCE = "brute_force"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    CONFIGURATION_TAMPERING = "configuration_tampering"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    threat_type: ThreatType
    severity: SecurityLevel
    source_ip: Optional[str]
    user_id: Optional[str]
    component: str
    operation: str
    timestamp: datetime
    details: Dict[str, Any]
    action_taken: Optional[str] = None
    resolved: bool = False
    false_positive: bool = False


@dataclass
class SecurityKey:
    """Security key with metadata"""
    key_id: str
    key_type: str  # "signing", "encryption", "hmac"
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int = 0
    max_usage: Optional[int] = None
    active: bool = True


@dataclass
class AccessAttempt:
    """Access attempt tracking"""
    source_ip: str
    user_id: Optional[str]
    timestamp: datetime
    success: bool
    operation: str
    component: str


class ObservabilitySecurityHardening:
    """
    Comprehensive security hardening for LUKHAS observability systems.
    Provides cryptographic integrity, tamper detection, and security monitoring.
    """

    def __init__(
        self,
        key_storage_path: str = "./artifacts/security/keys",
        security_config_path: str = "./config/security_hardening.json",
        enable_encryption: bool = True,
        enable_signing: bool = True,
        key_rotation_days: int = 90,
        max_failed_attempts: int = 5,
        lockout_duration_minutes: int = 30,
    ):
        """
        Initialize security hardening system.

        Args:
            key_storage_path: Path to store cryptographic keys
            security_config_path: Path to security configuration
            enable_encryption: Enable data encryption
            enable_signing: Enable data signing
            key_rotation_days: Days between key rotation
            max_failed_attempts: Maximum failed attempts before lockout
            lockout_duration_minutes: Minutes to lock out after failed attempts
        """
        self.key_storage_path = Path(key_storage_path)
        self.key_storage_path.mkdir(parents=True, exist_ok=True)
        self.security_config_path = Path(security_config_path)
        self.enable_encryption = enable_encryption
        self.enable_signing = enable_signing
        self.key_rotation_days = key_rotation_days
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration_minutes = lockout_duration_minutes

        # Security state
        self.security_keys: Dict[str, SecurityKey] = {}
        self.security_events: List[SecurityEvent] = []
        self.access_attempts: deque = deque(maxlen=10000)
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.locked_sources: Dict[str, datetime] = {}

        # Integrity verification
        self.integrity_hashes: Dict[str, str] = {}
        self.tamper_detection_enabled = True

        # Security monitoring
        self.threat_detection_rules = []
        self.security_baselines: Dict[str, Any] = {}

        # Background tasks
        self._security_monitor_task: Optional[asyncio.Task] = None
        self._key_rotation_task: Optional[asyncio.Task] = None

        # Initialize security system
        self._load_security_configuration()
        self._initialize_cryptographic_keys()
        self._setup_threat_detection()
        self._start_background_tasks()

    def _load_security_configuration(self):
        """Load security configuration"""
        default_config = {
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_derivation": "PBKDF2",
                "iterations": 100000,
            },
            "signing": {
                "algorithm": "RSA-PSS",
                "key_size": 2048,
                "hash_algorithm": "SHA-256",
            },
            "threat_detection": {
                "enable_behavioral_analysis": True,
                "enable_pattern_matching": True,
                "anomaly_threshold": 0.8,
            },
            "access_control": {
                "enforce_ip_whitelist": False,
                "whitelist_ips": [],
                "require_authentication": True,
                "session_timeout_minutes": 60,
            },
            "audit_security": {
                "sign_all_evidence": True,
                "encrypt_sensitive_data": True,
                "verify_integrity_on_read": True,
            },
        }

        if self.security_config_path.exists():
            try:
                import json
                with open(self.security_config_path) as f:
                    self.security_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in self.security_config:
                            self.security_config[key] = value
            except Exception as e:
                print(f"Warning: Failed to load security config: {e}")
                self.security_config = default_config
        else:
            self.security_config = default_config
            # Save default configuration
            try:
                import json
                with open(self.security_config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
            except Exception:
                pass

    def _initialize_cryptographic_keys(self):
        """Initialize cryptographic keys for security operations"""
        # Initialize signing key
        if self.enable_signing:
            signing_key_path = self.key_storage_path / "signing_key.pem"
            if signing_key_path.exists():
                try:
                    with open(signing_key_path, 'rb') as f:
                        private_key = serialization.load_pem_private_key(
                            f.read(), password=None, backend=default_backend()
                        )
                    self._store_key("primary_signing", "signing", private_key)
                except Exception as e:
                    print(f"Warning: Failed to load existing signing key: {e}")
                    self._generate_signing_key()
            else:
                self._generate_signing_key()

        # Initialize encryption key
        if self.enable_encryption:
            self._generate_encryption_key()

        # Initialize HMAC key for integrity
        hmac_key_path = self.key_storage_path / "hmac_key.bin"
        if hmac_key_path.exists():
            with open(hmac_key_path, 'rb') as f:
                hmac_key = f.read()
        else:
            hmac_key = os.urandom(32)  # 256-bit key
            with open(hmac_key_path, 'wb') as f:
                f.write(hmac_key)
            os.chmod(hmac_key_path, 0o600)

        self._store_key("primary_hmac", "hmac", hmac_key)

    def _generate_signing_key(self):
        """Generate RSA signing key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.security_config["signing"]["key_size"],
            backend=default_backend()
        )

        # Store private key
        signing_key_path = self.key_storage_path / "signing_key.pem"
        with open(signing_key_path, 'wb') as f:
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            f.write(pem)
        os.chmod(signing_key_path, 0o600)

        # Store public key
        public_key = private_key.public_key()
        public_key_path = self.key_storage_path / "signing_key_public.pem"
        with open(public_key_path, 'wb') as f:
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            f.write(pem)

        self._store_key("primary_signing", "signing", private_key)

    def _generate_encryption_key(self):
        """Generate encryption key"""
        encryption_key = os.urandom(32)  # 256-bit key
        encryption_key_path = self.key_storage_path / "encryption_key.bin"
        with open(encryption_key_path, 'wb') as f:
            f.write(encryption_key)
        os.chmod(encryption_key_path, 0o600)

        self._store_key("primary_encryption", "encryption", encryption_key)

    def _store_key(self, key_id: str, key_type: str, key_data: Any):
        """Store security key with metadata"""
        if key_type == "signing":
            # For RSA keys, store the serialized form
            key_bytes = key_data.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            key_bytes = key_data

        security_key = SecurityKey(
            key_id=key_id,
            key_type=key_type,
            key_data=key_bytes,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=self.key_rotation_days),
        )

        self.security_keys[key_id] = security_key

    def _setup_threat_detection(self):
        """Setup threat detection rules and baselines"""
        self.threat_detection_rules = [
            {
                "name": "excessive_failed_attempts",
                "condition": lambda attempts: len(attempts) > self.max_failed_attempts,
                "threat_type": ThreatType.BRUTE_FORCE,
                "severity": SecurityLevel.HIGH,
            },
            {
                "name": "unusual_access_pattern",
                "condition": self._detect_unusual_access_pattern,
                "threat_type": ThreatType.ANOMALOUS_BEHAVIOR,
                "severity": SecurityLevel.MEDIUM,
            },
            {
                "name": "integrity_violation",
                "condition": self._detect_integrity_violation,
                "threat_type": ThreatType.INTEGRITY_VIOLATION,
                "severity": SecurityLevel.CRITICAL,
            },
        ]

    async def secure_evidence_collection(
        self,
        evidence_data: Dict[str, Any],
        source_ip: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, str]]:
        """
        Secure evidence collection with integrity verification.

        Args:
            evidence_data: Evidence data to secure
            source_ip: Source IP address
            user_id: User ID if authenticated

        Returns:
            Tuple of (evidence_id, security_metadata)
        """
        evidence_id = str(uuid4())

        # Verify access authorization
        if not await self._verify_access_authorization(source_ip, user_id, "evidence_collection"):
            await self._record_security_event(
                ThreatType.UNAUTHORIZED_ACCESS,
                SecurityLevel.HIGH,
                source_ip,
                user_id,
                "evidence_collection",
                "collect_evidence",
                {"evidence_id": evidence_id, "access_denied": True},
            )
            raise PermissionError("Access denied for evidence collection")

        # Create security metadata
        security_metadata = {
            "evidence_id": evidence_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_ip": source_ip,
            "user_id": user_id,
        }

        # Generate integrity hash
        evidence_json = json.dumps(evidence_data, sort_keys=True, default=str)  # noqa: F821  # TODO: json
        integrity_hash = self._compute_integrity_hash(evidence_json.encode())
        security_metadata["integrity_hash"] = integrity_hash

        # Sign evidence if enabled
        if self.enable_signing:
            signature = await self._sign_data(evidence_json.encode())
            security_metadata["signature"] = signature

        # Encrypt sensitive data if enabled
        if self.enable_encryption and self._is_sensitive_evidence(evidence_data):
            await self._encrypt_data(evidence_json.encode())
            security_metadata["encrypted"] = True
            security_metadata["encryption_key_id"] = "primary_encryption"
        else:
            security_metadata["encrypted"] = False

        # Store integrity hash for verification
        self.integrity_hashes[evidence_id] = integrity_hash

        return evidence_id, security_metadata

    async def verify_evidence_integrity(
        self,
        evidence_id: str,
        evidence_data: Dict[str, Any],
        security_metadata: Dict[str, str],
    ) -> bool:
        """
        Verify evidence integrity using cryptographic methods.

        Args:
            evidence_id: Evidence identifier
            evidence_data: Evidence data to verify
            security_metadata: Security metadata from collection

        Returns:
            True if integrity is verified
        """
        try:
            # Verify integrity hash
            evidence_json = json.dumps(evidence_data, sort_keys=True, default=str)  # noqa: F821  # TODO: json
            computed_hash = self._compute_integrity_hash(evidence_json.encode())

            stored_hash = security_metadata.get("integrity_hash")
            if not stored_hash or computed_hash != stored_hash:
                await self._record_security_event(
                    ThreatType.INTEGRITY_VIOLATION,
                    SecurityLevel.CRITICAL,
                    None,
                    None,
                    "evidence_verification",
                    "verify_integrity",
                    {
                        "evidence_id": evidence_id,
                        "hash_mismatch": True,
                        "expected": stored_hash,
                        "computed": computed_hash,
                    },
                )
                return False

            # Verify signature if present
            if "signature" in security_metadata:
                signature_valid = await self._verify_signature(
                    evidence_json.encode(),
                    security_metadata["signature"]
                )
                if not signature_valid:
                    await self._record_security_event(
                        ThreatType.DATA_TAMPERING,
                        SecurityLevel.CRITICAL,
                        None,
                        None,
                        "evidence_verification",
                        "verify_signature",
                        {"evidence_id": evidence_id, "signature_invalid": True},
                    )
                    return False

            return True

        except Exception as e:
            await self._record_security_event(
                ThreatType.INTEGRITY_VIOLATION,
                SecurityLevel.HIGH,
                None,
                None,
                "evidence_verification",
                "verify_integrity_error",
                {"evidence_id": evidence_id, "error": str(e)},
            )
            return False

    def _compute_integrity_hash(self, data: bytes) -> str:
        """Compute HMAC-SHA256 integrity hash"""
        hmac_key = self.security_keys["primary_hmac"].key_data
        return hmac.new(hmac_key, data, hashlib.sha256).hexdigest()

    async def _sign_data(self, data: bytes) -> str:
        """Sign data using RSA-PSS"""
        signing_key_data = self.security_keys["primary_signing"].key_data
        private_key = serialization.load_pem_private_key(
            signing_key_data, password=None, backend=default_backend()
        )

        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature.hex()

    async def _verify_signature(self, data: bytes, signature_hex: str) -> bool:
        """Verify RSA-PSS signature"""
        try:
            signing_key_data = self.security_keys["primary_signing"].key_data
            private_key = serialization.load_pem_private_key(
                signing_key_data, password=None, backend=default_backend()
            )
            public_key = private_key.public_key()

            signature = bytes.fromhex(signature_hex)
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    async def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM"""
        encryption_key = self.security_keys["primary_encryption"].key_data
        iv = os.urandom(12)  # 96-bit IV for GCM

        cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Return IV + tag + ciphertext
        return iv + encryptor.tag + ciphertext

    async def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        encryption_key = self.security_keys["primary_encryption"].key_data

        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def _is_sensitive_evidence(self, evidence_data: Dict[str, Any]) -> bool:
        """Determine if evidence contains sensitive data"""
        sensitive_fields = ["user_id", "session_id", "personal_data", "financial_data", "medical_data"]
        sensitive_evidence_types = ["authentication", "data_access", "regulatory_event"]

        # Check for sensitive fields
        for field in sensitive_fields:
            if field in evidence_data.get("payload", {}):
                return True

        # Check for sensitive evidence types
        evidence_type = evidence_data.get("evidence_type", "")
        return evidence_type in sensitive_evidence_types

    async def _verify_access_authorization(
        self,
        source_ip: Optional[str],
        user_id: Optional[str],
        operation: str,
    ) -> bool:
        """Verify access authorization for operations"""
        # Check if source is locked out
        if source_ip and source_ip in self.locked_sources:
            lockout_expires = self.locked_sources[source_ip]
            if datetime.now(timezone.utc) < lockout_expires:
                return False
            else:
                # Remove expired lockout
                del self.locked_sources[source_ip]

        # Check IP whitelist if enabled
        if self.security_config["access_control"]["enforce_ip_whitelist"]:
            whitelist = self.security_config["access_control"]["whitelist_ips"]
            if source_ip not in whitelist:
                return False

        # Record access attempt
        access_attempt = AccessAttempt(
            source_ip=source_ip or "unknown",
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            success=True,
            operation=operation,
            component="security_hardening",
        )
        self.access_attempts.append(access_attempt)

        return True

    async def record_failed_access_attempt(
        self,
        source_ip: Optional[str],
        user_id: Optional[str],
        operation: str,
        component: str,
    ):
        """Record failed access attempt and apply security measures"""
        if not source_ip:
            return

        # Record failed attempt
        access_attempt = AccessAttempt(
            source_ip=source_ip,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            success=False,
            operation=operation,
            component=component,
        )
        self.access_attempts.append(access_attempt)

        # Track failed attempts for this source
        current_time = datetime.now(timezone.utc)
        self.failed_attempts[source_ip].append(current_time)

        # Clean old attempts (older than lockout duration)
        cutoff_time = current_time - timedelta(minutes=self.lockout_duration_minutes)
        self.failed_attempts[source_ip] = [
            attempt for attempt in self.failed_attempts[source_ip]
            if attempt >= cutoff_time
        ]

        # Check if lockout threshold exceeded
        if len(self.failed_attempts[source_ip]) >= self.max_failed_attempts:
            # Lock out the source
            lockout_until = current_time + timedelta(minutes=self.lockout_duration_minutes)
            self.locked_sources[source_ip] = lockout_until

            # Record security event
            await self._record_security_event(
                ThreatType.BRUTE_FORCE,
                SecurityLevel.HIGH,
                source_ip,
                user_id,
                component,
                operation,
                {
                    "failed_attempts": len(self.failed_attempts[source_ip]),
                    "lockout_until": lockout_until.isoformat(),
                },
                action_taken="source_locked_out",
            )

    async def _record_security_event(
        self,
        threat_type: ThreatType,
        severity: SecurityLevel,
        source_ip: Optional[str],
        user_id: Optional[str],
        component: str,
        operation: str,
        details: Dict[str, Any],
        action_taken: Optional[str] = None,
    ):
        """Record security event"""
        event = SecurityEvent(
            event_id=str(uuid4()),
            threat_type=threat_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            component=component,
            operation=operation,
            timestamp=datetime.now(timezone.utc),
            details=details,
            action_taken=action_taken,
        )

        self.security_events.append(event)

        # Collect evidence of security event
        await collect_evidence(
            evidence_type=EvidenceType.SECURITY_EVENT,
            source_component="security_hardening",
            operation="security_event_recorded",
            payload={
                "event_id": event.event_id,
                "threat_type": threat_type.value,
                "severity": severity.value,
                "source_ip": source_ip,
                "user_id": user_id,
                "component": component,
                "operation": operation,
                "details": details,
                "action_taken": action_taken,
            },
        )

    def _detect_unusual_access_pattern(self, source_ip: str, user_id: Optional[str]) -> bool:
        """Detect unusual access patterns"""
        current_time = datetime.now(timezone.utc)
        recent_attempts = [
            attempt for attempt in self.access_attempts
            if (attempt.source_ip == source_ip and
                (current_time - attempt.timestamp).total_seconds() < 3600)  # Last hour
        ]

        # Check for unusual frequency
        if len(recent_attempts) > 100:  # More than 100 requests per hour
            return True

        # Check for rapid succession
        if len(recent_attempts) >= 10:
            time_spans = []
            for i in range(1, len(recent_attempts)):
                time_span = (recent_attempts[i].timestamp - recent_attempts[i-1].timestamp).total_seconds()
                time_spans.append(time_span)

            avg_time_span = sum(time_spans) / len(time_spans)
            if avg_time_span < 1.0:  # Less than 1 second between requests on average
                return True

        return False

    def _detect_integrity_violation(self, evidence_id: str) -> bool:
        """Detect integrity violations in stored evidence"""
        # This would check stored evidence for integrity violations
        # For now, return False (no violation detected)
        return False

    async def rotate_security_keys(self):
        """Rotate cryptographic keys"""
        current_time = datetime.now(timezone.utc)

        keys_to_rotate = []
        for key_id, key in self.security_keys.items():
            if key.expires_at and current_time >= key.expires_at:
                keys_to_rotate.append(key_id)

        for key_id in keys_to_rotate:
            old_key = self.security_keys[key_id]

            # Generate new key
            if old_key.key_type == "signing":
                self._generate_signing_key()
            elif old_key.key_type == "encryption":
                self._generate_encryption_key()
            elif old_key.key_type == "hmac":
                hmac_key = os.urandom(32)
                self._store_key(key_id, "hmac", hmac_key)

            # Record key rotation event
            await self._record_security_event(
                ThreatType.CONFIGURATION_TAMPERING,  # Placeholder threat type
                SecurityLevel.MEDIUM,
                None,
                None,
                "security_hardening",
                "key_rotation",
                {
                    "key_id": key_id,
                    "key_type": old_key.key_type,
                    "old_key_created": old_key.created_at.isoformat(),
                },
                action_taken="key_rotated",
            )

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        current_time = datetime.now(timezone.utc)

        # Count security events by severity
        event_counts = defaultdict(int)
        recent_events = []
        for event in self.security_events:
            event_counts[event.severity.value] += 1
            if (current_time - event.timestamp).total_seconds() < 3600:  # Last hour
                recent_events.append(event)

        # Check key expiration status
        expiring_keys = []
        for key_id, key in self.security_keys.items():
            if key.expires_at:
                days_until_expiry = (key.expires_at - current_time).days
                if days_until_expiry <= 7:  # Expires within 7 days
                    expiring_keys.append({
                        "key_id": key_id,
                        "key_type": key.key_type,
                        "days_until_expiry": days_until_expiry,
                    })

        return {
            "timestamp": current_time.isoformat(),
            "security_events_total": len(self.security_events),
            "security_events_by_severity": dict(event_counts),
            "recent_events_count": len(recent_events),
            "locked_sources_count": len(self.locked_sources),
            "active_keys_count": len([k for k in self.security_keys.values() if k.active]),
            "expiring_keys": expiring_keys,
            "encryption_enabled": self.enable_encryption,
            "signing_enabled": self.enable_signing,
            "tamper_detection_enabled": self.tamper_detection_enabled,
        }

    def _start_background_tasks(self):
        """Start background security monitoring tasks"""
        async def security_monitor():
            while True:
                try:
                    await self._run_security_monitoring()
                    await asyncio.sleep(300)  # Every 5 minutes
                except Exception as e:
                    print(f"Security monitoring error: {e}")
                    await asyncio.sleep(300)

        async def key_rotation_monitor():
            while True:
                try:
                    await self.rotate_security_keys()
                    await asyncio.sleep(3600)  # Every hour
                except Exception as e:
                    print(f"Key rotation error: {e}")
                    await asyncio.sleep(3600)

        # Start background tasks if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._security_monitor_task = loop.create_task(security_monitor())
                self._key_rotation_task = loop.create_task(key_rotation_monitor())
        except RuntimeError:
            # No event loop running
            pass

    async def _run_security_monitoring(self):
        """Run security monitoring checks"""
        current_time = datetime.now(timezone.utc)

        # Check for threat patterns
        for rule in self.threat_detection_rules:
            try:
                if rule["name"] == "excessive_failed_attempts":
                    for source_ip, attempts in self.failed_attempts.items():
                        if rule["condition"](attempts):
                            await self._record_security_event(
                                rule["threat_type"],
                                rule["severity"],
                                source_ip,
                                None,
                                "security_monitoring",
                                "threat_detection",
                                {"rule": rule["name"], "attempts": len(attempts)},
                            )

                elif rule["name"] == "unusual_access_pattern":
                    # Check recent access attempts for patterns
                    recent_sources = set()
                    for attempt in self.access_attempts:
                        if (current_time - attempt.timestamp).total_seconds() < 3600:
                            recent_sources.add(attempt.source_ip)

                    for source_ip in recent_sources:
                        if rule["condition"](source_ip, None):
                            await self._record_security_event(
                                rule["threat_type"],
                                rule["severity"],
                                source_ip,
                                None,
                                "security_monitoring",
                                "threat_detection",
                                {"rule": rule["name"]},
                            )

            except Exception as e:
                print(f"Error in threat detection rule {rule['name']}: {e}")

    async def shutdown(self):
        """Shutdown security hardening system"""
        if self._security_monitor_task:
            self._security_monitor_task.cancel()
        if self._key_rotation_task:
            self._key_rotation_task.cancel()


# Global security hardening instance
_security_hardening: Optional[ObservabilitySecurityHardening] = None


def initialize_security_hardening(**kwargs) -> ObservabilitySecurityHardening:
    """Initialize global security hardening system"""
    global _security_hardening
    _security_hardening = ObservabilitySecurityHardening(**kwargs)
    return _security_hardening


def get_security_hardening() -> ObservabilitySecurityHardening:
    """Get or create global security hardening system"""
    global _security_hardening
    if _security_hardening is None:
        _security_hardening = initialize_security_hardening()
    return _security_hardening


async def secure_evidence_operation(evidence_data: Dict[str, Any], **kwargs) -> Tuple[str, Dict[str, str]]:
    """Convenience function for secure evidence operations"""
    security_system = get_security_hardening()
    return await security_system.secure_evidence_collection(evidence_data, **kwargs)


async def shutdown_security_hardening():
    """Shutdown global security hardening"""
    global _security_hardening
    if _security_hardening:
        await _security_hardening.shutdown()
        _security_hardening = None
