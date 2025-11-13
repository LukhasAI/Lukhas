from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class NodeEvent:
    node: str
    run_id: str
    cycle_idx: int
    payload: Dict[str, Any]

def emit_event(evt: NodeEvent) -> None:
    """
    Hook: integrate with core.events.typed_event_bus.
    For now, it's a no-op so tests remain hermetic.
    """
    # TODO: wire to event bus when available
    pass

def wavec_checkpoint(run_id: str, cycle_idx: int, memory_state: Dict[str, Any]) -> None:
    """
    Hook: integrate with WaveC snapshot store (gzip+sha256+TTL).
    Tests will monkeypatch this function to assert it was called.
    """
    # TODO: persist snapshot in WaveC service when available
    pass
