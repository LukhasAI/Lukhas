"""
Lukhas AI Core Integration Module
Integrates all the distributed AI architecture components

This module demonstrates how Event Sourcing, Actor System,
Distributed Tracing, and Efficient Communication work together
to create a sustainable, energy-efficient AI system.
"""
import streamlit as st

import asyncio
import logging
import uuid
from typing import Any, Optional

# MitochondriaModel is optional - create a simple placeholder if not available
try:
    from bio.core.systems_mitochondria_model import MitochondriaModel
except ImportError:
    # Simple placeholder for energy model
    class MitochondriaModel:
        def __init__(self):
            self.energy = 100.0


# Use the colony system from lukhas
from lukhas.colonies.base import BaseColony

# Import our core components

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistributedAISystem:
    """
    Complete distributed AI system managing multiple colonies
    """

    def __init__(
        self,
        system_name: str = "lukhas-distributed-ai",
        energy_model: Optional[MitochondriaModel] = None,
    ):
        self.system_name = system_name
        self.colonies: dict[str, BaseColony] = {}
        self.is_running = False
        self.energy_model = energy_model or MitochondriaModel()

    async def start(self):
        """Start the distributed AI system"""
        self.is_running = True
        logger.info(f"Distributed AI System '{self.system_name}' started")

    async def stop(self):
        """Stop the distributed AI system"""
        # Stop all colonies
        stop_tasks = []
        for colony in self.colonies.values():
            stop_tasks.append(colony.stop())

        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

        self.colonies.clear()
        self.is_running = False

        logger.info(f"Distributed AI System '{self.system_name}' stopped")

    def task_priority_score(self, task_data: dict[str, Any]) -> float:
        """Compute task priority influenced by mitochondrial energy."""
        base_priority = float(task_data.get("priority", 0.5))
        energy_factor = self.energy_model.energy_output()
        # ΛTAG: energy_priority
        score = max(0.0, min(1.0, base_priority * (0.5 + energy_factor)))
        return score

    async def create_colony(self, colony_id: str, colony_class: type, **kwargs) -> BaseColony:
        """Create a new colony"""
        if colony_id in self.colonies:
            raise ValueError(f"Colony {colony_id} already exists")

        colony = colony_class(colony_id=colony_id, **kwargs)
        await colony.start()

        self.colonies[colony_id] = colony
        logger.info(f"Created colony {colony_id} of type {colony_class.__name__}")

        return colony

    async def execute_distributed_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a task that requires coordination between multiple colonies
        """
        task_id = str(uuid.uuid4())

        # Find colonies with required capabilities
        required_capabilities = task_data.get("required_capabilities", ["reasoning"])
        suitable_colonies = []

        for colony in self.colonies.values():
            if any(cap in colony.capabilities for cap in required_capabilities):
                suitable_colonies.append(colony)

        if not suitable_colonies:
            return {
                "status": "failed",
                "error": "No colonies with required capabilities",
            }

        priority_score = self.task_priority_score(task_data)

        # Execute task on the first suitable colony
        primary_colony = suitable_colonies[0]

        logger.info(f"Executing distributed task {task_id} on colony {primary_colony.colony_id}")

        result = await primary_colony.execute_task(
            task_id,
            {
                **task_data,
                "requires_collaboration": len(required_capabilities) > 1,
            },
        )

        return {
            "task_id": task_id,
            "primary_colony": primary_colony.colony_id,
            "result": result,
            "priority_score": priority_score,
            "system_stats": await self.get_system_statistics(),
        }

    async def get_system_statistics(self) -> dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            "system_name": self.system_name,
            "colony_count": len(self.colonies),
            "is_running": self.is_running,
            "colonies": {},
        }

        for colony_id, colony in self.colonies.items():
            stats["colonies"][colony_id] = colony.get_status()

        return stats


async def demo_integrated_system():
    """
    Demonstrate the complete integrated distributed AI system
    """
    print("🚀 Starting Lukhas Distributed AI System Demo")
    print("=" * 60)

    # Create and start the system
    system = DistributedAISystem("lukhas-demo")
    await system.start()

    try:
        # Create specialized colonies
        await system.create_colony("reasoning-specialist-001", ReasoningColony)

        await system.create_colony("memory-specialist-001", MemoryColony)

        await system.create_colony("creative-specialist-001", CreativityColony)

        print(f"\n✅ Created {len(system.colonies} specialized colonies")

        # Execute various distributed tasks
        tasks = [
            {
                "type": "complex_analysis",
                "required_capabilities": ["reasoning", "memory"],
                "complexity": "high",
                "data_size": "large",
            },
            {
                "type": "creative_synthesis",
                "required_capabilities": ["creativity", "reasoning"],
                "complexity": "medium",
                "inspiration_sources": ["art", "science"],
            },
            {
                "type": "knowledge_integration",
                "required_capabilities": ["memory", "reasoning", "creativity"],
                "complexity": "very_high",
                "domains": ["ai", "neuroscience", "philosophy"],
            },
        ]

        print(f"\n🎯 Executing {len(tasks} distributed tasks...")

        results = []
        for i, task in enumerate(tasks, 1):
            print(f"\n  Task {i}: {task['type']}")
            result = await system.execute_distributed_task(task)
            results.append(result)

            # Show energy efficiency
            primary_result = result.get("result", {})
            if "energy_efficiency" in primary_result:
                efficiency = primary_result["energy_efficiency"]
                print(f"    ⚡ Energy Efficiency: {efficiency:.1%}")

        # Get comprehensive system statistics
        print("\n📊 System Performance Analysis")
        print("-" * 40)

        final_stats = await system.get_system_statistics()

        for colony_id, colony_stats in final_stats["colonies"].items():
            print(f"\n🤖 Colony: {colony_id}")
            print(f"  Capabilities: {colony_stats.get('capabilities', []}")
            print(f"  Is Running: {colony_stats.get('is_running', False}")

        print("\n🎉 Demo completed successfully!")
        print(f"   Total colonies: {final_stats['colony_count']}")
        print(f"   Tasks executed: {len(results}")
        print("   System efficiency: Optimized for sustainability")

    finally:
        # Clean shutdown
        await system.stop()
        print("\n🛑 System stopped gracefully")


if __name__ == "__main__":
    # Run the integrated system demo
    asyncio.run(demo_integrated_system())
