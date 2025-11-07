import random
import unittest
from candidate.quantum.measurement import QuantumMeasurement
from candidate.quantum.superposition_engine import SuperpositionState

class TestQuantumMeasurement(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.measurement = QuantumMeasurement(rng=self.rng)
        self.options = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        self.amplitudes = [1/3**0.5, 1/3**0.5, 1/3**0.5]
        self.state = SuperpositionState(
            options=self.options,
            amplitudes=[complex(a) for a in self.amplitudes],
            metadata={"probabilities": [1/3, 1/3, 1/3], "coherence": 1.0},
        )

    def test_collapse_basic(self):
        result = self.measurement.collapse(self.state)
        self.assertIn(result.collapsed_option, self.options)
        self.assertIn(result.selected_index, [0, 1, 2])
        self.assertAlmostEqual(sum(result.metadata["probabilities"]), 1.0)
        self.assertLess(result.post_state.metadata["coherence"], 1.0)

    def test_collapse_with_bias(self):
        context = {"bias": {"B": 2.0}}  # Strongly bias towards option B
        result = self.measurement.collapse(self.state, context)
        # With a strong bias and a fixed seed, we expect a deterministic result
        self.assertEqual(result.collapsed_option["id"], "B")
        self.assertEqual(result.selected_index, 1)

    def test_collapse_argmax_mode(self):
        # Even with a different seed, argmax should be deterministic
        measurement_engine = QuantumMeasurement(rng=random.Random(1))
        context = {"mode": "argmax", "bias": {"C": 1.5}}
        result = measurement_engine.collapse(self.state, context)
        self.assertEqual(result.collapsed_option["id"], "C")
        self.assertEqual(result.selected_index, 2)

    def test_no_options_to_measure(self):
        empty_state = SuperpositionState(options=[], amplitudes=[], metadata={})
        with self.assertRaises(ValueError):
            self.measurement.collapse(empty_state)

    def test_decoherence(self):
        context = {"decoherence": 0.5}
        initial_norm = sum(abs(amp) ** 2 for amp in self.state.amplitudes)
        result = self.measurement.collapse(self.state, context)
        final_norm = sum(abs(amp) ** 2 for amp in result.post_state.amplitudes)
        self.assertAlmostEqual(final_norm, 1.0) # Should be renormalized
        # Check if coherence is reduced as expected
        self.assertAlmostEqual(result.post_state.metadata["coherence"], self.state.metadata.get("coherence", 1.0) * 0.5)


    def test_preferred_option(self):
        context = {"preferred_option": "A", "preferred_weight": 5.0}
        # Given the strong preference, the result should be deterministic with a fixed seed
        result = self.measurement.collapse(self.state, context)
        self.assertEqual(result.collapsed_option["id"], "A")

    def test_zero_probabilities_bias(self):
        # Create a bias that makes all probabilities zero
        context = {"bias": {"A": -1.0, "B": -1.0, "C": -1.0}}
        result = self.measurement.collapse(self.state, context)
        # It should revert to a uniform distribution
        self.assertAlmostEqual(result.probability, 1/3, places=5)

if __name__ == "__main__":
    unittest.main()
