#!/usr/bin/env python3
"""
LUKHAS Prometheus Metrics Integration
Enterprise-grade metrics collection and export for production monitoring.

Features:
- Custom LUKHAS metrics with proper labeling
- Memory system performance tracking
- MATRIZ orchestration monitoring
- Plugin system health metrics
- Automatic metric registration and collection
- HTTP endpoint for Prometheus scraping
"""

import os
import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, Info,
        CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
        start_http_server, push_to_gateway
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Mock classes for when Prometheus client is not available
    class MockMetric:
        def inc(self, amount=1, **labels): pass
        def dec(self, amount=1, **labels): pass
        def set(self, value, **labels): pass
        def observe(self, amount, **labels): pass
        def info(self, value, **labels): pass

    Counter = Histogram = Gauge = Summary = Info = MockMetric
    CollectorRegistry = None


def setup_metrics_endpoint(port: int = 8090) -> bool:
    """
    Set up Prometheus metrics HTTP endpoint.

    Args:
        port: Port to serve metrics on

    Returns:
        True if successfully started, False otherwise
    """
    if not PROMETHEUS_AVAILABLE:
        return False

    try:
        start_http_server(port)
        return True
    except Exception:
        return False


@dataclass
class MetricsConfig:
    """Configuration for Prometheus metrics collection"""
    enabled: bool = True
    namespace: str = "lukhas"
    subsystem: str = "ai"
    http_port: int = 8000
    push_gateway_url: Optional[str] = None
    push_job_name: str = "lukhas-ai"
    push_interval: int = 30  # seconds
    registry_name: str = "lukhas_registry"


