import asyncio
import unittest

from core.bio_systems.bio_simulation_controller import BioSimulationController


class TestSimulationController(unittest.IsolatedAsyncioTestCase):

    async def test_hormone_decay(self):
        """
        Tests that the hormone levels decay over time.
        """
        controller = BioSimulationController()
        controller.add_hormone("testosterone", 1.0, 0.1)
        await controller.start_simulation()
        await asyncio.sleep(1.1)
        self.assertLess(controller.hormones["testosterone"].level, 1.0)
        await controller.stop_simulation()


if __name__ == "__main__":
    unittest.main()
