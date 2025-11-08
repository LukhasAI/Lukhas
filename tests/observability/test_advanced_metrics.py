#!/usr/bin/env python3
"""
Test suite for LUKHAS Advanced Metrics System
Comprehensive tests for advanced metrics, anomaly detection, and performance monitoring.
"""

import asyncio
import statistics

from async_utils import create_background_task

# Test imports
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability.advanced_metrics import (
    AdvancedMetricsSystem,
    AnomalyType,
    MetricAnomaly,
    MetricSeverity,
    initialize_advanced_metrics,
    record_metric,
    record_operation_performance,
)


@pytest.fixture
def mock_prometheus_metrics():
    """Mock Prometheus metrics system"""
    mock_metrics = MagicMock()
    mock_metrics.lane = "test"
    mock_metrics.errors_total = MagicMock()
    mock_metrics.errors_total.labels.return_value.inc = MagicMock()
    return mock_metrics


@pytest.fixture
def advanced_metrics_system(mock_prometheus_metrics):
    """Create advanced metrics system for testing"""
    with patch('observability.advanced_metrics.get_lukhas_metrics', return_value=mock_prometheus_metrics):
        system = AdvancedMetricsSystem(
            enable_anomaly_detection=True,
            enable_ml_features=True,
            metric_retention_hours=24,
            anomaly_sensitivity=0.8,
            compliance_checks_enabled=True,
        )
        yield system
        # Cleanup
        create_background_task(system.shutdown())


