import pytest
import time
import uuid
import threading
from unittest.mock import MagicMock

from lukhas.core.distributed_tracing import (
    TraceSpan,
    TraceContext,
    TraceCollector,
    DistributedTracer,
    AIAgentTracer,
    get_global_collector,
    get_global_tracer,
)

class TestTraceSpan:
    def test_span_creation_and_finish(self):
        start_time = time.time()
        span = TraceSpan(
            span_id="span1",
            trace_id="trace1",
            parent_span_id=None,
            operation_name="test_op",
            service_name="test_service",
            start_time=start_time,
            end_time=None,
            duration=None,
            tags={},
            logs=[],
            status="active",
        )
        time.sleep(0.01)
        span.finish("ok")
        assert span.end_time is not None
        assert span.duration is not None
        assert span.duration > 0
        assert span.status == "ok"

class TestTraceContext:
    def test_context_creation_and_propagation(self):
        ctx = TraceContext(trace_id="trace1", correlation_id="corr1", span_stack=["span1"])
        assert ctx.span_id == "span1"
        assert ctx.parent_span_id is None

        child_ctx = ctx.with_span("span2")
        assert child_ctx.span_id == "span2"
        assert child_ctx.parent_span_id == "span1"

        headers = child_ctx.to_headers()
        assert headers["lukhas-trace-id"] == "trace1"
        assert headers["lukhas-span-id"] == "span2"

        rehydrated_ctx = TraceContext.from_headers(headers)
        assert rehydrated_ctx.trace_id == "trace1"
        assert rehydrated_ctx.span_id == "span2"

class TestTraceCollector:
    @pytest.fixture
    def collector(self):
        return TraceCollector()

    def test_add_and_get_trace(self, collector):
        span = TraceSpan("span1", "trace1", None, "op1", "service1", time.time(), None, None, {}, [], "active")
        collector.add_span(span)

        trace = collector.get_trace("trace1")
        assert trace is not None
        assert len(trace["spans"]) == 1
        assert trace["status"] == "active"

        span.finish()
        # In the actual implementation, completion is checked when a new span is added.
        # Here we explicitly call the internal method to simulate this for the test.
        collector._check_trace_completion(span.trace_id)

        completed_trace = collector.get_trace("trace1")
        assert completed_trace is not None
        assert "completed_at" in completed_trace

class TestDistributedTracer:
    @pytest.fixture
    def tracer(self):
        return DistributedTracer("test_service")

    def test_start_trace_and_span(self, tracer):
        ctx = tracer.start_trace("root_op")
        assert ctx.trace_id is not None
        assert len(ctx.span_stack) == 1

        with tracer.trace_operation("child_op", parent_context=ctx) as child_ctx:
            assert child_ctx.parent_span_id == ctx.span_id
            assert len(child_ctx.span_stack) == 2

        # Check if span was finished
        span = tracer.collector.spans.get(child_ctx.span_id)
        assert span.status == "ok"
        assert span.end_time is not None

    def test_thread_safety_of_context(self, tracer):
        """Verify that trace context is thread-local."""
        results = {}

        def worker(op_name):
            with tracer.trace_operation(op_name) as ctx:
                time.sleep(0.01)
                results[op_name] = tracer.get_current_context().span_id
                assert tracer.get_current_context().span_id == ctx.span_id

        t1 = threading.Thread(target=worker, args=("op1",))
        t2 = threading.Thread(target=worker, args=("op2",))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert results["op1"] != results["op2"]

class TestAIAgentTracer:
    @pytest.fixture
    def ai_tracer(self):
        return AIAgentTracer("test_agent")

    def test_trace_agent_operation(self, ai_tracer):
        with ai_tracer.trace_agent_operation("agent1", "reason") as ctx:
            span = ai_tracer.collector.spans[ctx.span_id]
            assert span.tags["agent.id"] == "agent1"
            assert span.operation_name == "agent.reason"

def test_global_instances():
    c1 = get_global_collector()
    c2 = get_global_collector()
    assert c1 is c2

    t1 = get_global_tracer()
    t2 = get_global_tracer()
    assert t1 is t2
