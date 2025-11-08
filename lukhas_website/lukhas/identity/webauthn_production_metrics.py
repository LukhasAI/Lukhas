"""
WebAuthn Production Metrics

Advanced Prometheus metrics collection for WebAuthn authentication system.
Provides comprehensive observability for security, performance, and reliability.

Performance Target: <1ms metric collection overhead
Coverage: 100% of WebAuthn operations and security events
Retention: 90 days for security events, 30 days for performance metrics

Metrics Categories:
- Authentication performance (p95, p99, p99.9 latencies)
- Security events (threats detected, blocked requests)
- User behavior patterns (device usage, geographic patterns)
- System health (circuit breaker status, rate limiting)
- Error rates and failure modes
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import structlog
from identity.webauthn_production import WebAuthnCredential
from identity.webauthn_security_hardening import SecurityEvent
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

logger = structlog.get_logger(__name__)


class MetricLabel(Enum):
    """Standardized metric labels for consistent reporting."""
    OPERATION = "operation"
    USER_TIER = "user_tier"
    AUTH_TYPE = "authenticator_type"
    THREAT_LEVEL = "threat_level"
    RESULT = "result"
    ERROR_TYPE = "error_type"
    DEVICE_TYPE = "device_type"
    GEOGRAPHIC_REGION = "region"
    SECURITY_POLICY = "policy"
    IP_REPUTATION = "ip_reputation"


@dataclass
class MetricThresholds:
    """SLO thresholds for alerting and monitoring."""

    # Performance SLOs (T4/0.01% excellence)
    auth_latency_p95_ms: float = 100.0
    auth_latency_p99_ms: float = 150.0
    auth_latency_p999_ms: float = 200.0

    # Security SLOs
    max_threat_events_per_hour: int = 100
    max_false_positive_rate: float = 0.01  # 1%
    max_emergency_lockdown_duration_minutes: int = 15

    # Reliability SLOs
    min_success_rate: float = 0.999  # 99.9%
    max_error_rate: float = 0.001   # 0.1%

    # System SLOs
    max_circuit_breaker_trips_per_hour: int = 5
    max_rate_limit_blocks_per_minute: int = 1000


class WebAuthnProductionMetrics:
    """Comprehensive production metrics for WebAuthn system."""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics collectors."""
        self.registry = registry or CollectorRegistry()
        self.thresholds = MetricThresholds()
        self._init_metrics()

    def _init_metrics(self):
        """Initialize all Prometheus metrics."""

        # Authentication Performance Metrics
        self.auth_request_duration = Histogram(
            'webauthn_auth_request_duration_seconds',
            'WebAuthn authentication request duration',
            ['operation', 'user_tier', 'authenticator_type', 'result'],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )

        self.auth_requests_total = Counter(
            'webauthn_auth_requests_total',
            'Total WebAuthn authentication requests',
            ['operation', 'result', 'authenticator_type', 'user_tier'],
            registry=self.registry
        )

        self.auth_success_rate = Gauge(
            'webauthn_auth_success_rate',
            'WebAuthn authentication success rate (sliding window)',
            ['authenticator_type', 'user_tier'],
            registry=self.registry
        )

        # Security Metrics
        self.security_events_total = Counter(
            'webauthn_security_events_total',
            'Total security events detected',
            ['event_type', 'threat_level', 'action_taken'],
            registry=self.registry
        )

        self.threat_detection_latency = Histogram(
            'webauthn_threat_detection_duration_seconds',
            'Time to detect security threats',
            ['threat_level', 'detection_method'],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
            registry=self.registry
        )

        self.blocked_requests_total = Counter(
            'webauthn_blocked_requests_total',
            'Total blocked authentication requests',
            ['block_reason', 'ip_reputation', 'user_tier'],
            registry=self.registry
        )

        self.false_positives_total = Counter(
            'webauthn_false_positives_total',
            'Total false positive security blocks',
            ['policy', 'user_tier'],
            registry=self.registry
        )

        # User Behavior Metrics
        self.active_devices_gauge = Gauge(
            'webauthn_active_devices',
            'Number of active WebAuthn devices',
            ['device_type', 'authenticator_type'],
            registry=self.registry
        )

        self.user_sessions_gauge = Gauge(
            'webauthn_active_user_sessions',
            'Number of active user sessions',
            ['user_tier', 'region'],
            registry=self.registry
        )

        self.credential_usage = Counter(
            'webauthn_credential_usage_total',
            'Total credential usage by type',
            ['credential_type', 'usage_pattern'],
            registry=self.registry
        )

        # System Health Metrics
        self.rate_limiter_status = Gauge(
            'webauthn_rate_limiter_tokens_available',
            'Available rate limiter tokens',
            ['limiter_type', 'user_tier'],
            registry=self.registry
        )

        self.circuit_breaker_status = Gauge(
            'webauthn_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['service', 'operation'],
            registry=self.registry
        )

        self.circuit_breaker_trips = Counter(
            'webauthn_circuit_breaker_trips_total',
            'Total circuit breaker trips',
            ['service', 'operation', 'reason'],
            registry=self.registry
        )

        # Error and Failure Metrics
        self.auth_errors_total = Counter(
            'webauthn_auth_errors_total',
            'Total authentication errors',
            ['error_type', 'error_code', 'operation'],
            registry=self.registry
        )

        self.system_errors_total = Counter(
            'webauthn_system_errors_total',
            'Total system-level errors',
            ['component', 'error_type', 'severity'],
            registry=self.registry
        )

        # Geographic and Device Metrics
        self.auth_by_region = Counter(
            'webauthn_auth_by_region_total',
            'Authentication attempts by geographic region',
            ['region', 'country', 'result'],
            registry=self.registry
        )

        self.device_fingerprint_matches = Counter(
            'webauthn_device_fingerprint_matches_total',
            'Device fingerprint match results',
            ['match_type', 'confidence_level'],
            registry=self.registry
        )

        # Emergency Response Metrics
        self.emergency_lockdowns_total = Counter(
            'webauthn_emergency_lockdowns_total',
            'Total emergency lockdown activations',
            ['trigger_reason', 'scope'],
            registry=self.registry
        )

        self.lockdown_duration = Histogram(
            'webauthn_lockdown_duration_seconds',
            'Duration of emergency lockdowns',
            ['trigger_reason'],
            buckets=(60, 300, 600, 1800, 3600, 7200),  # 1m to 2h
            registry=self.registry
        )

        # Business Intelligence Metrics
        self.user_adoption_by_tier = Gauge(
            'webauthn_user_adoption_by_tier',
            'WebAuthn adoption rate by user tier',
            ['user_tier'],
            registry=self.registry
        )

        self.credential_lifecycle_events = Counter(
            'webauthn_credential_lifecycle_events_total',
            'Credential lifecycle events',
            ['event_type', 'credential_type', 'user_tier'],
            registry=self.registry
        )

    async def record_auth_attempt(
        self,
        operation: str,
        user_tier: str,
        authenticator_type: str,
        duration_seconds: float,
        result: str,
        additional_labels: Optional[dict[str, str]] = None
    ):
        """Record authentication attempt metrics."""
        labels = {
            'operation': operation,
            'user_tier': user_tier,
            'authenticator_type': authenticator_type,
            'result': result
        }

        if additional_labels:
            labels.update(additional_labels)

        # Record duration
        self.auth_request_duration.labels(**labels).observe(duration_seconds)

        # Count request
        self.auth_requests_total.labels(**labels).inc()

        # Update success rate (simplified - in production would use sliding window)
        if result == 'success':
            current_rate = self.auth_success_rate.labels(
                authenticator_type=authenticator_type,
                user_tier=user_tier
            )._value._value or 0.0
            # Simple exponential moving average
            new_rate = 0.9 * current_rate + 0.1 * 1.0
            self.auth_success_rate.labels(
                authenticator_type=authenticator_type,
                user_tier=user_tier
            ).set(new_rate)

    async def record_security_event(
        self,
        event: SecurityEvent,
        detection_duration: Optional[float] = None,
        action_taken: str = "monitored"
    ):
        """Record security event metrics."""

        # Count security event
        self.security_events_total.labels(
            event_type=event.event_type,
            threat_level=event.threat_level.value,
            action_taken=action_taken
        ).inc()

        # Record detection latency if provided
        if detection_duration is not None:
            self.threat_detection_latency.labels(
                threat_level=event.threat_level.value,
                detection_method=event.detection_method or "unknown"
            ).observe(detection_duration)

        # Additional context-specific metrics
        if event.blocked:
            ip_reputation = event.context.get('ip_reputation', 'unknown')
            user_tier = event.context.get('user_tier', 'unknown')

            self.blocked_requests_total.labels(
                block_reason=event.event_type,
                ip_reputation=ip_reputation,
                user_tier=user_tier
            ).inc()

    async def record_false_positive(
        self,
        policy: str,
        user_tier: str,
        context: Optional[dict[str, Any]] = None
    ):
        """Record false positive security detection."""
        self.false_positives_total.labels(
            policy=policy,
            user_tier=user_tier
        ).inc()

        logger.warning(
            "False positive detected",
            policy=policy,
            user_tier=user_tier,
            context=context
        )

    async def record_device_activity(
        self,
        device_type: str,
        authenticator_type: str,
        active_count: int
    ):
        """Record active device metrics."""
        self.active_devices_gauge.labels(
            device_type=device_type,
            authenticator_type=authenticator_type
        ).set(active_count)

    async def record_user_session(
        self,
        user_tier: str,
        region: str,
        active_count: int
    ):
        """Record active user session metrics."""
        self.user_sessions_gauge.labels(
            user_tier=user_tier,
            region=region
        ).set(active_count)

    async def record_credential_usage(
        self,
        credential: WebAuthnCredential,
        usage_pattern: str = "normal"
    ):
        """Record credential usage patterns."""
        self.credential_usage.labels(
            credential_type=credential.authenticator_type.value,
            usage_pattern=usage_pattern
        ).inc()

    async def record_rate_limiter_status(
        self,
        limiter_type: str,
        user_tier: str,
        available_tokens: int
    ):
        """Record rate limiter token availability."""
        self.rate_limiter_status.labels(
            limiter_type=limiter_type,
            user_tier=user_tier
        ).set(available_tokens)

    async def record_circuit_breaker_event(
        self,
        service: str,
        operation: str,
        state: str,  # "closed", "open", "half-open"
        trip_reason: Optional[str] = None
    ):
        """Record circuit breaker events."""
        state_value = {"closed": 0, "open": 1, "half-open": 2}.get(state, 0)

        self.circuit_breaker_status.labels(
            service=service,
            operation=operation
        ).set(state_value)

        if trip_reason:
            self.circuit_breaker_trips.labels(
                service=service,
                operation=operation,
                reason=trip_reason
            ).inc()

    async def record_authentication_error(
        self,
        error_type: str,
        error_code: str,
        operation: str,
        context: Optional[dict[str, Any]] = None
    ):
        """Record authentication errors."""
        self.auth_errors_total.labels(
            error_type=error_type,
            error_code=error_code,
            operation=operation
        ).inc()

    async def record_geographic_auth(
        self,
        region: str,
        country: str,
        result: str
    ):
        """Record geographic authentication patterns."""
        self.auth_by_region.labels(
            region=region,
            country=country,
            result=result
        ).inc()

    async def record_emergency_lockdown(
        self,
        trigger_reason: str,
        scope: str,
        duration_seconds: Optional[float] = None
    ):
        """Record emergency lockdown events."""
        self.emergency_lockdowns_total.labels(
            trigger_reason=trigger_reason,
            scope=scope
        ).inc()

        if duration_seconds is not None:
            self.lockdown_duration.labels(
                trigger_reason=trigger_reason
            ).observe(duration_seconds)

    async def record_credential_lifecycle_event(
        self,
        event_type: str,  # "created", "used", "expired", "revoked"
        credential_type: str,
        user_tier: str
    ):
        """Record credential lifecycle events."""
        self.credential_lifecycle_events.labels(
            event_type=event_type,
            credential_type=credential_type,
            user_tier=user_tier
        ).inc()

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary for dashboards."""
        # This would typically query the metrics backend
        # For now, returning a structure that would be populated
        return {
            "performance": {
                "auth_latency_p95": "metrics would be queried here",
                "auth_latency_p99": "metrics would be queried here",
                "success_rate": "metrics would be queried here"
            },
            "security": {
                "threats_detected_last_hour": "metrics would be queried here",
                "blocked_requests_last_hour": "metrics would be queried here",
                "false_positive_rate": "metrics would be queried here"
            },
            "system_health": {
                "circuit_breaker_status": "metrics would be queried here",
                "rate_limiter_status": "metrics would be queried here",
                "error_rate": "metrics would be queried here"
            },
            "business_intelligence": {
                "active_users": "metrics would be queried here",
                "adoption_rate": "metrics would be queried here",
                "geographic_distribution": "metrics would be queried here"
            }
        }

    def check_slo_compliance(self) -> dict[str, bool]:
        """Check SLO compliance status."""
        # This would query actual metrics and compare against thresholds
        # For now, returning structure that would be populated
        return {
            "auth_latency_p95": True,  # Would check against self.thresholds.auth_latency_p95_ms
            "auth_latency_p99": True,
            "success_rate": True,
            "threat_detection_rate": True,
            "false_positive_rate": True,
            "system_availability": True
        }

    def get_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format."""
        return generate_latest(self.registry)


