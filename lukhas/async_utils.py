"""
Async utility functions for LUKHAS consciousness architecture.

Provides common async patterns with proper task lifecycle management,
designed for the distributed consciousness system's reliability requirements.
"""

import asyncio
import logging
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from functools import wraps
from typing import Callable, Optional, TypeVar

from .async_manager import (
    ConsciousnessTaskManager,
    TaskPriority,
    get_background_manager,
    get_consciousness_manager,
    get_guardian_manager,
    get_orchestration_manager,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


def consciousness_task(
    *,
    name: str,
    priority: TaskPriority = TaskPriority.NORMAL,
    component: str = "unknown",
    description: str = "",
    consciousness_context: Optional[str] = None,
    manager: Optional[ConsciousnessTaskManager] = None,
):
    """
    Decorator to automatically manage async tasks in consciousness system.

    Usage:
        @consciousness_task(name="memory_processing", priority=TaskPriority.CRITICAL)
        async def process_memory():
            # Task will be automatically managed
            pass
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., asyncio.Task[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> asyncio.Task[T]:
            # Determine manager based on priority if not specified
            if manager is None:
                if priority == TaskPriority.CRITICAL:
                    task_manager = get_consciousness_manager()
                elif priority == TaskPriority.HIGH:
                    task_manager = get_orchestration_manager()
                elif priority == TaskPriority.NORMAL:
                    task_manager = get_background_manager()
                else:
                    task_manager = get_background_manager()
            else:
                task_manager = manager

            coro = func(*args, **kwargs)
            return task_manager.create_task(
                coro,
                name=name,
                priority=priority,
                component=component,
                description=description,
                consciousness_context=consciousness_context,
            )

        return wrapper

    return decorator


async def await_with_timeout(
    awaitable: Awaitable[T],
    timeout: float,
    *,
    name: str = "timeout_task",
    default: Optional[T] = None,
    raise_on_timeout: bool = True,
) -> Optional[T]:
    """
    Await an operation with timeout and proper error handling.

    Args:
        awaitable: The awaitable to execute
        timeout: Timeout in seconds
        name: Name for logging/debugging
        default: Default value to return on timeout (if raise_on_timeout=False)
        raise_on_timeout: Whether to raise TimeoutError on timeout

    Returns:
        Result of awaitable or default value

    Raises:
        asyncio.TimeoutError: If timeout occurs and raise_on_timeout=True
    """
    try:
        result = await asyncio.wait_for(awaitable, timeout=timeout)
        logger.debug(f"Task '{name}' completed within {timeout}s")
        return result
    except asyncio.TimeoutError:
        logger.warning(f"Task '{name}' timed out after {timeout}s")
        if raise_on_timeout:
            raise
        return default


async def run_with_retry(
    coro_factory: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    *,
    name: str = "retry_task",
    exceptions: tuple = (Exception,),
) -> T:
    """
    Run a coroutine with retry logic and exponential backoff.

    Args:
        coro_factory: Factory function that creates the coroutine to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff_factor: Multiplier for delay on each retry
        name: Name for logging/debugging
        exceptions: Exception types to retry on

    Returns:
        Result of successful execution

    Raises:
        The last exception if all retries fail
    """
    last_exception = None
    current_delay = delay

    for attempt in range(max_retries + 1):
        try:
            coro = coro_factory()
            result = await coro
            if attempt > 0:
                logger.info(f"Task '{name}' succeeded on attempt {attempt + 1}")
            return result
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Task '{name}' failed on attempt {attempt + 1}/{max_retries + 1}: {e}. Retrying in {current_delay}s"
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                logger.error(f"Task '{name}' failed after {max_retries + 1} attempts: {e}")

    raise last_exception


@asynccontextmanager
async def consciousness_context(context_name: str, manager: Optional[ConsciousnessTaskManager] = None):
    """
    Context manager for consciousness processing operations.

    Provides automatic cleanup and error handling for consciousness-related
    async operations.

    Usage:
        async with consciousness_context("memory_processing") as ctx:
            # All tasks created here will be tracked and cleaned up
            task1 = ctx.create_task(...)
            task2 = ctx.create_task(...)
    """
    if manager is None:
        manager = get_consciousness_manager()

    tasks = []

    class ContextTaskCreator:
        def create_task(
            self, coro: Awaitable[T], *, name: str, priority: TaskPriority = TaskPriority.NORMAL, description: str = ""
        ) -> asyncio.Task[T]:
            task = manager.create_task(
                coro,
                name=name,
                priority=priority,
                component=context_name,
                description=description,
                consciousness_context=context_name,
            )
            tasks.append(task)
            return task

    ctx = ContextTaskCreator()

    try:
        logger.debug(f"Starting consciousness context: {context_name}")
        yield ctx
    finally:
        # Cancel any remaining tasks
        pending_tasks = [task for task in tasks if not task.done()]
        if pending_tasks:
            logger.info(f"Cleaning up {len(pending_tasks)} pending tasks from context '{context_name}'")
            for task in pending_tasks:
                task.cancel()

            # Wait for cancellation to complete
            try:
                await asyncio.gather(*pending_tasks, return_exceptions=True)
            except Exception as e:
                logger.warning(f"Error during task cleanup in context '{context_name}': {e}")

        logger.debug(f"Consciousness context cleanup complete: {context_name}")


async def gather_with_error_handling(
    *awaitables: Awaitable, name: str = "gather_task", return_exceptions: bool = True, log_errors: bool = True
) -> list:
    """
    Enhanced asyncio.gather with error handling and logging.

    Args:
        *awaitables: Awaitables to execute concurrently
        name: Name for logging/debugging
        return_exceptions: Whether to return exceptions instead of raising
        log_errors: Whether to log exceptions

    Returns:
        List of results and/or exceptions
    """
    try:
        results = await asyncio.gather(*awaitables, return_exceptions=return_exceptions)

        if log_errors and return_exceptions:
            error_count = sum(1 for result in results if isinstance(result, Exception))
            if error_count > 0:
                logger.warning(f"Task group '{name}' completed with {error_count} errors out of {len(results)} tasks")
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Task {i} in '{name}' failed: {result}")

        return results
    except Exception as e:
        if log_errors:
            logger.error(f"Task group '{name}' failed: {e}")
        raise


async def run_background_task(
    coro: Awaitable[T], *, name: str, description: str = "", manager: Optional[ConsciousnessTaskManager] = None
) -> asyncio.Task[T]:
    """
    Create and run a background task with proper management.

    Args:
        coro: Coroutine to run in background
        name: Task name
        description: Task description
        manager: Optional specific task manager

    Returns:
        The created task
    """
    if manager is None:
        manager = get_background_manager()

    return manager.create_task(
        coro, name=name, priority=TaskPriority.LOW, component="background", description=description
    )


async def run_consciousness_task(
    coro: Awaitable[T],
    *,
    name: str,
    priority: TaskPriority = TaskPriority.HIGH,
    description: str = "",
    consciousness_context: Optional[str] = None,
) -> asyncio.Task[T]:
    """
    Create and run a consciousness processing task.

    Args:
        coro: Coroutine to run
        name: Task name
        priority: Task priority
        description: Task description
        consciousness_context: Consciousness context identifier

    Returns:
        The created task
    """
    manager = get_consciousness_manager()

    return manager.create_task(
        coro,
        name=name,
        priority=priority,
        component="consciousness",
        description=description,
        consciousness_context=consciousness_context,
    )


async def run_guardian_task(
    coro: Awaitable[T], *, name: str, description: str = "", consciousness_context: Optional[str] = None
) -> asyncio.Task[T]:
    """
    Create and run a guardian/governance task.

    Args:
        coro: Coroutine to run
        name: Task name
        description: Task description
        consciousness_context: Consciousness context identifier

    Returns:
        The created task
    """
    manager = get_guardian_manager()

    return manager.create_task(
        coro,
        name=name,
        priority=TaskPriority.CRITICAL,
        component="guardian",
        description=description,
        consciousness_context=consciousness_context,
    )


# Compatibility functions for legacy patterns
async def create_managed_task(
    coro: Awaitable[T],
    name: str = "managed_task",
    priority: TaskPriority = TaskPriority.NORMAL,
    component: str = "legacy",
) -> asyncio.Task[T]:
    """
    Legacy compatibility function for creating managed tasks.

    This function provides a simple interface for migrating from
    bare asyncio.create_task calls to managed tasks.
    """
    manager = get_background_manager()

    return manager.create_task(
        coro, name=name, priority=priority, component=component, description="Legacy managed task"
    )
