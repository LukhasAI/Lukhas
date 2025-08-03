"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - ORCHESTRATION
║ Main orchestrator that manages agents and plugins.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: agent_orchestrator.py
║ Path: lukhas/orchestration/agent_orchestrator.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Orchestration Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module contains the main agent orchestrator for the LUKHAS system. It is
║ responsible for managing the lifecycle of agents, coordinating plugins,
║ distributing tasks, and handling inter-agent communication.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

from .interfaces.agent_interface import (
    AgentInterface, AgentStatus, AgentContext, AgentMessage, AgentCapability
)
from .interfaces.plugin_registry import PluginRegistry, PluginStatus
from .interfaces.orchestration_protocol import (
    OrchestrationProtocol, MessageType, Priority, TaskDefinition,
    TaskResult, OrchestrationMessage, MessageBuilder
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Central orchestrator for managing agents and plugins in the LUKHAS system.

    Responsibilities:
    - Agent lifecycle management
    - Plugin coordination
    - Task distribution and load balancing
    - Inter-agent communication
    - System health monitoring
    """

    def __init__(self, orchestrator_id: str = "main_orchestrator"):
        """Initialize the orchestrator"""
        self.orchestrator_id = orchestrator_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Agent management
        self.agents: Dict[str, AgentInterface] = {}
        self.agent_capabilities: Dict[AgentCapability, Set[str]] = {}

        # Plugin management
        self.plugin_registry = PluginRegistry()

        # Communication protocol
        self.protocol = OrchestrationProtocol(orchestrator_id)

        # Task management
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Tuple[TaskDefinition, str]] = {}  # task_id -> (task, agent_id)
        self.task_results: Dict[str, TaskResult] = {}

        # System state
        self.is_running = False
        self.start_time = datetime.now()
        self._logger = logger

        # Configuration
        self.config = {
            "max_concurrent_tasks_per_agent": 5,
            "task_timeout_default": 300,  # 5 minutes
            "heartbeat_interval": 30,  # seconds
            "plugin_dirs": ["lukhas/plugins", "plugins"],
            "auto_discover_plugins": True
        }

        # Setup protocol handlers
        self._setup_protocol_handlers()

    def _setup_protocol_handlers(self) -> None:
        """Setup message handlers for the orchestration protocol"""
        self.protocol.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)
        self.protocol.register_handler(MessageType.STATUS, self._handle_status_request)
        self.protocol.register_handler(MessageType.ERROR, self._handle_error)
        self.protocol.register_handler(MessageType.TASK_COMPLETE, self._handle_task_completion)
        self.protocol.register_handler(MessageType.REGISTRATION, self._handle_registration)

    async def initialize(self) -> bool:
        """Initialize the orchestrator and all subsystems"""
        try:
            self._logger.info(f"Initializing LUKHAS Agent Orchestrator - Session: {self.session_id}")

            # Start protocol
            self.protocol.start()

            # Discover and load plugins if configured
            if self.config.get("auto_discover_plugins", True):
                await self._initialize_plugins()

            # Start background tasks
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._task_scheduler())
            asyncio.create_task(self._health_monitor())

            self.is_running = True
            self._logger.info("Orchestrator initialization complete")
            return True

        except Exception as e:
            self._logger.error(f"Orchestrator initialization failed: {e}", exc_info=True)
            return False

    async def _initialize_plugins(self) -> None:
        """Initialize the plugin system"""
        try:
            # Set plugin directories
            self.plugin_registry.plugin_dirs = self.config.get("plugin_dirs", [])

            # Discover available plugins
            discovered = self.plugin_registry.discover_plugins()
            self._logger.info(f"Discovered {len(discovered)} plugins")

            # Load core plugins
            core_plugins = ["monitoring", "logging", "metrics"]
            for plugin_name in core_plugins:
                if plugin_name in discovered:
                    await self.plugin_registry.load_plugin(plugin_name)

        except Exception as e:
            self._logger.error(f"Plugin initialization error: {e}")

    async def register_agent(self, agent: AgentInterface) -> bool:
        """
        Register an agent with the orchestrator.

        Args:
            agent: Agent instance to register

        Returns:
            bool: True if registration successful
        """
        try:
            agent_id = agent.metadata.agent_id

            if agent_id in self.agents:
                self._logger.warning(f"Agent {agent_id} already registered")
                return False

            # Create agent context
            context = AgentContext(
                orchestrator_id=self.orchestrator_id,
                session_id=self.session_id,
                memory_access=AgentCapability.MEMORY_ACCESS in agent.metadata.capabilities,
                resource_limits={
                    "max_concurrent_tasks": self.config["max_concurrent_tasks_per_agent"],
                    "max_memory_mb": 1024,
                    "max_cpu_percent": 50
                },
                shared_state={},
                active_tasks=[],
                message_queue=asyncio.Queue()
            )

            # Initialize agent
            if await agent.initialize(context):
                self.agents[agent_id] = agent

                # Update capability index
                for capability in agent.metadata.capabilities:
                    if capability not in self.agent_capabilities:
                        self.agent_capabilities[capability] = set()
                    self.agent_capabilities[capability].add(agent_id)

                # Start agent message handler
                asyncio.create_task(self._handle_agent_messages(agent))

                self._logger.info(f"Registered agent: {agent.metadata.name} ({agent_id})")

                # Broadcast registration
                await self.protocol.broadcast(
                    MessageType.REGISTRATION,
                    {
                        "agent_id": agent_id,
                        "agent_name": agent.metadata.name,
                        "capabilities": [c.value for c in agent.metadata.capabilities]
                    }
                )

                return True
            else:
                self._logger.error(f"Agent {agent_id} initialization failed")
                return False

        except Exception as e:
            self._logger.error(f"Agent registration error: {e}", exc_info=True)
            return False

    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the orchestrator.

        Args:
            agent_id: ID of agent to unregister

        Returns:
            bool: True if unregistration successful
        """
        try:
            if agent_id not in self.agents:
                self._logger.warning(f"Agent {agent_id} not registered")
                return False

            agent = self.agents[agent_id]

            # Check for active tasks
            active_agent_tasks = [
                task_id for task_id, (_, assigned_agent) in self.active_tasks.items()
                if assigned_agent == agent_id
            ]

            if active_agent_tasks:
                self._logger.warning(f"Agent {agent_id} has {len(active_agent_tasks)} active tasks")
                # TODO: Reassign or cancel tasks

            # Shutdown agent
            await agent.shutdown()

            # Remove from registry
            del self.agents[agent_id]

            # Update capability index
            for capability, agent_set in self.agent_capabilities.items():
                agent_set.discard(agent_id)

            self._logger.info(f"Unregistered agent: {agent_id}")
            return True

        except Exception as e:
            self._logger.error(f"Agent unregistration error: {e}", exc_info=True)
            return False

    async def submit_task(self, task: TaskDefinition) -> str:
        """
        Submit a task for execution.

        Args:
            task: Task definition

        Returns:
            str: Task ID
        """
        self._logger.info(f"Submitting task: {task.description}")
        # Process task directly
        agent = self.agents.get("codex")
        if agent:
            self._logger.info(f"Found agent: {agent.metadata.agent_id}")
            result = await self._execute_agent_task(agent, task)
            return task.task_id
        else:
            self._logger.error("Codex agent not registered")
            return None

    async def _task_scheduler(self) -> None:
        """Background task scheduler that assigns tasks to agents"""
        while self.is_running:
            try:
                # Get task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                # Find suitable agent
                agent_id = self._find_suitable_agent(task)

                if agent_id:
                    # Assign task to agent
                    agent = self.agents[agent_id]

                    # Update task assignment
                    task.assigned_to = agent_id
                    self.active_tasks[task.task_id] = (task, agent_id)

                    # Send task to agent
                    agent.context.active_tasks.append(task.task_id)

                    # Create task execution coroutine
                    asyncio.create_task(self._execute_agent_task(agent, task))

                    self._logger.info(f"Task {task.task_id} assigned to agent {agent_id}")
                else:
                    # No suitable agent, put back in queue
                    await self.task_queue.put(task)
                    await asyncio.sleep(1)  # Wait before retry

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"Task scheduler error: {e}", exc_info=True)

    def _find_suitable_agent(self, task: TaskDefinition) -> Optional[str]:
        """
        Find a suitable agent for the task based on requirements and load.

        Args:
            task: Task to assign

        Returns:
            Agent ID or None
        """
        suitable_agents = []

        # Check requirements
        required_capabilities = task.requirements.get("capabilities", [])

        # Find agents with required capabilities
        if required_capabilities:
            # Get agents that have all required capabilities
            candidate_sets = []
            for cap_str in required_capabilities:
                # Convert string to capability enum if needed
                try:
                    cap = AgentCapability(cap_str)
                    if cap in self.agent_capabilities:
                        candidate_sets.append(self.agent_capabilities[cap])
                except ValueError:
                    # Custom capability
                    custom_agents = {
                        agent_id for agent_id, agent in self.agents.items()
                        if agent.has_capability(cap_str)
                    }
                    candidate_sets.append(custom_agents)

            # Find intersection of all capability sets
            if candidate_sets:
                suitable_agents = list(set.intersection(*candidate_sets))
        else:
            # No specific requirements, all ready agents are suitable
            suitable_agents = [
                agent_id for agent_id, agent in self.agents.items()
                if agent.status == AgentStatus.READY and agent.metadata.agent_id == "codex"
            ]

        if not suitable_agents:
            return None

        # Select agent with lowest load
        best_agent = None
        min_load = float('inf')

        for agent_id in suitable_agents:
            agent = self.agents[agent_id]

            # Check agent status
            if agent.status not in [AgentStatus.READY, AgentStatus.ACTIVE]:
                continue

            # Check resource limits
            current_tasks = len(agent.context.active_tasks)
            max_tasks = agent.context.resource_limits.get("max_concurrent_tasks", 5)

            if current_tasks >= max_tasks:
                continue

            # Select agent with fewest active tasks
            if current_tasks < min_load:
                min_load = current_tasks
                best_agent = agent_id

        return best_agent

    async def _execute_agent_task(self, agent: AgentInterface, task: TaskDefinition) -> None:
        """Execute a task on an agent"""
        start_time = datetime.now()

        try:
            # Set timeout
            timeout = task.timeout or self.config["task_timeout_default"]

            # Execute task with timeout
            result_data = await asyncio.wait_for(
                agent.process_task(task.to_dict()),
                timeout=timeout
            )

            # Create task result
            result = TaskResult(
                task_id=task.task_id,
                status="success",
                result_data=result_data,
                execution_time=(datetime.now() - start_time).total_seconds()
            )

        except asyncio.TimeoutError:
            result = TaskResult(
                task_id=task.task_id,
                status="timeout",
                error="Task execution timed out",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
        except Exception as e:
            result = TaskResult(
                task_id=task.task_id,
                status="failure",
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )

        # Clean up
        agent.context.active_tasks.remove(task.task_id)
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]

        # Send completion message
        await self.protocol.send_message(
            MessageBuilder.task_complete(task.task_id, result)
        )

        # Notify plugins
        await self.plugin_registry.broadcast_signal({
            "type": "task_complete",
            "task_id": task.task_id,
            "agent_id": agent.metadata.agent_id,
            "result": result.to_dict()
        })

        self.task_results[task.task_id] = result

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed task."""
        return self.task_results.get(task_id)

    async def _handle_agent_messages(self, agent: AgentInterface) -> None:
        """Handle messages from an agent"""
        while agent.metadata.agent_id in self.agents:
            try:
                # Get message from agent's queue
                message = await asyncio.wait_for(
                    agent.context.message_queue.get(),
                    timeout=1.0
                )

                # Route message
                if message.recipient_id:
                    # Direct message to another agent
                    if message.recipient_id in self.agents:
                        recipient = self.agents[message.recipient_id]

                        # Handle message and get response
                        response = await recipient.handle_message(message)

                        if response and message.requires_response:
                            # Send response back
                            await agent.context.message_queue.put(response)
                    elif message.recipient_id == self.orchestrator_id:
                        # Message for orchestrator
                        await self._handle_orchestrator_message(message)
                else:
                    # Broadcast message
                    await self._broadcast_agent_message(message)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"Error handling agent message: {e}", exc_info=True)

    async def _handle_orchestrator_message(self, message: AgentMessage) -> None:
        """Handle messages directed to the orchestrator"""
        if message.message_type == "status_request":
            status = self.get_status()
            response = AgentMessage(
                sender_id=self.orchestrator_id,
                recipient_id=message.sender_id,
                message_type="status_response",
                content=status
            )
            if message.sender_id in self.agents:
                await self.agents[message.sender_id].context.message_queue.put(response)

    async def _broadcast_agent_message(self, message: AgentMessage) -> None:
        """Broadcast a message from an agent to all other agents"""
        sender_id = message.sender_id

        for agent_id, agent in self.agents.items():
            if agent_id != sender_id:
                try:
                    # Send to agent
                    await agent.handle_message(message)
                except Exception as e:
                    self._logger.error(f"Error broadcasting to agent {agent_id}: {e}")

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats"""
        interval = self.config.get("heartbeat_interval", 30)

        while self.is_running:
            try:
                # Get system status
                status = self.get_status()

                # Send heartbeat
                await self.protocol.broadcast(
                    MessageType.HEARTBEAT,
                    status,
                    Priority.LOW
                )

                await asyncio.sleep(interval)

            except Exception as e:
                self._logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(interval)

    async def _health_monitor(self) -> None:
        """Monitor system health and agent status"""
        while self.is_running:
            try:
                # Check agent health
                for agent_id, agent in list(self.agents.items()):
                    try:
                        health = await agent.get_health_status()

                        if not health.get("healthy", True):
                            self._logger.warning(f"Agent {agent_id} unhealthy: {health}")

                            # Consider unregistering if critical
                            if agent.status == AgentStatus.ERROR:
                                await self.unregister_agent(agent_id)

                    except Exception as e:
                        self._logger.error(f"Health check failed for agent {agent_id}: {e}")

                # Check plugin health
                plugin_list = self.plugin_registry.list_plugins(status=PluginStatus.ERROR)
                if plugin_list:
                    self._logger.warning(f"{len(plugin_list)} plugins in error state")

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self._logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)

    async def _handle_heartbeat(self, message: OrchestrationMessage) -> None:
        """Handle heartbeat messages"""
        # Log heartbeat from other nodes
        self._logger.debug(f"Heartbeat from {message.sender_id}: {message.payload}")

    async def _handle_status_request(self, message: OrchestrationMessage) -> None:
        """Handle status request messages"""
        status = self.get_status()

        response = OrchestrationMessage(
            message_type=MessageType.RESPONSE,
            recipient_id=message.sender_id,
            correlation_id=message.message_id,
            payload=status
        )

        await self.protocol.send_message(response)

    async def _handle_error(self, message: OrchestrationMessage) -> None:
        """Handle error messages"""
        error_info = message.payload
        self._logger.error(f"Error from {message.sender_id}: {error_info}")

        # Notify plugins
        await self.plugin_registry.broadcast_signal({
            "type": "error",
            "source": message.sender_id,
            "error": error_info
        })

    async def _handle_task_completion(self, message: OrchestrationMessage) -> None:
        """Handle task completion messages"""
        result = TaskResult(**message.payload)
        self._logger.info(f"Task {result.task_id} completed with status: {result.status}")

    async def _handle_registration(self, message: OrchestrationMessage) -> None:
        """Handle agent registration broadcasts"""
        reg_info = message.payload
        self._logger.info(f"Agent registered: {reg_info.get('agent_name')} with capabilities: {reg_info.get('capabilities')}")

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "session_id": self.session_id,
            "is_running": self.is_running,
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "agents": {
                "total": len(self.agents),
                "by_status": self._count_agents_by_status(),
                "capabilities": {
                    cap.value: len(agents)
                    for cap, agents in self.agent_capabilities.items()
                }
            },
            "tasks": {
                "queued": self.task_queue.qsize(),
                "active": len(self.active_tasks)
            },
            "plugins": {
                "loaded": len(self.plugin_registry.plugins),
                "by_status": self._count_plugins_by_status()
            },
            "protocol": self.protocol.get_statistics()
        }

    def _count_agents_by_status(self) -> Dict[str, int]:
        """Count agents by status"""
        counts = {}
        for agent in self.agents.values():
            status = agent.status.name
            counts[status] = counts.get(status, 0) + 1
        return counts

    def _count_plugins_by_status(self) -> Dict[str, int]:
        """Count plugins by status"""
        counts = {}
        for plugin in self.plugin_registry.plugins.values():
            status = plugin.status.name
            counts[status] = counts.get(status, 0) + 1
        return counts

    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator"""
        self._logger.info("Shutting down orchestrator...")
        self.is_running = False

        # Stop protocol
        self.protocol.stop()

        # Shutdown all agents
        for agent_id in list(self.agents.keys()):
            await self.unregister_agent(agent_id)

        # Unload all plugins
        for plugin_name in list(self.plugin_registry.plugins.keys()):
            await self.plugin_registry.unload_plugin(plugin_name)

        self._logger.info("Orchestrator shutdown complete")