import asyncio
import unittest

from core.bio_systems.bio_oscillator import MoodOscillator, OscillationType


class TestOscillatorDriftSafety(unittest.IsolatedAsyncioTestCase):

    async def test_trauma_lock_engagement(self):
        """
        Tests that the trauma lock engages when the drift score is high.
        """
        mood_oscillator = MoodOscillator(simulate_trauma_lock=True)
        mood_oscillator.update_mood(0.0, 0.9)
        await asyncio.sleep(0.01)  # allow the task to run
        self.assertEqual(mood_oscillator.mood_state, "trauma_lock")
        self.assertEqual(
            mood_oscillator.target_frequency,
            mood_oscillator._get_default_frequency(OscillationType.DELTA),
        )

    async def test_mood_phase_transitions(self):
        """
        Tests that the mood phase transitions are working correctly.
        """
        mood_oscillator = MoodOscillator()
        mood_oscillator.update_mood(0.6, 0.0)
        await asyncio.sleep(0.01)  # allow the task to run
        self.assertEqual(mood_oscillator.mood_state, "elated")
        self.assertEqual(
            mood_oscillator.target_frequency,
            mood_oscillator._get_default_frequency(OscillationType.GAMMA),
        )

        mood_oscillator.update_mood(-0.6, 0.0)
        await asyncio.sleep(0.01)  # allow the task to run
        self.assertEqual(mood_oscillator.mood_state, "depressed")
        self.assertEqual(
            mood_oscillator.target_frequency,
            mood_oscillator._get_default_frequency(OscillationType.THETA),
        )

        mood_oscillator.update_mood(0.0, 0.0)
        await asyncio.sleep(0.01)  # allow the task to run
        self.assertEqual(mood_oscillator.mood_state, "neutral")
        self.assertEqual(
            mood_oscillator.target_frequency,
            mood_oscillator._get_default_frequency(OscillationType.ALPHA),
        )

    async def test_bio_loop_recognition(self):
        """
        Tests that the bio loop recognition is working correctly.
        This is a conceptual test, as the bio loop recognition is not fully implemented yet.
        """
        mood_oscillator = MoodOscillator()
        mood_oscillator.update_mood(0.6, 0.0)
        await asyncio.sleep(0.01)  # allow the task to run
        mood_oscillator.update_mood(0.6, 0.0)
        await asyncio.sleep(0.01)  # allow the task to run
        mood_oscillator.update_mood(0.6, 0.0)
        await asyncio.sleep(0.01)  # allow the task to run
        # In the future, this should trigger a bio loop recognition event.
        self.assertEqual(mood_oscillator.mood_state, "elated")


if __name__ == "__main__":
    unittest.main()
