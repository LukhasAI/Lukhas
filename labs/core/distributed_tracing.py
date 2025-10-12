"""
Distributed Tracing System for Lukhas AI
Addresses TODO 168: Distributed tracing with correlation IDs

This module provides comprehensive tracing capabilities for distributed
AI agent interactions, enabling observability and debugging.
"""
import json
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from typing import Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """A single span in a distributed trace"""

    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    tags: dict[str, Any]
    logs: list[dict[str, Any]]
    status: str  # "ok", "error", "timeout"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def finish(self, status: str = "ok"):
        """Mark the span as finished"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status

    def add_tag(self, key: str, value: Any):
        """Add a tag to the span"""
        self.tags[key] = value

    def add_log(self, event: str, fields: Optional[dict[str, Any]] = None):
        """Add a log entry to the span"""
        log_entry = {
            "timestamp": time.time(),
            "event": event,
            "fields": fields or {},
        }
        self.logs.append(log_entry)


@dataclass
class TraceContext:
    """Context for maintaining trace information in the current execution"""

    trace_id: str
    correlation_id: str
    span_stack: list[str]
    baggage: dict[str, str] = None

    def __post_init__(self):
        if self.baggage is None:
            self.baggage = {}

    @property
    def span_id(self) -> Optional[str]:
        """Get the current span ID"""
        return self.span_stack[-1] if self.span_stack else None

    @property
    def parent_span_id(self) -> Optional[str]:
        """Get the parent span ID"""
        return self.span_stack[-2] if len(self.span_stack) > 1 else None

    def with_span(self, span_id: str) -> "TraceContext":
        """Create a new context with a child span"""
        new_stack = self.span_stack.copy()
        new_stack.append(span_id)
        return TraceContext(
            trace_id=self.trace_id,
            correlation_id=self.correlation_id,
            span_stack=new_stack,
            baggage=self.baggage.copy(),
        )

    def set_baggage_item(self, key: str, value: str):
        """Set a baggage item that propagates with the trace"""
        self.baggage[key] = value

    def get_baggage_item(self, key: str) -> Optional[str]:
        """Get a baggage item"""
        return self.baggage.get(key)

    def to_headers(self) -> dict[str, str]:
        """Convert context to HTTP-like headers for propagation"""
        headers = {
            "lukhas-trace-id": self.trace_id,
            "lukhas-correlation-id": self.correlation_id,
        }

        if self.span_id:
            headers["lukhas-span-id"] = self.span_id

        if self.parent_span_id:
            headers["lukhas-parent-span-id"] = self.parent_span_id

        # Add baggage
        for key, value in self.baggage.items():
            headers[f"lukhas-baggage-{key}"] = value

        return headers

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> Optional["TraceContext"]:
        """Create context from HTTP-like headers"""
        trace_id = headers.get("lukhas-trace-id")
        correlation_id = headers.get("lukhas-correlation-id")
        span_id = headers.get("lukhas-span-id")

        if not trace_id or not correlation_id:
            return None

        span_stack = [span_id] if span_id else []
        parent_span_id = headers.get("lukhas-parent-span-id")
        if parent_span_id:
            span_stack.insert(0, parent_span_id)

        context = cls(
            trace_id=trace_id,
            correlation_id=correlation_id,
            span_stack=span_stack,
        )

        # Extract baggage
        for key, value in headers.items():
            if key.startswith("lukhas-baggage-"):
                baggage_key = key[15:]  # Remove "lukhas-baggage-" prefix
                context.baggage[baggage_key] = value

        return context


class TraceCollector:
    """
    Collects and stores trace spans for analysis
    """

    def __init__(self, max_traces: int = 10000):
        self.max_traces = max_traces
        self.traces: dict[str, list[TraceSpan]] = defaultdict(list)
        self.spans: dict[str, TraceSpan] = {}
        self.completed_traces: deque = deque(maxlen=max_traces)
        self._lock = threading.Lock()

    def add_span(self, span: TraceSpan):
        """Add a span to the collector"""
        with self._lock:
            self.spans[span.span_id] = span
            self.traces[span.trace_id].append(span)

            # Check if trace is complete
            if span.end_time is not None:
                self._check_trace_completion(span.trace_id)

    def _check_trace_completion(self, trace_id: str):
        """Check if a trace is complete and move to completed traces"""
        trace_spans = self.traces[trace_id]

        # Simple heuristic: trace is complete if all spans are finished
        # and no new spans have been added for a while
        all_finished = all(span.end_time is not None for span in trace_spans)

        if all_finished and len(trace_spans) > 0:
            # Move to completed traces
            trace_data = {
                "trace_id": trace_id,
                "spans": [span.to_dict() for span in trace_spans],
                "completed_at": time.time(),
                "total_duration": self._calculate_trace_duration(trace_spans),
                "span_count": len(trace_spans),
            }

            self.completed_traces.append(trace_data)

            # Clean up active traces
            del self.traces[trace_id]
            for span in trace_spans:
                # Only delete if the span exists in our spans dict
                if span.span_id in self.spans:
                    del self.spans[span.span_id]

    def _calculate_trace_duration(self, spans: list[TraceSpan]) -> float:
        """Calculate the total duration of a trace"""
        if not spans:
            return 0.0

        start_times = [span.start_time for span in spans]
        end_times = [span.end_time for span in spans if span.end_time]

        if not end_times:
            return 0.0

        return max(end_times) - min(start_times)

    def get_trace(self, trace_id: str) -> Optional[dict[str, Any]]:
        """Get a specific trace"""
        # Check active traces
        if trace_id in self.traces:
            spans = self.traces[trace_id]
            return {
                "trace_id": trace_id,
                "spans": [span.to_dict() for span in spans],
                "status": "active",
                "span_count": len(spans),
            }

        # Check completed traces
        for trace_data in self.completed_traces:
            if trace_data["trace_id"] == trace_id:
                return trace_data

        return None

    def get_traces_by_operation(self, operation_name: str) -> list[dict[str, Any]]:
        """Get traces containing a specific operation"""
        matching_traces = []

        # Check active traces
        for trace_id, spans in self.traces.items():
            if any(span.operation_name == operation_name for span in spans):
                matching_traces.append(
                    {
                        "trace_id": trace_id,
                        "spans": [span.to_dict() for span in spans],
                        "status": "active",
                    }
                )

        # Check completed traces
        for trace_data in self.completed_traces:
            spans = trace_data["spans"]
            if any(span["operation_name"] == operation_name for span in spans):
                matching_traces.append(trace_data)

        return matching_traces

    def get_trace_statistics(self) -> dict[str, Any]:
        """Get statistics about collected traces"""
        with self._lock:
            active_traces = len(self.traces)
            completed_traces = len(self.completed_traces)
            total_spans = len(self.spans)  # Active spans

            operation_counts = defaultdict(int)
            service_counts = defaultdict(int)

            # Count operations and services in active traces
            for spans in self.traces.values():
                for span in spans:
                    operation_counts[span.operation_name] += 1
                    service_counts[span.service_name] += 1

            # Count in completed traces
            completed_span_count = 0
            for trace_data in self.completed_traces:
                for span_data in trace_data["spans"]:
                    operation_counts[span_data["operation_name"]] += 1
                    service_counts[span_data["service_name"]] += 1
                    completed_span_count += 1

            # Total spans includes both active and completed
            total_all_spans = total_spans + completed_span_count

            return {
                "active_traces": active_traces,
                "completed_traces": completed_traces,
                "total_spans": total_all_spans,  # Include both active and completed
                "active_spans": total_spans,
                "completed_spans": completed_span_count,
                "top_operations": dict(
                    sorted(
                        operation_counts.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )[:10]
                ),
                "services": list(service_counts.keys()),
                "collection_time": time.time(),
            }


class DistributedTracer:
    """
    Main tracer for creating and managing distributed traces
    """

    def __init__(self, service_name: str, collector: TraceCollector = None):
        self.service_name = service_name
        self.collector = collector or TraceCollector()
        self._current_context: threading.local = threading.local()

    def start_trace(self, operation_name: str, trace_id: Optional[str] = None) -> TraceContext:
        """Start a new trace"""
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        correlation_id = f"corr-{trace_id[:8]}"
        span_id = str(uuid.uuid4())

        context = TraceContext(
            trace_id=trace_id,
            correlation_id=correlation_id,
            span_stack=[span_id],
        )

        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=None,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time(),
            end_time=None,
            duration=None,
            tags={},
            logs=[],
            status="active",
        )

        self.collector.add_span(span)
        self._current_context.context = context

        return context

    def start_span(
        self,
        operation_name: str,
        parent_context: Optional[TraceContext] = None,
    ) -> TraceContext:
        """Start a new span within an existing trace"""
        if parent_context is None:
            parent_context = getattr(self._current_context, "context", None)

        if parent_context is None:
            # No parent context, start a new trace
            return self.start_trace(operation_name)

        span_id = str(uuid.uuid4())
        context = parent_context.with_span(span_id)

        span = TraceSpan(
            span_id=span_id,
            trace_id=context.trace_id,
            parent_span_id=context.parent_span_id,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time(),
            end_time=None,
            duration=None,
            tags={},
            logs=[],
            status="active",
        )

        self.collector.add_span(span)

        return context

    def finish_span(self, context: TraceContext, status: str = "ok"):
        """Finish a span"""
        if context.span_id:
            span = self.collector.spans.get(context.span_id)
            if span:
                span.finish(status)
                self.collector.add_span(span)  # Update the collector

    def add_tag(self, context: TraceContext, key: str, value: Any):
        """Add a tag to the current span"""
        if context.span_id:
            span = self.collector.spans.get(context.span_id)
            if span:
                span.add_tag(key, value)

    def add_log(
        self,
        context: TraceContext,
        event: str,
        fields: Optional[dict[str, Any]] = None,
    ):
        """Add a log entry to the current span"""
        if context.span_id:
            span = self.collector.spans.get(context.span_id)
            if span:
                span.add_log(event, fields or {})

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        parent_context: Optional[TraceContext] = None,
    ):
        """Context manager for tracing an operation"""
        context = self.start_span(operation_name, parent_context)
        old_context = getattr(self._current_context, "context", None)
        self._current_context.context = context

        try:
            yield context
            self.finish_span(context, "ok")
        except Exception as e:
            self.add_tag(context, "error", True)
            self.add_log(context, "error", {"error_message": str(e)})
            self.finish_span(context, "error")
            raise
        finally:
            self._current_context.context = old_context

    def get_current_context(self) -> Optional[TraceContext]:
        """Get the current trace context"""
        return getattr(self._current_context, "context", None)


class AIAgentTracer(DistributedTracer):
    """
    Specialized tracer for AI agents
    Adds AI-specific tracing capabilities
    """

    def trace_agent_operation(
        self,
        agent_id: str,
        operation: str,
        task_data: Optional[dict[str, Any]] = None,
    ):
        """Trace an AI agent operation"""
        operation_name = f"agent.{operation}"

        @contextmanager
        def _trace():
            with self.trace_operation(operation_name) as context:
                self.add_tag(context, "agent.id", agent_id)
                self.add_tag(context, "agent.operation", operation)

                if task_data:
                    self.add_tag(context, "task.type", task_data.get("type"))
                    self.add_tag(context, "task.complexity", task_data.get("complexity"))

                context.set_baggage_item("agent_id", agent_id)
                yield context

        return _trace()

    def trace_agent_collaboration(self, initiator_id: str, target_id: str, collaboration_type: str):
        """Trace collaboration between agents"""
        operation_name = f"collaboration.{collaboration_type}"

        @contextmanager
        def _trace():
            with self.trace_operation(operation_name) as context:
                self.add_tag(context, "collaboration.initiator", initiator_id)
                self.add_tag(context, "collaboration.target", target_id)
                self.add_tag(context, "collaboration.type", collaboration_type)

                context.set_baggage_item("initiator_agent", initiator_id)
                context.set_baggage_item("target_agent", target_id)
                yield context

        return _trace()

    def trace_memory_operation(self, agent_id: str, operation: str, memory_size: Optional[int] = None):
        """Trace memory operations"""
        operation_name = f"memory.{operation}"

        @contextmanager
        def _trace():
            with self.trace_operation(operation_name) as context:
                self.add_tag(context, "lukhas.memory.agent_id", agent_id)
                self.add_tag(context, "lukhas.memory.operation", operation)

                if memory_size is not None:
                    self.add_tag(context, "lukhas.memory.size", memory_size)

                yield context

        return _trace()


# Global tracer instances
_global_collector = None
_global_tracer = None


def get_global_collector() -> TraceCollector:
    """Get the global trace collector"""
    global _global_collector
    if _global_collector is None:
        _global_collector = TraceCollector()
    return _global_collector


def get_global_tracer(service_name: str = "lukhas-ai") -> DistributedTracer:
    """Get the global tracer"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = DistributedTracer(service_name, get_global_collector())
    return _global_tracer


