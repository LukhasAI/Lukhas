#!/usr/bin/env python3
"""
LUKHAS Identity Service Metrics Collector
T4/0.01% Excellence Standard

Advanced metrics collection for OIDC/WebAuthn services with Prometheus integration.
Provides comprehensive performance, security, and operational monitoring.
"""

from __future__ import annotations

import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Prometheus metrics (with fallback stubs)
try:
    from prometheus_client import Counter, Gauge, Histogram, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def inc(self, amount=1):
            pass

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def observe(self, value):
            pass

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def set(self, value):
            pass

    class Info:
        def __init__(self, *args, **kwargs):
            pass
        def info(self, labels):
            pass


class MetricType(Enum):
    """Metric types for identity services"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    INFO = "info"


class OperationType(Enum):
    """Identity operation types"""
    AUTHORIZATION = "authorization"
    TOKEN_EXCHANGE = "token_exchange"
    TOKEN_INTROSPECTION = "token_introspection"
    TOKEN_REVOCATION = "token_revocation"
    USERINFO = "userinfo"
    JWKS = "jwks"
    DISCOVERY = "discovery"
    WEBAUTHN_REGISTRATION = "webauthn_registration"
    WEBAUTHN_AUTHENTICATION = "webauthn_authentication"
    CLIENT_REGISTRATION = "client_registration"
    SESSION_VALIDATION = "session_validation"


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MetricSnapshot:
    """Snapshot of metric values at a point in time"""
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Performance statistics"""
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    mean_ms: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0


