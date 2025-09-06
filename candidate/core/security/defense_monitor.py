"""
Defense-in-Depth Security Monitoring for LUKHAS AI
==================================================
Comprehensive security monitoring system implementing multiple layers of defense:
- Intrusion Detection System (IDS)
- Anomaly Detection for AI Operations
- Security Event Correlation
- Automated Threat Response
- Compliance Monitoring
"""

import asyncio
import hashlib
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

try:
    from .secure_logging import get_security_logger

    logger = get_security_logger(__name__)
    LOGGING_AVAILABLE = True
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    LOGGING_AVAILABLE = False


class ThreatLevel(Enum):
    """Security threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Types of security events"""

    AUTHENTICATION_FAILURE = "auth_failure"
    MULTIPLE_FAILED_LOGINS = "multiple_failed_logins"
    SUSPICIOUS_API_USAGE = "suspicious_api_usage"
    UNUSUAL_DATA_ACCESS = "unusual_data_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALICIOUS_INPUT_DETECTED = "malicious_input"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access"
    DATA_EXFILTRATION_ATTEMPT = "data_exfiltration"
    CONFIGURATION_CHANGE = "config_change"
    SECURITY_POLICY_VIOLATION = "policy_violation"


@dataclass
class SecurityEvent:
    """Security event data structure"""

    event_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)
    raw_data: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "threat_level": self.threat_level.value,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.source_ip,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "details": self.details,
            "raw_data": self.raw_data,
        }


@dataclass
class ThreatDetectionRule:
    """Rule for detecting security threats"""

    rule_id: str
    name: str
    description: str
    event_types: list[SecurityEventType]
    conditions: dict[str, Any]
    threshold: int
    time_window_minutes: int
    threat_level: ThreatLevel
    auto_response: bool = False
    enabled: bool = True


