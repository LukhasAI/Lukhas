import asyncio
import unittest

from core.bio_systems.bio_oscillator import MoodOscillator, OscillationType
from core.bio_systems.bio_simulation_controller import BioSimulationController


class TestBioPhaseControl(unittest.IsolatedAsyncioTestCase):

    async def test_trigger_phase_shift(self):
        """
        Tests that the trigger_phase_shift function is working correctly.
        """
        controller = BioSimulationController()
        mood_oscillator = MoodOscillator()
        mood_oscillator.phase = 0.0
        controller.trigger_phase_shift(mood_oscillator, 0.4)
        self.assertEqual(mood_oscillator.phase, 0.4)

        # Test that the phase shift is ignored if it's too large
        controller.trigger_phase_shift(mood_oscillator, 1.0)
        self.assertEqual(mood_oscillator.phase, 0.4)

    async def test_stabilize_oscillator(self):
        """
        Tests that the stabilize_oscillator function is working correctly.
        """
        controller = BioSimulationController()
        mood_oscillator = MoodOscillator()
        mood_oscillator.driftScore = 0.8
        mood_oscillator.affect_delta = 0.8
        mood_oscillator.target_frequency = 100.0
        controller.stabilize_oscillator(mood_oscillator)
        await asyncio.sleep(0.01)  # allow the task to run
        self.assertEqual(mood_oscillator.driftScore, 0.0)
        self.assertEqual(mood_oscillator.affect_delta, 0.0)
        self.assertEqual(
            mood_oscillator.target_frequency,
            mood_oscillator._get_default_frequency(OscillationType.ALPHA),
        )


if __name__ == "__main__":
    unittest.main()