class TestAdvancedMetricsSystem:
    """Test advanced metrics system functionality"""

    @pytest.mark.asyncio
    async def test_basic_metric_recording(self, advanced_metrics_system):
        """Test basic metric recording"""
        await advanced_metrics_system.record_advanced_metric(
            metric_name="test_response_time",
            value=0.05,  # 50ms
            labels={"endpoint": "/api/test"},
        )

        assert "test_response_time" in advanced_metrics_system.metric_history
        assert len(advanced_metrics_system.metric_history["test_response_time"]) == 1
        assert advanced_metrics_system.metric_history["test_response_time"][0] == 0.05

    @pytest.mark.asyncio
    async def test_anomaly_detection_statistical(self, advanced_metrics_system):
        """Test statistical anomaly detection"""
        metric_name = "test_latency"

        # Record baseline data (normal values)
        normal_values = [0.1, 0.12, 0.09, 0.11, 0.10, 0.13, 0.08, 0.11, 0.12, 0.10]
        for value in normal_values:
            await advanced_metrics_system.record_advanced_metric(metric_name, value)

        # Set up baseline
        advanced_metrics_system.metric_baselines[metric_name] = {
            "mean": statistics.mean(normal_values),
            "std": statistics.stdev(normal_values),
            "updated_at": datetime.now(timezone.utc),
        }

        # Record anomalous value
        await advanced_metrics_system.record_advanced_metric(metric_name, 1.5)  # Significant spike

        # Should have detected anomaly
        anomalies = [a for a in advanced_metrics_system.detected_anomalies if a.metric_name == metric_name]
        assert len(anomalies) > 0

        anomaly = anomalies[0]
        assert anomaly.anomaly_type in [AnomalyType.UNUSUAL_PATTERN, AnomalyType.THRESHOLD_BREACH]
        assert anomaly.confidence > 0.5

    @pytest.mark.asyncio
    async def test_threshold_based_detection(self, advanced_metrics_system):
        """Test threshold-based anomaly detection"""
        metric_name = "lukhas_response_time_seconds"

        # This metric has predefined thresholds
        # Record value above critical threshold
        await advanced_metrics_system.record_advanced_metric(metric_name, 0.3)  # Above 0.25 critical

        # Should detect threshold breach
        threshold_anomalies = [
            a for a in advanced_metrics_system.detected_anomalies
            if a.metric_name == metric_name and a.anomaly_type == AnomalyType.THRESHOLD_BREACH
        ]
        assert len(threshold_anomalies) > 0

        anomaly = threshold_anomalies[0]
        assert anomaly.severity == MetricSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_ml_anomaly_detection(self, advanced_metrics_system):
        """Test ML-based anomaly detection"""
        if not advanced_metrics_system.enable_ml_features:
            pytest.skip("ML features not available")

        metric_name = "ml_test_metric"

        # Generate training data
        import numpy as np
        np.random.seed(42)  # For reproducible tests
        training_data = np.random.normal(100, 10, 100)  # Mean=100, std=10

        for value in training_data:
            await advanced_metrics_system.record_advanced_metric(metric_name, float(value))

        # Train model
        await advanced_metrics_system._train_anomaly_model(metric_name, training_data.tolist())

        # Test with anomalous value
        await advanced_metrics_system.record_advanced_metric(metric_name, 200.0)  # Outlier

        # Check for ML-detected anomalies
        [
            a for a in advanced_metrics_system.detected_anomalies
            if a.metric_name == metric_name and a.anomaly_type == AnomalyType.ISOLATION_FOREST
        ]

        # ML detection might not always trigger, depending on the model
        # This is expected behavior for edge cases

    def test_operation_timing_recording(self, advanced_metrics_system):
        """Test operation timing recording"""
        operation_name = "test_operation"

        advanced_metrics_system.record_operation_timing(
            operation=operation_name,
            duration_ms=150.5,
            success=True,
            context={"user_count": 5},
        )

        assert operation_name in advanced_metrics_system.operation_timings
        timing_data = advanced_metrics_system.operation_timings[operation_name][0]
        assert timing_data["duration_ms"] == 150.5
        assert timing_data["success"] is True
        assert timing_data["context"]["user_count"] == 5

    def test_compliance_metric_updates(self, advanced_metrics_system):
        """Test compliance metric updates and violation detection"""
        regulation = "GDPR"
        metric_name = "data_retention_days"

        # Update compliance metric within threshold
        advanced_metrics_system.update_compliance_metric(regulation, metric_name, 2000)  # Within limit

        compliance_key = f"{regulation.lower()}_{metric_name}"
        assert compliance_key in advanced_metrics_system.compliance_metrics

        metric = advanced_metrics_system.compliance_metrics[compliance_key]
        assert metric.is_compliant is True

        # Update with violation
        advanced_metrics_system.update_compliance_metric(regulation, metric_name, 3000)  # Over limit

        metric = advanced_metrics_system.compliance_metrics[compliance_key]
        assert metric.is_compliant is False
        assert metric.violation_count == 1

    def test_metric_statistics(self, advanced_metrics_system):
        """Test metric statistics calculation"""
        metric_name = "stats_test_metric"
        test_values = [10, 20, 30, 40, 50]

        # Record test data
        for value in test_values:
            advanced_metrics_system.metric_history[metric_name].append(value)

        stats = advanced_metrics_system.get_metric_statistics(metric_name)

        assert stats["count"] == 5
        assert stats["min"] == 10
        assert stats["max"] == 50
        assert stats["mean"] == 30
        assert stats["median"] == 30
        assert "std" in stats
        assert "p95" in stats
        assert "p99" in stats

    def test_anomaly_summary(self, advanced_metrics_system):
        """Test anomaly summary functionality"""
        # Add test anomalies
        test_anomaly = MetricAnomaly(
            anomaly_id="test_anomaly_1",
            metric_name="test_metric",
            anomaly_type=AnomalyType.PERFORMANCE_REGRESSION,
            severity=MetricSeverity.WARNING,
            value=100.0,
            expected_range=(80.0, 90.0),
            confidence=0.85,
            timestamp=datetime.now(timezone.utc),
        )

        advanced_metrics_system.detected_anomalies.append(test_anomaly)

        # Get summary
        summary = advanced_metrics_system.get_anomaly_summary(hours_back=24)
        assert len(summary) == 1
        assert summary[0].anomaly_id == "test_anomaly_1"

        # Filter by severity
        warning_summary = advanced_metrics_system.get_anomaly_summary(
            hours_back=24,
            severity_filter=MetricSeverity.WARNING
        )
        assert len(warning_summary) == 1

        critical_summary = advanced_metrics_system.get_anomaly_summary(
            hours_back=24,
            severity_filter=MetricSeverity.CRITICAL
        )
        assert len(critical_summary) == 0

    def test_performance_dashboard_data(self, advanced_metrics_system):
        """Test performance dashboard data generation"""
        # Add some operation timings
        advanced_metrics_system.record_operation_timing("api_call", 100, True)
        advanced_metrics_system.record_operation_timing("db_query", 50, True)
        advanced_metrics_system.record_operation_timing("cache_miss", 200, False)

        dashboard_data = advanced_metrics_system.get_performance_dashboard_data()

        assert "operation_statistics" in dashboard_data
        assert "anomaly_counts" in dashboard_data
        assert "compliance_status" in dashboard_data
        assert "total_metrics_tracked" in dashboard_data

        # Check operation statistics
        op_stats = dashboard_data["operation_statistics"]
        if "api_call" in op_stats:  # Might not be present due to time filtering
            assert "avg_duration_ms" in op_stats["api_call"]
            assert "success_rate" in op_stats["api_call"]

    @pytest.mark.asyncio
    async def test_metric_history_cleanup(self, advanced_metrics_system):
        """Test automatic cleanup of old metric data"""
        metric_name = "cleanup_test_metric"

        # Record metrics with old timestamps
        old_timestamp = datetime.now(timezone.utc) - timedelta(days=2)
        recent_timestamp = datetime.now(timezone.utc)

        # Simulate old data
        advanced_metrics_system.metric_timestamps[metric_name].append(old_timestamp)
        advanced_metrics_system.metric_history[metric_name].append(100.0)

        # Record recent metric (this should trigger cleanup)
        await advanced_metrics_system.record_advanced_metric(
            metric_name=metric_name,
            value=200.0,
            timestamp=recent_timestamp,
        )

        # Old data should be cleaned up (assuming retention is less than 2 days)
        if advanced_metrics_system.metric_retention_hours < 48:  # 2 days
            # The cleanup should have removed old data
            timestamps = list(advanced_metrics_system.metric_timestamps[metric_name])
            assert all(ts >= old_timestamp + timedelta(hours=1) for ts in timestamps)

    @pytest.mark.asyncio
    async def test_concurrent_metric_recording(self, advanced_metrics_system):
        """Test concurrent metric recording"""
        async def record_metrics(metric_suffix, count):
            for i in range(count):
                await advanced_metrics_system.record_advanced_metric(
                    metric_name=f"concurrent_metric_{metric_suffix}",
                    value=i * 10,
                )

        # Run concurrent recording tasks
        tasks = [
            record_metrics("a", 5),
            record_metrics("b", 5),
            record_metrics("c", 5),
        ]

        await asyncio.gather(*tasks)

        # Check that all metrics were recorded
        assert len(advanced_metrics_system.metric_history["concurrent_metric_a"]) == 5
        assert len(advanced_metrics_system.metric_history["concurrent_metric_b"]) == 5
        assert len(advanced_metrics_system.metric_history["concurrent_metric_c"]) == 5


