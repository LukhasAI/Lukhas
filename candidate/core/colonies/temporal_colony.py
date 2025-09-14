"""Temporal Colony - simulate past and future symbolic states."""

import copy
import logging
from typing import Any, Optional

from .base_colony import BaseColony

logger = logging.getLogger(__name__)

# ΛTAG: temporal_ops


class TemporalColony(BaseColony):
    """Colony supporting reversible temporal reasoning."""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["temporal_reasoning"])
        self.current_state: dict[str, Any] = {"glyphs": []}
        self.state_history: list[dict[str, Any]] = []

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

    def get_state(self, index: Optional[int] = None) -> Optional[dict[str, Any]]:
        """Return a historical state or current if index is None."""
        if index is None:
            return self.current_state
        if 0 <= index < len(self.state_history):
            return copy.deepcopy(self.state_history[index])
        return None

    def _apply_operations(self, state: dict[str, Any], operations: list[dict[str, Any]]) -> None:
        for op in operations:
            op_type = op.get("type")
            if op_type == "add_glyph":
                state.setdefault("glyphs", []).append(op.get("value"))
            elif op_type == "remove_glyph" and op.get("value") in state.get("glyphs", []):
                state["glyphs"].remove(op.get("value"))
            elif op_type == "append_many":
                state.setdefault("glyphs", []).extend(op.get("values", []))
            elif op_type == "replace":
                state["glyphs"] = op.get("values", [])

    def simulate_future_state(
        self,
        operations: list[dict[str, Any]],
        from_index: Optional[int] = None,
    ) -> dict[str, Any]:
        """Return a simulated state after applying operations without committing."""
        base_state = self.get_state(from_index)
        if base_state is None:
            base_state = self.current_state
        future_state = copy.deepcopy(base_state)
        self._apply_operations(future_state, operations)
        logger.info("Simulated future state", glyphs=future_state.get("glyphs"))
        return future_state

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
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
        return {
            "status": "completed",
            "state": copy.deepcopy(self.current_state),
        }


if __name__ == "__main__":
    # Basic tests for TemporalColony
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Running tests for TemporalColony...")
    colony = TemporalColony("test_temporal")
    assert colony.get_state() == {"glyphs": []}
    logger.info(f"Initial state: {colony.get_state()}")

    # Test append_many
    colony.snapshot_state()
    operations = [{"type": "append_many", "values": ["g1", "g2", "g3"]}]
    colony._apply_operations(colony.current_state, operations)
    assert colony.get_state()["glyphs"] == ["g1", "g2", "g3"]
    logger.info(f"After append_many: {colony.get_state()}")

    # Test add_glyph
    colony.snapshot_state()
    operations = [{"type": "add_glyph", "value": "g4"}]
    colony._apply_operations(colony.current_state, operations)
    assert colony.get_state()["glyphs"] == ["g1", "g2", "g3", "g4"]
    logger.info(f"After add_glyph: {colony.get_state()}")

    # Test replace
    colony.snapshot_state()
    operations = [{"type": "replace", "values": ["g5", "g6"]}]
    colony._apply_operations(colony.current_state, operations)
    assert colony.get_state()["glyphs"] == ["g5", "g6"]
    logger.info(f"After replace: {colony.get_state()}")

    # Test revert
    assert colony.revert_last() is True
    assert colony.get_state()["glyphs"] == ["g1", "g2", "g3", "g4"]
    logger.info(f"After first revert: {colony.get_state()}")

    assert colony.revert_last() is True
    assert colony.get_state()["glyphs"] == ["g1", "g2", "g3"]
    logger.info(f"After second revert: {colony.get_state()}")

    # Test simulation
    future_ops = [{"type": "remove_glyph", "value": "g1"}]
    future_state = colony.simulate_future_state(future_ops)
    assert future_state["glyphs"] == ["g2", "g3"]
    assert colony.get_state()["glyphs"] == ["g1", "g2", "g3"]  # Current state unchanged
    logger.info(f"Simulated future state: {future_state}")
    logger.info(f"Current state after simulation: {colony.get_state()}")

    # Test empty revert
    colony.revert_last()
    assert colony.get_state() == {'glyphs': []}
    assert colony.revert_last() is False
    logger.info(f"State after all reverts: {colony.get_state()}")

    logger.info("TemporalColony tests passed!")
    print("\nTemporalColony tests passed!")
