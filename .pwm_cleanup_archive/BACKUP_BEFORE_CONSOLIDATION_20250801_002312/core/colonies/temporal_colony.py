"""Temporal Colony - simulate past and future symbolic states."""

import copy
import logging
from typing import Any, Dict, List, Optional

from .base_colony import BaseColony

logger = logging.getLogger(__name__)


# ΛTAG: temporal_ops
class TemporalColony(BaseColony):
    """Colony supporting reversible temporal reasoning."""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["temporal_reasoning"])
        self.current_state: Dict[str, Any] = {"glyphs": []}
        self.state_history: List[Dict[str, Any]] = []

    def snapshot_state(self) -> None:
        """Save a deep copy of the current symbolic state."""
        self.state_history.append(copy.deepcopy(self.current_state))
        logger.info("State snapshot saved", history_len=len(self.state_history))

    def revert_last(self) -> bool:
        """Revert to the most recent snapshot."""
        if not self.state_history:
            return False
        self.current_state = self.state_history.pop()
        logger.info("State reverted", remaining=len(self.state_history))
        return True

    def get_state(self, index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Return a historical state or current if index is None."""
        if index is None:
            return self.current_state
        if 0 <= index < len(self.state_history):
            return copy.deepcopy(self.state_history[index])
        return None

    def _apply_operations(
        self, state: Dict[str, Any], operations: List[Dict[str, Any]]
    ) -> None:
        for op in operations:
            if op.get("type") == "add_glyph":
                state.setdefault("glyphs", []).append(op.get("value"))
            elif op.get("type") == "remove_glyph" and op.get("value") in state.get(
                "glyphs", []
            ):
                state["glyphs"].remove(op.get("value"))
            # ✅ TODO: implement more operation types

    def simulate_future_state(
        self, operations: List[Dict[str, Any]], from_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """Return a simulated state after applying operations without committing."""
        base_state = self.get_state(from_index)
        if base_state is None:
            base_state = self.current_state
        future_state = copy.deepcopy(base_state)
        self._apply_operations(future_state, operations)
        logger.info("Simulated future state", glyphs=future_state.get("glyphs"))
        return future_state

    async def execute_task(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info("TemporalColony executing task", task_id=task_id)
        operations = task_data.get("operations", [])
        if task_data.get("simulate"):
            future = self.simulate_future_state(operations, task_data.get("from_index"))
            return {"status": "simulated", "state": future}
        if task_data.get("revert"):
            success = self.revert_last()
            return {"status": "reverted" if success else "failed"}
        self.snapshot_state()
        self._apply_operations(self.current_state, operations)
        return {"status": "completed", "state": copy.deepcopy(self.current_state)}
