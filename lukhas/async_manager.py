"""
Production-grade async task lifecycle management for LUKHAS consciousness architecture.

This module provides consciousness-aware async task management with graceful shutdown,
proper error handling, and monitoring integration. Designed specifically for the
distributed consciousness system's reliability requirements.
"""

import asyncio
import logging
import time
import uuid
from collections.abc import Awaitable
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

class TaskPriority(Enum):
    """Task priority levels for consciousness system."""
    CRITICAL = "critical"  # Core consciousness processing
    HIGH = "high"        # Orchestration and communication
    NORMAL = "normal"    # Background services
    LOW = "low"          # Maintenance tasks

@dataclass
class TaskMetadata:
    """Metadata for tracking async tasks."""
    task_id: str
    name: str
    priority: TaskPriority
    created_at: float
    component: str
    description: str = ""
    consciousness_context: Optional[str] = None

class ConsciousnessTaskManager:
    """
    Production-grade async task manager for LUKHAS consciousness architecture.

    Provides:
    - Task lifecycle management with graceful shutdown
    - Priority-based task organization
    - Consciousness-aware error handling
    - Monitoring and telemetry integration
    - Memory-efficient task tracking
    """

    def __init__(self, name: str, max_concurrent_tasks: int = 1000):
        self.name = name
        self.max_concurrent_tasks = max_concurrent_tasks

        # Task registries by priority
        self._tasks: dict[TaskPriority, set[asyncio.Task]] = {
            priority: set() for priority in TaskPriority
        }

        # Task metadata tracking
        self._task_metadata: dict[asyncio.Task, TaskMetadata] = {}

        # Shutdown coordination
        self._shutdown_event = asyncio.Event()
        self._is_shutting_down = False

        # Statistics
        self._stats = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_cancelled": 0,
            "tasks_failed": 0,
            "shutdown_count": 0
        }

        logger.info(f"Initialized {self.__class__.__name__}[{name}] with max_concurrent_tasks={max_concurrent_tasks}")

    def create_task(
        self,
        coro: Awaitable[T],
        *,
        name: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        component: str = "unknown",
        description: str = "",
        consciousness_context: Optional[str] = None
    ) -> asyncio.Task[T]:
        """
        Create and register an async task with consciousness-aware management.

        Args:
            coro: The coroutine to execute
            name: Human-readable task name
            priority: Task priority level
            component: Component/module creating the task
            description: Optional task description
            consciousness_context: Optional consciousness context identifier

        Returns:
            The created asyncio.Task

        Raises:
            RuntimeError: If task limit exceeded or manager is shutting down
        """
        if self._is_shutting_down:
            raise RuntimeError(f"TaskManager[{self.name}] is shutting down, cannot create new tasks")

        total_tasks = sum(len(tasks) for tasks in self._tasks.values())
        if total_tasks >= self.max_concurrent_tasks:
            raise RuntimeError(f"TaskManager[{self.name}] task limit exceeded: {total_tasks}/{self.max_concurrent_tasks}")

        # Create task with name for better debugging
        task_id = str(uuid.uuid4())
        full_name = f"{component}:{name}:{task_id[:8]}"
        task = asyncio.create_task(coro, name=full_name)

        # Create metadata
        metadata = TaskMetadata(
            task_id=task_id,
            name=name,
            priority=priority,
            created_at=time.time(),
            component=component,
            description=description,
            consciousness_context=consciousness_context
        )

        # Register task
        self._tasks[priority].add(task)
        self._task_metadata[task] = metadata

        # Set up cleanup callback
        task.add_done_callback(self._task_done_callback)

        self._stats["tasks_created"] += 1

        logger.debug(f"Created task {full_name} (priority={priority.value}, component={component})")

        return task

    def _task_done_callback(self, task: asyncio.Task) -> None:
        """Callback invoked when task completes."""
        metadata = self._task_metadata.pop(task, None)
        if not metadata:
            return

        # Remove from priority registry
        for priority_tasks in self._tasks.values():
            priority_tasks.discard(task)

        # Update statistics
        if task.cancelled():
            self._stats["tasks_cancelled"] += 1
            logger.debug(f"Task {task.get_name()} cancelled")
        elif task.exception():
            self._stats["tasks_failed"] += 1
            exception = task.exception()
            logger.warning(f"Task {task.get_name()} failed: {exception}")

            # Log consciousness context if available
            if metadata.consciousness_context:
                logger.error(f"Consciousness context failure: {metadata.consciousness_context} - {exception}")
        else:
            self._stats["tasks_completed"] += 1
            logger.debug(f"Task {task.get_name()} completed successfully")

    async def shutdown(self, timeout: float = 30.0, force_after: float = 60.0) -> None:
        """
        Gracefully shutdown all managed tasks.

        Args:
            timeout: Time to wait for graceful shutdown per priority level
            force_after: Time after which to force-cancel remaining tasks
        """
        if self._is_shutting_down:
            logger.warning(f"TaskManager[{self.name}] shutdown already in progress")
            return

        self._is_shutting_down = True
        self._shutdown_event.set()

        logger.info(f"Starting graceful shutdown of TaskManager[{self.name}]")

        # Shutdown by priority: CRITICAL -> HIGH -> NORMAL -> LOW
        priorities = [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]

        start_time = time.time()

        for priority in priorities:
            tasks = list(self._tasks[priority])
            if not tasks:
                continue

            logger.info(f"Shutting down {len(tasks)} {priority.value} priority tasks")

            try:
                # Wait for tasks to complete naturally
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=timeout
                )
                logger.info(f"All {priority.value} priority tasks completed gracefully")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout waiting for {priority.value} priority tasks, proceeding to next level")
                # Don't cancel yet - let force_after handle it if needed

        # Force-cancel any remaining tasks after force_after period
        elapsed = time.time() - start_time
        if elapsed < force_after:
            remaining_wait = force_after - elapsed
            logger.info(f"Waiting {remaining_wait:.1f}s more before force cancellation")
            await asyncio.sleep(remaining_wait)

        # Cancel any remaining tasks
        remaining_tasks = []
        for priority_tasks in self._tasks.values():
            remaining_tasks.extend(priority_tasks)

        if remaining_tasks:
            logger.warning(f"Force-cancelling {len(remaining_tasks)} remaining tasks")
            for task in remaining_tasks:
                if not task.done():
                    task.cancel()

            # Wait briefly for cancellation to complete
            try:
                await asyncio.wait(remaining_tasks, timeout=5.0)
            except asyncio.TimeoutError:
                logger.error("Some tasks did not respond to cancellation")

        self._stats["shutdown_count"] += 1

        total_time = time.time() - start_time
        logger.info(f"TaskManager[{self.name}] shutdown complete in {total_time:.2f}s")
        logger.info(f"Final stats: {self.get_stats()}")

    def get_stats(self) -> dict[str, Any]:
        """Get task manager statistics."""
        active_tasks = {
            priority.value: len(tasks)
            for priority, tasks in self._tasks.items()
        }

        return {
            **self._stats,
            "active_tasks": active_tasks,
            "total_active": sum(active_tasks.values()),
            "is_shutting_down": self._is_shutting_down
        }

    def get_active_tasks(self) -> dict[str, list]:
        """Get details of currently active tasks."""
        result = {}
        for priority, tasks in self._tasks.items():
            task_info = []
            for task in tasks:
                metadata = self._task_metadata.get(task)
                if metadata:
                    task_info.append({
                        "name": task.get_name(),
                        "component": metadata.component,
                        "description": metadata.description,
                        "age": time.time() - metadata.created_at,
                        "done": task.done(),
                        "cancelled": task.cancelled()
                    })
            result[priority.value] = task_info
        return result

    @asynccontextmanager
    async def task_context(
        self,
        coro: Awaitable[T],
        *,
        name: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        component: str = "unknown",
        description: str = "",
        consciousness_context: Optional[str] = None
    ):
        """
        Context manager for creating and automatically cleaning up a task.

        Usage:
            async with task_manager.task_context(my_coro(), name="my_task") as task:
                result = await task
        """
        task = self.create_task(
            coro,
            name=name,
            priority=priority,
            component=component,
            description=description,
            consciousness_context=consciousness_context
        )
        try:
            yield task
        finally:
            if not task.done():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

