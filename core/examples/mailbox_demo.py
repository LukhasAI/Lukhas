"""
Demonstration of Enhanced Mailbox Features
Shows priority queues, back-pressure, persistence, and sequential guarantees
"""

import asyncio
import json

# Add parent directory to path
import sys
from pathlib import Path

from core.actor_system import get_global_actor_system
from core.mailbox import BackPressureStrategy, MailboxActor, MailboxType

sys.path.append(str(Path(__file__).parent.parent.parent))


class SequentialCounterActor(MailboxActor):
    """
    Demonstrates sequential processing guarantee
    Counter must always increment by 1 without race conditions
    """

    def __init__(self, actor_id: str):
        super().__init__(
            actor_id,
            mailbox_type=MailboxType.BOUNDED,
            mailbox_config={"max_size": 100},
        )
        self.counter = 0
        self.register_handler("increment", self._handle_increment)
        self.register_handler("get_count", self._handle_get_count)

    async def _handle_increment(self, message):
        """Increment counter - sequential guarantee ensures no race conditions"""
        self.counter += 1
        # Simulate some processing time
        await asyncio.sleep(0.01)
        return {"new_count": self.counter}

    async def _handle_get_count(self, message):
        """Get current count"""
        return {"count": self.counter}


class PriorityTaskActor(MailboxActor):
    """
    Demonstrates priority mailbox with different task priorities
    """

    def __init__(self, actor_id: str):
        super().__init__(
            actor_id,
            mailbox_type=MailboxType.PRIORITY,
            mailbox_config={"max_size": 50, "starvation_prevention": True},
        )
        self.tasks_processed = {
            "SYSTEM": 0,
            "HIGH": 0,
            "NORMAL": 0,
            "LOW": 0,
            "BULK": 0,
        }
        self.register_handler("process_task", self._handle_task)
        self.register_handler("get_stats", self._handle_get_stats)

    async def _handle_task(self, message):
        """Process task based on priority"""
        priority = message.payload.get("priority", "NORMAL")
        task_name = message.payload.get("task_name", "unknown")

        # Track processing
        self.tasks_processed[priority] = self.tasks_processed.get(priority, 0) + 1

        # Simulate work
        await asyncio.sleep(0.05)

        print(f"Processed {priority} priority task: {task_name}")
        return {"processed": task_name, "priority": priority}

    async def _handle_get_stats(self, message):
        """Get processing statistics"""
        return {
            "tasks_processed": self.tasks_processed,
            "mailbox_stats": self.get_mailbox_stats(),
        }


class BackPressureActor(MailboxActor):
    """
    Demonstrates back-pressure handling strategies
    """

    def __init__(self, actor_id: str, strategy: BackPressureStrategy):
        super().__init__(
            actor_id,
            mailbox_type=MailboxType.BOUNDED,
            mailbox_config={
                "max_size": 10,  # Small mailbox to trigger back-pressure
                "back_pressure_strategy": strategy,
            },
        )
        self.strategy = strategy
        self.processed_messages = []
        self.register_handler("slow_process", self._handle_slow_process)
        self.register_handler("get_processed", self._handle_get_processed)

    async def _handle_slow_process(self, message):
        """Simulate slow processing to trigger back-pressure"""
        msg_id = message.payload.get("id")
        await asyncio.sleep(0.1)  # Slow processing
        self.processed_messages.append(msg_id)
        return {"processed": msg_id}

    async def _handle_get_processed(self, message):
        """Get list of processed messages"""
        return {
            "processed": self.processed_messages,
            "strategy": self.strategy.value,
            "mailbox_stats": self.mailbox.get_stats(),
        }


class PersistentStateActor(MailboxActor):
    """
    Demonstrates persistent mailbox for crash recovery
    """

    def __init__(self, actor_id: str):
        super().__init__(
            actor_id,
            mailbox_type=MailboxType.PERSISTENT,
            mailbox_config={
                "max_size": 100,
                "persistence_path": f"/tmp/{actor_id}_mailbox.json",
                "persistence_interval": 2.0,
            },
        )
        self.state = {"processed": [], "crashed": False}
        self.register_handler("update_state", self._handle_update)
        self.register_handler("crash", self._handle_crash)
        self.register_handler("get_state", self._handle_get_state)

    async def pre_start(self):
        """Restore mailbox on startup"""
        if hasattr(self.mailbox, "restore_from_disk"):
            restored = await self.mailbox.restore_from_disk()
            if restored > 0:
                print(f"Restored {restored} messages from disk")
                self.state["crashed"] = True

    async def _handle_update(self, message):
        """Update persistent state"""
        update = message.payload.get("update")
        self.state["processed"].append(update)
        return {"state_size": len(self.state["processed"])}

    async def _handle_crash(self, message):
        """Simulate a crash"""
        print("Simulating crash - messages will be persisted")
        # In real scenario, process would exit
        # For demo, we just stop the actor
        self._running = False
        return {"crashed": True}

    async def _handle_get_state(self, message):
        """Get current state"""
        return {"state": self.state}


