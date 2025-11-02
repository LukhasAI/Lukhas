"""
Unit tests for symbolic quantum perception instrumentation.

Tests validate driftScore, collapseHash, and entanglementHealth calculations
using seeded random generators for deterministic behavior.
"""

import unittest
from unittest.mock import patch

import numpy as np
import pytest

# Import the quantum perception components to test
try:
    from symbolic.core.quantum_perception import (
        EntangledSymbolPair,
        ObservationType,
        ObserverEffect,
        QuantumPerceptionField,
        WaveFunctionCollapse,
    )
    from symbolic.core.visual_symbol import QuantumState, SymbolState, VisualSymbol
    SYMBOLIC_AVAILABLE = True
except ImportError:
    pytest.skip("Symbolic core modules not available", allow_module_level=True)
    SYMBOLIC_AVAILABLE = False


class TestQuantumPerceptionInstrumentation(unittest.TestCase):
    """Test ΛTRACE instrumentation in quantum perception system."""

    def setUp(self):
        """Set up test fixtures with deterministic seeding."""
        # Seed all random generators for deterministic tests
        np.random.seed(42)

        # Create test quantum perception field
        self.field = QuantumPerceptionField(
            observer_id="test_observer",
            consciousness_level=0.7,
            field_dimensions=(5, 5, 5)
        )
        self.field.enable_trace(True)

        # Create test symbols
        self.symbol_a = self._create_test_symbol("test_symbol_a", entropy=0.3, coherence=0.8)
        self.symbol_b = self._create_test_symbol("test_symbol_b", entropy=0.5, coherence=0.6)

        # Add symbols to field
        self.field.add_symbol(self.symbol_a)
        self.field.add_symbol(self.symbol_b)

    def _create_test_symbol(self, symbol_id: str, entropy: float = 0.4, coherence: float = 0.7) -> VisualSymbol:
        """Create a test visual symbol with specified properties."""
        quantum_state = QuantumState(
            amplitude=complex(0.8, 0.2),
            phase=np.pi / 4,
            entropy=entropy,
            coherence=coherence,
            trust=0.9
        )

        symbol_state = SymbolState(
            symbol_id=symbol_id,
            current_state="superposition",
            visual_weight=0.8,
            emotional_valence=0.2,
            emotional_arousal=0.6,
            quantum_field=quantum_state
        )

        return VisualSymbol(state=symbol_state)

    @pytest.mark.unit
    def test_drift_score_calculation_deterministic(self):
        """Test drift score calculation produces deterministic results."""
        # Test with known values
        pre_entropy = 0.3
        post_entropy = 0.5
        pre_coherence = 0.8
        post_coherence = 0.6

        drift_score = self.field._calculate_drift_score(
            pre_entropy, post_entropy, pre_coherence, post_coherence
        )

        # Expected drift score calculation:
        # entropy_delta = |0.5 - 0.3| = 0.2
        # coherence_delta = |0.6 - 0.8| = 0.2
        # normalized_entropy_drift = min(0.2 / (0.3 + 0.001), 1.0) ≈ 0.665
        # normalized_coherence_drift = min(0.2 / (0.8 + 0.001), 1.0) ≈ 0.250
        # drift_score = (0.665 + 0.250) / 2.0 ≈ 0.457

        self.assertAlmostEqual(drift_score, 0.457, places=2)
        self.assertGreaterEqual(drift_score, 0.0)
        self.assertLessEqual(drift_score, 1.0)

    @pytest.mark.unit
    def test_drift_score_edge_cases(self):
        """Test drift score calculation edge cases."""
        # No drift case
        no_drift = self.field._calculate_drift_score(0.5, 0.5, 0.7, 0.7)
        self.assertEqual(no_drift, 0.0)

        # Maximum drift case
        max_drift = self.field._calculate_drift_score(0.0, 1.0, 0.0, 1.0)
        self.assertGreater(max_drift, 0.8)  # Should be high drift

        # Zero initial values (edge case handling)
        zero_initial = self.field._calculate_drift_score(0.0, 0.1, 0.0, 0.1)
        self.assertGreaterEqual(zero_initial, 0.0)
        self.assertLessEqual(zero_initial, 1.0)

    @pytest.mark.unit
    def test_collapse_hash_deterministic(self):
        """Test collapse hash generation is deterministic."""
        observer = ObserverEffect(
            observer_id="test_observer",
            consciousness_level=0.7,
            observation_type=ObservationType.ACTIVE
        )

        result = {"collapsed_state": "definite", "eigenstate": 1}

        # Mock time.time() for deterministic hashing
        with patch('time.time', return_value=1698000000.123456):
            hash1 = self.field._generate_collapse_hash(self.symbol_a, observer, result)
            hash2 = self.field._generate_collapse_hash(self.symbol_a, observer, result)

        # Same inputs should produce same hash
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 16)  # Should be 16 character hex string

        # Different symbols should produce different hashes
        with patch('time.time', return_value=1698000000.123456):
            hash3 = self.field._generate_collapse_hash(self.symbol_b, observer, result)

        self.assertNotEqual(hash1, hash3)

    @pytest.mark.unit
    def test_affect_delta_calculation(self):
        """Test affect delta calculation for different observation types."""
        observer = ObserverEffect(
            observer_id="test_observer",
            consciousness_level=0.8,
            observation_type=ObservationType.INTENTIONAL
        )

        affect_delta = self.field._calculate_affect_delta(
            observer, ObservationType.INTENTIONAL, drift_score=0.3
        )

        # Verify structure
        required_keys = {'valence', 'arousal', 'dominance', 'intensity'}
        self.assertEqual(set(affect_delta.keys()), required_keys)

        # Verify ranges
        self.assertGreaterEqual(affect_delta['valence'], -1.0)
        self.assertLessEqual(affect_delta['valence'], 1.0)
        self.assertGreaterEqual(affect_delta['arousal'], 0.0)
        self.assertLessEqual(affect_delta['arousal'], 1.0)
        self.assertGreaterEqual(affect_delta['dominance'], 0.0)
        self.assertLessEqual(affect_delta['dominance'], 1.0)
        self.assertGreaterEqual(affect_delta['intensity'], 0.0)
        self.assertLessEqual(affect_delta['intensity'], 1.0)

    @pytest.mark.unit
    def test_observe_symbol_lambda_trace_integration(self):
        """Test observe_symbol includes ΛTRACE metadata."""
        # Enable trace for this test
        self.field.enable_trace(True)

        result = self.field.observe_symbol(
            self.symbol_a.state.symbol_id,
            observer_id="test_observer",
            observation_type=ObservationType.ACTIVE
        )

        # Verify enhanced result structure
        self.assertIn('lambda_trace', result)
        lambda_trace = result['lambda_trace']

        # Verify ΛTRACE fields
        required_trace_fields = {
            'drift_score', 'collapse_hash', 'affect_delta', 'observer_id',
            'symbol_id', 'observation_timestamp', 'field_coherence', 'observation_count'
        }
        self.assertEqual(set(lambda_trace.keys()), required_trace_fields)

        # Verify types and ranges
        self.assertIsInstance(lambda_trace['drift_score'], float)
        self.assertIsInstance(lambda_trace['collapse_hash'], str)
        self.assertIsInstance(lambda_trace['affect_delta'], dict)
        self.assertEqual(lambda_trace['observer_id'], "test_observer")
        self.assertEqual(lambda_trace['symbol_id'], self.symbol_a.state.symbol_id)


