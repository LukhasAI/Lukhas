"""
LUKHAS Agent Interface
=====================

Defines the core interface for all LUKHAS orchestration agents.
This provides a standardized way for agents to interact with the
orchestration system while maintaining modularity and extensibility.

ΛTAG: agent, interface, orchestration
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Set, Callable, Union
from datetime import datetime
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle states"""
    INITIALIZING = auto()
    READY = auto()
    ACTIVE = auto()
    PROCESSING = auto()
    PAUSED = auto()
    ERROR = auto()
    SHUTTING_DOWN = auto()
    TERMINATED = auto()


class AgentCapability(Enum):
    """Standard agent capabilities"""
    # Core capabilities
    TASK_PROCESSING = "task_processing"
    MEMORY_ACCESS = "memory_access"
    LEARNING = "learning"
    REASONING = "reasoning"
    
    # Communication capabilities
    INTER_AGENT_COMM = "inter_agent_communication"
    BROADCAST = "broadcast"
    SUBSCRIBE = "subscribe"
    
    # System capabilities
    RESOURCE_MANAGEMENT = "resource_management"
    ERROR_RECOVERY = "error_recovery"
    SELF_MONITORING = "self_monitoring"
    
    # Specialized capabilities
    QUANTUM_PROCESSING = "quantum_processing"
    DREAM_SYNTHESIS = "dream_synthesis"
    ETHICAL_REASONING = "ethical_reasoning"
    SYMBOLIC_PROCESSING = "symbolic_processing"


@dataclass
class AgentMetadata:
    """Metadata describing an agent"""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = "LUKHAS Team"
    created_at: datetime = field(default_factory=datetime.now)
    capabilities: Set[AgentCapability] = field(default_factory=set)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: Optional[str] = None  # None for broadcast
    message_type: str = "info"
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0  # Higher is more important
    requires_response: bool = False


@dataclass 
class AgentContext:
    """Runtime context for agent execution"""
    orchestrator_id: str
    session_id: str
    memory_access: bool = False
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    active_tasks: List[str] = field(default_factory=list)
    message_queue: asyncio.Queue = field(default_factory=asyncio.Queue)


class AgentInterface(ABC):
    """
    Abstract base class for all LUKHAS orchestration agents.
    
    This interface defines the contract that all agents must implement
    to participate in the orchestration system.
    """
    
    def __init__(self, metadata: Optional[AgentMetadata] = None):
        """Initialize the agent with metadata"""
        self.metadata = metadata or AgentMetadata()
        self.status = AgentStatus.INITIALIZING
        self.context: Optional[AgentContext] = None
        self._message_handlers: Dict[str, Callable] = {}
        self._lifecycle_hooks: Dict[str, List[Callable]] = {
            'pre_init': [],
            'post_init': [],
            'pre_process': [],
            'post_process': [],
            'pre_shutdown': [],
            'post_shutdown': []
        }
        self._logger = logging.getLogger(f"{self.__class__.__name__}.{self.metadata.agent_id[:8]}")
    
    # Abstract methods that must be implemented
    
    @abstractmethod
    async def initialize(self, context: AgentContext) -> bool:
        """
        Initialize the agent with the given context.
        
        Args:
            context: Runtime context from the orchestrator
            
        Returns:
            bool: True if initialization successful
        """
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task assigned by the orchestrator.
        
        Args:
            task: Task definition with type, parameters, etc.
            
        Returns:
            Dict containing task results and metadata
        """
        pass
    
    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle an incoming message from another agent or the orchestrator.
        
        Args:
            message: Incoming message
            
        Returns:
            Optional response message
        """
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health and performance metrics.
        
        Returns:
            Dict containing health metrics
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the agent.
        """
        pass
    
    # Common functionality provided by the interface
    
    def register_capability(self, capability: Union[AgentCapability, str]) -> None:
        """Register a capability for this agent"""
        if isinstance(capability, str):
            # Custom capability
            self.metadata.tags.append(f"capability:{capability}")
        else:
            self.metadata.capabilities.add(capability)
    
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type"""
        self._message_handlers[message_type] = handler
        self._logger.info(f"Registered handler for message type: {message_type}")
    
    def add_lifecycle_hook(self, phase: str, hook: Callable) -> None:
        """Add a lifecycle hook for the specified phase"""
        if phase in self._lifecycle_hooks:
            self._lifecycle_hooks[phase].append(hook)
            self._logger.info(f"Added lifecycle hook for phase: {phase}")
        else:
            raise ValueError(f"Unknown lifecycle phase: {phase}")
    
    async def execute_lifecycle_hooks(self, phase: str) -> None:
        """Execute all hooks for a given lifecycle phase"""
        hooks = self._lifecycle_hooks.get(phase, [])
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(self)
                else:
                    hook(self)
            except Exception as e:
                self._logger.error(f"Error in lifecycle hook {phase}: {e}")
    
    async def send_message(self, recipient_id: Optional[str], content: Any, 
                          message_type: str = "info", priority: int = 0,
                          requires_response: bool = False) -> str:
        """
        Send a message to another agent or broadcast.
        
        Args:
            recipient_id: Target agent ID or None for broadcast
            content: Message content
            message_type: Type of message
            priority: Message priority
            requires_response: Whether a response is expected
            
        Returns:
            str: Message ID
        """
        message = AgentMessage(
            sender_id=self.metadata.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            priority=priority,
            requires_response=requires_response
        )
        
        if self.context and self.context.message_queue:
            await self.context.message_queue.put(message)
            self._logger.debug(f"Sent message {message.message_id} to {recipient_id or 'all'}")
        
        return message.message_id
    
    async def broadcast(self, content: Any, message_type: str = "info", priority: int = 0) -> str:
        """Broadcast a message to all agents"""
        return await self.send_message(None, content, message_type, priority)
    
    def update_status(self, new_status: AgentStatus) -> None:
        """Update agent status and log the change"""
        old_status = self.status
        self.status = new_status
        self._logger.info(f"Status changed: {old_status.name} -> {new_status.name}")
    
    def has_capability(self, capability: Union[AgentCapability, str]) -> bool:
        """Check if agent has a specific capability"""
        if isinstance(capability, AgentCapability):
            return capability in self.metadata.capabilities
        else:
            return f"capability:{capability}" in self.metadata.tags
    
    async def handle_error(self, error: Exception, context: str = "") -> None:
        """Standard error handling"""
        self._logger.error(f"Error in {context}: {error}", exc_info=True)
        self.update_status(AgentStatus.ERROR)
        
        # Send error notification
        await self.send_message(
            self.context.orchestrator_id if self.context else None,
            {
                "error": str(error),
                "context": context,
                "agent_id": self.metadata.agent_id,
                "timestamp": datetime.now().isoformat()
            },
            message_type="error",
            priority=10
        )
    
    def get_metadata_dict(self) -> Dict[str, Any]:
        """Get agent metadata as dictionary"""
        return {
            "agent_id": self.metadata.agent_id,
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "created_at": self.metadata.created_at.isoformat(),
            "capabilities": [c.value for c in self.metadata.capabilities],
            "dependencies": self.metadata.dependencies,
            "tags": self.metadata.tags,
            "status": self.status.name
        }


