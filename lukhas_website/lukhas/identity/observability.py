"""
LUKHAS Identity Observability Layer
==================================

Comprehensive observability infrastructure for the LUKHAS tiered authentication system.
Provides OpenTelemetry tracing, Prometheus metrics, structured logging, and performance
monitoring for T4/0.01% excellence compliance.

Features:
- OpenTelemetry distributed tracing
- Prometheus metrics collection
- Structured logging with correlation IDs
- Performance monitoring and SLA tracking
- Security event monitoring
- Health checks and alerting
- Dashboard-ready metrics export
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog

# OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import (
        FastAPIInstrumentor,  # noqa: F401  # TODO: opentelemetry.instrumentation....
    )
    from opentelemetry.instrumentation.httpx import (
        HTTPXClientInstrumentor,  # noqa: F401  # TODO: opentelemetry.instrumentation....
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

# Prometheus imports
try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = structlog.get_logger(__name__)


class AuthenticationMetrics:
    """Prometheus metrics for authentication system."""

    def __init__(self, registry: Optional[Any] = None):
        """Initialize authentication metrics."""
        self.registry = registry or (CollectorRegistry() if PROMETHEUS_AVAILABLE else None)

        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus not available - metrics disabled")
            return

        # Authentication counters
        self.auth_attempts_total = Counter(
            'lukhas_auth_attempts_total',
            'Total authentication attempts',
            ['tier', 'result', 'user_id'],
            registry=self.registry
        )

        self.auth_errors_total = Counter(
            'lukhas_auth_errors_total',
            'Total authentication errors',
            ['tier', 'error_type'],
            registry=self.registry
        )

        # Performance histograms
        self.auth_duration_seconds = Histogram(
            'lukhas_auth_duration_seconds',
            'Authentication duration in seconds',
            ['tier'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry
        )

        self.webauthn_challenge_duration_seconds = Histogram(
            'lukhas_webauthn_challenge_duration_seconds',
            'WebAuthn challenge generation duration',
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
            registry=self.registry
        )

        self.biometric_auth_duration_seconds = Histogram(
            'lukhas_biometric_auth_duration_seconds',
            'Biometric authentication duration',
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
            registry=self.registry
        )

        # System gauges
        self.active_sessions = Gauge(
            'lukhas_active_sessions_total',
            'Number of active authentication sessions',
            registry=self.registry
        )

        self.guardian_validations = Counter(
            'lukhas_guardian_validations_total',
            'Total Guardian system validations',
            ['action', 'result'],
            registry=self.registry
        )

        # Security metrics
        self.security_events_total = Counter(
            'lukhas_security_events_total',
            'Total security events',
            ['event_type', 'threat_level', 'action'],
            registry=self.registry
        )

        self.rate_limit_hits = Counter(
            'lukhas_rate_limit_hits_total',
            'Rate limit violations',
            ['rule_name', 'action'],
            registry=self.registry
        )

        self.nonce_operations = Counter(
            'lukhas_nonce_operations_total',
            'Nonce operations',
            ['operation', 'result'],
            registry=self.registry
        )

        # SLA compliance metrics
        self.sla_violations = Counter(
            'lukhas_sla_violations_total',
            'SLA violations by tier',
            ['tier', 'metric'],
            registry=self.registry
        )

        # System info
        self.system_info = Info(
            'lukhas_auth_system',
            'Authentication system information',
            registry=self.registry
        )

        # Set system info
        self.system_info.info({
            'component': 'I.2_Tiered_Authentication',
            'version': '1.0.0',
            'standard': 'T4/0.01% Excellence'
        })

    def record_authentication_attempt(self, tier: str, success: bool, user_id: str, duration_seconds: float):
        """Record authentication attempt metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        result = 'success' if success else 'failure'
        self.auth_attempts_total.labels(tier=tier, result=result, user_id=user_id).inc()
        self.auth_duration_seconds.labels(tier=tier).observe(duration_seconds)

        # Check SLA compliance
        sla_limits = {'T1': 0.05, 'T2': 0.2, 'T3': 0.15, 'T4': 0.3, 'T5': 0.4}
        if tier in sla_limits and duration_seconds > sla_limits[tier]:
            self.sla_violations.labels(tier=tier, metric='latency').inc()

    def record_authentication_error(self, tier: str, error_type: str):
        """Record authentication error."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.auth_errors_total.labels(tier=tier, error_type=error_type).inc()

    def record_webauthn_challenge(self, duration_seconds: float):
        """Record WebAuthn challenge generation."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.webauthn_challenge_duration_seconds.observe(duration_seconds)

    def record_biometric_auth(self, duration_seconds: float):
        """Record biometric authentication."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.biometric_auth_duration_seconds.observe(duration_seconds)

    def record_guardian_validation(self, action: str, success: bool):
        """Record Guardian system validation."""
        if not PROMETHEUS_AVAILABLE:
            return

        result = 'success' if success else 'failure'
        self.guardian_validations.labels(action=action, result=result).inc()

    def record_security_event(self, event_type: str, threat_level: str, action: str):
        """Record security event."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.security_events_total.labels(
            event_type=event_type,
            threat_level=threat_level,
            action=action
        ).inc()

    def record_rate_limit_hit(self, rule_name: str, action: str):
        """Record rate limit hit."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.rate_limit_hits.labels(rule_name=rule_name, action=action).inc()

    def record_nonce_operation(self, operation: str, success: bool):
        """Record nonce operation."""
        if not PROMETHEUS_AVAILABLE:
            return

        result = 'success' if success else 'failure'
        self.nonce_operations.labels(operation=operation, result=result).inc()

    def update_active_sessions(self, count: int):
        """Update active sessions count."""
        if not PROMETHEUS_AVAILABLE:
            return

        self.active_sessions.set(count)

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus not available\n"

        return generate_latest(self.registry).decode('utf-8')


class OpenTelemetryTracer:
    """OpenTelemetry tracing for authentication system."""

    def __init__(self, service_name: str = "lukhas-identity"):
        """Initialize OpenTelemetry tracing."""
        self.service_name = service_name
        self.tracer = None

        if not OTEL_AVAILABLE:
            logger.warning("OpenTelemetry not available - tracing disabled")
            return

        # Configure tracing
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "1.0.0",
            "service.instance.id": f"{service_name}-{int(time.time())}"
        })

        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))

        # Configure OTLP exporter (can be configured to send to Jaeger, etc.)
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint="http://localhost:4317",  # Default OTLP endpoint
                insecure=True
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
        except Exception as e:
            logger.warning("Failed to configure OTLP exporter", error=str(e))

        # Get tracer
        self.tracer = trace.get_tracer(service_name)

        logger.info("OpenTelemetry tracing initialized", service_name=service_name)

    @asynccontextmanager
    async def trace_authentication(self, tier: str, user_id: str, correlation_id: str):
        """Trace authentication operation."""
        if not self.tracer:
            yield None
            return

        with self.tracer.start_as_current_span(
            f"authenticate_{tier.lower()}",
            attributes={
                "auth.tier": tier,
                "auth.user_id": user_id,
                "auth.correlation_id": correlation_id,
                "auth.component": "tiered_authenticator"
            }
        ) as span:
            yield span

    @asynccontextmanager
    async def trace_webauthn_challenge(self, user_id: str, correlation_id: str):
        """Trace WebAuthn challenge generation."""
        if not self.tracer:
            yield None
            return

        with self.tracer.start_as_current_span(
            "webauthn_challenge_generation",
            attributes={
                "webauthn.user_id": user_id,
                "webauthn.correlation_id": correlation_id,
                "webauthn.component": "enhanced_webauthn_service"
            }
        ) as span:
            yield span

    @asynccontextmanager
    async def trace_webauthn_verification(self, challenge_id: str, correlation_id: str):
        """Trace WebAuthn verification."""
        if not self.tracer:
            yield None
            return

        with self.tracer.start_as_current_span(
            "webauthn_verification",
            attributes={
                "webauthn.challenge_id": challenge_id,
                "webauthn.correlation_id": correlation_id,
                "webauthn.component": "enhanced_webauthn_service"
            }
        ) as span:
            yield span

    @asynccontextmanager
    async def trace_biometric_auth(self, user_id: str, modality: str, nonce: str):
        """Trace biometric authentication."""
        if not self.tracer:
            yield None
            return

        with self.tracer.start_as_current_span(
            "biometric_authentication",
            attributes={
                "biometric.user_id": user_id,
                "biometric.modality": modality,
                "biometric.nonce": nonce,
                "biometric.component": "mock_biometric_provider"
            }
        ) as span:
            yield span

    @asynccontextmanager
    async def trace_security_check(self, ip_address: str, endpoint: str):
        """Trace security hardening check."""
        if not self.tracer:
            yield None
            return

        with self.tracer.start_as_current_span(
            "security_hardening_check",
            attributes={
                "security.ip_address": ip_address,
                "security.endpoint": endpoint,
                "security.component": "security_hardening_manager"
            }
        ) as span:
            yield span

    def add_span_event(self, span: Any, name: str, attributes: Dict[str, Any]):
        """Add event to current span."""
        if span and hasattr(span, 'add_event'):
            span.add_event(name, attributes)

    def set_span_status(self, span: Any, success: bool, message: str = ""):
        """Set span status."""
        if span and hasattr(span, 'set_status'):
            from opentelemetry.trace import Status, StatusCode
            status_code = StatusCode.OK if success else StatusCode.ERROR
            span.set_status(Status(status_code, message))


class StructuredLogger:
    """Enhanced structured logging for authentication system."""

    def __init__(self):
        """Initialize structured logger."""
        self.logger = structlog.get_logger("identity")

    def log_authentication_attempt(
        self,
        tier: str,
        user_id: str,
        correlation_id: str,
        success: bool,
        duration_ms: float,
        reason: str = "",
        ip_address: str = "",
        user_agent: str = ""
    ):
        """Log authentication attempt with full context."""
        log_data = {
            "event": "authentication_attempt",
            "tier": tier,
            "user_id": user_id,
            "correlation_id": correlation_id,
            "success": success,
            "duration_ms": duration_ms,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if reason:
            log_data["reason"] = reason

        if success:
            self.logger.info("Authentication successful", **log_data)
        else:
            self.logger.warning("Authentication failed", **log_data)

    def log_security_event(
        self,
        event_type: str,
        threat_level: str,
        action: str,
        ip_address: str,
        description: str,
        indicators: List[str],
        correlation_id: str = ""
    ):
        """Log security event."""
        log_data = {
            "event": "security_event",
            "event_type": event_type,
            "threat_level": threat_level,
            "action": action,
            "ip_address": ip_address,
            "description": description,
            "indicators": indicators,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if threat_level in ["high", "critical"]:
            self.logger.error("High-severity security event", **log_data)
        else:
            self.logger.warning("Security event detected", **log_data)

    def log_performance_sla_violation(
        self,
        tier: str,
        operation: str,
        duration_ms: float,
        target_ms: float,
        correlation_id: str = ""
    ):
        """Log SLA violation."""
        log_data = {
            "event": "sla_violation",
            "tier": tier,
            "operation": operation,
            "duration_ms": duration_ms,
            "target_ms": target_ms,
            "violation_percent": ((duration_ms - target_ms) / target_ms) * 100,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.logger.error("Performance SLA violation", **log_data)

    def log_guardian_validation(
        self,
        action: str,
        success: bool,
        duration_ms: float,
        context: Dict[str, Any],
        correlation_id: str = ""
    ):
        """Log Guardian system validation."""
        log_data = {
            "event": "guardian_validation",
            "action": action,
            "success": success,
            "duration_ms": duration_ms,
            "context": context,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if success:
            self.logger.debug("Guardian validation successful", **log_data)
        else:
            self.logger.warning("Guardian validation failed", **log_data)


class ObservabilityManager:
    """Comprehensive observability manager for authentication system."""

    def __init__(self, service_name: str = "lukhas-identity"):
        """Initialize observability components."""
        self.service_name = service_name

        # Initialize components
        self.metrics = AuthenticationMetrics()
        self.tracer = OpenTelemetryTracer(service_name)
        self.logger = StructuredLogger()

        # Performance tracking
        self._performance_data = {
            "authentication_times": {},
            "webauthn_times": [],
            "biometric_times": [],
            "security_check_times": []
        }

        # SLA targets (in milliseconds)
        self._sla_targets = {
            "T1": 50,
            "T2": 200,
            "T3": 150,
            "T4": 300,
            "T5": 400
        }

        structlog.get_logger(__name__).info(
            "Observability manager initialized",
            service_name=service_name,
            prometheus_available=PROMETHEUS_AVAILABLE,
            otel_available=OTEL_AVAILABLE
        )

    @asynccontextmanager
    async def observe_authentication(self, tier: str, user_id: str, correlation_id: str, ip_address: str = "", user_agent: str = ""):
        """Comprehensive observability wrapper for authentication."""
        start_time = time.perf_counter()

        # Start tracing
        async with self.tracer.trace_authentication(tier, user_id, correlation_id) as span:
            try:
                yield span

                # Success path
                duration_ms = (time.perf_counter() - start_time) * 1000
                duration_seconds = duration_ms / 1000

                # Record metrics
                self.metrics.record_authentication_attempt(tier, True, user_id, duration_seconds)

                # Log success
                self.logger.log_authentication_attempt(
                    tier, user_id, correlation_id, True, duration_ms,
                    reason="success", ip_address=ip_address, user_agent=user_agent
                )

                # Check SLA compliance
                if tier in self._sla_targets and duration_ms > self._sla_targets[tier]:
                    self.logger.log_performance_sla_violation(
                        tier, "authentication", duration_ms, self._sla_targets[tier], correlation_id
                    )

                # Update performance tracking
                if tier not in self._performance_data["authentication_times"]:
                    self._performance_data["authentication_times"][tier] = []
                self._performance_data["authentication_times"][tier].append(duration_ms)

                # Set span success
                self.tracer.set_span_status(span, True)

            except Exception as e:
                # Error path
                duration_ms = (time.perf_counter() - start_time) * 1000
                duration_seconds = duration_ms / 1000

                # Record error metrics
                self.metrics.record_authentication_attempt(tier, False, user_id, duration_seconds)
                self.metrics.record_authentication_error(tier, type(e).__name__)

                # Log error
                self.logger.log_authentication_attempt(
                    tier, user_id, correlation_id, False, duration_ms,
                    reason=str(e), ip_address=ip_address, user_agent=user_agent
                )

                # Set span error
                self.tracer.set_span_status(span, False, str(e))

                raise

    @asynccontextmanager
    async def observe_webauthn_challenge(self, user_id: str, correlation_id: str):
        """Observe WebAuthn challenge generation."""
        start_time = time.perf_counter()

        async with self.tracer.trace_webauthn_challenge(user_id, correlation_id) as span:
            try:
                yield span

                duration_ms = (time.perf_counter() - start_time) * 1000
                duration_seconds = duration_ms / 1000

                self.metrics.record_webauthn_challenge(duration_seconds)
                self._performance_data["webauthn_times"].append(duration_ms)

                self.tracer.set_span_status(span, True)

            except Exception as e:
                self.tracer.set_span_status(span, False, str(e))
                raise

    @asynccontextmanager
    async def observe_biometric_auth(self, user_id: str, modality: str, nonce: str):
        """Observe biometric authentication."""
        start_time = time.perf_counter()

        async with self.tracer.trace_biometric_auth(user_id, modality, nonce) as span:
            try:
                yield span

                duration_ms = (time.perf_counter() - start_time) * 1000
                duration_seconds = duration_ms / 1000

                self.metrics.record_biometric_auth(duration_seconds)
                self._performance_data["biometric_times"].append(duration_ms)

                self.tracer.set_span_status(span, True)

            except Exception as e:
                self.tracer.set_span_status(span, False, str(e))
                raise

    @asynccontextmanager
    async def observe_security_check(self, ip_address: str, endpoint: str):
        """Observe security hardening check."""
        start_time = time.perf_counter()

        async with self.tracer.trace_security_check(ip_address, endpoint) as span:
            try:
                yield span

                duration_ms = (time.perf_counter() - start_time) * 1000
                self._performance_data["security_check_times"].append(duration_ms)

                self.tracer.set_span_status(span, True)

            except Exception as e:
                self.tracer.set_span_status(span, False, str(e))
                raise

    def record_guardian_validation(self, action: str, success: bool, duration_ms: float, context: Dict[str, Any], correlation_id: str = ""):
        """Record Guardian system validation."""
        self.metrics.record_guardian_validation(action, success)
        self.logger.log_guardian_validation(action, success, duration_ms, context, correlation_id)

    def record_security_event(self, event_type: str, threat_level: str, action: str, ip_address: str, description: str, indicators: List[str], correlation_id: str = ""):
        """Record security event."""
        self.metrics.record_security_event(event_type, threat_level, action)
        self.logger.log_security_event(event_type, threat_level, action, ip_address, description, indicators, correlation_id)

    def record_rate_limit_hit(self, rule_name: str, action: str):
        """Record rate limit hit."""
        self.metrics.record_rate_limit_hit(rule_name, action)

    def record_nonce_operation(self, operation: str, success: bool):
        """Record nonce operation."""
        self.metrics.record_nonce_operation(operation, success)

    def update_active_sessions(self, count: int):
        """Update active sessions count."""
        self.metrics.update_active_sessions(count)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring."""
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_name": self.service_name,
            "sla_targets": self._sla_targets,
            "performance_data": {}
        }

        # Authentication performance by tier
        for tier, times in self._performance_data["authentication_times"].items():
            if not times:
                continue

            target = self._sla_targets.get(tier, 0)
            mean_time = sum(times) / len(times)
            p95_time = sorted(times)[int(len(times) * 0.95)] if times else 0
            sla_violations = sum(1 for t in times if t > target)

            summary["performance_data"][f"auth_{tier.lower()}"] = {
                "samples": len(times),
                "mean_ms": round(mean_time, 2),
                "p95_ms": round(p95_time, 2),
                "target_ms": target,
                "sla_compliance_rate": 1.0 - (sla_violations / len(times)),
                "sla_violations": sla_violations
            }

        # WebAuthn performance
        if self._performance_data["webauthn_times"]:
            times = self._performance_data["webauthn_times"]
            summary["performance_data"]["webauthn"] = {
                "samples": len(times),
                "mean_ms": round(sum(times) / len(times), 2),
                "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 2)
            }

        # Biometric performance
        if self._performance_data["biometric_times"]:
            times = self._performance_data["biometric_times"]
            summary["performance_data"]["biometric"] = {
                "samples": len(times),
                "mean_ms": round(sum(times) / len(times), 2),
                "p95_ms": round(sorted(times)[int(len(times) * 0.95)], 2)
            }

        return summary

    def get_metrics_endpoint(self) -> str:
        """Get Prometheus metrics for export."""
        return self.metrics.get_metrics()

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for monitoring."""
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_name": self.service_name,
            "observability": {
                "prometheus_available": PROMETHEUS_AVAILABLE,
                "opentelemetry_available": OTEL_AVAILABLE,
                "structured_logging": True
            },
            "performance_summary": self.get_performance_summary()
        }


# Global observability manager instance
_observability_manager: Optional[ObservabilityManager] = None


def get_observability_manager() -> ObservabilityManager:
    """Get or create global observability manager."""
    global _observability_manager
    if _observability_manager is None:
        _observability_manager = ObservabilityManager()
    return _observability_manager


def initialize_observability(service_name: str = "lukhas-identity") -> ObservabilityManager:
    """Initialize observability infrastructure."""
    global _observability_manager
    _observability_manager = ObservabilityManager(service_name)
    return _observability_manager
