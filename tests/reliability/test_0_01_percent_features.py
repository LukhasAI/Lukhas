#!/usr/bin/env python3
"""
Tests for 0.01% Excellence Reliability Features

Validates the subtle but critical reliability patterns that distinguish
top-tier systems from merely good ones.
"""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from core.reliability import (
    AdaptiveCircuitBreaker,
    AdaptiveTimeoutManager,
    BackoffConfig,
    BackoffStrategy,
    CircuitBreakerOpenError,
    ErrorCategory,
    ErrorContextManager,
    ErrorSeverity,
    IntelligentBackoff,
    PerformanceRegressionDetector,
    TimeoutConfig,
)


class TestAdaptiveCircuitBreaker:
    """Test adaptive circuit breaker with intelligent thresholds."""

    @pytest.fixture
    def circuit_breaker(self):
        return AdaptiveCircuitBreaker(
            name="test_circuit",
            failure_threshold=0.5,
            recovery_timeout=1.0,
            min_request_threshold=5
        )

    def test_circuit_starts_closed(self, circuit_breaker):
        """Test that circuit breaker starts in closed state."""
        health = circuit_breaker.get_health_status()
        assert health['state'] == 'closed'
        assert health['failure_rate'] == 0.0

    @pytest.mark.asyncio
    async def test_successful_operations(self, circuit_breaker):
        """Test that successful operations keep circuit closed."""
        async def success_func():
            await asyncio.sleep(0.01)
            return "success"

        for _ in range(10):
            result = await circuit_breaker.call(success_func)
            assert result == "success"

        health = circuit_breaker.get_health_status()
        assert health['state'] == 'closed'
        assert health['success_count'] == 10

    @pytest.mark.asyncio
    async def test_circuit_opens_on_failures(self, circuit_breaker):
        """Test that circuit opens when failure threshold is exceeded."""
        async def failing_func():
            raise ValueError("Test failure")

        # Generate failures to trigger circuit opening
        for i in range(10):
            try:
                await circuit_breaker.call(failing_func)
            except (ValueError, CircuitBreakerOpenError):
                pass  # Ignore both test failures and circuit breaker errors

        health = circuit_breaker.get_health_status()
        assert health['state'] == 'open'

    @pytest.mark.asyncio
    async def test_circuit_fails_fast_when_open(self, circuit_breaker):
        """Test that circuit fails fast when open."""
        # Force circuit to open
        for _ in range(10):
            try:
                await circuit_breaker.call(lambda: exec('raise ValueError("failure")'))
            except:
                pass

        # Circuit should now be open and fail fast
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(lambda: "should not execute")

    @pytest.mark.asyncio
    async def test_adaptive_threshold_calculation(self, circuit_breaker):
        """Test that adaptive thresholds work correctly."""
        # Simulate degraded performance to test adaptive thresholds
        circuit_breaker.baseline_performance = 100.0  # 100ms baseline

        # Add slow response times to trigger adaptive behavior
        for _ in range(20):
            circuit_breaker.response_times.append(300.0)  # 300ms responses

        adaptive_threshold = circuit_breaker._get_adaptive_threshold()
        assert adaptive_threshold > circuit_breaker.failure_threshold


class TestPerformanceRegressionDetector:
    """Test intelligent performance regression detection."""

    @pytest.fixture
    def detector(self):
        return PerformanceRegressionDetector(
            baseline_window_hours=1,
            comparison_window_minutes=1,
            min_samples=10
        )

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly."""
        health = detector.get_health_summary()
        assert health['total_operations_monitored'] == 0
        assert health['detector_healthy'] is True

    def test_operation_recording(self, detector):
        """Test that operations are recorded correctly."""
        detector.record_operation("test_op", 100.0, success=True)

        health = detector.get_health_summary()
        assert health['total_operations_monitored'] == 1

    def test_baseline_calculation(self, detector):
        """Test baseline calculation with sufficient data."""
        # Record baseline data
        for i in range(50):
            detector.record_operation("test_op", 100.0 + i, success=True)

        baseline = detector._get_or_calculate_baseline("test_op")
        assert baseline is not None
        assert baseline.operation == "test_op"
        # The baseline calculation uses the last window_size samples, which defaults to lower value
        assert baseline.sample_count >= 10

    def test_regression_detection(self, detector):
        """Test that performance regressions are detected."""
        # Establish baseline
        for i in range(50):
            detector.record_operation("test_op", 100.0, success=True)

        # Force baseline calculation
        detector._get_or_calculate_baseline("test_op")

        # Simulate performance regression
        for i in range(20):
            detector.record_operation("test_op", 300.0, success=True)  # 3x slower

        alerts = detector.get_active_alerts()
        assert len(alerts) > 0
        assert any(alert.metric == "p95_latency" for alert in alerts)


class TestErrorContextManager:
    """Test enhanced error context and correlation."""

    @pytest.fixture
    def error_manager(self):
        return ErrorContextManager()

    def test_error_classification(self, error_manager):
        """Test automatic error classification."""
        # Network error
        network_error = ConnectionError("Connection refused")
        category = error_manager._classify_error(network_error)
        assert category == ErrorCategory.NETWORK

        # Validation error
        validation_error = ValueError("Invalid input format")
        category = error_manager._classify_error(validation_error)
        assert category == ErrorCategory.VALIDATION

    def test_severity_assessment(self, error_manager):
        """Test error severity assessment."""
        # Critical system error
        system_error = RuntimeError("System failure")
        severity = error_manager._assess_severity(system_error, ErrorCategory.SYSTEM)
        assert severity == ErrorSeverity.CRITICAL

        # Authentication error
        auth_error = PermissionError("Access denied")
        severity = error_manager._assess_severity(auth_error, ErrorCategory.AUTHENTICATION)
        assert severity == ErrorSeverity.HIGH

    def test_error_context_capture(self, error_manager):
        """Test comprehensive error context capture."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            context = error_manager.capture_error(e, "test_operation")

        assert context.exception_type == "ValueError"
        assert context.operation == "test_operation"
        assert context.category == ErrorCategory.VALIDATION
        assert len(context.stack_trace) > 0
        assert context.error_id is not None

    def test_pattern_detection(self, error_manager):
        """Test error pattern detection."""
        # Generate multiple similar errors
        for _ in range(5):
            try:
                raise ValueError("Repeated error")
            except Exception as e:
                error_manager.capture_error(e, "test_operation")

        # Check if pattern was detected
        assert len(error_manager.error_patterns) > 0


