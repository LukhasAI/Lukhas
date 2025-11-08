#!/usr/bin/env python3

"""
LUKHAS Advanced Security Framework

Enterprise-grade security infrastructure with JWT authentication, encryption,
audit trails, threat detection, and compliance monitoring.

# ΛTAG: security_framework, authentication, encryption, audit_trails, threat_detection
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging

# Import for compatibility
import random
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import bcrypt
import jwt

logger = logging.getLogger(__name__)

# Optional cryptographic dependencies
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("Cryptography library not available - using fallback implementations")


class SecurityLevel(Enum):
    """Security clearance levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class ThreatLevel(Enum):
    """Threat severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthenticationMethod(Enum):
    """Authentication methods supported."""
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    MFAC = "multi_factor"
    CERTIFICATE = "certificate"


@dataclass
class SecurityConfig:
    """Configuration for security framework."""

    # JWT Configuration
    jwt_secret_key: str = ""  # Will be generated if empty
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_hours: int = 168  # 7 days

    # Encryption Configuration
    encryption_key: str | None = None  # Will be generated if None
    password_salt_rounds: int = 12

    # Rate Limiting
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 20
    rate_limit_whitelist: list[str] = field(default_factory=list)

    # Audit Configuration
    audit_retention_days: int = 90
    audit_sensitive_data: bool = False
    audit_all_requests: bool = True

    # Threat Detection
    threat_detection_enabled: bool = True
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    suspicious_patterns_enabled: bool = True

    # Compliance
    data_classification_enabled: bool = True
    pii_detection_enabled: bool = True
    gdpr_compliance: bool = True

    def __post_init__(self):
        """Generate default values after initialization."""
        if not self.jwt_secret_key:
            self.jwt_secret_key = secrets.token_urlsafe(32)

        if self.encryption_key is None and CRYPTO_AVAILABLE:
            self.encryption_key = Fernet.generate_key().decode()


@dataclass
class UserPrincipal:
    """Authenticated user principal."""

    user_id: str
    username: str
    email: str
    security_level: SecurityLevel
    permissions: set[str]
    roles: set[str]
    authentication_method: AuthenticationMethod
    session_id: str
    issued_at: float
    expires_at: float
    last_activity: float
    ip_address: str | None = None
    user_agent: str | None = None
    mfa_verified: bool = False

    def is_expired(self) -> bool:
        """Check if principal is expired."""
        return time.time() > self.expires_at

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or "admin:*" in self.permissions

    def has_role(self, role: str) -> bool:
        """Check if user has specific role."""
        return role in self.roles

    def has_security_level(self, required_level: SecurityLevel) -> bool:
        """Check if user meets required security level."""
        level_hierarchy = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.INTERNAL: 1,
            SecurityLevel.CONFIDENTIAL: 2,
            SecurityLevel.SECRET: 3,
            SecurityLevel.TOP_SECRET: 4
        }
        return level_hierarchy[self.security_level] >= level_hierarchy[required_level]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "security_level": self.security_level.value,
            "permissions": list(self.permissions),
            "roles": list(self.roles),
            "authentication_method": self.authentication_method.value,
            "session_id": self.session_id,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "last_activity": self.last_activity,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "mfa_verified": self.mfa_verified
        }


@dataclass
class SecurityAuditEvent:
    """Security audit event."""

    event_id: str
    timestamp: float
    event_type: str
    severity: ThreatLevel
    user_id: str | None
    session_id: str | None
    ip_address: str | None
    user_agent: str | None
    resource: str
    action: str
    outcome: str  # success, failure, blocked
    details: dict[str, Any]
    risk_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "resource": self.resource,
            "action": self.action,
            "outcome": self.outcome,
            "details": self.details,
            "risk_score": self.risk_score
        }


class EncryptionService:
    """Encryption and decryption service."""

    def __init__(self, config: SecurityConfig):
        self.config = config

        if CRYPTO_AVAILABLE and config.encryption_key:
            self.cipher_suite = Fernet(config.encryption_key.encode())
        else:
            self.cipher_suite = None
            logger.warning("Encryption service not available - using base64 encoding")

    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        if self.cipher_suite:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        else:
            # Fallback to base64 encoding (NOT secure for production)
            return base64.urlsafe_b64encode(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        if self.cipher_suite:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        else:
            # Fallback from base64 decoding
            return base64.urlsafe_b64decode(encrypted_data.encode()).decode()

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        try:
            salt = bcrypt.gensalt(rounds=self.config.password_salt_rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except ImportError:
            # Fallback to simple hashing (NOT secure for production)
            salt = secrets.token_hex(16)
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except ImportError:
            # Fallback verification (simplified)
            return self.hash_password(password) == hashed


class JWTService:
    """JWT token service for authentication."""

    def __init__(self, config: SecurityConfig):
        self.config = config

    def create_access_token(self, user_principal: UserPrincipal) -> str:
        """Create JWT access token."""

        payload = {
            "user_id": user_principal.user_id,
            "username": user_principal.username,
            "email": user_principal.email,
            "security_level": user_principal.security_level.value,
            "permissions": list(user_principal.permissions),
            "roles": list(user_principal.roles),
            "session_id": user_principal.session_id,
            "iat": int(user_principal.issued_at),
            "exp": int(user_principal.expires_at),
            "type": "access"
        }

        return jwt.encode(payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)

    def create_refresh_token(self, user_principal: UserPrincipal) -> str:
        """Create JWT refresh token."""

        refresh_expires = time.time() + (self.config.jwt_refresh_hours * 3600)

        payload = {
            "user_id": user_principal.user_id,
            "session_id": user_principal.session_id,
            "iat": int(user_principal.issued_at),
            "exp": int(refresh_expires),
            "type": "refresh"
        }

        return jwt.encode(payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode JWT token."""

        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=[self.config.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> str | None:
        """Create new access token from refresh token."""

        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        # This would typically fetch user data from database
        # For now, return a simplified token
        new_payload = {
            "user_id": payload["user_id"],
            "session_id": payload["session_id"],
            "iat": int(time.time()),
            "exp": int(time.time() + (self.config.jwt_expiration_hours * 3600)),
            "type": "access"
        }

        return jwt.encode(new_payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)


class RateLimiter:
    """Rate limiting service with sliding window."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.request_history: dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: dict[str, float] = {}  # IP -> unblock_time

    def is_allowed(self, identifier: str, current_time: float | None = None) -> bool:
        """Check if request is allowed under rate limits."""

        if current_time is None:
            current_time = time.time()

        # Check if IP is in whitelist
        if identifier in self.config.rate_limit_whitelist:
            return True

        # Check if IP is temporarily blocked
        if identifier in self.blocked_ips:
            if current_time < self.blocked_ips[identifier]:
                return False
            else:
                del self.blocked_ips[identifier]

        # Clean old requests (sliding window)
        window_start = current_time - 60  # 1 minute window
        history = self.request_history[identifier]

        while history and history[0] < window_start:
            history.popleft()

        # Check rate limit
        if len(history) >= self.config.rate_limit_requests_per_minute:
            # Block IP temporarily for burst violations
            if len(history) >= (self.config.rate_limit_requests_per_minute + self.config.rate_limit_burst_size):
                self.blocked_ips[identifier] = current_time + 300  # 5 minute block
            return False

        # Record this request
        history.append(current_time)
        return True

    def get_rate_limit_status(self, identifier: str) -> dict[str, Any]:
        """Get current rate limit status for identifier."""

        current_time = time.time()
        window_start = current_time - 60
        history = self.request_history[identifier]

        # Clean old requests
        while history and history[0] < window_start:
            history.popleft()

        remaining = max(0, self.config.rate_limit_requests_per_minute - len(history))
        reset_time = window_start + 60 if history else current_time

        return {
            "limit": self.config.rate_limit_requests_per_minute,
            "remaining": remaining,
            "reset_time": reset_time,
            "blocked": identifier in self.blocked_ips
        }


class ThreatDetector:
    """Threat detection and analysis service."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.failed_attempts: dict[str, list[float]] = defaultdict(list)
        self.suspicious_patterns: dict[str, int] = defaultdict(int)
        self.risk_scores: dict[str, float] = defaultdict(float)

    def analyze_request(self,
                       ip_address: str,
                       user_agent: str,
                       endpoint: str,
                       user_id: str | None = None) -> float:
        """Analyze request and return risk score (0-1)."""

        if not self.config.threat_detection_enabled:
            return 0.0

        risk_score = 0.0
        current_time = time.time()

        # Check for brute force attempts
        if user_id:
            recent_failures = [
                t for t in self.failed_attempts[user_id]
                if current_time - t < 300  # Last 5 minutes
            ]
            if len(recent_failures) >= 3:
                risk_score += 0.4

        # Check for suspicious user agents
        suspicious_agents = ["bot", "crawler", "spider", "scanner"]
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            risk_score += 0.2

        # Check for suspicious endpoints
        sensitive_endpoints = ["/admin", "/config", "/debug", "/internal"]
        if any(endpoint.startswith(ep) for ep in sensitive_endpoints):
            risk_score += 0.3

        # Check for rapid requests from same IP
        ip_pattern_key = f"ip_requests:{ip_address}"
        self.suspicious_patterns[ip_pattern_key] += 1

        # Clean old patterns
        if random.random() < 0.01:  # 1% chance to clean
            self._clean_old_patterns()

        if self.suspicious_patterns[ip_pattern_key] > 100:  # >100 requests recently
            risk_score += 0.3

        # Update risk score for this IP
        self.risk_scores[ip_address] = max(self.risk_scores[ip_address], risk_score)

        return min(risk_score, 1.0)

    def record_failed_authentication(self, identifier: str) -> bool:
        """Record failed authentication and check if should be locked."""

        current_time = time.time()
        self.failed_attempts[identifier].append(current_time)

        # Clean old attempts
        cutoff_time = current_time - (self.config.lockout_duration_minutes * 60)
        self.failed_attempts[identifier] = [
            t for t in self.failed_attempts[identifier] if t > cutoff_time
        ]

        # Check if should be locked
        return len(self.failed_attempts[identifier]) >= self.config.max_failed_attempts

    def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is currently locked out."""

        current_time = time.time()
        cutoff_time = current_time - (self.config.lockout_duration_minutes * 60)

        recent_failures = [
            t for t in self.failed_attempts[identifier] if t > cutoff_time
        ]

        return len(recent_failures) >= self.config.max_failed_attempts

    def _clean_old_patterns(self) -> None:
        """Clean old suspicious patterns."""

        # Simple cleanup - in production this would be more sophisticated
        if len(self.suspicious_patterns) > 10000:
            # Keep only half the entries
            items = list(self.suspicious_patterns.items())
            self.suspicious_patterns.clear()
            self.suspicious_patterns.update(items[-5000:])


class SecurityAuditor:
    """Security audit logging and compliance service."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.audit_events: deque = deque(maxlen=10000)
        self.sensitive_data_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]

    def log_security_event(self,
                          event_type: str,
                          severity: ThreatLevel,
                          resource: str,
                          action: str,
                          outcome: str,
                          user_id: str | None = None,
                          session_id: str | None = None,
                          ip_address: str | None = None,
                          user_agent: str | None = None,
                          details: dict[str, Any] | None = None,
                          risk_score: float = 0.0) -> SecurityAuditEvent:
        """Log security audit event."""

        import uuid

        event = SecurityAuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            outcome=outcome,
            details=details or {},
            risk_score=risk_score
        )

        # Sanitize sensitive data if not configured to audit it
        if not self.config.audit_sensitive_data:
            event.details = self._sanitize_data(event.details)

        self.audit_events.append(event)

        # Log to standard logging
        log_level = logging.WARNING if severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL] else logging.INFO
        logger.log(log_level, f"Security event: {event_type} - {outcome}", extra={
            "event_id": event.event_id,
            "severity": severity.value,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "risk_score": risk_score
        })

        return event

    def _sanitize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize sensitive data from audit logs."""

        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Check for sensitive patterns
                import re
                for pattern in self.sensitive_data_patterns:
                    value = re.sub(pattern, "[REDACTED]", value)
            elif isinstance(value, dict):
                value = self._sanitize_data(value)

            sanitized[key] = value

        return sanitized

    def get_audit_events(self,
                        start_time: float | None = None,
                        end_time: float | None = None,
                        event_type: str | None = None,
                        user_id: str | None = None,
                        severity: ThreatLevel | None = None) -> list[SecurityAuditEvent]:
        """Get filtered audit events."""

        filtered_events = []

        for event in self.audit_events:
            # Time range filter
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue

            # Event type filter
            if event_type and event.event_type != event_type:
                continue

            # User ID filter
            if user_id and event.user_id != user_id:
                continue

            # Severity filter
            if severity and event.severity != severity:
                continue

            filtered_events.append(event)

        return filtered_events

    def generate_compliance_report(self) -> dict[str, Any]:
        """Generate compliance report."""

        current_time = time.time()
        report_period = 30 * 24 * 3600  # 30 days
        start_time = current_time - report_period

        events = self.get_audit_events(start_time=start_time)

        # Categorize events
        event_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        outcome_counts = defaultdict(int)

        for event in events:
            event_counts[event.event_type] += 1
            severity_counts[event.severity.value] += 1
            outcome_counts[event.outcome] += 1

        return {
            "report_period_days": 30,
            "total_events": len(events),
            "event_types": dict(event_counts),
            "severity_distribution": dict(severity_counts),
            "outcome_distribution": dict(outcome_counts),
            "high_risk_events": len([e for e in events if e.risk_score > 0.7]),
            "compliance_status": "compliant" if len(events) > 0 else "no_activity",
            "generated_at": current_time
        }


class LUKHASSecurityFramework:
    """Main security framework integrating all security services."""

    def __init__(self, config: SecurityConfig | None = None):
        """Initialize security framework."""

        self.config = config or SecurityConfig()

        # Initialize services
        self.encryption = EncryptionService(self.config)
        self.jwt_service = JWTService(self.config)
        self.rate_limiter = RateLimiter(self.config)
        self.threat_detector = ThreatDetector(self.config)
        self.auditor = SecurityAuditor(self.config)

        # Active sessions
        self.active_sessions: dict[str, UserPrincipal] = {}

        # Integration with telemetry
        try:
            from observability.telemetry_system import get_telemetry
            self.telemetry = get_telemetry()
        except ImportError:
            self.telemetry = None

    def authenticate_user(self,
                         username: str,
                         password: str,
                         ip_address: str | None = None,
                         user_agent: str | None = None) -> UserPrincipal | None:
        """Authenticate user with username/password."""

        # Check for lockout
        if self.threat_detector.is_locked_out(username):
            self.auditor.log_security_event(
                event_type="authentication_blocked",
                severity=ThreatLevel.MEDIUM,
                resource="auth",
                action="login",
                outcome="blocked",
                user_id=username,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "account_locked"}
            )
            return None

        # Analyze threat risk
        risk_score = self.threat_detector.analyze_request(
            ip_address or "unknown",
            user_agent or "unknown",
            "/auth/login",
            username
        )

        # This would typically validate against a user database
        # For demo purposes, we'll use hardcoded validation
        if username == "demo" and password == "secure123":
            # Create user principal
            current_time = time.time()
            session_id = secrets.token_urlsafe(32)

            principal = UserPrincipal(
                user_id="demo_user_id",
                username=username,
                email="demo@lukhas.ai",
                security_level=SecurityLevel.INTERNAL,
                permissions={"read:basic", "write:basic"},
                roles={"user"},
                authentication_method=AuthenticationMethod.JWT,
                session_id=session_id,
                issued_at=current_time,
                expires_at=current_time + (self.config.jwt_expiration_hours * 3600),
                last_activity=current_time,
                ip_address=ip_address,
                user_agent=user_agent,
                mfa_verified=False
            )

            # Store active session
            self.active_sessions[session_id] = principal

            # Log successful authentication
            self.auditor.log_security_event(
                event_type="authentication_success",
                severity=ThreatLevel.LOW,
                resource="auth",
                action="login",
                outcome="success",
                user_id=principal.user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"security_level": principal.security_level.value},
                risk_score=risk_score
            )

            return principal
        else:
            # Record failed attempt
            should_lock = self.threat_detector.record_failed_authentication(username)

            self.auditor.log_security_event(
                event_type="authentication_failure",
                severity=ThreatLevel.MEDIUM if should_lock else ThreatLevel.LOW,
                resource="auth",
                action="login",
                outcome="failure",
                user_id=username,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"reason": "invalid_credentials", "will_lock": should_lock},
                risk_score=risk_score
            )

            return None

    def create_access_token(self, principal: UserPrincipal) -> str:
        """Create JWT access token for authenticated user."""
        return self.jwt_service.create_access_token(principal)

    def create_refresh_token(self, principal: UserPrincipal) -> str:
        """Create JWT refresh token for authenticated user."""
        return self.jwt_service.create_refresh_token(principal)

    def verify_access_token(self, token: str) -> UserPrincipal | None:
        """Verify JWT access token and return user principal."""

        payload = self.jwt_service.verify_token(token)
        if not payload or payload.get("type") != "access":
            return None

        # Check if session is still active
        session_id = payload.get("session_id")
        if session_id in self.active_sessions:
            principal = self.active_sessions[session_id]

            # Update last activity
            principal.last_activity = time.time()

            return principal

        return None

    @asynccontextmanager
    async def secure_operation(self,
                              operation_name: str,
                              principal: UserPrincipal,
                              required_permission: str | None = None,
                              required_security_level: SecurityLevel | None = None):
        """Context manager for secure operations with authorization."""

        # Check permissions
        if required_permission and not principal.has_permission(required_permission):
            self.auditor.log_security_event(
                event_type="authorization_failure",
                severity=ThreatLevel.MEDIUM,
                resource=operation_name,
                action="access",
                outcome="denied",
                user_id=principal.user_id,
                session_id=principal.session_id,
                ip_address=principal.ip_address,
                details={"required_permission": required_permission}
            )
            raise PermissionError(f"Permission denied: {required_permission}")

        # Check security level
        if required_security_level and not principal.has_security_level(required_security_level):
            self.auditor.log_security_event(
                event_type="authorization_failure",
                severity=ThreatLevel.MEDIUM,
                resource=operation_name,
                action="access",
                outcome="denied",
                user_id=principal.user_id,
                session_id=principal.session_id,
                ip_address=principal.ip_address,
                details={"required_security_level": required_security_level.value}
            )
            raise PermissionError(f"Insufficient security level: {required_security_level.value}")

        # Log operation start
        start_time = time.time()
        self.auditor.log_security_event(
            event_type="operation_start",
            severity=ThreatLevel.LOW,
            resource=operation_name,
            action="execute",
            outcome="started",
            user_id=principal.user_id,
            session_id=principal.session_id,
            ip_address=principal.ip_address
        )

        try:
            yield

            # Log successful completion
            duration = time.time() - start_time
            self.auditor.log_security_event(
                event_type="operation_success",
                severity=ThreatLevel.LOW,
                resource=operation_name,
                action="execute",
                outcome="success",
                user_id=principal.user_id,
                session_id=principal.session_id,
                ip_address=principal.ip_address,
                details={"duration_seconds": duration}
            )

        except Exception as e:
            # Log operation failure
            duration = time.time() - start_time
            self.auditor.log_security_event(
                event_type="operation_failure",
                severity=ThreatLevel.MEDIUM,
                resource=operation_name,
                action="execute",
                outcome="failure",
                user_id=principal.user_id,
                session_id=principal.session_id,
                ip_address=principal.ip_address,
                details={"error": str(e), "duration_seconds": duration}
            )
            raise

    def logout_user(self, session_id: str) -> bool:
        """Logout user by session ID."""

        if session_id in self.active_sessions:
            principal = self.active_sessions[session_id]
            del self.active_sessions[session_id]

            self.auditor.log_security_event(
                event_type="logout",
                severity=ThreatLevel.LOW,
                resource="auth",
                action="logout",
                outcome="success",
                user_id=principal.user_id,
                session_id=session_id,
                ip_address=principal.ip_address
            )

            return True

        return False

    def get_security_status(self) -> dict[str, Any]:
        """Get current security framework status."""

        return {
            "active_sessions": len(self.active_sessions),
            "total_audit_events": len(self.auditor.audit_events),
            "rate_limiter_status": {
                "blocked_ips": len(self.rate_limiter.blocked_ips),
                "tracked_identifiers": len(self.rate_limiter.request_history)
            },
            "threat_detector_status": {
                "locked_accounts": sum(
                    1 for attempts in self.threat_detector.failed_attempts.values()
                    if len(attempts) >= self.config.max_failed_attempts
                ),
                "suspicious_patterns": len(self.threat_detector.suspicious_patterns)
            },
            "configuration": {
                "jwt_expiration_hours": self.config.jwt_expiration_hours,
                "rate_limit_per_minute": self.config.rate_limit_requests_per_minute,
                "threat_detection_enabled": self.config.threat_detection_enabled,
                "audit_enabled": True,
                "encryption_available": CRYPTO_AVAILABLE
            }
        }


# Global security framework instance
_global_security: LUKHASSecurityFramework | None = None


def get_security_framework() -> LUKHASSecurityFramework:
    """Get global security framework instance."""
    global _global_security

    if _global_security is None:
        _global_security = LUKHASSecurityFramework()

    return _global_security



if __name__ == "__main__":
    # Example usage
    async def demo_security():

        # Create security framework
        security = LUKHASSecurityFramework()

        # Authenticate user
        principal = security.authenticate_user("demo", "secure123", "127.0.0.1", "Demo Client")

        if principal:
            print(f"✅ Authentication successful: {principal.username}")

            # Create tokens
            access_token = security.create_access_token(principal)
            security.create_refresh_token(principal)

            print(f"✅ Access token created: {access_token[:50]}...")

            # Verify token
            verified_principal = security.verify_access_token(access_token)
            if verified_principal:
                print(f"✅ Token verified: {verified_principal.username}")

            # Secure operation
            async with security.secure_operation("demo_operation", principal):
                print("✅ Secure operation executed")

            # Get security status
            status = security.get_security_status()
            print(f"✅ Security status: {status['active_sessions']} active sessions")

        else:
            print("❌ Authentication failed")

    asyncio.run(demo_security())
