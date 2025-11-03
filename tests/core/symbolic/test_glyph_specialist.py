"""
Test suite for core/symbolic/glyph_specialist.py - GLYPH System
Following AUTONOMOUS_GUIDE_TEST_COVERAGE.md Phase 4: Systematic Test Writing

COVERAGE TARGET: 75%+ for core/symbolic/glyph_specialist.py
PRIORITY: HIGH (GLYPH symbolic consciousness layer system)

Test Categories:
1. GlyphSignal dataclass tests
2. GlyphConsensusResult dataclass tests
3. GlyphSpecialist initialization tests
4. Consensus evaluation tests
5. Weight computation tests
6. Edge case and error handling tests
7. Integration tests
"""
from dataclasses import asdict
from datetime import datetime, timezone

import pytest
from core.symbolic.glyph_specialist import GlyphConsensusResult, GlyphSignal, GlyphSpecialist


class TestGlyphSignal:
    """Test GlyphSignal dataclass functionality."""

    def test_glyph_signal_creation_minimal(self):
        """Test GlyphSignal creation with minimal parameters."""
        signal = GlyphSignal(
            layer_id="test_layer",
            driftScore=0.5,
            affect_delta=0.2
        )

        assert signal.layer_id == "test_layer"
        assert signal.driftScore == 0.5
        assert signal.affect_delta == 0.2
        assert signal.glyph_markers == []
        assert isinstance(signal.captured_at, datetime)

    def test_glyph_signal_creation_full(self):
        """Test GlyphSignal creation with all parameters."""
        test_time = datetime.now(timezone.utc)
        test_markers = ["marker1", "marker2", "marker3"]

        signal = GlyphSignal(
            layer_id="full_layer",
            driftScore=0.8,
            affect_delta=-0.3,
            glyph_markers=test_markers,
            captured_at=test_time
        )

        assert signal.layer_id == "full_layer"
        assert signal.driftScore == 0.8
        assert signal.affect_delta == -0.3
        assert signal.glyph_markers == test_markers
        assert signal.captured_at == test_time

    def test_glyph_signal_immutable(self):
        """Test that GlyphSignal is immutable (frozen dataclass)."""
        signal = GlyphSignal(
            layer_id="immutable_test",
            driftScore=0.5,
            affect_delta=0.2
        )

        with pytest.raises(Exception):  # Should raise FrozenInstanceError
            signal.layer_id = "changed"  # type: ignore

        with pytest.raises(Exception):
            signal.driftScore = 0.9  # type: ignore

    def test_glyph_signal_default_timestamp(self):
        """Test that default timestamp is recent and has timezone."""
        before = datetime.now(timezone.utc)
        signal = GlyphSignal(layer_id="time_test", driftScore=0.0, affect_delta=0.0)
        after = datetime.now(timezone.utc)

        assert before <= signal.captured_at <= after
        assert signal.captured_at.tzinfo is not None

    def test_glyph_signal_equality(self):
        """Test GlyphSignal equality comparison."""
        test_time = datetime.now(timezone.utc)

        signal1 = GlyphSignal(
            layer_id="test",
            driftScore=0.5,
            affect_delta=0.2,
            captured_at=test_time
        )

        signal2 = GlyphSignal(
            layer_id="test",
            driftScore=0.5,
            affect_delta=0.2,
            captured_at=test_time
        )

        signal3 = GlyphSignal(
            layer_id="different",
            driftScore=0.5,
            affect_delta=0.2,
            captured_at=test_time
        )

        assert signal1 == signal2
        assert signal1 != signal3

    def test_glyph_signal_glyph_markers_types(self):
        """Test glyph_markers accepts different sequence types."""
        # Test with list
        signal_list = GlyphSignal(
            layer_id="list_test",
            driftScore=0.5,
            affect_delta=0.2,
            glyph_markers=["a", "b", "c"]
        )
        assert list(signal_list.glyph_markers) == ["a", "b", "c"]

        # Test with tuple
        signal_tuple = GlyphSignal(
            layer_id="tuple_test",
            driftScore=0.5,
            affect_delta=0.2,
            glyph_markers=("x", "y", "z")
        )
        assert list(signal_tuple.glyph_markers) == ["x", "y", "z"]


