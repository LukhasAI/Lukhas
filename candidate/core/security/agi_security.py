"""
LUKHAS AGI Security Layer
Enterprise-grade security for AGI operations
"""
import asyncio
import hashlib
import json
import secrets
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional


class SecurityLevel(Enum):
    """Security clearance levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVILEGED = "privileged"
    CRITICAL = "critical"
    PERSONALITY = "personality"  # Highest level for personality data


class ThreatType(Enum):
    """Types of security threats"""

    INJECTION = "injection"
    MANIPULATION = "manipulation"
    EXTRACTION = "extraction"
    IMPERSONATION = "impersonation"
    OVERFLOW = "overflow"
    ADVERSARIAL = "adversarial"
    CONSCIOUSNESS_HIJACK = "consciousness_hijack"


@dataclass
class SecurityContext:
    """Security context for operations"""

    user_id: str
    session_id: str
    clearance_level: SecurityLevel
    permissions: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityIncident:
    """Security incident record"""

    id: str
    threat_type: ThreatType
    severity: float  # 0.0 to 1.0
    source: str
    target: str
    timestamp: datetime
    details: dict[str, Any]
    blocked: bool
    response_actions: list[str] = field(default_factory=list)


class SecurityValidator(ABC):
    """Abstract base for security validators"""

    @abstractmethod
    async def validate(self, data: Any, context: SecurityContext) -> tuple[bool, Optional[str]]:
        """Validate data/operation"""


class AGISecuritySystem:
    """
    Comprehensive security system for LUKHAS AGI
    Protects against threats while preserving functionality
    """

    def __init__(self):
        # Security configuration
        self.security_config = {
            "max_input_length": 10000,
            "max_memory_access": 1000,
            "max_consciousness_depth": 10,
            "personality_lock": True,
        }

        # Access control
        self.access_control = AccessControlSystem()
        self.session_manager = SessionManager()

        # Threat detection
        self.threat_detector = ThreatDetectionSystem()
        self.anomaly_detector = AnomalyDetector()

        # Data protection
        self.encryption_manager = EncryptionManager()
        self.sanitizer = DataSanitizer()

        # Audit logging
        self.audit_logger = AuditLogger()
        self.incident_history: list[SecurityIncident] = []

        # Security validators
        self.validators: dict[str, SecurityValidator] = {
            "input": InputValidator(),
            "memory": MemoryAccessValidator(),
            "consciousness": ConsciousnessValidator(),
            "api": APIValidator(),
        }

        # Rate limiting
        self.rate_limiter = RateLimiter()

        # Secure channels
        self.secure_channels: dict[str, SecureChannel] = {}

        self._running = False

    async def initialize(self):
        """Initialize security system"""
        self._running = True

        # Start security monitoring
        asyncio.create_task(self._threat_monitor_loop())
        asyncio.create_task(self._audit_loop())
        asyncio.create_task(self._key_rotation_loop())

        # Initialize subsystems
        await self.encryption_manager.initialize()
        await self.threat_detector.initialize()

    async def create_session(self, user_id: str, auth_token: str) -> Optional[SecurityContext]:
        """
        Create secure session

        Args:
            user_id: User identifier
            auth_token: Authentication token

        Returns:
            Security context if authenticated
        """
        # Verify authentication
        if not await self._verify_auth_token(user_id, auth_token):
            await self.audit_logger.log_auth_failure(user_id)
            return None

        # Create session
        session_id = self._generate_session_id()
        clearance = await self.access_control.get_user_clearance(user_id)
        permissions = await self.access_control.get_user_permissions(user_id)

        context = SecurityContext(
            user_id=user_id,
            session_id=session_id,
            clearance_level=clearance,
            permissions=permissions,
        )

        # Store session
        await self.session_manager.create_session(context)

        # Audit successful auth
        await self.audit_logger.log_auth_success(user_id, session_id)

        return context

    async def validate_operation(
        self, operation: str, data: Any, context: SecurityContext
    ) -> tuple[bool, Optional[str]]:
        """
        Validate operation security

        Args:
            operation: Operation name
            data: Operation data
            context: Security context

        Returns:
            (is_valid, error_message)
        """
        # Check rate limits
        if not await self.rate_limiter.check_limit(context.user_id, operation):
            return False, "Rate limit exceeded"

        # Check permissions
        if not self.access_control.check_permission(context, operation):
            return False, "Insufficient permissions"

        # Validate input
        for validator_name, validator in self.validators.items():
            if validator_name in operation.lower():
                is_valid, error = await validator.validate(data, context)
                if not is_valid:
                    return False, f"Validation failed: {error}"

        # Check for threats
        threat = await self.threat_detector.detect_threat(operation, data, context)
        if threat:
            await self._handle_threat(threat, context)
            return (
                False,
                f"Security threat detected: {threat.threat_type.value}",
            )

        # Check anomalies
        if await self.anomaly_detector.is_anomalous(operation, data, context):
            await self._investigate_anomaly(operation, data, context)
            # Don't block, but flag for investigation

        return True, None

    async def secure_data(self, data: Any, security_level: SecurityLevel) -> bytes:
        """
        Secure data based on security level

        Args:
            data: Data to secure
            security_level: Required security level

        Returns:
            Encrypted data
        """
        # Serialize data
        serialized = json.dumps(data).encode("utf-8")

        # Encrypt based on security level
        if security_level == SecurityLevel.PERSONALITY:
            # Highest security for personality data
            encrypted = await self.encryption_manager.encrypt_personality(serialized)
        elif security_level in [
            SecurityLevel.CRITICAL,
            SecurityLevel.PRIVILEGED,
        ]:
            encrypted = await self.encryption_manager.encrypt_sensitive(serialized)
        else:
            encrypted = await self.encryption_manager.encrypt_standard(serialized)

        return encrypted

    async def create_secure_channel(self, channel_id: str, participants: list[str]) -> "SecureChannel":
        """Create secure communication channel"""
        channel = SecureChannel(channel_id, participants, self.encryption_manager)
        self.secure_channels[channel_id] = channel
        return channel

    # Threat handling
    async def _handle_threat(self, threat: SecurityIncident, context: SecurityContext):
        """Handle detected security threat"""
        # Record incident
        self.incident_history.append(threat)

        # Take response actions based on threat type
        if threat.threat_type == ThreatType.CONSCIOUSNESS_HIJACK:
            # Critical threat - immediate isolation
            threat.response_actions.append("isolate_consciousness")
            await self._isolate_consciousness()

        elif threat.threat_type == ThreatType.INJECTION:
            # Block and sanitize
            threat.response_actions.append("block_and_sanitize")

        elif threat.threat_type == ThreatType.EXTRACTION:
            # Limit data access
            threat.response_actions.append("limit_access")
            await self.access_control.limit_user_access(context.user_id)

        # Notify security team if severe
        if threat.severity > 0.7:
            await self._notify_security_team(threat)

    async def _investigate_anomaly(self, operation: str, data: Any, context: SecurityContext):
        """Investigate detected anomaly"""
        # Create investigation record
        investigation = {
            "operation": operation,
            "user_id": context.user_id,
            "timestamp": datetime.now(timezone.utc),
            "data_hash": hashlib.sha256(str(data).encode()).hexdigest(),
        }

        # Queue for manual review if needed
        await self.audit_logger.log_anomaly(investigation)

    # Security monitoring
    async def _threat_monitor_loop(self):
        """Monitor for security threats"""
        while self._running:
            await asyncio.sleep(10)  # Check every 10 seconds

            # Check active sessions
            active_sessions = await self.session_manager.get_active_sessions()

            for session in active_sessions:
                # Check for session anomalies
                if await self._is_session_compromised(session):
                    await self.session_manager.terminate_session(session.session_id)

    async def _audit_loop(self):
        """Periodic audit tasks"""
        while self._running:
            await asyncio.sleep(300)  # Every 5 minutes

            # Audit access patterns
            await self.audit_logger.analyze_access_patterns()

            # Check for privilege escalation attempts
            await self._check_privilege_escalation()

    async def _key_rotation_loop(self):
        """Rotate encryption keys periodically"""
        while self._running:
            await asyncio.sleep(86400)  # Daily

            await self.encryption_manager.rotate_keys()

    # Helper methods
    async def _verify_auth_token(self, user_id: str, token: str) -> bool:
        """Verify authentication token"""
        # In production, would verify against auth service
        return len(token) > 32  # Simplified

    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)

    async def _isolate_consciousness(self):
        """Emergency consciousness isolation"""
        # In production, would isolate consciousness subsystem

    async def _notify_security_team(self, threat: SecurityIncident):
        """Notify security team of critical threat"""
        # In production, would send alerts

    async def _is_session_compromised(self, session: SecurityContext) -> bool:
        """Check if session shows signs of compromise"""
        # Check for suspicious patterns
        return False  # Simplified

    async def _check_privilege_escalation(self):
        """Check for privilege escalation attempts"""
        # Analyze permission request patterns


class AccessControlSystem:
    """Role-based access control"""

    def __init__(self):
        self.user_roles: dict[str, set[str]] = {}
        self.role_permissions: dict[str, set[str]] = {
            "admin": {"*"},  # All permissions
            "researcher": {"read", "analyze", "experiment"},
            "user": {"read", "interact"},
            "api_client": {"api.read", "api.write"},
        }

        self.clearance_levels: dict[str, SecurityLevel] = {
            "admin": SecurityLevel.PERSONALITY,
            "researcher": SecurityLevel.PRIVILEGED,
            "user": SecurityLevel.INTERNAL,
            "api_client": SecurityLevel.PUBLIC,
        }

    async def get_user_clearance(self, user_id: str) -> SecurityLevel:
        """Get user's security clearance"""
        roles = self.user_roles.get(user_id, {"user"})

        # Highest clearance from roles
        max_clearance = SecurityLevel.PUBLIC
        for role in roles:
            clearance = self.clearance_levels.get(role, SecurityLevel.PUBLIC)
            if clearance.value > max_clearance.value:
                max_clearance = clearance

        return max_clearance

    async def get_user_permissions(self, user_id: str) -> set[str]:
        """Get user's permissions"""
        roles = self.user_roles.get(user_id, {"user"})

        permissions = set()
        for role in roles:
            permissions.update(self.role_permissions.get(role, set()))

        return permissions

    def check_permission(self, context: SecurityContext, operation: str) -> bool:
        """Check if context has permission for operation"""
        if "*" in context.permissions:
            return True

        # Check exact match
        if operation in context.permissions:
            return True

        # Check wildcard match
        return any(perm.endswith("*") and operation.startswith(perm[:-1]) for perm in context.permissions)

    async def limit_user_access(self, user_id: str):
        """Temporarily limit user access"""
        # In production, would modify user permissions


