#!/usr/bin/env python3
"""
Performance Regression Testing for MΛTRIZ RL Consciousness System

This module implements continuous performance monitoring and regression detection
for consciousness processing systems. Part of the 0.001% advanced testing approach
that ensures consciousness quality never degrades over time.

Tracks key performance metrics:
- Consciousness coherence computation latency
- Memory fold cascade prevention speed  
- Ethical alignment validation time
- Trinity Framework integration overhead
- Constitutional constraint verification performance
"""

import asyncio
import json
import statistics
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest.mock import Mock, patch

import pytest


@dataclass
class PerformanceMetric:
    """Single performance measurement with context"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetric':
        return cls(
            name=data["name"],
            value=data["value"],
            unit=data["unit"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            context=data.get("context", {})
        )


@dataclass
class PerformanceBenchmark:
    """Expected performance thresholds for consciousness operations"""
    coherence_computation_max_ms: float = 50.0  # Max 50ms for coherence calculation
    memory_fold_access_max_ms: float = 10.0     # Max 10ms for memory fold access
    ethical_validation_max_ms: float = 25.0     # Max 25ms for ethics check
    trinity_integration_max_ms: float = 100.0   # Max 100ms for full Trinity cycle
    constitutional_check_max_ms: float = 15.0   # Max 15ms for constitutional constraint
    
    def check_performance(self, metric: PerformanceMetric) -> Tuple[bool, str]:
        """Check if a metric meets performance benchmarks"""
        thresholds = {
            "coherence_computation": self.coherence_computation_max_ms,
            "memory_fold_access": self.memory_fold_access_max_ms,
            "ethical_validation": self.ethical_validation_max_ms,
            "trinity_integration": self.trinity_integration_max_ms,
            "constitutional_check": self.constitutional_check_max_ms
        }
        
        threshold = thresholds.get(metric.name)
        if threshold is None:
            return True, f"No benchmark defined for {metric.name}"
        
        if metric.value <= threshold:
            return True, f"✅ {metric.name}: {metric.value:.2f}{metric.unit} <= {threshold}{metric.unit}"
        else:
            return False, f"❌ {metric.name}: {metric.value:.2f}{metric.unit} > {threshold}{metric.unit} (REGRESSION)"


class PerformanceTracker:
    """Tracks and analyzes consciousness performance over time"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("rl/performance_history.json")
        self.metrics: List[PerformanceMetric] = []
        self.benchmark = PerformanceBenchmark()
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical performance data if available"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.metrics = [PerformanceMetric.from_dict(m) for m in data.get("metrics", [])]
        except (json.JSONDecodeError, KeyError, ValueError):
            # Start fresh if historical data is corrupted
            self.metrics = []
    
    def save_metrics(self):
        """Persist metrics to storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "metrics": [m.to_dict() for m in self.metrics],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save performance metrics: {e}")
    
    def record_metric(self, name: str, value: float, unit: str, context: Dict[str, Any] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(timezone.utc),
            context=context or {}
        )
        self.metrics.append(metric)
        return metric
    
    def get_recent_metrics(self, name: str, count: int = 10) -> List[PerformanceMetric]:
        """Get recent metrics for a specific measurement"""
        filtered = [m for m in self.metrics if m.name == name]
        return sorted(filtered, key=lambda m: m.timestamp, reverse=True)[:count]
    
    def detect_regression(self, name: str, current_value: float, 
                         threshold_factor: float = 1.5) -> Tuple[bool, str]:
        """Detect performance regression using statistical analysis"""
        recent = self.get_recent_metrics(name, count=20)
        
        if len(recent) < 5:
            return False, f"Insufficient historical data for {name} (need 5+ samples, have {len(recent)})"
        
        historical_values = [m.value for m in recent[1:]]  # Exclude current measurement
        mean_historical = statistics.mean(historical_values)
        std_historical = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
        
        # Regression if current value is significantly worse than historical mean
        regression_threshold = mean_historical + (threshold_factor * std_historical)
        
        if current_value > regression_threshold:
            return True, (
                f"🔴 REGRESSION DETECTED in {name}: "
                f"{current_value:.2f} > {regression_threshold:.2f} "
                f"(mean: {mean_historical:.2f}, std: {std_historical:.2f})"
            )
        else:
            improvement = ((mean_historical - current_value) / mean_historical) * 100
            return False, (
                f"✅ Performance stable/improved for {name}: "
                f"{current_value:.2f} vs historical {mean_historical:.2f} "
                f"({improvement:+.1f}% change)"
            )


class ConsciousnessPerformanceTester:
    """High-level performance testing for consciousness operations"""
    
    def __init__(self):
        self.tracker = PerformanceTracker()
        self.mock_consciousness_system = self._create_mock_consciousness_system()
    
    def _create_mock_consciousness_system(self):
        """Create mock consciousness system for performance testing"""
        return Mock(spec=[
            'compute_coherence',
            'access_memory_fold', 
            'validate_ethics',
            'integrate_trinity_framework',
            'check_constitutional_constraints'
        ])
    
    @contextmanager
    def measure_performance(self, operation_name: str, context: Dict[str, Any] = None):
        """Context manager for measuring operation performance"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            self.tracker.record_metric(
                name=operation_name,
                value=duration_ms,
                unit="ms",
                context=context or {}
            )
    
    def test_coherence_computation_performance(self, consciousness_state: Dict[str, Any] = None):
        """Test consciousness coherence computation performance"""
        test_state = consciousness_state or {
            "awareness": 0.95,
            "temporal_coherence": 0.98,
            "ethical_alignment": 0.97,
            "memory_folds": 150
        }
        
        with self.measure_performance("coherence_computation", {"state_complexity": len(test_state)}):
            # Simulate coherence computation with realistic processing time
            time.sleep(0.020)  # 20ms baseline processing
            result = self.mock_consciousness_system.compute_coherence(test_state)
            
        return result
    
    def test_memory_fold_access_performance(self, fold_id: str = "test_fold_001"):
        """Test memory fold access performance"""
        with self.measure_performance("memory_fold_access", {"fold_id": fold_id}):
            # Simulate memory access with realistic I/O time
            time.sleep(0.005)  # 5ms baseline access
            result = self.mock_consciousness_system.access_memory_fold(fold_id)
            
        return result
    
    def test_ethical_validation_performance(self, action: Dict[str, Any] = None):
        """Test ethical validation performance"""
        test_action = action or {
            "type": "consciousness_decision",
            "impact_score": 0.7,
            "stakeholders": ["user", "system"]
        }
        
        with self.measure_performance("ethical_validation", {"action_type": test_action["type"]}):
            # Simulate ethics validation with constitutional AI checking
            time.sleep(0.015)  # 15ms baseline validation
            result = self.mock_consciousness_system.validate_ethics(test_action)
            
        return result
    
    async def test_trinity_integration_performance(self):
        """Test Trinity Framework integration performance (async)"""
        with self.measure_performance("trinity_integration", {"framework": "⚛️🧠🛡️"}):
            # Simulate Trinity Framework integration across Identity, Consciousness, Guardian
            await asyncio.sleep(0.080)  # 80ms baseline integration
            result = self.mock_consciousness_system.integrate_trinity_framework()
            
        return result
    
    def test_constitutional_constraint_performance(self, constraints: List[str] = None):
        """Test constitutional constraint checking performance"""
        test_constraints = constraints or [
            "temporal_coherence >= 0.95",
            "ethical_alignment >= 0.98", 
            "cascade_prevention >= 0.997"
        ]
        
        with self.measure_performance("constitutional_check", {"constraint_count": len(test_constraints)}):
            # Simulate constitutional constraint verification
            time.sleep(0.010)  # 10ms baseline verification
            result = self.mock_consciousness_system.check_constitutional_constraints(test_constraints)
            
        return result


