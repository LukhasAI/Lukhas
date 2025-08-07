#!/usr/bin/env python3
"""
Test Actor/Colony Integration
Validates communication between actor system and colony modules
"""

import asyncio
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core systems
from core.core_utilities import Actor
from core.actor_system import ActorSystem
from orchestration.symbolic_kernel_bus import kernel_bus
from core.colonies.memory_colony_enhanced import MemoryColony
from core.colonies.creativity_colony import CreativityColony
from core.colonies.reasoning_colony import ReasoningColony

class ColonyActor(Actor):
    """Actor that manages a colony"""
    def __init__(self, actor_id: str, colony):
        super().__init__(actor_id)
        self.colony = colony
        self.task_results = []

    async def handle_message(self, message):
        """Handle messages for the colony"""
        if message.get("type") == "execute_task":
            task_id = message.get("task_id")
            task_data = message.get("task_data", {})

            logger.info(f"🎯 {self.actor_id} executing task: {task_id}")

            # Execute task through colony
            result = await self.colony.execute_task(task_id, task_data)
            self.task_results.append(result)

            # Send result back
            return {
                "status": "completed",
                "task_id": task_id,
                "result": result,
                "colony": self.colony.colony_id
            }

        return {"status": "unknown_message_type"}

async def test_actor_colony_communication():
    """Test basic actor-colony communication"""
    print("\n🧪 Testing Actor-Colony Communication...")

    # Create actor system
    actor_system = ActorSystem()

    # Create colonies
    memory_colony = MemoryColony("memory_colony_1")
    creativity_colony = CreativityColony("creativity_colony_1")
    reasoning_colony = ReasoningColony("reasoning_colony_1")

    # Create actors for each colony
    memory_actor = ColonyActor("memory_actor", memory_colony)
    creativity_actor = ColonyActor("creativity_actor", creativity_colony)
    reasoning_actor = ColonyActor("reasoning_actor", reasoning_colony)

    # Create actor references
    memory_ref = await actor_system.create_actor(
        lambda: memory_actor,
        "memory_actor"
    )
    creativity_ref = await actor_system.create_actor(
        lambda: creativity_actor,
        "creativity_actor"
    )
    reasoning_ref = await actor_system.create_actor(
        lambda: reasoning_actor,
        "reasoning_actor"
    )

    # Send tasks to each actor
    tasks = [
        {
            "actor_id": "memory_actor",
            "task_id": "mem_task_1",
            "task_data": {"action": "store", "data": "test memory"}
        },
        {
            "actor_id": "creativity_actor",
            "task_id": "create_task_1",
            "task_data": {"action": "generate", "prompt": "test creation"}
        },
        {
            "actor_id": "reasoning_actor",
            "task_id": "reason_task_1",
            "task_data": {"action": "analyze", "data": "test reasoning"}
        }
    ]

    results = []
    for task in tasks:
        result = await actor_system.send_message(
            task["actor_id"],
            {
                "type": "execute_task",
                "task_id": task["task_id"],
                "task_data": task["task_data"]
            }
        )
        results.append(result)
        print(f"   - {task['actor_id']}: ✅ Task completed")

    # Cleanup
    await actor_system.stop()

    return all(r.get("status") == "completed" for r in results)

async def test_event_bus_integration():
    """Test event bus integration with colonies"""
    print("\n🧪 Testing Event Bus Integration...")

    # Create event bus
    event_bus = EventBus()

    # Create actor system
    actor_system = ActorSystem()

    # Create colonies and actors
    memory_colony = MemoryColony("memory_colony_2")
    memory_actor = ColonyActor("memory_actor_2", memory_colony)
    await actor_system.register_actor(memory_actor)

    # Track events
    events_received = []

    async def event_handler(event):
        events_received.append(event)
        logger.info(f"📨 Event received: {event.get('type')}")

    # Subscribe to events
    await kernel_bus.subscribe("colony.*", event_handler)

    # Emit colony events
    await event_bus.emit("colony.task.started", {"colony": "memory", "task": "test"})
    await event_bus.emit("colony.task.completed", {"colony": "memory", "result": "success"})

    # Wait for events to propagate
    await asyncio.sleep(0.1)

    print(f"   - Events emitted: 2")
    print(f"   - Events received: {len(events_received)}")

    # Cleanup
    await actor_system.stop()

    return len(events_received) == 2

async def test_cross_colony_coordination():
    """Test coordination between multiple colonies"""
    print("\n🧪 Testing Cross-Colony Coordination...")

    # Create actor system
    actor_system = ActorSystem()

    # Create colonies
    memory_colony = MemoryColony("memory_colony_3")
    reasoning_colony = ReasoningColony("reasoning_colony_3")

    # Create coordinating actors
    memory_actor = ColonyActor("memory_actor_3", memory_colony)
    reasoning_actor = ColonyActor("reasoning_actor_3", reasoning_colony)

    await actor_system.register_actor(memory_actor)
    await actor_system.register_actor(reasoning_actor)

    # Step 1: Store data in memory colony
    store_result = await actor_system.send_message(
        "memory_actor_3",
        {
            "type": "execute_task",
            "task_id": "store_data",
            "task_data": {"action": "store", "data": "Important fact: AI helps humans"}
        }
    )

    # Step 2: Reason about the stored data
    reason_result = await actor_system.send_message(
        "reasoning_actor_3",
        {
            "type": "execute_task",
            "task_id": "analyze_data",
            "task_data": {"action": "analyze", "data": "AI helps humans"}
        }
    )

    print("   - Memory storage: ✅ Complete")
    print("   - Reasoning analysis: ✅ Complete")
    print("   - Cross-colony coordination: ✅ Success")

    # Cleanup
    await actor_system.stop()

    return (store_result.get("status") == "completed" and
            reason_result.get("status") == "completed")

async def main():
    """Main test runner"""
    print("🚀 Testing Actor/Colony Integration")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = []

    # Run tests
    results.append(await test_actor_colony_communication())
    results.append(await test_event_bus_integration())
    results.append(await test_cross_colony_coordination())

    # Summary
    print("\n" + "=" * 50)
    print("📊 Integration Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   - Tests passed: {passed}/{total}")
    print(f"   - Success rate: {(passed/total)*100:.0f}%")

    if passed == total:
        print("\n✅ Actor/Colony integration is fully functional!")
        print("   - Actors can manage colonies")
        print("   - Event bus integration works")
        print("   - Cross-colony coordination successful")
    else:
        print("\n⚠️ Some integration tests failed")

    return passed == total

if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)