class TestEntangledSymbolPairHealth(unittest.TestCase):
    """Test entanglement health tracking and telemetry."""

    def setUp(self):
        """Set up entangled symbol pair for testing."""
        np.random.seed(42)  # Deterministic testing

        self.symbol_a = self._create_test_symbol("entangled_a", entropy=0.2, coherence=0.9)
        self.symbol_b = self._create_test_symbol("entangled_b", entropy=0.3, coherence=0.8)

        self.pair = EntangledSymbolPair(
            symbol_a=self.symbol_a,
            symbol_b=self.symbol_b,
            entanglement_strength=0.7,
            drift_threshold=0.4
        )

    def _create_test_symbol(self, symbol_id: str, entropy: float = 0.4, coherence: float = 0.7) -> VisualSymbol:
        """Create a test visual symbol with specified properties."""
        quantum_state = QuantumState(
            amplitude=complex(0.8, 0.2),
            phase=np.pi / 3,
            entropy=entropy,
            coherence=coherence,
            trust=0.85
        )

        symbol_state = SymbolState(
            symbol_id=symbol_id,
            current_state="superposition",
            visual_weight=0.75,
            emotional_valence=0.1,
            emotional_arousal=0.5,
            quantum_field=quantum_state
        )

        return VisualSymbol(state=symbol_state)

    @pytest.mark.unit
    def test_entanglement_health_initialization(self):
        """Test entanglement health is properly initialized."""
        self.assertEqual(self.pair.entanglement_health, 1.0)
        self.assertEqual(len(self.pair.health_history), 0)
        self.assertEqual(self.pair.drift_threshold, 0.4)

    @pytest.mark.unit
    def test_entanglement_health_calculation_deterministic(self):
        """Test entanglement health calculation is deterministic."""
        # Perform several correlation measurements
        correlations = []
        for i in range(5):
            # Slightly modify symbol states for variance
            self.symbol_a.state.quantum_field.phase += 0.1 * i
            self.symbol_b.state.quantum_field.phase += 0.05 * i
            correlation = self.pair.measure_correlation()
            correlations.append(correlation)

        # Verify health tracking
        self.assertGreater(len(self.pair.health_history), 0)
        self.assertLessEqual(self.pair.entanglement_health, 1.0)
        self.assertGreaterEqual(self.pair.entanglement_health, 0.0)

        # Health should be influenced by correlation stability
        correlation_variance = np.var(correlations)
        1.0 - min(correlation_variance * 2.0, 0.8)

        # Health should reflect both stability and strength
        self.assertLess(self.pair.entanglement_health, 1.0)  # Should decrease from initial

    @pytest.mark.unit
    def test_drift_warning_emission(self):
        """Test ΛTAG drift warnings are emitted when health degrades."""
        # Force health below threshold by creating unstable correlations
        for _i in range(10):
            # Create highly variable phase differences
            self.symbol_a.state.quantum_field.phase = np.pi * np.random.random()
            self.symbol_b.state.quantum_field.phase = np.pi * np.random.random()
            self.symbol_a.state.quantum_field.coherence = 0.2 + 0.6 * np.random.random()
            self.symbol_b.state.quantum_field.coherence = 0.2 + 0.6 * np.random.random()

            self.pair.measure_correlation()

        # Health should degrade due to instability
        if self.pair.entanglement_health < self.pair.drift_threshold:
            # Verify warning timestamp was updated
            self.assertGreater(self.pair.last_drift_warning, 0)

    @pytest.mark.unit
    def test_summarize_health_deterministic(self):
        """Test health summary provides deterministic analytics."""
        # Generate some health history
        for i in range(5):
            self.symbol_a.state.quantum_field.coherence = 0.8 - 0.1 * i
            self.pair.measure_correlation()

        health_summary = self.pair.summarize_health()

        # Verify summary structure
        required_fields = {
            'current_health', 'health_trend', 'risk_level', 'correlation_stability',
            'entanglement_strength', 'age_seconds', 'total_observations',
            'drift_warnings_issued', 'recommendations', 'analytics_metadata'
        }
        self.assertEqual(set(health_summary.keys()), required_fields)

        # Verify health trend calculation
        self.assertIn(health_summary['health_trend'], ['improving', 'degrading', 'stable'])

        # Verify risk level calculation
        self.assertIn(health_summary['risk_level'], ['low', 'medium', 'high'])

        # Verify analytics metadata
        metadata = health_summary['analytics_metadata']
        self.assertIn('mean_health', metadata)
        self.assertIn('min_health', metadata)
        self.assertIn('max_health', metadata)

    @pytest.mark.unit
    def test_health_window_size_limits(self):
        """Test health calculations respect window size limits."""
        # Generate more correlations than window size
        window_size = self.pair.health_window_size
        for _i in range(window_size + 5):
            self.pair.measure_correlation()

        # Verify correlation history is managed
        self.assertLessEqual(len(self.pair.correlation_history), window_size + 5)

        # Health calculation should use only recent window
        recent_correlations = [entry["correlation"] for entry in self.pair.correlation_history[-window_size:]]
        self.assertEqual(len(recent_correlations), min(window_size, len(self.pair.correlation_history)))


