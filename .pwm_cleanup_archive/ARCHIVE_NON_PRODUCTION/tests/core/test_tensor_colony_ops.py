import asyncio

import pytest

torch = pytest.importorskip("torch")

from core.colonies.reasoning_colony import ReasoningColony
from core.colonies.tensor_colony_ops import batch_propagate, tags_to_tensor
from core.symbolism.tags import TagPermission, TagScope


def test_tags_to_tensor():
    tag_data = {"a": ("hello", TagScope.LOCAL, TagPermission.PUBLIC, None)}
    tensor = tags_to_tensor(tag_data)
    assert tensor.shape[0] == 1
    assert tensor.shape[1] == 16


def test_batch_propagate():
    colony = ReasoningColony("c1")
    tag_data = {"t": ("value", TagScope.GLOBAL, TagPermission.PUBLIC, None)}

    async def run():
        await colony.start()
        batch_propagate([colony], tag_data)
        await colony.stop()

    asyncio.run(run())

    assert "t" in colony.symbolic_carryover
