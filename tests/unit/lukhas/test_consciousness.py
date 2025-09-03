#!/usr/bin/env python3
"""
T4-Grade Unit Tests for LUKHAS Consciousness Module
==================================================

Comprehensive test suite for consciousness module following T4 standards:
- 90% code coverage minimum
- Security vulnerability testing
- Performance benchmarks
- Trinity Framework compliance
"""

import asyncio
import time
from unittest.mock import patch

import pytest

from lukhas.consciousness import (
    AwarenessLevel,
    ConsciousnessConfig,
    ConsciousnessKernel,
    ConsciousnessState,
    ConsciousnessWrapper,
    SafetyMode,
)
from lukhas.governance.identity.connector import SecurityError  # ΛTAG: security_guard


class TestConsciousnessWrapper:
    """Test suite for ConsciousnessWrapper class."""

    @pytest.fixture
    def mock_config(self) -> ConsciousnessConfig:
        """Create a mock configuration for testing."""
        return ConsciousnessConfig(
            safety_mode=SafetyMode.STRICT,
            awareness_level=AwarenessLevel.BASIC,
            max_processing_time=1.0,
            enable_dreaming=False,
            drift_threshold=0.15,
        )

    @pytest.fixture
    def consciousness(self, mock_config: ConsciousnessConfig) -> ConsciousnessWrapper:
        """Create a consciousness instance for testing."""
        return ConsciousnessWrapper(config=mock_config)

    @pytest.mark.unit
    def test_initialization(self, consciousness: ConsciousnessWrapper):
        """Test proper initialization of consciousness wrapper."""
        assert consciousness is not None
        assert consciousness.config.safety_mode == SafetyMode.STRICT
        assert consciousness.state.awareness == AwarenessLevel.BASIC
        assert consciousness.is_active is False

    @pytest.mark.unit
    def test_alias_equivalence(self, mock_config: ConsciousnessConfig):
        """Test that ConsciousnessKernel is properly aliased."""
        wrapper = ConsciousnessWrapper(config=mock_config)
        ConsciousnessKernel(config=mock_config)

        assert isinstance(wrapper, ConsciousnessWrapper)
        assert ConsciousnessKernel is ConsciousnessWrapper

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_activation(self, consciousness: ConsciousnessWrapper):
        """Test consciousness activation and deactivation."""
        # Test activation
        await consciousness.activate()
        assert consciousness.is_active is True
        assert consciousness.state.last_activity is not None

        # Test deactivation
        await consciousness.deactivate()
        assert consciousness.is_active is False

    @pytest.mark.unit
    @pytest.mark.security
    def test_safety_mode_enforcement(self, consciousness: ConsciousnessWrapper):
        """Test that safety mode is properly enforced."""
        consciousness.config.safety_mode = SafetyMode.STRICT

        # Attempt potentially unsafe operation
        with pytest.raises(ValueError, match="Safety mode violation"):
            consciousness.process_input("UNSAFE_COMMAND_INJECT")

    @pytest.mark.unit
    @pytest.mark.performance
    def test_processing_time_limits(self, consciousness: ConsciousnessWrapper):
        """Test that processing time limits are enforced."""
        consciousness.config.max_processing_time = 0.1

        start_time = time.time()

        # Simulate slow processing
        with patch.object(consciousness, "_process_internal") as mock_process:
            mock_process.side_effect = lambda _: time.sleep(0.2)

            with pytest.raises(TimeoutError):
                consciousness.process_input("slow_operation")

        # Should timeout within reasonable bounds
        elapsed = time.time() - start_time
        assert elapsed < 0.3  # Allow some overhead

    @pytest.mark.unit
    @pytest.mark.trinity
    def test_trinity_framework_compliance(self, consciousness: ConsciousnessWrapper):
        """Test Trinity Framework (Identity-Consciousness-Guardian) compliance."""
        # Identity component
        assert hasattr(consciousness, "identity_context")

        # Consciousness component (self)
        assert consciousness.state is not None

        # Guardian component
        assert hasattr(consciousness, "guardian_check")
        assert consciousness.config.drift_threshold == 0.15

    @pytest.mark.unit
    def test_state_transitions(self, consciousness: ConsciousnessWrapper):
        """Test consciousness state transitions."""

        # Test state change
        consciousness.update_awareness(AwarenessLevel.ENHANCED)
        assert consciousness.state.awareness == AwarenessLevel.ENHANCED
        assert consciousness.state.last_state_change is not None

        # Test invalid state transition
        with pytest.raises(ValueError):
            consciousness.update_awareness("INVALID_LEVEL")

    @pytest.mark.unit
    @pytest.mark.critical
    def test_error_handling(self, consciousness: ConsciousnessWrapper):
        """Test comprehensive error handling."""
        # Test null input
        with pytest.raises(ValueError, match="Input cannot be None"):
            consciousness.process_input(None)

        # Test empty input
        result = consciousness.process_input("")
        assert result is not None

        # Test malformed input
        with pytest.raises(ValueError):
            consciousness.process_input({"malformed": "object"})

    @pytest.mark.unit
    @pytest.mark.regression
    def test_memory_leak_prevention(self, consciousness: ConsciousnessWrapper):
        """Regression test for memory leak issues."""
        import gc
        import sys

        # Get initial reference count
        initial_refs = sys.getrefcount(consciousness)

        # Simulate multiple operations
        for i in range(100):
            consciousness.process_input(f"test_input_{i}")
            if i % 10 == 0:
                gc.collect()

        # Check final reference count
        final_refs = sys.getrefcount(consciousness)

        # Should not have significant reference increase
        assert abs(final_refs - initial_refs) <= 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, consciousness: ConsciousnessWrapper):
        """Test handling of concurrent consciousness operations."""
        tasks = []

        # Create multiple concurrent tasks
        for i in range(10):
            task = asyncio.create_task(
                consciousness.process_input_async(f"concurrent_test_{i}")
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that all operations completed successfully
        for result in results:
            assert not isinstance(result, Exception)
            assert result is not None


class TestConsciousnessConfig:
    """Test suite for ConsciousnessConfig class."""

    @pytest.mark.unit
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = ConsciousnessConfig(
            safety_mode=SafetyMode.MODERATE,
            awareness_level=AwarenessLevel.ENHANCED,
            max_processing_time=2.0,
            drift_threshold=0.1,
        )
        assert config.is_valid()

        # Invalid drift threshold
        with pytest.raises(ValueError):
            ConsciousnessConfig(drift_threshold=1.5)  # > 1.0

        # Invalid processing time
        with pytest.raises(ValueError):
            ConsciousnessConfig(max_processing_time=-1.0)

    @pytest.mark.unit
    @pytest.mark.security
    def test_security_config_enforcement(self):
        """Test security configuration enforcement."""
        config = ConsciousnessConfig(safety_mode=SafetyMode.STRICT)

        # Strict mode should have additional validations
        assert config.requires_authentication is True
        assert config.enable_audit_logging is True
        assert config.max_processing_time <= 5.0


class TestConsciousnessState:
    """Test suite for ConsciousnessState class."""

    @pytest.mark.unit
    def test_state_serialization(self):
        """Test consciousness state serialization/deserialization."""
        state = ConsciousnessState(
            awareness=AwarenessLevel.ENHANCED, is_active=True, last_activity=time.time()
        )

        # Serialize to dict
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        assert "awareness" in state_dict
        assert "is_active" in state_dict

        # Deserialize from dict
        restored_state = ConsciousnessState.from_dict(state_dict)
        assert restored_state.awareness == state.awareness
        assert restored_state.is_active == state.is_active

    @pytest.mark.unit
    def test_state_immutability(self):
        """Test that critical state properties are immutable when needed."""
        state = ConsciousnessState(awareness=AwarenessLevel.BASIC)

        # Timestamp should be auto-generated and immutable
        with pytest.raises(AttributeError):
            state.creation_timestamp = time.time()


# Performance benchmarks
class TestConsciousnessPerformance:
    """Performance benchmark tests for consciousness module."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_processing_throughput(self, consciousness: ConsciousnessWrapper):
        """Benchmark processing throughput."""
        num_operations = 1000
        start_time = time.time()

        for i in range(num_operations):
            consciousness.process_input(f"benchmark_test_{i}")

        elapsed_time = time.time() - start_time
        throughput = num_operations / elapsed_time

        # T4 requirement: >100 operations/second
        assert throughput > 100, f"Throughput {throughput:.2f} ops/sec below minimum"

    @pytest.mark.performance
    def test_memory_usage(self, consciousness: ConsciousnessWrapper):
        """Test memory usage stays within bounds."""
        import tracemalloc

        tracemalloc.start()

        # Perform multiple operations
        for i in range(100):
            consciousness.process_input(f"memory_test_{i}")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # T4 requirement: <10MB peak memory usage
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 10, f"Peak memory usage {peak_mb:.2f}MB exceeds limit"


# Security tests
class TestConsciousnessSecurity:
    """Security-focused tests for consciousness module."""

    @pytest.mark.security
    @pytest.mark.critical
    def test_injection_attack_prevention(self, consciousness: ConsciousnessWrapper):
        """Test prevention of various injection attacks."""
        malicious_inputs = [
            "__import__('os').system('rm -rf /')",
            "exec('malicious_code()')",
            "eval('dangerous_expression')",
            "'; DROP TABLE consciousness; --",
            "<script>alert('xss')</script>",
        ]

        for malicious_input in malicious_inputs:
            with pytest.raises((ValueError, SecurityError, SyntaxError)):
                consciousness.process_input(malicious_input)

    @pytest.mark.security
    def test_sensitive_data_handling(self, consciousness: ConsciousnessWrapper):
        """Test proper handling of sensitive data."""
        sensitive_data = {
            "password": "secret123",
            "api_key": "sk-1234567890abcdef",
            "token": "bearer_token_here",
        }

        result = consciousness.process_input(sensitive_data)

        # Sensitive data should be sanitized in logs/output
        assert "secret123" not in str(result)
        assert "sk-1234567890abcdef" not in str(result)
        assert "bearer_token_here" not in str(result)


# Integration tests
@pytest.mark.integration
class TestConsciousnessIntegration:
    """Integration tests with other LUKHAS modules."""

    @pytest.mark.integration
    async def test_guardian_system_integration(self):
        """Test integration with Guardian System."""
        from lukhas.governance.guardian import GuardianSystem

        GuardianSystem()
        consciousness = ConsciousnessWrapper()

        # Test ethical decision making
        decision = await consciousness.make_ethical_decision(
            "Should I process this ambiguous request?",
            context={"user_trust_level": 0.8},
        )

        assert decision is not None
        assert hasattr(decision, "ethical_score")
        assert decision.ethical_score >= 0.0

    @pytest.mark.integration
    async def test_memory_system_integration(self):
        """Test integration with memory system."""
        from lukhas.memory import dump_state

        consciousness = ConsciousnessWrapper()
        await consciousness.activate()

        # Process some inputs to create memories
        for i in range(5):
            consciousness.process_input(f"memory_integration_test_{i}")

        # Dump memory state
        memory_state = dump_state("/tmp/consciousness_memory_test.json")
        assert memory_state is not None

        # Clean up
        import os

        if os.path.exists("/tmp/consciousness_memory_test.json"):
            os.remove("/tmp/consciousness_memory_test.json")


if __name__ == "__main__":
    pytest.main(
        [__file__, "-v", "--cov=lukhas.consciousness", "--cov-report=term-missing"]
    )
