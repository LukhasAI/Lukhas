"""
T4/0.01% Excellence SLO Burn Rate Tests

Validates burn rate calculations for T4 excellence SLOs with 4 errors/1h and 2 errors/6h thresholds.
Production-ready monitoring for Guardian (<100ms), Memory (<1ms), Orchestrator (<250ms) components.
"""

import pytest
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from dataclasses import dataclass
from unittest.mock import Mock, patch
import json
import tempfile
import os


@dataclass
class SLOMetric:
    """SLO metric with burn rate calculation"""
    name: str
    slo_target_ms: float
    error_budget: float
    burn_rate_4_1h: float  # 4 errors in 1 hour
    burn_rate_2_6h: float  # 2 errors in 6 hours


class BurnRateCalculator:
    """Production burn rate calculator with T4 excellence thresholds"""

    SLO_TARGETS = {
        "guardian_latency": SLOMetric("guardian_latency", 100.0, 0.01, 4.0, 2.0),
        "memory_latency": SLOMetric("memory_latency", 1000.0, 0.01, 4.0, 2.0),
        "orchestrator_latency": SLOMetric("orchestrator_latency", 250000.0, 0.01, 4.0, 2.0),
    }

    def __init__(self, metrics_store: Dict[str, List[Tuple[datetime, float]]] = None):
        self.metrics_store = metrics_store or {}

    def add_metric(self, metric_name: str, timestamp: datetime, value_ms: float):
        """Add metric observation"""
        if metric_name not in self.metrics_store:
            self.metrics_store[metric_name] = []
        self.metrics_store[metric_name].append((timestamp, value_ms))

    def calculate_error_rate(self, metric_name: str, window_hours: int) -> float:
        """Calculate error rate over time window"""
        if metric_name not in self.SLO_TARGETS:
            raise ValueError(f"Unknown metric: {metric_name}")

        slo = self.SLO_TARGETS[metric_name]
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=window_hours)

        observations = self.metrics_store.get(metric_name, [])
        recent_obs = [(ts, val) for ts, val in observations if ts >= cutoff]

        if not recent_obs:
            return 0.0

        violations = sum(1 for _, val in recent_obs if val > slo.slo_target_ms)
        return violations / len(recent_obs)

    def calculate_burn_rate(self, metric_name: str, window_hours: int) -> float:
        """Calculate SLO burn rate"""
        error_rate = self.calculate_error_rate(metric_name, window_hours)
        slo = self.SLO_TARGETS[metric_name]

        # Burn rate = current error rate / error budget
        return error_rate / slo.error_budget if slo.error_budget > 0 else float('inf')

    def check_burn_rate_violation(self, metric_name: str) -> Dict[str, bool]:
        """Check if burn rate exceeds thresholds"""
        slo = self.SLO_TARGETS[metric_name]

        burn_1h = self.calculate_burn_rate(metric_name, 1)
        burn_6h = self.calculate_burn_rate(metric_name, 6)

        return {
            "1h_violation": burn_1h > slo.burn_rate_4_1h,
            "6h_violation": burn_6h > slo.burn_rate_2_6h,
            "burn_rate_1h": burn_1h,
            "burn_rate_6h": burn_6h,
        }