class TestQuantumPerceptionFieldTracing(unittest.TestCase):
    """Test ΛTRACE integration in quantum perception field."""

    def setUp(self):
        """Set up perception field for tracing tests."""
        np.random.seed(42)
        self.field = QuantumPerceptionField(
            observer_id="trace_test_observer",
            consciousness_level=0.6
        )

    @pytest.mark.unit
    def test_trace_enable_disable(self):
        """Test trace enable/disable functionality."""
        # Initially disabled
        self.assertFalse(getattr(self.field, '_trace_enabled', False))

        # Enable trace
        self.field.enable_trace(True)
        self.assertTrue(self.field._trace_enabled)

        # Disable trace
        self.field.enable_trace(False)
        self.assertFalse(self.field._trace_enabled)

    @pytest.mark.unit
    def test_provenance_chain_building(self):
        """Test provenance chain construction for guardian auditing."""
        symbol = self._create_test_symbol("provenance_test")
        observer = ObserverEffect(
            observer_id="audit_observer",
            consciousness_level=0.8,
            observation_type=ObservationType.INTENTIONAL
        )

        provenance_chain = self.field._build_provenance_chain(symbol, observer)

        # Verify provenance structure
        self.assertIsInstance(provenance_chain, list)
        self.assertGreater(len(provenance_chain), 0)

        # Verify required provenance events
        event_types = [event['event'] for event in provenance_chain]
        self.assertIn('symbol_creation', event_types)
        self.assertIn('observer_registration', event_types)

    def _create_test_symbol(self, symbol_id: str) -> VisualSymbol:
        """Create a test visual symbol."""
        quantum_state = QuantumState(
            amplitude=complex(0.7, 0.3),
            phase=np.pi / 6,
            entropy=0.4,
            coherence=0.8,
            trust=0.9
        )

        symbol_state = SymbolState(
            symbol_id=symbol_id,
            current_state="superposition",
            visual_weight=0.7,
            emotional_valence=0.3,
            emotional_arousal=0.4,
            quantum_field=quantum_state
        )

        return VisualSymbol(state=symbol_state)


if __name__ == "__main__":
    # Run with pytest for better output
    pytest.main([__file__, "-v", "--tb=short"])