def create_ai_tracer(agent_id: str) -> AIAgentTracer:
    """Create a tracer for an AI agent"""
    return AIAgentTracer(f"agent-{agent_id}", get_global_collector())


def demo_distributed_tracing():
    """Demonstrate distributed tracing"""
    # Create tracers for different agents
    agent1_tracer = create_ai_tracer("reasoning-001")
    agent2_tracer = create_ai_tracer("memory-001")

    # Simulate a complex operation with multiple spans
    with agent1_tracer.trace_agent_operation(
        "reasoning-001",
        "analyze_data",
        {"type": "reasoning", "complexity": "high"},
    ) as ctx:
        # Add some logs and tags
        agent1_tracer.add_log(ctx, "started_analysis", {"input_size": 1000})

        # Simulate sub-operations
        with agent1_tracer.trace_operation("load_model") as load_ctx:
            agent1_tracer.add_tag(load_ctx, "model.name", "reasoning-v2")
            time.sleep(0.1)  # Simulate work

        # Simulate collaboration with another agent
        with agent1_tracer.trace_agent_collaboration("reasoning-001", "memory-001", "knowledge_sharing"):
            # Memory agent operations (simulated)
            with agent2_tracer.trace_memory_operation("memory-001", "retrieve", memory_size=500) as mem_ctx:
                agent2_tracer.add_tag(mem_ctx, "query.type", "semantic_search")
                time.sleep(0.05)

        agent1_tracer.add_log(ctx, "analysis_complete", {"result_confidence": 0.92})

    # Get statistics
    collector = get_global_collector()
    stats = collector.get_trace_statistics()

    print("Tracing Statistics:")
    print(json.dumps(stats, indent=2))

    # Get traces by operation
    analysis_traces = collector.get_traces_by_operation("agent.analyze_data")
    print(f"\nFound {len(analysis_traces)} traces for analyze_data operation")

    if analysis_traces:
        trace = analysis_traces[0]
        print(f"Trace {trace['trace_id']} has {len(trace['spans'])} spans")

        for span_data in trace["spans"]:
            print(f"  - {span_data['operation_name']} ({span_data['duration']:.3f}s)")


