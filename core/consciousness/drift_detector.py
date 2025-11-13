"""Consciousness drift detection utilities for legacy consensus."""

from __future__ import annotations

import json
import logging
import sqlite3
from collections import defaultdict, deque
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Protocol

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


class DriftArchiveBackend(Protocol):
    """Protocol for drift history archival backends."""

    def archive_snapshot(self, snapshot: dict) -> str:
        """Archive a drift detection snapshot.

        Args:
            snapshot: Drift snapshot with layers, timestamps, metrics

        Returns:
            Archive ID for the stored snapshot
        """
        ...

    def query_archives(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        layer: str | None = None,
        min_drift: float | None = None,
    ) -> List[dict]:
        """Query archived drift snapshots."""
        ...


class FileDriftArchive:
    """File-based drift archive using JSON lines."""

    def __init__(self, archive_dir: Path):
        """Initialize file-based archive.

        Args:
            archive_dir: Directory to store archive files
        """
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self._current_file = self._get_current_archive_file()

    def _get_current_archive_file(self) -> Path:
        """Get current archive file (one per day)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.archive_dir / f"drift_archive_{today}.jsonl"

    def archive_snapshot(self, snapshot: dict) -> str:
        """Archive snapshot to JSON lines file."""
        archive_id = f"drift_{datetime.now(timezone.utc).isoformat()}"

        archive_entry = {
            "archive_id": archive_id,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "snapshot": snapshot,
        }

        # Append to daily archive file
        with open(self._current_file, "a") as f:
            f.write(json.dumps(archive_entry) + "\n")

        return archive_id

    def query_archives(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        layer: str | None = None,
        min_drift: float | None = None,
    ) -> List[dict]:
        """Query archived snapshots from JSON lines files."""
        results = []

        # Scan all archive files
        for archive_file in sorted(self.archive_dir.glob("drift_archive_*.jsonl")):
            with open(archive_file) as f:
                for line in f:
                    entry = json.loads(line)

                    # Apply filters
                    archived_at = datetime.fromisoformat(entry["archived_at"])
                    if start_time and archived_at < start_time:
                        continue
                    if end_time and archived_at > end_time:
                        continue

                    # Layer and drift filters require parsing snapshot
                    if layer or min_drift:
                        snapshot = entry["snapshot"]
                        if layer:
                            # Filter by layer presence
                            if layer not in snapshot.get("layers", {}):
                                continue
                        if min_drift:
                            # Filter by drift score
                            layers = snapshot.get("layers", {})
                            max_drift = max(
                                (layer_data.get("driftScore", 0) for layer_data in layers.values()),
                                default=0,
                            )
                            if max_drift < min_drift:
                                continue

                    results.append(entry)

        return results


class SQLiteDriftArchive:
    """SQLite-based drift archive with indexed queries."""

    def __init__(self, db_path: Path):
        """Initialize SQLite archive.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_archives (
                    archive_id TEXT PRIMARY KEY,
                    archived_at TIMESTAMP NOT NULL,
                    snapshot_json TEXT NOT NULL,
                    max_drift_score REAL,
                    layer_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_archived_at
                ON drift_archives(archived_at)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_max_drift
                ON drift_archives(max_drift_score)
            """)

            conn.commit()

    def archive_snapshot(self, snapshot: dict) -> str:
        """Archive snapshot to SQLite database."""
        archive_id = f"drift_{datetime.now(timezone.utc).isoformat()}"
        archived_at = datetime.now(timezone.utc).isoformat()

        # Extract metadata for indexing
        layers = snapshot.get("layers", {})
        max_drift_score = max(
            (layer_data.get("driftScore", 0) for layer_data in layers.values()), default=0
        )
        layer_count = len(layers)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO drift_archives
                (archive_id, archived_at, snapshot_json, max_drift_score, layer_count)
                VALUES (?, ?, ?, ?, ?)
            """,
                (archive_id, archived_at, json.dumps(snapshot), max_drift_score, layer_count),
            )
            conn.commit()

        return archive_id

    def query_archives(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        layer: str | None = None,
        min_drift: float | None = None,
    ) -> List[dict]:
        """Query archived snapshots with indexed filtering."""
        query = "SELECT archive_id, archived_at, snapshot_json FROM drift_archives WHERE 1=1"
        params: List = []

        if start_time:
            query += " AND archived_at >= ?"
            params.append(start_time.isoformat())
        if end_time:
            query += " AND archived_at <= ?"
            params.append(end_time.isoformat())
        if min_drift:
            query += " AND max_drift_score >= ?"
            params.append(min_drift)

        query += " ORDER BY archived_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            results = []

            for row in cursor:
                archive_id, archived_at, snapshot_json = row
                snapshot = json.loads(snapshot_json)

                # Additional layer filter (not indexed)
                if layer:
                    if layer not in snapshot.get("layers", {}):
                        continue

                results.append(
                    {"archive_id": archive_id, "archived_at": archived_at, "snapshot": snapshot}
                )

        return results


