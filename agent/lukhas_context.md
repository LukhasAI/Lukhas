# Agent Module Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*


**Module**: agent
**Purpose**: Real LUKHAS agents for internal consciousness operations
**Lane**: L2 (Integration)
**Language**: Python
**Last Updated**: 2025-10-02

---

## Module Overview

The agent module provides real LUKHAS agents for internal consciousness operations, including collaborative agents, intelligence bridges, and agent interface systems.

### Key Components
- **Collaborative Agents**: Multi-agent collaboration systems
- **Intelligence Bridge**: Bridge between intelligence systems
- **Agent Interfaces**: Standardized agent communication interfaces
- **Agent System Status**: System-wide agent health and status monitoring

### Constellation Framework Integration
- **🧠 Flow Star (Consciousness)**: Consciousness-driven agent operations
- **⚛️ Anchor Star (Identity)**: Agent identity and authentication
- **🛡️ Watch Star (Guardian)**: Agent ethics and behavior monitoring

---

## Architecture

### Core Agent Components

#### Entrypoints (from manifest)
```python
from agent import (
    get_agent_system_status,         # Get system-wide agent status
)

from agent.collaborative import is_available as collaborative_available
from agent.intelligence_bridge import is_available as intelligence_bridge_available
from agent.interfaces import is_available as interfaces_available
```

---

## Agent Systems

### 1. Collaborative Agents
**Module**: `agent.collaborative`
**Purpose**: Multi-agent collaboration and coordination
**Availability Check**: `agent.collaborative.is_available`

```python
from agent.collaborative import is_available

if is_available:
    # Use collaborative agent features
    pass
```

### 2. Intelligence Bridge
**Module**: `agent.intelligence_bridge`
**Purpose**: Bridge between intelligence systems and agents
**Availability Check**: `agent.intelligence_bridge.is_available`

```python
from agent.intelligence_bridge import is_available

if is_available:
    # Use intelligence bridge features
    pass
```

### 3. Agent Interfaces
**Module**: `agent.interfaces`
**Purpose**: Standardized agent communication interfaces
**Availability Check**: `agent.interfaces.is_available`

```python
from agent.interfaces import is_available

if is_available:
    # Use agent interface features
    pass
```

---

## System Status

### Agent System Status
```python
from agent import get_agent_system_status

status = get_agent_system_status()
# Returns:
# {
#   'collaborative': {'available': bool, 'active_agents': int},
#   'intelligence_bridge': {'available': bool, 'connections': int},
#   'interfaces': {'available': bool, 'registered_interfaces': int}
# }
```

---

## Development Guidelines

### 1. Availability Checks
Always check availability before using agent features:
```python
from agent.collaborative import is_available

if is_available:
    # Use features
    pass
else:
    # Handle unavailable case
    pass
```

### 2. Agent Identity
- All agents must have valid ΛID identity
- Agent operations logged for audit trail
- Guardian system validates agent behavior

### 3. Testing
- Unit tests for individual agent components
- Integration tests for multi-agent scenarios
- Behavior tests for ethics compliance

---

## MATRIZ Pipeline Integration

This module operates within the MATRIZ cognitive framework:

- **M (Memory)**: Agent memory and state management
- **A (Attention)**: Agent task focus and prioritization
- **T (Thought)**: Agent decision making and reasoning
- **R (Risk)**: Ethics validation for agent operations
- **I (Intent)**: Agent goal and intention tracking
- **A (Action)**: Agent action execution and monitoring

---

## Related Modules

- **Consciousness** ([../consciousness/](../consciousness/)) - Consciousness operations
- **Identity** ([../identity/](../identity/)) - Agent identity and authentication
- **Governance** ([../governance/](../governance/)) - Agent ethics and behavior

---

## Documentation

- **README**: [agent/README.md](README.md) - Agent overview
- **Docs**: [agent/docs/](docs/) - Agent architecture and guides
- **Tests**: [agent/tests/](tests/) - Agent test suites
- **Module Index**: [../MODULE_INDEX.md](../MODULE_INDEX.md#agent)

---

**Status**: Integration Lane (L2)
**Manifest**: ✓ module.manifest.json (schema v3.0.0)
**Team**: Core
**Code Owners**: @lukhas-core
**Last Updated**: 2025-10-02