class SessionManager:
    """Secure session management"""

    def __init__(self):
        self.sessions: dict[str, SecurityContext] = {}
        self.session_activity: dict[str, datetime] = {}
        self.session_timeout = timedelta(hours=24)

    async def create_session(self, context: SecurityContext):
        """Create new session"""
        self.sessions[context.session_id] = context
        self.session_activity[context.session_id] = datetime.now(timezone.utc)

    async def get_session(self, session_id: str) -> Optional[SecurityContext]:
        """Get session if valid"""
        if session_id not in self.sessions:
            return None

        # Check timeout
        last_activity = self.session_activity.get(session_id)
        if last_activity and datetime.now(timezone.utc) - last_activity > self.session_timeout:
            await self.terminate_session(session_id)
            return None

        # Update activity
        self.session_activity[session_id] = datetime.now(timezone.utc)

        return self.sessions.get(session_id)

    async def terminate_session(self, session_id: str):
        """Terminate session"""
        self.sessions.pop(session_id, None)
        self.session_activity.pop(session_id, None)

    async def get_active_sessions(self) -> list[SecurityContext]:
        """Get all active sessions"""
        return list(self.sessions.values())


class ThreatDetectionSystem:
    """Detect security threats in real-time"""

    def __init__(self):
        self.threat_patterns = {
            ThreatType.INJECTION: [
                "eval",
                "exec",
                "__import__",
                "compile",
                "pickle",
                "marshal",
                "subprocess",
            ],
            ThreatType.MANIPULATION: [
                "personality",
                "core_values",
                "goal_alignment",
            ],
            ThreatType.CONSCIOUSNESS_HIJACK: [
                "consciousness.override",
                "awareness.replace",
            ],
        }

    async def initialize(self):
        """Initialize threat detection"""

    async def detect_threat(self, operation: str, data: Any, context: SecurityContext) -> Optional[SecurityIncident]:
        """Detect threats in operation"""
        data_str = str(data).lower()

        # Check for threat patterns
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if pattern in data_str or pattern in operation.lower():
                    return SecurityIncident(
                        id=self._generate_incident_id(),
                        threat_type=threat_type,
                        severity=0.8,
                        source=context.user_id,
                        target=operation,
                        timestamp=datetime.now(timezone.utc),
                        details={"pattern": pattern},
                        blocked=True,
                    )

        return None

    def _generate_incident_id(self) -> str:
        """Generate incident ID"""
        import uuid

        return f"incident_{uuid.uuid4().hex[:8]}"


