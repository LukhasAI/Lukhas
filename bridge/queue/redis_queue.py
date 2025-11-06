"""
Redis-based Priority Task Queue for LUKHAS AI-Driven Pipeline
Uses Redis Sorted Sets (ZADD/BZPOPMIN) for atomic priority queueing.
"""
import asyncio
import json
import logging
from typing import Any, Optional
from datetime import datetime
from enum import IntEnum

import redis.asyncio as redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TaskPriority(IntEnum):
    """Task priority levels (lower score = higher priority)"""
    CRITICAL = 1    # Architectural violations, build failures
    HIGH = 2        # Bug fixes, failing tests
    MEDIUM = 3      # TODO tasks, refactoring
    LOW = 4         # Documentation, non-urgent


class TaskType(str):
    """Task types for routing"""
    ARCHITECTURAL_VIOLATION = "architectural_violation"
    TODO_COMMENT = "todo_comment"
    BUG_FIX = "bug_fix"
    TEST_CREATION = "test_creation"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"


class Task(BaseModel):
    """Task model for AI agent execution"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: TaskType = Field(..., description="Type of task")
    priority: TaskPriority = Field(..., description="Task priority")
    agent: str = Field(..., description="Target agent (jules/codex/gemini/ollama)")
    prompt: str = Field(..., description="Task prompt for agent")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    pr_number: Optional[int] = Field(None, description="Associated PR number")
    file_paths: list[str] = Field(default_factory=list, description="Related file paths")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    callback_url: Optional[str] = Field(None, description="Webhook callback URL")


class RedisTaskQueue:
    """
    Production-grade Redis task queue using Sorted Sets.

    Features:
    - Atomic priority-based dequeue (BZPOPMIN)
    - Non-blocking enqueue (ZADD)
    - Task persistence (Redis AOF)
    - Concurrent worker support
    """

    QUEUE_KEY = "lukhas:task_queue"
    TASK_DATA_PREFIX = "lukhas:task:"

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection"""
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.redis = await redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.redis:
            await self.redis.close()

    async def enqueue(self, task: Task) -> None:
        """
        Enqueue task with priority.

        Uses ZADD (atomic) to add task to sorted set with priority as score.
        Task data stored separately with TTL of 7 days.
        """
        if not self.redis:
            raise RuntimeError("Redis connection not initialized. Use 'async with' context manager.")

        # Store task data with 7-day TTL
        task_key = f"{self.TASK_DATA_PREFIX}{task.task_id}"
        await self.redis.setex(
            task_key,
            7 * 24 * 3600,  # 7 days
            task.json()
        )

        # Add to priority queue
        await self.redis.zadd(
            self.QUEUE_KEY,
            {task.task_id: task.priority.value}
        )

        logger.info(
            f"Enqueued task {task.task_id} "
            f"(priority={task.priority.name}, agent={task.agent})"
        )

    async def dequeue(self, timeout: int = 0) -> Optional[Task]:
        """
        Dequeue highest-priority task (blocking).

        Uses BZPOPMIN (atomic blocking pop) to get task with lowest score
        (highest priority). Blocks until task available if timeout=0.

        Args:
            timeout: Block timeout in seconds (0 = block forever)

        Returns:
            Task object or None if timeout
        """
        if not self.redis:
            raise RuntimeError("Redis connection not initialized.")

        # Blocking pop of lowest score (highest priority)
        result = await self.redis.bzpopmin(self.QUEUE_KEY, timeout=timeout)

        if not result:
            return None

        # Result format: (queue_key, task_id, score)
        _, task_id, _ = result

        # Retrieve task data
        task_key = f"{self.TASK_DATA_PREFIX}{task_id}"
        task_json = await self.redis.get(task_key)

        if not task_json:
            logger.error(f"Task data not found for {task_id}")
            return None

        # Delete task data after retrieval
        await self.redis.delete(task_key)

        task = Task.parse_raw(task_json)
        logger.info(f"Dequeued task {task_id} (agent={task.agent})")

        return task

    async def queue_size(self) -> int:
        """Get current queue size"""
        if not self.redis:
            return 0
        return await self.redis.zcard(self.QUEUE_KEY)

    async def peek(self, count: int = 10) -> list[dict]:
        """Peek at top N tasks without removing"""
        if not self.redis:
            return []

        # Get top N task IDs with scores
        tasks = await self.redis.zrange(
            self.QUEUE_KEY,
            0, count - 1,
            withscores=True
        )

        result = []
        for task_id, score in tasks:
            task_key = f"{self.TASK_DATA_PREFIX}{task_id}"
            task_json = await self.redis.get(task_key)
            if task_json:
                task_data = json.loads(task_json)
                task_data['priority_score'] = score
                result.append(task_data)

        return result
