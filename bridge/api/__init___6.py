"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


LUKHAS Orchestration Interfaces
===============================

Core interfaces for the LUKHAS orchestration system, providing:
- Agent interface definitions
- Plugin registry and management
- Communication protocols
- Lifecycle management

ΛTAG: orchestration, interfaces, agent, plugin
"""

from .agent_interface import (
    AgentInterface,
    AgentMetadata,
    AgentCapability,
    AgentStatus,
    AgentMessage,
    AgentContext
)

from .plugin_registry import (
    PluginRegistry,
    PluginMetadata,
    PluginType,
    PluginStatus,
    PluginDependency
)

from .orchestration_protocol import (
    OrchestrationProtocol,
    MessageType,
    Priority,
    TaskDefinition,
    TaskResult
)

__all__ = [
    # Agent interface
    'AgentInterface',
    'AgentMetadata', 
    'AgentCapability',
    'AgentStatus',
    'AgentMessage',
    'AgentContext',
    
    # Plugin registry
    'PluginRegistry',
    'PluginMetadata',
    'PluginType',
    'PluginStatus',
    'PluginDependency',
    
    # Orchestration protocol
    'OrchestrationProtocol',
    'MessageType',
    'Priority',
    'TaskDefinition',
    'TaskResult'
]