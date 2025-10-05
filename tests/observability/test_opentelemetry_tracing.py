#!/usr/bin/env python3
"""
Tests for LUKHAS OpenTelemetry tracing integration.
Validates tracing functionality with and without OpenTelemetry available.
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.observability.opentelemetry_tracing import (
    OTEL_AVAILABLE,
    LUKHASTracer,
    get_lukhas_tracer,
    initialize_tracing,
    shutdown_tracing,
    trace_function,
    trace_matriz_execution,
    trace_memory_recall,
)


class TestLUKHASTracerWithoutOTel:
    """Test LUKHAS tracer behavior when OpenTelemetry is not available"""

    @patch('lukhas.observability.opentelemetry_tracing.OTEL_AVAILABLE', False)
    def test_tracer_initialization_without_otel(self):
        """Test tracer initialization when OpenTelemetry is not available"""
        tracer = LUKHASTracer("test-service")

        assert not tracer.enabled
        assert tracer.service_name == "test-service"
        assert tracer.service_version == "1.0.0"

    @patch('lukhas.observability.opentelemetry_tracing.OTEL_AVAILABLE', False)
    def test_mock_operations_without_otel(self):
        """Test that mock operations work when OpenTelemetry is not available"""
        tracer = LUKHASTracer("test-service")

        # Should not raise exceptions
        with tracer.trace_operation("test_operation") as span:
            span.set_attribute("test.key", "test.value")
            span.set_status("OK")

        tracer.trace_memory_operation("store", item_count=5, latency_ms=10.0)
        tracer.trace_matriz_stage("intent", 25.0, success=True)
        tracer.trace_plugin_operation("discovery", plugin_count=3)


@pytest.mark.skipif(not OTEL_AVAILABLE, reason="OpenTelemetry not available")
class TestLUKHASTracerWithOTel:
    """Test LUKHAS tracer with OpenTelemetry available"""

    def test_tracer_initialization_with_otel(self):
        """Test tracer initialization with OpenTelemetry"""
        tracer = LUKHASTracer(
            service_name="test-service",
            service_version="2.0.0",
            enable_auto_instrumentation=False,  # Disable for testing
        )

        assert tracer.enabled
        assert tracer.service_name == "test-service"
        assert tracer.service_version == "2.0.0"
        assert tracer._tracer is not None
        assert tracer._meter is not None

    def test_custom_metrics_setup(self):
        """Test that custom metrics are properly set up"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        # Check that metrics are created
        assert hasattr(tracer, 'memory_operations_counter')
        assert hasattr(tracer, 'memory_recall_latency')
        assert hasattr(tracer, 'fold_operations_counter')
        assert hasattr(tracer, 'matriz_stage_duration')
        assert hasattr(tracer, 'matriz_pipeline_duration')
        assert hasattr(tracer, 'plugin_discovery_counter')
        assert hasattr(tracer, 'plugin_instantiation_counter')

    def test_trace_operation_context_manager(self):
        """Test the trace_operation context manager"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        attributes = {"test.component": "memory", "test.value": 42}

        with tracer.trace_operation("test_operation", attributes) as span:
            # Should not raise exceptions
            assert span is not None

    def test_trace_operation_with_exception(self):
        """Test trace_operation with exception handling"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        with pytest.raises(ValueError):
            with tracer.trace_operation("failing_operation") as span:
                raise ValueError("Test exception")

    def test_memory_operation_tracing(self):
        """Test memory operation tracing"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        # Should not raise exceptions
        tracer.trace_memory_operation("store", item_count=10, latency_ms=15.5)
        tracer.trace_memory_operation("recall", item_count=5, latency_ms=8.2)
        tracer.trace_memory_operation("fold", success=False)

    def test_matriz_stage_tracing(self):
        """Test MATRIZ stage tracing"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        # Should not raise exceptions
        tracer.trace_matriz_stage("intent", 25.0, success=True)
        tracer.trace_matriz_stage("processing", 95.0, success=True)
        tracer.trace_matriz_stage("validation", 30.0, success=False, timeout=True, error="Timeout")

    def test_matriz_pipeline_tracing(self):
        """Test MATRIZ pipeline tracing"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        # Should not raise exceptions
        tracer.trace_matriz_pipeline(
            total_duration_ms=180.0,
            stages_completed=4,
            stages_failed=1,
            within_budget=True,
            user_query="What is 2+2?"
        )

    def test_plugin_operation_tracing(self):
        """Test plugin operation tracing"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        # Should not raise exceptions
        tracer.trace_plugin_operation("discovery", plugin_count=15, success=True)
        tracer.trace_plugin_operation("instantiation", plugin_name="math_node", success=True)
        tracer.trace_plugin_operation("instantiation", plugin_name="broken_node", success=False, error="Import error")

    def test_fold_operation_tracing(self):
        """Test fold operation tracing"""
        tracer = LUKHASTracer("test-service", enable_auto_instrumentation=False)

        # Should not raise exceptions
        tracer.trace_fold_operation("compression", fold_count=5, compression_ratio=0.6)
        tracer.trace_fold_operation("eviction", fold_count=10, success=True)
        tracer.trace_fold_operation("decompression", fold_count=2, success=False)


