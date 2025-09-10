"""Builtin Jules agent implementation.

ΛTAG: builtin_jules_agent
"""

from ..base import OrchestrationAgent
from ..types import AgentCapability, AgentContext, AgentResponse


class Jules01Agent(OrchestrationAgent):
    """Simple Jules agent for demonstration."""

    def get_agent_id(self) -> str:
        return "jules_01"

    def get_capabilities(self) -> list[AgentCapability]:
        return [AgentCapability.ORCHESTRATION]

    def process(self, context: AgentContext) -> AgentResponse:
        return AgentResponse(success=True, result=None, metadata={})

    def validate_context(self, context: AgentContext) -> bool:
        return True