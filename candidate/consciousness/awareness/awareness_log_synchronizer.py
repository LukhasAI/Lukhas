"""Awareness log synchronization with tier gating."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from lukhas.tiers import GlobalTier

logger = logging.getLogger(__name__)


class AwarenessLogSynchronizer:
    """Synchronize claude consciousness logs with tier-based access gating.

    # \u039bTAG: awareness_tier_sync
    """

    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.instance_logger = logger.getChild(self.__class__.__name__)
        self.instance_logger.debug(
            "\u039bTRACE: Initialized AwarenessLogSynchronizer", log_path=str(self.log_path)
        )

    def _read_logs(self) -> List[Dict[str, Any]]:
        """Read raw log entries.

        Returns:
            list[dict[str, Any]]: parsed log entries; malformed lines skipped.

        # \u039bTAG: log_read
        """
        entries: List[Dict[str, Any]] = []
        if not self.log_path.exists():
            self.instance_logger.warning("\u039bTRACE: Log file not found", path=str(self.log_path))
            return entries
        for line in self.log_path.read_text().splitlines():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                self.instance_logger.warning("\u039bTRACE: Malformed log line skipped", line=line)
        return entries

    def sync_for_user(self, user_id: str, requester_tier: GlobalTier) -> List[Dict[str, Any]]:
        """Return log entries visible to requester tier, marking boundaries.

        # \u039bTAG: tier_sync
        """
        visible: List[Dict[str, Any]] = []
        for entry in self._read_logs():
            if entry.get("user_id") != user_id:
                continue
            entry_tier = GlobalTier(entry.get("tier", GlobalTier.PUBLIC.value))
            if entry_tier.value <= requester_tier.value:
                if requester_tier.value >= GlobalTier.ELEVATED.value and "summary" in entry:
                    # Second-tier expansion: attach summary for elevated access
                    entry["expansion"] = entry["summary"]
                visible.append(entry)
            else:
                visible.append(
                    {
                        "restricted": True,
                        "reason": "tier_boundary",
                        "required_tier": entry_tier.value,
                    }
                )
        return visible

    # TODO: integrate driftScore and affect_delta metrics for deeper analytics
