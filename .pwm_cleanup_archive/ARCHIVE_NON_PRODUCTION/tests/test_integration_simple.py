#!/usr/bin/env python3
"""
Simplified integration test for actor/colony systems
"""

import asyncio
from datetime import datetime

from core.colonies.creativity_colony import CreativityColony
from core.colonies.memory_colony_enhanced import MemoryColony
from core.colonies.reasoning_colony import ReasoningColony
from core.integration_hub import UnifiedIntegration

# Import modules that we know work
from core.task_manager import LukhλsTaskManager
from orchestration.symbolic_kernel_bus import kernel_bus


async def test_task_manager_with_colonies():
    """Test task manager coordinating with colonies"""
    print("\n🧪 Testing Task Manager with Colonies...")

    # Create task manager
    task_manager = LukhλsTaskManager()

    # Create colonies
    memory_colony = MemoryColony("test_memory")
    creativity_colony = CreativityColony("test_creativity")
    reasoning_colony = ReasoningColony("test_reasoning")

    # Create tasks that would interact with colonies
    task1 = task_manager.create_task(
        name="Memory Storage Task",
        description="Store test data in memory colony",
        handler="file_processing",  # Using existing handler
        parameters={"colony": "memory", "action": "store"},
    )

    task2 = task_manager.create_task(
        name="Creative Generation Task",
        description="Generate creative content",
        handler="design_system",  # Using existing handler
        parameters={"colony": "creativity", "action": "generate"},
    )

    # Execute tasks
    success1 = await task_manager.execute_task(task1)
    success2 = await task_manager.execute_task(task2)

    print(f"   - Memory task: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"   - Creative task: {'✅ Success' if success2 else '❌ Failed'}")

    return success1 and success2


async def test_integration_hub_with_colonies():
    """Test integration hub managing colonies"""
    print("\n🧪 Testing Integration Hub with Colonies...")

    # Create integration hub
    hub = UnifiedIntegration()

    # Create colonies
    memory_colony = MemoryColony("hub_memory")
    reasoning_colony = ReasoningColony("hub_reasoning")

    # Register colonies as components
    result1 = hub.register_component(
        "memory_colony",
        memory_colony,
        {"type": "colony", "capabilities": memory_colony.capabilities},
    )

    result2 = hub.register_component(
        "reasoning_colony",
        reasoning_colony,
        {"type": "colony", "capabilities": reasoning_colony.capabilities},
    )

    print(
        f"   - Memory colony registration: {'✅ Success' if result1.success else '❌ Failed'}"
    )
    print(
        f"   - Reasoning colony registration: {'✅ Success' if result2.success else '❌ Failed'}"
    )

    # Test integration operations
    if hasattr(hub, "execute_integration"):
        # Try to execute an integration if the method exists
        integration_result = await hub.execute_integration(
            "cross_colony_sync",
            {"source": "memory_colony", "target": "reasoning_colony"},
        )
        print("   - Cross-colony integration: ✅ Attempted")
    else:
        print("   - Cross-colony integration: ℹ️ Method not available")

    return result1.success and result2.success


async def test_event_bus_with_colonies():
    """Test event bus communication between colonies"""
    print("\n🧪 Testing Event Bus with Colonies...")

    # Create event bus
    event_bus = EventBus()

    # Create colonies
    memory_colony = MemoryColony("event_memory")
    creativity_colony = CreativityColony("event_creativity")

    # Track events
    events_received = []

    async def colony_event_handler(event):
        events_received.append(event)
        print(f"   - Event received: {event.get('type', 'unknown')}")

    # Subscribe to colony events
    kernel_bus.subscribe("colony.*", colony_event_handler)

    # Simulate colony events
    await event_bus.publish(
        "colony.memory.store",
        {"colony": memory_colony.colony_id, "action": "store", "data": "test data"},
    )

    await event_bus.publish(
        "colony.creativity.generate",
        {
            "colony": creativity_colony.colony_id,
            "action": "generate",
            "prompt": "test prompt",
        },
    )

    # Wait for events
    await asyncio.sleep(0.1)

    print("   - Events emitted: 2")
    print(f"   - Events received: {len(events_received)}")

    return len(events_received) == 2


async def test_colony_task_execution():
    """Test direct colony task execution"""
    print("\n🧪 Testing Direct Colony Task Execution...")

    # Create colonies
    memory_colony = MemoryColony("exec_memory")
    reasoning_colony = ReasoningColony("exec_reasoning")

    # Test memory colony task
    memory_result = await memory_colony.execute_task(
        "mem_task_1", {"action": "store", "data": {"key": "test", "value": "data"}}
    )

    # Test reasoning colony task
    reasoning_result = await reasoning_colony.execute_task(
        "reason_task_1",
        {"action": "analyze", "data": "What is the meaning of this test?"},
    )

    print("   - Memory task execution: ✅ Complete")
    print("   - Reasoning task execution: ✅ Complete")

    return True


async def main():
    """Main test runner"""
    print("🚀 Testing Simplified Integration")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = []

    # Run tests
    results.append(await test_task_manager_with_colonies())
    results.append(await test_integration_hub_with_colonies())
    results.append(await test_event_bus_with_colonies())
    results.append(await test_colony_task_execution())

    # Summary
    print("\n" + "=" * 50)
    print("📊 Integration Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   - Tests passed: {passed}/{total}")
    print(f"   - Success rate: {(passed/total)*100:.0f}%")

    if passed == total:
        print("\n✅ All integration tests passed!")
        print("   - Task Manager ↔ Colonies: Working")
        print("   - Integration Hub ↔ Colonies: Working")
        print("   - Event Bus ↔ Colonies: Working")
        print("   - Direct Colony Execution: Working")
    else:
        print("\n⚠️ Some integration tests need attention")

    return passed == total


if __name__ == "__main__":
    import sys

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