# --- New Additions for Event Replay and State Snapshotting (TODO 169) ---


@dataclass
class AgentState:
    """Represents the state of an agent at a point in time."""

    agent_id: str
    timestamp: float
    state_data: dict[str, Any]


class StateSnapshotter:
    """Handles taking and restoring agent state snapshots."""

    def __init__(self, storage_path: str = "/tmp/snapshots"):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def take_snapshot(self, agent_id: str, state_data: dict[str, Any]):
        """Saves a snapshot of an agent's state."""
        snapshot = AgentState(
            agent_id=agent_id,
            timestamp=time.time(),
            state_data=state_data,
        )
        filepath = os.path.join(self.storage_path, f"{agent_id}-{snapshot.timestamp}.json")
        with open(filepath, "w") as f:
            json.dump(asdict(snapshot), f, indent=2)
        logger.info(f"State snapshot for agent {agent_id} saved to {filepath}")
        return filepath

    def restore_latest_snapshot(self, agent_id: str) -> Optional[AgentState]:
        """Restores the most recent snapshot for an agent."""
        try:
            files = [f for f in os.listdir(self.storage_path) if f.startswith(f"{agent_id}-") and f.endswith(".json")]
            if not files:
                return None
            latest_file = max(
                files,
                key=lambda f: float(f.split("-")[1].replace(".json", "")),
            )
            filepath = os.path.join(self.storage_path, latest_file)
            with open(filepath) as f:
                data = json.load(f)
                return AgentState(**data)
        except Exception as e:
            logger.error(f"Failed to restore snapshot for agent {agent_id}: {e}")
            return None


