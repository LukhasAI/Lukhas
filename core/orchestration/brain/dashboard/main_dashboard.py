"""Main dashboard orchestrator for Healix monitoring."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Mapping, Optional, Sequence

from core.blockchain import BlockchainWrapper
from core.consciousness.drift_detector import DriftDetector
from core.emotion import EmotionMapper
from core.orchestration.brain.spine.accent_adapter import AccentAdapter
from core.orchestration.brain.spine.healix_mapper import HealixMapper
from core.widgets.healix_widget import HealixWidget, create_healix_widget

logger = logging.getLogger("healix_main_dashboard")


class HealixDashboard:
    """Coordinate Healix timeline, drift monitoring, and audit logging."""

    def __init__(
        self,
        *,
        accent_adapter: Optional[AccentAdapter] = None,
        emotion_mapper: Optional[EmotionMapper] = None,
        drift_detector: Optional[DriftDetector] = None,
        widget: Optional[HealixWidget] = None,
        blockchain: Optional[BlockchainWrapper] = None,
    ) -> None:
        self.accent_adapter = accent_adapter or AccentAdapter()
        self.emotion_mapper = emotion_mapper or EmotionMapper()
        self.healix_mapper = HealixMapper(self.accent_adapter, self.emotion_mapper)
        self.drift_detector = drift_detector or DriftDetector()
        self.widget = widget or create_healix_widget()
        self.blockchain = blockchain or BlockchainWrapper()
        # ΛTAG: driftScore - initial dashboard state registration
        logger.debug(
            "HealixDashboard initialized",
            extra={
                "tier": self.accent_adapter.tier,
                "drift_threshold": self.drift_detector.drift_threshold,
            },
        )

    def build_dashboard_state(
        self,
        user_id: str,
        *,
        baseline_state: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Build the dashboard snapshot for a given user."""

        helix_nodes = self.healix_mapper.map_helix_from_memory(user_id)
        self.widget.load_nodes(helix_nodes)
        timeline_points = [point.__dict__ for point in self.widget.render_timeline()]

        current_state = self._derive_current_state(helix_nodes)
        drift_summary = self.drift_detector.summarize(baseline_state, current_state)

        ledger_entry = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "driftScore": drift_summary["driftScore"],
            "affect_delta": drift_summary["affect_delta"],
        }
        self.blockchain.record_transaction(f"healix::{user_id}", ledger_entry)
        logger.info(
            "Healix dashboard state constructed",
            extra={
                "user_id": user_id,
                "driftScore": drift_summary["driftScore"],
                "timeline_points": len(timeline_points),
            },
        )
        return {
            "timeline": timeline_points,
            "drift": drift_summary,
            "ledger_length": len(self.blockchain.get_transactions()),
        }

    def _derive_current_state(self, nodes: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
        """Derive a symbolic current emotional state from helix nodes."""

        if not nodes:
            return {"emotion_vector": [0.0, 0.0, 0.0]}
        last = nodes[-1]
        intensity = float(last.get("intensity", 0.0))
        affect = float(last.get("affect_delta", intensity * 0.5))
        # ΛTAG: affect_delta - convert to simple 3d vector for drift detector
        vector = [intensity, affect, max(0.0, 1.0 - intensity)]
        logger.debug(
            "Current state derived",
            extra={"vector": vector, "source_hash": last.get("hash")},
        )
        return {"emotion_vector": vector}

    # ✅ TODO: add multi-user aggregation once orchestration demands it