class TestBurnRateCalculation:
    """Test burn rate calculations for T4 excellence SLOs"""

    def test_burn_rate_calculator_initialization(self):
        """Test burn rate calculator initializes correctly"""
        calc = BurnRateCalculator()
        assert len(calc.SLO_TARGETS) == 3
        assert "guardian_latency" in calc.SLO_TARGETS
        assert "memory_latency" in calc.SLO_TARGETS
        assert "orchestrator_latency" in calc.SLO_TARGETS

    def test_slo_targets_configuration(self):
        """Test SLO targets match T4 excellence requirements"""
        calc = BurnRateCalculator()

        # Guardian: <100ms SLA
        guardian = calc.SLO_TARGETS["guardian_latency"]
        assert guardian.slo_target_ms == 100.0
        assert guardian.error_budget == 0.01  # 1% error budget

        # Memory: <1ms SLA
        memory = calc.SLO_TARGETS["memory_latency"]
        assert memory.slo_target_ms == 1000.0  # 1ms in microseconds
        assert memory.error_budget == 0.01

        # Orchestrator: <250ms SLA
        orchestrator = calc.SLO_TARGETS["orchestrator_latency"]
        assert orchestrator.slo_target_ms == 250000.0  # 250ms in microseconds
        assert orchestrator.error_budget == 0.01

    def test_add_metric_observation(self):
        """Test adding metric observations"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        calc.add_metric("guardian_latency", now, 80.0)
        calc.add_metric("guardian_latency", now, 120.0)  # SLO violation

        assert len(calc.metrics_store["guardian_latency"]) == 2
        assert calc.metrics_store["guardian_latency"][0] == (now, 80.0)
        assert calc.metrics_store["guardian_latency"][1] == (now, 120.0)

    def test_error_rate_calculation_no_violations(self):
        """Test error rate calculation with no SLO violations"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # All observations within SLO
        for i in range(10):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 80.0)

        error_rate = calc.calculate_error_rate("guardian_latency", 1)
        assert error_rate == 0.0

    def test_error_rate_calculation_with_violations(self):
        """Test error rate calculation with SLO violations"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # 2 violations out of 10 observations = 20% error rate
        for i in range(8):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 80.0)
        for i in range(2):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i+8), 150.0)  # violation

        error_rate = calc.calculate_error_rate("guardian_latency", 1)
        assert error_rate == 0.2  # 20%

    def test_burn_rate_calculation(self):
        """Test burn rate calculation formula"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # 1 violation out of 100 observations = 1% error rate
        # Burn rate = 1% / 1% error budget = 1.0
        for i in range(99):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 80.0)
        calc.add_metric("guardian_latency", now, 150.0)  # 1 violation

        burn_rate = calc.calculate_burn_rate("guardian_latency", 2)
        assert burn_rate == 1.0

    def test_burn_rate_violation_detection_1h_window(self):
        """Test 1-hour burn rate violation detection"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Add 5 violations in 1 hour (exceeds 4 error threshold)
        for i in range(95):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 80.0)
        for i in range(5):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 150.0)

        result = calc.check_burn_rate_violation("guardian_latency")
        assert result["1h_violation"] is True
        assert result["burn_rate_1h"] > 4.0

    def test_burn_rate_violation_detection_6h_window(self):
        """Test 6-hour burn rate violation detection"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Add 3 violations in 6 hours (exceeds 2 error threshold)
        for i in range(97):
            calc.add_metric("guardian_latency", now - timedelta(hours=i/20), 80.0)
        for i in range(3):
            calc.add_metric("guardian_latency", now - timedelta(hours=i), 150.0)

        result = calc.check_burn_rate_violation("guardian_latency")
        assert result["6h_violation"] is True
        assert result["burn_rate_6h"] > 2.0

    def test_no_burn_rate_violation(self):
        """Test no burn rate violation when within thresholds"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Add minimal violations within thresholds
        for i in range(98):
            calc.add_metric("guardian_latency", now - timedelta(hours=i/20), 80.0)
        for i in range(2):  # Only 2 violations, within 6h threshold
            calc.add_metric("guardian_latency", now - timedelta(hours=i), 150.0)

        result = calc.check_burn_rate_violation("guardian_latency")
        assert result["1h_violation"] is False
        assert result["6h_violation"] is False

    def test_all_metrics_burn_rate_monitoring(self):
        """Test burn rate monitoring for all T4 excellence metrics"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Test each metric individually
        metrics_to_test = [
            ("guardian_latency", 100.0, 150.0),   # Target: 100ms, violation: 150ms
            ("memory_latency", 1000.0, 1500.0),   # Target: 1ms, violation: 1.5ms
            ("orchestrator_latency", 250000.0, 300000.0)  # Target: 250ms, violation: 300ms
        ]

        for metric_name, target, violation_value in metrics_to_test:
            # Clear previous data
            calc.metrics_store[metric_name] = []

            # Add normal observations
            for i in range(95):
                calc.add_metric(metric_name, now - timedelta(minutes=i), target - 10)

            # Add violations exceeding 1h threshold
            for i in range(5):
                calc.add_metric(metric_name, now - timedelta(minutes=i), violation_value)

            result = calc.check_burn_rate_violation(metric_name)
            assert result["1h_violation"] is True, f"Failed for {metric_name}"

    def test_time_window_filtering(self):
        """Test that old observations don't affect burn rate calculations"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Add old violations (outside 1h window)
        for i in range(10):
            calc.add_metric("guardian_latency", now - timedelta(hours=2), 150.0)

        # Add recent good observations (within 1h window)
        for i in range(60):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 80.0)

        result = calc.check_burn_rate_violation("guardian_latency")
        assert result["1h_violation"] is False  # Old violations should not count
        assert result["6h_violation"] is True   # But should affect 6h window

    @pytest.mark.performance
    def test_burn_rate_calculation_performance(self):
        """Test burn rate calculation performance for large datasets"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Add large number of observations
        start_time = time.perf_counter()
        for i in range(10000):
            calc.add_metric("guardian_latency", now - timedelta(seconds=i), 80.0)

        # Measure burn rate calculation time
        calc_start = time.perf_counter()
        result = calc.check_burn_rate_violation("guardian_latency")
        calc_time = time.perf_counter() - calc_start

        # Should complete in reasonable time (<100ms)
        assert calc_time < 0.1
        assert result["1h_violation"] is False

    def test_unknown_metric_handling(self):
        """Test handling of unknown metrics"""
        calc = BurnRateCalculator()

        with pytest.raises(ValueError, match="Unknown metric"):
            calc.calculate_error_rate("unknown_metric", 1)

    def test_empty_metrics_store(self):
        """Test burn rate calculation with empty metrics store"""
        calc = BurnRateCalculator()

        error_rate = calc.calculate_error_rate("guardian_latency", 1)
        assert error_rate == 0.0

        burn_rate = calc.calculate_burn_rate("guardian_latency", 1)
        assert burn_rate == 0.0


