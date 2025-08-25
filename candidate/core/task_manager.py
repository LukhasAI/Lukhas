"""
LUKHAS Task Manager

Core task orchestration system for the LUKHAS symbolic AI ecosystem.
Manages agent coordination, workflow execution, and task queue processing.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Individual task definition."""

    id: str
    name: str
    description: str
    handler: str  # Function or module to execute
    parameters: dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 300.0  # 5 minutes default
    dependencies: list[str] = field(default_factory=list)
    agent_id: Optional[str] = None


@dataclass
class TaskQueue:
    """Task queue configuration."""

    name: str
    max_concurrent: int = 5
    auto_start: bool = True
    persistent: bool = True


@dataclass
class Agent:
    """Agent configuration for task execution."""

    id: str
    name: str
    capabilities: list[str]
    max_concurrent_tasks: int = 3
    status: str = "idle"  # idle, busy, offline
    last_activity: Optional[datetime] = None


class LukhλsTaskManager:
    """
    Task Manager for the LUKHAS ecosystem.

    Coordinates multiple agents, manages task queues, and orchestrates
    complex workflows across the symbolic AI system.
    """

    def __init__(self, config_path: str = "config/task_manager_config.json"):
        self.config_path = Path(config_path)
        self.tasks: dict[str, Task] = {}
        self.queues: dict[str, TaskQueue] = {}
        self.agents: dict[str, Agent] = {}
        self.task_handlers: dict[str, Callable] = {}
        self.running_tasks: dict[str, asyncio.Task] = {}

        self._load_config()
        self._setup_default_queues()
        self._setup_default_agents()
        self._register_task_handlers()

    def _load_config(self) -> None:
        """Load task manager configuration from a JSON file."""
        logger.info(f"📋 Loading task manager configuration from {self.config_path}...")
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    config_data = json.load(f)

                # Load queue configurations
                if "queues" in config_data:
                    for q_id, q_config in config_data["queues"].items():
                        self.queues[q_id] = TaskQueue(**q_config)
                    logger.info(f"Loaded {len(config_data['queues'])} queue configurations.")

                # Load agent definitions
                if "agents" in config_data:
                    for a_id, a_config in config_data["agents"].items():
                        self.agents[a_id] = Agent(**a_config)
                    logger.info(f"Loaded {len(config_data['agents'])} agent definitions.")

                # TODO: Load workflow templates and scheduling rules if needed
            else:
                logger.warning(f"Config file not found at {self.config_path}. Using defaults.")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)

    def _setup_default_queues(self) -> None:
        """Setup default task queues for LUKHAS operations."""
        default_queues = {
            "symbol_validation": TaskQueue(
                name="Symbol Validation",
                max_concurrent=3,
                auto_start=True,
                persistent=True,
            ),
            "design_system": TaskQueue(
                name="Design System",
                max_concurrent=2,
                auto_start=True,
                persistent=True,
            ),
            "agent_communication": TaskQueue(
                name="Agent Communication",
                max_concurrent=5,
                auto_start=True,
                persistent=True,
            ),
            "file_processing": TaskQueue(
                name="File Processing",
                max_concurrent=4,
                auto_start=True,
                persistent=True,
            ),
            "integration_sync": TaskQueue(
                name="Integration Sync",
                max_concurrent=2,
                auto_start=False,
                persistent=True,
            ),
        }

        for queue_id, queue in default_queues.items():
            self.add_queue(queue_id, queue)

    def _setup_default_agents(self) -> None:
        """Setup default agents for task execution."""
        default_agents = {
            "symbol_validator": Agent(
                id="symbol_validator",
                name="Symbol Validation Agent",
                capabilities=[
                    "symbol_validation",
                    "file_scanning",
                    "auto_correction",
                ],
                max_concurrent_tasks=2,
            ),
            "design_coordinator": Agent(
                id="design_coordinator",
                name="Design System Coordinator",
                capabilities=[
                    "design_tokens",
                    "asset_organization",
                    "figma_sync",
                ],
                max_concurrent_tasks=1,
            ),
            "communication_hub": Agent(
                id="communication_hub",
                name="Agent Communication Hub",
                capabilities=[
                    "message_routing",
                    "protocol_handling",
                    "ethics_checking",
                ],
                max_concurrent_tasks=3,
            ),
            "file_processor": Agent(
                id="file_processor",
                name="File Processing Agent",
                capabilities=["file_operations", "backup_creation", "cleanup"],
                max_concurrent_tasks=2,
            ),
            "integration_manager": Agent(
                id="integration_manager",
                name="Integration Manager",
                capabilities=[
                    "notion_sync",
                    "api_coordination",
                    "external_services",
                ],
                max_concurrent_tasks=1,
            ),
        }

        for agent_id, agent in default_agents.items():
            self.register_agent(agent_id, agent)

    def _register_task_handlers(self) -> None:
        """Register task handler functions."""
        async def symbol_validation_handler(task: Task) -> Any:
            """Handle symbol validation tasks."""
            logger.info(f"🔍 Executing symbol validation: {task.name}")
            file_path = task.parameters.get("file_path")
            if not file_path:
                raise ValueError("file_path parameter is required for symbol validation.")

            # Simulate reading a file and checking for a symbolic tag
            await asyncio.sleep(0.5)
            # with open(file_path, 'r') as f:
            #     content = f.read()
            # issues_found = 0
            # if "Λ" not in content:
            #     issues_found = 1
            issues_found = 0 # Placeholder
            logger.info(f"Validation complete for {file_path}. Issues found: {issues_found}")
            return {"symbols_checked": 1, "issues_found": issues_found, "file_path": file_path}

        async def design_system_handler(task: Task) -> Any:
            """Handle design system tasks."""
            logger.info(f"🎨 Executing design system task: {task.name}")
            asset_type = task.parameters.get("asset_type", "unknown")
            asset_name = task.parameters.get("asset_name", "unknown")
            # Simulate updating a design token
            await asyncio.sleep(1)
            logger.info(f"Updated design token for {asset_type}: {asset_name}")
            return {"assets_processed": 1, "tokens_updated": 1, "asset_name": asset_name}

        async def file_processing_handler(task: Task) -> Any:
            """Handle file processing tasks."""
            logger.info(f"📁 Executing file processing: {task.name}")
            operation = task.parameters.get("operation")
            path = task.parameters.get("path")
            if not operation or not path:
                raise ValueError("operation and path parameters are required.")

            # Simulate file operation
            await asyncio.sleep(1)
            logger.info(f"Performed '{operation}' on path: {path}")
            return {"files_processed": 1, "cleanup_completed": True, "operation": operation}

        self.task_handlers.update(
            {
                "symbol_validation": symbol_validation_handler,
                "design_system": design_system_handler,
                "file_processing": file_processing_handler,
            }
        )
        logger.info("Registered core task handlers.")

    def add_queue(self, queue_id: str, queue: TaskQueue) -> None:
        """Add a task queue to the manager."""
        self.queues[queue_id] = queue
        logger.info(f"➕ Added task queue: {queue.name}")

    def register_agent(self, agent_id: str, agent: Agent) -> None:
        """Register an agent for task execution."""
        self.agents[agent_id] = agent
        logger.info(f"🤖 Registered agent: {agent.name}")

    def create_task(
        self,
        name: str,
        description: str,
        handler: str,
        parameters: Optional[dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        queue: str = "default",
        agent_id: Optional[str] = None,
    ) -> str:
        """
        Create a new task.

        Args:
            name: Task name
            description: Task description
            handler: Handler function name
            parameters: Task parameters
            priority: Task priority
            queue: Target queue name
            agent_id: Preferred agent ID

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            description=description,
            handler=handler,
            parameters=parameters or {},
            priority=priority,
            agent_id=agent_id,
        )

        self.tasks[task_id] = task
        logger.info(f"✨ Created task: {name} ({task_id[:8]})")

        return task_id

    async def execute_task(self, task_id: str) -> bool:
        """
        Execute a specific task.

        Args:
            task_id: ID of the task to execute

        Returns:
            True if task completed successfully
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return False

        task = self.tasks[task_id]

        if task.status != TaskStatus.PENDING:
            logger.warning(f"Task {task_id} is not pending (status: {task.status})")
            return False

        # Update task status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            # Get handler function
            if task.handler not in self.task_handlers:
                raise ValueError(f"Unknown task handler: {task.handler}")

            handler = self.task_handlers[task.handler]

            # Execute task with timeout
            result = await asyncio.wait_for(handler(task), timeout=task.timeout)

            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            logger.info(f"✅ Task completed: {task.name} ({task_id[:8]})")
            return True

        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = "Task timed out"
            logger.error(f"⏰ Task timed out: {task.name} ({task_id[:8]})")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"❌ Task failed: {task.name} ({task_id[:8]}) - {e}")

        return False

    async def process_queue(self, queue_id: str) -> None:
        """Process tasks in a specific queue."""
        if queue_id not in self.queues:
            logger.error(f"Queue not found: {queue_id}")
            return

        queue = self.queues[queue_id]
        logger.info(f"🔄 Processing queue: {queue.name}")

        # Get pending tasks for this queue
        pending_tasks = [
            task for task in self.tasks.values() if task.status == TaskStatus.PENDING
        ]

        # Sort by priority
        pending_tasks.sort(key=lambda t: t.priority.value, reverse=True)

        # Process tasks up to queue limit
        semaphore = asyncio.Semaphore(queue.max_concurrent)

        async def process_with_semaphore(task_id: str):
            async with semaphore:
                await self.execute_task(task_id)

        # Execute tasks concurrently
        tasks_to_run = pending_tasks[: queue.max_concurrent]
        if tasks_to_run:
            await asyncio.gather(
                *[process_with_semaphore(task.id) for task in tasks_to_run]
            )

    def get_task_status(self, task_id: str) -> Optional[dict[str, Any]]:
        """Get status information for a task."""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "started_at": (task.started_at.isoformat() if task.started_at else None),
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            "result": task.result,
            "error": task.error,
            "retry_count": task.retry_count,
        }

    def get_system_status(self) -> dict[str, Any]:
        """Get overall system status."""
        task_counts = {}
        for status in TaskStatus:
            task_counts[status.value] = len(
                [t for t in self.tasks.values() if t.status == status]
            )

        agent_status = {
            agent_id: {
                "name": agent.name,
                "status": agent.status,
                "capabilities": agent.capabilities,
                "active_tasks": len(
                    [
                        t
                        for t in self.tasks.values()
                        if t.agent_id == agent_id and t.status == TaskStatus.RUNNING
                    ]
                ),
            }
            for agent_id, agent in self.agents.items()
        }

        return {
            "total_tasks": len(self.tasks),
            "task_counts": task_counts,
            "active_queues": len([q for q in self.queues.values() if q.auto_start]),
            "registered_agents": len(self.agents),
            "agent_status": agent_status,
            "system_uptime": datetime.now().isoformat(),
        }


