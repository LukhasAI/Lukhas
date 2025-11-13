
import unittest
from unittest.mock import MagicMock

from candidate.quantum.measurement_history import MeasurementHistory
from candidate.quantum.superposition_engine import SuperpositionState


class TestMeasurementHistory(unittest.TestCase):
    def setUp(self):
        self.history = MeasurementHistory(max_history=10)
        self.state1 = SuperpositionState(
            options=[{"id": "a"}, {"id": "b"}],
            amplitudes=[(2**-0.5), (2**-0.5)],
            metadata={},
        )
        self.state2 = SuperpositionState(
            options=[{"id": "x"}, {"id": "y"}],
            amplitudes=[(2**-0.5), (2**-0.5)],
            metadata={},
        )
        self.context1 = {"setting": "test"}
        self.context2 = {"setting": "prod"}

    def test_record_measurement_adds_to_history(self):
        self.assertEqual(len(self.history.measurements), 0)
        self.history.record_measurement(self.state1, self.context1, "a", 0.5)
        self.assertEqual(len(self.history.measurements), 1)
        self.assertEqual(self.history.measurements[0]["outcome_label"], "a")

    def test_max_history_is_respected(self):
        for i in range(12):
            self.history.record_measurement(self.state1, self.context1, "a", i / 12)
        self.assertEqual(len(self.history.measurements), 10)
        self.assertAlmostEqual(self.history.measurements[0]["probability"], 2 / 12)

    def test_estimate_future_bias_no_history(self):
        bias = self.history.estimate_future_bias(self.state1, self.context1)
        self.assertEqual(bias, {})

    def test_estimate_future_bias_simple_case(self):
        self.history.record_measurement(self.state1, self.context1, "a", 0.8)
        self.history.record_measurement(self.state1, self.context1, "a", 0.8)
        self.history.record_measurement(self.state1, self.context1, "b", 0.2)

        bias = self.history.estimate_future_bias(self.state1, self.context1)

        # Expected probs: a=2/3, b=1/3. Avg prob = 0.5
        # Bias: a = 0.66 - 0.5 = 0.166, b = 0.33 - 0.5 = -0.166
        self.assertAlmostEqual(bias["a"], 1/6)
        self.assertAlmostEqual(bias["b"], -1/6)

    def test_history_segregation_by_state(self):
        self.history.record_measurement(self.state1, self.context1, "a", 0.9)
        self.history.record_measurement(self.state2, self.context1, "x", 0.1)

        bias1 = self.history.estimate_future_bias(self.state1, self.context1)
        self.assertIn("a", bias1)
        self.assertNotIn("x", bias1)

        bias2 = self.history.estimate_future_bias(self.state2, self.context1)
        self.assertIn("x", bias2)
        self.assertNotIn("a", bias2)

    def test_history_segregation_by_context(self):
        self.history.record_measurement(self.state1, self.context1, "a", 0.9)
        self.history.record_measurement(self.state1, self.context2, "b", 0.1)

        bias1 = self.history.estimate_future_bias(self.state1, self.context1)
        self.assertIn("a", bias1)
        self.assertNotIn("b", bias1)

        bias2 = self.history.estimate_future_bias(self.state1, self.context2)
        self.assertIn("b", bias2)
        self.assertNotIn("a", bias2)

    def test_stable_state_and_context_ids(self):
        state_id1 = self.history._get_state_id(self.state1)
        state_id2 = self.history._get_state_id(self.state1)
        self.assertEqual(state_id1, state_id2)

        context_id1 = self.history._get_context_id(self.context1)
        context_id2 = self.history._get_context_id(self.context1)
        self.assertEqual(context_id1, context_id2)

    def test_context_id_ignores_volatile_keys(self):
        context1 = {"setting": "test", "bias": {"a": 1.0}}
        context2 = {"setting": "test", "preferred_option": "b"}
        context_id1 = self.history._get_context_id(context1)
        context_id2 = self.history._get_context_id(context2)
        base_context_id = self.history._get_context_id({"setting": "test"})
        self.assertEqual(context_id1, base_context_id)
        self.assertEqual(context_id2, base_context_id)

if __name__ == "__main__":
    unittest.main()
