"""
Tests for core.agent_tracer module

Tests the AI Agent Tracer functionality including:
- TraceSpan lifecycle and duration tracking
- TraceCollector metrics aggregation
- AIAgentTracer context manager patterns
- GlobalTracer singleton and multi-agent coordination
"""

import time
from unittest.mock import patch

import pytest

from core.agent_tracer import (
    AIAgentTracer,
    GlobalTracer,
    TraceCollector,
    TraceSpan,
    get_global_tracer,
)


class TestTraceSpan:
    """Test TraceSpan data class and duration tracking"""

    def test_trace_span_creation(self):
        """Test creating a trace span with required fields"""
        span = TraceSpan(
            span_id="test-span-1",
            agent_id="agent-001",
            operation="process_message",
            start_time=time.time(),
        )

        assert span.span_id == "test-span-1"
        assert span.agent_id == "agent-001"
        assert span.operation == "process_message"
        assert span.end_time is None
        assert span.metadata == {}

    def test_trace_span_with_metadata(self):
        """Test trace span with custom metadata"""
        metadata = {"priority": "high", "user_id": "user-123"}
        span = TraceSpan(
            span_id="test-span-2",
            agent_id="agent-002",
            operation="authenticate",
            start_time=time.time(),
            metadata=metadata,
        )

        assert span.metadata == metadata
        assert span.metadata["priority"] == "high"

    def test_trace_span_duration_before_finish(self):
        """Test duration calculation before span is finished"""
        start = time.time()
        span = TraceSpan(
            span_id="test-span-3",
            agent_id="agent-003",
            operation="compute",
            start_time=start,
        )

        time.sleep(0.01)  # Small delay
        duration = span.duration

        assert duration > 0
        assert duration < 1.0  # Should be much less than 1 second
        assert span.end_time is None  # Not finished yet

    def test_trace_span_finish(self):
        """Test finishing a span and getting final duration"""
        span = TraceSpan(
            span_id="test-span-4",
            agent_id="agent-004",
            operation="complete",
            start_time=time.time(),
        )

        time.sleep(0.01)
        final_duration = span.finish()

        assert span.end_time is not None
        assert final_duration > 0
        assert span.duration == final_duration  # Duration should be stable after finish

    def test_trace_span_duration_after_finish(self):
        """Test that duration remains stable after finishing"""
        span = TraceSpan(
            span_id="test-span-5",
            agent_id="agent-005",
            operation="test",
            start_time=time.time(),
        )

        time.sleep(0.01)
        span.finish()
        duration1 = span.duration

        time.sleep(0.01)  # Wait more time
        duration2 = span.duration

        # Duration should not change after finish
        assert duration1 == duration2


class TestTraceCollector:
    """Test TraceCollector metrics and span collection"""

    @pytest.fixture
    def collector(self):
        """Provide a fresh TraceCollector for each test"""
        return TraceCollector()

    def test_collector_initialization(self, collector):
        """Test collector starts with empty state"""
        assert len(collector.spans) == 0
        assert collector.metrics["total_operations"] == 0
        assert collector.metrics["total_duration"] == 0.0
        assert collector.metrics["operations_by_type"] == {}

    def test_collect_single_span(self, collector):
        """Test collecting a single finished span"""
        span = TraceSpan(
            span_id="span-1",
            agent_id="agent-1",
            operation="test_op",
            start_time=time.time(),
        )
        time.sleep(0.01)
        span.finish()

        collector.collect_span(span)

        assert len(collector.spans) == 1
        assert collector.metrics["total_operations"] == 1
        assert collector.metrics["total_duration"] > 0

    def test_collect_multiple_spans(self, collector):
        """Test collecting multiple spans updates metrics correctly"""
        spans = []
        for i in range(5):
            span = TraceSpan(
                span_id=f"span-{i}",
                agent_id=f"agent-{i}",
                operation="test_op",
                start_time=time.time(),
            )
            time.sleep(0.002)
            span.finish()
            spans.append(span)

        for span in spans:
            collector.collect_span(span)

        assert len(collector.spans) == 5
        assert collector.metrics["total_operations"] == 5
        assert collector.metrics["total_duration"] > 0

    def test_operations_by_type_tracking(self, collector):
        """Test that operations are tracked by type"""
        operations = ["read", "write", "read", "delete", "write", "read"]

        for i, op_type in enumerate(operations):
            span = TraceSpan(
                span_id=f"span-{i}",
                agent_id="agent-1",
                operation=op_type,
                start_time=time.time(),
            )
            span.finish()
            collector.collect_span(span)

        ops_by_type = collector.metrics["operations_by_type"]

        assert ops_by_type["read"]["count"] == 3
        assert ops_by_type["write"]["count"] == 2
        assert ops_by_type["delete"]["count"] == 1

    def test_get_metrics_with_averages(self, collector):
        """Test get_metrics calculates averages correctly"""
        # Add 3 spans with known durations
        for i in range(3):
            span = TraceSpan(
                span_id=f"span-{i}",
                agent_id="agent-1",
                operation="test",
                start_time=time.time(),
            )
            time.sleep(0.01)
            span.finish()
            collector.collect_span(span)

        metrics = collector.get_metrics()

        assert metrics["total_spans"] == 3
        assert metrics["total_operations"] == 3
        assert metrics["avg_duration"] > 0
        assert metrics["avg_duration"] == metrics["total_duration"] / 3

    def test_get_metrics_empty_collector(self, collector):
        """Test get_metrics with no collected spans"""
        metrics = collector.get_metrics()

        assert metrics["total_spans"] == 0
        assert metrics["total_operations"] == 0
        assert metrics["avg_duration"] == 0.0

    def test_get_spans_for_agent(self, collector):
        """Test filtering spans by agent ID"""
        # Create spans for different agents
        for agent_id in ["agent-1", "agent-2", "agent-1", "agent-3", "agent-1"]:
            span = TraceSpan(
                span_id=f"span-{len(collector.spans)}",
                agent_id=agent_id,
                operation="test",
                start_time=time.time(),
            )
            span.finish()
            collector.collect_span(span)

        agent1_spans = collector.get_spans_for_agent("agent-1")
        agent2_spans = collector.get_spans_for_agent("agent-2")
        agent3_spans = collector.get_spans_for_agent("agent-3")

        assert len(agent1_spans) == 3
        assert len(agent2_spans) == 1
        assert len(agent3_spans) == 1
        assert all(s.agent_id == "agent-1" for s in agent1_spans)


