#!/usr/bin/env python3
"""
Tests for LUKHAS Prometheus metrics integration.
Validates metrics collection with and without Prometheus client available.
"""

import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.observability.prometheus_metrics import (
    LUKHASMetrics,
    MetricsConfig,
    initialize_metrics,
    get_lukhas_metrics,
    shutdown_metrics,
    PROMETHEUS_AVAILABLE,
)


class TestMetricsConfig:
    """Test metrics configuration"""

    def test_default_config(self):
        """Test default metrics configuration"""
        config = MetricsConfig()

        assert config.enabled is True
        assert config.namespace == "lukhas"
        assert config.subsystem == "ai"
        assert config.http_port == 8000
        assert config.push_gateway_url is None
        assert config.push_job_name == "lukhas-ai"
        assert config.push_interval == 30

    def test_custom_config(self):
        """Test custom metrics configuration"""
        config = MetricsConfig(
            enabled=False,
            namespace="custom",
            subsystem="test",
            http_port=9090,
            push_gateway_url="http://pushgateway:9091",
            push_job_name="test-job",
            push_interval=60,
        )

        assert config.enabled is False
        assert config.namespace == "custom"
        assert config.subsystem == "test"
        assert config.http_port == 9090
        assert config.push_gateway_url == "http://pushgateway:9091"
        assert config.push_job_name == "test-job"
        assert config.push_interval == 60


class TestLUKHASMetricsWithoutPrometheus:
    """Test LUKHAS metrics when Prometheus client is not available"""

    @patch('lukhas.observability.prometheus_metrics.PROMETHEUS_AVAILABLE', False)
    def test_metrics_initialization_without_prometheus(self):
        """Test metrics initialization when Prometheus is not available"""
        metrics = LUKHASMetrics()

        assert not metrics.enabled
        assert metrics.config.enabled is True  # Config says enabled, but no client

    @patch('lukhas.observability.prometheus_metrics.PROMETHEUS_AVAILABLE', False)
    def test_mock_operations_without_prometheus(self):
        """Test that operations work when Prometheus is not available"""
        metrics = LUKHASMetrics()

        # Should not raise exceptions
        metrics.record_request("test", "GET", "200", 0.1)
        metrics.record_error("test", "ValueError")
        metrics.record_memory_operation("store", True, 0.05, 10)
        metrics.record_matriz_pipeline(0.15, True, True, 4)
        metrics.record_plugin_operation("discovery", True, 0.02)
        metrics.update_system_uptime()

        # Should return disabled status
        summary = metrics.get_metrics_summary()
        assert summary["enabled"] is False