class TestGlobalTracingFunctions:
    """Test global tracing initialization and access functions"""

    def test_initialize_tracing(self):
        """Test global tracing initialization"""
        tracer = initialize_tracing(
            service_name="global-test",
            service_version="3.0.0",
            enable_auto_instrumentation=False,
        )

        assert tracer.service_name == "global-test"
        assert tracer.service_version == "3.0.0"

    def test_get_lukhas_tracer(self):
        """Test getting global tracer instance"""
        tracer1 = get_lukhas_tracer()
        tracer2 = get_lukhas_tracer()

        # Should return same instance
        assert tracer1 is tracer2

    def test_shutdown_tracing(self):
        """Test tracing shutdown"""
        # Should not raise exceptions
        shutdown_tracing()


class TestTracingDecorators:
    """Test tracing decorators and context managers"""

    def test_trace_function_decorator(self):
        """Test the trace_function decorator"""
        @trace_function("custom_operation", {"component": "test"})
        def test_function(x, y):
            return x + y

        # Should not raise exceptions
        result = test_function(2, 3)
        assert result == 5

    def test_trace_function_decorator_with_exception(self):
        """Test trace_function decorator with exception"""
        @trace_function("failing_operation")
        def failing_function():
            raise RuntimeError("Test error")

        with pytest.raises(RuntimeError):
            failing_function()

    def test_trace_function_decorator_with_class_method(self):
        """Test trace_function decorator on class methods"""
        class TestClass:
            @trace_function("class_method")
            def test_method(self, value):
                return value * 2

        obj = TestClass()
        result = obj.test_method(5)
        assert result == 10

    def test_trace_memory_recall_context_manager(self):
        """Test trace_memory_recall context manager"""
        with trace_memory_recall(item_count=10):
            # Simulate some work
            time.sleep(0.001)

    def test_trace_memory_recall_with_exception(self):
        """Test trace_memory_recall with exception"""
        with pytest.raises(ValueError):
            with trace_memory_recall(item_count=5):
                raise ValueError("Memory error")

    def test_trace_matriz_execution_context_manager(self):
        """Test trace_matriz_execution context manager"""
        with trace_matriz_execution() as context:
            # Simulate pipeline execution
            context["stages_completed"] = 3
            context["stages_failed"] = 0

    def test_trace_matriz_execution_with_exception(self):
        """Test trace_matriz_execution with exception"""
        with pytest.raises(RuntimeError):
            with trace_matriz_execution() as context:
                context["stages_completed"] = 2
                raise RuntimeError("Pipeline error")