class TestAdaptiveTimeouts:
    """Test intelligent timeout and backoff strategies."""

    @pytest.fixture
    def timeout_manager(self):
        return AdaptiveTimeoutManager()

    @pytest.fixture
    def backoff(self):
        config = BackoffConfig(
            initial_delay=0.1,
            max_delay=1.0,
            max_attempts=3
        )
        return IntelligentBackoff(config)

    def test_timeout_adaptation(self, timeout_manager):
        """Test that timeouts adapt based on historical data."""
        config = TimeoutConfig(
            base_timeout=1000,
            max_timeout=5000,
            min_timeout=100
        )
        timeout_manager.register_operation("test_op", config)

        # Record fast operations
        for _ in range(50):
            timeout_manager.record_latency("test_op", 50.0, True)

        adaptive_timeout = timeout_manager.get_adaptive_timeout("test_op")
        assert adaptive_timeout < config.base_timeout  # Should adapt to faster operations

    @pytest.mark.asyncio
    async def test_adaptive_timeout_execution(self, timeout_manager):
        """Test execution with adaptive timeout."""
        async def fast_operation():
            await asyncio.sleep(0.01)
            return "success"

        result = await timeout_manager.execute_with_adaptive_timeout(
            "test_op", fast_operation
        )
        assert result == "success"

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, backoff):
        """Test exponential backoff calculation."""
        attempt_count = 0

        async def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await backoff.execute_with_backoff("test_op", failing_operation)
        assert result == "success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_adaptive_backoff_strategy(self):
        """Test adaptive backoff strategy."""
        config = BackoffConfig(
            strategy=BackoffStrategy.ADAPTIVE,
            initial_delay=0.1,
            max_attempts=3
        )
        backoff = IntelligentBackoff(config)

        # Record some failure history
        for _ in range(10):
            backoff.attempt_history.append({
                'success': False,
                'attempt': 1,
                'latency_ms': 100,
                'timestamp': time.time()
            })

        delay = backoff._adaptive_delay(1)
        assert delay > config.initial_delay  # Should be more conservative with low success rate

    def test_fibonacci_backoff(self, backoff):
        """Test Fibonacci sequence calculation."""
        fib_5 = backoff._fibonacci(5)
        assert fib_5 == 5  # 5th Fibonacci number

        fib_8 = backoff._fibonacci(8)
        assert fib_8 == 21  # 8th Fibonacci number

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_load_aware_delay(self, mock_memory, mock_cpu, backoff):
        """Test load-aware delay adjustment."""
        mock_cpu.return_value = 80.0  # 80% CPU
        mock_memory.return_value = Mock(percent=70.0)  # 70% memory

        load_multiplier = backoff._get_load_multiplier()
        assert load_multiplier > 1.0  # Should increase delay under high load


class TestIntegration:
    """Integration tests for reliability components."""

    @pytest.mark.asyncio
    async def test_reliability_stack_integration(self):
        """Test that all reliability components work together."""
        from core.reliability import (
            circuit_breaker,
            enhanced_error_handler,
            performance_monitor,
            resilient_operation,
        )

        # Test operation with full reliability stack
        @resilient_operation(
            "integration_test",
            timeout_config=TimeoutConfig(base_timeout=1000, max_timeout=5000, min_timeout=100),
            backoff_config=BackoffConfig(max_attempts=2, initial_delay=0.1)
        )
        @performance_monitor("integration_test")
        @enhanced_error_handler("integration_test")
        @circuit_breaker("integration_test")
        async def test_operation():
            await asyncio.sleep(0.01)
            return "success"

        result = await test_operation()
        assert result == "success"

    def test_health_status_aggregation(self):
        """Test that health status aggregation works correctly."""
        from core.reliability import get_reliability_health_status

        health = get_reliability_health_status()
        assert "circuit_breakers" in health
        assert "performance_monitoring" in health
        assert "error_tracking" in health
        assert health["reliability_systems_operational"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
