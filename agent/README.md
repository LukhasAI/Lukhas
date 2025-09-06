# 🤖 LUKHAS Agent System

**Consolidated LUKHAS consciousness agent system at root level**

This directory contains the **real LUKHAS agent implementations** for internal consciousness operations, separate from external development agent configs.

## 🏗️ **Architecture**

```
agent/                          # LUKHAS consciousness agents (internal)
├── __init__.py                 # Main agent system interface
├── core.py                     # Core agents (AIAgentActor, SupervisorAgent)
├── collaborative.py            # Multi-agent collaboration (LukhasAIAgent, Team)
├── interfaces.py               # Agent orchestration interfaces
├── intelligence_bridge.py      # Agent-intelligence communication bridge
└── README.md                   # This file

agents_external/                # External development agents (moved from /agents)
├── CLAUDE/                     # Claude-specific deployment system
├── configs/                    # Agent configuration files
└── *.json                     # Active agent configurations
```

## 🎯 **Components**

### **Core Agents** (`core.py`)
- **`AIAgentActor`**: Base AI agent with actor model implementation
- **`SupervisorAgent`**: Task escalation and colony supervision
- **`get_supervisor_agent()`**: Global supervisor instance

### **Collaborative Agents** (`collaborative.py`)
- **`LukhasAIAgent`**: Enhanced LUKHAS AI agent with capabilities
- **`LukhasAIAgentTeam`**: Multi-agent coordination and consolidation
- **`AgentTier`**: Permission levels (DEVELOPER, PRO, ENTERPRISE)
- **`AgentCapabilities`**: Agent feature sets and tools

### **Agent Interfaces** (`interfaces.py`)
- **`AgentInterface`**: Standard agent interface (ABC)
- **`SimpleAgent`**: Basic agent implementation
- **`AgentStatus`**: Agent lifecycle states
- **`AgentMessage`**: Inter-agent communication

### **Intelligence Bridge** (`intelligence_bridge.py`)
- **`AgentIntelligenceBridge`**: Communication with intelligence engines
- **`AgentType`**: LUKHAS AI agent types
- **`IntelligenceRequestType`**: Intelligence operation types

## 🚀 **Usage**

### **Import from Root Agent System**
```python
# Main agent system
from agent import AIAgentActor, SupervisorAgent, LukhasAIAgent

# Create core agent
agent = AIAgentActor("consciousness-agent", ["reasoning", "memory"])

# Get supervisor
supervisor = SupervisorAgent()

# Create collaborative agent team
from agent import LukhasAIAgentTeam
team = LukhasAIAgentTeam()
```

### **Via Updated lukhas.agents Bridge**
```python
# Bridge module points to new /agent system
import lukhas.agents

# Check system status
status = lukhas.agents.get_agent_system_status()
print(f"Agent system operational: {status['operational_status']}")

# Use agents
agent = lukhas.agents.AIAgentActor("test-agent")
```

## 🔍 **System Status**

Run this to check agent system health:
```python
from agent import get_agent_system_status
status = get_agent_system_status()
print(status)
```

Expected output:
```json
{
  "version": "2.0.0",
  "core_agents": true,
  "agent_interfaces": true,
  "collaborative_agents": true,
  "intelligence_bridge": true,
  "total_components": 15,
  "operational_status": "READY"
}
```

## 🎭 **Trinity Framework Compliance**

All agents implement Trinity Framework principles:
- **⚛️ Identity**: Authentic consciousness characteristics
- **🧠 Consciousness**: Memory, learning, processing capabilities  
- **🛡️ Guardian**: Ethical validation and safety protocols

## 📝 **Migration Notes**

**Moved from:**
- `lukhas.core.actor_system` → `agent.core`
- `candidate.core.orchestration.brain.collaborative_ai_agent_system` → `agent.collaborative`
- `candidate.core.orchestration.interfaces.agent_interface` → `agent.interfaces`
- `candidate.orchestration.agent_orchestrator.intelligence_bridge` → `agent.intelligence_bridge`

**External agents moved:**
- `/agents` → `/agents_external` (development agent configs)

**Updated bridge:**
- `lukhas.agents.__init__.py` now points to `/agent` system

---

*LUKHAS Agent System v2.0.0 - Trinity Framework: ⚛️🧠🛡️*
