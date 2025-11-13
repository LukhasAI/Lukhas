import cmath
import math
import random
import unittest
from unittest.mock import MagicMock

from candidate.quantum.superposition_engine import (
    QuantumSuperpositionEngine,
    SuperpositionState,
)


class TestQuantumSuperpositionEngine(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.engine = QuantumSuperpositionEngine(rng=self.rng)
        self.options = [{"id": "a", "value": 1}, {"id": "b", "value": 2}]

    def test_create_state_returns_superposition_state(self):
        state = self.engine.create_state(self.options)
        self.assertIsInstance(state, SuperpositionState)
        self.assertEqual(len(state.options), 2)
        self.assertEqual(len(state.amplitudes), 2)

    def test_create_state_normalizes_amplitudes(self):
        state = self.engine.create_state(self.options)
        norm = sum(abs(amp) ** 2 for amp in state.amplitudes)
        self.assertAlmostEqual(norm, 1.0)

    def test_create_state_with_empty_options_raises_error(self):
        with self.assertRaises(ValueError):
            self.engine.create_state([])

    def test_amplitude_computation_with_weights(self):
        options = [{"id": "a", "weight": 4}, {"id": "b", "weight": 1}]
        state = self.engine.create_state(options)
        # Probabilities should be proportional to weights (16:1)
        prob_a = abs(state.amplitudes[0]) ** 2
        prob_b = abs(state.amplitudes[1]) ** 2
        self.assertAlmostEqual(prob_a / prob_b, 16.0, places=1)

    def test_contextual_bias(self):
        context = {"bias": {"a": 1.0}}  # Double the weight of 'a'
        options = [{"id": "a", "weight": 1}, {"id": "b", "weight": 1}]
        state = self.engine.create_state(options, context)
        prob_a = abs(state.amplitudes[0]) ** 2
        prob_b = abs(state.amplitudes[1]) ** 2
        # Expected weight for a is 1*(1+1)=2, for b is 1. Probability ratio should be 4:1
        self.assertAlmostEqual(prob_a / prob_b, 4.0, places=1)

    def test_phase_resolution(self):
        context = {"phase_seed": "test"}
        state1 = self.engine.create_state(self.options, context)
        state2 = self.engine.create_state(self.options, context)
        # Phases should be deterministic given the same seed
        self.assertEqual(state1.amplitudes[0].real, state2.amplitudes[0].real)
        self.assertEqual(state1.amplitudes[0].imag, state2.amplitudes[0].imag)


    def test_interference_effect(self):
        options = [{"id": "a"}, {"id": "b"}]
        context = {
            "interference": [{"source": "a", "target": "b", "strength": 0.5}]
        }
        state = self.engine.create_state(options, context)
        self.assertIn("interference_events", state.metadata)
        self.assertEqual(len(state.metadata["interference_events"]), 1)
        # Amplitudes should have changed due to interference
        state_no_interference = self.engine.create_state(options)
        self.assertNotEqual(state.amplitudes[0], state_no_interference.amplitudes[0])

    def test_coherence_metadata(self):
        context = {
            "interference": [{"source": "a", "target": "b", "strength": 0.5}]
        }
        state = self.engine.create_state(self.options, context)
        self.assertIn("coherence", state.metadata)
        self.assertLess(state.metadata["coherence"], 1.0)

    def test_zero_norm_reverts_to_uniform(self):
        # All weights are zero, leading to zero norm
        options = [{"id": "a", "weight": 0}, {"id": "b", "weight": 0}]
        state = self.engine.create_state(options)
        self.assertAlmostEqual(abs(state.amplitudes[0]) ** 2, 0.5)
        self.assertAlmostEqual(abs(state.amplitudes[1]) ** 2, 0.5)

    def test_option_label_extraction(self):
        option_id = {"id": "test"}
        option_name = {"name": "test"}
        option_label = {"label": "test"}
        option_action = {"action": "test"}
        option_hashable = {"key": "value"}
        option_unhashable = {"key": ["value"]}

        self.assertEqual(self.engine._option_label(option_id), "test")
        self.assertEqual(self.engine._option_label(option_name), "test")
        self.assertEqual(self.engine._option_label(option_label), "test")
        self.assertEqual(self.engine._option_label(option_action), "test")
        self.assertIsInstance(self.engine._option_label(option_hashable), str)
        self.assertIsInstance(self.engine._option_label(option_unhashable), str)

    def test_extract_weight_with_different_keys(self):
        self.assertEqual(self.engine._extract_weight({"weight": 2.0}), 2.0)
        self.assertEqual(self.engine._extract_weight({"score": 3.0}), 3.0)
        self.assertEqual(self.engine._extract_weight({"confidence": 4.0}), 4.0)
        self.assertEqual(self.engine._extract_weight({"priority": 5.0}), 5.0)
        self.assertEqual(self.engine._extract_weight({"other": 1.0}), 1.0) # Default
        self.assertEqual(self.engine._extract_weight({"weight": "bad"}), 1.0) # Default on error


    def test_phase_noise(self):
        context = {"phase_noise": 0.5}
        state1 = self.engine.create_state(self.options, context)
        state2 = self.engine.create_state(self.options, context)
        # With noise, phases should be different
        self.assertNotEqual(state1.amplitudes[0], state2.amplitudes[0])

    def test_resolve_index(self):
        self.assertEqual(self.engine._resolve_index("a", self.options), 0)
        self.assertEqual(self.engine._resolve_index("b", self.options), 1)
        self.assertIsNone(self.engine._resolve_index("c", self.options))
        self.assertIsNone(self.engine._resolve_index(None, self.options))

    def test_interference_with_unknown_labels(self):
        context = {
            "interference": [{"source": "a", "target": "c", "strength": 0.5}]
        }
        state = self.engine.create_state(self.options, context)
        # No interference should have occurred
        self.assertEqual(len(state.metadata["interference_events"]), 0)


    def test_global_bias(self):
        context = {"global_bias": 0.5}
        state = self.engine.create_state(self.options, context)
        # All probabilities should be affected, but the ratio should remain the same
        prob_a = abs(state.amplitudes[0]) ** 2
        prob_b = abs(state.amplitudes[1]) ** 2
        # Without bias, the ratio is roughly 1:1, global bias should not change that
        self.assertAlmostEqual(prob_a / prob_b, 1.0, places=1)


    def test_single_option_superposition(self):
        single_option = [{"id": "lonely"}]
        state = self.engine.create_state(single_option)
        self.assertEqual(len(state.options), 1)
        self.assertAlmostEqual(abs(state.amplitudes[0]), 1.0)

    def test_complex_options_hashing(self):
        complex_options = [{"data": [1, 2], "frozen": frozenset([3, 4])}]
        # Should not raise a TypeError
        label = self.engine._option_label(complex_options[0])
        self.assertIsInstance(label, str)

    def test_interference_strength_zero(self):
        context = {
            "interference": [{"source": "a", "target": "b", "strength": 0.0}]
        }
        state = self.engine.create_state(self.options, context)
        self.assertEqual(len(state.metadata["interference_events"]), 0)

    def test_phase_from_option(self):
        options = [{"id": "a", "phase": math.pi / 2}]
        state = self.engine.create_state(options)
        self.assertAlmostEqual(cmath.phase(state.amplitudes[0]), math.pi / 2)


if __name__ == "__main__":
    unittest.main()
