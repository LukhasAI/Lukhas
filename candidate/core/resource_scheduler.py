"""
Swarm Resource Scheduler
Addresses Phase Δ, Step 2 (Resource Scheduling)

This module provides a SwarmResourceScheduler that dynamically assigns
tasks to colonies based on their resource state, memory load, and
symbolic tag density.
"""


class SwarmResourceScheduler:
    def __init__(self, swarm_hub: SwarmHub):
        self.swarm_hub = swarm_hub

    def schedule_task(self, task):
        """
        Schedules a task to the most appropriate colony.
        """
        best_colony = None
        best_score = -1

        for colony_id, info in self.swarm_hub.colonies.items():
            colony = info["colony"]
            if colony.resource_state == ResourceState.CRITICAL:
                continue

            score = self._calculate_score(colony)
            if score > best_score:
                best_score = score
                best_colony = colony_id

        print(f"Scheduler: Assigned task to colony {best_colony}")
        return best_colony

    def _calculate_score(self, colony):
        """
        Calculates a score for a colony based on its resource state,
        memory load, and symbolic tag density.
        """
        # Lower is better for these metrics
        resource_state_score = 1 - (colony.resource_state.value / 4.0)
        memory_load_score = 1 - colony.memory_load
        symbolic_density_score = 1 - colony.symbolic_tag_density

        # Simple weighted average
        score = (0.5 * resource_state_score) + (0.3 * memory_load_score) + (0.2 * symbolic_density_score)
        return score


if __name__ == "__main__":
    swarm_hub = SwarmHub()
    reasoning_colony = swarm_hub.register_colony("reasoning", "symbolic:reasoning")
    memory_colony = swarm_hub.register_colony("memory", "symbolic:memory")
    creativity_colony = swarm_hub.register_colony("creativity", "symbolic:creativity")

    swarm_hub.update_colony_resource_state("reasoning", ResourceState.STABLE, 0.5, 0.6)
    swarm_hub.update_colony_resource_state("memory", ResourceState.ABUNDANT, 0.1, 0.2)
    swarm_hub.update_colony_resource_state("creativity", ResourceState.STRAINED, 0.9, 0.8)

    scheduler = SwarmResourceScheduler(swarm_hub)

    print("\n--- Scheduling a memory-intensive task ---")
    winner = scheduler.schedule_task({"type": "memory_task"})
    print(f"--> Best colony for memory task: {winner}")

    print("\n--- Scheduling a creative task ---")
    creativity_colony.update_resource_state(ResourceState.ABUNDANT)
    winner = scheduler.schedule_task({"type": "creative_task"})
    print(f"--> Best colony for creative task: {winner}")
