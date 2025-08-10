import asyncio

from core.colonies.reasoning_colony import ReasoningColony
from core.symbolic.collapse.vector_ops import vector_collapse
from core.symbolism.tags import TagPermission, TagScope


def test_vector_collapse_mapping():
    assert vector_collapse([0.9, 0.8]) == TagScope.GLOBAL
    assert vector_collapse([0.5, 0.4]) == TagScope.LOCAL
    assert vector_collapse([0.1, 0.2]) == TagScope.TEMPORAL
    assert vector_collapse([-0.1, -0.2]) == TagScope.ETHICAL


def test_propagation_uses_vector_collapse():
    colony = ReasoningColony("vc_test")
    task = {
        "type": "demo",
        "collapse_vector": [0.8, 0.9, 0.85],
        "tags": {"demo_tag": ("val", None, TagPermission.PUBLIC, None)},
    }

    async def run():
        await colony.start()
        await colony.execute_task("t1", task)
        await colony.stop()

    asyncio.run(run())

    assert colony.symbolic_carryover["demo_tag"][1] == TagScope.GLOBAL
