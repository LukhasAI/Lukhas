#!/usr/bin/env python3
"""
Aka Qualia Memory Interface (C4.2)
===================================

Storage-agnostic memory client for Aka Qualia phenomenological scenes.
Following Freud-2025 C4 specifications for memory persistence and GDPR compliance.

Implementations:
- SqlMemory: PostgreSQL/SQLite with privacy hashing and vector similarity
- NoopMemory: No-op implementation for testing and development
"""

import datetime as dt
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AkaqMemory(ABC):
    """
    Storage-agnostic memory client interface.

    Implementations handle scene persistence, retrieval, and GDPR compliance
    with different storage backends (SQL, NoSQL, in-memory).
    """

    @abstractmethod
    def save(
        self,
        *,
        user_id: str,
        scene: dict[str, Any],
        glyphs: list[dict[str, Any]],
        policy: dict[str, Any],
        metrics: dict[str, Any],
        cfg_version: str,
    ) -> str:
        """
        Atomically persist scene+glyphs+metrics with full audit trail.

        Args:
            user_id: User identifier for scene ownership
            scene: Complete PhenomenalScene data including proto, risk, context
            glyphs: List of PhenomenalGlyph data generated for this scene
            policy: RegulationPolicy applied to this scene
            metrics: Computed consciousness metrics (drift_phi, congruence_index, etc.)
            cfg_version: Configuration version for reproducibility

        Returns:
            scene_id: ULID identifier for the stored scene

        Raises:
            MemoryError: If storage operation fails
        """
        pass

    @abstractmethod
    def fetch_prev_scene(self, *, user_id: str, before_ts: Optional[dt.datetime] = None) -> Optional[dict[str, Any]]:
        """
        Get most recent scene for user strictly before timestamp.

        Used for drift_phi computation and consciousness continuity.

        Args:
            user_id: User identifier
            before_ts: Timestamp boundary (defaults to now)

        Returns:
            Complete scene dict with proto, metrics, etc. or None if not found
        """
        pass

    @abstractmethod
    def history(self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None) -> list[dict[str, Any]]:
        """
        Get reverse-chronological slice of scenes for user.

        Args:
            user_id: User identifier
            limit: Maximum scenes to return
            since: Only return scenes after this timestamp

        Returns:
            List of scene dicts ordered by timestamp desc
        """
        pass

    @abstractmethod
    def search_by_glyph(self, *, user_id: str, key: str, limit: int = 50) -> list[dict[str, Any]]:
        """
        Find scenes that emitted a specific glyph key.

        Used for pattern analysis and consciousness archaeology.

        Args:
            user_id: User identifier
            key: GLYPH key to search for (e.g., "aka:vigilance")
            limit: Maximum scenes to return

        Returns:
            List of scene dicts that generated the specified glyph
        """
        pass

    @abstractmethod
    def top_drift(self, *, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get scenes with highest drift_phi (temporal incoherence events).

        Used for debugging consciousness continuity issues.

        Args:
            user_id: User identifier
            limit: Maximum scenes to return

        Returns:
            List of scene dicts ordered by drift_phi desc
        """
        pass

    @abstractmethod
    def delete_user(self, *, user_id: str) -> int:
        """
        Delete all data for user (GDPR "right to erasure").

        Args:
            user_id: User identifier

        Returns:
            Total number of records deleted (scenes + glyphs)
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get memory client statistics and health metrics"""
        pass


def create_memory_client(driver: str = "noop", **kwargs) -> AkaqMemory:
    """
    Factory function to create appropriate memory client.

    Args:
        driver: Memory backend type ("sql", "noop")
        **kwargs: Driver-specific configuration

    Returns:
        Configured memory client instance

    Examples:
        >>> # Development/testing
        >>> memory = create_memory_client("noop")

        >>> # SQLite development
        >>> memory = create_memory_client("sql", dsn="sqlite:///./data/akaq_dev.db", rotate_salt="dev_salt_123")

        >>> # PostgreSQL production
        >>> memory = create_memory_client(
        ...     "sql",
        ...     dsn="postgresql://lukhas:***@localhost:5432/lukhas",
        ...     rotate_salt=os.environ["AKAQ_ROTATE_SALT"],
        ...     is_prod=True,
        ... )
    """
    if driver == "noop":
        from memory_noop import NoopMemory

        return NoopMemory(**kwargs)
    elif driver == "sql":
        from memory_sql import SqlMemory

        return SqlMemory(**kwargs)
    else:
        raise ValueError(f"Unknown memory driver: {driver}. Use 'noop' or 'sql'")
