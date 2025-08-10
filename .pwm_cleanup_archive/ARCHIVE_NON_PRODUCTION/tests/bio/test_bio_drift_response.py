import unittest

from core.bio_systems.bio_oscillator import MoodOscillator, OscillationType


class TestBioDriftResponse(unittest.IsolatedAsyncioTestCase):

    # LUKHAS_TAG: drift_test
    async def test_bio_drift_response(self):
        """
        Tests that the bio_drift_response function is working correctly.
        """
        mood_oscillator = MoodOscillator()
        pulse_data = mood_oscillator.bio_drift_response({"joy": 0.8, "sadness": -0.2})
        self.assertAlmostEqual(
            pulse_data["frequency"],
            mood_oscillator._get_default_frequency(OscillationType.ALPHA),
        )
        self.assertAlmostEqual(pulse_data["amplitude"], 0.3)
        self.assertAlmostEqual(pulse_data["variability"], 1.0)

    # ΛTEST: override_verification
    async def test_trauma_triggered_state(self):
        """
        Tests that the trauma-triggered state is working correctly.
        """
        mood_oscillator = MoodOscillator(simulate_trauma_lock=True)
        mood_oscillator.driftScore = 0.9
        pulse_data = mood_oscillator.bio_drift_response({})
        self.assertEqual(
            pulse_data["frequency"],
            mood_oscillator._get_default_frequency(OscillationType.DELTA),
        )
        self.assertEqual(pulse_data["amplitude"], 0.1)
        self.assertEqual(pulse_data["variability"], 0.0)


if __name__ == "__main__":
    unittest.main()
