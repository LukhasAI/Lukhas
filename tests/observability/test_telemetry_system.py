#!/usr/bin/env python3
"""
Test Suite: Advanced Telemetry & Observability System

Enterprise-grade test coverage for telemetry collection, distributed tracing,
real-time metrics aggregation, and performance monitoring.

# ΛTAG: test_telemetry, observability_testing, metrics_validation, tracing_tests
"""

import asyncio
import time
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from observability.telemetry_system import (
    MetricData,
    MetricType,
    SeverityLevel,
    TelemetryCollector,
    TelemetryEvent,
    TraceSpan,
    emit_event,
    emit_metric,
    get_telemetry,
    trace_operation,
)


class TestTelemetryEvent:
    """Test telemetry event functionality."""

    def test_event_creation(self):
        """Test creating telemetry events."""

        event = TelemetryEvent(
            event_id="test-123",
            timestamp=time.time(),
            component="test_component",
            event_type="test_event",
            severity=SeverityLevel.INFO,
            message="Test message",
            data={"key": "value"},
            tags={"env": "test"}
        )

        assert event.event_id == "test-123"
        assert event.component == "test_component"
        assert event.event_type == "test_event"
        assert event.severity == SeverityLevel.INFO
        assert event.message == "Test message"
        assert event.data == {"key": "value"}
        assert event.tags == {"env": "test"}

    def test_event_to_dict(self):
        """Test event serialization."""

        event = TelemetryEvent(
            event_id="test-123",
            timestamp=1234567890.0,
            component="test_component",
            event_type="test_event",
            severity=SeverityLevel.WARNING,
            message="Test message"
        )

        event_dict = event.to_dict()

        assert event_dict["event_id"] == "test-123"
        assert event_dict["timestamp"] == 1234567890.0
        assert event_dict["component"] == "test_component"
        assert event_dict["event_type"] == "test_event"
        assert event_dict["severity"] == "warning"
        assert event_dict["message"] == "Test message"


class TestMetricData:
    """Test metric data functionality."""

    def test_metric_creation(self):
        """Test creating metric data."""

        metric = MetricData(
            metric_name="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=85.5,
            timestamp=time.time(),
            component="system",
            tags={"host": "server1"}
        )

        assert metric.metric_name == "cpu_usage"
        assert metric.metric_type == MetricType.GAUGE
        assert metric.value == 85.5
        assert metric.component == "system"
        assert metric.tags == {"host": "server1"}

    def test_metric_to_dict(self):
        """Test metric serialization."""

        metric = MetricData(
            metric_name="response_time",
            metric_type=MetricType.HISTOGRAM,
            value=150.0,
            timestamp=1234567890.0,
            component="api"
        )

        metric_dict = metric.to_dict()

        assert metric_dict["metric_name"] == "response_time"
        assert metric_dict["metric_type"] == "histogram"
        assert metric_dict["value"] == 150.0
        assert metric_dict["timestamp"] == 1234567890.0
        assert metric_dict["component"] == "api"


class TestTraceSpan:
    """Test distributed tracing span functionality."""

    def test_span_creation(self):
        """Test creating trace spans."""

        span = TraceSpan(
            trace_id="trace-123",
            span_id="span-456",
            parent_span_id="parent-789",
            operation_name="test_operation",
            component="test_service",
            start_time=time.time()
        )

        assert span.trace_id == "trace-123"
        assert span.span_id == "span-456"
        assert span.parent_span_id == "parent-789"
        assert span.operation_name == "test_operation"
        assert span.component == "test_service"
        assert span.status == "active"

    def test_span_finish(self):
        """Test finishing trace spans."""

        start_time = time.time()
        span = TraceSpan(
            trace_id="trace-123",
            span_id="span-456",
            parent_span_id=None,
            operation_name="test_operation",
            component="test_service",
            start_time=start_time
        )

        # Simulate some processing time
        time.sleep(0.1)
        span.finish()

        assert span.status == "completed"
        assert span.end_time is not None
        assert span.duration_ms is not None
        assert span.duration_ms > 90  # Should be at least 90ms

    def test_span_add_log(self):
        """Test adding logs to spans."""

        span = TraceSpan(
            trace_id="trace-123",
            span_id="span-456",
            parent_span_id=None,
            operation_name="test_operation",
            component="test_service",
            start_time=time.time()
        )

        span.add_log("Processing started", {"step": 1})
        span.add_log("Processing completed", {"step": 2})

        assert len(span.logs) == 2
        assert span.logs[0]["message"] == "Processing started"
        assert span.logs[0]["data"] == {"step": 1}
        assert span.logs[1]["message"] == "Processing completed"
        assert span.logs[1]["data"] == {"step": 2}

    def test_span_set_error(self):
        """Test setting span errors."""

        span = TraceSpan(
            trace_id="trace-123",
            span_id="span-456",
            parent_span_id=None,
            operation_name="test_operation",
            component="test_service",
            start_time=time.time()
        )

        span.set_error("Connection timeout")

        assert span.status == "error"
        assert span.tags["error"] == "true"
        assert len(span.logs) == 1
        assert "Error: Connection timeout" in span.logs[0]["message"]


