"""
Visual Swarm Map Generator
Addresses Phase Δ, Step 4

This module provides a way to generate a visual representation of the
Symbiotic Swarm using the Mermaid.js format.
"""
import random
import time

from lukhas.core.swarm import SwarmHub


class SwarmVisualizer:
    def __init__(self, swarm_hub: SwarmHub):
        self.swarm_hub = swarm_hub

    def generate_mermaid_graph(self, ethical_statuses=None):
        if ethical_statuses is None:
            ethical_statuses = {}
        graph_str = "graph TD;\n"

        # Add colonies as nodes
        for colony_id, info in self.swarm_hub.colonies.items():
            status = info["status"]
            ethical_status = ethical_statuses.get(colony_id, "unknown")

            style = ""
            if status == "unhealthy":
                style = "style " + colony_id + " fill:#f9f,stroke:#333,stroke-width:4px"
            elif ethical_status == "red":
                style = "style " + colony_id + " fill:#ff9999,stroke:#333,stroke-width:2px"
            elif ethical_status == "yellow":
                style = "style " + colony_id + " fill:#ffff99,stroke:#333,stroke-width:2px"
            elif ethical_status == "green":
                style = "style " + colony_id + " fill:#99ff99,stroke:#333,stroke-width:2px"

            graph_str += f"    {colony_id}[{colony_id} - {status} - {ethical_status}];\n"
            if style:
                graph_str += f"    {style};\n"

        # Add connections (simplified)
        # In a real system, you would have a more sophisticated way of tracking
        # connections
        colonies = list(self.swarm_hub.colonies.keys())
        for i in range(len(colonies) - 1):
            graph_str += f"    {colonies[i]} --> {colonies[i + 1]};\n"

        return graph_str


if __name__ == "__main__":
    swarm_hub = SwarmHub()
    swarm_hub.register_colony("ingestion", "symbolic:ingestion")
    swarm_hub.register_colony("feature_engineering", "symbolic:feature_engineering")
    swarm_hub.register_colony("inference", "symbolic:inference")

    visualizer = SwarmVisualizer(swarm_hub)

    while True:
        # Simulate changing ethical statuses
        ethical_statuses = {
            "ingestion": random.choice(["green", "yellow", "red"]),
            "feature_engineering": random.choice(["green", "yellow", "red"]),
            "inference": random.choice(["green", "yellow", "red"]),
        }

        mermaid_graph = visualizer.generate_mermaid_graph(ethical_statuses)

        # Clear the console and print the new graph
        print("\033[H\033[J")
        print("--- Live Swarm Map (updates every 5 seconds) ---")
        print(mermaid_graph)

        time.sleep(5)