import asyncio

import pytest

from memory.loop_monitor import SymbolicLoopMonitor


@pytest.mark.asyncio
async def test_loop_auto_cancel_on_entanglement():
    monitor = SymbolicLoopMonitor(check_interval=0.05, entanglement_threshold=0.2)

    async def spin():
        while True:
            await asyncio.sleep(0.01)

    task = monitor.register_loop("test", spin())
    await monitor.start()
    await asyncio.sleep(0.1)
    monitor.report_entanglement("test", 0.5)
    await asyncio.sleep(0.1)

    assert task.cancelled()
    await monitor.stop()
