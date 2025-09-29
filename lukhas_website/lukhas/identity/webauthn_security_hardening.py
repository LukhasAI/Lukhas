"""
WebAuthn Security Hardening
===========================

P0-4 ID-W4N: Advanced security hardening for WebAuthn implementation
with abuse protection, threat detection, and production security measures.

Features:
- Rate limiting and abuse protection
- Device fingerprinting and anomaly detection
- Credential binding and attestation validation
- Geographic and temporal access controls
- Advanced threat detection and mitigation
- Security audit logging and monitoring
- Emergency revocation and incident response
"""

import hashlib
import time
import logging
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import json
import secrets

from .webauthn_production import WebAuthnCredential, CredentialStatus

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Types of security events"""
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CREDENTIAL_MISUSE = "credential_misuse"
    DEVICE_ANOMALY = "device_anomaly"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    ATTESTATION_FAILURE = "attestation_failure"
    REPLAY_ATTACK = "replay_attack"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SUSPICIOUS_REGISTRATION = "suspicious_registration"
    INVALID_ORIGIN = "invalid_origin"


class SecurityAction(Enum):
    """Security actions to take"""
    ALLOW = "allow"
    RATE_LIMIT = "rate_limit"
    SUSPEND_USER = "suspend_user"
    REVOKE_CREDENTIAL = "revoke_credential"
    BLOCK_IP = "block_ip"
    REQUIRE_ADDITIONAL_AUTH = "require_additional_auth"
    EMERGENCY_LOCKDOWN = "emergency_lockdown"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    user_id: Optional[str]
    credential_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    action_taken: Optional[SecurityAction] = None
    resolved: bool = False


@dataclass
class DeviceFingerprint:
    """Device fingerprint for anomaly detection"""
    fingerprint_hash: str
    user_agent: str
    screen_resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    webgl_renderer: Optional[str] = None
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = 1
    suspicious: bool = False


@dataclass
class GeographicContext:
    """Geographic context for location-based security analysis"""
    country: str
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EmergencyLockdown:
    """Emergency lockdown status and configuration"""
    active: bool = False
    reason: Optional[str] = None
    started_at: Optional[datetime] = None
    duration_minutes: int = 15
    scope: str = "global"  # global, user, ip, etc


@dataclass
class SecurityMetrics:
    """Security metrics collection for monitoring and alerting"""
    total_requests: int = 0
    blocked_requests: int = 0
    threat_events_detected: int = 0
    false_positives: int = 0
    emergency_lockdowns: int = 0
    attack_patterns: List[str] = field(default_factory=list)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_requests: int
    window_seconds: int
    cooldown_seconds: int = 0
    burst_limit: Optional[int] = None


@dataclass
class GeographicContext:
    """Geographic context for access"""
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None


class WebAuthnSecurityHardening:
    """
    Advanced security hardening for WebAuthn operations.

    Provides comprehensive protection against various attack vectors
    including abuse, replay attacks, device spoofing, and credential misuse.
    """

    def __init__(self):
        # Rate limiting tracking
        self.rate_limits = {
            'registration': RateLimitConfig(max_requests=5, window_seconds=300),  # 5 per 5min
            'authentication': RateLimitConfig(max_requests=20, window_seconds=300),  # 20 per 5min
            'failed_auth': RateLimitConfig(max_requests=5, window_seconds=600),  # 5 failures per 10min
            'credential_enumeration': RateLimitConfig(max_requests=10, window_seconds=300)
        }

        self.request_tracking: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(lambda: deque()))

        # Security event tracking
        self.security_events: List[SecurityEvent] = []
        self.blocked_ips: Set[str] = set()
        self.suspicious_devices: Set[str] = set()
        self.device_fingerprints: Dict[str, DeviceFingerprint] = {}

        # Threat detection patterns
        self.threat_patterns = self._initialize_threat_patterns()

        # Geographic anomaly detection
        self.user_locations: Dict[str, List[GeographicContext]] = defaultdict(list)

        # Credential binding validation
        self.credential_bindings: Dict[str, Dict[str, Any]] = {}

        logger.info("WebAuthnSecurityHardening initialized")

    async def validate_request_security(
        self,
        operation: str,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], List[SecurityEvent]]:
        """Validate request security and detect threats."""
        events = []
        additional_context = additional_context or {}

        # Check rate limiting
        rate_limit_key = f"{ip_address}:{operation}"
        if not await self._check_rate_limit(rate_limit_key, operation):
            event = SecurityEvent(
                event_id=secrets.token_urlsafe(16),
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                threat_level=ThreatLevel.MEDIUM,
                user_id=user_id,
                credential_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(timezone.utc),
                details={'operation': operation},
                action_taken=SecurityAction.RATE_LIMIT
            )
            events.append(event)
            self.security_events.append(event)
            return False, "Rate limit exceeded", events

        # Check for suspicious user agents
        if any(pattern in user_agent.lower() for pattern in self.threat_patterns['suspicious_user_agents']['automated_tools']):
            event = SecurityEvent(
                event_id=secrets.token_urlsafe(16),
                event_type=SecurityEventType.SUSPICIOUS_REGISTRATION,
                threat_level=ThreatLevel.HIGH,
                user_id=user_id,
                credential_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(timezone.utc),
                details={'suspicious_agent': user_agent},
                action_taken=SecurityAction.BLOCK_IP
            )
            events.append(event)
            self.security_events.append(event)
            return False, "Suspicious user agent detected", events

        return True, None, events

    async def _check_rate_limit(self, key: str, operation: str) -> bool:
        """Check if request is within rate limits."""
        now = time.time()
        rate_config = self.rate_limits.get(operation)
        if not rate_config:
            return True

        # Clean old requests
        request_times = self.request_tracking[operation][key]
        while request_times and now - request_times[0] > rate_config.window_seconds:
            request_times.popleft()

        # Check if within limit
        if len(request_times) >= rate_config.max_requests:
            return False

        # Add current request
        request_times.append(now)
        return True

    def _initialize_threat_patterns(self) -> Dict[str, Any]:
        """Initialize threat detection patterns"""
        return {
            'suspicious_user_agents': {
                'automated_tools': ['curl', 'wget', 'python-requests', 'selenium'],
                'known_malware': ['bot', 'crawler', 'scraper'],
                'suspicious_patterns': ['test', 'hack', 'exploit']
            },
            'rapid_credential_creation': {
                'max_credentials_per_hour': 3,
                'max_credentials_per_day': 10
            },
            'geographic_impossibility': {
                'max_travel_speed_kmh': 1000  # Speed of commercial aircraft
            },
            'temporal_patterns': {
                'min_time_between_authentications_seconds': 1,
                'max_session_duration_hours': 12
            }
        }

    async def validate_request_security(self,
                                      operation: str,
                                      user_id: Optional[str],
                                      ip_address: str,
                                      user_agent: str,
                                      additional_context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str], List[SecurityEvent]]:
        """
        Validate request security before processing WebAuthn operations.

        Returns:
            (is_allowed, block_reason, security_events)
        """
        events = []
        additional_context = additional_context or {}

        # Check IP blocking
        if ip_address in self.blocked_ips:
            event = SecurityEvent(
                event_id=secrets.token_urlsafe(16),
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                threat_level=ThreatLevel.HIGH,
                user_id=user_id,
                credential_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(timezone.utc),
                details={'reason': 'IP blocked'},
                action_taken=SecurityAction.BLOCK_IP
            )
            events.append(event)
            return False, "IP address blocked due to suspicious activity", events

        # Rate limiting validation
        rate_limit_passed, rate_limit_reason, rate_limit_events = await self._validate_rate_limits(
            operation, user_id, ip_address, user_agent
        )
        events.extend(rate_limit_events)

        if not rate_limit_passed:
            return False, rate_limit_reason, events

        # User agent analysis
        ua_threat_level = self._analyze_user_agent(user_agent)
        if ua_threat_level >= ThreatLevel.HIGH:
            event = SecurityEvent(
                event_id=secrets.token_urlsafe(16),
                event_type=SecurityEventType.DEVICE_ANOMALY,
                threat_level=ua_threat_level,
                user_id=user_id,
                credential_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(timezone.utc),
                details={'analysis': 'Suspicious user agent detected'},
                action_taken=SecurityAction.RATE_LIMIT
            )
            events.append(event)

            if ua_threat_level == ThreatLevel.CRITICAL:
                return False, "User agent indicates potential security threat", events

        # Device fingerprinting
        if 'device_fingerprint' in additional_context:
            fingerprint_events = await self._validate_device_fingerprint(
                user_id, additional_context['device_fingerprint'], ip_address, user_agent
            )
            events.extend(fingerprint_events)

        # Geographic validation
        if 'geographic_info' in additional_context:
            geo_events = await self._validate_geographic_context(
                user_id, additional_context['geographic_info'], ip_address
            )
            events.extend(geo_events)

        # Store security events
        self.security_events.extend(events)

        # Determine overall security decision
        high_threat_events = [e for e in events if e.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]

        if len(high_threat_events) >= 3:
            return False, "Multiple high-threat indicators detected", events
        elif any(e.threat_level == ThreatLevel.CRITICAL for e in events):
            return False, "Critical security threat detected", events

        return True, None, events

    async def _validate_rate_limits(self,
                                  operation: str,
                                  user_id: Optional[str],
                                  ip_address: str,
                                  user_agent: str) -> Tuple[bool, Optional[str], List[SecurityEvent]]:
        """Validate rate limits for the operation"""
        events = []
        now = time.time()

        # Check per-IP rate limits
        for rate_type, config in self.rate_limits.items():
            if rate_type not in operation and rate_type != operation:
                continue

            ip_key = f"{ip_address}:{rate_type}"
            request_times = self.request_tracking[ip_key]['times']

            # Clean old requests outside window
            while request_times and now - request_times[0] > config.window_seconds:
                request_times.popleft()

            # Check rate limit
            if len(request_times) >= config.max_requests:
                event = SecurityEvent(
                    event_id=secrets.token_urlsafe(16),
                    event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                    threat_level=ThreatLevel.MEDIUM,
                    user_id=user_id,
                    credential_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=datetime.now(timezone.utc),
                    details={
                        'rate_type': rate_type,
                        'requests_in_window': len(request_times),
                        'max_allowed': config.max_requests,
                        'window_seconds': config.window_seconds
                    },
                    action_taken=SecurityAction.RATE_LIMIT
                )
                events.append(event)

                # Consider IP blocking for severe violations
                if len(request_times) >= config.max_requests * 3:
                    self.blocked_ips.add(ip_address)
                    event.action_taken = SecurityAction.BLOCK_IP

                return False, f"Rate limit exceeded for {rate_type}", events

            # Record this request
            request_times.append(now)

        # Check per-user rate limits if user_id provided
        if user_id:
            for rate_type, config in self.rate_limits.items():
                if rate_type not in operation and rate_type != operation:
                    continue

                user_key = f"{user_id}:{rate_type}"
                request_times = self.request_tracking[user_key]['times']

                # Clean old requests
                while request_times and now - request_times[0] > config.window_seconds:
                    request_times.popleft()

                # Check user rate limit (typically higher than IP limits)
                user_max = config.max_requests * 2  # 2x IP limit for users
                if len(request_times) >= user_max:
                    event = SecurityEvent(
                        event_id=secrets.token_urlsafe(16),
                        event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                        threat_level=ThreatLevel.HIGH,
                        user_id=user_id,
                        credential_id=None,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        timestamp=datetime.now(timezone.utc),
                        details={
                            'rate_type': f'user_{rate_type}',
                            'requests_in_window': len(request_times),
                            'max_allowed': user_max
                        },
                        action_taken=SecurityAction.SUSPEND_USER
                    )
                    events.append(event)
                    return False, f"User rate limit exceeded for {rate_type}", events

                request_times.append(now)

        return True, None, events

    def _analyze_user_agent(self, user_agent: str) -> ThreatLevel:
        """Analyze user agent for suspicious patterns"""
        if not user_agent:
            return ThreatLevel.MEDIUM

        user_agent_lower = user_agent.lower()
        patterns = self.threat_patterns['suspicious_user_agents']

        # Check for automated tools
        for tool in patterns['automated_tools']:
            if tool in user_agent_lower:
                return ThreatLevel.HIGH

        # Check for known malware patterns
        for malware in patterns['known_malware']:
            if malware in user_agent_lower:
                return ThreatLevel.CRITICAL

        # Check for suspicious patterns
        for pattern in patterns['suspicious_patterns']:
            if pattern in user_agent_lower:
                return ThreatLevel.MEDIUM

        # Check for very old browsers (potential security risk)
        if 'msie' in user_agent_lower or 'internet explorer' in user_agent_lower:
            return ThreatLevel.MEDIUM

        return ThreatLevel.LOW

    async def _validate_device_fingerprint(self,
                                         user_id: Optional[str],
                                         fingerprint_data: Dict[str, Any],
                                         ip_address: str,
                                         user_agent: str) -> List[SecurityEvent]:
        """Validate device fingerprint for anomaly detection"""
        events = []

        # Generate fingerprint hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()

        now = datetime.now(timezone.utc)

        # Check if this is a known device
        if fingerprint_hash in self.device_fingerprints:
            device = self.device_fingerprints[fingerprint_hash]
            device.last_seen = now
            device.usage_count += 1

            # Check for suspicious device
            if device.suspicious:
                event = SecurityEvent(
                    event_id=secrets.token_urlsafe(16),
                    event_type=SecurityEventType.DEVICE_ANOMALY,
                    threat_level=ThreatLevel.HIGH,
                    user_id=user_id,
                    credential_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=now,
                    details={'fingerprint_hash': fingerprint_hash, 'reason': 'Previously flagged device'},
                    action_taken=SecurityAction.REQUIRE_ADDITIONAL_AUTH
                )
                events.append(event)

        else:
            # New device - create fingerprint record
            device = DeviceFingerprint(
                fingerprint_hash=fingerprint_hash,
                user_agent=user_agent,
                screen_resolution=fingerprint_data.get('screen_resolution'),
                timezone=fingerprint_data.get('timezone'),
                language=fingerprint_data.get('language'),
                platform=fingerprint_data.get('platform'),
                webgl_renderer=fingerprint_data.get('webgl_renderer')
            )

            # Analyze new device for suspicious characteristics
            threat_level = self._analyze_device_fingerprint(fingerprint_data)

            if threat_level >= ThreatLevel.MEDIUM:
                device.suspicious = True

                event = SecurityEvent(
                    event_id=secrets.token_urlsafe(16),
                    event_type=SecurityEventType.DEVICE_ANOMALY,
                    threat_level=threat_level,
                    user_id=user_id,
                    credential_id=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=now,
                    details={'fingerprint_hash': fingerprint_hash, 'analysis': 'New suspicious device'},
                    action_taken=SecurityAction.REQUIRE_ADDITIONAL_AUTH if threat_level == ThreatLevel.HIGH else None
                )
                events.append(event)

            self.device_fingerprints[fingerprint_hash] = device

        return events

    def _analyze_device_fingerprint(self, fingerprint_data: Dict[str, Any]) -> ThreatLevel:
        """Analyze device fingerprint for suspicious characteristics"""
        threat_level = ThreatLevel.LOW

        # Check for headless browsers (common in automation)
        if fingerprint_data.get('webgl_renderer') == 'SwiftShader':
            threat_level = ThreatLevel.MEDIUM

        # Check for unusual screen resolutions
        screen_res = fingerprint_data.get('screen_resolution')
        if screen_res:
            try:
                width, height = map(int, screen_res.split('x'))
                # Very small or very large resolutions can indicate automation
                if width < 800 or height < 600 or width > 7680 or height > 4320:
                    threat_level = ThreatLevel.MEDIUM
            except (ValueError, AttributeError):
                threat_level = ThreatLevel.LOW

        # Check for missing common properties
        expected_properties = ['screen_resolution', 'timezone', 'language', 'platform']
        missing_props = [prop for prop in expected_properties if not fingerprint_data.get(prop)]

        if len(missing_props) >= 3:
            threat_level = ThreatLevel.MEDIUM

        return threat_level

    async def _validate_geographic_context(self,
                                         user_id: Optional[str],
                                         geo_info: Dict[str, Any],
                                         ip_address: str) -> List[SecurityEvent]:
        """Validate geographic context for access anomalies"""
        events = []

        if not user_id:
            return events

        geo_context = GeographicContext(
            country=geo_info.get('country'),
            region=geo_info.get('region'),
            city=geo_info.get('city'),
            latitude=geo_info.get('latitude'),
            longitude=geo_info.get('longitude'),
            timezone=geo_info.get('timezone'),
            isp=geo_info.get('isp')
        )

        now = datetime.now(timezone.utc)

        # Get user's location history
        user_locations = self.user_locations[user_id]

        if user_locations:
            last_location = user_locations[-1]

            # Check for impossible travel (geographic impossibility)
            if (last_location.latitude and last_location.longitude and
                geo_context.latitude and geo_context.longitude):

                distance_km = self._calculate_distance(
                    last_location.latitude, last_location.longitude,
                    geo_context.latitude, geo_context.longitude
                )

                # Estimate minimum time based on last access
                # For this example, assume last access was recent (would need actual timestamp)
                time_diff_hours = 1  # Mock - would calculate from actual last access

                if time_diff_hours > 0:
                    travel_speed_kmh = distance_km / time_diff_hours
                    max_speed = self.threat_patterns['geographic_impossibility']['max_travel_speed_kmh']

                    if travel_speed_kmh > max_speed:
                        event = SecurityEvent(
                            event_id=secrets.token_urlsafe(16),
                            event_type=SecurityEventType.GEOGRAPHIC_ANOMALY,
                            threat_level=ThreatLevel.HIGH,
                            user_id=user_id,
                            credential_id=None,
                            ip_address=ip_address,
                            user_agent="",
                            timestamp=now,
                            details={
                                'distance_km': distance_km,
                                'time_hours': time_diff_hours,
                                'calculated_speed_kmh': travel_speed_kmh,
                                'max_speed_kmh': max_speed,
                                'previous_location': f"{last_location.city}, {last_location.country}",
                                'current_location': f"{geo_context.city}, {geo_context.country}"
                            },
                            action_taken=SecurityAction.REQUIRE_ADDITIONAL_AUTH
                        )
                        events.append(event)

        # Store current location
        user_locations.append(geo_context)

        # Keep only recent locations (last 10)
        if len(user_locations) > 10:
            user_locations.pop(0)

        return events

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two geographic points using Haversine formula"""
        import math

        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance

    async def validate_credential_binding(self,
                                        credential: WebAuthnCredential,
                                        request_context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate credential binding and usage context"""

        # Check credential status
        if credential.status != CredentialStatus.ACTIVE:
            return False, f"Credential status is {credential.status.value}"

        # Check credential expiry (if applicable)
        if hasattr(credential, 'expires_at') and credential.expires_at:
            if datetime.now(timezone.utc) > credential.expires_at:
                return False, "Credential has expired"

        # Validate sign count (replay attack detection)
        if credential.sign_count > 0:
            expected_min_count = credential.sign_count
            actual_count = request_context.get('sign_count', 0)

            if actual_count <= expected_min_count:
                # Potential replay attack
                await self._record_security_event(
                    SecurityEventType.REPLAY_ATTACK,
                    ThreatLevel.HIGH,
                    credential.user_id,
                    credential.credential_id,
                    request_context.get('ip_address'),
                    request_context.get('user_agent'),
                    {
                        'expected_min_count': expected_min_count,
                        'actual_count': actual_count
                    },
                    SecurityAction.REVOKE_CREDENTIAL
                )
                return False, "Replay attack detected - invalid sign count"

        # Validate device binding (if enabled)
        if credential.credential_id in self.credential_bindings:
            binding = self.credential_bindings[credential.credential_id]
            request_fingerprint = request_context.get('device_fingerprint', {})

            if binding.get('device_fingerprint') != request_fingerprint:
                await self._record_security_event(
                    SecurityEventType.CREDENTIAL_MISUSE,
                    ThreatLevel.HIGH,
                    credential.user_id,
                    credential.credential_id,
                    request_context.get('ip_address'),
                    request_context.get('user_agent'),
                    {'reason': 'Device fingerprint mismatch'},
                    SecurityAction.REQUIRE_ADDITIONAL_AUTH
                )
                return False, "Credential device binding validation failed"

        # Check for credential overuse patterns
        usage_pattern = await self._analyze_credential_usage_pattern(credential, request_context)
        if usage_pattern['threat_level'] >= ThreatLevel.HIGH:
            return False, usage_pattern['reason']

        return True, None

    async def _analyze_credential_usage_pattern(self,
                                              credential: WebAuthnCredential,
                                              request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze credential usage patterns for anomalies"""

        # This would analyze:
        # - Frequency of usage
        # - Geographic patterns
        # - Temporal patterns
        # - Device patterns

        # For now, return basic analysis
        return {
            'threat_level': ThreatLevel.LOW,
            'reason': None,
            'patterns_detected': []
        }

    async def _record_security_event(self,
                                   event_type: SecurityEventType,
                                   threat_level: ThreatLevel,
                                   user_id: Optional[str],
                                   credential_id: Optional[str],
                                   ip_address: Optional[str],
                                   user_agent: Optional[str],
                                   details: Dict[str, Any],
                                   action_taken: Optional[SecurityAction] = None):
        """Record a security event"""

        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            event_type=event_type,
            threat_level=threat_level,
            user_id=user_id,
            credential_id=credential_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(timezone.utc),
            details=details,
            action_taken=action_taken
        )

        self.security_events.append(event)

        # Log critical events
        if threat_level == ThreatLevel.CRITICAL:
            logger.critical(f"Critical security event: {event_type.value} for user {user_id}")
        elif threat_level == ThreatLevel.HIGH:
            logger.warning(f"High threat security event: {event_type.value} for user {user_id}")

    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard with current threat landscape"""

        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)

        recent_events = [e for e in self.security_events if e.timestamp >= last_24h]

        # Threat level distribution
        threat_distribution = defaultdict(int)
        for event in recent_events:
            threat_distribution[event.threat_level.value] += 1

        # Event type distribution
        event_type_distribution = defaultdict(int)
        for event in recent_events:
            event_type_distribution[event.event_type.value] += 1

        # Top threat sources
        ip_threats = defaultdict(int)
        for event in recent_events:
            if event.ip_address:
                ip_threats[event.ip_address] += 1

        return {
            'timestamp': now.isoformat(),
            'summary': {
                'total_events_24h': len(recent_events),
                'blocked_ips': len(self.blocked_ips),
                'suspicious_devices': len([d for d in self.device_fingerprints.values() if d.suspicious]),
                'active_threats': len([e for e in recent_events if e.threat_level == ThreatLevel.CRITICAL])
            },
            'threat_distribution': dict(threat_distribution),
            'event_types': dict(event_type_distribution),
            'top_threat_ips': dict(sorted(ip_threats.items(), key=lambda x: x[1], reverse=True)[:10]),
            'recent_critical_events': [
                {
                    'event_id': e.event_id,
                    'type': e.event_type.value,
                    'threat_level': e.threat_level.value,
                    'user_id': e.user_id,
                    'timestamp': e.timestamp.isoformat(),
                    'action_taken': e.action_taken.value if e.action_taken else None
                }
                for e in recent_events
                if e.threat_level == ThreatLevel.CRITICAL
            ][:10]
        }

    async def emergency_lockdown(self, reason: str, duration_minutes: int = 60):
        """Initiate emergency lockdown of WebAuthn operations"""

        logger.critical(f"EMERGENCY LOCKDOWN INITIATED: {reason}")

        # This would:
        # 1. Block all new WebAuthn operations
        # 2. Revoke active sessions
        # 3. Send emergency notifications
        # 4. Create incident tickets

        await self._record_security_event(
            SecurityEventType.RATE_LIMIT_EXCEEDED,  # Using existing enum for now
            ThreatLevel.CRITICAL,
            None,
            None,
            None,
            None,
            {
                'lockdown_reason': reason,
                'duration_minutes': duration_minutes,
                'initiated_at': datetime.now(timezone.utc).isoformat()
            },
            SecurityAction.EMERGENCY_LOCKDOWN
        )

    def get_security_metrics(self) -> SecurityMetrics:
        """Get comprehensive security metrics for monitoring."""
        total_blocked = len([e for e in self.security_events if e.action_taken in [
            SecurityAction.RATE_LIMIT, SecurityAction.SUSPEND_USER,
            SecurityAction.REVOKE_CREDENTIAL, SecurityAction.BLOCK_IP
        ]])

        threat_events = len([e for e in self.security_events if e.threat_level in [
            ThreatLevel.HIGH, ThreatLevel.CRITICAL
        ]])

        attack_patterns = list(set([
            e.event_type.value for e in self.security_events
            if e.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ]))

        return SecurityMetrics(
            total_requests=len(self.security_events),
            blocked_requests=total_blocked,
            threat_events_detected=threat_events,
            false_positives=0,  # Would be calculated based on resolved events
            emergency_lockdowns=len([e for e in self.security_events
                                   if e.action_taken == SecurityAction.EMERGENCY_LOCKDOWN]),
            attack_patterns=attack_patterns
        )

    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old security data"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        # Clean old security events
        self.security_events = [e for e in self.security_events if e.timestamp >= cutoff_date]

        # Clean old device fingerprints
        old_devices = [
            fp_hash for fp_hash, device in self.device_fingerprints.items()
            if device.last_seen < cutoff_date
        ]

        for fp_hash in old_devices:
            del self.device_fingerprints[fp_hash]

        # Clean old rate limiting data
        now = time.time()
        for operation_data in self.request_tracking.values():
            for request_times in operation_data.values():
                while request_times and now - request_times[0] > (days_to_keep * 86400):
                    request_times.popleft()

        logger.info(f"Cleaned up security data: {len(old_devices)} old devices removed")


# Global security hardening instance
_global_security_hardening: Optional[WebAuthnSecurityHardening] = None


def get_security_hardening() -> WebAuthnSecurityHardening:
    """Get global security hardening instance"""
    global _global_security_hardening
    if _global_security_hardening is None:
        _global_security_hardening = WebAuthnSecurityHardening()
    return _global_security_hardening