"""
Test suite for LUKHAS drift recovery simulation tools.

This test module validates the drift injection, recovery measurement,
and resilience scoring capabilities of the DriftRecoverySimulator.
"""

import json
import tempfile
from pathlib import Path
from trace.drift_tools import (
    DriftRecoverySimulator,
    EntropyProfile,
    RecoveryMetrics,
    SymbolicHealth,
    quick_drift_test,
)

import pytest


class TestEntropyProfile:
    """Test entropy profile generation."""

    def test_sine_wave_entropy(self):
        """Test sine wave entropy calculation."""
        profile = EntropyProfile("test_sine", 0.5, 0.2, 1.0, "sine")

        # Test at different time points
        t0 = profile.compute_entropy(0.0)
        t_quarter = profile.compute_entropy(0.25)
        t_half = profile.compute_entropy(0.5)

        assert 0.3 <= t0 <= 0.7  # Base magnitude +/- variance
        assert t0 != t_quarter != t_half  # Values should vary

    def test_random_entropy(self):
        """Test random entropy generation."""
        profile = EntropyProfile("test_random", 0.5, 0.2, 1.0, "random")

        # Generate multiple values
        values = [profile.compute_entropy(i * 0.1) for i in range(10)]

        # All values should be within expected range
        for v in values:
            assert 0.3 <= v <= 0.7

        # Values should not all be identical (very unlikely for random)
        assert len(set(values)) > 1


class TestSymbolicHealth:
    """Test symbolic health metrics."""

    def test_default_health(self):
        """Test default health initialization."""
        health = SymbolicHealth()

        assert health.coherence == 1.0
        assert health.stability == 1.0
        assert health.overall_health() == 1.0

    def test_degraded_health(self):
        """Test health calculation with degraded metrics."""
        health = SymbolicHealth(
            coherence=0.5,
            stability=0.6,
            ethical_alignment=0.7,
            emotional_balance=0.4,
            memory_integrity=0.8,
            glyph_resonance=0.9,
        )

        overall = health.overall_health()
        assert 0 < overall < 1
        assert overall == pytest.approx(0.635, rel=0.01)

    def test_health_to_dict(self):
        """Test health metric serialization."""
        health = SymbolicHealth(coherence=0.8)
        health_dict = health.to_dict()

        assert "coherence" in health_dict
        assert health_dict["coherence"] == 0.8
        assert "overall" in health_dict