# Global task managers for different consciousness subsystems
_task_managers: dict[str, ConsciousnessTaskManager] = {}

def get_task_manager(name: str, max_concurrent: int = 1000) -> ConsciousnessTaskManager:
    """Get or create a named task manager."""
    if name not in _task_managers:
        _task_managers[name] = ConsciousnessTaskManager(name, max_concurrent)
    return _task_managers[name]

async def shutdown_all_managers(timeout: float = 30.0) -> None:
    """Shutdown all registered task managers."""
    if not _task_managers:
        logger.info("No task managers to shutdown")
        return

    logger.info(f"Shutting down {len(_task_managers)} task managers")

    # Shutdown in parallel
    shutdown_tasks = [
        manager.shutdown(timeout)
        for manager in _task_managers.values()
    ]

    await asyncio.gather(*shutdown_tasks, return_exceptions=True)

    _task_managers.clear()
    logger.info("All task managers shutdown complete")

# Pre-configured managers for consciousness subsystems
def get_consciousness_manager() -> ConsciousnessTaskManager:
    """Get task manager for consciousness processing."""
    return get_task_manager("consciousness", max_concurrent=500)

def get_orchestration_manager() -> ConsciousnessTaskManager:
    """Get task manager for orchestration and communication."""
    return get_task_manager("orchestration", max_concurrent=300)

def get_background_manager() -> ConsciousnessTaskManager:
    """Get task manager for background services."""
    return get_task_manager("background", max_concurrent=200)

def get_guardian_manager() -> ConsciousnessTaskManager:
    """Get task manager for guardian/governance tasks."""
    return get_task_manager("guardian", max_concurrent=100)