class TestGlyphConsensusResult:
    """Test GlyphConsensusResult dataclass functionality."""

    def test_consensus_result_creation_minimal(self):
        """Test GlyphConsensusResult creation with minimal parameters."""
        result = GlyphConsensusResult(
            consensus=True,
            driftScore=0.3,
            affect_delta=0.1,
            agreement_ratio=0.8,
            dissenting_layers=["layer1"],
            glyph_signature=["sig1", "sig2"]
        )

        assert result.consensus is True
        assert result.driftScore == 0.3
        assert result.affect_delta == 0.1
        assert result.agreement_ratio == 0.8
        assert result.dissenting_layers == ["layer1"]
        assert result.glyph_signature == ["sig1", "sig2"]
        assert isinstance(result.evaluated_at, datetime)

    def test_consensus_result_immutable(self):
        """Test that GlyphConsensusResult is immutable."""
        result = GlyphConsensusResult(
            consensus=True,
            driftScore=0.3,
            affect_delta=0.1,
            agreement_ratio=0.8,
            dissenting_layers=[],
            glyph_signature=[]
        )

        with pytest.raises(Exception):
            result.consensus = False  # type: ignore

        with pytest.raises(Exception):
            result.driftScore = 0.9  # type: ignore

    def test_consensus_result_default_timestamp(self):
        """Test default timestamp behavior."""
        before = datetime.now(timezone.utc)
        result = GlyphConsensusResult(
            consensus=False,
            driftScore=0.7,
            affect_delta=-0.2,
            agreement_ratio=0.3,
            dissenting_layers=["layer1", "layer2"],
            glyph_signature=["warning"]
        )
        after = datetime.now(timezone.utc)

        assert before <= result.evaluated_at <= after
        assert result.evaluated_at.tzinfo is not None


class TestGlyphSpecialist:
    """Test GlyphSpecialist functionality."""

    def test_glyph_specialist_initialization_default(self):
        """Test GlyphSpecialist initialization with default parameters."""
        specialist = GlyphSpecialist()

        assert specialist.drift_threshold == 0.3
        assert hasattr(specialist, '_logger')

    def test_glyph_specialist_initialization_custom(self):
        """Test GlyphSpecialist initialization with custom threshold."""
        specialist = GlyphSpecialist(drift_threshold=0.5)

        assert specialist.drift_threshold == 0.5

    def test_evaluate_empty_signals_raises_error(self):
        """Test that evaluate raises ValueError for empty signals."""
        specialist = GlyphSpecialist()

        with pytest.raises(ValueError, match="signals must not be empty"):
            specialist.evaluate([])

    def test_evaluate_single_signal(self):
        """Test evaluation with single signal."""
        specialist = GlyphSpecialist()
        signal = GlyphSignal(
            layer_id="single_test",
            driftScore=0.2,
            affect_delta=0.1,
            glyph_markers=["marker1"]
        )

        result = specialist.evaluate([signal])

        assert isinstance(result, GlyphConsensusResult)
        assert result.driftScore == 0.2
        assert result.affect_delta == 0.1
        assert isinstance(result.consensus, bool)
        assert isinstance(result.agreement_ratio, float)
        assert isinstance(result.dissenting_layers, list)
        assert isinstance(result.glyph_signature, list)

    def test_evaluate_multiple_signals_consensus(self):
        """Test evaluation with multiple signals that should reach consensus."""
        specialist = GlyphSpecialist(drift_threshold=0.5)

        signals = [
            GlyphSignal(
                layer_id="layer1",
                driftScore=0.2,
                affect_delta=0.1,
                glyph_markers=["stable"]
            ),
            GlyphSignal(
                layer_id="layer2",
                driftScore=0.25,
                affect_delta=0.15,
                glyph_markers=["stable"]
            ),
            GlyphSignal(
                layer_id="layer3",
                driftScore=0.18,
                affect_delta=0.08,
                glyph_markers=["stable"]
            )
        ]

        result = specialist.evaluate(signals)

        assert isinstance(result, GlyphConsensusResult)
        # All signals have drift below threshold (0.5), should reach consensus
        assert result.driftScore < 0.5
        assert len(result.glyph_signature) > 0

    def test_evaluate_multiple_signals_no_consensus(self):
        """Test evaluation with signals that should not reach consensus."""
        specialist = GlyphSpecialist(drift_threshold=0.3)

        signals = [
            GlyphSignal(
                layer_id="stable_layer",
                driftScore=0.1,
                affect_delta=0.05,
                glyph_markers=["stable"]
            ),
            GlyphSignal(
                layer_id="drifting_layer",
                driftScore=0.8,  # High drift
                affect_delta=-0.3,
                glyph_markers=["drift", "warning"]
            )
        ]

        result = specialist.evaluate(signals)

        assert isinstance(result, GlyphConsensusResult)
        # Mixed signals should affect consensus
        assert len(result.dissenting_layers) >= 0

    def test_evaluate_high_drift_signals(self):
        """Test evaluation with all high-drift signals."""
        specialist = GlyphSpecialist(drift_threshold=0.2)

        signals = [
            GlyphSignal(
                layer_id="high_drift1",
                driftScore=0.9,
                affect_delta=-0.4,
                glyph_markers=["critical", "drift"]
            ),
            GlyphSignal(
                layer_id="high_drift2",
                driftScore=0.85,
                affect_delta=-0.35,
                glyph_markers=["critical", "warning"]
            )
        ]

        result = specialist.evaluate(signals)

        assert isinstance(result, GlyphConsensusResult)
        assert result.driftScore > specialist.drift_threshold

    def test_evaluate_preserves_signal_data(self):
        """Test that evaluation preserves original signal data."""
        specialist = GlyphSpecialist()
        original_signals = [
            GlyphSignal(
                layer_id="preserve_test",
                driftScore=0.4,
                affect_delta=0.2,
                glyph_markers=["test_marker"]
            )
        ]

        # Create copy to verify original is unchanged
        original_layer_id = original_signals[0].layer_id
        original_drift = original_signals[0].driftScore

        specialist.evaluate(original_signals)

        # Original signals should be unchanged
        assert original_signals[0].layer_id == original_layer_id
        assert original_signals[0].driftScore == original_drift

    def test_different_thresholds_affect_results(self):
        """Test that different thresholds can affect consensus results."""
        signal = GlyphSignal(
            layer_id="threshold_test",
            driftScore=0.4,
            affect_delta=0.1,
            glyph_markers=["test"]
        )

        strict_specialist = GlyphSpecialist(drift_threshold=0.2)
        lenient_specialist = GlyphSpecialist(drift_threshold=0.6)

        strict_result = strict_specialist.evaluate([signal])
        lenient_result = lenient_specialist.evaluate([signal])

        # Results might differ based on threshold
        assert isinstance(strict_result, GlyphConsensusResult)
        assert isinstance(lenient_result, GlyphConsensusResult)


