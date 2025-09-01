#!/usr/bin/env python3
"""
Wave C C5 Observability Integration
===================================

Prometheus metrics, monitoring dashboards, and alerting for the Aka Qualia
phenomenological processing pipeline.

Provides comprehensive observability for:
- Memory system performance and health
- Consciousness processing metrics
- GLYPH mapping effectiveness
- Router dispatch performance
- Oneiric feedback quality
"""

import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
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

    # Stub classes for when Prometheus is not available
    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, amount=1, labels=None):
            pass

        def labels(self, **labels):
            return self

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, amount, labels=None):
            pass

        def time(self):
            return lambda f: f

        def labels(self, **labels):
            return self

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, value, labels=None):
            pass

        def inc(self, amount=1):
            pass

        def dec(self, amount=1):
            pass

        def labels(self, **labels):
            return self

    class Info:
        def __init__(self, *args, **kwargs):
            pass

        def info(self, labels):
            pass

    CollectorRegistry = None

    def generate_latest(r):
        return b"# Prometheus not available\n"

    CONTENT_TYPE_LATEST = "text/plain"


@dataclass
class AkaqMetrics:
    """Structured metrics for Aka Qualia consciousness processing"""

    drift_phi: float = 0.0
    congruence_index: float = 1.0
    neurosis_risk: float = 0.0
    regulation_intensity: float = 0.0
    glyph_coverage: float = 1.0
    router_priority: float = 0.5
    memory_efficiency: float = 1.0
    dream_coherence: float = 1.0