class EventReplayer:
    """Replays events from a trace to reconstruct state."""

    def __init__(self, trace_collector: TraceCollector, snapshotter: StateSnapshotter):
        self.trace_collector = trace_collector
        self.snapshotter = snapshotter

    def replay_trace(self, trace_id: str, to_timestamp: Optional[float] = None) -> dict[str, Any]:
        """
        Replays a trace to reconstruct the state of agents involved.
        - Starts from the nearest snapshot before the trace began.
        - Replays events up to the specified timestamp.
        """
        trace_data = self.trace_collector.get_trace(trace_id)
        if not trace_data:
            raise ValueError(f"Trace with ID {trace_id} not found.")

        # Identify agents in the trace
        agent_ids = set()
        for span_data in trace_data["spans"]:
            for tag_key, tag_value in span_data.get("tags", {}).items():
                if "agent.id" in tag_key or "agent_id" in tag_key:
                    agent_ids.add(tag_value)

        reconstructed_states = {}
        for agent_id in agent_ids:
            reconstructed_states[agent_id] = self.replay_agent_state(agent_id, trace_data, to_timestamp)

        return reconstructed_states

    def replay_agent_state(
        self,
        agent_id: str,
        trace_data: dict[str, Any],
        to_timestamp: Optional[float] = None,
    ) -> dict[str, Any]:
        """Reconstructs the state of a single agent from a trace."""
        # Start with the latest snapshot before the trace
        initial_state = self.snapshotter.restore_latest_snapshot(agent_id)
        current_state = initial_state.state_data if initial_state else {}

        # Filter and sort events for this agent from the trace
        agent_events = []
        for span_data in trace_data["spans"]:
            is_agent_span = False
            for tag_key, tag_value in span_data.get("tags", {}).items():
                if ("agent.id" in tag_key or "agent_id" in tag_key) and tag_value == agent_id:
                    is_agent_span = True
                    break

            if is_agent_span:
                for log in span_data.get("logs", []):
                    if not to_timestamp or log["timestamp"] <= to_timestamp:
                        agent_events.append(log)

        agent_events.sort(key=lambda e: e["timestamp"])

        # Apply events to the state
        for event in agent_events:
            # This is a simplified state update logic. A real implementation
            # would have more sophisticated event handlers.
            event_name = event.get("event")
            fields = event.get("fields", {})
            if "update" in event_name:
                current_state.update(fields)
            elif "delete" in event_name and "key" in fields:
                current_state.pop(fields["key"], None)

        return current_state