class TestAIAgentTracer:
    """Test AIAgentTracer context manager and operation tracking"""

    @pytest.fixture
    def collector(self):
        """Provide a fresh TraceCollector"""
        return TraceCollector()

    @pytest.fixture
    def tracer(self, collector):
        """Provide an AIAgentTracer for testing"""
        return AIAgentTracer("test-agent", collector)

    def test_tracer_initialization(self, tracer, collector):
        """Test tracer initializes with correct state"""
        assert tracer.agent_id == "test-agent"
        assert tracer.collector is collector
        assert len(tracer.active_spans) == 0

    def test_trace_operation_basic(self, tracer, collector):
        """Test basic operation tracing with context manager"""
        with tracer.trace_agent_operation("test-agent", "basic_op") as span:
            assert span.agent_id == "test-agent"
            assert span.operation == "basic_op"
            assert span.end_time is None  # Not finished yet
            time.sleep(0.01)

        # After exiting context, span should be finished and collected
        assert span.end_time is not None
        assert len(collector.spans) == 1
        assert collector.spans[0] is span

    def test_trace_operation_with_metadata(self, tracer):
        """Test tracing with custom metadata"""
        metadata = {"priority": "high", "retry_count": 3}

        with tracer.trace_agent_operation("test-agent", "metadata_op", **metadata) as span:
            assert span.metadata == metadata

    def test_trace_operation_exception_handling(self, tracer, collector):
        """Test that spans are collected even when exceptions occur"""
        with pytest.raises(ValueError):
            with tracer.trace_agent_operation("test-agent", "failing_op"):
                time.sleep(0.01)
                raise ValueError("Test error")

        # Span should still be collected despite exception
        assert len(collector.spans) == 1
        assert collector.spans[0].operation == "failing_op"
        assert collector.spans[0].end_time is not None

    def test_active_operations_tracking(self, tracer):
        """Test tracking of active operations"""
        assert len(tracer.get_active_operations()) == 0

        with tracer.trace_agent_operation("test-agent", "active_op"):
            active_ops = tracer.get_active_operations()
            assert len(active_ops) == 1
            assert "active_op" in active_ops

        # After context exits, no active operations
        assert len(tracer.get_active_operations()) == 0

    def test_multiple_concurrent_operations(self, tracer):
        """Test tracking multiple operations in same context"""
        # Simulate nested or parallel operations by manually managing spans
        with tracer.trace_agent_operation("test-agent", "op1"):
            with tracer.trace_agent_operation("test-agent", "op2"):
                active_ops = tracer.get_active_operations()
                assert len(active_ops) == 2
                assert "op1" in active_ops
                assert "op2" in active_ops

    def test_get_metrics_for_agent(self, tracer, collector):
        """Test getting metrics specific to an agent"""
        # Initially no operations
        metrics = tracer.get_metrics()
        assert metrics["agent_id"] == "test-agent"
        assert metrics["total_operations"] == 0

        # Add some operations
        for i in range(3):
            with tracer.trace_agent_operation("test-agent", f"op-{i}"):
                time.sleep(0.01)

        metrics = tracer.get_metrics()
        assert metrics["total_operations"] == 3
        assert metrics["avg_duration"] > 0
        assert metrics["active_operations"] == 0


