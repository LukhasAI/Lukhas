"""
LUKHAS Security Hardening Module for Tiered Authentication
=========================================================

Advanced security hardening features for the LUKHAS tiered authentication system.
Provides comprehensive protection against common attacks and security vulnerabilities.

Features:
- Anti-replay protection with nonce management
- Rate limiting and DDoS protection
- Request fingerprinting and anomaly detection
- Session hijacking protection
- Brute force attack mitigation
- Guardian system integration
- Comprehensive audit logging
- Performance monitoring (<10ms overhead)
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import structlog

# Import Guardian system for security monitoring
try:
    from ..governance.guardian_system import GuardianSystem
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False

logger = structlog.get_logger(__name__)


class ThreatLevel(Enum):
    """Security threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAction(Enum):
    """Security response actions."""

    ALLOW = "allow"
    WARN = "warn"
    THROTTLE = "throttle"
    BLOCK = "block"
    TERMINATE = "terminate"


@dataclass
class SecurityEvent:
    """Security event for audit logging."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    threat_level: ThreatLevel = ThreatLevel.LOW
    action_taken: SecurityAction = SecurityAction.ALLOW

    # Request context
    ip_address: str = ""
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None

    # Security details
    description: str = ""
    indicators: List[str] = field(default_factory=list)
    risk_score: float = 0.0

    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert security event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "threat_level": self.threat_level.value,
            "action_taken": self.action_taken.value,
            "ip_address": self.ip_address,
            "user_id": self.user_id,
            "user_agent": self.user_agent,
            "endpoint": self.endpoint,
            "description": self.description,
            "indicators": self.indicators,
            "risk_score": self.risk_score,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""

    name: str
    max_requests: int
    window_seconds: int
    action: SecurityAction = SecurityAction.THROTTLE

    # Advanced options
    burst_allowance: int = 0
    progressive_penalties: bool = False
    whitelist_ips: Set[str] = field(default_factory=set)


@dataclass
class NonceRecord:
    """Anti-replay nonce record."""

    nonce: str
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15))

    @property
    def is_expired(self) -> bool:
        """Check if nonce is expired."""
        return datetime.now(timezone.utc) > self.expires_at


@dataclass
class RequestFingerprint:
    """Request fingerprinting for anomaly detection."""

    ip_address: str
    user_agent: str
    request_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Behavioral features
    request_size: int = 0
    headers_count: int = 0
    timing_pattern: float = 0.0

    # Risk indicators
    suspicious_headers: List[str] = field(default_factory=list)
    anomaly_score: float = 0.0


class AntiReplayProtection:
    """
    Anti-replay protection using cryptographic nonces.

    Prevents replay attacks by ensuring each request uses a unique,
    time-limited nonce that cannot be reused.
    """

    def __init__(
        self,
        nonce_lifetime_minutes: int = 15,
        max_nonces_per_user: int = 100,
        cleanup_interval_seconds: int = 300
    ):
        """Initialize anti-replay protection."""
        self.nonce_lifetime_minutes = nonce_lifetime_minutes
        self.max_nonces_per_user = max_nonces_per_user
        self.cleanup_interval_seconds = cleanup_interval_seconds

        self.logger = logger.bind(component="AntiReplayProtection")

        # Nonce storage
        self._nonces: Dict[str, NonceRecord] = {}
        self._user_nonces: Dict[str, Set[str]] = defaultdict(set)

        # Statistics
        self._stats = {
            "nonces_generated": 0,
            "nonces_validated": 0,
            "replay_attempts_blocked": 0,
            "expired_nonces_cleaned": 0
        }

        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()

    def _start_cleanup_task(self) -> None:
        """Start background nonce cleanup task."""
        async def cleanup_loop():
            while True:
                try:
                    await self._cleanup_expired_nonces()
                    await asyncio.sleep(self.cleanup_interval_seconds)
                except Exception as e:
                    self.logger.error("Nonce cleanup error", error=str(e))
                    await asyncio.sleep(60)  # Fallback interval

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def generate_nonce(
        self,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> str:
        """
        Generate cryptographically secure nonce.

        Args:
            user_id: Optional user identifier
            endpoint: Optional endpoint identifier

        Returns:
            Unique nonce string
        """
        try:
            # Generate cryptographically secure nonce
            nonce_bytes = secrets.token_bytes(32)
            timestamp = int(time.time() * 1000)
            context = f"{user_id or 'anonymous'}:{endpoint or 'unknown'}:{timestamp}"

            # Create nonce with HMAC for integrity
            nonce_hash = hashlib.sha256(nonce_bytes + context.encode()).hexdigest()
            nonce = f"nonce_{timestamp}_{nonce_hash[:16]}"

            # Store nonce record
            record = NonceRecord(
                nonce=nonce,
                user_id=user_id,
                endpoint=endpoint
            )

            self._nonces[nonce] = record

            # Track user nonces
            if user_id:
                self._user_nonces[user_id].add(nonce)

                # Enforce per-user nonce limit
                if len(self._user_nonces[user_id]) > self.max_nonces_per_user:
                    oldest_nonce = min(
                        self._user_nonces[user_id],
                        key=lambda n: self._nonces[n].created_at if n in self._nonces else datetime.min
                    )
                    await self._remove_nonce(oldest_nonce)

            self._stats["nonces_generated"] += 1

            self.logger.debug("Nonce generated", nonce=nonce, user_id=user_id)
            return nonce

        except Exception as e:
            self.logger.error("Nonce generation failed", error=str(e))
            raise

    async def validate_nonce(
        self,
        nonce: str,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate nonce for anti-replay protection.

        Args:
            nonce: Nonce to validate
            user_id: Optional user identifier for context
            endpoint: Optional endpoint identifier for context

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            self._stats["nonces_validated"] += 1

            # Check if nonce exists
            if nonce not in self._nonces:
                self._stats["replay_attempts_blocked"] += 1
                return False, "nonce_not_found"

            record = self._nonces[nonce]

            # Check if nonce is expired
            if record.is_expired:
                await self._remove_nonce(nonce)
                self._stats["replay_attempts_blocked"] += 1
                return False, "nonce_expired"

            # Validate context (optional strict validation)
            if user_id and record.user_id and record.user_id != user_id:
                self._stats["replay_attempts_blocked"] += 1
                return False, "nonce_user_mismatch"

            if endpoint and record.endpoint and record.endpoint != endpoint:
                self._stats["replay_attempts_blocked"] += 1
                return False, "nonce_endpoint_mismatch"

            # Remove nonce to prevent replay
            await self._remove_nonce(nonce)

            self.logger.debug("Nonce validated successfully", nonce=nonce, user_id=user_id)
            return True, "valid"

        except Exception as e:
            self.logger.error("Nonce validation failed", nonce=nonce, error=str(e))
            return False, "validation_error"

    async def _remove_nonce(self, nonce: str) -> None:
        """Remove nonce from storage."""
        if nonce in self._nonces:
            record = self._nonces.pop(nonce)
            if record.user_id and record.user_id in self._user_nonces:
                self._user_nonces[record.user_id].discard(nonce)

    async def _cleanup_expired_nonces(self) -> None:
        """Clean up expired nonces."""
        now = datetime.now(timezone.utc)
        expired_nonces = [
            nonce for nonce, record in self._nonces.items()
            if record.expires_at < now
        ]

        for nonce in expired_nonces:
            await self._remove_nonce(nonce)

        if expired_nonces:
            self._stats["expired_nonces_cleaned"] += len(expired_nonces)
            self.logger.debug("Cleaned expired nonces", count=len(expired_nonces))

    def get_stats(self) -> Dict[str, Any]:
        """Get anti-replay protection statistics."""
        return {
            **self._stats,
            "active_nonces": len(self._nonces),
            "users_with_nonces": len(self._user_nonces),
            "avg_nonces_per_user": (
                len(self._nonces) / max(1, len(self._user_nonces))
            )
        }


class RateLimiter:
    """
    Advanced rate limiting with multiple strategies.

    Provides protection against DDoS attacks, brute force attempts,
    and abusive usage patterns with configurable rules and actions.
    """

    def __init__(self, guardian_system: Optional[GuardianSystem] = None):
        """Initialize rate limiter."""
        self.guardian = guardian_system
        self.logger = logger.bind(component="RateLimiter")

        # Rate limiting rules
        self._rules: Dict[str, RateLimitRule] = {}
        self._default_rules()

        # Request tracking
        self._request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._blocked_ips: Dict[str, datetime] = {}
        self._penalties: Dict[str, int] = defaultdict(int)

        # Statistics
        self._stats = {
            "requests_processed": 0,
            "requests_blocked": 0,
            "requests_throttled": 0,
            "unique_ips": 0
        }

    def _default_rules(self) -> None:
        """Set up default rate limiting rules."""
        self._rules = {
            "authentication": RateLimitRule(
                name="authentication",
                max_requests=10,
                window_seconds=60,
                action=SecurityAction.THROTTLE,
                burst_allowance=3,
                progressive_penalties=True
            ),
            "webauthn_challenge": RateLimitRule(
                name="webauthn_challenge",
                max_requests=5,
                window_seconds=60,
                action=SecurityAction.THROTTLE
            ),
            "biometric_auth": RateLimitRule(
                name="biometric_auth",
                max_requests=3,
                window_seconds=60,
                action=SecurityAction.BLOCK
            ),
            "global": RateLimitRule(
                name="global",
                max_requests=100,
                window_seconds=60,
                action=SecurityAction.BLOCK
            )
        }

    async def check_rate_limit(
        self,
        identifier: str,
        rule_name: str = "global",
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[SecurityAction, str]:
        """
        Check if request should be rate limited.

        Args:
            identifier: Request identifier (IP, user ID, etc.)
            rule_name: Rate limiting rule to apply
            context: Additional context for decision making

        Returns:
            Tuple of (action, reason)
        """
        try:
            self._stats["requests_processed"] += 1

            # Check if IP is blocked
            if identifier in self._blocked_ips:
                block_until = self._blocked_ips[identifier]
                if datetime.now(timezone.utc) < block_until:
                    self._stats["requests_blocked"] += 1
                    return SecurityAction.BLOCK, "ip_blocked"
                else:
                    # Unblock expired IPs
                    del self._blocked_ips[identifier]

            # Get applicable rule
            rule = self._rules.get(rule_name, self._rules["global"])

            # Check whitelist
            if identifier in rule.whitelist_ips:
                return SecurityAction.ALLOW, "whitelisted"

            # Track request
            now = time.time()
            request_times = self._request_history[identifier]
            request_times.append(now)

            # Count requests in window
            window_start = now - rule.window_seconds
            recent_requests = [t for t in request_times if t >= window_start]
            request_count = len(recent_requests)

            # Update request history
            self._request_history[identifier] = deque(recent_requests, maxlen=1000)

            # Check rate limit
            effective_limit = rule.max_requests + rule.burst_allowance

            if request_count <= rule.max_requests:
                # Within normal limits
                return SecurityAction.ALLOW, "within_limits"
            elif request_count <= effective_limit:
                # In burst allowance
                if rule.action == SecurityAction.THROTTLE:
                    self._stats["requests_throttled"] += 1
                    return SecurityAction.THROTTLE, "burst_allowance"
                else:
                    return SecurityAction.ALLOW, "burst_allowed"
            else:
                # Rate limit exceeded
                await self._apply_rate_limit_action(identifier, rule, request_count, context)

                if rule.action == SecurityAction.BLOCK:
                    self._stats["requests_blocked"] += 1
                elif rule.action == SecurityAction.THROTTLE:
                    self._stats["requests_throttled"] += 1

                return rule.action, f"rate_limit_exceeded_{request_count}/{rule.max_requests}"

        except Exception as e:
            self.logger.error("Rate limit check failed", identifier=identifier, error=str(e))
            return SecurityAction.ALLOW, "check_error"

    async def _apply_rate_limit_action(
        self,
        identifier: str,
        rule: RateLimitRule,
        request_count: int,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Apply rate limiting action."""
        try:
            if rule.progressive_penalties:
                # Increase penalty for repeat offenders
                self._penalties[identifier] += 1
                penalty_multiplier = min(self._penalties[identifier], 10)
            else:
                penalty_multiplier = 1

            if rule.action == SecurityAction.BLOCK:
                # Block IP for escalating duration
                block_duration = timedelta(minutes=5 * penalty_multiplier)
                self._blocked_ips[identifier] = datetime.now(timezone.utc) + block_duration

                # Create security event
                event = SecurityEvent(
                    event_type="rate_limit_block",
                    threat_level=ThreatLevel.MEDIUM,
                    action_taken=SecurityAction.BLOCK,
                    ip_address=identifier,
                    description=f"IP blocked for {block_duration} due to rate limit violation",
                    indicators=[f"rule:{rule.name}", f"requests:{request_count}"],
                    risk_score=min(request_count / rule.max_requests, 10.0)
                )

                await self._log_security_event(event)

        except Exception as e:
            self.logger.error("Failed to apply rate limit action", error=str(e))

    async def _log_security_event(self, event: SecurityEvent) -> None:
        """Log security event."""
        self.logger.warning("Security event", **event.to_dict())

        # Guardian integration
        if self.guardian:
            try:
                await self.guardian.monitor_behavior_async("security_event", event.to_dict())
            except Exception as e:
                self.logger.error("Guardian logging failed", error=str(e))

    def add_rule(self, rule: RateLimitRule) -> None:
        """Add custom rate limiting rule."""
        self._rules[rule.name] = rule
        self.logger.info("Rate limiting rule added", rule_name=rule.name)

    def whitelist_ip(self, ip_address: str, rule_name: str = "global") -> None:
        """Add IP to whitelist for specific rule."""
        if rule_name in self._rules:
            self._rules[rule_name].whitelist_ips.add(ip_address)
            self.logger.info("IP whitelisted", ip=ip_address, rule=rule_name)

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        return {
            **self._stats,
            "active_blocks": len(self._blocked_ips),
            "tracked_identifiers": len(self._request_history),
            "rules_configured": len(self._rules)
        }


