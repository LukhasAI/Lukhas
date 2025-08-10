import asyncio

from core.core_utilities import QuantizedCycleManager


async def _run():
    manager = QuantizedCycleManager(step_duration=0)
    await manager.start_cycle()
    await manager.end_cycle()
    assert manager.cycle_count == 1


asyncio.run(_run())
