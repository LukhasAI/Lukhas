#!/usr/bin/env python3
"""
Aka Qualia No-Op Memory Implementation (C4.2)
==============================================

No-operation memory client for testing and environments where persistence is not needed.
Provides the same interface as SqlMemory but stores nothing and returns empty results.
"""

import datetime as dt
import uuid
from typing import Any, Dict, List, Optional

from .memory import AkaqMemory


class NoopMemory(AkaqMemory):
    """
    No-operation memory implementation for testing and lightweight deployments.

    All operations are no-ops that return sensible defaults without persistence.
    Useful for:
    - Testing environments where persistence is not needed
    - Lightweight deployments without database requirements
    - Development/debugging where memory overhead should be minimal
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize no-op memory client"""
        self.driver = "noop"
        self.config = config or {}

        # Track operation counts for statistics
        self.save_calls = 0
        self.fetch_calls = 0
        self.search_calls = 0
        self.history_calls = 0
        self.delete_calls = 0

    def save(
        self,
        *,
        user_id: str,
        scene: Dict[str, Any],
        glyphs: List[Dict[str, Any]],
        policy: Dict[str, Any],
        metrics: Dict[str, Any],
        cfg_version: str,
    ) -> str:
        """
        Simulate saving scene data (no-op).

        Returns a fake scene ID but stores nothing.
        """
        self.save_calls += 1
        # Return a deterministic fake scene ID
        return f"noop_{uuid.uuid4().hex[:8]}"

    def fetch_prev_scene(self, *, user_id: str, before_ts: Optional[dt.datetime] = None) -> Optional[Dict[str, Any]]:
        """
        Simulate fetching previous scene (no-op).

        Always returns None since no data is stored.
        """
        self.fetch_calls += 1
        return None

    def history(self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None) -> List[Dict[str, Any]]:
        """
        Simulate fetching scene history (no-op).

        Always returns empty list since no data is stored.
        """
        self.history_calls += 1
        return []

    def search_by_glyph(self, *, user_id: str, key: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Simulate glyph-based search (no-op).

        Always returns empty list since no data is stored.
        """
        self.search_calls += 1
        return []

    def top_drift(self, *, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simulate top drift analysis (no-op).

        Always returns empty list since no data is stored.
        """
        return []

    def delete_user(self, *, user_id: str) -> int:
        """
        Simulate user data deletion (no-op).

        Always returns 0 since no data is stored.
        """
        self.delete_calls += 1
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get no-op memory client statistics"""
        return {
            "driver": self.driver,
            "is_prod": False,
            "scenes_saved": self.save_calls,
            "save_failures": 0,
            "success_rate": 1.0,
            "operation_counts": {
                "save_calls": self.save_calls,
                "fetch_calls": self.fetch_calls,
                "search_calls": self.search_calls,
                "history_calls": self.history_calls,
                "delete_calls": self.delete_calls,
            },
        }
