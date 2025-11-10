import random
import unittest
from unittest.mock import MagicMock, patch

from candidate.quantum.measurement import MeasurementResult, QuantumMeasurement
from candidate.quantum.superposition_engine import SuperpositionState


class TestQuantumMeasurement(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.measurement = QuantumMeasurement(rng=self.rng)
        self.options = [{"id": "a"}, {"id": "b"}]
        self.amplitudes = [complex(1 / 2**0.5), complex(1 / 2**0.5)]
        self.state = SuperpositionState(
            options=self.options,
            amplitudes=self.amplitudes,
            metadata={"probabilities": [0.5, 0.5]},
        )

    def test_collapse_returns_measurement_result(self):
        result = self.measurement.collapse(self.state)
        self.assertIsInstance(result, MeasurementResult)

    def test_collapse_with_empty_state_raises_error(self):
        empty_state = SuperpositionState(options=[], amplitudes=[], metadata={})
        with self.assertRaises(ValueError):
            self.measurement.collapse(empty_state)

    def test_stochastic_collapse_selects_an_option(self):
        result = self.measurement.collapse(self.state)
        self.assertIn(result.collapsed_option, self.options)
        self.assertIn(result.selected_index, [0, 1])

    def test_argmax_collapse_selects_most_likely(self):
        amplitudes = [complex(0.2), complex(0.8)]
        state = SuperpositionState(
            options=self.options,
            amplitudes=amplitudes,
            metadata={"probabilities": [0.04, 0.64]},
        )
        context = {"mode": "argmax"}
        result = self.measurement.collapse(state, context)
        self.assertEqual(result.selected_index, 1)

    def test_measurement_bias(self):
        context = {"bias": {"a": 3.0}}  # 3.0 means 1+3 = 4x multiplier
        result = self.measurement.collapse(self.state, context)
        # Probabilities were 0.5, 0.5. With bias they become 0.5*4, 0.5*1 -> 2, 0.5
        # Normalized: 2/2.5 = 0.8, 0.5/2.5 = 0.2
        self.assertAlmostEqual(result.metadata["probabilities"][0], 0.8)

    def test_decoherence_effect(self):
        context = {"decoherence": 0.5}
        result = self.measurement.collapse(self.state, context)
        post_norm = sum(abs(amp) ** 2 for amp in result.post_state.amplitudes)
        self.assertAlmostEqual(post_norm, 1.0)
        # Coherence should be reduced
        self.assertLess(
            result.post_state.metadata["coherence"],
            self.state.metadata.get("coherence", 1.0),
        )


    def test_post_collapse_state(self):
        result = self.measurement.collapse(self.state)
        self.assertIsInstance(result.post_state, SuperpositionState)
        self.assertEqual(len(result.post_state.options), 2)

    def test_zero_probabilities_reverts_to_uniform(self):
        # Biasing such that all probabilities become zero
        context = {"bias": {"a": -1.0, "b": -1.0}}
        result = self.measurement.collapse(self.state, context)
        # Should fall back to a 50/50 chance
        self.assertAlmostEqual(result.metadata["probabilities"][0], 0.5)

    def test_metadata_is_correct(self):
        context = {"some_key": "some_value"}
        result = self.measurement.collapse(self.state, context)
        self.assertIn("basis", result.metadata)
        self.assertIn("probabilities", result.metadata)
        self.assertIn("selected_label", result.metadata)
        self.assertIn("coherence_loss", result.metadata)
        self.assertEqual(result.metadata["basis"], context)

    def test_preferred_option_bias(self):
        context = {"preferred_option": "b", "preferred_weight": 9.0} # 1+9=10x multiplier
        result = self.measurement.collapse(self.state, context)
        # Probabilities were 0.5, 0.5. Now 0.5*1, 0.5*10 -> 0.5, 5
        # Normalized: 0.5/5.5, 5/5.5
        self.assertAlmostEqual(result.metadata["probabilities"][1], 5/5.5)


    def test_sampling_is_correct(self):
        probabilities = [0.1, 0.2, 0.7]
        # Rig the RNG to test each range
        with patch.object(self.rng, 'random', return_value=0.05):
            self.assertEqual(self.measurement._sample_index(probabilities), 0)
        with patch.object(self.rng, 'random', return_value=0.15):
            self.assertEqual(self.measurement._sample_index(probabilities), 1)
        with patch.object(self.rng, 'random', return_value=0.5):
            self.assertEqual(self.measurement._sample_index(probabilities), 2)
        with patch.object(self.rng, 'random', return_value=0.99):
            self.assertEqual(self.measurement._sample_index(probabilities), 2) # Last index for value > sum

    def test_single_option_collapse(self):
        single_option_state = SuperpositionState(
            options=[{"id": "lonely"}],
            amplitudes=[complex(1.0)],
            metadata={"probabilities": [1.0]}
        )
        result = self.measurement.collapse(single_option_state)
        self.assertEqual(result.selected_index, 0)
        self.assertAlmostEqual(result.probability, 1.0)


    def test_option_label_extraction(self):
        self.assertEqual(self.measurement._option_label({"id": "x"}), "x")
        self.assertEqual(self.measurement._option_label({"label": "y"}), "y")
        self.assertIsInstance(self.measurement._option_label({"data": [1]}), str)

    def test_state_with_no_probabilities_metadata(self):
        state = SuperpositionState(options=self.options, amplitudes=self.amplitudes, metadata={})
        # Should not raise an error, should fall back to uniform
        result = self.measurement.collapse(state)
        self.assertAlmostEqual(result.metadata['probabilities'][0], 0.5)

    def test_decoherence_range_clamping(self):
        # Decoherence > 1.0 should be clamped to 1.0
        result_high = self.measurement.collapse(self.state, {"decoherence": 2.0})
        self.assertEqual(result_high.metadata['coherence_loss'], 1.0)
        # Decoherence < 0.0 should be clamped to 0.0
        result_low = self.measurement.collapse(self.state, {"decoherence": -1.0})
        self.assertEqual(result_low.metadata['coherence_loss'], 0.0)


if __name__ == "__main__":
    unittest.main()