class EncryptionManager:
    """Manage encryption operations"""

    def __init__(self):
        self.keys = {}
        self.algorithm = "AES-256-GCM"

    async def initialize(self):
        """Initialize encryption"""
        # Generate initial keys
        self.keys["standard"] = secrets.token_bytes(32)
        self.keys["sensitive"] = secrets.token_bytes(32)
        self.keys["personality"] = secrets.token_bytes(32)

    async def encrypt_standard(self, data: bytes) -> bytes:
        """Standard encryption"""
        # In production, would use proper encryption
        return self._simple_xor(data, self.keys["standard"])

    async def encrypt_sensitive(self, data: bytes) -> bytes:
        """Sensitive data encryption"""
        return self._simple_xor(data, self.keys["sensitive"])

    async def encrypt_personality(self, data: bytes) -> bytes:
        """Personality data encryption (highest security)"""
        # Multiple encryption layers
        encrypted = self._simple_xor(data, self.keys["personality"])
        encrypted = self._simple_xor(encrypted, self.keys["sensitive"])
        return encrypted

    async def rotate_keys(self):
        """Rotate encryption keys"""
        # In production, would properly rotate keys
        for key_type in self.keys:
            self.keys[key_type] = secrets.token_bytes(32)

    def _simple_xor(self, data: bytes, key: bytes) -> bytes:
        """Simple XOR encryption (for demo - use real encryption in production)"""
        return bytes(d ^ k for d, k in zip(data, key * (len(data) // len(key) + 1)))


class DataSanitizer:
    """Sanitize input/output data"""

    def sanitize_input(self, data: str) -> str:
        """Sanitize user input"""
        # Remove potential threats
        dangerous = ["<script", "javascript:", "eval(", "exec("]

        sanitized = data
        for pattern in dangerous:
            sanitized = sanitized.replace(pattern, "")

        return sanitized[:10000]  # Length limit


class RateLimiter:
    """Rate limiting for operations"""

    def __init__(self):
        self.limits = {
            "default": (100, 60),  # 100 requests per 60 seconds
            "api.write": (10, 60),
            "consciousness.access": (5, 60),
            "personality.access": (1, 300),
        }
        self.requests: dict[str, list[datetime]] = defaultdict(list)

    async def check_limit(self, user_id: str, operation: str) -> bool:
        """Check if operation is within rate limit"""
        limit_key = operation if operation in self.limits else "default"
        max_requests, window_seconds = self.limits[limit_key]

        key = f"{user_id}:{operation}"
        now = datetime.now(timezone.utc)

        # Clean old requests
        self.requests[key] = [req for req in self.requests[key] if now - req < timedelta(seconds=window_seconds)]

        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False

        # Record request
        self.requests[key].append(now)
        return True


class AnomalyDetector:
    """Detect anomalous behavior"""

    async def is_anomalous(self, operation: str, data: Any, context: SecurityContext) -> bool:
        """Check if operation is anomalous"""
        # In production, would use ML-based anomaly detection
        return False


class AuditLogger:
    """Security audit logging"""

    async def log_auth_success(self, user_id: str, session_id: str):
        """Log successful authentication"""
        # In production, would log to secure audit system

    async def log_auth_failure(self, user_id: str):
        """Log failed authentication"""

    async def log_anomaly(self, investigation: dict[str, Any]):
        """Log anomaly for investigation"""

    async def analyze_access_patterns(self):
        """Analyze access patterns for threats"""


class SecureChannel:
    """Encrypted communication channel"""

    def __init__(
        self,
        channel_id: str,
        participants: list[str],
        encryption_manager: EncryptionManager,
    ):
        self.channel_id = channel_id
        self.participants = set(participants)
        self.encryption_manager = encryption_manager
        self.message_history = []

    async def send_message(self, sender: str, message: Any) -> bool:
        """Send encrypted message"""
        if sender not in self.participants:
            return False

        encrypted = await self.encryption_manager.encrypt_sensitive(json.dumps(message).encode("utf-8"))

        self.message_history.append(
            {
                "sender": sender,
                "encrypted_message": encrypted,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        return True


# Security validators


class InputValidator(SecurityValidator):
    """Validate user inputs"""

    async def validate(self, data: Any, context: SecurityContext) -> tuple[bool, Optional[str]]:
        if isinstance(data, str) and len(data) > 10000:
            return False, "Input too long"
        return True, None


class MemoryAccessValidator(SecurityValidator):
    """Validate memory access"""

    async def validate(self, data: Any, context: SecurityContext) -> tuple[bool, Optional[str]]:
        if context.clearance_level.value < SecurityLevel.PRIVILEGED.value:
            if "personality" in str(data).lower():
                return False, "Insufficient clearance for personality memory"
        return True, None


class ConsciousnessValidator(SecurityValidator):
    """Validate consciousness operations"""

    async def validate(self, data: Any, context: SecurityContext) -> tuple[bool, Optional[str]]:
        if context.clearance_level.value < SecurityLevel.CRITICAL.value:
            return False, "Insufficient clearance for consciousness operations"
        return True, None


class APIValidator(SecurityValidator):
    """Validate API calls"""

    async def validate(self, data: Any, context: SecurityContext) -> tuple[bool, Optional[str]]:
        # Validate API request structure
        return True, None
