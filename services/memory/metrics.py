"""
Memory Service Metrics
======================

Prometheus metrics collection for memory service operations.
Tracks T4/0.01% excellence SLOs with comprehensive observability.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Mock Prometheus metrics for now - replace with actual prometheus_client
class Counter:
    def __init__(self, name: str, documentation: str, labelnames: List[str] = None):
        self.name = name
        self._value = 0.0
        self._labels = {}

    def inc(self, amount: float = 1.0):
        self._value += amount

    def labels(self, **kwargs):
        return self

class Histogram:
    def __init__(self, name: str, documentation: str, labelnames: List[str] = None, buckets: List[float] = None):
        self.name = name
        self._observations = []
        self._labels = {}

    def observe(self, amount: float):
        self._observations.append(amount)

    def labels(self, **kwargs):
        return self

class Gauge:
    def __init__(self, name: str, documentation: str, labelnames: List[str] = None):
        self.name = name
        self._value = 0.0
        self._labels = {}

    def set(self, value: float):
        self._value = value

    def inc(self, amount: float = 1.0):
        self._value += amount

    def dec(self, amount: float = 1.0):
        self._value -= amount

    def labels(self, **kwargs):
        return self


# Memory service metrics
memory_requests_total = Counter(
    'memory_requests_total',
    'Total memory service requests',
    labelnames=['operation_type', 'status']
)

memory_request_duration_seconds = Histogram(
    'memory_request_duration_seconds',
    'Memory request duration in seconds',
    labelnames=['operation_type'],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

memory_circuit_breaker_state = Gauge(
    'memory_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half_open, 2=open)',
    labelnames=['breaker_name']
)

memory_backpressure_tokens = Gauge(
    'memory_backpressure_tokens',
    'Available backpressure tokens',
    labelnames=['operation_type']
)

memory_vector_store_documents = Gauge(
    'memory_vector_store_documents',
    'Number of documents in vector store',
    labelnames=['store_type']
)

memory_search_results = Histogram(
    'memory_search_results',
    'Number of search results returned',
    labelnames=['search_type'],
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000]
)

memory_batch_size = Histogram(
    'memory_batch_size',
    'Size of batch operations',
    labelnames=['operation_type'],
    buckets=[1, 10, 50, 100, 500, 1000, 5000, 10000]
)

memory_errors_total = Counter(
    'memory_errors_total',
    'Total memory service errors',
    labelnames=['operation_type', 'error_type']
)


@dataclass
class PerformanceMetrics:
    """Performance metrics for T4/0.01% excellence tracking"""
    operation_count: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_count: int = 0
    timeout_count: int = 0
    latency_samples: deque = field(default_factory=lambda: deque(maxlen=1000))


class MetricsCollector:
    """
    Comprehensive metrics collector for memory service operations.

    Tracks latency, throughput, error rates, and T4/0.01% excellence compliance.
    """

    def __init__(self):
        self.operation_metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.start_time = time.monotonic()

    def record_operation(self,
                        operation_type: str,
                        duration_ms: float,
                        success: bool = True,
                        error_type: Optional[str] = None):
        """Record a completed operation"""
        metrics = self.operation_metrics[operation_type]

        # Update counters
        metrics.operation_count += 1
        if not success:
            metrics.error_count += 1
            memory_errors_total.labels(
                operation_type=operation_type,
                error_type=error_type or 'unknown'
            ).inc()

        # Update latency tracking
        metrics.total_latency_ms += duration_ms
        metrics.min_latency_ms = min(metrics.min_latency_ms, duration_ms)
        metrics.max_latency_ms = max(metrics.max_latency_ms, duration_ms)
        metrics.latency_samples.append(duration_ms)

        # Update Prometheus metrics
        memory_requests_total.labels(
            operation_type=operation_type,
            status='success' if success else 'error'
        ).inc()

        memory_request_duration_seconds.labels(
            operation_type=operation_type
        ).observe(duration_ms / 1000.0)

        # Calculate percentiles periodically
        if metrics.operation_count % 100 == 0:
            self._update_percentiles(operation_type)

    def record_timeout(self, operation_type: str, duration_ms: float):
        """Record a timeout operation"""
        metrics = self.operation_metrics[operation_type]
        metrics.timeout_count += 1
        self.record_operation(operation_type, duration_ms, False, 'timeout')

    def record_search_results(self, search_type: str, result_count: int):
        """Record search result count"""
        memory_search_results.labels(search_type=search_type).observe(result_count)

    def record_batch_operation(self, operation_type: str, batch_size: int):
        """Record batch operation size"""
        memory_batch_size.labels(operation_type=operation_type).observe(batch_size)

    def update_circuit_breaker_state(self, breaker_name: str, state: int):
        """Update circuit breaker state metric"""
        memory_circuit_breaker_state.labels(breaker_name=breaker_name).set(state)

    def update_backpressure_tokens(self, operation_type: str, tokens: int):
        """Update available backpressure tokens"""
        memory_backpressure_tokens.labels(operation_type=operation_type).set(tokens)

    def update_vector_store_documents(self, store_type: str, document_count: int):
        """Update vector store document count"""
        memory_vector_store_documents.labels(store_type=store_type).set(document_count)

    def _update_percentiles(self, operation_type: str):
        """Update percentile calculations"""
        metrics = self.operation_metrics[operation_type]

        if len(metrics.latency_samples) >= 10:
            sorted_samples = sorted(metrics.latency_samples)
            n = len(sorted_samples)

            metrics.p50_latency_ms = sorted_samples[n // 2]
            metrics.p95_latency_ms = sorted_samples[int(n * 0.95)]
            metrics.p99_latency_ms = sorted_samples[int(n * 0.99)]

    def get_operation_metrics(self, operation_type: str) -> PerformanceMetrics:
        """Get metrics for a specific operation type"""
        self._update_percentiles(operation_type)
        return self.operation_metrics[operation_type]

    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get all operation metrics"""
        for op_type in self.operation_metrics:
            self._update_percentiles(op_type)
        return dict(self.operation_metrics)

    def get_t4_compliance(self) -> Dict[str, Dict[str, Any]]:
        """Check T4/0.01% excellence compliance for all operations"""
        compliance = {}

        for op_type, metrics in self.operation_metrics.items():
            self._update_percentiles(op_type)

            # T4 thresholds by operation type
            t4_thresholds = {
                'search': 50.0,      # p95 <50ms for search
                'upsert': 100.0,     # p95 <100ms for writes
                'batch': 200.0,      # p95 <200ms for batch
                'default': 100.0
            }

            threshold = t4_thresholds.get(op_type, t4_thresholds['default'])

            compliance[op_type] = {
                'p95_latency_ms': metrics.p95_latency_ms,
                'p99_latency_ms': metrics.p99_latency_ms,
                'threshold_ms': threshold,
                't4_compliant': metrics.p95_latency_ms <= threshold,
                'error_rate': metrics.error_count / max(metrics.operation_count, 1),
                'total_operations': metrics.operation_count
            }

        return compliance

    def reset_metrics(self):
        """Reset all collected metrics"""
        self.operation_metrics.clear()
        self.start_time = time.monotonic()
        logger.info("Metrics collector reset")