class LUKHASMetrics:
    """
    Comprehensive Prometheus metrics for LUKHAS AI system.
    Provides enterprise-grade monitoring and alerting capabilities.
    """

    def __init__(self, config: Optional[MetricsConfig] = None):
        """
        Initialize LUKHAS Prometheus metrics.

        Args:
            config: Metrics configuration (uses defaults if None)
        """
        self.config = config or MetricsConfig()
        self.enabled = PROMETHEUS_AVAILABLE and self.config.enabled
        # ΛTAG: lane_labeling -- capture active lane for consistent metric labelling
        self.lane = os.getenv("LUKHAS_LANE", "experimental").lower()

        if not PROMETHEUS_AVAILABLE:
            print("Warning: Prometheus client not available. Metrics disabled.")
            return

        # Create custom registry
        self.registry = CollectorRegistry()

        # Initialize metric categories
        self._init_system_metrics()
        self._init_memory_metrics()
        self._init_matriz_metrics()
        self._init_plugin_metrics()
        self._init_observability_metrics()
        self._init_business_metrics()

        # Runtime state tracking
        self._start_time = time.time()
        self._request_counts = defaultdict(int)
        self._error_counts = defaultdict(int)
        self._latency_buffer = deque(maxlen=1000)

        # Background tasks
        self._push_thread = None
        self._stop_pushing = threading.Event()

        if self.config.push_gateway_url:
            self._start_push_gateway()

    def _init_system_metrics(self):
        """Initialize system-level metrics"""
        if not self.enabled:
            return

        # System health and uptime
        self.system_uptime = Gauge(
            "system_uptime_seconds",
            "System uptime in seconds",
            ["lane"],
            namespace=self.config.namespace,
            subsystem=self.config.subsystem,
            registry=self.registry,
        )

        self.system_info = Info(
            "system_info",
            "System information",
            ["lane"],
            namespace=self.config.namespace,
            subsystem=self.config.subsystem,
            registry=self.registry,
        )

        # Request and error tracking
        self.requests_total = Counter(
            "requests_total",
            "Total number of requests",
            ["endpoint", "method", "status", "lane"],
            namespace=self.config.namespace,
            subsystem=self.config.subsystem,
            registry=self.registry,
        )

        self.errors_total = Counter(
            "errors_total",
            "Total number of errors",
            ["component", "error_type", "lane"],
            namespace=self.config.namespace,
            subsystem=self.config.subsystem,
            registry=self.registry,
        )

        # Performance metrics
        self.response_time = Histogram(
            "response_time_seconds",
            "Response time distribution",
            ["endpoint", "method", "lane"],
            namespace=self.config.namespace,
            subsystem=self.config.subsystem,
            registry=self.registry,
        )

        self.active_connections = Gauge(
            "active_connections",
            "Number of active connections",
            ["lane"],
            namespace=self.config.namespace,
            subsystem=self.config.subsystem,
            registry=self.registry,
        )

    def _init_memory_metrics(self):
        """Initialize memory system metrics"""
        if not self.enabled:
            return

        # Memory operations
        self.memory_operations_total = Counter(
            "memory_operations_total",
            "Total memory operations",
            ["operation", "success", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.memory_recall_latency = Histogram(
            "memory_recall_latency_seconds",
            "Memory recall latency distribution",
            ["item_count_range", "success", "lane"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.memory_items_total = Gauge(
            "memory_items_total",
            "Total number of memory items",
            ["memory_type", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.memory_size_bytes = Gauge(
            "memory_size_bytes",
            "Memory usage in bytes",
            ["component", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        # Fold system metrics
        self.fold_operations_total = Counter(
            "fold_operations_total",
            "Total fold operations",
            ["operation", "success", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.fold_compression_ratio = Histogram(
            "fold_compression_ratio",
            "Fold compression ratio distribution",
            ["lane"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.active_folds = Gauge(
            "active_folds",
            "Number of active memory folds",
            ["status", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        # Compression metrics
        self.compression_operations_total = Counter(
            "compression_operations_total",
            "Total compression operations",
            ["algorithm", "result", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.compression_ratio = Histogram(
            "compression_ratio",
            "Compression ratio distribution",
            ["algorithm", "lane"],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.compression_speed_mbps = Gauge(
            "compression_speed_mbps",
            "Compression speed in MB/s",
            ["algorithm", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.compression_duration_ms = Histogram(
            "compression_duration_ms",
            "Compression operation duration",
            ["algorithm", "lane"],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.decompression_operations_total = Counter(
            "decompression_operations_total",
            "Total decompression operations",
            ["algorithm", "result", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.decompression_speed_mbps = Gauge(
            "decompression_speed_mbps",
            "Decompression speed in MB/s",
            ["algorithm", "lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.decompression_duration_ms = Histogram(
            "decompression_duration_ms",
            "Decompression operation duration",
            ["algorithm", "lane"],
            buckets=[0.5, 1, 2, 5, 10, 25, 50, 100, 250, 500],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        # Indexing metrics
        self.indexer_documents_indexed = Counter(
            "indexer_documents_indexed",
            "Total documents indexed",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_duplicates_detected = Counter(
            "indexer_duplicates_detected",
            "Total duplicate documents detected",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_embedding_errors = Counter(
            "indexer_embedding_errors",
            "Total embedding generation errors",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_errors = Counter(
            "indexer_errors",
            "Total indexer errors",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_document_processing_duration_ms = Histogram(
            "indexer_document_processing_duration_ms",
            "Document indexing processing time",
            ["lane"],
            buckets=[10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_batch_processing_duration_ms = Histogram(
            "indexer_batch_processing_duration_ms",
            "Batch indexing processing time",
            ["lane"],
            buckets=[100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_batch_processed = Counter(
            "indexer_batch_processed",
            "Total batches processed",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_batch_success_count = Gauge(
            "indexer_batch_success_count",
            "Number of successful documents in last batch",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.indexer_word_count = Gauge(
            "indexer_word_count",
            "Word count of last processed document",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        # Lifecycle management metrics
        self.lifecycle_cleanup_duration_ms = Histogram(
            "lifecycle_cleanup_duration_ms",
            "Document cleanup operation duration",
            ["lane"],
            buckets=[100, 500, 1000, 2500, 5000, 10000, 30000, 60000],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.lifecycle_documents_processed = Counter(
            "lifecycle_documents_processed",
            "Total documents processed in lifecycle operations",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.lifecycle_documents_deleted = Counter(
            "lifecycle_documents_deleted",
            "Total documents deleted by lifecycle manager",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.lifecycle_gdpr_requests_processed = Counter(
            "lifecycle_gdpr_requests_processed",
            "Total GDPR deletion requests processed",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

        self.lifecycle_gdpr_processing_duration_ms = Histogram(
            "lifecycle_gdpr_processing_duration_ms",
            "GDPR request processing duration",
            ["lane"],
            buckets=[100, 500, 1000, 5000, 10000, 30000, 60000, 300000],
            namespace=self.config.namespace,
            subsystem="memory",
            registry=self.registry,
        )

    def _init_matriz_metrics(self):
        """Initialize MATRIZ orchestration metrics"""
        if not self.enabled:
            return

        # Pipeline metrics
        self.matriz_pipeline_duration = Histogram(
            "matriz_pipeline_duration_seconds",
            "MATRIZ pipeline execution time",
            ["within_budget", "stages_completed", "lane"],
            buckets=[0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0, 2.0, 5.0],
            namespace=self.config.namespace,
            subsystem="matriz",
            registry=self.registry,
        )

        self.matriz_stage_duration = Histogram(
            "matriz_stage_duration_seconds",
            "MATRIZ stage execution time",
            ["stage", "success", "timeout", "lane"],
            buckets=[0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0],
            namespace=self.config.namespace,
            subsystem="matriz",
            registry=self.registry,
        )

        self.matriz_pipelines_total = Counter(
            "matriz_pipelines_total",
            "Total MATRIZ pipeline executions",
            ["success", "within_budget", "lane"],
            namespace=self.config.namespace,
            subsystem="matriz",
            registry=self.registry,
        )

        self.matriz_timeouts_total = Counter(
            "matriz_timeouts_total",
            "Total MATRIZ timeouts",
            ["stage", "lane"],
            namespace=self.config.namespace,
            subsystem="matriz",
            registry=self.registry,
        )

        # Node health metrics
        self.matriz_node_health = Gauge(
            "matriz_node_health",
            "MATRIZ node health score",
            ["node_name", "lane"],
            namespace=self.config.namespace,
            subsystem="matriz",
            registry=self.registry,
        )

        self.matriz_node_latency_p95 = Gauge(
            "matriz_node_latency_p95_seconds",
            "MATRIZ node 95th percentile latency",
            ["node_name", "lane"],
            namespace=self.config.namespace,
            subsystem="matriz",
            registry=self.registry,
        )

    def _init_plugin_metrics(self):
        """Initialize plugin system metrics"""
        if not self.enabled:
            return

        # Plugin operations
        self.plugin_operations_total = Counter(
            "plugin_operations_total",
            "Total plugin operations",
            ["operation", "success", "lane"],
            namespace=self.config.namespace,
            subsystem="plugins",
            registry=self.registry,
        )

        self.plugin_discovery_duration = Histogram(
            "plugin_discovery_duration_seconds",
            "Plugin discovery time",
            ["lane"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            namespace=self.config.namespace,
            subsystem="plugins",
            registry=self.registry,
        )

        self.plugins_registered = Gauge(
            "plugins_registered",
            "Number of registered plugins",
            ["category", "status", "lane"],
            namespace=self.config.namespace,
            subsystem="plugins",
            registry=self.registry,
        )

        self.plugin_instantiation_success_rate = Gauge(
            "plugin_instantiation_success_rate",
            "Plugin instantiation success rate",
            ["plugin_name", "lane"],
            namespace=self.config.namespace,
            subsystem="plugins",
            registry=self.registry,
        )

    def _init_observability_metrics(self):
        """Initialize observability and monitoring metrics"""
        if not self.enabled:
            return

        # Tracing metrics
        self.traces_exported_total = Counter(
            "traces_exported_total",
            "Total traces exported",
            ["exporter", "success", "lane"],
            namespace=self.config.namespace,
            subsystem="observability",
            registry=self.registry,
        )

        self.spans_created_total = Counter(
            "spans_created_total",
            "Total spans created",
            ["operation_type", "lane"],
            namespace=self.config.namespace,
            subsystem="observability",
            registry=self.registry,
        )

        # Metrics collection health
        self.metrics_collection_errors = Counter(
            "metrics_collection_errors_total",
            "Metrics collection errors",
            ["metric_name", "error_type", "lane"],
            namespace=self.config.namespace,
            subsystem="observability",
            registry=self.registry,
        )

        self.last_metrics_push = Gauge(
            "last_metrics_push_timestamp",
            "Timestamp of last metrics push",
            ["lane"],
            namespace=self.config.namespace,
            subsystem="observability",
            registry=self.registry,
        )

    def _init_business_metrics(self):
        """Initialize business KPI metrics"""
        if not self.enabled:
            return

        self.products_communications_total = Counter(
            "products_communications_total",
            "Total number of communications processed by products",
            ["product", "channel"],
            namespace=self.config.namespace,
            subsystem="business",
            registry=self.registry,
        )

        self.products_content_generated_total = Counter(
            "products_content_generated_total",
            "Total number of content items generated by products",
            ["product", "content_type"],
            namespace=self.config.namespace,
            subsystem="business",
            registry=self.registry,
        )

        self.products_user_feedback_rating = Histogram(
            "products_user_feedback_rating",
            "User feedback ratings for products",
            ["product"],
            namespace=self.config.namespace,
            subsystem="business",
            registry=self.registry,
            buckets=[1, 2, 3, 4, 5],
        )

    def record_system_info(self, info: Dict[str, str]):
        """Record system information"""
        if self.enabled:
            self.system_info.labels(lane=self.lane).info(info)

    def record_request(self, endpoint: str, method: str, status: str, duration: float):
        """Record HTTP request metrics"""
        if not self.enabled:
            return

        self.requests_total.labels(
            endpoint=endpoint,
            method=method,
            status=status,
            lane=self.lane,
        ).inc()
        self.response_time.labels(
            endpoint=endpoint,
            method=method,
            lane=self.lane,
        ).observe(duration)

        # Update runtime counters
        self._request_counts[f"{method}:{endpoint}"] += 1
        self._latency_buffer.append(duration)

    def record_error(self, component: str, error_type: str):
        """Record error occurrence"""
        if not self.enabled:
            return

        self.errors_total.labels(
            component=component,
            error_type=error_type,
            lane=self.lane,
        ).inc()
        self._error_counts[f"{component}:{error_type}"] += 1

    def record_memory_operation(
        self,
        operation: str,
        success: bool,
        latency: Optional[float] = None,
        item_count: Optional[int] = None,
    ):
        """Record memory system operation"""
        if not self.enabled:
            return

        self.memory_operations_total.labels(
            operation=operation,
            success=str(success),
            lane=self.lane,
        ).inc()

        if latency is not None and operation == "recall":
            # Categorize by item count range
            if item_count is not None:
                if item_count < 10:
                    range_label = "small"
                elif item_count < 100:
                    range_label = "medium"
                elif item_count < 1000:
                    range_label = "large"
                else:
                    range_label = "xlarge"
            else:
                range_label = "unknown"

            self.memory_recall_latency.labels(
                item_count_range=range_label,
                success=str(success),
                lane=self.lane,
            ).observe(latency)

    def record_memory_stats(self, items_by_type: Dict[str, int], size_by_component: Dict[str, int]):
        """Record memory system statistics"""
        if not self.enabled:
            return

        for memory_type, count in items_by_type.items():
            self.memory_items_total.labels(memory_type=memory_type, lane=self.lane).set(count)

        for component, size in size_by_component.items():
            self.memory_size_bytes.labels(component=component, lane=self.lane).set(size)

    def record_fold_operation(
        self,
        operation: str,
        success: bool,
        compression_ratio: Optional[float] = None,
        active_counts: Optional[Dict[str, int]] = None,
    ):
        """Record memory fold operation"""
        if not self.enabled:
            return

        self.fold_operations_total.labels(
            operation=operation,
            success=str(success),
            lane=self.lane,
        ).inc()

        if compression_ratio is not None:
            self.fold_compression_ratio.labels(lane=self.lane).observe(compression_ratio)

        if active_counts:
            for status, count in active_counts.items():
                self.active_folds.labels(status=status, lane=self.lane).set(count)

    def record_matriz_pipeline(
        self,
        duration: float,
        success: bool,
        within_budget: bool,
        stages_completed: int,
    ):
        """Record MATRIZ pipeline execution"""
        if not self.enabled:
            return

        self.matriz_pipelines_total.labels(
            success=str(success),
            within_budget=str(within_budget),
            lane=self.lane,
        ).inc()

        self.matriz_pipeline_duration.labels(
            within_budget=str(within_budget),
            stages_completed=str(min(stages_completed, 5)),  # Cap for cardinality
            lane=self.lane,
        ).observe(duration)

    def record_matriz_stage(
        self,
        stage: str,
        duration: float,
        success: bool,
        timeout: bool = False,
    ):
        """Record MATRIZ stage execution"""
        if not self.enabled:
            return

        self.matriz_stage_duration.labels(
            stage=stage,
            success=str(success),
            timeout=str(timeout),
            lane=self.lane,
        ).observe(duration)

        if timeout:
            self.matriz_timeouts_total.labels(stage=stage, lane=self.lane).inc()

    def record_matriz_node_health(self, node_name: str, health_score: float, p95_latency: float):
        """Record MATRIZ node health metrics"""
        if not self.enabled:
            return

        self.matriz_node_health.labels(node_name=node_name, lane=self.lane).set(health_score)
        self.matriz_node_latency_p95.labels(node_name=node_name, lane=self.lane).set(p95_latency)

    def record_plugin_operation(
        self,
        operation: str,
        success: bool,
        duration: Optional[float] = None,
        plugin_name: Optional[str] = None,
    ):
        """Record plugin system operation"""
        if not self.enabled:
            return

        self.plugin_operations_total.labels(
            operation=operation,
            success=str(success),
            lane=self.lane,
        ).inc()

        if operation == "discovery" and duration is not None:
            self.plugin_discovery_duration.labels(lane=self.lane).observe(duration)

        if plugin_name and operation == "instantiation":
            # Update success rate (simplified)
            current_rate = 1.0 if success else 0.0
            self.plugin_instantiation_success_rate.labels(
                plugin_name=plugin_name,
                lane=self.lane,
            ).set(current_rate)

    def record_plugin_stats(self, plugin_counts: Dict[str, Dict[str, int]]):
        """Record plugin registry statistics"""
        if not self.enabled:
            return

        for category, status_counts in plugin_counts.items():
            for status, count in status_counts.items():
                self.plugins_registered.labels(
                    category=category,
                    status=status,
                    lane=self.lane,
                ).set(count)

    def record_observability_operation(self, operation: str, component: str, success: bool):
        """Record observability system operation"""
        if not self.enabled:
            return

        if component == "tracing" and operation == "export":
            self.traces_exported_total.labels(
                exporter="otlp",
                success=str(success),
                lane=self.lane,
            ).inc()
        elif component == "tracing" and operation == "span_created":
            self.spans_created_total.labels(
                operation_type="lukhas",
                lane=self.lane,
            ).inc()

    def record_communication_processed(self, product: str, channel: str):
        """Record a communication processed by a product"""
        if self.enabled:
            self.products_communications_total.labels(product=product, channel=channel).inc()

    def record_content_generated(self, product: str, content_type: str):
        """Record a content item generated by a product"""
        if self.enabled:
            self.products_content_generated_total.labels(product=product, content_type=content_type).inc()

    def record_user_feedback(self, product: str, rating: float):
        """Record user feedback for a product"""
        if self.enabled:
            self.products_user_feedback_rating.labels(product=product).observe(rating)

    # Reliability metrics for 0.01% features
    def record_performance_regression(self, operation: str, metric: str, severity: str, degradation_percent: float):
        """Record performance regression detection"""
        if not self.enabled:
            return
        # Use existing error metric with additional labels
        self.errors_total.labels(
            component="performance_monitor",
            error_type=f"regression_{severity}",
            lane=self.lane,
        ).inc()

    def record_error_context(self, category: str, severity: str, operation: str, correlation_id: str):
        """Record error context capture"""
        if not self.enabled:
            return
        self.errors_total.labels(
            component="error_context",
            error_type=f"{category}_{severity}",
            lane=self.lane,
        ).inc()

    def record_timeout(self, operation: str, timeout_ms: float):
        """Record timeout event"""
        if not self.enabled:
            return
        self.errors_total.labels(
            component="timeout_manager",
            error_type="timeout",
            lane=self.lane,
        ).inc()

    def record_backoff_success(self, operation: str, attempts: int):
        """Record successful backoff operation"""
        if not self.enabled:
            return
        # Use existing request counter
        self.requests_total.labels(
            endpoint=operation,
            method="backoff",
            status="success",
            lane=self.lane,
        ).inc()

    def record_backoff_failure(self, operation: str, max_attempts: int):
        """Record failed backoff operation"""
        if not self.enabled:
            return
        self.errors_total.labels(
            component="backoff_manager",
            error_type="max_attempts_exceeded",
            lane=self.lane,
        ).inc()

    def update_system_uptime(self):
        """Update system uptime metric"""
        if self.enabled:
            uptime = time.time() - self._start_time
            self.system_uptime.labels(lane=self.lane).set(uptime)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics state"""
        if not self.enabled:
            return {"enabled": False, "reason": "Prometheus client not available"}

        uptime = time.time() - self._start_time
        avg_latency = sum(self._latency_buffer) / len(self._latency_buffer) if self._latency_buffer else 0

        return {
            "enabled": True,
            "uptime_seconds": uptime,
            "total_requests": sum(self._request_counts.values()),
            "total_errors": sum(self._error_counts.values()),
            "avg_latency_seconds": avg_latency,
            "metrics_registry": self.config.registry_name,
            "push_gateway_enabled": self.config.push_gateway_url is not None,
        }

    def start_http_server(self, port: Optional[int] = None) -> bool:
        """Start HTTP server for Prometheus scraping"""
        if not self.enabled:
            return False

        try:
            server_port = port or self.config.http_port
            start_http_server(server_port, registry=self.registry)
            print(f"Prometheus metrics server started on port {server_port}")
            return True
        except Exception as e:
            print(f"Failed to start metrics server: {e}")
            return False

    def _start_push_gateway(self):
        """Start background push to Prometheus push gateway"""
        if not self.enabled or not self.config.push_gateway_url:
            return

        def push_worker():
            while not self._stop_pushing.wait(self.config.push_interval):
                try:
                    push_to_gateway(
                        self.config.push_gateway_url,
                        job=self.config.push_job_name,
                        registry=self.registry,
                    )
                    if self.enabled:
                        self.last_metrics_push.labels(lane=self.lane).set(time.time())
                except Exception as e:
                    print(f"Failed to push metrics: {e}")
                    if self.enabled:
                        self.metrics_collection_errors.labels(
                            metric_name="push_gateway",
                            error_type=type(e).__name__,
                            lane=self.lane,
                        ).inc()

        self._push_thread = threading.Thread(target=push_worker, daemon=True)
        self._push_thread.start()

    def shutdown(self):
        """Shutdown metrics collection and push gateway"""
        if self._push_thread:
            self._stop_pushing.set()
            self._push_thread.join(timeout=5)

    def get_metrics_export(self) -> str:
        """Get metrics in Prometheus format for manual export"""
        if not self.enabled:
            return "# Prometheus client not available\n"

        return generate_latest(self.registry).decode('utf-8')


# Global metrics instance
_lukhas_metrics: Optional[LUKHASMetrics] = None


def initialize_metrics(config: Optional[MetricsConfig] = None) -> LUKHASMetrics:
    """Initialize global LUKHAS metrics"""
    global _lukhas_metrics
    _lukhas_metrics = LUKHASMetrics(config)
    return _lukhas_metrics


def get_lukhas_metrics() -> LUKHASMetrics:
    """Get or create global LUKHAS metrics instance"""
    global _lukhas_metrics
    if _lukhas_metrics is None:
        _lukhas_metrics = initialize_metrics()
    return _lukhas_metrics


def shutdown_metrics():
    """Shutdown global metrics collection"""
    global _lukhas_metrics
    if _lukhas_metrics:
        _lukhas_metrics.shutdown()
        _lukhas_metrics = None