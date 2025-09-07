"""
Swarm Resource Scheduler
Addresses Phase Δ, Step 2 (Resource Scheduling)

This module provides a SwarmResourceScheduler that dynamically assigns
tasks to colonies based on their resource state, memory load, and
symbolic tag density.
"""
import streamlit as st


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
    print(f"--> Best colony for memory task: {winner}")
    print(f"--> Best colony for creative task: {winner}")