async def demonstrate_sequential_guarantee():
    """Show that sequential processing prevents race conditions"""
    print("\n=== Sequential Processing Guarantee ===")

    system = await get_global_actor_system()
    counter = await system.create_actor(SequentialCounterActor, "counter-001")

    # Send 100 increment messages concurrently
    tasks = []
    for _i in range(100):
        tasks.append(counter.tell("increment", {}))

    await asyncio.gather(*tasks)

    # Wait for processing
    await asyncio.sleep(2)

    # Check final count
    result = await counter.ask("get_count", {})
    print(f"Final count: {result['count']} (should be 100)")

    # Get stats
    actor = system.get_actor("counter-001")
    stats = actor.get_stats()
    print(f"Mailbox stats: {json.dumps(stats['mailbox_details'], indent=2)}")


async def demonstrate_priority_processing():
    """Show priority-based message processing"""
    print("\n=== Priority Message Processing ===")

    system = await get_global_actor_system()
    priority_actor = await system.create_actor(PriorityTaskActor, "priority-001")

    # Send messages with different priorities
    tasks = []

    # Low priority background tasks
    for i in range(5):
        tasks.append(
            priority_actor.tell(
                "process_task",
                {"task_name": f"background-{i}", "priority": "LOW"},
            )
        )

    # Normal priority tasks
    for i in range(3):
        tasks.append(
            priority_actor.tell(
                "process_task",
                {"task_name": f"normal-{i}", "priority": "NORMAL"},
            )
        )

    # High priority urgent task
    tasks.append(
        priority_actor.tell(
            "process_task", {"task_name": "urgent-request", "priority": "HIGH"}
        )
    )

    # System critical task
    tasks.append(
        priority_actor.tell(
            "process_task",
            {"task_name": "system-health-check", "priority": "SYSTEM"},
        )
    )

    await asyncio.gather(*tasks)

    # Wait for processing
    await asyncio.sleep(2)

    # Get statistics
    stats = await priority_actor.ask("get_stats", {})
    print(f"Processing stats: {json.dumps(stats, indent=2)}")


async def demonstrate_back_pressure():
    """Show different back-pressure strategies"""
    print("\n=== Back-Pressure Handling ===")

    system = await get_global_actor_system()

    # Test DROP_NEWEST strategy
    drop_newest = await system.create_actor(
        BackPressureActor,
        "drop-newest-001",
        strategy=BackPressureStrategy.DROP_NEWEST,
    )

    # Send more messages than mailbox can hold
    print("\nTesting DROP_NEWEST strategy...")
    for i in range(20):
        success = await drop_newest.tell("slow_process", {"id": f"msg-{i}"})
        if not success:
            print(f"Message {i} was dropped (mailbox full)")

    await asyncio.sleep(3)

    result = await drop_newest.ask("get_processed", {})
    print(f"Processed with DROP_NEWEST: {len(result['processed'])} messages")
    print(f"Mailbox stats: {result['mailbox_stats']}")


async def demonstrate_persistence():
    """Show persistent mailbox for crash recovery"""
    print("\n=== Persistent Mailbox ===")

    system = await get_global_actor_system()

    # Create actor with persistent mailbox
    persistent = await system.create_actor(PersistentStateActor, "persistent-001")

    # Send some messages
    for i in range(5):
        await persistent.tell("update_state", {"update": f"state-{i}"})

    # Wait for persistence
    await asyncio.sleep(3)

    # Simulate crash
    await persistent.tell("crash", {})
    await asyncio.sleep(1)

    # Recreate actor - it should restore messages
    print("\nRecreating actor after crash...")
    await system.stop_actor("persistent-001")

    recovered = await system.create_actor(PersistentStateActor, "persistent-001")

    # Check state
    state = await recovered.ask("get_state", {})
    print(f"Recovered state: {json.dumps(state, indent=2)}")


async def main():
    """Run all demonstrations"""
    print("Enhanced Mailbox System Demonstration")
    print("=====================================")

    # Initialize system
    system = await get_global_actor_system()

    try:
        # Run demonstrations
        await demonstrate_sequential_guarantee()
        await demonstrate_priority_processing()
        await demonstrate_back_pressure()
        await demonstrate_persistence()

    finally:
        # Cleanup
        await system.stop()
        print("\nDemo completed!")


if __name__ == "__main__":
    asyncio.run(main())
