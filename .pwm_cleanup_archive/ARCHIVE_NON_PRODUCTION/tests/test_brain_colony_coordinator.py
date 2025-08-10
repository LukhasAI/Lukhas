import asyncio
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "colony_coordinator",
    Path(__file__).resolve().parent.parent
    / "orchestration"
    / "brain"
    / "colony_coordinator.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BrainColonyCoordinator = module.BrainColonyCoordinator


@pytest.mark.asyncio
async def test_basic_coordinate_thought():
    coordinator = BrainColonyCoordinator("test-brain")
    result = await coordinator.coordinate_thought({"type": "ping"})
    assert "plan_id" in result
    assert set(result["results"].keys()) == {"perceive", "reason", "emote", "act"}


if __name__ == "__main__":
    asyncio.run(test_basic_coordinate_thought())