@pytest.mark.asyncio
class TestDriftRecoverySimulator:
    """Test drift recovery simulator functionality."""

    async def test_drift_injection(self):
        """Test basic drift injection."""
        simulator = DriftRecoverySimulator()
        profile = EntropyProfile("test", 0.3, 0.1, 1.0)

        result = await simulator.inject_drift(
            "test_symbol", magnitude=0.5, entropy_profile=profile, duration=1.0
        )

        assert result["symbol_id"] == "test_symbol"
        assert result["initial_health"] == 1.0
        assert result["final_health"] < 1.0
        assert len(result["injection_log"]) > 0

    async def test_recovery_measurement(self):
        """Test recovery after drift injection."""
        simulator = DriftRecoverySimulator()

        # First inject drift
        profile = EntropyProfile("test", 0.5, 0.1, 1.0)
        await simulator.inject_drift(
            "test_symbol", magnitude=0.5, entropy_profile=profile, duration=1.0
        )

        # Then measure recovery
        recovery = await simulator.measure_recovery(
            "test_symbol", timeout=5.0, intervention_strategy="aggressive"
        )

        assert isinstance(recovery, RecoveryMetrics)
        assert recovery.converged is True
        assert recovery.time_to_recovery() < 5.0
        assert recovery.recovery_efficiency() > 0

    async def test_resilience_scoring(self):
        """Test resilience score calculation."""
        simulator = DriftRecoverySimulator()

        # Inject and recover
        profile = EntropyProfile("test", 0.3, 0.1, 1.0)
        await simulator.inject_drift("test_symbol", 0.3, profile, 1.0)
        await simulator.measure_recovery("test_symbol", 5.0, "moderate")

        score = simulator.score_resilience("test_symbol")
        assert 0 <= score <= 1
        assert score > 0.5  # Should have decent resilience with moderate drift

    async def test_emotional_cascade(self):
        """Test emotional cascade simulation."""
        simulator = DriftRecoverySimulator()

        result = await simulator.simulate_emotional_cascade(
            "cascade_trigger",
            cascade_depth=2,
            propagation_factor=0.7,
            dream_integration=False,
        )

        assert result["trigger_symbol"] == "cascade_trigger"
        assert len(result["affected_symbols"]) > 1
        assert result["total_health_loss"] > 0
        assert result["cascade_depth"] == 2

    async def test_benchmark_suite(self):
        """Test benchmark suite execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            simulator = DriftRecoverySimulator(checkpoint_dir=tmpdir)

            results = await simulator.run_benchmark_suite()

            assert results["total_tests"] >= 5
            assert "overall_resilience" in results
            assert 0 <= results["overall_resilience"] <= 1

            # Check that results were saved
            checkpoint_files = list(Path(tmpdir).glob("benchmark_*.json"))
            assert len(checkpoint_files) == 1

            # Verify saved data
            with open(checkpoint_files[0]) as f:
                saved_data = json.load(f)
                assert saved_data["total_tests"] == results["total_tests"]


@pytest.mark.asyncio
class TestIntegration:
    """Test integration scenarios."""

    async def test_quick_drift_test(self):
        """Test the quick drift test utility."""
        result = await quick_drift_test("integration_test")

        assert "injection" in result
        assert "recovery" in result
        assert "resilience_score" in result

        assert result["recovery"]["converged"] is True
        assert result["resilience_score"] > 0

    async def test_multiple_symbols(self):
        """Test handling multiple symbols simultaneously."""
        simulator = DriftRecoverySimulator()
        profile = EntropyProfile("test", 0.4, 0.1, 1.0)

        # Inject drift into multiple symbols
        symbols = ["symbol_1", "symbol_2", "symbol_3"]
        for symbol in symbols:
            await simulator.inject_drift(symbol, 0.3, profile, 0.5)

        # Verify all symbols are tracked
        assert len(simulator.symbols) == 3

        # Recover all symbols
        for symbol in symbols:
            recovery = await simulator.measure_recovery(symbol, 5.0, "moderate")
            assert recovery.converged

    async def test_cascade_with_dream_integration(self):
        """Test cascade with dream integration enabled."""
        simulator = DriftRecoverySimulator()

        # Compare cascades with and without dream integration
        cascade_dream = await simulator.simulate_emotional_cascade(
            "trigger_dream",
            cascade_depth=2,
            propagation_factor=0.7,
            dream_integration=True,
        )

        cascade_nodream = await simulator.simulate_emotional_cascade(
            "trigger_nodream",
            cascade_depth=2,
            propagation_factor=0.7,
            dream_integration=False,
        )

        # Dream integration should reduce cascade impact
        assert cascade_dream["total_health_loss"] < cascade_nodream["total_health_loss"]


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_recovery_without_drift(self):
        """Test recovery measurement without prior drift injection."""
        simulator = DriftRecoverySimulator()

        with pytest.raises(ValueError, match="Symbol .* not found"):
            await simulator.measure_recovery("nonexistent_symbol")

    def test_zero_resilience(self):
        """Test resilience score for non-recovered symbol."""
        simulator = DriftRecoverySimulator()
        score = simulator.score_resilience("nonexistent_symbol")
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_extreme_entropy(self):
        """Test system behavior with extreme entropy values."""
        simulator = DriftRecoverySimulator()

        # Very high entropy
        high_profile = EntropyProfile("extreme_high", 0.95, 0.05, 1.0)
        result = await simulator.inject_drift(
            "extreme_symbol", magnitude=0.9, entropy_profile=high_profile, duration=2.0
        )

        # Symbol should be severely degraded
        assert result["final_health"] < 0.3

        # Recovery should be difficult
        recovery = await simulator.measure_recovery(
            "extreme_symbol", timeout=10.0, intervention_strategy="aggressive"
        )

        # May not converge even with aggressive intervention
        if recovery.converged:
            assert recovery.time_to_recovery() > 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