class AkaqObservability:
    """
    Comprehensive observability system for Wave C Aka Qualia processing.

    Provides Prometheus metrics, health monitoring, and performance tracking
    for all components of the consciousness pipeline.
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize observability system"""
        self.enabled = PROMETHEUS_AVAILABLE
        self.registry = registry or (CollectorRegistry() if PROMETHEUS_AVAILABLE else None)
        self._local_data = {}  # For when Prometheus is not available

        if self.enabled:
            self._init_prometheus_metrics()
        else:
            print("⚠️  Prometheus not available - metrics will be collected locally only")

    def _init_prometheus_metrics(self):
        """Initialize all Prometheus metrics"""

        # Scene Processing Metrics
        self.scenes_processed_total = Counter(
            "akaq_scenes_processed_total",
            "Total number of phenomenological scenes processed",
            ["user_tier", "processing_mode", "status"],
            registry=self.registry,
        )

        self.scene_processing_duration = Histogram(
            "akaq_scene_processing_duration_seconds",
            "Time spent processing phenomenological scenes",
            ["stage", "complexity"],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
        )

        # GLYPH Mapping Metrics
        self.glyphs_mapped_total = Counter(
            "akaq_glyphs_mapped_total",
            "Total number of phenomenological glyphs mapped",
            ["glyph_type", "cache_status"],
            registry=self.registry,
        )

        self.glyph_mapping_accuracy = Histogram(
            "akaq_glyph_mapping_accuracy_ratio",
            "Accuracy ratio of GLYPH mapping (0.0-1.0)",
            ["palette_bias"],
            registry=self.registry,
            buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 0.99, 1.0],
        )

        # Memory System Metrics
        self.memory_operations_total = Counter(
            "akaq_memory_operations_total",
            "Total number of memory operations",
            ["operation", "client_type", "status"],
            registry=self.registry,
        )

        self.memory_operation_duration = Histogram(
            "akaq_memory_operation_duration_seconds",
            "Duration of memory operations",
            ["operation", "client_type"],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
        )

        self.memory_storage_bytes = Gauge(
            "akaq_memory_storage_bytes",
            "Total bytes stored in memory system",
            ["client_type", "data_type"],
            registry=self.registry,
        )

        # Router Performance Metrics
        self.router_dispatches_total = Counter(
            "akaq_router_dispatches_total",
            "Total number of router dispatches",
            ["priority_tier", "route_type", "status"],
            registry=self.registry,
        )

        self.router_queue_depth = Gauge(
            "akaq_router_queue_depth", "Current depth of router queue", ["priority_tier"], registry=self.registry
        )

        # Consciousness Quality Metrics
        self.consciousness_drift_phi = Gauge(
            "akaq_consciousness_drift_phi", "Current consciousness drift phi value", ["user_id"], registry=self.registry
        )

        self.consciousness_congruence = Gauge(
            "akaq_consciousness_congruence_index",
            "Consciousness congruence index (0.0-1.0)",
            ["processing_stage"],
            registry=self.registry,
        )

        self.neurosis_risk_level = Gauge(
            "akaq_neurosis_risk_level", "Current neurosis risk assessment", ["risk_category"], registry=self.registry
        )

        # Oneiric Processing Metrics
        self.dreams_generated_total = Counter(
            "akaq_dreams_generated_total",
            "Total number of dreams generated",
            ["dream_type", "trigger_source"],
            registry=self.registry,
        )

        self.dream_coherence_score = Histogram(
            "akaq_dream_coherence_score",
            "Coherence score of generated dreams",
            ["dream_type"],
            registry=self.registry,
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )

        # System Health Metrics
        self.system_health_status = Gauge(
            "akaq_system_health_status",
            "Overall system health status (0=unhealthy, 1=healthy)",
            ["component"],
            registry=self.registry,
        )

        # Component Information
        self.component_info = Info("akaq_component_info", "Information about Wave C components", registry=self.registry)

        # Set component information
        self.component_info.info(
            {
                "version": "1.0.0",
                "wave": "C",
                "architecture": "phenomenological_processing",
                "spec": "freud_2025",
                "constellation_framework": "identity_consciousness_guardian",
            }
        )

    @contextmanager
    def measure_scene_processing(self, stage: str, complexity: str = "normal"):
        """Context manager for measuring scene processing duration"""
        if not self.enabled:
            yield
            return

        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.scene_processing_duration.labels(stage=stage, complexity=complexity).observe(duration)

    @contextmanager
    def measure_memory_operation(self, operation: str, client_type: str = "unknown"):
        """Context manager for measuring memory operation duration"""
        if not self.enabled:
            yield
            return

        start_time = time.time()
        status = "success"
        try:
            yield
        except Exception:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            self.memory_operation_duration.labels(operation=operation, client_type=client_type).observe(duration)
            self.memory_operations_total.labels(operation=operation, client_type=client_type, status=status).inc()

    def record_scene_processed(
        self, user_tier: str = "standard", processing_mode: str = "normal", status: str = "success"
    ):
        """Record that a phenomenological scene was processed"""
        if self.enabled:
            self.scenes_processed_total.labels(
                user_tier=user_tier, processing_mode=processing_mode, status=status
            ).inc()
        else:
            key = f"scenes_{user_tier}_{processing_mode}_{status}"
            self._local_data[key] = self._local_data.get(key, 0) + 1

    def record_glyph_mapped(
        self, glyph_type: str, cache_status: str = "miss", accuracy: float = 1.0, palette_bias: str = "neutral"
    ):
        """Record GLYPH mapping with accuracy"""
        if self.enabled:
            self.glyphs_mapped_total.labels(glyph_type=glyph_type, cache_status=cache_status).inc()
            self.glyph_mapping_accuracy.labels(palette_bias=palette_bias).observe(accuracy)
        else:
            key = f"glyphs_{glyph_type}_{cache_status}"
            self._local_data[key] = self._local_data.get(key, 0) + 1
            self._local_data[f"glyph_accuracy_{palette_bias}"] = accuracy

    def record_router_dispatch(
        self, priority_tier: str, route_type: str = "standard", status: str = "success", queue_depth: int = 0
    ):
        """Record router dispatch event"""
        if self.enabled:
            self.router_dispatches_total.labels(priority_tier=priority_tier, route_type=route_type, status=status).inc()
            self.router_queue_depth.labels(priority_tier=priority_tier).set(queue_depth)
        else:
            key = f"router_{priority_tier}_{route_type}_{status}"
            self._local_data[key] = self._local_data.get(key, 0) + 1
            self._local_data[f"router_queue_{priority_tier}"] = queue_depth

    def update_consciousness_metrics(self, metrics: AkaqMetrics, user_id: str = "anonymous"):
        """Update consciousness quality metrics"""
        if self.enabled:
            # Hash user_id for privacy in metrics
            import hashlib

            user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]

            self.consciousness_drift_phi.labels(user_id=user_hash).set(metrics.drift_phi)
            self.consciousness_congruence.labels(processing_stage="current").set(metrics.congruence_index)
            self.neurosis_risk_level.labels(risk_category="general").set(metrics.neurosis_risk)
        else:
            self._local_data["drift_phi"] = metrics.drift_phi
            self._local_data["congruence_index"] = metrics.congruence_index
            self._local_data["neurosis_risk"] = metrics.neurosis_risk

    def record_dream_generated(self, dream_type: str, trigger_source: str = "regulation", coherence_score: float = 1.0):
        """Record dream generation event"""
        if self.enabled:
            self.dreams_generated_total.labels(dream_type=dream_type, trigger_source=trigger_source).inc()
            self.dream_coherence_score.labels(dream_type=dream_type).observe(coherence_score)
        else:
            key = f"dreams_{dream_type}_{trigger_source}"
            self._local_data[key] = self._local_data.get(key, 0) + 1
            self._local_data[f"dream_coherence_{dream_type}"] = coherence_score

    def update_system_health(self, component: str, healthy: bool):
        """Update system health status for a component"""
        if self.enabled:
            self.system_health_status.labels(component=component).set(1 if healthy else 0)
        else:
            self._local_data[f"health_{component}"] = 1 if healthy else 0

    def update_memory_storage(self, client_type: str, data_type: str, bytes_stored: int):
        """Update memory storage metrics"""
        if self.enabled:
            self.memory_storage_bytes.labels(client_type=client_type, data_type=data_type).set(bytes_stored)
        else:
            self._local_data[f"storage_{client_type}_{data_type}"] = bytes_stored

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of current metrics"""
        if self.enabled:
            return {
                "prometheus_enabled": True,
                "registry_metrics": len(list(self.registry.collect())),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            return {
                "prometheus_enabled": False,
                "local_metrics": len(self._local_data),
                "local_data": dict(self._local_data),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def export_prometheus_metrics(self) -> bytes:
        """Export metrics in Prometheus format"""
        if self.enabled and self.registry:
            return generate_latest(self.registry)
        else:
            # Return local metrics in Prometheus-like format
            output = []
            output.append("# Wave C Aka Qualia Metrics (Local Mode)")
            output.append(f"# Timestamp: {datetime.now(timezone.utc).isoformat()}")

            for key, value in self._local_data.items():
                output.append(f"akaq_{key} {value}")

            return "\n".join(output).encode("utf-8")

    def health_check(self) -> dict[str, Any]:
        """Comprehensive health check of observability system"""
        health = {
            "observability_enabled": self.enabled,
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.enabled:
            health.update(
                {
                    "registry_active": self.registry is not None,
                    "metrics_count": len(list(self.registry.collect())) if self.registry else 0,
                }
            )
        else:
            health.update({"local_metrics_count": len(self._local_data), "fallback_mode": "local_storage"})

        return health


# Global observability instance
_observability_instance: Optional[AkaqObservability] = None
_observability_lock = threading.Lock()


def get_observability() -> AkaqObservability:
    """Get global observability instance (singleton)"""
    global _observability_instance

    if _observability_instance is None:
        with _observability_lock:
            if _observability_instance is None:
                _observability_instance = AkaqObservability()

    return _observability_instance


def configure_observability(registry: Optional[CollectorRegistry] = None) -> AkaqObservability:
    """Configure global observability instance"""
    global _observability_instance

    with _observability_lock:
        _observability_instance = AkaqObservability(registry=registry)

    return _observability_instance


# Convenience functions for common operations
def measure_scene_processing(stage: str, complexity: str = "normal"):
    """Decorator/context manager for measuring scene processing"""
    return get_observability().measure_scene_processing(stage, complexity)


def measure_memory_operation(operation: str, client_type: str = "unknown"):
    """Decorator/context manager for measuring memory operations"""
    return get_observability().measure_memory_operation(operation, client_type)


def record_scene_processed(**kwargs):
    """Record scene processing event"""
    return get_observability().record_scene_processed(**kwargs)


def record_glyph_mapped(**kwargs):
    """Record GLYPH mapping event"""
    return get_observability().record_glyph_mapped(**kwargs)


def update_consciousness_metrics(metrics: AkaqMetrics, user_id: str = "anonymous"):
    """Update consciousness quality metrics"""
    return get_observability().update_consciousness_metrics(metrics, user_id)


if __name__ == "__main__":
    # Demo usage
    obs = get_observability()

    print("🔍 Wave C C5 Observability Demo")
    print(f"Prometheus available: {PROMETHEUS_AVAILABLE}")

    # Simulate some metrics
    with obs.measure_scene_processing("glyph_mapping", "complex"):
        time.sleep(0.01)  # Simulate processing

    obs.record_scene_processed(status="success")
    obs.record_glyph_mapped("vigilance", accuracy=0.95, palette_bias="aka_bias")
    obs.record_router_dispatch("high", status="success", queue_depth=3)

    metrics = AkaqMetrics(drift_phi=0.1, congruence_index=0.9, neurosis_risk=0.05)
    obs.update_consciousness_metrics(metrics)

    obs.record_dream_generated("regulation", coherence_score=0.8)
    obs.update_system_health("memory", True)
    obs.update_memory_storage("sql", "scenes", 1024000)

    # Print summary
    summary = obs.get_metrics_summary()
    print(f"📊 Metrics Summary: {summary}")

    # Print health check
    health = obs.health_check()
    print(f"🏥 Health Check: {health}")

    print("✅ Observability demo completed")
