import asyncio
import sys
from pathlib import Path

import pytest
from core.symbolic_core import plan_symbolic_core_preservation
from core.symbolic_core.colony_tag_propagation import SymbolicReasoningColony

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for module_name in ["labs", "labs.core", "labs.core.symbolic_core", "labs.core.symbolic_core.colony_tag_propagation"]:
    sys.modules.pop(module_name, None)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.create_task = lambda coro, *, _loop=loop: _loop.create_task(coro)  # type: ignore[assignment]



@pytest.mark.asyncio
async def test_symbolic_colony_processing_cycle() -> None:
    colony = SymbolicReasoningColony("demo_colony", agent_count=3)

    process_result = colony.process({"concept": "insight", "value": "glow", "confidence": 0.8})
    assert process_result["activation"]
    assert 0 <= process_result["driftScore"] <= 1

    consensus = colony.reach_consensus({"goal": "synchronize"})
    assert hasattr(consensus, "confidence")
    assert consensus.confidence >= 0.0

    belief_states = await colony.propagate_belief(
        {"concept": "insight", "value": "glow", "strength": 0.7, "iterations": 2}
    )
    assert len(belief_states) == len(colony.agents)


def test_symbolic_triage_plan_includes_actions():
    plan = plan_symbolic_core_preservation({"mito_qi": {"driftScore": 0.5, "affect_delta": 0.3}})
    assert "recommended_actions" in plan
    assert plan["collapseHash"]