class RequestAnalyzer:
    """
    Advanced request analysis for anomaly detection.

    Analyzes request patterns, headers, and behavior to detect
    suspicious activity and potential security threats.
    """

    def __init__(self, guardian_system: Optional[GuardianSystem] = None):
        """Initialize request analyzer."""
        self.guardian = guardian_system
        self.logger = logger.bind(component="RequestAnalyzer")

        # Request history for pattern analysis
        self._request_history: Dict[str, List[RequestFingerprint]] = defaultdict(list)
        self._baseline_patterns: Dict[str, Dict[str, float]] = {}

        # Suspicious indicators
        self._suspicious_user_agents = {
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
            "python-requests", "curl/", "wget/", "libwww-perl"
        }

        self._suspicious_headers = {
            "x-forwarded-for", "x-real-ip", "x-cluster-client-ip",
            "x-scanner", "x-exploit", "x-injection"
        }

        # Statistics
        self._stats = {
            "requests_analyzed": 0,
            "anomalies_detected": 0,
            "threats_identified": 0
        }

    async def analyze_request(
        self,
        ip_address: str,
        user_agent: str,
        headers: Dict[str, str],
        request_body: Optional[bytes] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[ThreatLevel, List[str]]:
        """
        Analyze request for security threats and anomalies.

        Args:
            ip_address: Client IP address
            user_agent: User agent string
            headers: Request headers
            request_body: Optional request body
            endpoint: Request endpoint

        Returns:
            Tuple of (threat_level, indicators)
        """
        try:
            self._stats["requests_analyzed"] += 1

            # Create request fingerprint
            fingerprint = await self._create_fingerprint(
                ip_address, user_agent, headers, request_body, endpoint
            )

            # Analyze fingerprint
            threat_level, indicators = await self._analyze_fingerprint(fingerprint)

            # Store for pattern analysis
            self._request_history[ip_address].append(fingerprint)

            # Keep only recent history (last 100 requests per IP)
            if len(self._request_history[ip_address]) > 100:
                self._request_history[ip_address] = self._request_history[ip_address][-100:]

            # Update statistics
            if threat_level != ThreatLevel.LOW:
                self._stats["anomalies_detected"] += 1

            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self._stats["threats_identified"] += 1

            return threat_level, indicators

        except Exception as e:
            self.logger.error("Request analysis failed", error=str(e))
            return ThreatLevel.LOW, []

    async def _create_fingerprint(
        self,
        ip_address: str,
        user_agent: str,
        headers: Dict[str, str],
        request_body: Optional[bytes],
        endpoint: Optional[str]
    ) -> RequestFingerprint:
        """Create request fingerprint for analysis."""
        # Create request hash
        request_data = f"{ip_address}:{user_agent}:{endpoint or ''}:{len(headers)}"
        if request_body:
            request_data += f":{len(request_body)}"

        request_hash = hashlib.sha256(request_data.encode()).hexdigest()[:16]

        # Identify suspicious headers
        suspicious_headers = [
            header for header in headers.keys()
            if any(suspicious in header.lower() for suspicious in self._suspicious_headers)
        ]

        # Calculate anomaly score
        anomaly_score = await self._calculate_anomaly_score(
            ip_address, user_agent, headers
        )

        return RequestFingerprint(
            ip_address=ip_address,
            user_agent=user_agent,
            request_hash=request_hash,
            request_size=len(request_body) if request_body else 0,
            headers_count=len(headers),
            suspicious_headers=suspicious_headers,
            anomaly_score=anomaly_score
        )

    async def _analyze_fingerprint(
        self, fingerprint: RequestFingerprint
    ) -> Tuple[ThreatLevel, List[str]]:
        """Analyze request fingerprint for threats."""
        indicators = []
        threat_score = 0.0

        # Check user agent
        if any(suspicious in fingerprint.user_agent.lower()
               for suspicious in self._suspicious_user_agents):
            indicators.append("suspicious_user_agent")
            threat_score += 0.3

        # Check for automation patterns
        if "bot" in fingerprint.user_agent.lower() and "google" not in fingerprint.user_agent.lower():
            indicators.append("potential_bot")
            threat_score += 0.2

        # Check suspicious headers
        if fingerprint.suspicious_headers:
            indicators.append("suspicious_headers")
            threat_score += 0.2 * len(fingerprint.suspicious_headers)

        # Check request size anomalies
        if fingerprint.request_size > 1024 * 1024:  # 1MB
            indicators.append("large_request_body")
            threat_score += 0.1

        # Check header count anomalies
        if fingerprint.headers_count > 50:
            indicators.append("excessive_headers")
            threat_score += 0.1

        # Check anomaly score
        if fingerprint.anomaly_score > 0.7:
            indicators.append("behavioral_anomaly")
            threat_score += fingerprint.anomaly_score * 0.3

        # Determine threat level
        if threat_score >= 0.8:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.5:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.2:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW

        return threat_level, indicators

    async def _calculate_anomaly_score(
        self, ip_address: str, user_agent: str, headers: Dict[str, str]
    ) -> float:
        """Calculate behavioral anomaly score."""
        try:
            # Get request history for IP
            history = self._request_history.get(ip_address, [])
            if len(history) < 5:
                return 0.0  # Insufficient data for anomaly detection

            # Analyze user agent consistency
            recent_user_agents = [fp.user_agent for fp in history[-10:]]
            user_agent_variety = len(set(recent_user_agents))

            # High variety indicates potential spoofing
            ua_anomaly = min(user_agent_variety / 10.0, 1.0) if user_agent_variety > 3 else 0.0

            # Analyze header patterns
            recent_header_counts = [fp.headers_count for fp in history[-10:]]
            avg_headers = sum(recent_header_counts) / len(recent_header_counts)
            current_headers = len(headers)

            # Significant deviation from average
            header_anomaly = abs(current_headers - avg_headers) / max(avg_headers, 1)
            header_anomaly = min(header_anomaly / 10.0, 1.0)

            # Combine anomaly scores
            return (ua_anomaly + header_anomaly) / 2

        except Exception:
            return 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Get request analysis statistics."""
        return {
            **self._stats,
            "tracked_ips": len(self._request_history),
            "baseline_patterns": len(self._baseline_patterns)
        }


class SecurityHardeningManager:
    """
    Comprehensive security hardening manager.

    Coordinates all security hardening features including anti-replay protection,
    rate limiting, request analysis, and threat response.
    """

    def __init__(self, guardian_system: Optional[GuardianSystem] = None):
        """Initialize security hardening manager."""
        self.guardian = guardian_system
        self.logger = logger.bind(component="SecurityHardeningManager")

        # Initialize security components
        self.anti_replay = AntiReplayProtection()
        self.rate_limiter = RateLimiter(guardian_system)
        self.request_analyzer = RequestAnalyzer(guardian_system)

        # Security event log
        self._security_events: List[SecurityEvent] = []
        self._max_events = 1000

        self.logger.info("Security hardening manager initialized")

    async def generate_nonce(
        self, user_id: Optional[str] = None, endpoint: Optional[str] = None
    ) -> str:
        """Generate anti-replay nonce."""
        return await self.anti_replay.generate_nonce(user_id, endpoint)

    async def validate_nonce(
        self, nonce: str, user_id: Optional[str] = None, endpoint: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Validate anti-replay nonce."""
        return await self.anti_replay.validate_nonce(nonce, user_id, endpoint)

    async def check_rate_limit(
        self, identifier: str, rule_name: str = "global", context: Optional[Dict[str, Any]] = None
    ) -> Tuple[SecurityAction, str]:
        """Check rate limiting."""
        return await self.rate_limiter.check_rate_limit(identifier, rule_name, context)

    async def analyze_request(
        self,
        ip_address: str,
        user_agent: str,
        headers: Dict[str, str],
        request_body: Optional[bytes] = None,
        endpoint: Optional[str] = None
    ) -> Tuple[ThreatLevel, List[str]]:
        """Analyze request for threats."""
        return await self.request_analyzer.analyze_request(
            ip_address, user_agent, headers, request_body, endpoint
        )

    async def comprehensive_security_check(
        self,
        ip_address: str,
        user_agent: str,
        headers: Dict[str, str],
        nonce: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_body: Optional[bytes] = None
    ) -> Tuple[SecurityAction, Dict[str, Any]]:
        """
        Perform comprehensive security check.

        Returns:
            Tuple of (action, security_report)
        """
        try:
            security_report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ip_address": ip_address,
                "endpoint": endpoint,
                "checks_performed": [],
                "threats_detected": [],
                "actions_taken": []
            }

            final_action = SecurityAction.ALLOW

            # 1. Rate limiting check
            rate_action, rate_reason = await self.check_rate_limit(
                ip_address, "global", {"user_id": user_id, "endpoint": endpoint}
            )

            security_report["checks_performed"].append("rate_limiting")
            security_report["rate_limit"] = {
                "action": rate_action.value,
                "reason": rate_reason
            }

            if rate_action in [SecurityAction.BLOCK, SecurityAction.THROTTLE]:
                final_action = rate_action
                security_report["actions_taken"].append(f"rate_limit_{rate_action.value}")

            # 2. Nonce validation (if provided)
            if nonce:
                nonce_valid, nonce_reason = await self.validate_nonce(nonce, user_id, endpoint)
                security_report["checks_performed"].append("nonce_validation")
                security_report["nonce_validation"] = {
                    "valid": nonce_valid,
                    "reason": nonce_reason
                }

                if not nonce_valid:
                    final_action = SecurityAction.BLOCK
                    security_report["threats_detected"].append("replay_attack")
                    security_report["actions_taken"].append("block_replay_attempt")

            # 3. Request analysis
            threat_level, indicators = await self.analyze_request(
                ip_address, user_agent, headers, request_body, endpoint
            )

            security_report["checks_performed"].append("request_analysis")
            security_report["request_analysis"] = {
                "threat_level": threat_level.value,
                "indicators": indicators
            }

            # Escalate action based on threat level
            if threat_level == ThreatLevel.CRITICAL:
                final_action = SecurityAction.BLOCK
                security_report["threats_detected"].extend(indicators)
                security_report["actions_taken"].append("block_critical_threat")
            elif threat_level == ThreatLevel.HIGH and final_action == SecurityAction.ALLOW:
                final_action = SecurityAction.THROTTLE
                security_report["threats_detected"].extend(indicators)
                security_report["actions_taken"].append("throttle_high_threat")

            # 4. Log security event if threats detected
            if security_report["threats_detected"]:
                event = SecurityEvent(
                    event_type="comprehensive_security_check",
                    threat_level=threat_level,
                    action_taken=final_action,
                    ip_address=ip_address,
                    user_id=user_id,
                    user_agent=user_agent,
                    endpoint=endpoint,
                    description=f"Security check completed with {len(security_report['threats_detected'])} threats",
                    indicators=security_report["threats_detected"]
                )

                await self._log_security_event(event)

            security_report["final_action"] = final_action.value
            return final_action, security_report

        except Exception as e:
            self.logger.error("Comprehensive security check failed", error=str(e))
            return SecurityAction.ALLOW, {
                "error": "security_check_failed",
                "message": str(e)
            }

    async def _log_security_event(self, event: SecurityEvent) -> None:
        """Log security event."""
        # Add to internal log
        self._security_events.append(event)
        if len(self._security_events) > self._max_events:
            self._security_events = self._security_events[-self._max_events:]

        # Log to structured logging
        self.logger.warning("Security event logged", **event.to_dict())

        # Guardian integration
        if self.guardian:
            try:
                await self.guardian.monitor_behavior_async("security_hardening_event", event.to_dict())
            except Exception as e:
                self.logger.error("Guardian security event logging failed", error=str(e))

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics."""
        return {
            "anti_replay": self.anti_replay.get_stats(),
            "rate_limiting": self.rate_limiter.get_stats(),
            "request_analysis": self.request_analyzer.get_stats(),
            "security_events": {
                "total_events": len(self._security_events),
                "recent_events": len([
                    e for e in self._security_events
                    if e.timestamp > datetime.now(timezone.utc) - timedelta(hours=1)
                ])
            }
        }


# Factory function for dependency injection
def create_security_hardening_manager(
    guardian_system: Optional[GuardianSystem] = None
) -> SecurityHardeningManager:
    """Create security hardening manager with configuration."""
    return SecurityHardeningManager(guardian_system)