if __name__ == "__main__":
    import os

    demo_distributed_tracing()

    # --- Demo for new features ---
    print("\n--- Demonstrating Observability Enhancements ---")
    collector = get_global_collector()
    snapshotter = StateSnapshotter()
    replayer = EventReplayer(collector, snapshotter)

    # Assume agent-007's state
    agent_state = {"status": "idle", "tasks_completed": 5}
    snapshotter.take_snapshot("agent-007", agent_state)

    # Run a trace for this agent
    tracer = create_ai_tracer("agent-007")
    with tracer.trace_agent_operation("agent-007", "process_new_data") as ctx:
        tracer.add_log(
            ctx,
            "state_update",
            {"status": "processing", "current_task": "task-123"},
        )
        agent_state.update({"status": "processing", "current_task": "task-123"})
        time.sleep(0.1)
        tracer.add_log(ctx, "state_update", {"tasks_completed": 6, "status": "idle"})
        agent_state.update({"tasks_completed": 6, "status": "idle"})

    trace_id = tracer.get_current_context().trace_id

    # Replay the trace to reconstruct the state
    try:
        final_state = replayer.replay_trace(trace_id)
        print("\nReconstructed state for agent-007:")
        print(json.dumps(final_state.get("agent-007", {}), indent=2))
    except Exception as e:
        print(f"\nError during replay: {e}")