class ConsciousnessDriftDetector:
    """Track and summarize drift metrics across consciousness layers.

    Supports optional archival of drift history before clearing for audit
    and compliance purposes. Archives provide immutable, timestamped records
    of drift snapshots for reconciliation and historical analysis.
    """

    def __init__(
        self,
        retention: int = 12,
        archive_backend: DriftArchiveBackend | None = None,
        archive_on_reset: bool = True,
    ) -> None:
        """Initialize drift detector with optional archival.

        Args:
            retention: Number of snapshots to retain per layer
            archive_backend: Backend for archiving drift snapshots
            archive_on_reset: Whether to archive history on reset
        """
        self.retention = retention
        self._history: dict[str, deque[DriftSnapshot]] = defaultdict(
            lambda: deque(maxlen=self.retention)
        )
        self._logger = logger
        self._archive_backend = archive_backend
        self._archive_on_reset = archive_on_reset

        # Initialize default archive if none provided
        if archive_backend is None and archive_on_reset:
            # Use file-based archive by default
            archive_dir = Path("data/drift_archives")
            self._archive_backend = FileDriftArchive(archive_dir)

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

    def reset(self) -> str | None:
        """Clear all recorded history with optional archival.

        Returns:
            Archive ID if snapshot was archived, None otherwise
        """
        archive_id = None

        # Archive before clearing if enabled
        if self._archive_on_reset and self._archive_backend:
            try:
                snapshot = self.summarize_layers()
                archive_id = self._archive_backend.archive_snapshot(snapshot)

                self._logger.info(
                    "# ΛTAG: drift_reset -- archived drift history",
                    extra={
                        "archive_id": archive_id,
                        "layer_count": len(snapshot.get("layers", {})),
                    },
                )
            except Exception as e:
                self._logger.error(
                    f"# ΛTAG: drift_reset -- failed to archive: {e}", exc_info=True
                )

        # Clear history
        self._history.clear()
        self._logger.info("# ΛTAG: drift_reset -- cleared drift detector history")

        return archive_id

    def query_archived_snapshots(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        layer: str | None = None,
        min_drift: float | None = None,
    ) -> List[dict]:
        """Query archived drift snapshots.

        Args:
            start_time: Filter by minimum archive time
            end_time: Filter by maximum archive time
            layer: Filter by layer name
            min_drift: Filter by minimum drift score

        Returns:
            List of archived snapshots matching filters
        """
        if not self._archive_backend:
            self._logger.warning("No archive backend configured")
            return []

        return self._archive_backend.query_archives(
            start_time=start_time, end_time=end_time, layer=layer, min_drift=min_drift
        )


def get_drift_archive_backend(backend_type: str = "file", **kwargs) -> DriftArchiveBackend:
    """Factory for creating drift archive backends.

    Args:
        backend_type: Type of backend ("file" or "sqlite")
        **kwargs: Backend-specific configuration

    Returns:
        Configured archive backend

    Raises:
        ValueError: If backend_type is unknown
    """
    if backend_type == "file":
        archive_dir = kwargs.get("archive_dir", Path("data/drift_archives"))
        return FileDriftArchive(archive_dir)
    elif backend_type == "sqlite":
        db_path = kwargs.get("db_path", Path("data/drift_archives.db"))
        return SQLiteDriftArchive(db_path)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
