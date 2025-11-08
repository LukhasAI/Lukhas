#!/usr/bin/env python3
"""Test Redis queue implementation"""
import asyncio
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.queue.redis_queue import RedisTaskQueue, Task, TaskPriority, TaskType


async def test_queue():
    """Test Redis queue operations"""
    print("🧪 Testing LUKHAS Redis Task Queue")
    print("=" * 70)

    async with RedisTaskQueue() as queue:
        # Enqueue tasks with different priorities
        print("\n1. Enqueuing tasks with different priorities...")
        tasks = [
            Task(
                task_id=str(uuid.uuid4()),
                task_type=TaskType.ARCHITECTURAL_VIOLATION,
                priority=TaskPriority.CRITICAL,
                agent="jules",
                prompt="Fix Trinity Framework violation in consciousness module"
            ),
            Task(
                task_id=str(uuid.uuid4()),
                task_type=TaskType.TODO_COMMENT,
                priority=TaskPriority.MEDIUM,
                agent="codex",
                prompt="Fix TODO in main.py"
            ),
            Task(
                task_id=str(uuid.uuid4()),
                task_type=TaskType.BUG_FIX,
                priority=TaskPriority.HIGH,
                agent="jules",
                prompt="Fix failing test in test_orchestration.py"
            ),
        ]

        for task in tasks:
            await queue.enqueue(task)
            print(f"  ✅ Enqueued: {task.task_id[:8]}... (priority={task.priority.name})")

        # Check queue size
        size = await queue.queue_size()
        print(f"\n2. Queue size: {size} tasks")

        # Peek at queue
        print("\n3. Peeking at queue (should be ordered by priority):")
        peek_tasks = await queue.peek()
        for t in peek_tasks:
            print(f"  📋 {t['task_id'][:8]}... - {t['priority_score']} ({TaskPriority(int(t['priority_score'])).name})")

        # Dequeue (should get CRITICAL task first)
        print("\n4. Dequeuing tasks (should be CRITICAL → HIGH → MEDIUM):")
        task1 = await queue.dequeue(timeout=5)
        if task1:
            print(f"  ✅ Dequeued: {task1.task_id[:8]}... (priority={task1.priority.name}, agent={task1.agent})")
            assert task1.priority == TaskPriority.CRITICAL, "First task should be CRITICAL"
        else:
            print("  ❌ Failed to dequeue task 1")
            return False

        task2 = await queue.dequeue(timeout=5)
        if task2:
            print(f"  ✅ Dequeued: {task2.task_id[:8]}... (priority={task2.priority.name}, agent={task2.agent})")
            assert task2.priority == TaskPriority.HIGH, "Second task should be HIGH"
        else:
            print("  ❌ Failed to dequeue task 2")
            return False

        task3 = await queue.dequeue(timeout=5)
        if task3:
            print(f"  ✅ Dequeued: {task3.task_id[:8]}... (priority={task3.priority.name}, agent={task3.agent})")
            assert task3.priority == TaskPriority.MEDIUM, "Third task should be MEDIUM"
        else:
            print("  ❌ Failed to dequeue task 3")
            return False

        # Verify queue is empty
        size_after = await queue.queue_size()
        print(f"\n5. Queue size after dequeue: {size_after} tasks")
        assert size_after == 0, "Queue should be empty"

    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_queue())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
