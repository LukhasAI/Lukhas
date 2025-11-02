"""
LUKHAS Ledger Prometheus Metrics v2.0.0
=======================================

Comprehensive metrics collection for T4/0.01% excellence monitoring:
- ledger_append_seconds: Event append latency histogram
- ledger_replay_seconds: Replay operation latency
- ledger_consumer_lag: Consumer processing lag gauge
- Performance alerts: consumer lag >1000, append p95 >50ms
"""

import logging
import threading
import time
from typing import Any, Dict, Optional

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    start_http_server,
)

logger = logging.getLogger(__name__)


class LedgerMetrics:
    """
    Prometheus metrics collector for LUKHAS ledger operations.

    Implements T4/0.01% excellence performance monitoring with
    specific focus on sub-50ms append latency requirements.
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics with optional custom registry"""
        self.registry = registry or CollectorRegistry()
        self._lock = threading.Lock()

        # Event append latency histogram (key T4 metric)
        self.ledger_append_seconds = Histogram(
            "ledger_append_seconds",
            "Time spent appending events to ledger",
            buckets=(
                0.001,  # 1ms
                0.005,  # 5ms
                0.010,  # 10ms
                0.025,  # 25ms
                0.050,  # 50ms (T4 requirement threshold)
                0.100,  # 100ms
                0.250,  # 250ms
                0.500,  # 500ms
                1.000,  # 1s
                2.500,  # 2.5s
                5.000,  # 5s
                10.000,  # 10s
            ),
            labelnames=["event_type", "status"],
            registry=self.registry,
        )

        # Event replay latency histogram
        self.ledger_replay_seconds = Histogram(
            "ledger_replay_seconds",
            "Time spent replaying events from ledger",
            buckets=(0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250, 0.500, 1.0, 2.5, 5.0),
            labelnames=["from_offset", "event_count"],
            registry=self.registry,
        )

        # Consumer processing lag gauge
        self.ledger_consumer_lag = Gauge(
            "ledger_consumer_lag",
            "Number of events behind the consumer is from latest",
            labelnames=["consumer_id", "handler_type"],
            registry=self.registry,
        )

        # Total events processed counter
        self.ledger_events_total = Counter(
            "ledger_events_total",
            "Total number of events processed by type",
            labelnames=["event_type", "status", "handler"],
            registry=self.registry,
        )

        # Event bus health gauge
        self.ledger_bus_health = Gauge(
            "ledger_bus_health",
            "Event bus health status (1=healthy, 0=unhealthy)",
            labelnames=["component"],
            registry=self.registry,
        )

        # Consumer error rate counter
        self.ledger_consumer_errors_total = Counter(
            "ledger_consumer_errors_total",
            "Total consumer processing errors",
            labelnames=["consumer_id", "error_type"],
            registry=self.registry,
        )

        # Database performance metrics
        self.ledger_db_operations_seconds = Histogram(
            "ledger_db_operations_seconds",
            "Database operation latency",
            buckets=(0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250),
            labelnames=["operation", "table"],
            registry=self.registry,
        )

        # Circuit breaker status
        self.ledger_circuit_breaker_status = Gauge(
            "ledger_circuit_breaker_status",
            "Circuit breaker status (0=closed, 1=open, 0.5=half_open)",
            labelnames=["component"],
            registry=self.registry,
        )

        # Dead letter queue size
        self.ledger_dead_letter_queue_size = Gauge(
            "ledger_dead_letter_queue_size", "Number of events in dead letter queue", registry=self.registry
        )

        # Performance alert thresholds
        self.ALERT_THRESHOLDS = {
            "consumer_lag_max": 1000,  # Alert if lag > 1000 events
            "append_p95_max_ms": 50,  # Alert if p95 append > 50ms
            "error_rate_max": 0.01,  # Alert if error rate > 1%
            "circuit_breaker_open": 1,  # Alert if circuit breaker open
        }

        logger.info("LedgerMetrics initialized with T4/0.01% excellence thresholds")

    def record_append_latency(self, duration_seconds: float, event_type: str, success: bool = True):
        """Record event append latency"""
        with self._lock:
            status = "success" if success else "error"
            self.ledger_append_seconds.labels(event_type=event_type, status=status).observe(duration_seconds)

            # Check T4 requirement
            duration_ms = duration_seconds * 1000
            if duration_ms > 50:
                logger.warning(f"Append latency {duration_ms:.2f}ms exceeds T4 requirement (50ms) for {event_type}")

    def record_replay_latency(self, duration_seconds: float, from_offset: int, event_count: int):
        """Record replay operation latency"""
        with self._lock:
            self.ledger_replay_seconds.labels(from_offset=str(from_offset), event_count=str(event_count)).observe(
                duration_seconds
            )

    def update_consumer_lag(self, consumer_id: str, handler_type: str, lag: int):
        """Update consumer lag metric"""
        with self._lock:
            self.ledger_consumer_lag.labels(consumer_id=consumer_id, handler_type=handler_type).set(lag)

            # Check alert threshold
            if lag > self.ALERT_THRESHOLDS["consumer_lag_max"]:
                logger.error(
                    f"ALERT: Consumer {consumer_id} lag {lag} exceeds threshold {self.ALERT_THRESHOLDS['consumer_lag_max']}"
                )

    def increment_events_processed(self, event_type: str, handler: str, success: bool = True):
        """Increment processed events counter"""
        with self._lock:
            status = "success" if success else "error"
            self.ledger_events_total.labels(event_type=event_type, status=status, handler=handler).inc()

    def record_consumer_error(self, consumer_id: str, error_type: str):
        """Record consumer processing error"""
        with self._lock:
            self.ledger_consumer_errors_total.labels(consumer_id=consumer_id, error_type=error_type).inc()

    def update_bus_health(self, component: str, healthy: bool):
        """Update event bus component health"""
        with self._lock:
            self.ledger_bus_health.labels(component=component).set(1 if healthy else 0)

    def record_db_operation(self, duration_seconds: float, operation: str, table: str):
        """Record database operation latency"""
        with self._lock:
            self.ledger_db_operations_seconds.labels(operation=operation, table=table).observe(duration_seconds)

    def update_circuit_breaker_status(self, component: str, state: str):
        """Update circuit breaker status"""
        state_values = {"closed": 0, "open": 1, "half_open": 0.5}
        value = state_values.get(state, 0)

        with self._lock:
            self.ledger_circuit_breaker_status.labels(component=component).set(value)

            if value == 1:  # Circuit breaker open
                logger.error(f"ALERT: Circuit breaker OPEN for component {component}")

    def update_dead_letter_queue_size(self, size: int):
        """Update dead letter queue size"""
        with self._lock:
            self.ledger_dead_letter_queue_size.set(size)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for T4 validation"""
        # Get current metric values (simplified - in production would query Prometheus)
        try:
            # Get append latency p95 (approximated from histogram buckets)
            append_histogram = self.ledger_append_seconds._value
            total_samples = sum(bucket.get() for bucket in append_histogram.values())

            if total_samples == 0:
                append_p95_ms = 0
            else:
                # Simple p95 approximation from buckets
                p95_threshold = total_samples * 0.95
                cumulative = 0
                append_p95_ms = 0

                for bucket_upper, counter in sorted(append_histogram.items()):
                    cumulative += counter.get()
                    if cumulative >= p95_threshold:
                        append_p95_ms = float(bucket_upper.replace("le", "").replace('"', "")) * 1000
                        break

            return {
                "append_p95_ms": append_p95_ms,
                "append_p95_meets_sla": append_p95_ms < self.ALERT_THRESHOLDS["append_p95_max_ms"],
                "total_events_processed": total_samples,
                "alert_thresholds": self.ALERT_THRESHOLDS,
                "metrics_healthy": True,
            }

        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {
                "append_p95_ms": -1,
                "append_p95_meets_sla": False,
                "total_events_processed": 0,
                "error": str(e),
                "metrics_healthy": False,
            }

    def generate_prometheus_metrics(self) -> str:
        """Generate Prometheus metrics text format"""
        return generate_latest(self.registry).decode("utf-8")

    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics HTTP server"""
        try:
            start_http_server(port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
            raise


# Global metrics instance
_global_metrics: Optional[LedgerMetrics] = None
_metrics_lock = threading.Lock()


def get_metrics() -> LedgerMetrics:
    """Get global metrics instance (singleton pattern)"""
    global _global_metrics

    with _metrics_lock:
        if _global_metrics is None:
            _global_metrics = LedgerMetrics()
        return _global_metrics


def reset_metrics():
    """Reset global metrics instance (for testing)"""
    global _global_metrics

    with _metrics_lock:
        _global_metrics = None


# Context managers for automatic metric recording
class MetricTimer:
    """Context manager for timing operations"""

    def __init__(self, metrics: LedgerMetrics, metric_func, *args, **kwargs):
        self.metrics = metrics
        self.metric_func = metric_func
        self.args = args
        self.kwargs = kwargs
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            success = exc_type is None
            self.metric_func(duration, *self.args, success=success, **self.kwargs)


def time_append_operation(event_type: str):
    """Context manager for timing append operations"""
    metrics = get_metrics()
    return MetricTimer(metrics, metrics.record_append_latency, event_type)


def time_replay_operation(from_offset: int, event_count: int):
    """Context manager for timing replay operations"""
    metrics = get_metrics()
    return MetricTimer(metrics, metrics.record_replay_latency, from_offset, event_count)


def time_db_operation(operation: str, table: str):
    """Context manager for timing database operations"""
    metrics = get_metrics()
    return MetricTimer(metrics, metrics.record_db_operation, operation, table)


# Health check utilities
def check_t4_compliance() -> Dict[str, Any]:
    """Check T4/0.01% excellence compliance"""
    metrics = get_metrics()
    summary = metrics.get_performance_summary()

    compliance_checks = {
        "append_p95_under_50ms": summary.get("append_p95_meets_sla", False),
        "metrics_collection_healthy": summary.get("metrics_healthy", False),
        "total_events_processed": summary.get("total_events_processed", 0),
    }

    all_checks_pass = all(compliance_checks.values())

    return {
        "t4_compliant": all_checks_pass,
        "checks": compliance_checks,
        "performance_summary": summary,
        "timestamp": time.time(),
    }
