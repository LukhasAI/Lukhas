import random
import unittest
import cmath
from candidate.quantum.superposition_engine import QuantumSuperpositionEngine

class TestQuantumSuperpositionEngine(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.engine = QuantumSuperpositionEngine(rng=self.rng)
        self.options = [{"id": "A", "weight": 1}, {"id": "B", "weight": 1}, {"id": "C", "weight": 1}]

    def test_create_state_basic(self):
        state = self.engine.create_state(self.options)
        self.assertEqual(len(state.options), 3)
        self.assertEqual(len(state.amplitudes), 3)
        self.assertAlmostEqual(sum(abs(amp) ** 2 for amp in state.amplitudes), 1.0)
        self.assertIn("probabilities", state.metadata)

    def test_create_state_with_bias(self):
        context = {"bias": {"B": 1.5}} # Bias towards B
        state = self.engine.create_state(self.options, context)
        # Probability of B should be the highest
        prob_b = state.metadata["probabilities"][1]
        self.assertGreater(prob_b, state.metadata["probabilities"][0])
        self.assertGreater(prob_b, state.metadata["probabilities"][2])

    def test_create_state_with_interference(self):
        context = {
            "interference": [
                {"source": "A", "target": "C", "strength": 0.8}
            ]
        }
        state = self.engine.create_state(self.options, context)
        # Check if interference event was recorded
        self.assertEqual(len(state.metadata["interference_events"]), 1)
        # The norm should still be 1 after interference
        self.assertAlmostEqual(sum(abs(amp) ** 2 for amp in state.amplitudes), 1.0)


    def test_no_options_to_create_state(self):
        with self.assertRaises(ValueError):
            self.engine.create_state([])

    def test_normalization(self):
        options = [{"id": "X", "weight": 3}, {"id": "Y", "weight": 4}]
        state = self.engine.create_state(options)
        # Magnitudes should be proportional to weights before normalization
        # After normalization, sum of squares of magnitudes is 1
        self.assertAlmostEqual(sum(p for p in state.metadata["probabilities"]), 1.0)


    def test_phase_resolution(self):
        # With a fixed seed, phases should be deterministic
        state1 = self.engine.create_state(self.options, context={"phase_seed": "seed1"})
        state2 = self.engine.create_state(self.options, context={"phase_seed": "seed1"})
        self.assertEqual(state1.amplitudes, state2.amplitudes)

        # Different seed should result in different phases
        state3 = self.engine.create_state(self.options, context={"phase_seed": "seed2"})
        self.assertNotEqual(state1.amplitudes, state3.amplitudes)

    def test_zero_norm_amplitudes(self):
        # Create a situation where all amplitudes could become zero
        options = [{"id": "Z", "weight": 0}]
        state = self.engine.create_state(options)
        # Should revert to a uniform distribution
        self.assertAlmostEqual(state.metadata["probabilities"][0], 1.0)


if __name__ == "__main__":
    unittest.main()
