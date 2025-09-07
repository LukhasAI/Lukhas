"""
LUKHAS AI Colony System - Base Infrastructure
Core interfaces and management for agent colonies
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
import streamlit as st
from datetime import timezone

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ColonyRole(Enum):
    """Standard colony roles"""

    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    GUARDIAN = "guardian"
    ORCHESTRATOR = "orchestrator"


class ColonyStatus(Enum):
    """Colony operational status"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class ColonyAgent:
    """Individual agent within a colony"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: ColonyRole = ColonyRole.WORKER
    capabilities: list[str] = field(default_factory=list)
    status: ColonyStatus = ColonyStatus.INITIALIZING
    load: float = 0.0  # 0.0 to 1.0
    last_active: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ColonyTask:
    """Task for colony processing"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    payload: Any = None
    priority: int = 5  # 1-10, 10 = highest
    required_capabilities: list[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"  # pending, assigned, processing, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None


class BaseColony(ABC):
    """Base class for all LUKHAS AI colonies"""

    def __init__(self, name: str, max_agents: int = 10):
        self.name = name
        self.max_agents = max_agents
        self.agents: dict[str, ColonyAgent] = {}
        self.task_queue: list[ColonyTask] = []
        self.completed_tasks: dict[str, ColonyTask] = {}
        self.status = ColonyStatus.INITIALIZING
        self.trinity_aligned = True
        self.created_at = datetime.now(timezone.utc)
        self._initialize_colony()

    def _initialize_colony(self):
        """Initialize colony with default agents"""
        # Create coordinator agent
        coordinator = ColonyAgent(
            role=ColonyRole.COORDINATOR,
            capabilities=["coordinate", "delegate", "monitor"],
            status=ColonyStatus.ACTIVE,
        )
        self.agents[coordinator.id] = coordinator

        # Create default workers
        for _i in range(min(3, self.max_agents - 1)):
            worker = ColonyAgent(
                role=ColonyRole.WORKER,
                capabilities=self.get_default_capabilities(),
                status=ColonyStatus.ACTIVE,
            )
            self.agents[worker.id] = worker

        self.status = ColonyStatus.ACTIVE

    @abstractmethod
    def get_default_capabilities(self) -> list[str]:
        """Get default capabilities for this colony type"""
        pass

    @abstractmethod
    def process_task(self, task: ColonyTask) -> Any:
        """Process a task within this colony"""
        pass

    def submit_task(
        self,
        task_type: str,
        payload: Any,
        priority: int = 5,
        required_capabilities: Optional[list[str]] = None,
    ) -> ColonyTask:
        """Submit a task to the colony"""
        task = ColonyTask(
            task_type=task_type,
            payload=payload,
            priority=priority,
            required_capabilities=required_capabilities or [],
        )

        # Insert task in priority order
        inserted = False
        for i, existing_task in enumerate(self.task_queue):
            if task.priority > existing_task.priority:
                self.task_queue.insert(i, task)
                inserted = True
                break

        if not inserted:
            self.task_queue.append(task)

        return task

    def assign_task(self, task: ColonyTask) -> Optional[str]:
        """Assign task to best available agent"""
        suitable_agents = []

        for agent in self.agents.values():
            if (
                agent.status == ColonyStatus.ACTIVE
                and agent.load < 0.8
                and all(cap in agent.capabilities for cap in task.required_capabilities)
            ):
                suitable_agents.append(agent)

        if not suitable_agents:
            return None

        # Choose agent with lowest load
        best_agent = min(suitable_agents, key=lambda a: a.load)
        task.assigned_agent = best_agent.id
        task.status = "assigned"
        best_agent.load += 0.2  # Increase load

        return best_agent.id

    def process_queue(self) -> dict[str, Any]:
        """Process pending tasks in queue"""
        processed = 0
        failed = 0

        while self.task_queue and processed < 10:  # Limit per cycle
            task = self.task_queue.pop(0)

            # Assign if not already assigned
            if not task.assigned_agent and not self.assign_task(task):
                # No available agents, put back at front
                self.task_queue.insert(0, task)
                break

            try:
                task.status = "processing"
                task.result = self.process_task(task)
                task.status = "completed"
                task.completed_at = datetime.now(timezone.utc)

                # Reduce agent load
                if task.assigned_agent and task.assigned_agent in self.agents:
                    self.agents[task.assigned_agent].load = max(0, self.agents[task.assigned_agent].load - 0.2)

                self.completed_tasks[task.id] = task
                processed += 1

            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                task.completed_at = datetime.now(timezone.utc)
                failed += 1

                # Reduce agent load even on failure
                if task.assigned_agent and task.assigned_agent in self.agents:
                    self.agents[task.assigned_agent].load = max(0, self.agents[task.assigned_agent].load - 0.2)

        return {
            "processed": processed,
            "failed": failed,
            "queue_remaining": len(self.task_queue),
            "active_agents": len([a for a in self.agents.values() if a.status == ColonyStatus.ACTIVE]),
        }

    def get_status(self) -> dict[str, Any]:
        """Get colony status"""
        return {
            "name": self.name,
            "status": self.status.value,
            "agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == ColonyStatus.ACTIVE]),
            "queue_size": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "trinity_aligned": self.trinity_aligned,
            "uptime": (datetime.now(timezone.utc) - self.created_at).total_seconds(),
        }

    def trinity_sync(self) -> dict[str, Any]:
        """Synchronize with Trinity Framework"""
        return {
            "identity": "⚛️",
            "consciousness": "🧠",
            "guardian": "🛡️",
            "colony": self.name,
            "status": "synchronized",
        }

    def add_agent(
        self,
        capabilities: Optional[list[str]] = None,
        role: ColonyRole = ColonyRole.WORKER,
    ) -> ColonyAgent:
        """Add new agent to colony"""
        if len(self.agents) >= self.max_agents:
            raise ValueError(f"Colony {self.name} at maximum capacity ({self.max_agents})")

        agent = ColonyAgent(
            role=role,
            capabilities=capabilities or self.get_default_capabilities(),
            status=ColonyStatus.ACTIVE,
        )

        self.agents[agent.id] = agent
        return agent

    def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from colony"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.role == ColonyRole.COORDINATOR:
                # Don't remove coordinator unless replacing
                coordinators = [a for a in self.agents.values() if a.role == ColonyRole.COORDINATOR]
                if len(coordinators) <= 1:
                    return False

            del self.agents[agent_id]
            return True
        return False


class ColonyRegistry:
    """Registry for managing all colonies"""

    def __init__(self):
        self.colonies: dict[str, BaseColony] = {}
        self.task_routes: dict[str, str] = {}  # task_type -> colony_name

    def register_colony(self, colony: BaseColony):
        """Register a colony"""
        self.colonies[colony.name] = colony

    def unregister_colony(self, colony_name: str) -> bool:
        """Unregister a colony"""
        if colony_name in self.colonies:
            del self.colonies[colony_name]
            # Remove task routes
            self.task_routes = {k: v for k, v in self.task_routes.items() if v != colony_name}
            return True
        return False

    def add_task_route(self, task_type: str, colony_name: str):
        """Route specific task types to colonies"""
        if colony_name in self.colonies:
            self.task_routes[task_type] = colony_name

    def submit_task(self, task_type: str, payload: Any, priority: int = 5) -> Optional[ColonyTask]:
        """Submit task to appropriate colony"""
        colony_name = self.task_routes.get(task_type)

        if colony_name and colony_name in self.colonies:
            return self.colonies[colony_name].submit_task(task_type, payload, priority)

        # No specific route, try first available colony
        for colony in self.colonies.values():
            if colony.status == ColonyStatus.ACTIVE:
                return colony.submit_task(task_type, payload, priority)

        return None

    def get_colony(self, name: str) -> Optional[BaseColony]:
        """Get colony by name"""
        return self.colonies.get(name)

    def get_all_colonies(self) -> dict[str, BaseColony]:
        """Get all registered colonies"""
        return self.colonies.copy()

    def process_all_queues(self) -> dict[str, Any]:
        """Process queues for all active colonies"""
        results = {}

        for name, colony in self.colonies.items():
            if colony.status == ColonyStatus.ACTIVE:
                results[name] = colony.process_queue()

        return results

    def get_system_status(self) -> dict[str, Any]:
        """Get overall colony system status"""
        total_agents = sum(len(c.agents) for c in self.colonies.values())
        total_tasks = sum(len(c.task_queue) for c in self.colonies.values())
        active_colonies = len([c for c in self.colonies.values() if c.status == ColonyStatus.ACTIVE])

        return {
            "total_colonies": len(self.colonies),
            "active_colonies": active_colonies,
            "total_agents": total_agents,
            "pending_tasks": total_tasks,
            "task_routes": len(self.task_routes),
            "trinity_aligned": True,
        }


# Global registry singleton
_colony_registry = None


def get_colony_registry() -> ColonyRegistry:
    """Get or create global colony registry"""
    global _colony_registry
    if _colony_registry is None:
        _colony_registry = ColonyRegistry()
    return _colony_registry
