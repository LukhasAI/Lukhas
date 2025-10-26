"""
AI Agent Tracer for Swarm Telemetry

Provides distributed tracing and telemetry for swarm agents and colonies
with support for operations tracking, metrics collection, and observability.
"""
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """Represents a traced operation span"""
    span_id: str
    agent_id: str
    operation: str
    start_time: float
    end_time: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def finish(self) -> float:
        """Mark span as finished and return duration"""
        self.end_time = time.time()
        return self.duration

    @property
    def duration(self) -> float:
        """Get span duration in seconds"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time


class TraceCollector:
    """Collects and stores trace spans for analysis"""

    def __init__(self):
        self.spans: list[TraceSpan] = []
        self.metrics: dict[str, Any] = {
            "total_operations": 0,
            "total_duration": 0.0,
            "operations_by_type": {}
        }

    def collect_span(self, span: TraceSpan) -> None:
        """Collect a completed trace span"""
        self.spans.append(span)

        # Update metrics
        self.metrics["total_operations"] += 1
        self.metrics["total_duration"] += span.duration

        op_type = span.operation
        if op_type not in self.metrics["operations_by_type"]:
            self.metrics["operations_by_type"][op_type] = {
                "count": 0,
                "total_duration": 0.0
            }

        self.metrics["operations_by_type"][op_type]["count"] += 1
        self.metrics["operations_by_type"][op_type]["total_duration"] += span.duration

        logger.debug(
            f"Trace collected: {span.agent_id} - {span.operation} ({span.duration:.4f}s)"
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get collected telemetry metrics"""
        return {
            **self.metrics,
            "total_spans": len(self.spans),
            "avg_duration": (
                self.metrics["total_duration"] / self.metrics["total_operations"]
                if self.metrics["total_operations"] > 0
                else 0.0
            )
        }

    def get_spans_for_agent(self, agent_id: str) -> list[TraceSpan]:
        """Get all spans for a specific agent"""
        return [span for span in self.spans if span.agent_id == agent_id]


class AIAgentTracer:
    """
    Tracer for AI agent operations in swarm architecture

    Provides context managers for tracing operations with automatic
    span collection and metrics aggregation.
    """

    def __init__(self, agent_id: str, collector: TraceCollector):
        """
        Initialize agent tracer

        Args:
            agent_id: Unique identifier for the agent being traced
            collector: TraceCollector instance for storing spans
        """
        self.agent_id = agent_id
        self.collector = collector
        self.active_spans: dict[str, TraceSpan] = {}

    @contextmanager
    def trace_agent_operation(self, agent_id: str, operation: str, **metadata):
        """
        Trace an agent operation with automatic span management

        Args:
            agent_id: Agent performing the operation
            operation: Name of the operation being traced
            **metadata: Additional metadata to attach to the span

        Yields:
            TraceSpan for the operation

        Example:
            with tracer.trace_agent_operation("agent-1", "process_message"):
                # Agent operation here
                pass
        """
        span_id = f"span-{uuid4().hex[:8]}"
        span = TraceSpan(
            span_id=span_id,
            agent_id=agent_id,
            operation=operation,
            start_time=time.time(),
            metadata=metadata
        )

        self.active_spans[span_id] = span

        try:
            yield span
        finally:
            span.finish()
            self.active_spans.pop(span_id, None)
            self.collector.collect_span(span)

    def get_active_operations(self) -> list[str]:
        """Get list of currently active operations"""
        return [span.operation for span in self.active_spans.values()]

    def get_metrics(self) -> dict[str, Any]:
        """Get metrics for this agent"""
        agent_spans = self.collector.get_spans_for_agent(self.agent_id)

        if not agent_spans:
            return {
                "agent_id": self.agent_id,
                "total_operations": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0
            }

        total_duration = sum(span.duration for span in agent_spans)

        return {
            "agent_id": self.agent_id,
            "total_operations": len(agent_spans),
            "total_duration": total_duration,
            "avg_duration": total_duration / len(agent_spans),
            "active_operations": len(self.active_spans)
        }


class GlobalTracer:
    """Global tracer singleton for swarm-wide telemetry"""

    def __init__(self):
        self.collector = TraceCollector()
        self.agent_tracers: dict[str, AIAgentTracer] = {}

    def get_tracer(self, agent_id: str) -> AIAgentTracer:
        """Get or create a tracer for an agent"""
        if agent_id not in self.agent_tracers:
            self.agent_tracers[agent_id] = AIAgentTracer(agent_id, self.collector)
        return self.agent_tracers[agent_id]

    def get_global_metrics(self) -> dict[str, Any]:
        """Get swarm-wide telemetry metrics"""
        return {
            "collector_metrics": self.collector.get_metrics(),
            "total_agents": len(self.agent_tracers),
            "agents": {
                agent_id: tracer.get_metrics()
                for agent_id, tracer in self.agent_tracers.items()
            }
        }


# Global singleton instance
_global_tracer: Optional[GlobalTracer] = None


def get_global_tracer() -> GlobalTracer:
    """Get or create the global tracer singleton"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = GlobalTracer()
    return _global_tracer


__all__ = [
    "AIAgentTracer",
    "TraceCollector",
    "TraceSpan",
    "GlobalTracer",
    "get_global_tracer",
]
