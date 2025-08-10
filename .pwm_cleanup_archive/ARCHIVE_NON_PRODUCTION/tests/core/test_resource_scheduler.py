import unittest

from core.resource_scheduler import SwarmResourceScheduler
from core.swarm import ResourceState, SwarmHub


class TestSwarmResourceScheduler(unittest.TestCase):
    def setUp(self):
        self.swarm_hub = SwarmHub()
        self.reasoning_colony = self.swarm_hub.register_colony(
            "reasoning", "symbolic:reasoning"
        )
        self.memory_colony = self.swarm_hub.register_colony("memory", "symbolic:memory")
        self.creativity_colony = self.swarm_hub.register_colony(
            "creativity", "symbolic:creativity"
        )
        self.scheduler = SwarmResourceScheduler(self.swarm_hub)

    def test_schedule_to_abundant_colony(self):
        self.swarm_hub.update_colony_resource_state(
            "reasoning", ResourceState.STABLE, 0.5, 0.5
        )
        self.swarm_hub.update_colony_resource_state(
            "memory", ResourceState.ABUNDANT, 0.1, 0.1
        )
        self.swarm_hub.update_colony_resource_state(
            "creativity", ResourceState.STRAINED, 0.8, 0.8
        )

        winner = self.scheduler.schedule_task({"type": "test_task"})
        self.assertEqual(winner, "memory")

    def test_avoid_critical_colony(self):
        self.swarm_hub.update_colony_resource_state(
            "reasoning", ResourceState.STABLE, 0.5, 0.5
        )
        self.swarm_hub.update_colony_resource_state(
            "memory", ResourceState.ABUNDANT, 0.1, 0.1
        )
        self.swarm_hub.update_colony_resource_state(
            "creativity", ResourceState.CRITICAL, 0.9, 0.9
        )

        winner = self.scheduler.schedule_task({"type": "test_task"})
        self.assertNotEqual(winner, "creativity")

    def test_schedule_based_on_memory_load(self):
        self.swarm_hub.update_colony_resource_state(
            "reasoning", ResourceState.STABLE, 0.8, 0.5
        )
        self.swarm_hub.update_colony_resource_state(
            "memory", ResourceState.STABLE, 0.2, 0.5
        )
        self.swarm_hub.update_colony_resource_state(
            "creativity", ResourceState.STABLE, 0.5, 0.5
        )

        winner = self.scheduler.schedule_task({"type": "test_task"})
        self.assertEqual(winner, "memory")

    def test_schedule_based_on_tag_density(self):
        self.swarm_hub.update_colony_resource_state(
            "reasoning", ResourceState.STABLE, 0.5, 0.8
        )
        self.swarm_hub.update_colony_resource_state(
            "memory", ResourceState.STABLE, 0.5, 0.2
        )
        self.swarm_hub.update_colony_resource_state(
            "creativity", ResourceState.STABLE, 0.5, 0.5
        )

        winner = self.scheduler.schedule_task({"type": "test_task"})
        self.assertEqual(winner, "memory")


if __name__ == "__main__":
    unittest.main()
