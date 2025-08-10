import asyncio

from core.colonies.reasoning_colony import ReasoningColony
from core.symbolism.tags import TagPermission, TagScope


def test_restricted_tag_escalation():
    colony = ReasoningColony("c1")
    task = {
        "type": "restricted",
        "tags": {"secret": ("x", TagScope.LOCAL, TagPermission.RESTRICTED, None)},
    }

    async def run():
        await colony.start()
        result = await colony.execute_task("t1", task)
        await colony.stop()
        return result

    result = asyncio.run(run())
    assert result["status"] == "escalated"
    assert colony.fast_execution_blocked