class TestTelemetryCollector:
    """Test telemetry collector functionality."""

    @pytest.fixture
    def collector(self):
        """Create telemetry collector for testing."""
        return TelemetryCollector(
            max_events=100,
            max_metrics=200,
            max_spans=50,
            flush_interval_sec=60.0
        )

    def test_emit_event(self, collector):
        """Test emitting telemetry events."""

        event = collector.emit_event(
            component="test_component",
            event_type="test_event",
            message="Test message",
            severity=SeverityLevel.INFO,
            data={"key": "value"},
            tags={"env": "test"}
        )

        assert isinstance(event, TelemetryEvent)
        assert event.component == "test_component"
        assert event.event_type == "test_event"
        assert event.message == "Test message"
        assert event.severity == SeverityLevel.INFO

        # Check event is stored
        assert len(collector.events) == 1
        assert collector.events[0] == event

    def test_emit_metric(self, collector):
        """Test emitting telemetry metrics."""

        metric = collector.emit_metric(
            component="test_component",
            metric_name="test_metric",
            value=42.0,
            metric_type=MetricType.COUNTER,
            tags={"env": "test"}
        )

        assert isinstance(metric, MetricData)
        assert metric.component == "test_component"
        assert metric.metric_name == "test_metric"
        assert metric.value == 42.0
        assert metric.metric_type == MetricType.COUNTER

        # Check metric is stored
        assert len(collector.metrics) == 1
        assert collector.metrics[0] == metric

    def test_start_span(self, collector):
        """Test starting trace spans."""

        span = collector.start_span(
            operation_name="test_operation",
            component="test_service",
            tags={"version": "1.0"}
        )

        assert isinstance(span, TraceSpan)
        assert span.operation_name == "test_operation"
        assert span.component == "test_service"
        assert span.tags == {"version": "1.0"}
        assert span.status == "active"

        # Check span is stored
        assert span.span_id in collector.spans
        assert collector.spans[span.span_id] == span

    def test_finish_span(self, collector):
        """Test finishing trace spans."""

        span = collector.start_span("test_operation", "test_service")
        span_id = span.span_id

        # Span should be in active spans
        assert span_id in collector.spans

        collector.finish_span(span)

        # Span should be moved to completed spans
        assert span_id not in collector.spans
        assert len(collector.completed_spans) == 1
        assert collector.completed_spans[0] == span
        assert span.status == "completed"

    @pytest.mark.asyncio
    async def test_trace_operation_context_manager(self, collector):
        """Test trace operation context manager."""

        async with collector.trace_operation("test_operation", "test_service") as span:
            assert isinstance(span, TraceSpan)
            assert span.operation_name == "test_operation"
            assert span.component == "test_service"
            assert span.status == "active"

            # Span should be in active spans during execution
            assert span.span_id in collector.spans

            span.add_log("Operation in progress")

        # After context, span should be completed
        assert span.status == "completed"
        assert span.span_id not in collector.spans
        assert len(collector.completed_spans) == 1

    @pytest.mark.asyncio
    async def test_trace_operation_with_exception(self, collector):
        """Test trace operation context manager with exceptions."""

        with pytest.raises(ValueError):
            async with collector.trace_operation("test_operation", "test_service") as span:
                span.add_log("About to fail")
                raise ValueError("Test error")

        # Span should be marked as error
        assert span.status == "error"
        assert span.tags["error"] == "true"
        assert any("Error: Test error" in log["message"] for log in span.logs)

    def test_metric_aggregations(self, collector):
        """Test real-time metric aggregations."""

        # Emit multiple metrics with same name
        collector.emit_metric("test", "cpu_usage", 50.0)
        collector.emit_metric("test", "cpu_usage", 75.0)
        collector.emit_metric("test", "cpu_usage", 60.0)

        # Check aggregations
        key = "test.cpu_usage"
        assert key in collector.metric_aggregations

        agg = collector.metric_aggregations[key]
        assert agg["count"] == 3
        assert agg["sum"] == 185.0
        assert agg["min"] == 50.0
        assert agg["max"] == 75.0
        assert agg["avg"] == 185.0 / 3
        assert agg["last_value"] == 60.0

    def test_component_health_calculation(self, collector):
        """Test component health score calculation."""

        # Emit various events for a component
        collector.emit_event("test_component", "info", "Normal operation", SeverityLevel.INFO)
        collector.emit_event("test_component", "warning", "Minor issue", SeverityLevel.WARNING)
        collector.emit_event("test_component", "error", "Error occurred", SeverityLevel.ERROR)

        health = collector.get_component_health("test_component")

        assert health["component"] == "test_component"
        assert 0.0 <= health["health_score"] <= 1.0
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert health["recent_events"] == 3
        assert health["error_count"] == 1
        assert health["warning_count"] == 1

    def test_system_overview(self, collector):
        """Test system overview generation."""

        # Add some test data
        collector.emit_event("component1", "info", "Component 1 info", SeverityLevel.INFO)
        collector.emit_event("component2", "error", "Component 2 error", SeverityLevel.ERROR)
        collector.emit_metric("component1", "metric1", 100.0)

        collector.start_span("test_op", "component1")

        overview = collector.get_system_overview()

        assert "timestamp" in overview
        assert "overall_health" in overview
        assert "system_status" in overview
        assert "components" in overview
        assert "active_operations" in overview
        assert "recent_activity" in overview
        assert "storage" in overview

        # Should have health data for both components
        assert len(overview["components"]) == 2
        assert "component1" in overview["components"]
        assert "component2" in overview["components"]

        # Should show 1 active operation
        assert overview["active_operations"] == 1

    @pytest.mark.asyncio
    async def test_background_processing(self, collector):
        """Test background processing tasks."""

        # Start background processing
        await collector.start_background_processing()
        assert collector.flush_task is not None

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Stop background processing
        await collector.stop_background_processing()
        assert collector.flush_task is None


