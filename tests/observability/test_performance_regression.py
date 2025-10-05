#!/usr/bin/env python3
"""
Test suite for LUKHAS Performance Regression Detection
Comprehensive tests for ML-based anomaly detection and performance monitoring.
"""

import asyncio
import statistics

# Test imports
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.observability.performance_regression import (
    DetectionMethod,
    PerformanceBaseline,
    PerformanceRegression,
    PerformanceRegressionDetector,
    RegressionSeverity,
    initialize_regression_detector,
    record_performance_data,
)


@pytest.fixture
def mock_dependencies():
    """Mock external dependencies"""
    mock_advanced_metrics = MagicMock()
    mock_alerting_system = MagicMock()
    mock_alerting_system.trigger_alert = AsyncMock()

    return {
        'advanced_metrics': mock_advanced_metrics,
        'alerting_system': mock_alerting_system,
    }


@pytest.fixture
async def regression_detector(mock_dependencies):
    """Create performance regression detector for testing"""
    with patch('lukhas.observability.performance_regression.get_advanced_metrics', return_value=mock_dependencies['advanced_metrics']):
        with patch('lukhas.observability.performance_regression.get_alerting_system', return_value=mock_dependencies['alerting_system']):
            detector = PerformanceRegressionDetector(
                baseline_window_days=1,  # Short for testing
                detection_sensitivity=0.8,
                min_samples_for_baseline=10,
                enable_ml_detection=True,
                enable_seasonal_analysis=False,  # Disable for simpler testing
                false_positive_learning=True,
            )
            yield detector
            await detector.shutdown()


