
import random
import unittest
from unittest.mock import MagicMock, patch

from candidate.quantum.measurement import MeasurementResult, QuantumMeasurement
from candidate.quantum.measurement_history import MeasurementHistory
from candidate.quantum.superposition_engine import SuperpositionState


class TestQuantumMeasurement(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.history = MeasurementHistory()
        self.measurement = QuantumMeasurement(rng=self.rng, history=self.history)
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

    @patch.object(MeasurementHistory, "estimate_future_bias")
    def test_historical_bias_is_applied(self, mock_estimate_bias):
        mock_estimate_bias.return_value = {"a": 0.5}  # Strong bias towards 'a'

        results = [self.measurement.collapse(self.state).selected_index for _ in range(100)]

        # Expect 'a' (index 0) to be chosen more often than not
        self.assertGreater(results.count(0), 60)
        mock_estimate_bias.assert_called()

    @patch.object(MeasurementHistory, "record_measurement")
    def test_measurement_is_recorded(self, mock_record):
        self.measurement.collapse(self.state)
        mock_record.assert_called_once()
        call_args = mock_record.call_args[0]
        self.assertIsInstance(call_args[0], SuperpositionState)
        self.assertIsInstance(call_args[1], dict) # context
        self.assertIn(call_args[2], ["a", "b"]) # outcome_label
        self.assertIsInstance(call_args[3], float) # probability

    def test_integration_with_history(self):
        # First measurement, biased towards 'a'
        self.measurement.collapse(self.state, context={"bias": {"a": 1.0}})

        # Now, collapse again. History should create a bias towards 'a'
        # even without explicit context bias.

        # To make the test deterministic, let's rig the history estimate
        with patch.object(self.history, 'estimate_future_bias', return_value={"a": 0.25}):
             result = self.measurement.collapse(self.state)
             # Base probs are 0.5, 0.5. Bias for 'a' is 0.25
             # Modifier for 'a' is 1.25, for 'b' is 1.0
             # Weighted: 0.5*1.25 = 0.625, 0.5*1.0=0.5. Total = 1.125
             # Final probs: a=0.555..., b=0.444...
             self.assertAlmostEqual(result.metadata["probabilities"][0], 0.625 / 1.125)

if __name__ == "__main__":
    unittest.main()