class TestTracingIntegration:
    """Test tracing integration scenarios"""

    def test_memory_system_integration(self):
        """Test tracing integration with memory system operations"""
        tracer = get_lukhas_tracer()

        # Simulate memory operations
        with tracer.trace_operation("memory_batch_operation"):
            tracer.trace_memory_operation("store", item_count=100, latency_ms=5.0)
            tracer.trace_memory_operation("recall", item_count=20, latency_ms=12.0)
            tracer.trace_fold_operation("compression", fold_count=5, compression_ratio=0.7)

    def test_matriz_system_integration(self):
        """Test tracing integration with MATRIZ orchestration"""
        tracer = get_lukhas_tracer()

        # Simulate MATRIZ pipeline
        pipeline_start = time.perf_counter()

        # Stage executions
        tracer.trace_matriz_stage("intent", 15.0, success=True)
        tracer.trace_matriz_stage("decision", 8.0, success=True)
        tracer.trace_matriz_stage("processing", 85.0, success=True)
        tracer.trace_matriz_stage("validation", 20.0, success=True)

        # Pipeline completion
        total_duration = (time.perf_counter() - pipeline_start) * 1000
        tracer.trace_matriz_pipeline(
            total_duration_ms=total_duration,
            stages_completed=4,
            stages_failed=0,
            within_budget=total_duration < 250,
        )

    def test_plugin_system_integration(self):
        """Test tracing integration with plugin system"""
        tracer = get_lukhas_tracer()

        # Simulate plugin discovery and instantiation
        tracer.trace_plugin_operation("discovery", plugin_count=25, success=True)

        # Simulate individual plugin instantiations
        plugins = ["math_node", "facts_node", "creative_node"]
        for plugin in plugins:
            tracer.trace_plugin_operation("instantiation", plugin_name=plugin, success=True)

    def test_error_scenarios(self):
        """Test tracing with various error scenarios"""
        tracer = get_lukhas_tracer()

        # Memory errors
        tracer.trace_memory_operation("recall", item_count=1000, latency_ms=150.0, success=False)

        # MATRIZ timeouts
        tracer.trace_matriz_stage("processing", 200.0, success=False, timeout=True, error="Processing timeout")

        # Plugin failures
        tracer.trace_plugin_operation("instantiation", plugin_name="broken_plugin", success=False, error="ImportError")


class TestEnvironmentConfiguration:
    """Test environment-based configuration"""

    @patch.dict('os.environ', {'LUKHAS_JAEGER_ENDPOINT': 'localhost:14268'})
    def test_jaeger_endpoint_from_env(self):
        """Test Jaeger endpoint configuration from environment"""
        tracer = initialize_tracing(enable_auto_instrumentation=False)
        # Should not raise exceptions during initialization
        assert tracer is not None

    @patch.dict('os.environ', {'LUKHAS_OTLP_ENDPOINT': 'http://localhost:4317'})
    def test_otlp_endpoint_from_env(self):
        """Test OTLP endpoint configuration from environment"""
        tracer = initialize_tracing(enable_auto_instrumentation=False)
        # Should not raise exceptions during initialization
        assert tracer is not None

    def test_no_endpoint_configuration(self):
        """Test configuration with no endpoints (console output)"""
        tracer = initialize_tracing(enable_auto_instrumentation=False)
        # Should fall back to console exporter
        assert tracer is not None


class TestPerformanceAndScaling:
    """Test tracing performance and scaling"""

    def test_high_volume_tracing(self):
        """Test tracing with high volume of operations"""
        tracer = get_lukhas_tracer()

        # Simulate high-volume operations
        for i in range(100):
            tracer.trace_memory_operation("recall", item_count=10, latency_ms=5.0)
            if i % 10 == 0:
                tracer.trace_fold_operation("compression", fold_count=1)

    def test_concurrent_tracing(self):
        """Test concurrent tracing operations"""
        import threading
        tracer = get_lukhas_tracer()
        errors = []

        def worker():
            try:
                for i in range(10):
                    with tracer.trace_operation(f"worker_operation_{i}"):
                        tracer.trace_memory_operation("store", item_count=1)
            except Exception as e:
                errors.append(e)

        # Launch multiple threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Should not have any errors
        assert len(errors) == 0

    def test_large_attribute_values(self):
        """Test tracing with large attribute values"""
        tracer = get_lukhas_tracer()

        # Test with large string attributes
        large_query = "x" * 10000
        tracer.trace_matriz_pipeline(
            total_duration_ms=100.0,
            stages_completed=3,
            stages_failed=0,
            within_budget=True,
            user_query=large_query,  # Should be hashed, not stored directly
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