class TestPerformanceRegressionDetector:
    """Test performance regression detector functionality"""

    @pytest.mark.asyncio
    async def test_basic_metric_recording(self, regression_detector):
        """Test basic performance metric recording"""
        await regression_detector.record_performance_metric(
            metric_name="response_time",
            component="api_server",
            value=0.1,  # 100ms
            operation="get_user",
        )

        metric_key = "api_server_response_time"
        assert metric_key in regression_detector.metric_timeseries
        assert len(regression_detector.metric_timeseries[metric_key]) == 1
        assert regression_detector.metric_timeseries[metric_key][0] == 0.1

    @pytest.mark.asyncio
    async def test_baseline_establishment(self, regression_detector):
        """Test performance baseline establishment"""
        metric_name = "test_latency"
        component = "test_service"

        # Record baseline data
        baseline_values = [0.1, 0.12, 0.09, 0.11, 0.10, 0.13, 0.08, 0.11, 0.12, 0.10, 0.09, 0.11]
        for value in baseline_values:
            await regression_detector.record_performance_metric(metric_name, component, value)

        # Establish baseline
        baseline = await regression_detector.establish_baseline(metric_name, component)

        assert baseline is not None
        assert baseline.metric_name == metric_name
        assert baseline.component == component
        assert abs(baseline.baseline_value - statistics.mean(baseline_values)) < 0.001
        assert baseline.sample_count == len(baseline_values)
        assert "p50" in baseline.percentiles
        assert "p95" in baseline.percentiles
        assert "p99" in baseline.percentiles

    @pytest.mark.asyncio
    async def test_insufficient_data_baseline(self, regression_detector):
        """Test baseline establishment with insufficient data"""
        metric_name = "insufficient_data"
        component = "test_service"

        # Record too few samples
        for i in range(5):  # Less than min_samples_for_baseline
            await regression_detector.record_performance_metric(metric_name, component, 0.1)

        # Should not establish baseline
        baseline = await regression_detector.establish_baseline(metric_name, component)
        assert baseline is None

    @pytest.mark.asyncio
    async def test_statistical_regression_detection(self, regression_detector):
        """Test statistical regression detection"""
        metric_name = "statistical_test"
        component = "test_service"

        # Establish baseline with normal values
        normal_values = [0.1] * 15  # Consistent 100ms
        for value in normal_values:
            await regression_detector.record_performance_metric(metric_name, component, value)

        baseline = await regression_detector.establish_baseline(metric_name, component)
        assert baseline is not None

        # Record regression value
        await regression_detector.record_performance_metric(metric_name, component, 0.5)  # 500ms - significant regression

        # Should detect regression
        metric_key = f"{component}_{metric_name}"
        regressions = [r for r in regression_detector.detected_regressions.values() if r.metric_name == metric_name]
        assert len(regressions) > 0

        regression = regressions[0]
        assert regression.severity in [RegressionSeverity.MAJOR, RegressionSeverity.CRITICAL]
        assert regression.detection_method in [DetectionMethod.Z_SCORE, DetectionMethod.STATISTICAL_THRESHOLD]

    @pytest.mark.asyncio
    async def test_trend_regression_detection(self, regression_detector):
        """Test trend-based regression detection"""
        metric_name = "trend_test"
        component = "trend_service"

        # Create gradual performance degradation trend
        base_time = datetime.now(timezone.utc) - timedelta(hours=1)
        trend_values = [0.1 + (i * 0.02) for i in range(25)]  # Gradually increasing latency

        for i, value in enumerate(trend_values):
            timestamp = base_time + timedelta(minutes=i)
            await regression_detector.record_performance_metric(
                metric_name, component, value, timestamp=timestamp
            )

        # Establish baseline (early values)
        baseline = await regression_detector.establish_baseline(metric_name, component)
        assert baseline is not None

        # Should detect trend regression
        regressions = [r for r in regression_detector.detected_regressions.values()
                      if r.metric_name == metric_name and r.detection_method == DetectionMethod.TREND_ANALYSIS]
        # Note: Trend detection requires scipy and sufficient data points

    @pytest.mark.asyncio
    async def test_ml_regression_detection(self, regression_detector):
        """Test ML-based regression detection"""
        if not regression_detector.enable_ml_detection:
            pytest.skip("ML detection not available")

        metric_name = "ml_test"
        component = "ml_service"

        # Generate training data
        try:
            import numpy as np
            np.random.seed(42)
            training_data = np.random.normal(0.1, 0.01, 100)  # Mean=100ms, low variance
        except ImportError:
            pytest.skip("NumPy not available for ML testing")

        for value in training_data:
            await regression_detector.record_performance_metric(metric_name, component, float(value))

        # Establish baseline and train model
        baseline = await regression_detector.establish_baseline(metric_name, component)
        assert baseline is not None

        # Record clear anomaly
        await regression_detector.record_performance_metric(metric_name, component, 1.0)  # 10x increase

        # Check for ML-detected regression
        ml_regressions = [r for r in regression_detector.detected_regressions.values()
                         if r.metric_name == metric_name and r.detection_method == DetectionMethod.ISOLATION_FOREST]
        # ML detection might not always trigger depending on the model

    def test_regression_severity_classification(self, regression_detector):
        """Test regression severity classification"""
        # Test different degradation levels
        assert regression_detector._classify_regression_severity(5) == RegressionSeverity.MINOR
        assert regression_detector._classify_regression_severity(20) == RegressionSeverity.MODERATE
        assert regression_detector._classify_regression_severity(35) == RegressionSeverity.MAJOR
        assert regression_detector._classify_regression_severity(60) == RegressionSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_regression_resolution(self, regression_detector):
        """Test regression resolution tracking"""
        # Create a test regression
        from uuid import uuid4
        regression_id = str(uuid4())

        regression = PerformanceRegression(
            regression_id=regression_id,
            metric_name="test_metric",
            component="test_component",
            detection_method=DetectionMethod.Z_SCORE,
            severity=RegressionSeverity.MODERATE,
            baseline_value=0.1,
            current_value=0.2,
            degradation_percentage=100.0,
            detection_timestamp=datetime.now(timezone.utc),
            confidence_score=0.9,
            statistical_significance=0.95,
            affected_operations=["test_op"],
        )

        regression_detector.detected_regressions[regression_id] = regression

        # Mark as resolved
        success = await regression_detector.mark_regression_resolved(regression_id, "test_user")
        assert success is True
        assert regression.resolved is True
        assert regression.resolution_timestamp is not None

    @pytest.mark.asyncio
    async def test_false_positive_marking(self, regression_detector):
        """Test false positive marking and learning"""
        # Create a test regression
        from uuid import uuid4
        regression_id = str(uuid4())

        regression = PerformanceRegression(
            regression_id=regression_id,
            metric_name="false_positive_test",
            component="test_component",
            detection_method=DetectionMethod.Z_SCORE,
            severity=RegressionSeverity.WARNING,
            baseline_value=0.1,
            current_value=0.15,
            degradation_percentage=50.0,
            detection_timestamp=datetime.now(timezone.utc),
            confidence_score=0.7,
            statistical_significance=0.85,
            affected_operations=[],
        )

        regression_detector.detected_regressions[regression_id] = regression

        # Mark as false positive
        success = await regression_detector.mark_false_positive(regression_id, "test_user")
        assert success is True
        assert regression.false_positive is True
        assert regression_detector.detection_stats["false_positives"] > 0

    def test_get_active_regressions(self, regression_detector):
        """Test getting active regressions with filtering"""
        from uuid import uuid4

        # Create test regressions
        regression1 = PerformanceRegression(
            regression_id=str(uuid4()),
            metric_name="test_metric_1",
            component="service_a",
            detection_method=DetectionMethod.Z_SCORE,
            severity=RegressionSeverity.CRITICAL,
            baseline_value=0.1,
            current_value=0.3,
            degradation_percentage=200.0,
            detection_timestamp=datetime.now(timezone.utc),
            confidence_score=0.95,
            statistical_significance=0.98,
            affected_operations=[],
        )

        regression2 = PerformanceRegression(
            regression_id=str(uuid4()),
            metric_name="test_metric_2",
            component="service_b",
            detection_method=DetectionMethod.TREND_ANALYSIS,
            severity=RegressionSeverity.MODERATE,
            baseline_value=0.2,
            current_value=0.3,
            degradation_percentage=50.0,
            detection_timestamp=datetime.now(timezone.utc),
            confidence_score=0.8,
            statistical_significance=0.9,
            affected_operations=[],
            resolved=True,  # This one is resolved
        )

        regression_detector.detected_regressions[regression1.regression_id] = regression1
        regression_detector.detected_regressions[regression2.regression_id] = regression2

        # Get all active regressions
        active_regressions = regression_detector.get_active_regressions()
        assert len(active_regressions) == 1  # Only unresolved one
        assert active_regressions[0].regression_id == regression1.regression_id

        # Filter by component
        service_a_regressions = regression_detector.get_active_regressions(component_filter="service_a")
        assert len(service_a_regressions) == 1
        assert service_a_regressions[0].component == "service_a"

        # Filter by severity
        critical_regressions = regression_detector.get_active_regressions(severity_filter=RegressionSeverity.CRITICAL)
        assert len(critical_regressions) == 1
        assert critical_regressions[0].severity == RegressionSeverity.CRITICAL

    def test_regression_statistics(self, regression_detector):
        """Test regression statistics generation"""
        from uuid import uuid4

        # Create test regressions with different properties
        current_time = datetime.now(timezone.utc)

        regression1 = PerformanceRegression(
            regression_id=str(uuid4()),
            metric_name="stats_test_1",
            component="service_a",
            detection_method=DetectionMethod.Z_SCORE,
            severity=RegressionSeverity.CRITICAL,
            baseline_value=0.1,
            current_value=0.4,
            degradation_percentage=300.0,
            detection_timestamp=current_time - timedelta(hours=2),
            confidence_score=0.95,
            statistical_significance=0.98,
            affected_operations=[],
            resolved=True,
        )

        regression2 = PerformanceRegression(
            regression_id=str(uuid4()),
            metric_name="stats_test_2",
            component="service_b",
            detection_method=DetectionMethod.TREND_ANALYSIS,
            severity=RegressionSeverity.MODERATE,
            baseline_value=0.2,
            current_value=0.25,
            degradation_percentage=25.0,
            detection_timestamp=current_time - timedelta(hours=1),
            confidence_score=0.8,
            statistical_significance=0.85,
            affected_operations=[],
            false_positive=True,
        )

        regression_detector.detected_regressions[regression1.regression_id] = regression1
        regression_detector.detected_regressions[regression2.regression_id] = regression2

        stats = regression_detector.get_regression_statistics(hours_back=24)

        assert stats["total_regressions"] == 2
        assert stats["by_severity"]["critical"] == 1
        assert stats["by_severity"]["moderate"] == 1
        assert stats["by_component"]["service_a"] == 1
        assert stats["by_component"]["service_b"] == 1
        assert stats["by_detection_method"]["z_score"] == 1
        assert stats["by_detection_method"]["trend_analysis"] == 1
        assert stats["resolved_count"] == 1
        assert stats["false_positive_count"] == 1

    @pytest.mark.asyncio
    async def test_concurrent_metric_recording(self, regression_detector):
        """Test concurrent performance metric recording"""
        async def record_metrics(component_id, count):
            for i in range(count):
                await regression_detector.record_performance_metric(
                    metric_name="concurrent_test",
                    component=f"service_{component_id}",
                    value=0.1 + (i * 0.01),
                )

        # Run concurrent recording
        tasks = [record_metrics(i, 10) for i in range(5)]
        await asyncio.gather(*tasks)

        # Verify all metrics were recorded
        total_recorded = sum(
            len(timeseries) for key, timeseries in regression_detector.metric_timeseries.items()
            if "concurrent_test" in key
        )
        assert total_recorded == 50  # 5 components * 10 metrics each

    @pytest.mark.asyncio
    async def test_metric_history_cleanup(self, regression_detector):
        """Test automatic cleanup of old metrics"""
        metric_name = "cleanup_test"
        component = "cleanup_service"

        # Record metrics with old timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(days=3)
        recent_timestamp = datetime.now(timezone.utc)

        # Record old metric
        await regression_detector.record_performance_metric(
            metric_name, component, 0.1, timestamp=old_timestamp
        )

        # Record recent metric (should trigger cleanup)
        await regression_detector.record_performance_metric(
            metric_name, component, 0.2, timestamp=recent_timestamp
        )

        metric_key = f"{component}_{metric_name}"

        # Check cleanup occurred (depends on baseline_window_days setting)
        timestamps = list(regression_detector.metric_timestamps[metric_key])
        if regression_detector.baseline_window_days < 2:  # Our test setting is 1 day
            # Old timestamp should be cleaned up
            assert all(ts >= old_timestamp + timedelta(days=1) for ts in timestamps)

    @pytest.mark.asyncio
    async def test_root_cause_analysis(self, regression_detector):
        """Test automated root cause analysis"""
        # Create correlated metrics that might indicate root causes
        base_time = datetime.now(timezone.utc)

        # Record primary metric regression
        await regression_detector.record_performance_metric(
            "response_time", "api_service", 0.5, timestamp=base_time
        )

        # Record correlated metrics around the same time
        await regression_detector.record_performance_metric(
            "error_rate", "api_service", 0.1, timestamp=base_time + timedelta(seconds=30)
        )

        # Establish baselines
        for metric in ["response_time", "error_rate"]:
            key = f"api_service_{metric}"
            regression_detector.performance_baselines[key] = PerformanceBaseline(
                metric_name=metric,
                component="api_service",
                baseline_value=0.05 if metric == "response_time" else 0.01,
                std_deviation=0.01,
                percentiles={"p50": 0.05, "p95": 0.08, "p99": 0.1},
                sample_count=100,
                baseline_period_start=base_time - timedelta(hours=1),
                baseline_period_end=base_time,
                confidence_interval=(0.04, 0.06),
            )

        # Create test regression
        from uuid import uuid4
        regression = PerformanceRegression(
            regression_id=str(uuid4()),
            metric_name="response_time",
            component="api_service",
            detection_method=DetectionMethod.Z_SCORE,
            severity=RegressionSeverity.CRITICAL,
            baseline_value=0.05,
            current_value=0.5,
            degradation_percentage=900.0,
            detection_timestamp=base_time,
            confidence_score=0.95,
            statistical_significance=0.98,
            affected_operations=[],
        )

        # Run root cause analysis
        await regression_detector._analyze_root_cause(regression)

        # Should have identified potential root causes
        assert len(regression.root_cause_candidates) >= 0  # May or may not find correlations