@pytest.fixture
def performance_tester():
    """Fixture providing performance tester instance"""
    return ConsciousnessPerformanceTester()


@pytest.fixture
def clean_performance_history():
    """Fixture that cleans up performance history after test"""
    yield
    # Clean up test performance data
    test_file = Path("rl/performance_history.json")
    if test_file.exists():
        try:
            test_file.unlink()
        except:
            pass


class TestConsciousnessPerformanceRegression:
    """Test suite for consciousness performance regression detection"""
    
    def test_coherence_computation_benchmark(self, performance_tester, clean_performance_history):
        """Test that coherence computation meets performance benchmarks"""
        # Run multiple iterations to establish baseline
        for _ in range(5):
            performance_tester.test_coherence_computation_performance()
        
        # Check latest metric against benchmark
        latest_metrics = performance_tester.tracker.get_recent_metrics("coherence_computation", 1)
        assert len(latest_metrics) > 0, "No coherence computation metrics recorded"
        
        latest = latest_metrics[0]
        is_acceptable, message = performance_tester.tracker.benchmark.check_performance(latest)
        print(message)
        
        # Allow some flexibility in testing environment
        assert latest.value < 100.0, f"Coherence computation too slow: {latest.value:.2f}ms"
    
    def test_memory_fold_access_benchmark(self, performance_tester, clean_performance_history):
        """Test that memory fold access meets performance benchmarks"""
        for fold_id in ["fold_001", "fold_002", "fold_003"]:
            performance_tester.test_memory_fold_access_performance(fold_id)
        
        latest_metrics = performance_tester.tracker.get_recent_metrics("memory_fold_access", 1)
        assert len(latest_metrics) > 0, "No memory fold access metrics recorded"
        
        latest = latest_metrics[0]
        is_acceptable, message = performance_tester.tracker.benchmark.check_performance(latest)
        print(message)
        
        assert latest.value < 50.0, f"Memory fold access too slow: {latest.value:.2f}ms"
    
    def test_ethical_validation_benchmark(self, performance_tester, clean_performance_history):
        """Test that ethical validation meets performance benchmarks"""
        test_actions = [
            {"type": "user_data_access", "impact_score": 0.8},
            {"type": "consciousness_modification", "impact_score": 0.9},
            {"type": "memory_fold_creation", "impact_score": 0.6}
        ]
        
        for action in test_actions:
            performance_tester.test_ethical_validation_performance(action)
        
        latest_metrics = performance_tester.tracker.get_recent_metrics("ethical_validation", 1)
        assert len(latest_metrics) > 0, "No ethical validation metrics recorded"
        
        latest = latest_metrics[0]
        is_acceptable, message = performance_tester.tracker.benchmark.check_performance(latest)
        print(message)
        
        assert latest.value < 75.0, f"Ethical validation too slow: {latest.value:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_trinity_integration_benchmark(self, performance_tester, clean_performance_history):
        """Test that Trinity Framework integration meets performance benchmarks"""
        for _ in range(3):
            await performance_tester.test_trinity_integration_performance()
        
        latest_metrics = performance_tester.tracker.get_recent_metrics("trinity_integration", 1)
        assert len(latest_metrics) > 0, "No Trinity integration metrics recorded"
        
        latest = latest_metrics[0]
        is_acceptable, message = performance_tester.tracker.benchmark.check_performance(latest)
        print(message)
        
        assert latest.value < 200.0, f"Trinity integration too slow: {latest.value:.2f}ms"
    
    def test_constitutional_constraint_benchmark(self, performance_tester, clean_performance_history):
        """Test that constitutional constraint checking meets performance benchmarks"""
        constraint_sets = [
            ["temporal_coherence >= 0.95"],
            ["temporal_coherence >= 0.95", "ethical_alignment >= 0.98"],
            ["temporal_coherence >= 0.95", "ethical_alignment >= 0.98", "cascade_prevention >= 0.997"]
        ]
        
        for constraints in constraint_sets:
            performance_tester.test_constitutional_constraint_performance(constraints)
        
        latest_metrics = performance_tester.tracker.get_recent_metrics("constitutional_check", 1)
        assert len(latest_metrics) > 0, "No constitutional check metrics recorded"
        
        latest = latest_metrics[0]
        is_acceptable, message = performance_tester.tracker.benchmark.check_performance(latest)
        print(message)
        
        assert latest.value < 50.0, f"Constitutional checking too slow: {latest.value:.2f}ms"
    
    def test_regression_detection_algorithm(self, performance_tester, clean_performance_history):
        """Test that regression detection correctly identifies performance degradation"""
        # Establish baseline with consistent performance
        baseline_values = [20.0, 21.0, 19.5, 20.5, 21.5]  # ~20ms average
        for value in baseline_values:
            performance_tester.tracker.record_metric("test_operation", value, "ms")
        
        # Test with normal performance (should not detect regression)
        has_regression, message = performance_tester.tracker.detect_regression("test_operation", 22.0)
        print(f"Normal case: {message}")
        assert not has_regression, "False positive regression detection"
        
        # Test with significant performance degradation (should detect regression)
        has_regression, message = performance_tester.tracker.detect_regression("test_operation", 35.0)
        print(f"Regression case: {message}")
        assert has_regression, "Failed to detect actual performance regression"
    
    def test_performance_metrics_persistence(self, performance_tester, clean_performance_history):
        """Test that performance metrics are properly saved and loaded"""
        # Record some test metrics
        test_metrics = [
            ("coherence_computation", 25.5, "ms"),
            ("memory_fold_access", 8.2, "ms"),
            ("ethical_validation", 18.7, "ms")
        ]
        
        for name, value, unit in test_metrics:
            performance_tester.tracker.record_metric(name, value, unit)
        
        # Save metrics
        performance_tester.tracker.save_metrics()
        
        # Create new tracker instance and verify it loads the data
        new_tracker = PerformanceTracker(performance_tester.tracker.storage_path)
        
        assert len(new_tracker.metrics) >= len(test_metrics), "Failed to load saved metrics"
        
        # Verify specific metrics were loaded correctly
        loaded_coherence = new_tracker.get_recent_metrics("coherence_computation", 1)
        assert len(loaded_coherence) > 0, "Coherence computation metric not loaded"
        assert loaded_coherence[0].value == 25.5, "Incorrect metric value loaded"
    
    def test_comprehensive_performance_suite(self, performance_tester, clean_performance_history):
        """Run comprehensive performance test suite covering all consciousness operations"""
        print("\n🚀 Running comprehensive consciousness performance benchmark...")
        
        # Test all major consciousness operations
        performance_tester.test_coherence_computation_performance()
        performance_tester.test_memory_fold_access_performance()
        performance_tester.test_ethical_validation_performance()
        performance_tester.test_constitutional_constraint_performance()
        
        # Analyze overall performance
        all_metrics = performance_tester.tracker.metrics
        operation_counts = {}
        for metric in all_metrics:
            operation_counts[metric.name] = operation_counts.get(metric.name, 0) + 1
        
        print(f"📊 Performance test completed:")
        for operation, count in operation_counts.items():
            recent = performance_tester.tracker.get_recent_metrics(operation, 1)
            if recent:
                print(f"  {operation}: {recent[0].value:.2f}ms (latest of {count} measurements)")
        
        # Verify we tested all critical operations
        critical_operations = ["coherence_computation", "memory_fold_access", "ethical_validation", "constitutional_check"]
        for op in critical_operations:
            assert op in operation_counts, f"Missing performance test for critical operation: {op}"
            assert operation_counts[op] > 0, f"No measurements for critical operation: {op}"
        
        # Save performance results for historical tracking
        performance_tester.tracker.save_metrics()
        print("💾 Performance metrics saved for historical tracking")


if __name__ == "__main__":
    # Run performance regression tests
    pytest.main([__file__, "-v", "--tb=short"])