@pytest.mark.skipif(not PROMETHEUS_AVAILABLE, reason="Prometheus client not available")
class TestLUKHASMetricsWithPrometheus:
    """Test LUKHAS metrics with Prometheus client available"""

    def test_metrics_initialization_with_prometheus(self):
        """Test metrics initialization with Prometheus"""
        config = MetricsConfig(
            push_gateway_url=None,  # Disable push gateway for testing
        )
        metrics = LUKHASMetrics(config)

        assert metrics.enabled
        assert metrics.registry is not None
        assert hasattr(metrics, 'system_uptime')
        assert hasattr(metrics, 'requests_total')
        assert hasattr(metrics, 'memory_operations_total')

    def test_system_metrics_recording(self):
        """Test system metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record system info
        metrics.record_system_info({"version": "1.0.0", "environment": "test"})

        # Record requests
        metrics.record_request("/api/test", "GET", "200", 0.15)
        metrics.record_request("/api/test", "POST", "201", 0.25)
        metrics.record_request("/api/error", "GET", "500", 0.05)

        # Record errors
        metrics.record_error("memory", "OutOfMemoryError")
        metrics.record_error("matriz", "TimeoutError")

        # Update uptime
        metrics.update_system_uptime()

        # Should not raise exceptions and should update internal state
        summary = metrics.get_metrics_summary()
        assert summary["enabled"] is True
        assert summary["total_requests"] == 3
        assert summary["total_errors"] == 2

    def test_memory_metrics_recording(self):
        """Test memory system metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record memory operations
        metrics.record_memory_operation("store", True, 0.005, 5)
        metrics.record_memory_operation("recall", True, 0.012, 50)
        metrics.record_memory_operation("recall", False, 0.150, 1000)

        # Record memory stats
        metrics.record_memory_stats(
            {"semantic": 100, "episodic": 50},
            {"active": 1024000, "compressed": 512000}
        )

        # Record fold operations
        metrics.record_fold_operation(
            "compression", True, 0.6,
            {"active": 10, "compressed": 25, "evicted": 5}
        )

    def test_matriz_metrics_recording(self):
        """Test MATRIZ orchestration metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record pipeline execution
        metrics.record_matriz_pipeline(0.180, True, True, 4)
        metrics.record_matriz_pipeline(0.280, False, False, 2)

        # Record stage executions
        metrics.record_matriz_stage("intent", 0.025, True)
        metrics.record_matriz_stage("processing", 0.095, True)
        metrics.record_matriz_stage("validation", 0.150, False, timeout=True)

        # Record node health
        metrics.record_matriz_node_health("math_node", 0.95, 0.045)
        metrics.record_matriz_node_health("facts_node", 0.87, 0.065)

    def test_plugin_metrics_recording(self):
        """Test plugin system metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record plugin operations
        metrics.record_plugin_operation("discovery", True, 0.025)
        metrics.record_plugin_operation("instantiation", True, plugin_name="math_node")
        metrics.record_plugin_operation("instantiation", False, plugin_name="broken_node")

        # Record plugin stats
        metrics.record_plugin_stats({
            "cognitive": {"active": 15, "failed": 2},
            "memory": {"active": 8, "failed": 0},
            "orchestration": {"active": 5, "failed": 1},
        })

    def test_lane_label_instrumentation(self):
        """Ensure lane labels are applied to emitted metrics."""
        previous_lane = os.environ.get("LUKHAS_LANE")
        os.environ["LUKHAS_LANE"] = "candidate"
        try:
            config = MetricsConfig(push_gateway_url=None)
            metrics = LUKHASMetrics(config)
            metrics.record_request("/lane", "GET", "200", 0.01)

            metric_family = metrics.requests_total.collect()[0]
            lane_labels = [sample.labels.get("lane") for sample in metric_family.samples]
            assert "candidate" in lane_labels
        finally:
            if previous_lane is None:
                os.environ.pop("LUKHAS_LANE", None)
            else:
                os.environ["LUKHAS_LANE"] = previous_lane

    def test_observability_metrics_recording(self):
        """Test observability system metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record observability operations
        metrics.record_observability_operation("export", "tracing", True)
        metrics.record_observability_operation("span_created", "tracing", True)
        metrics.record_observability_operation("export", "tracing", False)

    def test_business_metrics_recording(self):
        """Test business KPI metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record business metrics
        metrics.record_communication_processed("product-a", "chat")
        metrics.record_content_generated("product-b", "image")
        metrics.record_user_feedback("product-a", 4)
        metrics.record_user_feedback("product-a", 5)

        # Export metrics and check for new metric names
        export_data = metrics.get_metrics_export()
        assert "lukhas_business_products_communications_total" in export_data
        assert "lukhas_business_products_content_generated_total" in export_data
        assert "lukhas_business_products_user_feedback_rating_bucket" in export_data

    def test_metrics_export(self):
        """Test metrics export functionality"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Record some data
        metrics.record_request("/test", "GET", "200", 0.1)
        metrics.record_memory_operation("store", True)

        # Export metrics
        export_data = metrics.get_metrics_export()
        assert isinstance(export_data, str)

        # Check for the correct metric names based on namespace_subsystem pattern
        assert "lukhas_ai_requests_total" in export_data
        assert "lukhas_memory_memory_operations_total" in export_data

    def test_http_server_start(self):
        """Test HTTP server startup (mock)"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = LUKHASMetrics(config)

        # Mock the start_http_server function to avoid actually starting server
        with patch('lukhas.observability.prometheus_metrics.start_http_server') as mock_start:
            mock_start.return_value = None
            result = metrics.start_http_server(port=0)  # Use port 0 to avoid conflicts
            assert result is True
            mock_start.assert_called_once()


class TestGlobalMetricsFunctions:
    """Test global metrics initialization and access"""

    def test_initialize_metrics(self):
        """Test global metrics initialization"""
        config = MetricsConfig(
            namespace="test",
            push_gateway_url=None,
        )
        metrics = initialize_metrics(config)

        assert metrics.config.namespace == "test"

    def test_get_lukhas_metrics(self):
        """Test getting global metrics instance"""
        metrics1 = get_lukhas_metrics()
        metrics2 = get_lukhas_metrics()

        # Should return same instance
        assert metrics1 is metrics2

    def test_shutdown_metrics(self):
        """Test metrics shutdown"""
        # Should not raise exceptions
        shutdown_metrics()