class TestSLOBurnRateIntegration:
    """Integration tests for SLO burn rate monitoring with real scenarios"""

    def test_realistic_guardian_performance_scenario(self):
        """Test realistic Guardian performance with T4 excellence validation"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Simulate realistic Guardian latency distribution
        # 95% of requests under 80ms, 4% at 90-100ms, 1% over 100ms (SLO violations)
        observations = []

        # 95% fast responses
        for i in range(950):
            observations.append((now - timedelta(seconds=i*3.6), 75.0 + (i % 20)))

        # 4% borderline responses
        for i in range(40):
            observations.append((now - timedelta(seconds=i*3.6 + 950*3.6), 95.0))

        # 1% SLO violations
        for i in range(10):
            observations.append((now - timedelta(seconds=i*3.6 + 990*3.6), 150.0))

        # Add all observations
        for timestamp, latency in observations:
            calc.add_metric("guardian_latency", timestamp, latency)

        result = calc.check_burn_rate_violation("guardian_latency")

        # With 1% error rate and 1% error budget, burn rate should be ~1.0
        assert 0.8 <= result["burn_rate_1h"] <= 1.2
        assert result["1h_violation"] is False  # Within acceptable range

    def test_slo_burn_rate_alerting_thresholds(self):
        """Test SLO burn rate alerting matches production requirements"""
        calc = BurnRateCalculator()

        # Validate burn rate thresholds match PHASE_MATRIX requirements
        for metric_name, slo in calc.SLO_TARGETS.items():
            assert slo.burn_rate_4_1h == 4.0, f"{metric_name} 1h threshold incorrect"
            assert slo.burn_rate_2_6h == 2.0, f"{metric_name} 6h threshold incorrect"
            assert slo.error_budget == 0.01, f"{metric_name} error budget incorrect"

    def test_multi_metric_burn_rate_correlation(self):
        """Test burn rate correlation across multiple T4 excellence metrics"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Simulate correlated performance degradation across all components
        metrics = ["guardian_latency", "memory_latency", "orchestrator_latency"]
        targets = [100.0, 1000.0, 250000.0]
        violation_values = [200.0, 2000.0, 500000.0]

        for metric, target, violation in zip(metrics, targets, violation_values):
            # Normal performance
            for i in range(90):
                calc.add_metric(metric, now - timedelta(minutes=i), target * 0.8)

            # Correlated degradation
            for i in range(10):
                calc.add_metric(metric, now - timedelta(minutes=i), violation)

        # All metrics should show burn rate violations
        for metric in metrics:
            result = calc.check_burn_rate_violation(metric)
            assert result["1h_violation"] is True, f"{metric} should show violation"

    def test_burn_rate_temporal_analysis(self):
        """Test burn rate analysis over different temporal windows"""
        calc = BurnRateCalculator()
        now = datetime.now(timezone.utc)

        # Create scenario with recent improvement after earlier problems
        # Hours 3-6: High error rate (old)
        for i in range(50):
            calc.add_metric("guardian_latency", now - timedelta(hours=3 + i/12.5), 150.0)

        # Hours 1-3: Medium error rate
        for i in range(60):
            calc.add_metric("guardian_latency", now - timedelta(hours=1 + i/30), 120.0)

        # Last hour: Good performance
        for i in range(58):
            calc.add_metric("guardian_latency", now - timedelta(minutes=i), 80.0)
        for i in range(2):  # Minimal violations
            calc.add_metric("guardian_latency", now - timedelta(minutes=i+58), 110.0)

        result = calc.check_burn_rate_violation("guardian_latency")

        # Should show recovery: 1h window good, 6h window still affected
        assert result["1h_violation"] is False  # Recent recovery
        assert result["6h_violation"] is True   # Historical problems still impact 6h window


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])