class TestGlobalTracer:
    """Test GlobalTracer singleton and multi-agent coordination"""

    @pytest.fixture
    def global_tracer(self):
        """Provide a fresh GlobalTracer for each test"""
        return GlobalTracer()

    def test_global_tracer_initialization(self, global_tracer):
        """Test GlobalTracer starts with fresh state"""
        assert isinstance(global_tracer.collector, TraceCollector)
        assert len(global_tracer.agent_tracers) == 0

    def test_get_tracer_creates_new(self, global_tracer):
        """Test getting tracer creates it if it doesn't exist"""
        tracer = global_tracer.get_tracer("agent-001")

        assert isinstance(tracer, AIAgentTracer)
        assert tracer.agent_id == "agent-001"
        assert "agent-001" in global_tracer.agent_tracers

    def test_get_tracer_returns_existing(self, global_tracer):
        """Test getting same tracer returns existing instance"""
        tracer1 = global_tracer.get_tracer("agent-001")
        tracer2 = global_tracer.get_tracer("agent-001")

        assert tracer1 is tracer2

    def test_multiple_agents_coordination(self, global_tracer):
        """Test coordinating multiple agents through global tracer"""
        agent_ids = ["agent-1", "agent-2", "agent-3"]

        # Create operations for each agent
        for agent_id in agent_ids:
            tracer = global_tracer.get_tracer(agent_id)
            with tracer.trace_agent_operation(agent_id, "test_op"):
                time.sleep(0.01)

        # Check global metrics
        metrics = global_tracer.get_global_metrics()

        assert metrics["total_agents"] == 3
        assert len(metrics["agents"]) == 3
        assert metrics["collector_metrics"]["total_operations"] == 3

    def test_global_metrics_aggregation(self, global_tracer):
        """Test that global metrics aggregate across all agents"""
        # Agent 1: 2 operations
        tracer1 = global_tracer.get_tracer("agent-1")
        for _ in range(2):
            with tracer1.trace_agent_operation("agent-1", "op"):
                time.sleep(0.005)

        # Agent 2: 3 operations
        tracer2 = global_tracer.get_tracer("agent-2")
        for _ in range(3):
            with tracer2.trace_agent_operation("agent-2", "op"):
                time.sleep(0.005)

        metrics = global_tracer.get_global_metrics()

        assert metrics["total_agents"] == 2
        assert metrics["collector_metrics"]["total_operations"] == 5
        assert metrics["agents"]["agent-1"]["total_operations"] == 2
        assert metrics["agents"]["agent-2"]["total_operations"] == 3


class TestGlobalTracerSingleton:
    """Test the global tracer singleton pattern"""

    def test_get_global_tracer_singleton(self):
        """Test that get_global_tracer returns singleton instance"""
        tracer1 = get_global_tracer()
        tracer2 = get_global_tracer()

        assert tracer1 is tracer2
        assert isinstance(tracer1, GlobalTracer)

    @patch("core.agent_tracer._global_tracer", None)
    def test_get_global_tracer_creates_on_first_call(self):
        """Test that singleton is created on first call"""
        tracer = get_global_tracer()

        assert tracer is not None
        assert isinstance(tracer, GlobalTracer)


class TestIntegration:
    """Integration tests for complete tracing workflows"""

    def test_end_to_end_swarm_tracing(self):
        """Test complete workflow: multiple agents performing operations"""
        global_tracer = GlobalTracer()

        # Simulate swarm of 3 agents doing various operations
        agents_ops = {
            "agent-coordinator": ["initialize", "distribute_tasks", "aggregate_results"],
            "agent-worker-1": ["process_task", "validate", "store"],
            "agent-worker-2": ["process_task", "validate", "store"],
        }

        # Execute operations
        for agent_id, operations in agents_ops.items():
            tracer = global_tracer.get_tracer(agent_id)
            for operation in operations:
                with tracer.trace_agent_operation(agent_id, operation):
                    time.sleep(0.005)  # Simulate work

        # Verify complete telemetry
        global_metrics = global_tracer.get_global_metrics()

        assert global_metrics["total_agents"] == 3
        assert global_metrics["collector_metrics"]["total_operations"] == 9
        assert global_metrics["agents"]["agent-coordinator"]["total_operations"] == 3
        assert global_metrics["agents"]["agent-worker-1"]["total_operations"] == 3
        assert global_metrics["agents"]["agent-worker-2"]["total_operations"] == 3

    def test_operation_types_distribution(self):
        """Test tracking different operation types across agents"""
        global_tracer = GlobalTracer()

        operations = {
            "agent-1": ["read", "read", "write"],
            "agent-2": ["read", "delete", "write"],
        }

        for agent_id, ops in operations.items():
            tracer = global_tracer.get_tracer(agent_id)
            for op in ops:
                with tracer.trace_agent_operation(agent_id, op):
                    time.sleep(0.002)

        collector_metrics = global_tracer.get_global_metrics()["collector_metrics"]
        ops_by_type = collector_metrics["operations_by_type"]

        assert ops_by_type["read"]["count"] == 3
        assert ops_by_type["write"]["count"] == 2
        assert ops_by_type["delete"]["count"] == 1