class TestMetricsIntegration:
    """Test metrics integration scenarios"""

    def test_memory_system_integration(self):
        """Test metrics integration with memory system"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = get_lukhas_metrics() or LUKHASMetrics(config)

        # Simulate memory system operations
        for i in range(100):
            metrics.record_memory_operation("store", True, 0.005, 1)

        for i in range(50):
            success = i % 10 != 0  # 90% success rate
            latency = 0.008 if success else 0.15
            metrics.record_memory_operation("recall", success, latency, 20)

        # Record fold operations
        metrics.record_fold_operation("compression", True, 0.7)
        metrics.record_fold_operation("eviction", True)

        # Update stats
        metrics.record_memory_stats(
            {"semantic": 150, "episodic": 75},
            {"active": 2048000, "compressed": 1024000}
        )

    def test_matriz_system_integration(self):
        """Test metrics integration with MATRIZ orchestration"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = get_lukhas_metrics() or LUKHASMetrics(config)

        # Simulate MATRIZ pipelines
        for i in range(20):
            success = i % 5 != 0  # 80% success rate
            within_budget = i % 3 != 0  # 67% within budget
            duration = 0.18 if within_budget else 0.35
            stages = 4 if success else 2

            metrics.record_matriz_pipeline(duration, success, within_budget, stages)

            # Record individual stages
            metrics.record_matriz_stage("intent", 0.02, True)
            metrics.record_matriz_stage("decision", 0.015, True)

            if stages >= 3:
                metrics.record_matriz_stage("processing", 0.08, success)

            if stages >= 4:
                timeout = not success and i % 2 == 0
                metrics.record_matriz_stage("validation", 0.04, success, timeout)

        # Update node health
        metrics.record_matriz_node_health("math_node", 0.92, 0.055)
        metrics.record_matriz_node_health("facts_node", 0.89, 0.067)

    def test_plugin_system_integration(self):
        """Test metrics integration with plugin system"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = get_lukhas_metrics() or LUKHASMetrics(config)

        # Simulate plugin discovery
        metrics.record_plugin_operation("discovery", True, 0.035)

        # Simulate plugin instantiations
        plugins = ["math_node", "facts_node", "creative_node", "broken_node"]
        for plugin in plugins:
            success = plugin != "broken_node"
            metrics.record_plugin_operation("instantiation", success, plugin_name=plugin)

        # Update plugin stats
        metrics.record_plugin_stats({
            "cognitive": {"active": 12, "failed": 1},
            "memory": {"active": 6, "failed": 0},
            "orchestration": {"active": 4, "failed": 0},
        })

    def test_error_scenarios(self):
        """Test metrics with various error scenarios"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = get_lukhas_metrics() or LUKHASMetrics(config)

        # System errors
        metrics.record_error("memory", "OutOfMemoryError")
        metrics.record_error("matriz", "TimeoutError")
        metrics.record_error("plugins", "ImportError")

        # Failed operations
        metrics.record_memory_operation("recall", False, 0.25, 1000)
        metrics.record_matriz_stage("processing", 0.20, False, timeout=True)
        metrics.record_plugin_operation("instantiation", False, plugin_name="broken_plugin")

        # Record failed requests
        metrics.record_request("/api/broken", "POST", "500", 0.5)
        metrics.record_request("/api/timeout", "GET", "504", 10.0)

    def test_high_volume_metrics(self):
        """Test metrics with high volume of operations"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = get_lukhas_metrics() or LUKHASMetrics(config)

        # High volume simulation
        for i in range(1000):
            # Requests
            if i % 10 == 0:
                metrics.record_request(f"/api/endpoint_{i%5}", "GET", "200", 0.1)

            # Memory operations
            if i % 5 == 0:
                metrics.record_memory_operation("recall", True, 0.01, 10)

            # MATRIZ stages
            if i % 20 == 0:
                metrics.record_matriz_stage("processing", 0.08, True)

        # Should handle high volume without issues
        summary = metrics.get_metrics_summary()
        assert summary["total_requests"] >= 100

    def test_concurrent_metrics_recording(self):
        """Test concurrent metrics recording"""
        config = MetricsConfig(push_gateway_url=None)
        metrics = get_lukhas_metrics() or LUKHASMetrics(config)
        errors = []

        def worker(worker_id):
            try:
                for i in range(50):
                    metrics.record_request(f"/worker/{worker_id}", "GET", "200", 0.1)
                    metrics.record_memory_operation("store", True, 0.005, 1)
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)

        # Launch multiple threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Should complete without errors
        assert len(errors) == 0

        # Should have recorded all operations
        summary = metrics.get_metrics_summary()
        assert summary["total_requests"] >= 250


class TestMetricsConfiguration:
    """Test various metrics configuration scenarios"""

    def test_disabled_metrics(self):
        """Test metrics with disabled configuration"""
        config = MetricsConfig(enabled=False)
        metrics = LUKHASMetrics(config)

        # Should be disabled even if Prometheus is available
        assert not metrics.enabled

        # Operations should not raise exceptions
        metrics.record_request("/test", "GET", "200", 0.1)
        summary = metrics.get_metrics_summary()
        assert summary["enabled"] is False

    @patch.dict('os.environ', {}, clear=True)
    def test_environment_configuration(self):
        """Test configuration from environment variables"""
        # Test without environment variables
        config = MetricsConfig()
        metrics = LUKHASMetrics(config)

        # Should use defaults
        assert config.namespace == "lukhas"
        assert config.http_port == 8000

    def test_custom_namespace_and_subsystem(self):
        """Test custom namespace and subsystem"""
        config = MetricsConfig(
            namespace="custom_app",
            subsystem="test_module",
            push_gateway_url=None,
        )

        if PROMETHEUS_AVAILABLE:
            metrics = LUKHASMetrics(config)
            metrics.record_request("/test", "GET", "200", 0.1)

            export_data = metrics.get_metrics_export()
            assert "custom_app_test_module_requests_total" in export_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])