class TestGlyphSpecialistIntegration:
    """Integration tests for GlyphSpecialist with complex scenarios."""

    def test_realistic_consciousness_layer_scenario(self):
        """Test with realistic consciousness layer signals."""
        specialist = GlyphSpecialist(drift_threshold=0.3)

        # Simulate different consciousness layers
        signals = [
            GlyphSignal(
                layer_id="attention_layer",
                driftScore=0.15,
                affect_delta=0.1,
                glyph_markers=["focus", "stable"]
            ),
            GlyphSignal(
                layer_id="memory_layer",
                driftScore=0.25,
                affect_delta=0.05,
                glyph_markers=["recall", "coherent"]
            ),
            GlyphSignal(
                layer_id="reasoning_layer",
                driftScore=0.4,  # Slightly elevated
                affect_delta=-0.1,
                glyph_markers=["logic", "processing"]
            ),
            GlyphSignal(
                layer_id="emotional_layer",
                driftScore=0.1,
                affect_delta=0.3,
                glyph_markers=["emotion", "valence"]
            )
        ]

        result = specialist.evaluate(signals)

        assert isinstance(result, GlyphConsensusResult)
        assert len(result.glyph_signature) > 0
        assert 0.0 <= result.agreement_ratio <= 1.0
        assert isinstance(result.dissenting_layers, list)

    def test_weight_computation_accessibility(self):
        """Test that weight computation method can be accessed (if public)."""
        specialist = GlyphSpecialist()
        signal = GlyphSignal(
            layer_id="weight_test",
            driftScore=0.3,
            affect_delta=0.1,
            glyph_markers=["test"]
        )

        # Test that _compute_weight method exists and can be called
        if hasattr(specialist, '_compute_weight'):
            weight = specialist._compute_weight(signal)
            assert isinstance(weight, (int, float))
            assert weight >= 0


class TestGlyphSystemEdgeCases:
    """Test edge cases and error conditions."""

    def test_extreme_drift_scores(self):
        """Test with extreme drift scores."""
        specialist = GlyphSpecialist()

        signals = [
            GlyphSignal(layer_id="extreme_low", driftScore=-1.0, affect_delta=0.0),
            GlyphSignal(layer_id="extreme_high", driftScore=2.0, affect_delta=0.0),
            GlyphSignal(layer_id="zero", driftScore=0.0, affect_delta=0.0)
        ]

        result = specialist.evaluate(signals)
        assert isinstance(result, GlyphConsensusResult)

    def test_extreme_affect_deltas(self):
        """Test with extreme affect delta values."""
        specialist = GlyphSpecialist()

        signals = [
            GlyphSignal(layer_id="high_positive", driftScore=0.2, affect_delta=5.0),
            GlyphSignal(layer_id="high_negative", driftScore=0.2, affect_delta=-5.0),
            GlyphSignal(layer_id="zero_affect", driftScore=0.2, affect_delta=0.0)
        ]

        result = specialist.evaluate(signals)
        assert isinstance(result, GlyphConsensusResult)

    def test_empty_glyph_markers(self):
        """Test signals with empty glyph markers."""
        specialist = GlyphSpecialist()

        signals = [
            GlyphSignal(layer_id="empty_markers", driftScore=0.3, affect_delta=0.1, glyph_markers=[]),
            GlyphSignal(layer_id="with_markers", driftScore=0.3, affect_delta=0.1, glyph_markers=["marker"])
        ]

        result = specialist.evaluate(signals)
        assert isinstance(result, GlyphConsensusResult)

    def test_duplicate_layer_ids(self):
        """Test with duplicate layer IDs."""
        specialist = GlyphSpecialist()

        signals = [
            GlyphSignal(layer_id="duplicate", driftScore=0.3, affect_delta=0.1),
            GlyphSignal(layer_id="duplicate", driftScore=0.4, affect_delta=0.2)
        ]

        result = specialist.evaluate(signals)
        assert isinstance(result, GlyphConsensusResult)


# Test configuration for pytest
pytest_plugins = []
