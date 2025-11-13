"""
Prometheus metrics for the LUKHAS Memory system.

This module provides a centralized place for defining and reporting
Prometheus metrics related to the memory subsystem's performance and health.
It tracks key indicators such as fold operations, recall latency, cache
performance, and storage size.

Metrics are registered with the central LUKHAS_REGISTRY.
"""
from __future__ import annotations

import logging

# Use a try-except block to mock the prometheus_registry for tests
# and environments where it might not be available.
try:
    from lukhas.observability.prometheus_registry import counter, gauge, histogram
except ImportError:
    # This mock allows the code to be imported and type-checked even if the
    # observability stack is not fully available.
    logging.warning(
        "Could not import from lukhas.observability.prometheus_registry. "
        "Using mock metrics for memory system."
    )

    class _MockMetric:
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass

    _mock_metric_instance = _MockMetric()

    def counter(name, documentation, labelnames=None):
        return _mock_metric_instance

    def gauge(name, documentation, labelnames=None):
        return _mock_metric_instance

    def histogram(name, documentation, labelnames=None, buckets=None):
        return _mock_metric_instance

# --- Metric Definitions ---

# Counter for fold operations
MEMORY_FOLD_OPERATIONS_TOTAL = counter(
    "lukhas_memory_fold_operations_total",
    "Total number of memory fold operations.",
    ["tenant_id", "operation_type"],  # e.g., 'add', 'compact'
)

# Histogram for recall latency
MEMORY_RECALL_LATENCY_SECONDS = histogram(
    "lukhas_memory_recall_latency_seconds",
    "Latency of memory recall operations.",
    ["tenant_id", "index_type"],  # e.g., 'vector', 'keyword'
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Counters for cache hits and misses
MEMORY_CACHE_HITS_TOTAL = counter(
    "lukhas_memory_cache_hits_total",
    "Total number of cache hits in the memory system.",
    ["tenant_id", "cache_type"],  # e.g., 'embedding', 'query'
)

MEMORY_CACHE_MISSES_TOTAL = counter(
    "lukhas_memory_cache_misses_total",
    "Total number of cache misses in the memory system.",
    ["tenant_id", "cache_type"],
)

# Gauge for cache hit rate
MEMORY_CACHE_HIT_RATE = gauge(
    "lukhas_memory_cache_hit_rate",
    "The hit rate of the memory system cache.",
    ["tenant_id", "cache_type"],
)

# Gauge for storage size
MEMORY_STORAGE_SIZE_BYTES = gauge(
    "lukhas_memory_storage_size_bytes",
    "The total size of the memory store in bytes.",
    ["tenant_id", "storage_type"],  # e.g., 'index', 'documents'
)

# --- Metric Update Functions ---

def record_fold_operation(tenant_id: str, operation_type: str):
    """Records a fold operation."""
    MEMORY_FOLD_OPERATIONS_TOTAL.labels(tenant_id=tenant_id, operation_type=operation_type).inc()

def record_recall_latency(tenant_id: str, index_type: str, duration_seconds: float):
    """Records the latency of a recall operation."""
    MEMORY_RECALL_LATENCY_SECONDS.labels(tenant_id=tenant_id, index_type=index_type).observe(duration_seconds)

def record_cache_hit(tenant_id: str, cache_type: str):
    """Records a cache hit."""
    MEMORY_CACHE_HITS_TOTAL.labels(tenant_id=tenant_id, cache_type=cache_type).inc()

def record_cache_miss(tenant_id: str, cache_type: str):
    """Records a cache miss."""
    MEMORY_CACHE_MISSES_TOTAL.labels(tenant_id=tenant_id, cache_type=cache_type).inc()

def update_cache_hit_rate(tenant_id: str, cache_type: str, hit_rate: float):
    """Updates the cache hit rate gauge."""
    MEMORY_CACHE_HIT_RATE.labels(tenant_id=tenant_id, cache_type=cache_type).set(hit_rate)

def update_storage_size(tenant_id: str, storage_type: str, size_bytes: int):
    """Updates the storage size gauge."""
    MEMORY_STORAGE_SIZE_BYTES.labels(tenant_id=tenant_id, storage_type=storage_type).set(size_bytes)
