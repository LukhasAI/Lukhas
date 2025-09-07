import logging
import streamlit as st
logger = logging.getLogger(__name__)
"""

from __future__ import annotations
╔══════════════════════════════════════════════════════════════════════════════╗
║ 🧠 LUKHAS AI - SYMBOLIC LOOP MONITOR                                         ║
║ Automatic cancellation of rogue entanglement loops or memory corruption      ║
║                                                                            ║
║ This module monitors registered asynchronous loops for abnormal             ║
║ entanglement levels or memory corruption indicators. When thresholds        ║
║ are exceeded, the loop is gracefully cancelled to protect system stability. ║
║                                                                            ║
║ Symbolic Tags: {ΛMEMORY}, {ΛMONITOR}, {ΛPROTECT}                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import contextlib
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Optional


@dataclass
class LoopInfo:
    """Metadata for a monitored loop."""

    task: asyncio.Task
    start_time: float
    drift_score: float = 0.0  # ΛTAG: driftScore
    collapse_hash: Optional[str] = None  # ΛTAG: collapseHash
    affect_delta: float = 0.0  # ΛTAG: affect_delta
    entanglement_level: float = 0.0
    corruption_count: int = 0


class SymbolicLoopMonitor:
    """Monitor asynchronous loops and cancel on dangerous conditions."""

    def __init__(
        self,
        check_interval: float = 5.0,
        entanglement_threshold: float = 0.8,
        corruption_threshold: int = 3,
    ) -> None:
        self.check_interval = check_interval
        self.entanglement_threshold = entanglement_threshold
        self.corruption_threshold = corruption_threshold
        self._loops: dict[str, LoopInfo] = {}
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        logger.info(
            "LoopMonitor initialized",
            interval=self.check_interval,
            ent_threshold=self.entanglement_threshold,
            corrupt_threshold=self.corruption_threshold,
        )

    def register_loop(self, loop_id: str, coro: Awaitable) -> asyncio.Task:
        """Register and start monitoring a new loop."""
        task = asyncio.create_task(coro)
        self._loops[loop_id] = LoopInfo(task=task, start_time=time.time())
        logger.info("Loop registered", loop_id=loop_id)
        return task

    def report_entanglement(self, loop_id: str, level: float) -> None:
        info = self._loops.get(loop_id)
        if info:
            info.entanglement_level = level
            logger.debug("Entanglement reported", loop_id=loop_id, level=level)

    def report_corruption(self, loop_id: str) -> None:
        info = self._loops.get(loop_id)
        if info:
            info.corruption_count += 1
            logger.warning(
                "Memory corruption detected",
                loop_id=loop_id,
                count=info.corruption_count,
            )

    async def start(self) -> None:
        if not self._running:
            self._running = True
            self._monitor_task = asyncio.create_task(self._monitor())
            logger.info("LoopMonitor started")

    async def stop(self) -> None:
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitor_task
            logger.info("LoopMonitor stopped")

    async def _monitor(self) -> None:
        """Monitor loops for entanglement or corruption and cancel if needed."""
        while self._running:
            for loop_id, info in list(self._loops.items()):
                if info.task.done():
                    self._loops.pop(loop_id, None)
                    continue
                if (
                    info.entanglement_level >= self.entanglement_threshold
                    or info.corruption_count >= self.corruption_threshold
                ):
                    logger.error(
                        "Cancelling rogue loop",
                        loop_id=loop_id,
                        entanglement=info.entanglement_level,
                        corruption=info.corruption_count,
                    )
                    info.task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await info.task
                    self._loops.pop(loop_id, None)
            await asyncio.sleep(self.check_interval)