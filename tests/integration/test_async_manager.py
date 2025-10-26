"""
Tests for the LUKHAS async task management system.

Tests async task lifecycle management, graceful shutdown, and
consciousness-aware task prioritization for production reliability.
"""

import asyncio

import pytest
from async_manager import (
    ConsciousnessTaskManager,
    TaskPriority,
    get_background_manager,
    get_consciousness_manager,
    get_guardian_manager,
    get_orchestration_manager,
    shutdown_all_managers,
)
from async_utils import (
    await_with_timeout,
    consciousness_context,
    consciousness_task,
    run_with_retry,
)


class TestConsciousnessTaskManager:
    """Test the core task manager functionality."""

    @pytest.fixture
    def task_manager(self):
        """Create a task manager for testing."""
        return ConsciousnessTaskManager("test", max_concurrent_tasks=10)

    @pytest.mark.asyncio
    async def test_create_task_basic(self, task_manager):
        """Test basic task creation."""

        async def dummy_task():
            await asyncio.sleep(0.01)
            return "success"

        task = task_manager.create_task(dummy_task(), name="test_task", component="test")

        assert task is not None
        assert not task.done()

        result = await task
        assert result == "success"
        assert task.done()

    @pytest.mark.asyncio
    async def test_task_priorities(self, task_manager):
        """Test task creation with different priorities."""
        completed_order = []

        async def priority_task(priority_name):
            await asyncio.sleep(0.01)
            completed_order.append(priority_name)

        # Create tasks with different priorities
        critical_task = task_manager.create_task(
            priority_task("critical"), name="critical_task", priority=TaskPriority.CRITICAL, component="test"
        )

        normal_task = task_manager.create_task(
            priority_task("normal"), name="normal_task", priority=TaskPriority.NORMAL, component="test"
        )

        # Wait for completion
        await asyncio.gather(critical_task, normal_task)

        # Both should complete (priority affects shutdown order, not execution)
        assert len(completed_order) == 2
        assert "critical" in completed_order
        assert "normal" in completed_order

    @pytest.mark.asyncio
    async def test_task_limit_enforcement(self, task_manager):
        """Test task limit enforcement."""
        # Fill up to the limit
        tasks = []
        for i in range(10):  # Max concurrent is 10
            task = task_manager.create_task(
                asyncio.sleep(1),  # Long running task
                name=f"task_{i}",
                component="test",
            )
            tasks.append(task)

        # Try to create one more - should fail
        with pytest.raises(RuntimeError, match="task limit exceeded"):
            task_manager.create_task(asyncio.sleep(0.01), name="overflow_task", component="test")

        # Clean up
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, task_manager):
        """Test graceful shutdown of all tasks."""
        completed_tasks = []

        async def trackable_task(task_id):
            try:
                await asyncio.sleep(0.1)
                completed_tasks.append(f"completed_{task_id}")
            except asyncio.CancelledError:
                completed_tasks.append(f"cancelled_{task_id}")
                raise

        # Create several tasks
        tasks = []
        for i in range(3):
            task = task_manager.create_task(trackable_task(i), name=f"trackable_{i}", component="test")
            tasks.append(task)

        # Start shutdown
        await task_manager.shutdown(timeout=0.05)  # Short timeout

        # All tasks should be cancelled
        assert len(completed_tasks) >= 3  # Either completed or cancelled
        assert all("cancelled_" in result or "completed_" in result for result in completed_tasks)

    @pytest.mark.asyncio
    async def test_task_metadata_tracking(self, task_manager):
        """Test that task metadata is properly tracked."""

        async def dummy_task():
            return "done"

        task = task_manager.create_task(
            dummy_task(),
            name="metadata_test",
            component="test_component",
            description="Test task for metadata",
            consciousness_context="test_context",
        )

        # Check active tasks before completion
        active_tasks = task_manager.get_active_tasks()
        assert "normal" in active_tasks
        assert len(active_tasks["normal"]) == 1

        task_info = active_tasks["normal"][0]
        assert "metadata_test" in task_info["name"]
        assert task_info["component"] == "test_component"
        assert task_info["description"] == "Test task for metadata"

        await task

        # Check stats after completion
        stats = task_manager.get_stats()
        assert stats["tasks_created"] == 1
        assert stats["tasks_completed"] == 1