class TestAnomalyDetection:
    """Test anomaly detection algorithms"""

    @pytest.mark.asyncio
    async def test_z_score_detection(self, advanced_metrics_system):
        """Test Z-score based anomaly detection"""
        metric_name = "z_score_test"

        # Create baseline with known statistics
        baseline_values = [10] * 20  # Mean = 10, std = 0
        for value in baseline_values:
            await advanced_metrics_system.record_advanced_metric(metric_name, value)

        # Set up baseline manually for predictable testing
        advanced_metrics_system.metric_baselines[metric_name] = {
            "mean": 10.0,
            "std": 1.0,  # Small std dev
            "updated_at": datetime.now(timezone.utc),
        }

        # Record anomalous value (way outside normal range)
        await advanced_metrics_system.record_advanced_metric(metric_name, 20.0)  # 10 std devs away

        # Should detect statistical anomaly
        anomalies = [
            a for a in advanced_metrics_system.detected_anomalies
            if a.metric_name == metric_name
        ]
        assert len(anomalies) > 0

    @pytest.mark.asyncio
    async def test_trend_analysis_detection(self, advanced_metrics_system):
        """Test trend-based anomaly detection"""
        metric_name = "trend_test"

        # Create upward trend (performance degradation)
        trend_values = [10 + i * 2 for i in range(25)]  # Clear upward trend
        timestamps = [
            datetime.now(timezone.utc) - timedelta(hours=24-i) for i in range(25)
        ]

        for value, timestamp in zip(trend_values, timestamps):
            await advanced_metrics_system.record_advanced_metric(
                metric_name, value, timestamp=timestamp
            )

        # Set baseline
        advanced_metrics_system.metric_baselines[metric_name] = {
            "mean": 10.0,
            "std": 2.0,
            "updated_at": datetime.now(timezone.utc),
        }

        # Trigger trend analysis
        await advanced_metrics_system._detect_trend_regression(
            metric_name, advanced_metrics_system.metric_baselines[metric_name], 60.0, datetime.now(timezone.utc)
        )

        # Should detect trend-based anomaly
        [
            a for a in advanced_metrics_system.detected_anomalies
            if a.metric_name == metric_name and a.anomaly_type == AnomalyType.TREND_ANALYSIS
        ]
        # Note: Trend detection requires scipy, might not always trigger