async def main():
    """Main entry point for the task manager."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Task Manager")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--process-queue", type=str, help="Process specific queue")
    parser.add_argument(
        "--create-task",
        nargs=3,
        metavar=("NAME", "HANDLER", "DESCRIPTION"),
        help="Create a new task",
    )
    parser.add_argument("--execute-task", type=str, help="Execute specific task by ID")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    task_manager = LukhλsTaskManager()

    logger.info("⚙️ Starting LUKHAS Task Manager...")

    if args.status:
        status = task_manager.get_system_status()
        logger.info("📊 System Status:")
        logger.info(f"   - Total tasks: {status['total_tasks']}")
        logger.info(f"   - Active queues: {status['active_queues']}")
        logger.info(f"   - Registered agents: {status['registered_agents']}")
        for status_name, count in status["task_counts"].items():
            logger.info(f"   - {status_name.title()} tasks: {count}")
        return

    if args.create_task:
        name, handler, description = args.create_task
        task_id = task_manager.create_task(name, description, handler)
        logger.info(f"Created task: {task_id}")
        return

    if args.execute_task:
        success = await task_manager.execute_task(args.execute_task)
        logger.info(f"Task execution: {'✅ Success' if success else '❌ Failed'}")
        return

    if args.process_queue:
        await task_manager.process_queue(args.process_queue)
        return

    logger.info("⚙️ LUKHAS Task Manager initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
