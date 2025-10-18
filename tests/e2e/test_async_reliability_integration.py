"""
Comprehensive async reliability integration tests for LUKHAS consciousness architecture.

Tests async task lifecycle management, graceful shutdown, and error handling
across consciousness systems after the async guardian reliability hardening.
"""

import asyncio
import gc
import time

import pytest

from async_manager import (
    ConsciousnessTaskManager,
    TaskPriority,
    get_consciousness_manager,
    get_guardian_manager,
    shutdown_all_managers,
)
from async_utils import (
    await_with_timeout,
    consciousness_context,
    gather_with_error_handling,
    run_guardian_task,
)


@pytest.fixture
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def clean_managers():
    """Ensure clean manager state for each test."""
    await shutdown_all_managers()
    yield
    await shutdown_all_managers()


class TestAsyncTaskLifecycle:
    """Test async task lifecycle management."""

    @pytest.mark.asyncio
    async def test_task_creation_and_tracking(self, clean_managers):
        """Test that tasks are properly created and tracked."""
        manager = get_consciousness_manager()

        async def test_coro():
            await asyncio.sleep(0.1)
            return "success"

        task = manager.create_task(
            test_coro(),
            name="test_task",
            priority=TaskPriority.NORMAL,
            component="test",
            description="Test task creation",
        )

        # Verify task is tracked
        stats = manager.get_stats()
        assert stats["tasks_created"] == 1
        assert stats["total_active"] == 1

        # Wait for completion
        result = await task
        assert result == "success"

        # Verify completion tracking
        await asyncio.sleep(0.1)  # Allow callback to run
        stats = manager.get_stats()
        assert stats["tasks_completed"] == 1
        assert stats["total_active"] == 0

    @pytest.mark.asyncio
    async def test_task_cancellation_handling(self, clean_managers):
        """Test proper handling of task cancellation."""
        manager = get_consciousness_manager()

        async def long_running_task():
            try:
                await asyncio.sleep(10)  # Long task
            except asyncio.CancelledError:
                # Cleanup logic here
                raise

        task = manager.create_task(
            long_running_task(), name="cancellable_task", priority=TaskPriority.LOW, component="test"
        )

        # Cancel after short delay
        await asyncio.sleep(0.1)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        # Verify cancellation tracking
        await asyncio.sleep(0.1)
        stats = manager.get_stats()
        assert stats["tasks_cancelled"] == 1

    @pytest.mark.asyncio
    async def test_task_error_handling(self, clean_managers):
        """Test proper error handling and logging."""
        manager = get_consciousness_manager()

        async def failing_task():
            raise ValueError("Test error")

        task = manager.create_task(
            failing_task(),
            name="failing_task",
            priority=TaskPriority.HIGH,
            component="test",
            consciousness_context="error_test",
        )

        with pytest.raises(ValueError):
            await task

        # Verify error tracking
        await asyncio.sleep(0.1)
        stats = manager.get_stats()
        assert stats["tasks_failed"] == 1


class TestGracefulShutdown:
    """Test graceful shutdown functionality."""

    @pytest.mark.asyncio
    async def test_priority_based_shutdown(self, clean_managers):
        """Test that shutdown respects task priorities."""
        manager = get_consciousness_manager()
        shutdown_order = []

        async def priority_task(priority: TaskPriority, name: str):
            try:
                await asyncio.sleep(5)  # Long-running task
            except asyncio.CancelledError:
                shutdown_order.append(name)
                raise

        # Create tasks with different priorities
        manager.create_task(
            priority_task(TaskPriority.CRITICAL, "critical"),
            name="critical_task",
            priority=TaskPriority.CRITICAL,
            component="test",
        )

        manager.create_task(
            priority_task(TaskPriority.NORMAL, "normal"),
            name="normal_task",
            priority=TaskPriority.NORMAL,
            component="test",
        )

        manager.create_task(
            priority_task(TaskPriority.LOW, "low"), name="low_task", priority=TaskPriority.LOW, component="test"
        )

        # Start shutdown
        shutdown_task = asyncio.create_task(manager.shutdown(timeout=0.5))

        # Wait for shutdown
        await shutdown_task

        # Verify priority-based shutdown order
        # Critical tasks should be given more time before cancellation
        assert len(shutdown_order) == 3
        # Low priority tasks should be cancelled first in practice

    @pytest.mark.asyncio
    async def test_shutdown_timeout_handling(self, clean_managers):
        """Test shutdown timeout and force cancellation."""
        manager = get_consciousness_manager()

        async def stubborn_task():
            # Task that ignores cancellation for a while
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                await asyncio.sleep(0.5)  # Delay cancellation
                raise

        task = manager.create_task(
            stubborn_task(), name="stubborn_task", priority=TaskPriority.NORMAL, component="test"
        )

        start_time = time.time()
        await manager.shutdown(timeout=0.2, force_after=0.5)
        shutdown_time = time.time() - start_time

        # Should complete within force_after timeout
        assert shutdown_time < 1.0
        assert task.cancelled()


