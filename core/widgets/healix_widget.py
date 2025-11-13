"""Healix dashboard widget helpers."""
from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

logger = logging.getLogger("healix_widget")


@dataclass
class HealixTimelinePoint:
    """Representation of a memory node in the timeline."""

    timestamp: str
    tone: str
    intensity: float
    affect_delta: float


class HealixWidget:
    """Prepare dashboard-friendly Healix timeline data."""

    def __init__(self, nodes: Sequence[Mapping[str, object]] | None = None) -> None:
        self._nodes: list[Mapping[str, object]] = list(nodes or [])
        # ΛTAG: affect_delta - accumulate node affect deltas for timeline shading
        self._cumulative_affect_delta: float = 0.0
        logger.debug(
            "HealixWidget initialized",
            extra={"initial_nodes": len(self._nodes)},
        )

    def load_nodes(self, nodes: Iterable[Mapping[str, object]]) -> None:
        """Replace existing nodes with a new sequence."""

        self._nodes = list(nodes)
        logger.info("HealixWidget nodes loaded", extra={"count": len(self._nodes)})

    def render_timeline(self) -> list[HealixTimelinePoint]:
        """Render the timeline as symbolic points."""

        timeline: list[HealixTimelinePoint] = []
        self._cumulative_affect_delta = 0.0
        for node in self._nodes:
            affect_delta = float(node.get("intensity", 0.0)) * 0.5
            self._cumulative_affect_delta += abs(affect_delta)
            timeline.append(
                HealixTimelinePoint(
                    timestamp=str(node.get("timestamp", "")),
                    tone=str(node.get("tone", "neutral")),
                    intensity=float(node.get("intensity", 0.0)),
                    affect_delta=affect_delta,
                )
            )
        logger.debug(
            "Healix timeline rendered",
            extra={
                "points": len(timeline),
                "cumulative_affect_delta": self._cumulative_affect_delta,
            },
        )
        return timeline

    # ✅ TODO: integrate visualization metadata once front-end channel is available


def create_healix_widget(nodes: Sequence[Mapping[str, object]] | None = None) -> HealixWidget:
    """Factory helper for widget creation."""

    widget = HealixWidget(nodes)
    logger.debug("HealixWidget created via factory", extra={"has_nodes": bool(nodes)})
    return widget
