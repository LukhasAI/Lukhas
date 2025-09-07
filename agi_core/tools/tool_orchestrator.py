"""
LUKHAS AGI - Tool Orchestrator
Advanced tool coordination and orchestration system for consciousness development.
⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class OrchestrationStrategy(Enum):
    """Strategies for tool orchestration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"
    PRIORITY_BASED = "priority_based"


class ToolStatus(Enum):
    """Status of a tool in the orchestration."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ToolTask:
    """Represents a task for a tool in the orchestration."""

    task_id: str
    tool_name: str
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher number = higher priority
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    status: ToolStatus = ToolStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class OrchestrationContext:
    """Context for tool orchestration operations."""

    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    max_concurrent_tools: int = 5
    default_timeout: float = 30.0
    enable_retry: bool = True
    enable_logging: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Execution plan for tool orchestration."""

    plan_id: str
    tasks: list[ToolTask] = field(default_factory=list)
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    priority_order: list[str] = field(default_factory=list)
    estimated_duration: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolChain:
    """A chain of tools to be executed in sequence."""

    chain_id: str
    tools: list[str] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)
    shared_context: dict[str, Any] = field(default_factory=dict)
    chain_status: ToolStatus = ToolStatus.IDLE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ToolOrchestrator:
    """Advanced tool orchestration system for consciousness development."""

    def __init__(self, context: Optional[OrchestrationContext] = None):
        """Initialize the tool orchestrator."""
        self.context = context or OrchestrationContext()
        self.registered_tools: Dict[str, Dict[str, Callable]] = {}
        self.active_tasks: Dict[str, ToolTask] = {}
        self.completed_tasks: List[ToolTask] = []
        self.task_queue: List[ToolTask] = []
        self.orchestration_history: List[Dict[str, Any]] = []

    def register_tool(
        self,
        tool_name: str,
        tool_functions: Dict[str, Callable]
    ) -> None:
        """Register a tool with its available functions."""
        self.registered_tools[tool_name] = tool_functions

        if self.context.enable_logging:
            logger.info(f"Registered tool '{tool_name}' with {len(tool_functions)} functions")

    def create_task(
        self,
        tool_name: str,
        function_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        timeout: Optional[float] = None,
        task_id: Optional[str] = None
    ) -> ToolTask:
        """Create a new tool task."""
        if task_id is None:
            task_id = f"task_{len(self.active_tasks) + len(self.completed_tasks)}"

        task = ToolTask(
            task_id=task_id,
            tool_name=tool_name,
            function_name=function_name,
            parameters=parameters or {},
            priority=priority,
            timeout=timeout or self.context.default_timeout
        )

        return task

    async def execute_task(self, task: ToolTask) -> ToolTask:
        """Execute a single tool task."""
        if task.tool_name not in self.registered_tools:
            task.status = ToolStatus.FAILED
            task.error = f"Tool '{task.tool_name}' not registered"
            return task

        if task.function_name not in self.registered_tools[task.tool_name]:
            task.status = ToolStatus.FAILED
            task.error = f"Function '{task.function_name}' not found in tool '{task.tool_name}'"
            return task

        task.status = ToolStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        self.active_tasks[task.task_id] = task

        try:
            func = self.registered_tools[task.tool_name][task.function_name]

            # Execute with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(**task.parameters),
                    timeout=task.timeout
                )
            else:
                result = func(**task.parameters)

            task.result = result
            task.status = ToolStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)

        except asyncio.TimeoutError:
            task.status = ToolStatus.FAILED
            task.error = f"Task timed out after {task.timeout} seconds"
        except Exception as e:
            task.status = ToolStatus.FAILED
            task.error = str(e)

        # Move from active to completed
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        self.completed_tasks.append(task)

        # Log task completion
        if self.context.enable_logging:
            status = "✅" if task.status == ToolStatus.COMPLETED else "❌"
            logger.info(f"{status} Task {task.task_id} ({task.tool_name}.{task.function_name})")

        return task

    async def orchestrate_tasks(
        self,
        tasks: List[ToolTask],
        strategy: Optional[OrchestrationStrategy] = None
    ) -> List[ToolTask]:
        """Orchestrate multiple tool tasks."""
        strategy = strategy or self.context.strategy

        if strategy == OrchestrationStrategy.SEQUENTIAL:
            return await self._execute_sequential(tasks)
        elif strategy == OrchestrationStrategy.PARALLEL:
            return await self._execute_parallel(tasks)
        elif strategy == OrchestrationStrategy.PIPELINE:
            return await self._execute_pipeline(tasks)
        elif strategy == OrchestrationStrategy.PRIORITY_BASED:
            return await self._execute_priority_based(tasks)
        else:  # ADAPTIVE
            return await self._execute_adaptive(tasks)

    async def _execute_sequential(self, tasks: List[ToolTask]) -> List[ToolTask]:
        """Execute tasks sequentially."""
        results = []
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)
        return results

    async def _execute_parallel(self, tasks: List[ToolTask]) -> List[ToolTask]:
        """Execute tasks in parallel."""
        # Limit concurrent tasks
        max_concurrent = self.context.max_concurrent_tools

        if len(tasks) <= max_concurrent:
            # Execute all tasks concurrently
            task_coroutines = [self.execute_task(task) for task in tasks]
            return await asyncio.gather(*task_coroutines)
        else:
            # Execute in batches
            results = []
            for i in range(0, len(tasks), max_concurrent):
                batch = tasks[i:i + max_concurrent]
                batch_coroutines = [self.execute_task(task) for task in batch]
                batch_results = await asyncio.gather(*batch_coroutines)
                results.extend(batch_results)
            return results

    async def _execute_pipeline(self, tasks: List[ToolTask]) -> List[ToolTask]:
        """Execute tasks in pipeline mode (output of one feeds into next)."""
        results = []
        previous_result = None

        for task in tasks:
            # Pass previous result as input if available
            if previous_result is not None:
                task.parameters["previous_result"] = previous_result

            result = await self.execute_task(task)
            results.append(result)
            previous_result = result.result

        return results

    async def _execute_priority_based(self, tasks: List[ToolTask]) -> List[ToolTask]:
        """Execute tasks based on priority."""
        # Sort by priority (highest first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=True)
        return await self._execute_sequential(sorted_tasks)

    async def _execute_adaptive(self, tasks: List[ToolTask]) -> List[ToolTask]:
        """Execute tasks using adaptive strategy."""
        # Simple adaptive logic: use parallel for independent tasks,
        # sequential for dependent tasks
        if all(not task.parameters.get("depends_on") for task in tasks):
            return await self._execute_parallel(tasks)
        else:
            return await self._execute_sequential(tasks)

    def get_task_status(self, task_id: str) -> Optional[ToolStatus]:
        """Get the status of a specific task."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].status

        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task.status

        return None

    def get_active_tasks(self) -> List[ToolTask]:
        """Get all currently active tasks."""
        return list(self.active_tasks.values())

    def get_completed_tasks(self) -> List[ToolTask]:
        """Get all completed tasks."""
        return self.completed_tasks.copy()

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = ToolStatus.FAILED
            task.error = "Task cancelled by user"
            task.completed_at = datetime.now(timezone.utc)

            del self.active_tasks[task_id]
            self.completed_tasks.append(task)

            return True
        return False


# Convenience functions for quick orchestration
async def quick_tool_orchestration(
    tool_functions: Dict[str, Callable],
    function_calls: List[Dict[str, Any]],
    strategy: OrchestrationStrategy = OrchestrationStrategy.PARALLEL
) -> List[ToolTask]:
    """Quick tool orchestration for simple use cases."""
    orchestrator = ToolOrchestrator()

    # Register tool
    orchestrator.register_tool("quick_tool", tool_functions)

    # Create tasks
    tasks = []
    for i, call in enumerate(function_calls):
        task = orchestrator.create_task(
            tool_name="quick_tool",
            function_name=call["function"],
            parameters=call.get("parameters", {}),
            task_id=f"quick_task_{i}"
        )
        tasks.append(task)

    # Execute
    return await orchestrator.orchestrate_tasks(tasks, strategy)


def create_orchestration_context(
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
    max_concurrent_tools: int = 5,
    **kwargs
) -> OrchestrationContext:
    """Create an orchestration context with common settings."""
    return OrchestrationContext(
        strategy=strategy,
        max_concurrent_tools=max_concurrent_tools,
        **kwargs
    )


# Export main classes and functions
__all__ = [
    "ToolOrchestrator",
    "OrchestrationStrategy",
    "ToolStatus",
    "ToolTask",
    "OrchestrationContext",
    "ExecutionPlan",
    "ToolChain",
    "quick_tool_orchestration",
    "create_orchestration_context"
]
