"""
Unit tests for RedisTaskQueue.
"""
import asyncio
import uuid
from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest
from bridge.queue.redis_queue import RedisTaskQueue, Task, TaskPriority, TaskType


@pytest.fixture
def mock_redis_from_url():
    """Fixture to patch redis.asyncio.from_url to return a fakeredis instance."""
    fake_redis_instance = fakeredis.aioredis.FakeRedis(decode_responses=True)
    with patch('redis.asyncio.from_url', return_value=fake_redis_instance) as mock_from_url:
        yield mock_from_url, fake_redis_instance

@pytest.fixture
async def task_queue(mock_redis_from_url):
    """Fixture to get an instance of RedisTaskQueue using the async context manager."""
    queue = RedisTaskQueue()
    async with queue as q:
        yield q
        # Clean up the fake redis db after the test
        if q.redis:
            await q.redis.flushall()

def create_test_task(priority: TaskPriority, task_id: str = None) -> Task:
    """Helper function to create a test task."""
    if task_id is None:
        task_id = str(uuid.uuid4())
    return Task(
        task_id=task_id,
        task_type=TaskType.TEST_CREATION,
        priority=priority,
        agent="test_agent",
        prompt="Test prompt",
    )

from datetime import datetime

from pydantic import ValidationError


class TestTaskModel:
    """Tests for the Task Pydantic model."""

    def test_task_creation_valid(self):
        """Test that a Task object can be created with valid data."""
        task_data = {
            "task_id": "test-123",
            "task_type": TaskType.BUG_FIX,
            "priority": TaskPriority.HIGH,
            "agent": "jules",
            "prompt": "Fix the bug.",
        }
        task = Task(**task_data)
        assert task.task_id == "test-123"
        assert task.priority == TaskPriority.HIGH
        assert isinstance(task.created_at, datetime)
        assert task.context == {}

    def test_task_creation_missing_required_field(self):
        """Test that creating a task with a missing required field raises a ValidationError."""
        with pytest.raises(ValidationError):
            Task(
                task_type=TaskType.BUG_FIX,
                priority=TaskPriority.HIGH,
                agent="jules",
                prompt="Fix the bug.",
            )

    def test_task_creation_default_values(self):
        """Test that default values are correctly assigned."""
        task = Task(
            task_id="test-123",
            task_type=TaskType.BUG_FIX,
            priority=TaskPriority.HIGH,
            agent="jules",
            prompt="Fix the bug.",
        )
        assert isinstance(task.created_at, datetime)
        assert task.context == {}
        assert task.file_paths == []
        assert task.pr_number is None
        assert task.callback_url is None

    def test_task_invalid_priority(self):
        """Test that an invalid priority value raises a ValidationError."""
        with pytest.raises(ValidationError):
            Task(
                task_id="test-123",
                task_type=TaskType.BUG_FIX,
                priority=99,  # Invalid priority
                agent="jules",
                prompt="Fix the bug.",
            )

