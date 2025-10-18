"""Unit tests for DreamFeedbackController symbolic redirect scoring."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import dream as dream_pkg

dream_core_pkg = ModuleType("dream.core")
dream_core_pkg.__path__ = []  # Mark as namespace package for import machinery
sys.modules.setdefault("dream.core", dream_core_pkg)
dream_core_snapshot_module = importlib.import_module(
    "labs.consciousness.dream.core.dream_snapshot"
)
sys.modules["dream.core.dream_snapshot"] = dream_core_snapshot_module
setattr(dream_core_pkg, "dream_snapshot", dream_core_snapshot_module)
setattr(dream_pkg, "core", dream_core_pkg)

from lukhas.consciousness.dream.core.dream_feedback_controller import (  # noqa: E402
    DreamFeedbackController,
)


class StubSnapshotStore:
    def __init__(self, snapshots):
        self._snapshots = snapshots
        self.requested_user_id: str | None = None

    def get_recent_snapshots(self, user_id: str):
        self.requested_user_id = user_id
        return list(self._snapshots)


class StubEmotionalMemory:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple, dict]] = []

    def affect_delta(self, *args, **kwargs):  # pragma: no cover - stub only
        self.calls.append((args, kwargs))
        return {"intensity_change": 0.0}


def test_trigger_redirection_prefers_symbolic_alignment():
    controller = DreamFeedbackController()
    controller.snapshot_store = StubSnapshotStore(
        [
            {
                "dream_id": "dream_alpha",
                "emotional_context": {"confidence": 0.9, "curiosity": 0.65},
                "driftScore": 0.2,
            },
            {
                "dream_id": "dream_beta",
                "emotional_context": {"fear": 0.9},
                "driftScore": 0.0,
            },
        ]
    )
    controller.emotional_memory = StubEmotionalMemory()

    result = controller.trigger_redirection(
        "user-42",
        {"confidence": 0.82, "curiosity": 0.62},
    )

    assert result["target_snapshot"]["dream_id"] == "dream_alpha"
    assert result["symbolic_reason"].startswith("High driftScore detected")


def test_trigger_redirection_handles_missing_snapshots():
    controller = DreamFeedbackController()
    controller.snapshot_store = StubSnapshotStore([])
    controller.emotional_memory = StubEmotionalMemory()

    result = controller.trigger_redirection("user-99", {"calm": 0.5})

    assert result["target_snapshot"] is None
    assert result["symbolic_reason"].endswith("symbolic redirect unavailable")
