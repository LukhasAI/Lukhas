import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from orchestration.agent_orchestrator import AgentOrchestrator
from orchestration.interfaces.orchestration_protocol import TaskDefinition


#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])

class Query(BaseModel):
    text: str

from orchestration.agents.builtin.codex import Codex

orchestrator = AgentOrchestrator()
codex_agent = Codex()
asyncio.run(orchestrator.register_agent(codex_agent))
asyncio.run(orchestrator.initialize())

@router.post("/respond")
async def respond(query: Query):
    task = TaskDefinition(description=query.text)
    task_id = await orchestrator.submit_task(task)
    # This is a simplified approach. In a real scenario, we would wait for the task to complete
    # and return the result. For now, we'll just return the task ID.
    return {"task_id": task_id}

@router.get("/task_result/{task_id}")
async def get_task_result(task_id: str):
    result = await orchestrator.get_task_result(task_id)
    if result:
        return result.to_dict()
    return {"status": "pending"}
