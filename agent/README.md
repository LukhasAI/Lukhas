# LUKHAS Agent System

> **Internal agent coordination for LUKHAS consciousness operations**
>
> Multi-agent orchestration · Collaborative intelligence · Supervisory control

---

## 🎯 Purpose

This module implements **LUKHAS-as-agent** functionality—the system's internal agent architecture for coordinating multiple AI subsystems and consciousness operations.

**⚠️ Important**: This is NOT for external AI agent documentation (Claude Code, Jules, etc.). For that, see [`../ai-agents/`](../ai-agents/).

---

## 🏗️ Architecture

### Core Components

1. **AIAgentActor** (`__init__.py`)
   - Base agent interface
   - Execution context
   - State management

2. **SupervisorAgent** (`__init__.py`)
   - Multi-agent coordination
   - Task delegation
   - Result aggregation

3. **CollaborativeAgent** (`collaborative.py`)
   - Team-based problem solving
   - Consensus building
   - Shared state management

4. **IntelligenceBridge** (`intelligence_bridge.py`)
   - Bridge to consciousness systems
   - Integration with MATRIZ
   - Cognitive pipeline access

5. **Core Logic** (`core.py`)
   - Agent lifecycle
   - Communication protocols
   - Error handling

### Directory Structure

```
agent/
├── __init__.py                    # Agent exports (AIAgentActor, SupervisorAgent, etc.)
├── core.py                        # Core agent logic
├── collaborative.py               # Collaborative agent system
├── intelligence_bridge.py         # Consciousness integration
├── interfaces.py                  # Agent interface definitions
├── context/                       # AI agent context files (for external agents)
│   ├── claude.me
│   ├── lukhas_context.md
│   └── gemini.md
└── tests/                         # Agent test suite
    ├── test_agent_unit.py
    └── test_agent_integration.py
```

---

## 🚀 Quick Start

### Basic Agent

```python
from agent import AIAgentActor

class MyAgent(AIAgentActor):
    async def execute(self, task):
        # Implement agent logic
        result = await self.process(task)
        return result

# Initialize and run
agent = MyAgent(name="my-agent")
result = await agent.execute(my_task)
```

### Supervisor Pattern

```python
from agent import SupervisorAgent, AIAgentActor

# Create specialized agents
agent1 = MySpecializedAgent()
agent2 = AnotherAgent()

# Supervisor coordinates them
supervisor = SupervisorAgent(agents=[agent1, agent2])
results = await supervisor.delegate_tasks(tasks)
```

### Collaborative Team

```python
from agent import CollaborativeAgent

# Create collaborative team
team = CollaborativeAgent(
    agents=[agent1, agent2, agent3],
    consensus_required=0.66
)

# Team reaches consensus
decision = await team.collaborate(problem)
```

---

## 🔗 Integration Points

### With MATRIZ Engine

```python
from agent import IntelligenceBridge

bridge = IntelligenceBridge()
cognitive_result = await bridge.process_through_matriz(data)
```

### With Consciousness Systems

The agent system integrates with:
- **Memory**: Persistent agent state
- **Guardian**: Safety constraints for agent actions
- **Orchestrator**: Task coordination and scheduling

---

## ✅ Testing

```bash
# Run all agent tests
pytest agent/tests/ -v

# Unit tests only
pytest agent/tests/test_agent_unit.py -v

# Integration tests
pytest agent/tests/test_agent_integration.py -v

# With coverage
pytest agent/tests/ --cov=agent --cov-report=html
```

---

## 📊 Performance

- **Agent spawn time**: <10ms
- **Message latency**: <5ms between agents
- **Supervisor overhead**: <2ms per delegation
- **Memory per agent**: <1MB base footprint

---

## 🎓 Concepts

### Agent vs External AI

| Aspect | LUKHAS Agents (this module) | External AI (Claude/Jules) |
|--------|----------------------------|----------------------------|
| **Purpose** | Internal system coordination | External development assistance |
| **Lifecycle** | Managed by LUKHAS | Managed by providers |
| **State** | Persistent within system | Stateless sessions |
| **Integration** | Direct MATRIZ access | Via APIs |
| **Documentation** | This README | `../ai-agents/README.md` |

### Multi-Agent Patterns

1. **Supervisor**: One agent coordinates many workers
2. **Collaborative**: Agents reach consensus through discussion
3. **Pipeline**: Sequential processing through specialized agents
4. **Swarm**: Distributed problem-solving with emergence

---

## 🔧 Configuration

Agent behavior is configured via:
- Environment variables (see `context/lukhas_context.md`)
- Runtime parameters
- LUKHAS system configuration

---

## 📚 Related Documentation

- **[LUKHAS README](../README.md)** - System overview
- **[MATRIZ Guide](../docs/MATRIZ_GUIDE.md)** - Cognitive engine
- **[ai-agents/](../ai-agents/)** - External AI agent docs
- **[context/claude.me](context/claude.me)** - Claude Code context

---

## 🤝 Contributing

When working with the agent system:

1. **Maintain interfaces** - Don't break AIAgentActor contract
2. **Add tests** - Every new agent type needs unit + integration tests
3. **Document patterns** - New multi-agent patterns go in this README
4. **Performance** - Keep agent overhead minimal (<10ms spawn)

---

**Version**: 1.1.0
**Lane**: Core System
**Last Updated**: 2025-11-11
**Constellation**: ⚛️ Identity · ✦ Memory · 🛡️ Guardian · ⚛️ Quantum