@pytest.mark.asyncio
class TestRedisTaskQueue:
    """Test suite for the RedisTaskQueue."""

    async def test_context_manager(self, mock_redis_from_url):
        """Test the async context manager initialization and cleanup."""
        mock_from_url, fake_redis = mock_redis_from_url

        # Patch the aclose method on the fakeredis instance with an AsyncMock
        fake_redis.aclose = AsyncMock()

        queue = RedisTaskQueue()
        async with queue as q:
            assert q.redis is not None
            mock_from_url.assert_called_once()

        # The fakeredis object does not have a 'closed' attribute,
        # so we just ensure the context manager exits without error.
        pass

    async def test_aexit_with_exception(self, mock_redis_from_url):
        """Test that __aexit__ closes the connection even if an exception occurs."""
        mock_from_url, fake_redis = mock_redis_from_url
        fake_redis.aclose = AsyncMock()
        queue = RedisTaskQueue()
        with pytest.raises(ValueError, match="Test exception"):
            async with queue as q:
                raise ValueError("Test exception")
        fake_redis.aclose.assert_awaited_once()

    async def test_enqueue_without_context_manager_raises_error(self):
        """Test that calling enqueue without the context manager raises a RuntimeError."""
        queue = RedisTaskQueue()
        task = create_test_task(TaskPriority.MEDIUM)
        with pytest.raises(RuntimeError, match="Redis connection not initialized"):
            await queue.enqueue(task)

    async def test_dequeue_without_context_manager_raises_error(self):
        """Test that calling dequeue without the context manager raises a RuntimeError."""
        queue = RedisTaskQueue()
        with pytest.raises(RuntimeError, match="Redis connection not initialized"):
            await queue.dequeue()

    async def test_dequeue_task_data_not_found(self, task_queue):
        """Test that dequeue returns None if the task data is not found in Redis."""
        task = create_test_task(TaskPriority.CRITICAL)
        # Manually add to sorted set without adding the task data
        await task_queue.redis.zadd(task_queue.QUEUE_KEY, {task.task_id: task.priority.value})

        dequeued_task = await task_queue.dequeue(timeout=1)
        assert dequeued_task is None
        assert await task_queue.queue_size() == 0

    async def test_peek_empty_queue(self, task_queue):
        """Test peeking at an empty queue returns an empty list."""
        peeked_tasks = await task_queue.peek(count=10)
        assert peeked_tasks == []

    async def test_queue_size_without_context_manager(self):
        """Test that queue_size returns 0 if the connection is not initialized."""
        queue = RedisTaskQueue()
        assert await queue.queue_size() == 0

    async def test_peek_without_context_manager(self):
        """Test that peek returns an empty list if the connection is not initialized."""
        queue = RedisTaskQueue()
        assert await queue.peek() == []

    async def test_peek_with_missing_task_data(self, task_queue):
        """Test that peek handles missing task data gracefully."""
        # Manually add a task ID to the queue without corresponding data
        await task_queue.redis.zadd(task_queue.QUEUE_KEY, {"missing-task": 1.0})
        peeked_tasks = await task_queue.peek()
        assert peeked_tasks == []

    async def test_enqueue_and_queue_size(self, task_queue):
        """Test that a task can be enqueued and the queue size is correct."""
        assert await task_queue.queue_size() == 0
        task = create_test_task(TaskPriority.MEDIUM)
        await task_queue.enqueue(task)
        assert await task_queue.queue_size() == 1

    async def test_dequeue_from_empty_queue(self, task_queue):
        """Test that dequeuing from an empty queue with a timeout returns None."""
        task = await task_queue.dequeue(timeout=1)
        assert task is None

    async def test_enqueue_and_dequeue_single_task(self, task_queue):
        """Test that a single task can be enqueued and dequeued."""
        task = create_test_task(TaskPriority.MEDIUM)
        await task_queue.enqueue(task)
        assert await task_queue.queue_size() == 1

        dequeued_task = await task_queue.dequeue(timeout=1)
        assert dequeued_task is not None
        assert dequeued_task.task_id == task.task_id
        assert await task_queue.queue_size() == 0

    @pytest.mark.parametrize(
        "priorities, expected_order",
        [
            ([TaskPriority.LOW, TaskPriority.HIGH, TaskPriority.CRITICAL, TaskPriority.MEDIUM],
             [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]),
            ([TaskPriority.MEDIUM, TaskPriority.MEDIUM, TaskPriority.LOW],
             [TaskPriority.MEDIUM, TaskPriority.MEDIUM, TaskPriority.LOW]),
        ]
    )
    async def test_priority_order(self, task_queue, priorities, expected_order):
        """Test that tasks are dequeued in the correct priority order."""
        for i, priority in enumerate(priorities):
            task = create_test_task(priority, task_id=f"task-{i}")
            await task_queue.enqueue(task)

        dequeued_priorities = []
        for _ in range(len(priorities)):
            task = await task_queue.dequeue(timeout=1)
            dequeued_priorities.append(task.priority)

        assert dequeued_priorities == expected_order

    async def test_concurrency(self, task_queue):
        """Test concurrent enqueue and dequeue operations."""
        async def worker(queue, results):
            task = await queue.dequeue(timeout=5)
            if task:
                results.append(task)

        num_tasks = 10
        tasks = [create_test_task(TaskPriority.MEDIUM) for _ in range(num_tasks)]

        # Enqueue all tasks
        for task in tasks:
            await task_queue.enqueue(task)

        # Concurrently dequeue tasks
        results = []
        worker_tasks = [asyncio.create_task(worker(task_queue, results)) for _ in range(num_tasks)]
        await asyncio.gather(*worker_tasks)

        assert len(results) == num_tasks
        assert {t.task_id for t in results} == {t.task_id for t in tasks}
        assert await task_queue.queue_size() == 0

    async def test_peek(self, task_queue):
        """Test peeking at tasks without removing them."""
        tasks = [
            create_test_task(TaskPriority.CRITICAL, "task-1"),
            create_test_task(TaskPriority.HIGH, "task-2"),
            create_test_task(TaskPriority.LOW, "task-3"),
        ]
        for task in tasks:
            await task_queue.enqueue(task)

        peeked_tasks = await task_queue.peek(count=2)
        assert len(peeked_tasks) == 2
        assert peeked_tasks[0]['task_id'] == 'task-1'
        assert peeked_tasks[1]['task_id'] == 'task-2'

        assert await task_queue.queue_size() == 3
