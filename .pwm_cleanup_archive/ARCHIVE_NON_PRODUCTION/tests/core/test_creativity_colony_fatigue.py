import unittest
from unittest.mock import patch

from core.colonies.creativity_colony import CreativityColony


class TestCreativityColonyFatigue(unittest.TestCase):
    @patch("lukhas.core.colonies.creativity_colony.fatigue_level", return_value=0.6)
    def test_update_task_slots(self, mock_fatigue):
        colony = CreativityColony("creativity")
        colony.update_task_slots()
        self.assertEqual(colony.task_slots, max(1, int(3 * (1.0 - 0.6))))
        self.assertAlmostEqual(colony.driftScore, 1.0 - 0.6)


if __name__ == "__main__":
    unittest.main()
