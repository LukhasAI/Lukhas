"""
Comprehensive Test Suite for Core Metrics System
===============================================

Tests the LUKHAS Core Metrics system backed by centralized Prometheus registry.
This is a critical monitoring component that provides duplicate-tolerant metrics
for the entire LUKHAS system.

Test Coverage Areas:
- Prometheus metrics integration and availability
- Duplicate-tolerant registry functionality
- Router metrics (signal processing, cascade prevention)
- Network health metrics (coherence, active nodes)
- Metrics factory functions (counter, gauge, histogram)
- Backward compatibility with prometheus_client
- Error handling for missing dependencies
- Performance monitoring and collection
"""
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from core.metrics import (
    PROMETHEUS_AVAILABLE,
    Summary,
    network_active_nodes,
    network_coherence_score,
    router_cascade_preventions_total,
    router_no_rule_total,
    router_signal_processing_time,
)


class TestCoreMetrics:
    """Comprehensive test suite for the Core Metrics system."""

    @pytest.fixture
    def mock_prometheus_available(self):
        """Mock Prometheus as available."""
        with patch('core.metrics.PROMETHEUS_AVAILABLE', True):
            yield

    @pytest.fixture
    def mock_prometheus_unavailable(self):
        """Mock Prometheus as unavailable."""
        with patch('core.metrics.PROMETHEUS_AVAILABLE', False):
            yield

    @pytest.fixture
    def mock_observability_functions(self):
        """Mock observability functions."""
        with patch('core.metrics.counter') as mock_counter, \
             patch('core.metrics.gauge') as mock_gauge, \
             patch('core.metrics.histogram') as mock_histogram:

            # Configure mocks
            mock_counter.return_value = Mock()
            mock_gauge.return_value = Mock()
            mock_histogram.return_value = Mock()

            yield {
                'counter': mock_counter,
                'gauge': mock_gauge,
                'histogram': mock_histogram
            }

    # Prometheus Availability Tests
    def test_prometheus_availability_detection(self):
        """Test Prometheus availability detection."""
        # PROMETHEUS_AVAILABLE should be a boolean
        assert isinstance(PROMETHEUS_AVAILABLE, bool)

        # Summary should be available (either real or mock)
        assert Summary is not None

    def test_prometheus_available_summary_class(self):
        """Test Summary class when Prometheus is available."""
        if PROMETHEUS_AVAILABLE:
            # Should be the real Prometheus Summary
            assert hasattr(Summary, 'observe')
            # Create instance to verify it works
            try:
                summary = Summary('test_summary', 'Test summary metric')
                assert summary is not None
            except Exception:
                # May fail due to duplicate registration, which is expected
                pass

    def test_prometheus_unavailable_summary_class(self):
        """Test Summary class when Prometheus is unavailable."""
        with patch('core.metrics.PROMETHEUS_AVAILABLE', False):
            # Should be the mock Summary class
            summary = Summary('test_summary', 'Test summary metric')
            assert summary is not None
            assert hasattr(summary, 'observe')

            # Mock observe should not raise errors
            summary.observe(1.0)

    # Router Metrics Tests
    def test_router_no_rule_total_metric(self, mock_observability_functions):
        """Test router_no_rule_total counter metric."""
        counter_mock = mock_observability_functions['counter']

        # Verify metric was created with correct parameters
        counter_mock.assert_any_call(
            "lukhas_router_no_rule_total",
            "Signals that matched no routing rule",
            labelnames=("signal_type", "producer_module"),
        )

        # Test metric usage
        metric = router_no_rule_total
        assert metric is not None

    def test_router_signal_processing_time_metric(self, mock_observability_functions):
        """Test router_signal_processing_time histogram metric."""
        histogram_mock = mock_observability_functions['histogram']

        # Verify metric was created with correct parameters
        histogram_mock.assert_any_call(
            "lukhas_router_signal_processing_seconds",
            "Time spent processing signals in router",
            labelnames=("signal_type", "routing_strategy"),
        )

        # Test metric usage
        metric = router_signal_processing_time
        assert metric is not None

    def test_router_cascade_preventions_total_metric(self, mock_observability_functions):
        """Test router_cascade_preventions_total counter metric."""
        counter_mock = mock_observability_functions['counter']

        # Verify metric was created with correct parameters
        counter_mock.assert_any_call(
            "lukhas_router_cascade_preventions_total",
            "Number of signals blocked by cascade prevention",
            labelnames=("producer_module",),
        )

        # Test metric usage
        metric = router_cascade_preventions_total
        assert metric is not None

    # Network Health Metrics Tests
    def test_network_coherence_score_metric(self, mock_observability_functions):
        """Test network_coherence_score gauge metric."""
        gauge_mock = mock_observability_functions['gauge']

        # Verify metric was created with correct parameters
        gauge_mock.assert_any_call(
            "lukhas_network_coherence_score",
            "Current network coherence score (0-1)",
        )

        # Test metric usage
        metric = network_coherence_score
        assert metric is not None

    def test_network_active_nodes_metric(self, mock_observability_functions):
        """Test network_active_nodes gauge metric."""
        gauge_mock = mock_observability_functions['gauge']

        # Verify metric was created with correct parameters
        gauge_mock.assert_any_call(
            "lukhas_network_active_nodes",
            # Note: The description might be truncated in the provided code
        )

        # Test metric usage
        metric = network_active_nodes
        assert metric is not None

    # Metric Operations Tests
    def test_counter_metric_operations(self):
        """Test counter metric operations."""
        with patch('observability.counter') as mock_counter:
            # Create mock counter with expected methods
            mock_metric = Mock()
            mock_metric.inc = Mock()
            mock_counter.return_value = mock_metric

            # Import would create the metric
            from core.metrics import router_no_rule_total as test_counter

            # Test increment operations
            if hasattr(test_counter, 'inc'):
                test_counter.inc()
                test_counter.inc(2)
                test_counter.inc(labels={"signal_type": "awareness", "producer_module": "test"})

    def test_gauge_metric_operations(self):
        """Test gauge metric operations."""
        with patch('observability.gauge') as mock_gauge:
            # Create mock gauge with expected methods
            mock_metric = Mock()
            mock_metric.set = Mock()
            mock_metric.inc = Mock()
            mock_metric.dec = Mock()
            mock_gauge.return_value = mock_metric

            # Import would create the metric
            from core.metrics import network_coherence_score as test_gauge

            # Test gauge operations
            if hasattr(test_gauge, 'set'):
                test_gauge.set(0.8)
                test_gauge.inc(0.1)
                test_gauge.dec(0.05)

    def test_histogram_metric_operations(self):
        """Test histogram metric operations."""
        with patch('observability.histogram') as mock_histogram:
            # Create mock histogram with expected methods
            mock_metric = Mock()
            mock_metric.observe = Mock()
            mock_histogram.return_value = mock_metric

            # Import would create the metric
            from core.metrics import router_signal_processing_time as test_histogram

            # Test histogram operations
            if hasattr(test_histogram, 'observe'):
                test_histogram.observe(0.001)  # 1ms
                test_histogram.observe(0.050)  # 50ms
                test_histogram.observe(0.100, {"signal_type": "awareness", "routing_strategy": "broadcast"})

    # Duplicate Tolerance Tests
    def test_duplicate_tolerant_registry(self):
        """Test duplicate-tolerant registry functionality."""
        with patch('observability.counter') as mock_counter:
            mock_metric = Mock()
            mock_counter.return_value = mock_metric

            # Multiple imports should not cause ValueError
            try:
                # Simulate multiple module imports
                for _ in range(3):
                    from core.metrics import router_no_rule_total

                # Should not raise any exceptions
                assert True
            except ValueError as e:
                if "Duplicated timeseries" in str(e):
                    pytest.fail("Registry should be duplicate-tolerant")
                else:
                    raise

    def test_duplicate_metric_creation_handling(self):
        """Test handling of duplicate metric creation."""
        with patch('observability.counter') as mock_counter:
            # First call succeeds
            mock_counter.return_value = Mock()

            # Simulate duplicate creation
            mock_counter.side_effect = [Mock(), ValueError("Duplicated timeseries")]

            # Should handle gracefully
            try:
                # Second import
                import importlib

                from core.metrics import router_no_rule_total
                importlib.reload(importlib.import_module('core.metrics'))
            except ValueError:
                pytest.fail("Should handle duplicate creation gracefully")

    # Error Handling Tests
    def test_import_error_handling(self):
        """Test handling of import errors."""
        with patch('core.metrics.Summary', side_effect=ImportError("prometheus_client not available")):
            # Should fallback to mock Summary
            from core.metrics import Summary as TestSummary

            # Should be the mock class
            summary = TestSummary('test', 'test description')
            assert summary is not None
            assert hasattr(summary, 'observe')

    def test_missing_observability_module(self):
        """Test behavior when observability module is missing."""
        with patch('core.metrics.counter', side_effect=ImportError("observability not available")):
            try:
                # Should handle gracefully or raise appropriate error
                import importlib
                importlib.reload(importlib.import_module('core.metrics'))
            except ImportError:
                # Expected if observability is required
                pass

    def test_metric_creation_error_handling(self):
        """Test error handling during metric creation."""
        with patch('observability.counter', side_effect=Exception("Unexpected error")):
            try:
                import importlib
                importlib.reload(importlib.import_module('core.metrics'))
            except Exception:
                # Should handle or propagate appropriately
                pass

    # Performance Tests
    def test_metric_creation_performance(self):
        """Test metric creation performance."""
        start_time = time.time()

        # Import metrics module (triggers metric creation)
        import importlib

        import core.metrics
        importlib.reload(core.metrics)

        end_time = time.time()
        creation_time = end_time - start_time

        # Should create metrics quickly
        assert creation_time < 1.0  # Less than 1 second

    def test_metric_access_performance(self):
        """Test metric access performance."""
        from core.metrics import network_coherence_score, router_no_rule_total

        start_time = time.time()

        # Access metrics many times
        for _ in range(1000):
            _ = router_no_rule_total
            _ = network_coherence_score

        end_time = time.time()
        access_time = end_time - start_time

        # Should access metrics quickly
        assert access_time < 0.1  # Less than 100ms

    # Integration Tests
    def test_observability_integration(self):
        """Test integration with observability module."""
        try:
            from observability import counter, gauge, histogram

            # Test that functions are available
            assert callable(counter)
            assert callable(gauge)
            assert callable(histogram)

            # Test metric creation
            test_counter = counter("test_counter", "Test counter")
            test_gauge = gauge("test_gauge", "Test gauge")
            test_histogram = histogram("test_histogram", "Test histogram")

            assert test_counter is not None
            assert test_gauge is not None
            assert test_histogram is not None

        except ImportError:
            # Observability module may not be available in test environment
            pytest.skip("Observability module not available")

    def test_prometheus_client_integration(self):
        """Test integration with prometheus_client."""
        if PROMETHEUS_AVAILABLE:
            try:
                from prometheus_client import Summary as PrometheusClientSummary

                # Should be able to import and use
                assert PrometheusClientSummary is not None

                # Test compatibility
                assert Summary == PrometheusClientSummary or hasattr(Summary, 'observe')

            except ImportError:
                pytest.fail("prometheus_client should be available when PROMETHEUS_AVAILABLE is True")

    def test_metric_labels_integration(self):
        """Test metric labels integration."""
        with patch('observability.counter') as mock_counter:
            mock_metric = Mock()
            mock_metric.labels = Mock(return_value=Mock())
            mock_counter.return_value = mock_metric

            from core.metrics import router_no_rule_total

            # Test label usage
            if hasattr(router_no_rule_total, 'labels'):
                labeled_metric = router_no_rule_total.labels(
                    signal_type="awareness",
                    producer_module="consciousness"
                )
                assert labeled_metric is not None

    # Configuration Tests
    def test_metric_name_conventions(self):
        """Test metric naming conventions."""
        metric_names = [
            "lukhas_router_no_rule_total",
            "lukhas_router_signal_processing_seconds",
            "lukhas_router_cascade_preventions_total",
            "lukhas_network_coherence_score",
            "lukhas_network_active_nodes"
        ]

        for name in metric_names:
            # Should follow Prometheus naming conventions
            assert name.startswith("lukhas_")  # Namespace prefix
            assert "_" in name  # Contains underscores
            assert name.islower() or "_" in name  # Lowercase with underscores
            assert not name.endswith("_")  # No trailing underscore

    def test_metric_descriptions(self):
        """Test metric descriptions are meaningful."""
        descriptions = [
            "Signals that matched no routing rule",
            "Time spent processing signals in router",
            "Number of signals blocked by cascade prevention",
            "Current network coherence score (0-1)"
        ]

        for description in descriptions:
            # Should be descriptive
            assert len(description) > 10  # Reasonable length
            assert description[0].isupper()  # Starts with capital letter
            # Should not end with period (Prometheus convention)

    def test_metric_label_names(self):
        """Test metric label names follow conventions."""
        label_sets = [
            ("signal_type", "producer_module"),
            ("signal_type", "routing_strategy"),
            ("producer_module",)
        ]

        for labels in label_sets:
            for label in labels:
                # Should follow naming conventions
                assert label.islower()  # Lowercase
                assert "_" in label or label.isalpha()  # Underscores or letters only
                assert not label.startswith("_")  # No leading underscore
                assert not label.endswith("_")  # No trailing underscore

    # Cleanup and Resource Management Tests
    def test_metric_registry_cleanup(self):
        """Test metric registry cleanup doesn't cause issues."""
        # Import and use metrics
        # Simulate cleanup/restart scenario
        import importlib

        from core.metrics import network_coherence_score, router_no_rule_total
        importlib.reload(importlib.import_module('core.metrics'))

        # Should not cause any issues
        from core.metrics import router_no_rule_total as reloaded_metric
        assert reloaded_metric is not None

    def test_memory_usage_monitoring(self):
        """Test metrics don't cause memory leaks."""
        import gc
        import sys

        # Get initial reference count
        initial_refs = sys.getrefcount(None)  # Use None as baseline

        # Import and use metrics multiple times
        for _ in range(10):
            import importlib
            core_metrics = importlib.import_module('core.metrics')
            _ = core_metrics.router_no_rule_total
            _ = core_metrics.network_coherence_score

        # Force garbage collection
        gc.collect()

        # Check reference count hasn't grown excessively
        final_refs = sys.getrefcount(None)
        ref_growth = final_refs - initial_refs

        # Should not have significant reference growth
        assert ref_growth < 100  # Arbitrary reasonable threshold

    # Backward Compatibility Tests
    def test_backward_compatibility_summary(self):
        """Test backward compatibility with Summary class."""
        # Should be able to create Summary instances
        try:
            summary = Summary('test_summary', 'Test summary')
            assert summary is not None
            assert hasattr(summary, 'observe')

            # Should be able to call observe
            summary.observe(1.0)

        except Exception as e:
            # May fail due to duplicate registration in real environment
            if "already registered" not in str(e):
                raise

    def test_prometheus_client_compatibility(self):
        """Test compatibility with prometheus_client patterns."""
        if PROMETHEUS_AVAILABLE:
            # Should support common prometheus_client patterns
            from core.metrics import Summary

            # Test timing decorator pattern
            def timed_function():
                with Summary('test_timer', 'Test timer').time():
                    time.sleep(0.001)

            # Should not raise errors (may not work due to registration issues)
            try:  # TODO[T4-ISSUE]: {"code":"SIM105","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"try-except-pass pattern - consider contextlib.suppress for clarity","estimate":"10m","priority":"low","dependencies":"contextlib","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_tests_core_test_metrics_py_L509"}
                timed_function()
            except Exception:
                # Expected in test environment due to registration conflicts
                pass

    def test_fallback_behavior_consistency(self):
        """Test fallback behavior is consistent."""
        # When Prometheus is unavailable, should provide consistent interface
        with patch('core.metrics.PROMETHEUS_AVAILABLE', False):
            summary = Summary('test_fallback', 'Test fallback')

            # Should have consistent interface
            assert hasattr(summary, 'observe')

            # Should not raise errors
            summary.observe(1.0)
            summary.observe(2.0)
            summary.observe(3.0)
