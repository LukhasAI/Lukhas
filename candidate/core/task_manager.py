"""
LUKHAS Task Manager

Core task orchestration system for the LUKHAS symbolic AI ecosystem.
Manages agent coordination, workflow execution, and task queue processing.
"""
import asyncio
import importlib
import json
import logging
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
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
        self.config_data: dict[str, Any] = {}

        self._load_config()
        self._setup_default_queues()
        self._setup_default_agents()
        self._register_task_handlers()

    def _load_config(self) -> None:
        """Load task manager configuration."""
        logger.info("📋 Loading task manager configuration...")
        self.config_data = {"queues": {}, "agents": {}, "workflows": {}, "scheduling": {}}

        if not self.config_path.exists():
            logger.warning("Task manager config not found at %s – using defaults", self.config_path)
            return

        try:
            config_json = self.config_path.read_text(encoding="utf-8")
            loaded = json.loads(config_json)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("Failed to load task manager config: %s", exc)
            self.config_data["load_error"] = str(exc)
            return

        for key in ("queues", "agents", "workflows", "scheduling", "handlers"):
            if key in loaded and isinstance(loaded[key], dict):
                self.config_data[key] = loaded[key]

        logger.info(
            "Task manager configuration loaded",
            extra={
                "queue_count": len(self.config_data.get("queues", {})),
                "agent_count": len(self.config_data.get("agents", {})),
                "workflow_count": len(self.config_data.get("workflows", {})),
            },
        )

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
            if queue_id not in self.queues:
                self.add_queue(queue_id, queue)

        for queue_id, cfg in self.config_data.get("queues", {}).items():
            queue = self.queues.get(queue_id, TaskQueue(name=cfg.get("name", queue_id)))
            queue.max_concurrent = int(cfg.get("max_concurrent", queue.max_concurrent))
            queue.auto_start = bool(cfg.get("auto_start", queue.auto_start))
            queue.persistent = bool(cfg.get("persistent", queue.persistent))
            self.queues[queue_id] = queue
            logger.info("⚙️ Configured queue override", extra={"queue_id": queue_id, "config": cfg})

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
            if agent_id not in self.agents:
                self.register_agent(agent_id, agent)

        for agent_id, cfg in self.config_data.get("agents", {}).items():
            agent = self.agents.get(
                agent_id,
                Agent(
                    id=agent_id,
                    name=cfg.get("name", agent_id.title()),
                    capabilities=list(cfg.get("capabilities", [])),
                ),
            )
            agent.capabilities = list(cfg.get("capabilities", agent.capabilities))
            agent.max_concurrent_tasks = int(cfg.get("max_concurrent_tasks", agent.max_concurrent_tasks))
            self.agents[agent_id] = agent
            logger.info("🤖 Agent override applied", extra={"agent_id": agent_id, "capabilities": agent.capabilities})

    def _register_task_handlers(self) -> None:
        """Register task handler functions."""
        async def _load_text(path: Path) -> str:
            return await asyncio.to_thread(path.read_text, encoding="utf-8")

        async def symbol_validation_handler(task: Task) -> Any:
            """Handle symbol validation tasks."""

            logger.info("🔍 Executing symbol validation", extra={"task": task.id, "agent": task.agent_id})
            params = task.parameters or {}
            symbols: list[str] = []

            if "symbols" in params and isinstance(params["symbols"], list):
                symbols.extend(str(sym) for sym in params["symbols"])

            document = params.get("document")
            if isinstance(document, str):
                if Path(document).exists():
                    content = await _load_text(Path(document))
                else:
                    content = document
                symbols.extend(re.findall(r"#[ΛA-Z][A-Z0-9_]+", content))

            extracted = [sym.strip("# ") for sym in symbols if sym]
            if not extracted:
                return {"valid_symbols": [], "invalid_symbols": [], "duplicates": [], "driftScore": 0.0}

            counter = Counter(extracted)
            valid_pattern = re.compile(r"^[A-Z][A-Z0-9_]*$")
            valid = [sym for sym in extracted if valid_pattern.match(sym)]
            invalid = sorted({sym for sym in extracted if not valid_pattern.match(sym)})
            duplicates = sorted({sym for sym, count in counter.items() if count > 1})

            drift_score = max(0.0, 1.0 - (len(invalid) / len(extracted)))

            result = {
                "valid_symbols": sorted(set(valid)),
                "invalid_symbols": invalid,
                "duplicates": duplicates,
                "metrics": {
                    "total": len(extracted),
                    "unique": len(set(extracted)),
                    "invalid_ratio": len(invalid) / len(extracted),
                },
                "driftScore": drift_score,
            }

            logger.debug("Symbol validation result", extra=result)
            return result

        async def design_system_handler(task: Task) -> Any:
            """Handle design system tasks."""

            logger.info("🎨 Executing design system task", extra={"task": task.id})
            params = task.parameters or {}
            root = Path(params.get("design_root", "design-system"))
            asset_counts = {"json": 0, "yaml": 0, "svg": 0, "md": 0}
            latest_update = None

            if root.exists():
                for path in root.rglob("*"):
                    if not path.is_file():
                        continue
                    suffix = path.suffix.lower()
                    if suffix in {".json", ".yaml", ".yml", ".svg", ".md"}:
                        key = "yaml" if suffix in {".yaml", ".yml"} else suffix.lstrip(".")
                        asset_counts[key] = asset_counts.get(key, 0) + 1
                        timestamp = path.stat().st_mtime
                        latest_update = max(latest_update or timestamp, timestamp)

            affect_delta = float(params.get("affect_delta", 0.0))
            operations = params.get("operations", [])
            result = {
                "asset_counts": asset_counts,
                "latest_update": datetime.fromtimestamp(latest_update, tz=timezone.utc).isoformat()
                if latest_update
                else None,
                "operations": operations,
                "affect_delta": affect_delta,
            }

            logger.debug("Design system summary", extra=result)
            return result

        async def file_processing_handler(task: Task) -> Any:
            """Handle file processing tasks."""

            logger.info("📁 Executing file processing", extra={"task": task.id})
            params = task.parameters or {}
            paths = [Path(p) for p in params.get("paths", []) if isinstance(p, str)]
            processed = []
            total_size = 0

            for path in paths:
                entry = {"path": str(path), "exists": path.exists(), "size": 0}
                if path.exists() and path.is_file():
                    entry["size"] = path.stat().st_size
                    total_size += entry["size"]
                processed.append(entry)

            result = {
                "processed": processed,
                "total_size": total_size,
                "cleanup_completed": all(item["exists"] for item in processed),
            }

            logger.debug("File processing result", extra=result)
            return result

        self.task_handlers.update(
            {
                "symbol_validation": symbol_validation_handler,
                "design_system": design_system_handler,
                "file_processing": file_processing_handler,
            }
        )

        for handler_id, dotted_path in self.config_data.get("handlers", {}).items():
            try:
                module_name, func_name = dotted_path.rsplit(":", 1)
                module = importlib.import_module(module_name)
                handler = getattr(module, func_name)
            except (ValueError, ImportError, AttributeError) as exc:
                logger.error("Failed to load custom handler %s: %s", handler_id, exc)
                continue

            if asyncio.iscoroutinefunction(handler):
                self.task_handlers[handler_id] = handler
            else:
                async def _wrapper(task: Task, func=handler):
                    return await asyncio.to_thread(func, task)

                self.task_handlers[handler_id] = _wrapper


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
        task.started_at = datetime.now(timezone.utc)

        try:
            # Get handler function
            if task.handler not in self.task_handlers:
                raise ValueError(f"Unknown task handler: {task.handler}")

            handler = self.task_handlers[task.handler]

            # Execute task with timeout
            result = await asyncio.wait_for(handler(task), timeout=task.timeout)

            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
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
        pending_tasks = [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]

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
            await asyncio.gather(*[process_with_semaphore(task.id) for task in tasks_to_run])

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
            "completed_at": (task.completed_at.isoformat() if task.completed_at else None),
            "result": task.result,
            "error": task.error,
            "retry_count": task.retry_count,
        }

    def get_system_status(self) -> dict[str, Any]:
        """Get overall system status."""
        task_counts = {}
        for status in TaskStatus:
            task_counts[status.value] = len([t for t in self.tasks.values() if t.status == status])

        agent_status = {
            agent_id: {
                "name": agent.name,
                "status": agent.status,
                "capabilities": agent.capabilities,
                "active_tasks": len(
                    [t for t in self.tasks.values() if t.agent_id == agent_id and t.status == TaskStatus.RUNNING]
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
            "system_uptime": datetime.now(timezone.utc).isoformat(),
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
