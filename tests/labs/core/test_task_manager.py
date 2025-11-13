import asyncio
import pytest
from labs.core.task_manager import TaskManager, Task, TaskNotFoundError

@pytest.fixture
def task_manager():
    return TaskManager()

@pytest.mark.asyncio
async def test_submit_and_get_status(task_manager: TaskManager):
    task = Task('cognitive')
    task_id = await task_manager.submit_task(task)

    status = await task_manager.get_task_status(task_id)
    assert status.id == task_id
    assert status.state in ['pending', 'running', 'completed']

    await asyncio.sleep(0.5) # Allow time for task to complete

    status = await task_manager.get_task_status(task_id)
    assert status.state == 'completed'
    assert status.result == "Cognitive task complete"

@pytest.mark.asyncio
async def test_task_cancellation(task_manager: TaskManager):
    task = Task('cognitive')
    task_id = await task_manager.submit_task(task)

    # Allow the task to start running
    await asyncio.sleep(0.05)

    cancelled = await task_manager.cancel_task(task_id)
    assert cancelled is True

    # Allow time for the cancellation to be processed
    await asyncio.sleep(0.2)

    status = await task_manager.get_task_status(task_id)
    assert status.state == 'cancelled'

@pytest.mark.asyncio
async def test_task_not_found(task_manager: TaskManager):
    with pytest.raises(TaskNotFoundError):
        await task_manager.get_task_status("non_existent_id")

@pytest.mark.asyncio
async def test_task_priorities(task_manager: TaskManager):
    task1 = Task('cognitive', priority=1)
    task2 = Task('cognitive', priority=10)

    await task_manager.submit_task(task1)
    await task_manager.submit_task(task2)

    # This is a simplified test. A more robust test would inspect the order of execution.
    # For now, we'll just ensure they both complete.
    await asyncio.sleep(1)

    status1 = await task_manager.get_task_status(task1.id)
    status2 = await task_manager.get_task_status(task2.id)

    assert status1.state == 'completed'
    assert status2.state == 'completed'

@pytest.mark.asyncio
async def test_task_dependencies(task_manager: TaskManager):
    task1 = Task('cognitive')
    task2 = Task('cognitive', dependencies=[task1.id])

    await task_manager.submit_task(task2)
    await task_manager.submit_task(task1)

    await asyncio.sleep(2) # Allow time for tasks to complete

    task1_status = await task_manager.get_task_status(task1.id)
    task2_status = await task_manager.get_task_status(task2.id)

    assert task1_status.state == 'completed'
    assert task2_status.state == 'completed'

@pytest.mark.asyncio
async def test_task_failure_and_retry(task_manager: TaskManager):
    class FailingTask(Task):
        def __init__(self, **kwargs):
            super().__init__(task_type='failing', **kwargs)
            self.execution_count = 0

    async def failing_executor(task):
        task.execution_count += 1
        if task.execution_count <= 2:
            raise ValueError("Task failed")
        return "Task succeeded"

    task_manager._execute_failing = failing_executor

    # Monkey patch the _execute_task method to handle the new task type
    original_execute_task = task_manager._execute_task
    async def new_execute_task(task):
        if task.type == 'failing':
            return await task_manager._execute_failing(task)
        return await original_execute_task(task)
    task_manager._execute_task = new_execute_task

    failing_task = FailingTask(max_retries=2)
    task_id = await task_manager.submit_task(failing_task)

    await asyncio.sleep(1)

    status = await task_manager.get_task_status(task_id)
    assert status.state == 'completed'
    assert status.result == "Task succeeded"
    assert failing_task.execution_count == 3