class TestConvenienceFunctions:
    """Test convenience functions for telemetry."""

    def test_emit_event_function(self):
        """Test global emit_event function."""

        event = emit_event(
            component="test",
            event_type="test_event",
            message="Test message"
        )

        assert isinstance(event, TelemetryEvent)
        assert event.component == "test"
        assert event.event_type == "test_event"
        assert event.message == "Test message"

    def test_emit_metric_function(self):
        """Test global emit_metric function."""

        metric = emit_metric(
            component="test",
            metric_name="test_metric",
            value=123.45
        )

        assert isinstance(metric, MetricData)
        assert metric.component == "test"
        assert metric.metric_name == "test_metric"
        assert metric.value == 123.45

    @pytest.mark.asyncio
    async def test_trace_operation_function(self):
        """Test global trace_operation function."""

        async with trace_operation("test_operation", "test_component") as span:
            assert isinstance(span, TraceSpan)
            assert span.operation_name == "test_operation"
            assert span.component == "test_component"


class TestTelemetryIntegration:
    """Test telemetry system integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_telemetry_workflow(self):
        """Test complete telemetry workflow."""

        collector = TelemetryCollector()

        # Start background processing
        await collector.start_background_processing()

        try:
            # Simulate application workflow
            async with collector.trace_operation("user_request", "api_server") as request_span:
                request_span.add_log("Request received")

                # Emit some metrics
                collector.emit_metric("api_server", "request_count", 1, MetricType.COUNTER)
                collector.emit_metric("api_server", "response_time", 150.0, MetricType.HISTOGRAM)

                # Simulate database operation
                async with collector.trace_operation("db_query", "database", parent_span_id=request_span.span_id) as db_span:
                    db_span.add_log("Executing query")
                    collector.emit_metric("database", "query_time", 50.0, MetricType.HISTOGRAM)

                    # Simulate brief processing
                    await asyncio.sleep(0.01)

                    db_span.add_log("Query completed")

                # Emit success event
                collector.emit_event(
                    component="api_server",
                    event_type="request_completed",
                    message="Request processed successfully",
                    severity=SeverityLevel.INFO
                )

                request_span.add_log("Request processed")

            # Verify data was collected
            assert len(collector.events) >= 1
            assert len(collector.metrics) >= 3
            assert len(collector.completed_spans) >= 2

            # Check system overview
            overview = collector.get_system_overview()
            assert overview["overall_health"] > 0
            assert len(overview["components"]) >= 2

        finally:
            await collector.stop_background_processing()

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test telemetry error handling workflow."""

        collector = TelemetryCollector()

        # Simulate error scenario
        with pytest.raises(Exception):
            async with collector.trace_operation("failing_operation", "test_service") as span:
                span.add_log("Starting operation")

                # Emit error event
                collector.emit_event(
                    component="test_service",
                    event_type="operation_error",
                    message="Operation failed",
                    severity=SeverityLevel.ERROR
                )

                raise Exception("Simulated failure")

        # Verify error was captured
        assert span.status == "error"
        assert span.tags["error"] == "true"

        # Check component health reflects the error
        health = collector.get_component_health("test_service")
        assert health["error_count"] >= 1
        assert health["health_score"] < 1.0

    def test_performance_under_load(self):
        """Test telemetry performance under load."""

        collector = TelemetryCollector(max_events=1000, max_metrics=1000)

        # Generate lots of telemetry data
        start_time = time.time()

        for i in range(500):
            collector.emit_event(f"component_{i % 10}", "test_event", f"Event {i}")
            collector.emit_metric(f"component_{i % 10}", f"metric_{i % 5}", float(i))

        elapsed_time = time.time() - start_time

        # Should be able to handle 1000 operations quickly
        assert elapsed_time < 1.0  # Less than 1 second

        # Check data was stored (with limits applied)
        assert len(collector.events) <= 1000
        assert len(collector.metrics) <= 1000

        # Check aggregations were maintained
        assert len(collector.metric_aggregations) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