class DefenseMonitor:
    """
    Comprehensive defense-in-depth monitoring system
    Implements multiple security layers and automated threat detection
    """

    def __init__(self):
        """Initialize defense monitoring system"""

        # Event storage
        self.events: deque = deque(maxlen=10000)  # Ring buffer for events
        self.event_index: dict[str, list[SecurityEvent]] = defaultdict(list)

        # Threat detection rules
        self.detection_rules: dict[str, ThreatDetectionRule] = {}
        self._initialize_default_rules()

        # Monitoring state
        self.failed_logins: dict[str, list[datetime]] = defaultdict(list)
        self.api_usage_stats: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.suspicious_ips: set[str] = set()
        self.blocked_ips: set[str] = set()

        # Response handlers
        self.response_handlers: dict[SecurityEventType, list[Callable]] = defaultdict(list)

        # Metrics
        self.metrics = {
            "events_processed": 0,
            "threats_detected": 0,
            "auto_responses_triggered": 0,
            "false_positives": 0,
            "last_scan": None,
        }

        # Configuration
        self.max_failed_logins = 5
        self.login_window_minutes = 15
        self.api_rate_limit = 1000
        self.api_window_minutes = 60
        self.suspicious_ip_threshold = 10

        logger.info("Defense-in-depth monitoring system initialized")

    async def record_event(
        self,
        event_type: SecurityEventType,
        details: dict[str, Any],
        source_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        threat_level: Optional[ThreatLevel] = None,
    ) -> str:
        """Record security event and analyze for threats"""

        # Generate event ID
        event_id = self._generate_event_id()

        # Create event
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            threat_level=threat_level or ThreatLevel.LOW,
            timestamp=datetime.now(timezone.utc),
            source_ip=source_ip,
            user_id=user_id,
            endpoint=endpoint,
            details=details,
        )

        # Store event
        self.events.append(event)
        self.event_index[event_type.value].append(event)
        self.metrics["events_processed"] += 1

        # Analyze event for threats
        await self._analyze_event(event)

        # Log security event
        logger.info(
            f"Security event recorded: {event_type.value}",
            extra={
                "event_id": event_id,
                "threat_level": threat_level.value if threat_level else "low",
                "source_ip": source_ip,
                "user_id": user_id,
            },
        )

        return event_id

    async def _analyze_event(self, event: SecurityEvent):
        """Analyze event against detection rules"""

        for rule in self.detection_rules.values():
            if not rule.enabled:
                continue

            if event.event_type in rule.event_types and await self._evaluate_rule(rule, event):
                await self._trigger_threat_response(rule, event)

    async def _evaluate_rule(self, rule: ThreatDetectionRule, event: SecurityEvent) -> bool:
        """Evaluate if rule conditions are met"""

        # Get recent events of the same type
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=rule.time_window_minutes)
        recent_events = [e for e in self.event_index[event.event_type.value] if e.timestamp > cutoff_time]

        # Check threshold
        if len(recent_events) < rule.threshold:
            return False

        # Apply specific rule conditions
        if rule.rule_id == "multiple_failed_logins":
            return await self._check_failed_login_rule(recent_events, event)
        elif rule.rule_id == "suspicious_api_usage":
            return await self._check_api_usage_rule(recent_events, event)
        elif rule.rule_id == "unusual_data_access":
            return await self._check_data_access_rule(recent_events, event)
        elif rule.rule_id == "privilege_escalation":
            return await self._check_privilege_escalation_rule(recent_events, event)

        # Default threshold-based evaluation
        return True

    async def _trigger_threat_response(self, rule: ThreatDetectionRule, triggering_event: SecurityEvent):
        """Trigger automated threat response"""

        self.metrics["threats_detected"] += 1

        # Create threat alert
        threat_event = SecurityEvent(
            event_id=self._generate_event_id(),
            event_type=SecurityEventType.SECURITY_POLICY_VIOLATION,
            threat_level=rule.threat_level,
            timestamp=datetime.now(timezone.utc),
            source_ip=triggering_event.source_ip,
            user_id=triggering_event.user_id,
            details={
                "rule_triggered": rule.rule_id,
                "rule_name": rule.name,
                "triggering_event": triggering_event.event_id,
                "auto_response": rule.auto_response,
            },
        )

        self.events.append(threat_event)

        # Log threat detection
        logger.warning(
            f"THREAT DETECTED: {rule.name}",
            extra={
                "rule_id": rule.rule_id,
                "threat_level": rule.threat_level.value,
                "auto_response": rule.auto_response,
                "triggering_event": triggering_event.event_id,
            },
        )

        # Execute automated response if enabled
        if rule.auto_response:
            await self._execute_auto_response(rule, triggering_event)

        # Notify response handlers
        for handler in self.response_handlers.get(triggering_event.event_type, []):
            try:
                await handler(threat_event, triggering_event)
            except Exception as e:
                logger.error(f"Response handler failed: {e}")

    async def _execute_auto_response(self, rule: ThreatDetectionRule, event: SecurityEvent):
        """Execute automated response to threat"""

        self.metrics["auto_responses_triggered"] += 1

        if rule.rule_id == "multiple_failed_logins" and event.source_ip:
            # Block IP temporarily
            await self._block_ip_temporarily(event.source_ip, minutes=30)

        elif rule.rule_id == "suspicious_api_usage":
            # Rate limit user/IP
            if event.user_id:
                await self._rate_limit_user(event.user_id, minutes=15)
            if event.source_ip:
                await self._rate_limit_ip(event.source_ip, minutes=10)

        elif rule.rule_id == "data_exfiltration_attempt":
            # Emergency response - block all access
            if event.user_id:
                await self._emergency_block_user(event.user_id)

        logger.info(f"Automated response executed for rule: {rule.rule_id}")

    async def _block_ip_temporarily(self, ip_address: str, minutes: int):
        """Temporarily block IP address"""
        self.blocked_ips.add(ip_address)

        # Schedule unblock (in production, use proper task scheduler)
        logger.warning(f"IP blocked temporarily: {ip_address} for {minutes} minutes")

        # Record blocking event
        await self.record_event(
            SecurityEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
            {"action": "ip_blocked", "ip": ip_address, "duration_minutes": minutes},
            source_ip=ip_address,
        )

    async def _rate_limit_user(self, user_id: str, minutes: int):
        """Apply rate limiting to user"""
        logger.warning(f"Rate limiting applied to user: {user_id} for {minutes} minutes")

        # In production, integrate with rate limiting system
        await self.record_event(
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            {"action": "user_rate_limited", "user_id": user_id, "duration_minutes": minutes},
            user_id=user_id,
        )

    async def _rate_limit_ip(self, ip_address: str, minutes: int):
        """Apply rate limiting to IP"""
        logger.warning(f"Rate limiting applied to IP: {ip_address} for {minutes} minutes")

        await self.record_event(
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            {"action": "ip_rate_limited", "ip": ip_address, "duration_minutes": minutes},
            source_ip=ip_address,
        )

    async def _emergency_block_user(self, user_id: str):
        """Emergency block user account"""
        logger.critical(f"EMERGENCY: User account blocked: {user_id}")

        await self.record_event(
            SecurityEventType.DATA_EXFILTRATION_ATTEMPT,
            {"action": "emergency_user_blocked", "user_id": user_id},
            user_id=user_id,
            threat_level=ThreatLevel.CRITICAL,
        )

    # Rule condition checkers

    async def _check_failed_login_rule(self, events: list[SecurityEvent], current_event: SecurityEvent) -> bool:
        """Check multiple failed logins from same IP/user"""
        if not current_event.source_ip and not current_event.user_id:
            return False

        # Count failures from same source
        same_source_failures = [
            e for e in events if (e.source_ip == current_event.source_ip or e.user_id == current_event.user_id)
        ]

        return len(same_source_failures) >= self.max_failed_logins

    async def _check_api_usage_rule(self, events: list[SecurityEvent], current_event: SecurityEvent) -> bool:
        """Check for suspicious API usage patterns"""
        if not current_event.source_ip and not current_event.user_id:
            return False

        # Count API calls from same source
        api_calls = len(events)

        # Check for rapid-fire requests (potential bot)
        if api_calls >= self.api_rate_limit:
            return True

        # Check for unusual endpoint patterns
        endpoints = [e.endpoint for e in events if e.endpoint]
        unique_endpoints = len(set(endpoints))

        # Suspicious if hitting many different endpoints rapidly
        return bool(unique_endpoints > 20 and api_calls > 100)

    async def _check_data_access_rule(self, events: list[SecurityEvent], current_event: SecurityEvent) -> bool:
        """Check for unusual data access patterns"""
        # Look for access to sensitive data outside normal hours
        current_hour = current_event.timestamp.hour

        # Define business hours (9 AM to 6 PM)
        if current_hour < 9 or current_hour > 18:
            sensitive_endpoints = ["/api/credentials", "/api/admin", "/api/users"]
            if current_event.endpoint in sensitive_endpoints:
                return True

        return False

    async def _check_privilege_escalation_rule(self, events: list[SecurityEvent], current_event: SecurityEvent) -> bool:
        """Check for privilege escalation attempts"""
        if not current_event.user_id:
            return False

        # Look for admin endpoint access by non-admin users
        admin_endpoints = ["/api/admin", "/api/system", "/api/config"]
        if current_event.endpoint in admin_endpoints:
            # In production, check user roles
            return True  # Simplified check

        return False

    def _initialize_default_rules(self):
        """Initialize default threat detection rules"""

        self.detection_rules["multiple_failed_logins"] = ThreatDetectionRule(
            rule_id="multiple_failed_logins",
            name="Multiple Failed Login Attempts",
            description="Detects multiple failed login attempts from same IP or user",
            event_types=[SecurityEventType.AUTHENTICATION_FAILURE],
            conditions={"threshold": 5, "time_window": 15},
            threshold=5,
            time_window_minutes=15,
            threat_level=ThreatLevel.MEDIUM,
            auto_response=True,
        )

        self.detection_rules["suspicious_api_usage"] = ThreatDetectionRule(
            rule_id="suspicious_api_usage",
            name="Suspicious API Usage",
            description="Detects unusual API usage patterns indicating potential bot activity",
            event_types=[SecurityEventType.SUSPICIOUS_API_USAGE],
            conditions={"rate_limit": 1000, "time_window": 60},
            threshold=1000,
            time_window_minutes=60,
            threat_level=ThreatLevel.HIGH,
            auto_response=True,
        )

        self.detection_rules["unusual_data_access"] = ThreatDetectionRule(
            rule_id="unusual_data_access",
            name="Unusual Data Access",
            description="Detects access to sensitive data outside normal hours",
            event_types=[SecurityEventType.UNUSUAL_DATA_ACCESS],
            conditions={"business_hours": False},
            threshold=1,
            time_window_minutes=60,
            threat_level=ThreatLevel.HIGH,
            auto_response=False,
        )

        self.detection_rules["privilege_escalation"] = ThreatDetectionRule(
            rule_id="privilege_escalation",
            name="Privilege Escalation Attempt",
            description="Detects attempts to access admin functions",
            event_types=[SecurityEventType.PRIVILEGE_ESCALATION],
            conditions={"admin_endpoints": True},
            threshold=1,
            time_window_minutes=5,
            threat_level=ThreatLevel.CRITICAL,
            auto_response=False,
        )

    def get_security_metrics(self) -> dict[str, Any]:
        """Get comprehensive security metrics"""
        now = datetime.now(timezone.utc)

        # Calculate recent activity
        last_24h = now - timedelta(hours=24)
        recent_events = [e for e in self.events if e.timestamp > last_24h]

        # Group by threat level
        threat_breakdown = defaultdict(int)
        for event in recent_events:
            threat_breakdown[event.threat_level.value] += 1

        # Group by event type
        event_breakdown = defaultdict(int)
        for event in recent_events:
            event_breakdown[event.event_type.value] += 1

        return {
            **self.metrics,
            "total_events": len(self.events),
            "events_last_24h": len(recent_events),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "active_rules": len([r for r in self.detection_rules.values() if r.enabled]),
            "threat_level_breakdown": dict(threat_breakdown),
            "event_type_breakdown": dict(event_breakdown),
            "last_update": now.isoformat(),
        }

    def get_threat_summary(self, hours: int = 24) -> dict[str, Any]:
        """Get threat summary for specified time period"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_events = [e for e in self.events if e.timestamp > cutoff]

        # Find high-threat events
        high_threats = [e for e in recent_events if e.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]

        # Top source IPs
        ip_counts = defaultdict(int)
        for event in recent_events:
            if event.source_ip:
                ip_counts[event.source_ip] += 1

        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "time_period_hours": hours,
            "total_events": len(recent_events),
            "high_threat_events": len(high_threats),
            "critical_threats": len([e for e in high_threats if e.threat_level == ThreatLevel.CRITICAL]),
            "top_source_ips": top_ips,
            "threat_events": [e.to_dict() for e in high_threats[:10]],  # Latest 10 high threats
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def register_response_handler(self, event_type: SecurityEventType, handler: Callable):
        """Register custom response handler for security events"""
        self.response_handlers[event_type].append(handler)
        logger.info(f"Response handler registered for {event_type.value}")

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(int(time.time() * 1000000))
        return f"evt_{hashlib.sha256(timestamp.encode()).hexdigest()[:16]}"


# Global defense monitor instance
_defense_monitor: Optional[DefenseMonitor] = None


def get_defense_monitor() -> DefenseMonitor:
    """Get global defense monitor instance"""
    global _defense_monitor
    if _defense_monitor is None:
        _defense_monitor = DefenseMonitor()
    return _defense_monitor


# Convenience functions for common security events


async def record_authentication_failure(user_id: str, source_ip: str, reason: str = "invalid_credentials"):
    """Record authentication failure event"""
    monitor = get_defense_monitor()
    await monitor.record_event(
        SecurityEventType.AUTHENTICATION_FAILURE,
        {"reason": reason},
        source_ip=source_ip,
        user_id=user_id,
        threat_level=ThreatLevel.LOW,
    )


async def record_api_request(endpoint: str, source_ip: str, user_id: Optional[str] = None, response_code: int = 200):
    """Record API request for monitoring"""
    monitor = get_defense_monitor()

    # Determine if suspicious based on patterns
    threat_level = ThreatLevel.LOW
    if response_code >= 400:
        threat_level = ThreatLevel.MEDIUM

    await monitor.record_event(
        SecurityEventType.SUSPICIOUS_API_USAGE,
        {"response_code": response_code},
        source_ip=source_ip,
        user_id=user_id,
        endpoint=endpoint,
        threat_level=threat_level,
    )


async def record_data_access(resource: str, operation: str, user_id: str, source_ip: str):
    """Record data access for audit and monitoring"""
    monitor = get_defense_monitor()
    await monitor.record_event(
        SecurityEventType.UNUSUAL_DATA_ACCESS,
        {"resource": resource, "operation": operation},
        source_ip=source_ip,
        user_id=user_id,
        threat_level=ThreatLevel.LOW,
    )


# Example usage and testing
async def example_usage():
    """Example usage of defense monitoring system"""
    print("🛡️ Defense-in-Depth Monitoring Example")
    print("=" * 50)

    # Get defense monitor
    monitor = get_defense_monitor()

    # Simulate various security events
    print("\n📊 Simulating security events...")

    # Multiple failed logins (should trigger threat detection)
    for i in range(6):
        await record_authentication_failure(
            user_id="testuser@example.com", source_ip="192.168.1.100", reason="invalid_password"
        )
        await asyncio.sleep(0.1)  # Small delay

    # Suspicious API usage
    for i in range(50):
        await record_api_request(
            endpoint=f"/api/endpoint_{i % 10}", source_ip="10.0.0.50", user_id="apiuser@example.com"
        )

    # Data access during off-hours
    await record_data_access(
        resource="sensitive_database", operation="SELECT", user_id="nightuser@example.com", source_ip="172.16.0.10"
    )

    print("✅ Security events recorded")

    # Get security metrics
    metrics = monitor.get_security_metrics()
    print("\n📈 Security Metrics:")
    print(f"  Total events processed: {metrics['events_processed']}")
    print(f"  Threats detected: {metrics['threats_detected']}")
    print(f"  Auto-responses triggered: {metrics['auto_responses_triggered']}")
    print(f"  Blocked IPs: {metrics['blocked_ips']}")

    # Get threat summary
    threat_summary = monitor.get_threat_summary(hours=1)
    print("\n🚨 Threat Summary (last 1 hour):")
    print(f"  Total events: {threat_summary['total_events']}")
    print(f"  High-threat events: {threat_summary['high_threat_events']}")
    print(f"  Critical threats: {threat_summary['critical_threats']}")

    if threat_summary["top_source_ips"]:
        print(
            f"  Top source IP: {threat_summary['top_source_ips'][0][0]} ({threat_summary['top_source_ips'][0][1]} events)"
        )

    print("\n✅ Defense monitoring test completed")


if __name__ == "__main__":
    asyncio.run(example_usage())
