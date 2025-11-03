#!/usr/bin/env python3
"""
LUKHAS Advanced Telemetry & Observability System

Enterprise-grade telemetry system with real-time metrics, distributed tracing,
health monitoring, and performance analytics across all LUKHAS components.

# ΛTAG: telemetry_system, observability, real_time_monitoring, enterprise_metrics
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional Prometheus integration
try:
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback implementations
    class Counter:
        def __init__(self, *args, **kwargs):
            self.value = 0
        def inc(self, amount=1):
            self.value += amount
        def labels(self, **kwargs):
            return self

    class Histogram:
        def __init__(self, *args, **kwargs):
            self.observations = []
        def observe(self, value):
            self.observations.append(value)
        def labels(self, **kwargs):
            return self

    class Gauge:
        def __init__(self, *args, **kwargs):
            self.value = 0
        def set(self, value):
            self.value = value
        def labels(self, **kwargs):
            return self


class MetricType(Enum):
    """Types of telemetry metrics."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    TIMER = "timer"
    EVENT = "event"


class SeverityLevel(Enum):
    """Severity levels for telemetry events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TelemetryEvent:
    """Structured telemetry event."""

    event_id: str
    timestamp: float
    component: str
    event_type: str
    severity: SeverityLevel
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "component": self.component,
            "event_type": self.event_type,
            "severity": self.severity.value,
            "message": self.message,
            "data": self.data,
            "tags": self.tags,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }


@dataclass
class MetricData:
    """Structured metric data."""

    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: float
    component: str
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "component": self.component,
            "tags": self.tags
        }


@dataclass
class TraceSpan:
    """Distributed tracing span."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    component: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"  # active, completed, error

    def finish(self) -> None:
        """Finish the span and calculate duration."""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration_ms = (self.end_time - self.start_time) * 1000
            self.status = "completed"

    def add_log(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add log entry to span."""
        log_entry = {
            "timestamp": time.time(),
            "message": message,
            "data": data or {}
        }
        self.logs.append(log_entry)

    def set_error(self, error: str) -> None:
        """Mark span as error."""
        self.status = "error"
        self.add_log(f"Error: {error}")
        self.tags["error"] = "true"

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "component": self.component,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "tags": self.tags,
            "logs": self.logs,
            "status": self.status
        }


class TelemetryCollector:
    """Central telemetry collection and processing system."""

    def __init__(self,
                 max_events: int = 10000,
                 max_metrics: int = 50000,
                 max_spans: int = 5000,
                 flush_interval_sec: float = 30.0):
        """
        Initialize telemetry collector.

        Args:
            max_events: Maximum number of events to keep in memory
            max_metrics: Maximum number of metrics to keep in memory
            max_spans: Maximum number of spans to keep in memory
            flush_interval_sec: Interval for flushing data to external systems
        """

        # Event storage
        self.events: deque = deque(maxlen=max_events)
        self.metrics: deque = deque(maxlen=max_metrics)
        self.spans: Dict[str, TraceSpan] = {}  # Active spans
        self.completed_spans: deque = deque(maxlen=max_spans)

        # Real-time aggregations
        self.metric_aggregations: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.component_health: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Event subscribers
        self.event_subscribers: List[Callable] = []
        self.metric_subscribers: List[Callable] = []

        # Configuration
        self.flush_interval_sec = flush_interval_sec
        self.flush_task: Optional[asyncio.Task] = None

        # Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()

    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics."""

        self.prom_events_total = Counter(
            'lukhas_telemetry_events_total',
            'Total number of telemetry events',
            ['component', 'event_type', 'severity']
        )

        self.prom_operation_duration = Histogram(
            'lukhas_operation_duration_seconds',
            'Duration of operations',
            ['component', 'operation'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )

        self.prom_component_health = Gauge(
            'lukhas_component_health_score',
            'Component health score (0-1)',
            ['component']
        )

    def emit_event(self,
                   component: str,
                   event_type: str,
                   message: str,
                   severity: SeverityLevel = SeverityLevel.INFO,
                   data: Optional[Dict[str, Any]] = None,
                   tags: Optional[Dict[str, str]] = None,
                   trace_id: Optional[str] = None,
                   span_id: Optional[str] = None) -> TelemetryEvent:
        """Emit telemetry event."""

        event = TelemetryEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            component=component,
            event_type=event_type,
            severity=severity,
            message=message,
            data=data or {},
            tags=tags or {},
            trace_id=trace_id,
            span_id=span_id
        )

        # Store event
        self.events.append(event)

        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.prom_events_total.labels(
                component=component,
                event_type=event_type,
                severity=severity.value
            ).inc()

        # Notify subscribers
        for subscriber in self.event_subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")

        # Log to standard logging
        log_level = getattr(logging, severity.value.upper())
        logger.log(log_level, f"[{component}] {message}", extra={
            "event_type": event_type,
            "data": data,
            "tags": tags
        })

        return event

    def emit_metric(self,
                    component: str,
                    metric_name: str,
                    value: float,
                    metric_type: MetricType = MetricType.GAUGE,
                    tags: Optional[Dict[str, str]] = None) -> MetricData:
        """Emit telemetry metric."""

        metric = MetricData(
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
            component=component,
            tags=tags or {}
        )

        # Store metric
        self.metrics.append(metric)

        # Update aggregations
        self._update_metric_aggregations(metric)

        # Notify subscribers
        for subscriber in self.metric_subscribers:
            try:
                subscriber(metric)
            except Exception as e:
                logger.error(f"Metric subscriber error: {e}")

        return metric

    def start_span(self,
                   operation_name: str,
                   component: str,
                   parent_span_id: Optional[str] = None,
                   trace_id: Optional[str] = None,
                   tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        """Start a new trace span."""

        if trace_id is None:
            trace_id = str(uuid.uuid4())

        span = TraceSpan(
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            component=component,
            start_time=time.time(),
            tags=tags or {}
        )

        # Store active span
        self.spans[span.span_id] = span

        return span

    def finish_span(self, span: TraceSpan) -> None:
        """Finish a trace span."""

        span.finish()

        # Move to completed spans
        if span.span_id in self.spans:
            del self.spans[span.span_id]
        self.completed_spans.append(span)

        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE and span.duration_ms is not None:
            self.prom_operation_duration.labels(
                component=span.component,
                operation=span.operation_name
            ).observe(span.duration_ms / 1000.0)

    @asynccontextmanager
    async def trace_operation(self,
                              operation_name: str,
                              component: str,
                              parent_span_id: Optional[str] = None,
                              trace_id: Optional[str] = None,
                              tags: Optional[Dict[str, str]] = None):
        """Context manager for tracing operations."""

        span = self.start_span(
            operation_name=operation_name,
            component=component,
            parent_span_id=parent_span_id,
            trace_id=trace_id,
            tags=tags
        )

        try:
            yield span
        except Exception as e:
            span.set_error(str(e))
            raise
        finally:
            self.finish_span(span)

    def _update_metric_aggregations(self, metric: MetricData) -> None:
        """Update real-time metric aggregations."""

        key = f"{metric.component}.{metric.metric_name}"

        if key not in self.metric_aggregations:
            self.metric_aggregations[key] = {
                "count": 0,
                "sum": 0.0,
                "min": float('inf'),
                "max": float('-inf'),
                "avg": 0.0,
                "last_value": 0.0,
                "last_timestamp": 0.0
            }

        agg = self.metric_aggregations[key]
        agg["count"] += 1
        agg["sum"] += metric.value
        agg["min"] = min(agg["min"], metric.value)
        agg["max"] = max(agg["max"], metric.value)
        agg["avg"] = agg["sum"] / agg["count"]
        agg["last_value"] = metric.value
        agg["last_timestamp"] = metric.timestamp

    def get_component_health(self, component: str) -> Dict[str, Any]:
        """Get health metrics for a component."""

        # Calculate health based on recent events and metrics
        recent_events = [
            e for e in list(self.events)[-1000:]  # Last 1000 events
            if e.component == component and (time.time() - e.timestamp) < 300  # Last 5 minutes
        ]

        error_count = sum(1 for e in recent_events if e.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL])
        warning_count = sum(1 for e in recent_events if e.severity == SeverityLevel.WARNING)

        # Calculate health score (0-1)
        error_count + warning_count
        if len(recent_events) == 0:
            health_score = 1.0  # No recent events, assume healthy
        else:
            # Health decreases with errors (weight 3x) and warnings (weight 1x)
            weighted_issues = (error_count * 3) + warning_count
            health_score = max(0.0, 1.0 - (weighted_issues / len(recent_events)))

        # Update Prometheus gauge
        if PROMETHEUS_AVAILABLE:
            self.prom_component_health.labels(component=component).set(health_score)

        health_info = {
            "component": component,
            "health_score": health_score,
            "status": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.5 else "unhealthy",
            "recent_events": len(recent_events),
            "error_count": error_count,
            "warning_count": warning_count,
            "last_update": time.time()
        }

        self.component_health[component] = health_info
        return health_info

    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview."""

        # Component health
        components = set(e.component for e in self.events)
        component_health = {
            comp: self.get_component_health(comp)
            for comp in components
        }

        # Overall system health
        if component_health:
            overall_health = sum(h["health_score"] for h in component_health.values()) / len(component_health)
        else:
            overall_health = 1.0

        # Active spans
        active_operations = len(self.spans)

        # Recent activity
        recent_events = [e for e in self.events if (time.time() - e.timestamp) < 300]  # Last 5 minutes

        return {
            "timestamp": time.time(),
            "overall_health": overall_health,
            "system_status": "healthy" if overall_health > 0.8 else "degraded" if overall_health > 0.5 else "unhealthy",
            "components": component_health,
            "active_operations": active_operations,
            "recent_activity": {
                "events_5min": len(recent_events),
                "metrics_5min": len([m for m in self.metrics if (time.time() - m.timestamp) < 300]),
                "completed_spans_5min": len([s for s in self.completed_spans if s.end_time and (time.time() - s.end_time) < 300])
            },
            "storage": {
                "events": len(self.events),
                "metrics": len(self.metrics),
                "active_spans": len(self.spans),
                "completed_spans": len(self.completed_spans)
            }
        }

    async def start_background_processing(self) -> None:
        """Start background processing tasks."""

        if self.flush_task is None:
            self.flush_task = asyncio.create_task(self._background_flush_loop())

    async def stop_background_processing(self) -> None:
        """Stop background processing tasks."""

        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
            self.flush_task = None

    async def _background_flush_loop(self) -> None:
        """Background loop for flushing telemetry data."""

        while True:
            try:
                await asyncio.sleep(self.flush_interval_sec)
                await self._flush_telemetry_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Telemetry flush error: {e}")

    async def _flush_telemetry_data(self) -> None:
        """Flush telemetry data to external systems."""

        # This would integrate with external telemetry systems
        # For now, we'll just log a summary

        overview = self.get_system_overview()
        logger.info("Telemetry flush", extra={
            "system_health": overview["overall_health"],
            "active_operations": overview["active_operations"],
            "recent_events": overview["recent_activity"]["events_5min"]
        })


# Global telemetry collector instance
_global_telemetry: Optional[TelemetryCollector] = None


def get_telemetry() -> TelemetryCollector:
    """Get global telemetry collector instance."""
    global _global_telemetry

    if _global_telemetry is None:
        _global_telemetry = TelemetryCollector()

    return _global_telemetry


# Convenience functions for common telemetry operations
def emit_event(component: str, event_type: str, message: str, **kwargs) -> TelemetryEvent:
    """Convenience function to emit telemetry event."""
    return get_telemetry().emit_event(component, event_type, message, **kwargs)


def emit_metric(component: str, metric_name: str, value: float, **kwargs) -> MetricData:
    """Convenience function to emit telemetry metric."""
    return get_telemetry().emit_metric(component, metric_name, value, **kwargs)


def trace_operation(operation_name: str, component: str, **kwargs):
    """Convenience function to trace operation."""
    return get_telemetry().trace_operation(operation_name, component, **kwargs)


if __name__ == "__main__":
    # Example usage
    async def demo_telemetry():
        telemetry = TelemetryCollector()
        await telemetry.start_background_processing()

        # Emit some events
        telemetry.emit_event("demo", "startup", "Demo system starting")
        telemetry.emit_metric("demo", "cpu_usage", 45.2)

        # Trace an operation
        async with telemetry.trace_operation("demo_operation", "demo") as span:
            span.add_log("Starting demo operation")
            await asyncio.sleep(0.1)
            span.add_log("Demo operation completed")

        # Get system overview
        overview = telemetry.get_system_overview()
        print(json.dumps(overview, indent=2))

        await telemetry.stop_background_processing()

    asyncio.run(demo_telemetry())