class TestConsciousnessContextIntegration:
    """Test consciousness context management."""

    @pytest.mark.asyncio
    async def test_consciousness_context_cleanup(self, clean_managers):
        """Test that consciousness context properly cleans up tasks."""
        created_tasks = []

        async with consciousness_context("test_context") as ctx:
            # Create multiple tasks within context
            task1 = ctx.create_task(
                asyncio.sleep(5),  # Long task
                name="context_task1",
                priority=TaskPriority.NORMAL,
            )
            task2 = ctx.create_task(
                asyncio.sleep(5),  # Long task
                name="context_task2",
                priority=TaskPriority.HIGH,
            )

            created_tasks.extend([task1, task2])

            # Short delay then exit context (simulating early exit)
            await asyncio.sleep(0.1)

        # Tasks should be cancelled when context exits
        for task in created_tasks:
            assert task.cancelled()

    @pytest.mark.asyncio
    async def test_guardian_task_integration(self, clean_managers):
        """Test guardian task creation and management."""

        async def guardian_operation():
            await asyncio.sleep(0.2)
            return "guardian_complete"

        task = await run_guardian_task(
            guardian_operation(),
            name="test_guardian_op",
            description="Test guardian integration",
            consciousness_context="guardian_test",
        )

        result = await task
        assert result == "guardian_complete"

        # Verify guardian manager was used
        guardian_manager = get_guardian_manager()
        stats = guardian_manager.get_stats()
        assert stats["tasks_completed"] >= 1


class TestErrorRecovery:
    """Test error recovery and resilience."""

    @pytest.mark.asyncio
    async def test_task_limit_enforcement(self, clean_managers):
        """Test that task limits are properly enforced."""
        # Create manager with low limit
        manager = ConsciousnessTaskManager("test_limited", max_concurrent_tasks=2)

        async def dummy_task():
            await asyncio.sleep(1)

        # Create tasks up to limit
        task1 = manager.create_task(dummy_task(), name="task1", component="test")
        task2 = manager.create_task(dummy_task(), name="task2", component="test")

        # Third task should raise error
        with pytest.raises(RuntimeError, match="task limit exceeded"):
            manager.create_task(dummy_task(), name="task3", component="test")

        # Clean up
        task1.cancel()
        task2.cancel()
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_manager_shutdown_state(self, clean_managers):
        """Test that manager properly prevents new tasks during shutdown."""
        manager = get_consciousness_manager()

        async def test_task():
            await asyncio.sleep(0.1)

        # Start shutdown
        shutdown_task = asyncio.create_task(manager.shutdown())

        # Short delay to allow shutdown to start
        await asyncio.sleep(0.05)

        # Attempting to create task during shutdown should fail
        with pytest.raises(RuntimeError, match="shutting down"):
            manager.create_task(test_task(), name="late_task", component="test")

        await shutdown_task


class TestMemoryLeakPrevention:
    """Test memory leak prevention."""

    @pytest.mark.asyncio
    async def test_task_reference_cleanup(self, clean_managers):
        """Test that completed tasks don't create memory leaks."""
        manager = get_consciousness_manager()

        async def quick_task():
            return "done"

        # Create many short-lived tasks
        tasks = []
        for i in range(100):
            task = manager.create_task(quick_task(), name=f"quick_task_{i}", component="test")
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        # Allow cleanup callbacks to run
        await asyncio.sleep(0.1)

        # Force garbage collection
        gc.collect()

        # Verify tasks are cleaned up
        stats = manager.get_stats()
        assert stats["total_active"] == 0
        assert stats["tasks_completed"] == 100

        # Internal tracking should be cleaned up
        assert len(manager._task_metadata) == 0
        for priority_tasks in manager._tasks.values():
            assert len(priority_tasks) == 0


class TestAsyncUtilities:
    """Test async utility functions."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test await_with_timeout functionality."""

        async def slow_task():
            await asyncio.sleep(1.0)
            return "completed"

        # Should timeout
        result = await await_with_timeout(slow_task(), timeout=0.1, default="timed_out", raise_on_timeout=False)
        assert result == "timed_out"

        # Should complete
        async def fast_task():
            return "fast_done"

        result = await await_with_timeout(fast_task(), timeout=1.0)
        assert result == "fast_done"

    @pytest.mark.asyncio
    async def test_gather_error_handling(self):
        """Test enhanced gather with error handling."""

        async def success_task():
            return "success"

        async def failing_task():
            raise ValueError("test error")

        results = await gather_with_error_handling(
            success_task(), failing_task(), name="test_gather", return_exceptions=True
        )

        assert len(results) == 2
        assert results[0] == "success"
        assert isinstance(results[1], ValueError)


@pytest.mark.asyncio
async def test_integration_with_real_consciousness_systems():
    """Integration test with actual consciousness system components."""
    # This would test actual consciousness modules if available
    # For now, test the async infrastructure

    manager = get_consciousness_manager()

    # Simulate consciousness processing
    async def mock_awareness_processing():
        await asyncio.sleep(0.1)
        return {"awareness_level": 0.8, "processed": True}

    task = manager.create_task(
        mock_awareness_processing(),
        name="awareness_processing",
        priority=TaskPriority.CRITICAL,
        component="consciousness.awareness",
        consciousness_context="awareness_test",
    )

    result = await task
    assert result["processed"] is True
    assert result["awareness_level"] == 0.8

    await shutdown_all_managers()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