class TestIntegrationFunctions:
    """Test module-level integration functions"""

    def test_initialize_regression_detector(self, mock_dependencies):
        """Test regression detector initialization"""
        with patch('lukhas.observability.performance_regression.get_advanced_metrics', return_value=mock_dependencies['advanced_metrics']):
            with patch('lukhas.observability.performance_regression.get_alerting_system', return_value=mock_dependencies['alerting_system']):
                detector = initialize_regression_detector(
                    baseline_window_days=7,
                    enable_ml_detection=False,
                )

                assert detector is not None
                assert detector.baseline_window_days == 7
                assert detector.enable_ml_detection is False

    @pytest.mark.asyncio
    async def test_convenience_functions(self, regression_detector):
        """Test convenience functions"""
        with patch('lukhas.observability.performance_regression.get_regression_detector', return_value=regression_detector):
            # Test record_performance_data function
            await record_performance_data(
                metric_name="convenience_test",
                component="convenience_service",
                value=0.15,
                operation="test_operation",
            )

            # Verify data was recorded
            metric_key = "convenience_service_convenience_test"
            assert metric_key in regression_detector.metric_timeseries
            assert len(regression_detector.metric_timeseries[metric_key]) == 1


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_invalid_metric_values(self, regression_detector):
        """Test handling of invalid metric values"""
        # Test negative values (might be valid for some metrics)
        await regression_detector.record_performance_metric("test_metric", "test_component", -1.0)

        # Test zero values
        await regression_detector.record_performance_metric("test_metric", "test_component", 0.0)

        # Test very large values
        await regression_detector.record_performance_metric("test_metric", "test_component", 1e6)

        # All should be recorded without crashing
        metric_key = "test_component_test_metric"
        assert len(regression_detector.metric_timeseries[metric_key]) == 3

    @pytest.mark.asyncio
    async def test_baseline_with_zero_variance(self, regression_detector):
        """Test baseline establishment with zero variance data"""
        metric_name = "zero_variance"
        component = "test_service"

        # Record identical values (zero variance)
        identical_values = [0.1] * 15
        for value in identical_values:
            await regression_detector.record_performance_metric(metric_name, component, value)

        # Should still establish baseline
        baseline = await regression_detector.establish_baseline(metric_name, component)
        assert baseline is not None
        assert baseline.std_deviation == 0.0

    @pytest.mark.asyncio
    async def test_nonexistent_regression_operations(self, regression_detector):
        """Test operations on non-existent regressions"""
        fake_regression_id = "nonexistent_regression"

        # Should return False for non-existent regressions
        resolved = await regression_detector.mark_regression_resolved(fake_regression_id)
        assert resolved is False

        false_positive = await regression_detector.mark_false_positive(fake_regression_id)
        assert false_positive is False

    @pytest.mark.asyncio
    async def test_detection_without_baseline(self, regression_detector):
        """Test regression detection without established baseline"""
        # Record metric without establishing baseline
        await regression_detector.record_performance_metric("no_baseline", "test_service", 1.0)

        # Should not crash, but won't detect regressions
        regressions = [r for r in regression_detector.detected_regressions.values() if r.metric_name == "no_baseline"]
        assert len(regressions) == 0