class TestAsyncUtils:
    """Test async utility functions."""

    @pytest.mark.asyncio
    async def test_await_with_timeout_success(self):
        """Test successful await with timeout."""

        async def quick_task():
            await asyncio.sleep(0.01)
            return "success"

        result = await await_with_timeout(quick_task(), timeout=0.1, name="quick_test")
        assert result == "success"

    @pytest.mark.asyncio
    async def test_await_with_timeout_failure(self):
        """Test timeout behavior."""

        async def slow_task():
            await asyncio.sleep(0.1)
            return "too_late"

        with pytest.raises(asyncio.TimeoutError):
            await await_with_timeout(slow_task(), timeout=0.01, name="slow_test")

    @pytest.mark.asyncio
    async def test_await_with_timeout_default(self):
        """Test timeout with default return value."""

        async def slow_task():
            await asyncio.sleep(0.1)
            return "too_late"

        result = await await_with_timeout(
            slow_task(), timeout=0.01, name="slow_test", default="default_value", raise_on_timeout=False
        )
        assert result == "default_value"

    @pytest.mark.asyncio
    async def test_run_with_retry_success(self):
        """Test retry logic with eventual success."""
        attempt_count = 0

        async def flaky_task():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await run_with_retry(
            lambda: flaky_task(),
            max_retries=3,
            delay=0.001,  # Fast retry for testing
            name="flaky_test",
        )

        assert result == "success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_run_with_retry_failure(self):
        """Test retry logic with eventual failure."""

        async def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            await run_with_retry(lambda: always_fails(), max_retries=2, delay=0.001, name="failing_test")

    @pytest.mark.asyncio
    async def test_consciousness_context_manager(self):
        """Test consciousness context manager."""
        tasks_created = []

        async with consciousness_context("test_context") as ctx:
            # Create some tasks within context
            task1 = ctx.create_task(asyncio.sleep(0.01), name="context_task_1")
            task2 = ctx.create_task(asyncio.sleep(0.01), name="context_task_2")
            tasks_created.extend([task1, task2])

            # Tasks should be running
            assert not task1.done()
            assert not task2.done()

        # After context exit, tasks should complete or be cancelled
        await asyncio.sleep(0.02)
        for task in tasks_created:
            assert task.done()


class TestGlobalManagers:
    """Test global task manager functions."""

    def test_get_managers(self):
        """Test getting different manager types."""
        consciousness_mgr = get_consciousness_manager()
        orchestration_mgr = get_orchestration_manager()
        background_mgr = get_background_manager()
        guardian_mgr = get_guardian_manager()

        assert consciousness_mgr.name == "consciousness"
        assert orchestration_mgr.name == "orchestration"
        assert background_mgr.name == "background"
        assert guardian_mgr.name == "guardian"

        # Should return same instance on subsequent calls
        assert get_consciousness_manager() is consciousness_mgr

    @pytest.mark.asyncio
    async def test_shutdown_all_managers(self):
        """Test shutting down all global managers."""
        # Create some tasks across different managers
        consciousness_mgr = get_consciousness_manager()
        orchestration_mgr = get_orchestration_manager()

        task1 = consciousness_mgr.create_task(asyncio.sleep(1), name="long_consciousness_task", component="test")
        task2 = orchestration_mgr.create_task(asyncio.sleep(1), name="long_orchestration_task", component="test")

        # Shutdown all managers
        await shutdown_all_managers(timeout=0.1)

        # Tasks should be cancelled
        assert task1.cancelled() or task1.done()
        assert task2.cancelled() or task2.done()


