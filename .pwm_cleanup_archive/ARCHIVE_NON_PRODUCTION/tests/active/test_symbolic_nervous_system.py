"""
Unit tests for SymbolicNervousSystem
"""

import pytest
from perception.symbolic_nervous_system import SymbolicNervousSystem


class DummyManager:
    def __init__(self):
        self.last_store = None

    async def store(self, memory_data, memory_id=None, metadata=None):
        self.last_store = {"memory_data": memory_data, "metadata": metadata}
        return {"status": "ok", "memory_id": "1"}


@pytest.mark.asyncio
async def test_map_and_store_echo():
    manager = DummyManager()
    sns = SymbolicNervousSystem(memory_manager=manager)
    dream = {}
    result = await sns.store_sensory_echo(dream, temperature=25.0, light=0.8)
    assert result["sensory_echoes"]
    assert manager.last_store is not None
    assert manager.last_store["metadata"]["tags"] == ["warm", "bright"]


def test_tag_generation():
    sns = SymbolicNervousSystem()
    tags = sns.map_inputs_to_tags(15.0, 0.2)
    assert tags == ["cold", "dark"]
