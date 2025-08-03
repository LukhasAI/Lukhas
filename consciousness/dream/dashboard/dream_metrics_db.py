import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class DreamMetricsDB:
    """# ΛTAG: metrics_db
    Store dream scoring metrics in a SQLite database."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = Path(db_path or "dream_metrics.db")
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dream_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dream_id TEXT NOT NULL,
                    drift_score REAL,
                    entropy_delta REAL,
                    alignment_score REAL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dream_id
                ON dream_metrics(dream_id)
                """
            )
            conn.commit()

    def add_dream_metrics(
        self,
        dream_id: str,
        drift_score: float,
        entropy_delta: float,
        alignment_score: float,
        timestamp: Optional[str] = None,
    ) -> None:
        """Insert metrics for a dream."""
        ts = timestamp or datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO dream_metrics
                    (dream_id, drift_score, entropy_delta, alignment_score, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (dream_id, drift_score, entropy_delta, alignment_score, ts),
            )
            conn.commit()

