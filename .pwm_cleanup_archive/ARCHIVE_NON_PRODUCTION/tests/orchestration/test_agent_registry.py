from orchestration.agents.base import OrchestrationAgent
from orchestration.agents.registry import AgentRegistry
from orchestration.agents.types import (
    AgentCapability,
    AgentContext,
    AgentResponse,
)


class DummyAgent(OrchestrationAgent):
    def get_agent_id(self) -> str:
        return "dummy"

    def get_capabilities(self):
        return [AgentCapability.ORCHESTRATION]

    def process(self, context: AgentContext) -> AgentResponse:
        return AgentResponse(success=True, result=None, metadata={})

    def validate_context(self, context: AgentContext) -> bool:
        return True


def test_agent_registration_and_lookup():
    registry = AgentRegistry()
    agent = DummyAgent()
    registry.register(agent)

    assert registry.get_agent("dummy") is agent


def test_find_agents_by_capability():
    registry = AgentRegistry()
    agent = DummyAgent()
    registry.register(agent)

    agents = registry.find_agents_by_capability(AgentCapability.ORCHESTRATION)
    assert agent in agents