class TestConsciousnessTaskDecorator:
    """Test the consciousness task decorator."""

    @pytest.mark.asyncio
    async def test_consciousness_task_decorator(self):
        """Test the consciousness task decorator creates managed tasks."""

        @consciousness_task(name="decorated_task", priority=TaskPriority.HIGH, component="test.decorator")
        async def decorated_function():
            await asyncio.sleep(0.01)
            return "decorated_result"

        # Call the decorated function
        task = decorated_function()

        # Should return a task
        assert isinstance(task, asyncio.Task)

        # Task should complete successfully
        result = await task
        assert result == "decorated_result"


@pytest.mark.integration
class TestAsyncReliabilityIntegration:
    """Integration tests for async reliability features."""

    @pytest.mark.asyncio
    async def test_consciousness_processing_simulation(self):
        """Simulate consciousness processing with proper task management."""
        consciousness_mgr = get_consciousness_manager()
        processing_results = []

        async def memory_fold_processing():
            """Simulate memory fold processing."""
            await asyncio.sleep(0.02)
            processing_results.append("memory_processed")
            return "memory_fold_complete"

        async def dream_state_transition():
            """Simulate dream state processing."""
            await asyncio.sleep(0.03)
            processing_results.append("dream_processed")
            return "dream_state_complete"

        # Create consciousness tasks
        memory_task = consciousness_mgr.create_task(
            memory_fold_processing(),
            name="memory_fold_processing",
            priority=TaskPriority.CRITICAL,
            component="consciousness.memory",
            description="Process memory folds with cascade prevention",
            consciousness_context="memory_processing",
        )

        dream_task = consciousness_mgr.create_task(
            dream_state_transition(),
            name="dream_state_processing",
            priority=TaskPriority.HIGH,
            component="consciousness.dreams",
            description="Process dream state transitions",
            consciousness_context="dream_processing",
        )

        # Wait for completion
        memory_result = await memory_task
        dream_result = await dream_task

        assert memory_result == "memory_fold_complete"
        assert dream_result == "dream_state_complete"
        assert "memory_processed" in processing_results
        assert "dream_processed" in processing_results

        # Verify task manager stats
        stats = consciousness_mgr.get_stats()
        assert stats["tasks_completed"] >= 2

    @pytest.mark.asyncio
    async def test_guardian_system_reliability(self):
        """Test Guardian system async reliability."""
        guardian_mgr = get_guardian_manager()
        guardian_events = []

        async def ethical_evaluation():
            """Simulate ethical evaluation."""
            await asyncio.sleep(0.01)
            guardian_events.append("ethical_evaluation_complete")
            return {"drift_score": 0.05, "evaluation": "passed"}

        async def threat_detection():
            """Simulate threat detection."""
            await asyncio.sleep(0.01)
            guardian_events.append("threat_detection_complete")
            return {"threats_detected": 0, "status": "clear"}

        # Create guardian tasks
        ethics_task = guardian_mgr.create_task(
            ethical_evaluation(),
            name="ethical_evaluation",
            priority=TaskPriority.CRITICAL,
            component="governance.guardian",
            description="Perform ethical drift evaluation",
            consciousness_context="guardian_ethics",
        )

        threat_task = guardian_mgr.create_task(
            threat_detection(),
            name="threat_detection",
            priority=TaskPriority.CRITICAL,
            component="governance.guardian",
            description="Scan for security threats",
            consciousness_context="guardian_security",
        )

        # Wait for completion
        ethics_result = await ethics_task
        threat_result = await threat_task

        assert ethics_result["evaluation"] == "passed"
        assert threat_result["status"] == "clear"
        assert len(guardian_events) == 2

        # Guardian tasks should maintain high priority
        stats = guardian_mgr.get_stats()
        assert stats["tasks_completed"] >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
