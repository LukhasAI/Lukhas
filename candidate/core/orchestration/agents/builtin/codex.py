"""Builtin Codex agent implementation.

ΛTAG: builtin_codex_agent
"""

from ..interfaces.agent_interface import (
    AgentCapability,
    AgentContext,
    AgentInterface,
    AgentMetadata,
    AgentStatus,
)
from ..interfaces.orchestration_protocol import TaskDefinition, TaskResult


class Codex(AgentInterface):
    """Codex agent for general purpose queries."""

    def __init__(self):
        self.metadata = AgentMetadata(
            agent_id="codex",
            name="Codex Agent",
            capabilities=[AgentCapability.GENERAL_QUERY],
        )
        self.status = AgentStatus.READY
        self.context = None

    async def initialize(self, context: AgentContext) -> bool:
        self.context = context
        return True

    async def process_task(self, task: TaskDefinition) -> TaskResult:
        response = self.respond(task.description)
        return TaskResult(
            task_id=task.task_id,
            status="success",
            result_data={"response": response},
        )

    def respond(self, query: str) -> str:
        # CodexAgent basic logic
        parsed = self.parse_query(query)
        response = f"[Codex] Interpreted as: {parsed['intent']}, executed placeholder task."
        return response

    def parse_query(self, query: str) -> dict:
        # Simple intent parsing
        if ("doctor" in query and "hospital" in query) or ("car" in query and "road" in query):
            return {"intent": "analogy"}
        elif ("color" in query and "sky" in query) or ("sound" in query and "dog" in query):
            return {"intent": "question"}
        elif "sad child" in query or "happy child" in query:
            return {"intent": "decoupling"}
        else:
            return {"intent": "unknown"}

    async def shutdown(self) -> None:
        self.status = AgentStatus.SHUTDOWN

    async def get_health_status(self) -> dict:
        return {"status": "healthy"}