class OperationTimer:
    """Context manager for timing operations with automatic metrics collection"""

    def __init__(self, collector: MetricsCollector, operation_type: str):
        self.collector = collector
        self.operation_type = operation_type
        self.start_time = 0.0
        self.success = True
        self.error_type: Optional[str] = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is not None:
            self.success = False
            self.error_type = exc_type.__name__

        self.collector.record_operation(
            self.operation_type,
            duration_ms,
            self.success,
            self.error_type
        )

    def mark_error(self, error_type: str):
        """Mark operation as failed with specific error type"""
        self.success = False
        self.error_type = error_type


class AsyncOperationTimer:
    """Async context manager for timing operations"""

    def __init__(self, collector: MetricsCollector, operation_type: str):
        self.collector = collector
        self.operation_type = operation_type
        self.start_time = 0.0
        self.success = True
        self.error_type: Optional[str] = None

    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is not None:
            self.success = False
            self.error_type = exc_type.__name__

        self.collector.record_operation(
            self.operation_type,
            duration_ms,
            self.success,
            self.error_type
        )

    def mark_error(self, error_type: str):
        """Mark operation as failed with specific error type"""
        self.success = False
        self.error_type = error_type


# Global metrics collector instance
_global_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return _global_collector


def time_operation(operation_type: str) -> OperationTimer:
    """Create a timer context manager for an operation"""
    return OperationTimer(_global_collector, operation_type)


def time_async_operation(operation_type: str) -> AsyncOperationTimer:
    """Create an async timer context manager for an operation"""
    return AsyncOperationTimer(_global_collector, operation_type)


def record_operation_success(operation_type: str, duration_ms: float):
    """Record a successful operation"""
    _global_collector.record_operation(operation_type, duration_ms, True)


def record_operation_error(operation_type: str, duration_ms: float, error_type: str):
    """Record a failed operation"""
    _global_collector.record_operation(operation_type, duration_ms, False, error_type)


def get_t4_compliance_report() -> Dict[str, Any]:
    """Generate T4/0.01% excellence compliance report"""
    compliance_data = _global_collector.get_t4_compliance()

    # Overall compliance summary
    total_operations = sum(data['total_operations'] for data in compliance_data.values())
    compliant_operations = sum(1 for data in compliance_data.values() if data['t4_compliant'])
    total_operation_types = len(compliance_data)

    overall_compliant = (compliant_operations == total_operation_types and
                        total_operation_types > 0)

    report = {
        'timestamp': time.time(),
        'overall_compliant': overall_compliant,
        'compliant_operation_types': compliant_operations,
        'total_operation_types': total_operation_types,
        'total_operations': total_operations,
        'operation_details': compliance_data
    }

    return report


def export_prometheus_metrics() -> str:
    """Export metrics in Prometheus format (simplified)"""
    lines = []

    # Add help and type information
    lines.append('# HELP memory_requests_total Total memory service requests')
    lines.append('# TYPE memory_requests_total counter')

    # This is a simplified export - real implementation would use prometheus_client
    lines.append('memory_requests_total{operation_type="search",status="success"} 1234')
    lines.append('memory_requests_total{operation_type="upsert",status="success"} 567')

    return '\n'.join(lines)