class ServiceMetricsCollector:
    """
    Advanced metrics collector for LUKHAS Identity services.

    Features:
    - Prometheus metrics integration
    - Performance monitoring (latency, throughput)
    - Security event tracking
    - Resource utilization monitoring
    - Custom business metrics
    - Real-time alerting support
    """

    def __init__(self, service_name: str = "lukhas_identity"):
        """Initialize metrics collector"""
        self.service_name = service_name
        self._lock = threading.Lock()

        # Performance tracking
        self._request_times: Dict[str, List[float]] = {}
        self._max_samples = 1000  # Keep last 1000 samples per endpoint

        # Initialize Prometheus metrics
        self._init_prometheus_metrics()

        # Internal statistics
        self._stats = {
            'total_requests': 0,
            'total_errors': 0,
            'security_events': 0,
            'active_sessions': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

        logger.info(f"🔍 ServiceMetricsCollector initialized for {service_name}")

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # Request metrics
        self.http_requests_total = Counter(
            'lukhas_identity_http_requests_total',
            'Total HTTP requests processed',
            ['method', 'endpoint', 'status', 'lane']
        )

        self.http_request_duration_seconds = Histogram(
            'lukhas_identity_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'lane'],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
        )

        # Authentication metrics
        self.auth_attempts_total = Counter(
            'lukhas_identity_auth_attempts_total',
            'Total authentication attempts',
            ['method', 'tier', 'result', 'lane']
        )

        self.token_operations_total = Counter(
            'lukhas_identity_token_operations_total',
            'Total token operations',
            ['operation', 'grant_type', 'client_id', 'result']
        )

        self.webauthn_operations_total = Counter(
            'lukhas_identity_webauthn_operations_total',
            'Total WebAuthn operations',
            ['operation', 'result', 'authenticator_type']
        )

        # Security metrics
        self.security_events_total = Counter(
            'lukhas_identity_security_events_total',
            'Total security events',
            ['event_type', 'threat_level', 'action']
        )

        self.rate_limit_violations_total = Counter(
            'lukhas_identity_rate_limit_violations_total',
            'Total rate limit violations',
            ['endpoint', 'client_ip', 'action']
        )

        # Performance metrics
        self.active_sessions_gauge = Gauge(
            'lukhas_identity_active_sessions',
            'Number of active user sessions'
        )

        self.cache_operations_total = Counter(
            'lukhas_identity_cache_operations_total',
            'Total cache operations',
            ['cache_type', 'operation', 'result']
        )

        self.cache_hit_ratio = Gauge(
            'lukhas_identity_cache_hit_ratio',
            'Cache hit ratio',
            ['cache_type']
        )

        # Business metrics
        self.client_registrations_total = Counter(
            'lukhas_identity_client_registrations_total',
            'Total client registrations',
            ['application_type', 'status']
        )

        self.user_tier_distribution = Gauge(
            'lukhas_identity_user_tier_distribution',
            'Distribution of users by tier',
            ['tier_level']
        )

        # System health
        self.service_info = Info(
            'lukhas_identity_service_info',
            'Service information'
        )

        self.service_info.info({
            'service_name': self.service_name,
            'version': '1.0.0',
            'prometheus_available': str(PROMETHEUS_AVAILABLE).lower()
        })

    @contextmanager
    def time_operation(self, operation: OperationType, **labels):
        """Context manager for timing operations"""
        start_time = time.perf_counter()
        operation_labels = {
            'operation': operation.value,
            **labels
        }

        try:
            yield
            # Success
            duration = time.perf_counter() - start_time
            self._record_operation_success(operation, duration, **labels)

        except Exception as e:
            # Error
            duration = time.perf_counter() - start_time
            self._record_operation_error(operation, duration, str(e), **labels)
            raise

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float,
        lane: str = "default"
    ):
        """Record HTTP request metrics"""
        # Prometheus metrics
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code),
            lane=lane
        ).inc()

        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
            lane=lane
        ).observe(duration_seconds)

        # Internal tracking
        with self._lock:
            endpoint_key = f"{method}:{endpoint}"
            if endpoint_key not in self._request_times:
                self._request_times[endpoint_key] = []

            times = self._request_times[endpoint_key]
            times.append(duration_seconds * 1000)  # Convert to ms

            # Keep only recent samples
            if len(times) > self._max_samples:
                times[:] = times[-self._max_samples:]

            self._stats['total_requests'] += 1
            if status_code >= 400:
                self._stats['total_errors'] += 1

    def record_auth_attempt(
        self,
        method: str,
        tier: str,
        success: bool,
        lane: str = "default"
    ):
        """Record authentication attempt"""
        result = "success" if success else "failure"

        self.auth_attempts_total.labels(
            method=method,
            tier=tier,
            result=result,
            lane=lane
        ).inc()

    def record_token_operation(
        self,
        operation: str,
        grant_type: str,
        client_id: str,
        success: bool
    ):
        """Record token operation"""
        result = "success" if success else "failure"

        self.token_operations_total.labels(
            operation=operation,
            grant_type=grant_type,
            client_id=client_id,
            result=result
        ).inc()

    def record_webauthn_operation(
        self,
        operation: str,
        success: bool,
        authenticator_type: str = "unknown"
    ):
        """Record WebAuthn operation"""
        result = "success" if success else "failure"

        self.webauthn_operations_total.labels(
            operation=operation,
            result=result,
            authenticator_type=authenticator_type
        ).inc()

    def record_security_event(
        self,
        event_type: str,
        threat_level: ThreatLevel,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record security event"""
        self.security_events_total.labels(
            event_type=event_type,
            threat_level=threat_level.value,
            action=action
        ).inc()

        with self._lock:
            self._stats['security_events'] += 1

        # Log high/critical threats
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            logger.warning(
                f"Security event: {event_type} (level={threat_level.value}, action={action})",
                extra={"metadata": metadata or {}}
            )

    def record_rate_limit_violation(
        self,
        endpoint: str,
        client_ip: str,
        action: str = "blocked"
    ):
        """Record rate limit violation"""
        self.rate_limit_violations_total.labels(
            endpoint=endpoint,
            client_ip=client_ip,
            action=action
        ).inc()

    def record_cache_operation(
        self,
        cache_type: str,
        operation: str,
        hit: bool
    ):
        """Record cache operation"""
        result = "hit" if hit else "miss"

        self.cache_operations_total.labels(
            cache_type=cache_type,
            operation=operation,
            result=result
        ).inc()

        with self._lock:
            if hit:
                self._stats['cache_hits'] += 1
            else:
                self._stats['cache_misses'] += 1

        # Update cache hit ratio
        total_ops = self._stats['cache_hits'] + self._stats['cache_misses']
        if total_ops > 0:
            hit_ratio = self._stats['cache_hits'] / total_ops
            self.cache_hit_ratio.labels(cache_type=cache_type).set(hit_ratio)

    def record_client_registration(
        self,
        application_type: str,
        success: bool
    ):
        """Record client registration"""
        status = "success" if success else "failure"

        self.client_registrations_total.labels(
            application_type=application_type,
            status=status
        ).inc()

    def update_active_sessions(self, count: int):
        """Update active sessions gauge"""
        self.active_sessions_gauge.set(count)
        with self._lock:
            self._stats['active_sessions'] = count

    def update_user_tier_distribution(self, tier_counts: Dict[int, int]):
        """Update user tier distribution"""
        for tier, count in tier_counts.items():
            self.user_tier_distribution.labels(tier_level=str(tier)).set(count)

    def get_performance_stats(self, endpoint: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics"""
        stats = {}

        with self._lock:
            if endpoint:
                # Specific endpoint stats
                times = self._request_times.get(endpoint, [])
                if times:
                    stats[endpoint] = self._calculate_stats(times)
            else:
                # All endpoint stats
                for ep, times in self._request_times.items():
                    if times:
                        stats[ep] = self._calculate_stats(times)

        return stats

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health and status metrics"""
        with self._lock:
            total_requests = self._stats['total_requests']
            total_errors = self._stats['total_errors']
            error_rate = (total_errors / max(total_requests, 1)) * 100

            cache_total = self._stats['cache_hits'] + self._stats['cache_misses']
            cache_hit_rate = (self._stats['cache_hits'] / max(cache_total, 1)) * 100

            return {
                'service_name': self.service_name,
                'prometheus_available': PROMETHEUS_AVAILABLE,
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate_percent': error_rate,
                'active_sessions': self._stats['active_sessions'],
                'security_events': self._stats['security_events'],
                'cache_hit_rate_percent': cache_hit_rate,
                'uptime_seconds': time.time(),  # Placeholder
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _record_operation_success(self, operation: OperationType, duration: float, **labels):
        """Record successful operation"""
        logger.debug(f"Operation completed: {operation.value} ({duration*1000:.2f}ms)")

    def _record_operation_error(self, operation: OperationType, duration: float, error: str, **labels):
        """Record failed operation"""
        logger.warning(f"Operation failed: {operation.value} ({duration*1000:.2f}ms) - {error}")

    def _calculate_stats(self, times: List[float]) -> PerformanceStats:
        """Calculate performance statistics from timing samples"""
        if not times:
            return PerformanceStats()

        sorted_times = sorted(times)
        n = len(sorted_times)

        # Calculate percentiles
        p50_idx = max(0, int(n * 0.5) - 1)
        p95_idx = max(0, int(n * 0.95) - 1)
        p99_idx = max(0, int(n * 0.99) - 1)

        p50 = sorted_times[p50_idx]
        p95 = sorted_times[p95_idx]
        p99 = sorted_times[p99_idx]
        mean = sum(times) / n

        # Estimate requests per second (rough approximation)
        rps = min(n / 60.0, 1000.0)  # Assume times are from last minute, cap at 1000

        return PerformanceStats(
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            mean_ms=mean,
            requests_per_second=rps,
            error_rate=0.0  # Would need more sophisticated tracking
        )

    def create_snapshot(self) -> MetricSnapshot:
        """Create snapshot of current metrics"""
        health_metrics = self.get_health_metrics()
        performance_stats = self.get_performance_stats()

        return MetricSnapshot(
            timestamp=datetime.now(timezone.utc),
            metrics={
                'health': health_metrics,
                'performance': performance_stats,
                'service_info': {
                    'name': self.service_name,
                    'prometheus_enabled': PROMETHEUS_AVAILABLE
                }
            }
        )

    def export_metrics(self, format_type: str = "prometheus") -> str:
        """Export metrics in specified format"""
        if format_type == "prometheus" and PROMETHEUS_AVAILABLE:
            from prometheus_client import generate_latest
            return generate_latest().decode('utf-8')
        elif format_type == "json":
            import json
            snapshot = self.create_snapshot()
            return json.dumps({
                'timestamp': snapshot.timestamp.isoformat(),
                'metrics': snapshot.metrics
            }, indent=2)
        else:
            return "Unsupported format or Prometheus not available"


# Global metrics collector instance
_global_metrics_collector: Optional[ServiceMetricsCollector] = None


def get_metrics_collector() -> ServiceMetricsCollector:
    """Get global metrics collector instance"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = ServiceMetricsCollector()
        logger.info("🔍 Global ServiceMetricsCollector initialized")
    return _global_metrics_collector


def record_endpoint_metrics(
    method: str,
    endpoint: str,
    status_code: int,
    duration_seconds: float,
    lane: str = "identity"
):
    """Convenience function to record endpoint metrics"""
    collector = get_metrics_collector()
    collector.record_http_request(method, endpoint, status_code, duration_seconds, lane)