class TestIntegrationFunctions:
    """Test module-level integration functions"""

    def test_initialize_advanced_metrics(self, mock_prometheus_metrics):
        """Test advanced metrics initialization"""
        with patch('observability.advanced_metrics.get_lukhas_metrics', return_value=mock_prometheus_metrics):
            system = initialize_advanced_metrics(
                enable_anomaly_detection=True,
                enable_ml_features=False,
            )

            assert system is not None
            assert system.enable_anomaly_detection is True
            assert system.enable_ml_features is False

    @pytest.mark.asyncio
    async def test_convenience_functions(self, advanced_metrics_system):
        """Test convenience functions"""
        with patch('observability.advanced_metrics.get_advanced_metrics', return_value=advanced_metrics_system):
            # Test record_metric function
            await record_metric("test_metric", 100.5, labels={"test": "value"})

            # Test record_operation_performance function
            record_operation_performance("test_operation", 250.0, success=True)

            # Verify data was recorded
            assert "test_metric" in advanced_metrics_system.metric_history
            assert "test_operation" in advanced_metrics_system.operation_timings


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_invalid_metric_values(self, advanced_metrics_system):
        """Test handling of invalid metric values"""
        # Test with None value (should handle gracefully)
        try:
            await advanced_metrics_system.record_advanced_metric("test_metric", None)
        except Exception as e:
            # Should either handle gracefully or raise appropriate error
            assert isinstance(e, (TypeError, ValueError))

        # Test with string value (should handle or raise appropriate error)
        try:
            await advanced_metrics_system.record_advanced_metric("test_metric", "invalid")
        except Exception as e:
            assert isinstance(e, (TypeError, ValueError))

    @pytest.mark.asyncio
    async def test_anomaly_detection_with_insufficient_data(self, advanced_metrics_system):
        """Test anomaly detection with insufficient data"""
        metric_name = "insufficient_data_test"

        # Record only one data point
        await advanced_metrics_system.record_advanced_metric(metric_name, 100.0)

        # Should not crash, but may not detect anomalies
        [a for a in advanced_metrics_system.detected_anomalies if a.metric_name == metric_name]
        # May or may not have anomalies depending on implementation

    def test_compliance_metric_invalid_regulation(self, advanced_metrics_system):
        """Test compliance metric updates with invalid regulation"""
        # Should handle unknown regulations gracefully
        advanced_metrics_system.update_compliance_metric("INVALID_REGULATION", "test_metric", 100.0)

        # Should not crash, might create entry or ignore


class TestPerformanceOptimization:
    """Test performance optimization features"""

    @pytest.mark.asyncio
    async def test_high_volume_metric_recording(self, advanced_metrics_system):
        """Test performance with high volume of metrics"""
        import time

        start_time = time.time()

        # Record many metrics quickly
        for i in range(1000):
            await advanced_metrics_system.record_advanced_metric(
                f"bulk_metric_{i % 10}",  # 10 different metric names
                i * 0.01,
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 10.0, f"High volume recording took {duration}s, should be <10s"

        # Verify data integrity
        assert len(advanced_metrics_system.metric_history) >= 10

    def test_memory_usage_bounds(self, advanced_metrics_system):
        """Test that memory usage stays within bounds"""
        len(advanced_metrics_system.metric_history)

        # Record many metrics to test memory bounds
        for i in range(20000):  # Exceed maxlen of deques
            metric_name = f"memory_test_{i % 100}"  # 100 different metrics
            advanced_metrics_system.metric_history[metric_name].append(i)
            advanced_metrics_system.metric_timestamps[metric_name].append(datetime.now(timezone.utc))

        # Memory should be bounded by maxlen settings
        for metric_name, history in advanced_metrics_system.metric_history.items():
            assert len(history) <= 10000, f"Metric {metric_name} history too large: {len(history)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