class SimpleAgent(AgentInterface):
    """
    Example implementation of a simple agent.
    
    This serves as a template for creating new agents.
    """
    
    def __init__(self, name: str = "SimpleAgent"):
        metadata = AgentMetadata(
            name=name,
            description="A simple example agent",
            version="1.0.0"
        )
        super().__init__(metadata)
        
        # Register basic capabilities
        self.register_capability(AgentCapability.TASK_PROCESSING)
        self.register_capability(AgentCapability.INTER_AGENT_COMM)
    
    async def initialize(self, context: AgentContext) -> bool:
        """Initialize the agent"""
        try:
            await self.execute_lifecycle_hooks('pre_init')
            
            self.context = context
            self.update_status(AgentStatus.READY)
            
            await self.execute_lifecycle_hooks('post_init')
            return True
            
        except Exception as e:
            await self.handle_error(e, "initialization")
            return False
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task"""
        try:
            await self.execute_lifecycle_hooks('pre_process')
            self.update_status(AgentStatus.PROCESSING)
            
            # Simple task processing
            task_type = task.get('type', 'unknown')
            result = {
                'status': 'completed',
                'task_id': task.get('task_id', 'unknown'),
                'result': f"Processed {task_type} task",
                'timestamp': datetime.now().isoformat()
            }
            
            self.update_status(AgentStatus.ACTIVE)
            await self.execute_lifecycle_hooks('post_process')
            
            return result
            
        except Exception as e:
            await self.handle_error(e, "task processing")
            return {
                'status': 'error',
                'error': str(e),
                'task_id': task.get('task_id', 'unknown')
            }
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages"""
        try:
            # Check for registered handlers
            handler = self._message_handlers.get(message.message_type)
            if handler:
                return await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
            
            # Default handling
            self._logger.info(f"Received message {message.message_id} of type {message.message_type}")
            
            if message.requires_response:
                return AgentMessage(
                    sender_id=self.metadata.agent_id,
                    recipient_id=message.sender_id,
                    message_type="response",
                    content={"acknowledged": True, "original_message_id": message.message_id}
                )
            
            return None
            
        except Exception as e:
            await self.handle_error(e, "message handling")
            return None
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            'status': self.status.name,
            'agent_id': self.metadata.agent_id,
            'uptime': (datetime.now() - self.metadata.created_at).total_seconds(),
            'active_tasks': len(self.context.active_tasks) if self.context else 0,
            'capabilities': [c.value for c in self.metadata.capabilities],
            'healthy': self.status not in [AgentStatus.ERROR, AgentStatus.TERMINATED]
        }
    
    async def shutdown(self) -> None:
        """Shutdown the agent"""
        try:
            await self.execute_lifecycle_hooks('pre_shutdown')
            self.update_status(AgentStatus.SHUTTING_DOWN)
            
            # Cleanup tasks
            if self.context:
                # Clear message queue
                while not self.context.message_queue.empty():
                    try:
                        self.context.message_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
            
            self.update_status(AgentStatus.TERMINATED)
            await self.execute_lifecycle_hooks('post_shutdown')
            
        except Exception as e:
            self._logger.error(f"Error during shutdown: {e}")