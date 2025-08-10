import pytest

from core.core_utilities import Consistency, ConsistencyManager
from core.tiered_state_management import StateType, TieredStateManager


@pytest.mark.asyncio
async def test_apply_updates_strong():
    manager = TieredStateManager()
    cm = ConsistencyManager(manager)
    updates = {"agg1": {"count": 1}, "agg2": {"count": 2}}
    await cm.apply_updates(updates, Consistency.STRONG)
    state1 = await manager.get_state("agg1", StateType.LOCAL_EPHEMERAL)
    state2 = await manager.get_state("agg2", StateType.LOCAL_EPHEMERAL)
    assert state1 == {"count": 1}
    assert state2 == {"count": 2}


@pytest.mark.asyncio
async def test_apply_updates_eventual():
    manager = TieredStateManager()
    cm = ConsistencyManager(manager)
    updates = {"agg": {"value": 42}}
    await cm.apply_updates(updates, Consistency.EVENTUAL)
    state = await manager.get_state("agg", StateType.LOCAL_EPHEMERAL)
    assert state == {"value": 42}
