import pytest

from memory.systems.distributed_memory_fold import DistributedMemoryFold


@pytest.mark.asyncio
async def test_session_lifecycle():
    system = DistributedMemoryFold(node_id="test-node", port=9000)
    session = await system._get_session()
    assert session and not session.closed
    await system.shutdown()
    assert session.closed
