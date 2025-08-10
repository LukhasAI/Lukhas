#!/usr/bin/env python3
"""
Consent Path Logger - Immutable audit trail of consent decisions
Maps glyph sequences to actions with cryptographic proof
"""

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ConsentEntry:
    """Single consent decision in the path"""

    timestamp: datetime
    user_id: str
    glyphs: List[str]
    action: str
    outcome: str
    drift_score: float
    consent_hash: str
    parent_hash: Optional[str]
    metadata: Dict

    def compute_hash(self) -> str:
        """Compute SHA3-256 hash of consent entry"""
        content = {
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "glyphs": "".join(self.glyphs),
            "action": self.action,
            "outcome": self.outcome,
            "parent_hash": self.parent_hash or "genesis",
        }
        json_str = json.dumps(content, sort_keys=True)
        return hashlib.sha3_256(json_str.encode()).hexdigest()

    def to_symbolic_notation(self) -> str:
        """Convert to symbolic notation for logging"""
        glyph_str = "".join(self.glyphs)
        return f"{glyph_str} → {self.action} → {self.outcome}"


class ConsentPathLogger:
    """
    Immutable logger for consent decisions with blockchain-like structure
    Each entry references the previous one, creating an audit chain
    """

    def __init__(self, db_path: str = "trusthelix_consent.db"):
        self.db_path = db_path
        self.genesis_hash = self._get_or_create_genesis()
        logger.info(
            f"📝 Consent Path Logger initialized with genesis: {self.genesis_hash[:16]}..."
        )

    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consent_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    glyphs TEXT NOT NULL,
                    action TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    drift_score REAL NOT NULL,
                    consent_hash TEXT UNIQUE NOT NULL,
                    parent_hash TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_user_id ON consent_paths(user_id)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_consent_hash ON consent_paths(consent_hash)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp ON consent_paths(timestamp)
            """
            )

    def _get_or_create_genesis(self) -> str:
        """Get or create genesis entry"""
        # Create a new connection for this operation
        conn = sqlite3.connect(self.db_path)

        # Ensure tables exist
        self._init_database()

        cursor = conn.execute(
            "SELECT consent_hash FROM consent_paths WHERE parent_hash IS NULL LIMIT 1"
        )
        result = cursor.fetchone()

        if result:
            conn.close()
            return result[0]

        # Create genesis entry
        genesis = ConsentEntry(
            timestamp=datetime.utcnow(),
            user_id="system",
            glyphs=["🌿", "🪷", "🔐"],
            action="genesis",
            outcome="initialized",
            drift_score=0.0,
            consent_hash="",
            parent_hash=None,
            metadata={"type": "genesis", "version": "1.0.0"},
        )
        genesis.consent_hash = genesis.compute_hash()

        self._save_entry(genesis, conn)
        conn.close()
        return genesis.consent_hash

    def _save_entry(
        self, entry: ConsentEntry, conn: Optional[sqlite3.Connection] = None
    ):
        """Save entry to database"""
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            close_conn = True
        else:
            close_conn = False

        try:
            conn.execute(
                """
                INSERT INTO consent_paths 
                (timestamp, user_id, glyphs, action, outcome, drift_score, 
                 consent_hash, parent_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.timestamp.isoformat(),
                    entry.user_id,
                    json.dumps(entry.glyphs),
                    entry.action,
                    entry.outcome,
                    entry.drift_score,
                    entry.consent_hash,
                    entry.parent_hash,
                    json.dumps(entry.metadata),
                ),
            )
            conn.commit()
        finally:
            if close_conn:
                conn.close()

    def log_consent(
        self,
        user_id: str,
        glyphs: List[str],
        action: str,
        outcome: str = "success",
        drift_score: float = 0.0,
        metadata: Dict = None,
    ) -> ConsentEntry:
        """Log a consent decision to the immutable chain"""
        # Get last entry for this user
        parent_hash = self._get_last_hash(user_id)

        # Create new entry
        entry = ConsentEntry(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            glyphs=glyphs,
            action=action,
            outcome=outcome,
            drift_score=drift_score,
            consent_hash="",  # Will be computed
            parent_hash=parent_hash,
            metadata=metadata or {},
        )

        # Compute hash including parent
        entry.consent_hash = entry.compute_hash()

        # Save to database
        self._save_entry(entry)

        # Log symbolic notation
        logger.info(
            f"✓ Consent logged: {entry.to_symbolic_notation()} [hash: {entry.consent_hash[:8]}...]"
        )

        return entry

    def _get_last_hash(self, user_id: str) -> str:
        """Get the last consent hash for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT consent_hash FROM consent_paths 
                   WHERE user_id = ? 
                   ORDER BY id DESC LIMIT 1""",
                (user_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else self.genesis_hash

    def get_user_path(self, user_id: str, limit: int = 100) -> List[ConsentEntry]:
        """Get consent path for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT timestamp, user_id, glyphs, action, outcome, 
                          drift_score, consent_hash, parent_hash, metadata
                   FROM consent_paths
                   WHERE user_id = ?
                   ORDER BY id DESC
                   LIMIT ?""",
                (user_id, limit),
            )

            entries = []
            for row in cursor.fetchall():
                entries.append(
                    ConsentEntry(
                        timestamp=datetime.fromisoformat(row[0]),
                        user_id=row[1],
                        glyphs=json.loads(row[2]),
                        action=row[3],
                        outcome=row[4],
                        drift_score=row[5],
                        consent_hash=row[6],
                        parent_hash=row[7],
                        metadata=json.loads(row[8]) if row[8] else {},
                    )
                )

            return list(reversed(entries))  # Return chronological order

    def verify_path_integrity(self, user_id: str) -> Tuple[bool, List[str]]:
        """Verify the integrity of a user's consent path"""
        path = self.get_user_path(user_id)
        errors = []

        if not path:
            return True, []

        # Check first entry links to genesis or valid parent
        if path[0].parent_hash not in [self.genesis_hash, None]:
            # Verify parent exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM consent_paths WHERE consent_hash = ?",
                    (path[0].parent_hash,),
                )
                if not cursor.fetchone():
                    errors.append(f"Invalid parent hash: {path[0].parent_hash[:16]}...")

        # Verify chain integrity
        for i in range(1, len(path)):
            if path[i].parent_hash != path[i - 1].consent_hash:
                errors.append(f"Chain broken at position {i}")

            # Recompute hash
            computed = path[i].compute_hash()
            if computed != path[i].consent_hash:
                errors.append(f"Hash mismatch at position {i}")

        return len(errors) == 0, errors

    def export_path_visualization(self, user_id: str) -> str:
        """Export path as visual representation"""
        path = self.get_user_path(user_id)

        if not path:
            return "No consent path found"

        lines = [f"📜 Consent Path for {user_id}"]
        lines.append("=" * 50)

        for i, entry in enumerate(path):
            # Create visual representation
            drift_indicator = (
                "🟢"
                if entry.drift_score < 0.3
                else "🟡" if entry.drift_score < 0.7 else "🔴"
            )

            lines.append(f"\n[{i+1}] {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"    {entry.to_symbolic_notation()}")
            lines.append(f"    Drift: {drift_indicator} {entry.drift_score:.3f}")
            lines.append(f"    Hash: {entry.consent_hash[:16]}...")

            if i < len(path) - 1:
                lines.append("    ↓")

        # Verify integrity
        valid, errors = self.verify_path_integrity(user_id)
        lines.append("\n" + "=" * 50)
        if valid:
            lines.append("✅ Path integrity verified")
        else:
            lines.append("❌ Path integrity violations:")
            for error in errors:
                lines.append(f"   - {error}")

        return "\n".join(lines)

    def generate_audit_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict:
        """Generate audit report for date range"""
        with sqlite3.connect(self.db_path) as conn:
            # Build query
            query = "SELECT * FROM consent_paths WHERE 1=1"
            params = []

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())

            cursor = conn.execute(query, params)
            entries = cursor.fetchall()

            # Analyze data
            total_entries = len(entries)
            unique_users = len(set(row[2] for row in entries))  # user_id column

            # Action distribution
            action_counts = {}
            outcome_counts = {"success": 0, "failure": 0, "partial": 0}

            for row in entries:
                action = row[4]  # action column
                outcome = row[5]  # outcome column

                action_counts[action] = action_counts.get(action, 0) + 1
                if outcome in outcome_counts:
                    outcome_counts[outcome] += 1

            # Average drift
            drift_scores = [row[6] for row in entries]  # drift_score column
            avg_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0.0

            return {
                "period": {
                    "start": start_date.isoformat() if start_date else "genesis",
                    "end": end_date.isoformat() if end_date else "current",
                },
                "summary": {
                    "total_entries": total_entries,
                    "unique_users": unique_users,
                    "average_drift": avg_drift,
                    "success_rate": (
                        outcome_counts["success"] / total_entries
                        if total_entries
                        else 0
                    ),
                },
                "action_distribution": action_counts,
                "outcome_distribution": outcome_counts,
                "generated_at": datetime.utcnow().isoformat(),
            }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize logger
    logger_instance = ConsentPathLogger(":memory:")  # Use in-memory DB for demo

    # Simulate consent logging
    user_id = "demo_user_001"

    # Log a sequence of actions
    logger_instance.log_consent(
        user_id, ["🔐", "🧬", "🪷"], "authenticate", "success", 0.1
    )
    logger_instance.log_consent(
        user_id, ["🔓", "🧬", "🌸"], "unlock_profile", "success", 0.15
    )
    logger_instance.log_consent(
        user_id, ["🔓", "🧬", "🌸"], "view_data", "success", 0.17
    )
    logger_instance.log_consent(
        user_id, ["🔒", "🦠", "🥀"], "suspicious_attempt", "failure", 0.45
    )

    # Get and display path
    print(logger_instance.export_path_visualization(user_id))

    # Generate audit report
    print("\n📊 Audit Report:")
    report = logger_instance.generate_audit_report()
    print(json.dumps(report, indent=2))
