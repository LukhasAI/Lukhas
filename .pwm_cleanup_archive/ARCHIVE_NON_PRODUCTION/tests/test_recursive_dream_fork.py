import pytest
from dream.engine.dream_engine import DreamEngine

from core.colonies.creativity_colony import CreativityColony


class DummyCreativityColony(CreativityColony):
    def __init__(self):
        super().__init__("dummy")
        self.last_task = None

    async def execute_task(self, task_id: str, task_data: dict) -> dict:
        self.last_task = (task_id, task_data)
        return {"status": "ok", "task_id": task_id}


@pytest.mark.asyncio
async def test_detect_and_fork_recursive_dream():
    engine = DreamEngine()
    colony = DummyCreativityColony()
    symbols = ["A", "B", "A", "B"]
    forked = await engine.detect_and_fork_recursive_dream(symbols, colony)
    assert forked
    assert colony.last_task is not None
    assert colony.last_task[1]["type"] == "dreamscapes_nested"