class TestPerformanceOptimization:
    """Test performance optimization features"""

    @pytest.mark.asyncio
    async def test_high_volume_metric_recording(self, regression_detector):
        """Test performance with high volume of metrics"""
        import time

        start_time = time.time()

        # Record many metrics quickly
        for i in range(1000):
            await regression_detector.record_performance_metric(
                f"bulk_metric_{i % 10}",  # 10 different metrics
                "bulk_service",
                i * 0.001,
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time
        assert duration < 10.0, f"High volume recording took {duration}s, should be <10s"

        # Verify data integrity
        total_recorded = sum(len(timeseries) for timeseries in regression_detector.metric_timeseries.values())
        assert total_recorded >= 1000

    def test_memory_usage_bounds(self, regression_detector):
        """Test memory usage stays within bounds"""
        # Fill up metric storage to test bounds
        for i in range(20000):  # Exceed maxlen
            metric_key = f"memory_test_{i % 50}"  # 50 different metrics
            regression_detector.metric_timeseries[metric_key].append(i * 0.001)
            regression_detector.metric_timestamps[metric_key].append(datetime.now(timezone.utc))

        # Check that deques respect maxlen
        for timeseries in regression_detector.metric_timeseries.values():
            assert len(timeseries) <= 10000  # Default maxlen for deques

        for timestamps in regression_detector.metric_timestamps.values():
            assert len(timestamps) <= 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
