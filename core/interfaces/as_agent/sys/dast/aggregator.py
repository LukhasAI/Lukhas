"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                       LUKHΛS :: DAST AGGREGATOR MODULE                        │
│                     Version: v1.1 | Subsystem: DAST                          │
│       Collects and integrates symbolic tags from all active systems          │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This module aggregates symbolic signals, tags, and contextual markers from
    various sources including NIAS feedback, user gestures, partner widgets,
    emotional states, and memory overlays. It creates a unified context snapshot
    for downstream symbolic delivery and ethical evaluation.

Enhanced Core TypeScript - Integrated from Advanced Systems
Original: aggregator.py
Advanced: aggregator.py
Integration Date: 2025-05-31T07:55:30.569930
"""
from __future__ import annotations

import asyncio
from typing import Any

# Explicit imports replacing star imports per PEP8 guidelines # CLAUDE_EDIT_v0.8
# Since the constants.py file contains placeholder values and symbolic_utils.py
# doesn't have the referenced functions, we'll import what exists

# Import connectivity features with graceful degradation
try:
    from orchestration.golden_trio.trio_orchestrator import TrioOrchestrator
except ImportError:
    TrioOrchestrator = None

try:
    from dast.core.dast_engine import DASTEngine
except ImportError:
    DASTEngine = None

# TODO: Enable when hub dependencies are resolved
# from dast.integration.dast_integration_hub import get_dast_integration_hub


class DASTAggregator:
    """DAST component for aggregating symbolic tags with hub and orchestrator integration"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Orchestrator integration
        self.trio_orchestrator: TrioOrchestrator | None = None
        self.dast_engine = DASTEngine() if DASTEngine else None

        # Register with DAST integration hub (when available)
        self.dast_hub = None
        try:
            # TODO: Enable when hub dependencies are resolved
            # from dast.integration.dast_integration_hub import get_dast_integration_hub
            # self.dast_hub = get_dast_integration_hub()
            # asyncio.create_task(self.dast_hub.register_component(
            #     'aggregator',
            #     __file__,
            #     self
            # ))
            pass
        except ImportError:
            # Hub not available, continue without it
            pass

        # Component state
        self.active_tags: set[str] = set()
        self.aggregation_history: list[dict[str, Any]] = []

    async def register_with_trio(self) -> bool:
        """Register DAST aggregator with TrioOrchestrator"""
        if TrioOrchestrator is None:
            return False

        try:
            trio = TrioOrchestrator()
            await trio.register_component("dast_aggregator", self)
            self.trio_orchestrator = trio
            return True
        except Exception:
            return False

    def aggregate_symbolic_tags(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Merge symbolic tags from various DAST-compatible sources.

        Parameters:
        - inputs (dict): Dictionary with keys like 'gesture_tags', 'widget_tags', etc.

        Returns:
        - dict: Unified aggregation result with metadata
        """
        all_tags = set()
        for key in inputs:
            tags = inputs.get(key, [])
            if isinstance(tags, list):
                all_tags.update(tags)

        # Update component state
        self.active_tags = all_tags
        aggregation_result = {
            "timestamp": asyncio.get_event_loop().time(),
            "input_sources": list(inputs.keys()),
            "aggregated_tags": list(all_tags),
            "tag_count": len(all_tags),
        }

        self.aggregation_history.append(aggregation_result)

        return aggregation_result

    def get_status(self) -> dict[str, Any]:
        """Get aggregator status for hub monitoring"""
        return {
            "active_tags_count": len(self.active_tags),
            "aggregation_count": len(self.aggregation_history),
            "last_aggregation": (self.aggregation_history[-1] if self.aggregation_history else None),
            "trio_connected": self.trio_orchestrator is not None,
            "dast_engine_available": self.dast_engine is not None,
            "hub_connected": self.dast_hub is not None,
        }


# Global aggregator instance and orchestrator integration
_aggregator: DASTAggregator | None = None
trio_orchestrator: TrioOrchestrator | None = None
dast_engine = DASTEngine() if DASTEngine else None


def get_aggregator() -> DASTAggregator:
    """Get or create aggregator instance"""
    global _aggregator
    if _aggregator is None:
        _aggregator = DASTAggregator()
    return _aggregator


async def register_with_trio() -> bool:
    """Register DAST aggregator with TrioOrchestrator (global function for compatibility)"""
    global trio_orchestrator

    if TrioOrchestrator is None:
        return False

    try:
        trio = TrioOrchestrator()
        await trio.register_component("dast_aggregator", None)
        trio_orchestrator = trio
        return True
    except Exception:
        return False


# Backward compatibility functions


def aggregate_dast_tags(inputs: dict[str, Any]) -> dict[str, Any]:
    """Legacy function wrapper - delegates to DASTAggregator class"""
    aggregator = get_aggregator()
    return aggregator.aggregate_symbolic_tags(inputs)


def aggregate_symbolic_tags(inputs: dict[str, Any]) -> dict[str, Any]:
    """Legacy function wrapper - delegates to DASTAggregator class"""
    return aggregate_dast_tags(inputs)


"""
──────────────────────────────────────────────────────────────────────────────────────
NOTES:
    - This aggregator forms a central hub for all symbolic tag information across DAST
    - Enhanced with singleton pattern for state management and hub integration
    - Maintains backward compatibility through legacy function wrappers
    - Integrates with TrioOrchestrator and DASTEngine for advanced functionality
    - May integrate with partner_sdk or store modules for dynamic tag flows
──────────────────────────────────────────────────────────────────────────────────────
"""
