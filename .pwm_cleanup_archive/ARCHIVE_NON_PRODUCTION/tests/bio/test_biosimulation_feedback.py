import asyncio
import unittest

from core.bio_systems.bio_simulation_controller import BioSimulationController


class TestBioSimulationFeedback(unittest.IsolatedAsyncioTestCase):

    async def test_pulse_correction(self):
        """
        Tests that the pulse correction logic is working correctly.
        """
        controller = BioSimulationController()
        controller.add_hormone("cortisol", 0.5, 0.1)
        controller.add_hormone("dopamine", 0.5, 0.1)
        controller.add_hormone("serotonin", 0.5, 0.1)

        controller.driftScore = 0.6
        controller.affect_delta = 0.6
        await controller.start_simulation()
        await asyncio.sleep(1.1)
        self.assertGreater(controller.hormones["cortisol"].level, 0.5)
        self.assertGreater(controller.hormones["dopamine"].level, 0.5)
        await controller.stop_simulation()

    async def test_recovery_loop(self):
        """
        Tests that the recovery loop is working correctly.
        """
        controller = BioSimulationController()
        controller.add_hormone("cortisol", 1.0, 0.1)
        controller.driftScore = 0.8
        controller.recover()
        self.assertEqual(controller.driftScore, 0.0)
        self.assertEqual(controller.hormones["cortisol"].level, 0.5)


if __name__ == "__main__":
    unittest.main()
