"""Registry for orchestration agents.

ΛTAG: orchestration_agent_registry
"""
from typing import Optional

from .base import OrchestrationAgent
from .types import AgentCapability


class AgentRegistry:
    """Manages orchestration agent registration and discovery."""

    def __init__(self) -> None:
        self._agents: dict[str, OrchestrationAgent] = {}
        self._capability_map: dict[AgentCapability, list[str]] = {}

    def register(self, agent: OrchestrationAgent) -> None:
        """Register an agent instance."""
        agent_id = agent.get_agent_id()
        self._agents[agent_id] = agent

        for capability in agent.get_capabilities():
            self._capability_map.setdefault(capability, []).append(agent_id)

    def get_agent(self, agent_id: str) -> Optional[OrchestrationAgent]:
        """Retrieve an agent by its ID."""
        return self._agents.get(agent_id)

    def find_agents_by_capability(self, capability: AgentCapability) -> list[OrchestrationAgent]:
        """Find all agents that support a capability."""
        agent_ids = self._capability_map.get(capability, [])
        return [self._agents[aid] for aid in agent_ids]

    def list_agents(self) -> list[OrchestrationAgent]:
        """Return all registered agents."""
        return list(self._agents.values())