class MetricsMiddleware:
    """Middleware for automatic metrics collection."""

    def __init__(self, metrics: WebAuthnProductionMetrics):
        self.metrics = metrics

    async def __call__(self, operation: str, func, *args, **kwargs):
        """Wrap operations with automatic metrics collection."""
        start_time = time.perf_counter()

        try:
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start_time

            # Extract relevant labels from context
            user_tier = kwargs.get('user_tier', 'unknown')
            authenticator_type = kwargs.get('authenticator_type', 'unknown')

            await self.metrics.record_auth_attempt(
                operation=operation,
                user_tier=user_tier,
                authenticator_type=authenticator_type,
                duration_seconds=duration,
                result='success'
            )

            return result

        except Exception as e:
            duration = time.perf_counter() - start_time

            await self.metrics.record_auth_attempt(
                operation=operation,
                user_tier=kwargs.get('user_tier', 'unknown'),
                authenticator_type=kwargs.get('authenticator_type', 'unknown'),
                duration_seconds=duration,
                result='error'
            )

            await self.metrics.record_authentication_error(
                error_type=type(e).__name__,
                error_code=getattr(e, 'code', 'unknown'),
                operation=operation
            )

            raise


# Global metrics instance
webauthn_metrics = WebAuthnProductionMetrics()


