"""
Symbolic Shell Archiver
"""

import asyncio
import json
import logging
import time
from typing import Any

from lukhas.core.colonies.base_colony import BaseColony

logger = logging.getLogger(__name__)


class SymbolicShellArchiver:
    """
    Creates periodic snapshots of the full symbolic state.
    """

    def __init__(self, colonies: list[BaseColony], output_dir: str = "/tmp"):
        self.colonies = colonies
        self.output_dir = output_dir

    def get_full_symbolic_state(self) -> dict[str, Any]:
        """
        Get the full symbolic state of the system.
        """
        state = {"timestamp": time.time(), "colonies": {}}

        for colony in self.colonies:
            state["colonies"][colony.colony_id] = {
                "symbolic_carryover": {
                    k: (v[0], v[1].value, v[2].value, v[3], v[4]) for k, v in colony.symbolic_carryover.items()
                },
                "tag_propagation_log": colony.tag_propagation_log,
            }

        return state

    def create_snapshot(self):
        """
        Create a snapshot of the full symbolic state.
        """
        state = self.get_full_symbolic_state()
        timestamp = int(state["timestamp"])
        filename = f"{self.output_dir}/symbolic_snapshot_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(state, f, indent=4)

        logger.info(f"Created symbolic snapshot: {filename}")
        return filename

    async def _run_periodic_snapshots(self, interval: int):
        """
        Run the snapshot process periodically.
        """
        while self.is_running:
            self.create_snapshot()
            await asyncio.sleep(interval)

    def start(self, interval: int = 3600):
        """
        Start the archiver.
        """
        self.is_running = True
        self.task = asyncio.create_task(self._run_periodic_snapshots(interval))
        logger.info(f"SymbolicShellArchiver started with interval {interval}s")

    def stop(self):
        """
        Stop the archiver.
        """
        self.is_running = False
        if self.task:
            self.task.cancel()
        logger.info("SymbolicShellArchiver stopped")
