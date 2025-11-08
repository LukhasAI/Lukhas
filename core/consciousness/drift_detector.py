"""Consciousness drift detection utilities for legacy consensus."""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.symbolic.glyph_specialist import GlyphSignal

logger = logging.getLogger("Lukhas.Consciousness.DriftDetector")


@dataclass
class DriftSnapshot:
    """Snapshot of a consciousness layer state."""

    layer_id: str
    driftScore: float
    affect_delta: float
    glyph_markers: Sequence[str] = field(default_factory=list)
    metadata: dict | None = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConsciousnessDriftDetector:
    """Track and summarize drift metrics across consciousness layers."""

    def __init__(self, retention: int = 12) -> None:
        self.retention = retention
        self._history: dict[str, collections.deque[DriftSnapshot]] = defaultdict(
            lambda: deque(maxlen=self.retention)
        )
        self._logger = logger

    def record_snapshot(
        self,
        layer_id: str,
        driftScore: float,
        affect_delta: float,
        glyph_markers: Sequence[str] | None = None,
        metadata: dict | None = None,
    ) -> DriftSnapshot:
        """Record a new snapshot for a consciousness layer."""
        snapshot = DriftSnapshot(
            layer_id=layer_id,
            driftScore=driftScore,
            affect_delta=affect_delta,
            glyph_markers=list(glyph_markers or []),
            metadata=metadata or {},
        )
        self._history[layer_id].append(snapshot)
        self._logger.debug(
            "# ΛTAG: drift_snapshot -- recorded snapshot",
            extra={
                "layer_id": layer_id,
                "driftScore": driftScore,
                "affect_delta": affect_delta,
                "glyph_markers": snapshot.glyph_markers,
            },
        )
        return snapshot

    def build_glyph_signals(self) -> list[GlyphSignal]:
        """Create GLYPH signals from the most recent snapshots."""
        latest_snapshots = [snapshots[-1] for snapshots in self._history.values() if snapshots]
        signals = [
            GlyphSignal(
                layer_id=snapshot.layer_id,
                driftScore=snapshot.driftScore,
                affect_delta=snapshot.affect_delta,
                glyph_markers=snapshot.glyph_markers,
            )
            for snapshot in latest_snapshots
        ]
        return signals

    def summarize_layers(self) -> dict:
        """Summarize drift metrics across layers."""
        summaries: dict[str, dict[str, float]] = {}
        for layer_id, snapshots in self._history.items():
            if not snapshots:
                continue
            drift_values = [snap.driftScore for snap in snapshots]
            affect_values = [snap.affect_delta for snap in snapshots]
            summaries[layer_id] = {
                "driftScore": sum(drift_values) / len(drift_values),
                "affect_delta": sum(affect_values) / len(affect_values),
                "samples": float(len(snapshots)),
            }
        # ΛTAG: drift_summary
        return {
            "layers": summaries,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset(self) -> None:
        """Clear all recorded history."""
        self._history.clear()
        self._logger.info("# ΛTAG: drift_reset -- cleared drift detector history")
        # TODO: persist cleared state to archival store for audit reconciliation.
