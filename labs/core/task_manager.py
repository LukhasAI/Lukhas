from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Tuple
import uuid
import time

class Task:
    def __init__(self, task_type: str, priority: int = 0, dependencies: Optional[List[str]] = None, max_retries: int = 3, id: Optional[str] = None):
        self.id = id if id else str(uuid.uuid4())
        self.type = task_type
        self.state = 'pending'
        self.progress = 0.0
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.priority = priority
        self.dependencies = dependencies or []
        self.retry_count = 0
        self.max_retries = max_retries
        self.submission_time = time.time()

    def __lt__(self, other):
        # This allows tasks to be compared in the priority queue
        if self.priority == other.priority:
            return self.submission_time < other.submission_time
        return self.priority > other.priority

    def cancel(self):
        self.state = 'cancelled'

class TaskStatus:
    def __init__(self, id: str, state: str, progress: float = 0.0, result: Optional[Any] = None):
        self.id = id
        self.state = state
        self.progress = progress
        self.result = result

class TaskNotFoundError(Exception):
    pass

class TaskManager:
    '''Manage LUKHAS cognitive tasks'''

    def __init__(self):
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.completed_task_ids = set()
        self.running_async_tasks: Dict[str, asyncio.Task] = {}

    async def submit_task(self, task: Task) -> str:
        '''Submit task for execution'''
        self.active_tasks[task.id] = task
        await self.task_queue.put(task)

        if not hasattr(self, '_worker_task') or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_tasks())

        return task.id

    async def get_task_status(self, task_id: str) -> TaskStatus:
        '''Get task execution status'''
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        else:
            raise TaskNotFoundError(f"Task {task_id} not found")

        return TaskStatus(
            id=task.id,
            state=task.state,
            progress=task.progress,
            result=task.result
        )

    async def cancel_task(self, task_id: str) -> bool:
        '''Cancel running task'''
        if task_id in self.completed_tasks:
            return False

        if task_id in self.running_async_tasks:
            self.running_async_tasks[task_id].cancel()
            return True

        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            return True

        raise TaskNotFoundError(f"Task {task_id} not found")

    async def _process_tasks(self):
        '''Worker to process task queue'''
        while True:
            try:
                task = await self.task_queue.get()

                if task.state == 'cancelled':
                    self.active_tasks.pop(task.id, None)
                    self.completed_tasks[task.id] = task
                    self.completed_task_ids.add(task.id)
                    self.task_queue.task_done()
                    continue

                dependencies_met = all(dep in self.completed_task_ids for dep in task.dependencies)
                if not dependencies_met:
                    task.submission_time = time.time()
                    await self.task_queue.put(task)
                    self.task_queue.task_done()
                    await asyncio.sleep(0.1)
                    continue

                task.state = 'running'

                async_task = asyncio.create_task(self._execute_task(task))
                self.running_async_tasks[task.id] = async_task

                try:
                    result = await async_task
                    task.result = result
                    task.state = 'completed'
                    self.completed_task_ids.add(task.id)
                except asyncio.CancelledError:
                    task.state = 'cancelled'
                except Exception as e:
                    task.error = str(e)
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.state = 'pending'
                        await self.task_queue.put(task)
                    else:
                        task.state = 'failed'
                        self.completed_task_ids.add(task.id)

                if task.state in ['completed', 'failed', 'cancelled']:
                    self.active_tasks.pop(task.id, None)
                    self.completed_tasks[task.id] = task

                self.running_async_tasks.pop(task.id, None)
                self.task_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def _execute_task(self, task: Task) -> Any:
        '''Execute a single task'''
        if task.type == 'cognitive':
            return await self._execute_cognitive(task)
        elif task.type == 'memory':
            return await self._execute_memory(task)
        elif task.type == 'symbolic':
            return await self._execute_symbolic(task)
        else:
            raise ValueError(f"Unknown task type: {task.type}")

    async def _execute_cognitive(self, task: Task):
        # Placeholder for cognitive task execution
        await asyncio.sleep(0.1)
        return "Cognitive task complete"

    async def _execute_memory(self, task: Task):
        # Placeholder for memory task execution
        await asyncio.sleep(0.1)
        return "Memory task complete"

    async def _execute_symbolic(self, task: Task):
        # Placeholder for symbolic task execution
        await asyncio.sleep(0.1)
        return "Symbolic task complete"