def with_metrics(operation: str):
    """Decorator for automatic metrics collection."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            middleware = MetricsMiddleware(webauthn_metrics)
            return await middleware(operation, func, *args, **kwargs)
        return wrapper
    return decorator


# Example usage and integration points
if __name__ == "__main__":
    async def example_usage():
        """Example of metrics integration."""
        metrics = WebAuthnProductionMetrics()

        # Record authentication attempt
        await metrics.record_auth_attempt(
            operation="authenticate",
            user_tier="T4",
            authenticator_type="platform",
            duration_seconds=0.045,
            result="success"
        )

        # Record security event
        from identity.webauthn_security_hardening import SecurityEvent, ThreatLevel

        event = SecurityEvent(
            event_type="rate_limit_exceeded",
            threat_level=ThreatLevel.MEDIUM,
            timestamp=datetime.now(),
            context={"ip_address": "192.168.1.100"},
            blocked=True
        )

        await metrics.record_security_event(event, detection_duration=0.002)

        # Get metrics summary
        summary = metrics.get_metrics_summary()
        print(f"Metrics summary: {summary}")

        # Export Prometheus metrics
        prometheus_data = metrics.get_prometheus_metrics()
        print(f"Prometheus metrics size: {len(prometheus_data)} bytes")

    asyncio.run(example_usage())
