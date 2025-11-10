
import asyncio
import random
import unittest
from unittest.mock import MagicMock, patch

from candidate.quantum.entanglement import EntanglementEngine, EntangledSystem
from candidate.quantum.superposition_engine import SuperpositionState, QuantumSuperpositionEngine
from candidate.quantum.measurement import QuantumMeasurement, MeasurementResult

def create_simple_superposition_state(n_options=2, label="s") -> SuperpositionState:
    """Helper function to create a basic SuperpositionState."""
    options = [{"id": f"{label}_{i}", "value": i} for i in range(n_options)]
    engine = QuantumSuperpositionEngine()
    return engine.create_state(options)

class TestEntanglementEngine(unittest.TestCase):

    def setUp(self):
        """Set up a new EntanglementEngine for each test."""
        self.engine = EntanglementEngine()
        self.state1 = create_simple_superposition_state(2, "a")
        self.state2 = create_simple_superposition_state(2, "b")
        self.state3 = create_simple_superposition_state(2, "c")

    def test_initialization(self):
        """Test that the EntanglementEngine initializes correctly."""
        self.assertIsInstance(self.engine, EntanglementEngine)
        self.assertEqual(self.engine.entangled_systems, {})

    def test_create_entanglement_requires_two_or_more_states(self):
        """Test that entanglement creation fails with fewer than two states."""
        with self.assertRaises(ValueError):
            self.engine.create_entanglement([self.state1])

    def test_create_entanglement_creates_system(self):
        """Test that a new entangled system is created and tracked."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        self.assertIsInstance(system, EntangledSystem)
        self.assertIn(system.system_id, self.engine.entangled_systems)
        self.assertEqual(len(system.states), 2)
        self.assertEqual(len(system.correlation_matrix), 2)
        self.assertEqual(len(system.correlation_matrix[0]), 2)
        self.assertEqual(system.correlation_matrix[0][0], 1.0)
        self.assertEqual(system.correlation_matrix[1][1], 1.0)
        self.assertIn(system.correlation_matrix[0][1], [1.0, -1.0])
        self.assertEqual(system.correlation_matrix[0][1], system.correlation_matrix[1][0])

    def test_create_entanglement_with_three_states(self):
        """Test creating an entangled system with three states."""
        system = self.engine.create_entanglement([self.state1, self.state2, self.state3])
        self.assertEqual(len(system.states), 3)
        self.assertEqual(len(system.correlation_matrix), 3)
        for i in range(3):
            self.assertEqual(system.correlation_matrix[i][i], 1.0)
        self.assertEqual(system.correlation_matrix[0][1], system.correlation_matrix[1][0])
        self.assertEqual(system.correlation_matrix[0][2], system.correlation_matrix[2][0])
        self.assertEqual(system.correlation_matrix[1][2], system.correlation_matrix[2][1])

    @patch('candidate.quantum.measurement.QuantumMeasurement.collapse')
    def test_measure_system_correlated_outcome(self, mock_collapse):
        """Test that measuring one state collapses others to correlated outcomes."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        # Force correlation
        system.correlation_matrix[0][1] = 1.0
        system.correlation_matrix[1][0] = 1.0

        # Mock the measurement result
        mock_result = MagicMock(spec=MeasurementResult)
        mock_result.selected_index = 0
        mock_result.collapsed_option = self.state1.options[0]
        mock_collapse.return_value = mock_result

        outcomes = self.engine.measure_system(system, 0)

        mock_collapse.assert_called_once_with(self.state1, {})
        self.assertEqual(outcomes[0], self.state1.options[0])
        self.assertEqual(outcomes[1], self.state2.options[0])

    @patch('candidate.quantum.measurement.QuantumMeasurement.collapse')
    def test_measure_system_anti_correlated_outcome(self, mock_collapse):
        """Test anti-correlated outcomes."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        # Force anti-correlation
        system.correlation_matrix[0][1] = -1.0
        system.correlation_matrix[1][0] = -1.0

        mock_result = MagicMock(spec=MeasurementResult)
        mock_result.selected_index = 0
        mock_result.collapsed_option = self.state1.options[0]
        mock_collapse.return_value = mock_result

        outcomes = self.engine.measure_system(system, 0)

        self.assertEqual(outcomes[0], self.state1.options[0])
        self.assertEqual(outcomes[1], self.state2.options[1])

    @patch('candidate.quantum.measurement.QuantumMeasurement.collapse')
    def test_measure_different_state_in_pair(self, mock_collapse):
        """Test measuring the second state in a pair."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        system.correlation_matrix[0][1] = 1.0
        system.correlation_matrix[1][0] = 1.0

        mock_result = MagicMock(spec=MeasurementResult)
        mock_result.selected_index = 1
        mock_result.collapsed_option = self.state2.options[1]
        mock_collapse.return_value = mock_result

        outcomes = self.engine.measure_system(system, 1)

        mock_collapse.assert_called_once_with(self.state2, {})
        self.assertEqual(outcomes[1], self.state2.options[1])
        self.assertEqual(outcomes[0], self.state1.options[1])

    def test_measurement_with_real_measurement_class(self):
        """Test the full measurement process without mocking the collapse."""
        # Use a deterministic RNG for predictable measurement outcomes
        rng = random.Random(42)
        engine = EntanglementEngine(measurement_harness=QuantumMeasurement(rng=rng), rng=rng)
        state_a = create_simple_superposition_state(2, "a")
        state_b = create_simple_superposition_state(2, "b")

        system = engine.create_entanglement([state_a, state_b])
        system.correlation_matrix[0][1] = 1.0  # Force correlation
        system.correlation_matrix[1][0] = 1.0

        # With seed 42, the first collapse will select index 0.
        outcomes = engine.measure_system(system, 0)

        self.assertEqual(outcomes[0]['id'], 'a_0')
        self.assertEqual(outcomes[1]['id'], 'b_0')

    def test_bell_state_violation_simulation(self):
        """Simulate a CHSH-like experiment to test for Bell's inequality violation."""
        # This is a simplified, conceptual test that does not model measurement bases.
        # It demonstrates that the model can produce perfectly anti-correlated results,
        # which is a prerequisite for, but not a proof of, Bell's inequality violation.
        rng = random.Random(1337)
        engine = EntanglementEngine(measurement_harness=QuantumMeasurement(rng=rng), rng=rng)

        correlations = []
        for _ in range(100): # Run 100 trials
            state_a = create_simple_superposition_state(2, "a")
            state_b = create_simple_superposition_state(2, "b")
            system = engine.create_entanglement([state_a, state_b])
            system.correlation_matrix[0][1] = -1.0 # Anti-correlated (like a Bell pair)
            system.correlation_matrix[1][0] = -1.0

            # Alice and Bob choose their measurement settings (bases) randomly
            basis_a = {'basis': rng.choice(['Z', 'X'])}
            basis_b = {'basis': rng.choice(['Z', 'X'])}

            # For this simplified model, we'll just check if the outcomes are
            # correlated or anti-correlated. A real test would involve calculating
            # expectation values based on the measurement bases.

            # We measure state_a in basis_a and see what state_b should be
            outcomes = engine.measure_system(system, 0, context=basis_a)
            outcome_a = outcomes[0]['value']
            outcome_b = outcomes[1]['value']

            # CHSH inequality is |E(a,b) - E(a,b') + E(a',b) + E(a',b')| <= 2
            # For our simplified test, we'll just check that there is a strong
            # correlation when bases are the same, and weaker otherwise.

            if basis_a['basis'] == basis_b['basis']:
                # Expect perfect anti-correlation
                self.assertNotEqual(outcome_a, outcome_b)
            # A more detailed model would be needed to properly test the inequality.
            # We are just showing that the model *can* produce results that
            # are consistent with violations of local realism.

    def test_decoherence_weakens_correlation(self):
        """Test that decoherence reduces the strength of correlations."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        system.correlation_matrix[0][1] = 1.0
        system.correlation_matrix[1][0] = 1.0

        self.engine.apply_decoherence(system, 0.3)
        self.assertAlmostEqual(system.correlation_matrix[0][1], 0.7)
        self.assertAlmostEqual(system.correlation_matrix[1][0], 0.7)

    def test_full_decoherence_destroys_correlation(self):
        """Test that a decoherence of 1.0 removes the correlation."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        system.correlation_matrix[0][1] = 1.0
        system.correlation_matrix[1][0] = 1.0

        self.engine.apply_decoherence(system, 1.0)
        self.assertAlmostEqual(system.correlation_matrix[0][1], 0.0)
        self.assertAlmostEqual(system.correlation_matrix[1][0], 0.0)

    def test_decoherence_with_no_effect_at_zero_strength(self):
        """Test that decoherence has no effect at zero strength."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        system.correlation_matrix[0][1] = -1.0
        system.correlation_matrix[1][0] = -1.0

        self.engine.apply_decoherence(system, 0.0)
        self.assertEqual(system.correlation_matrix[0][1], -1.0)
        self.assertEqual(system.correlation_matrix[1][0], -1.0)

    def test_decoherence_raises_error_for_invalid_strength(self):
        """Test that decoherence raises a ValueError for out-of-bounds strength."""
        system = self.engine.create_entanglement([self.state1, self.state2])
        with self.assertRaises(ValueError):
            self.engine.apply_decoherence(system, 1.1)
        with self.assertRaises(ValueError):
            self.engine.apply_decoherence(system, -0.1)

    @patch('candidate.quantum.measurement.QuantumMeasurement.collapse')
    def test_ghz_state_measurement(self, mock_collapse):
        """Test measurement of a 3-particle GHZ-like state."""
        system = self.engine.create_entanglement([self.state1, self.state2, self.state3])
        # All states are correlated
        system.correlation_matrix = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

        mock_result = MagicMock(spec=MeasurementResult)
        mock_result.selected_index = 0
        mock_result.collapsed_option = self.state1.options[0]
        mock_collapse.return_value = mock_result

        outcomes = self.engine.measure_system(system, 0)

        self.assertEqual(outcomes[0], self.state1.options[0])
        self.assertEqual(outcomes[1], self.state2.options[0])
        self.assertEqual(outcomes[2], self.state3.options[0])

    @patch('candidate.quantum.measurement.QuantumMeasurement.collapse')
    def test_mixed_correlation_in_three_particle_system(self, mock_collapse):
        """Test a system with mixed correlations."""
        system = self.engine.create_entanglement([self.state1, self.state2, self.state3])
        # s1 and s2 are correlated, s1 and s3 are anti-correlated
        system.correlation_matrix = [[1.0, 1.0, -1.0], [1.0, 1.0, 0.0], [-1.0, 0.0, 1.0]]

        mock_result = MagicMock(spec=MeasurementResult)
        mock_result.selected_index = 1
        mock_result.collapsed_option = self.state1.options[1]
        mock_collapse.return_value = mock_result

        outcomes = self.engine.measure_system(system, 0)

        self.assertEqual(outcomes[0], self.state1.options[1])
        self.assertEqual(outcomes[1], self.state2.options[1]) # Correlated with s1
        self.assertEqual(outcomes[2], self.state3.options[0]) # Anti-correlated with s1

if __name__ == '__main__':
    unittest.main()
