"""
GDPR-Compliant Consent History Manager

This module implements a comprehensive consent history management system that
complies with GDPR Article 7(1) requirements for consent record keeping.

Features:
- Deterministic SHA-256 hashing of consent records
- Chronological storage with UTC timestamps
- Activity tracing for audit compliance
- Support for consent grant, withdrawal, revocation, and updates
- Immutable record keeping
- Multiple storage backends (in-memory, SQLite, PostgreSQL)
- GDPR Article 20 data portability (export functionality)

GDPR Compliance:
- Article 7(1): The controller shall be able to demonstrate that the data subject
  has consented to processing of his or her personal data.
- Article 20: Data portability - right to receive personal data in a structured,
  commonly used and machine-readable format.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol


class ConsentEventType(Enum):
    """Types of consent events."""

    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    REVOKED = "revoked"
    UPDATED = "updated"


class StorageBackend(Enum):
    """Available storage backend types."""

    MEMORY = "memory"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class TraceLogger(Protocol):
    """Protocol for trace logger interface."""

    def log_activity(self, user_id: str, activity: str, metadata: Dict[str, Any]) -> None:
        """Log an activity with metadata."""
        ...


class ConsentStorage(Protocol):
    """Protocol for consent storage backends."""

    def store_record(self, user_id: str, record: Dict[str, Any], record_hash: str) -> None:
        """Store a consent record."""
        ...

    def get_records(self, user_id: str, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve consent records for a user."""
        ...

    def get_latest_consent(self, user_id: str, scope: str) -> Optional[Dict[str, Any]]:
        """Get the latest consent record for a specific scope."""
        ...

    def close(self) -> None:
        """Close storage connections."""
        ...


class InMemoryStorage:
    """In-memory storage backend for testing."""

    def __init__(self) -> None:
        self._records: List[Dict[str, Any]] = []

    def store_record(self, user_id: str, record: Dict[str, Any], record_hash: str) -> None:
        """Store a consent record in memory."""
        self._records.append({
            "user_id": user_id,
            "record": record,
            "hash": record_hash
        })

    def get_records(self, user_id: str, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve consent records for a user."""
        records = [r for r in self._records if r["user_id"] == user_id]

        if start_time:
            records = [
                r for r in records
                if datetime.fromisoformat(r["record"]["timestamp"]) >= start_time
            ]

        # Sort chronologically
        records.sort(key=lambda x: x["record"]["timestamp"])
        return records

    def get_latest_consent(self, user_id: str, scope: str) -> Optional[Dict[str, Any]]:
        """Get the latest consent record for a specific scope."""
        records = self.get_records(user_id)

        # Filter by scope and get the latest
        scope_records = [
            r for r in records
            if r["record"]["scope_data"].get("scope") == scope
        ]

        if not scope_records:
            return None

        return scope_records[-1]  # Last record (most recent)

    def close(self) -> None:
        """No-op for in-memory storage."""
        pass


class SQLiteStorage:
    """SQLite storage backend for development."""

    def __init__(self, db_path: str = "consent_history.db") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS consent_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                scope_data TEXT NOT NULL,
                metadata TEXT NOT NULL,
                record_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Create indexes for efficient queries
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_timestamp
            ON consent_records(user_id, timestamp)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_scope
            ON consent_records(user_id, scope)
        """)

        self._conn.commit()

    def store_record(self, user_id: str, record: Dict[str, Any], record_hash: str) -> None:
        """Store a consent record in SQLite."""
        scope = record["scope_data"].get("scope", "")

        self._conn.execute("""
            INSERT INTO consent_records
            (user_id, timestamp, event_type, scope, scope_data, metadata, record_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            record["timestamp"],
            record["event_type"],
            scope,
            json.dumps(record["scope_data"]),
            json.dumps(record["metadata"]),
            record_hash
        ))
        self._conn.commit()

    def get_records(self, user_id: str, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve consent records for a user."""
        query = """
            SELECT user_id, timestamp, event_type, scope_data, metadata, record_hash
            FROM consent_records
            WHERE user_id = ?
        """
        params: List[Any] = [user_id]

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        query += " ORDER BY timestamp ASC"

        cursor = self._conn.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                "user_id": row["user_id"],
                "record": {
                    "timestamp": row["timestamp"],
                    "event_type": row["event_type"],
                    "scope_data": json.loads(row["scope_data"]),
                    "metadata": json.loads(row["metadata"])
                },
                "hash": row["record_hash"]
            }
            for row in rows
        ]

    def get_latest_consent(self, user_id: str, scope: str) -> Optional[Dict[str, Any]]:
        """Get the latest consent record for a specific scope."""
        cursor = self._conn.execute("""
            SELECT user_id, timestamp, event_type, scope_data, metadata, record_hash
            FROM consent_records
            WHERE user_id = ? AND scope = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (user_id, scope))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "user_id": row["user_id"],
            "record": {
                "timestamp": row["timestamp"],
                "event_type": row["event_type"],
                "scope_data": json.loads(row["scope_data"]),
                "metadata": json.loads(row["metadata"])
            },
            "hash": row["record_hash"]
        }

    def close(self) -> None:
        """Close database connection."""
        self._conn.close()


class PostgreSQLStorage:
    """PostgreSQL storage backend for production."""

    def __init__(self, connection_string: str) -> None:
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL storage. "
                "Install it with: pip install psycopg2-binary"
            )

        self._conn = psycopg2.connect(connection_string)
        self._conn.autocommit = False
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        import psycopg2

        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_records (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                event_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                scope_data JSONB NOT NULL,
                metadata JSONB NOT NULL,
                record_hash TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_timestamp
            ON consent_records(user_id, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_scope
            ON consent_records(user_id, scope)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scope_data
            ON consent_records USING GIN(scope_data)
        """)

        self._conn.commit()

    def store_record(self, user_id: str, record: Dict[str, Any], record_hash: str) -> None:
        """Store a consent record in PostgreSQL."""
        import psycopg2.extras

        scope = record["scope_data"].get("scope", "")
        cursor = self._conn.cursor()

        cursor.execute("""
            INSERT INTO consent_records
            (user_id, timestamp, event_type, scope, scope_data, metadata, record_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            record["timestamp"],
            record["event_type"],
            scope,
            psycopg2.extras.Json(record["scope_data"]),
            psycopg2.extras.Json(record["metadata"]),
            record_hash
        ))
        self._conn.commit()

    def get_records(self, user_id: str, start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve consent records for a user."""
        cursor = self._conn.cursor()

        query = """
            SELECT user_id, timestamp, event_type, scope_data, metadata, record_hash
            FROM consent_records
            WHERE user_id = %s
        """
        params: List[Any] = [user_id]

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)

        query += " ORDER BY timestamp ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                "user_id": row[0],
                "record": {
                    "timestamp": row[1].isoformat(),
                    "event_type": row[2],
                    "scope_data": row[3],
                    "metadata": row[4]
                },
                "hash": row[5]
            }
            for row in rows
        ]

    def get_latest_consent(self, user_id: str, scope: str) -> Optional[Dict[str, Any]]:
        """Get the latest consent record for a specific scope."""
        cursor = self._conn.cursor()

        cursor.execute("""
            SELECT user_id, timestamp, event_type, scope_data, metadata, record_hash
            FROM consent_records
            WHERE user_id = %s AND scope = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (user_id, scope))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "user_id": row[0],
            "record": {
                "timestamp": row[1].isoformat(),
                "event_type": row[2],
                "scope_data": row[3],
                "metadata": row[4]
            },
            "hash": row[5]
        }

    def close(self) -> None:
        """Close database connection."""
        self._conn.close()


class ConsentHistoryManager:
    """
    GDPR-compliant consent history manager.

    Requirements:
    - Deterministic SHA-256 hashing of consent records
    - Chronological storage with timestamps
    - Activity tracing for audit compliance
    - Support for consent grant, withdrawal, revocation
    - Immutable record keeping

    GDPR Compliance:
    - Article 7(1): Demonstrable consent
    - Article 20: Data portability
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        trace_logger: Optional[TraceLogger] = None
    ):
        """
        Initialize consent history manager.

        Args:
            config: Configuration dictionary with keys:
                - storage_backend: "memory", "sqlite", or "postgresql"
                - db_path: Path to SQLite database (for SQLite backend)
                - connection_string: PostgreSQL connection string (for PostgreSQL backend)
            trace_logger: Logger for activity tracing
        """
        self.config = config or {}
        self.trace_logger = trace_logger

        # Initialize storage backend
        backend_type = self.config.get("storage_backend", "memory")
        self._storage = self._init_storage(backend_type)

    def _init_storage(self, backend_type: str) -> ConsentStorage:
        """Initialize storage backend based on configuration."""
        if backend_type == "memory":
            return InMemoryStorage()
        elif backend_type == "sqlite":
            db_path = self.config.get("db_path", "consent_history.db")
            return SQLiteStorage(db_path)
        elif backend_type == "postgresql":
            connection_string = self.config.get("connection_string")
            if not connection_string:
                raise ValueError(
                    "PostgreSQL connection_string required in config"
                )
            return PostgreSQLStorage(connection_string)
        else:
            raise ValueError(
                f"Unsupported storage backend: {backend_type}. "
                f"Use 'memory', 'sqlite', or 'postgresql'."
            )

    def _generate_record_hash(self, record: Dict[str, Any], user_id: str) -> str:
        """
        Generate deterministic hash for consent record using SHA-256.

        The hash ensures data integrity and provides an immutable
        reference for each consent event.

        Args:
            record: Consent record to hash
            user_id: User identifier

        Returns:
            SHA-256 hash of record (hex string)
        """
        # Create deterministic string representation
        # Sort keys to ensure consistent ordering
        record_str = json.dumps(record, sort_keys=True, ensure_ascii=True)
        combined = f"{user_id}:{record_str}"

        # Generate SHA-256 hash
        hash_value = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        # Log activity if trace logger available
        if self.trace_logger:
            event_type = record.get("event_type", "unknown")
            self.trace_logger.log_activity(
                user_id,
                f"consent_{event_type}",
                {
                    "hash": hash_value,
                    "event_type": event_type,
                    "scope": record.get("scope_data", {}).get("scope"),
                    "timestamp": record.get("timestamp")
                }
            )

        return hash_value

    def add_record(
        self,
        user_id: str,
        event_type: str,
        scope_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add consent event and return hash.

        This method creates an immutable consent record with a cryptographic
        hash for audit trail purposes.

        Args:
            user_id: User identifier
            event_type: Type of consent event (granted, withdrawn, revoked, updated)
            scope_data: Consent scope information (must include 'scope' key)
            metadata: Additional metadata (e.g., IP address, user agent, reason)

        Returns:
            SHA-256 hash of the consent record

        Raises:
            ValueError: If event_type is invalid or scope_data is missing 'scope'
        """
        # Validate event type
        try:
            ConsentEventType(event_type)
        except ValueError:
            raise ValueError(
                f"Invalid event_type: {event_type}. "
                f"Must be one of: {[e.value for e in ConsentEventType]}"
            )

        # Validate scope_data
        if "scope" not in scope_data:
            raise ValueError("scope_data must contain 'scope' key")

        # Create record with UTC timestamp
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "scope_data": scope_data,
            "metadata": metadata or {}
        }

        # Generate deterministic hash
        record_hash = self._generate_record_hash(record, user_id)

        # Store record
        self._storage.store_record(user_id, record, record_hash)

        return record_hash

    def get_history(
        self,
        user_id: str,
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get consent history for user.

        Returns chronologically ordered consent records for audit purposes.

        Args:
            user_id: User identifier
            start_time: Optional start time to filter records (UTC)

        Returns:
            List of consent records with structure:
            [
                {
                    "user_id": str,
                    "record": {
                        "timestamp": str (ISO format),
                        "event_type": str,
                        "scope_data": dict,
                        "metadata": dict
                    },
                    "hash": str
                },
                ...
            ]
        """
        return self._storage.get_records(user_id, start_time)

    def verify_consent(self, user_id: str, scope: str) -> bool:
        """
        Verify active consent for scope.

        Checks if the user has active consent for the specified scope.
        Consent is considered active if the latest event for that scope
        is 'granted' or 'updated' (not 'withdrawn' or 'revoked').

        Args:
            user_id: User identifier
            scope: Consent scope to verify

        Returns:
            True if consent is active, False otherwise
        """
        latest = self._storage.get_latest_consent(user_id, scope)

        if not latest:
            return False

        event_type = latest["record"]["event_type"]

        # Consent is active if latest event is granted or updated
        return event_type in [
            ConsentEventType.GRANTED.value,
            ConsentEventType.UPDATED.value
        ]

    def revoke_consent(
        self,
        user_id: str,
        scope: str,
        reason: Optional[str] = None
    ) -> str:
        """
        Record consent revocation.

        Creates an administrative revocation record. This is different from
        user-initiated withdrawal.

        Args:
            user_id: User identifier
            scope: Consent scope to revoke
            reason: Optional reason for revocation

        Returns:
            SHA-256 hash of the revocation record
        """
        metadata = {}
        if reason:
            metadata["reason"] = reason
        metadata["revocation_type"] = "administrative"

        return self.add_record(
            user_id=user_id,
            event_type=ConsentEventType.REVOKED.value,
            scope_data={"scope": scope},
            metadata=metadata
        )

    def withdraw_consent(
        self,
        user_id: str,
        scope: str,
        reason: Optional[str] = None
    ) -> str:
        """
        Record user-initiated consent withdrawal.

        Args:
            user_id: User identifier
            scope: Consent scope to withdraw
            reason: Optional reason for withdrawal

        Returns:
            SHA-256 hash of the withdrawal record
        """
        metadata = {}
        if reason:
            metadata["reason"] = reason
        metadata["withdrawal_type"] = "user_initiated"

        return self.add_record(
            user_id=user_id,
            event_type=ConsentEventType.WITHDRAWN.value,
            scope_data={"scope": scope},
            metadata=metadata
        )

    def export_history(self, user_id: str) -> bytes:
        """
        Export consent history for GDPR Article 20 compliance (data portability).

        Returns consent history in a structured, machine-readable JSON format.

        Args:
            user_id: User identifier

        Returns:
            JSON-encoded consent history (UTF-8 bytes)
        """
        history = self.get_history(user_id)

        export_data = {
            "export_metadata": {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "total_records": len(history),
                "gdpr_article": "Article 20 - Right to data portability",
                "format": "application/json"
            },
            "consent_history": [
                {
                    "timestamp": record["record"]["timestamp"],
                    "event_type": record["record"]["event_type"],
                    "scope": record["record"]["scope_data"].get("scope"),
                    "scope_data": record["record"]["scope_data"],
                    "metadata": record["record"]["metadata"],
                    "record_hash": record["hash"]
                }
                for record in history
            ]
        }

        return json.dumps(export_data, indent=2, ensure_ascii=False).encode("utf-8")

    def get_consent_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of user's current consent status.

        Provides an overview of active and inactive consents.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with consent summary:
            {
                "user_id": str,
                "total_events": int,
                "active_consents": List[str],
                "withdrawn_consents": List[str],
                "revoked_consents": List[str],
                "last_updated": str (ISO format)
            }
        """
        history = self.get_history(user_id)

        # Track latest event per scope
        scope_status: Dict[str, Dict[str, Any]] = {}

        for record in history:
            scope = record["record"]["scope_data"].get("scope")
            if not scope:
                continue

            scope_status[scope] = {
                "event_type": record["record"]["event_type"],
                "timestamp": record["record"]["timestamp"]
            }

        # Categorize scopes
        active_consents = []
        withdrawn_consents = []
        revoked_consents = []

        for scope, status in scope_status.items():
            event_type = status["event_type"]
            if event_type in [ConsentEventType.GRANTED.value, ConsentEventType.UPDATED.value]:
                active_consents.append(scope)
            elif event_type == ConsentEventType.WITHDRAWN.value:
                withdrawn_consents.append(scope)
            elif event_type == ConsentEventType.REVOKED.value:
                revoked_consents.append(scope)

        # Get last update timestamp
        last_updated = history[-1]["record"]["timestamp"] if history else None

        return {
            "user_id": user_id,
            "total_events": len(history),
            "active_consents": sorted(active_consents),
            "withdrawn_consents": sorted(withdrawn_consents),
            "revoked_consents": sorted(revoked_consents),
            "last_updated": last_updated
        }

    def close(self) -> None:
        """Close storage connections."""
        self._storage.close()

    def __enter__(self) -> "ConsentHistoryManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


__all__ = [
    "ConsentHistoryManager",
    "ConsentEventType",
    "StorageBackend",
    "TraceLogger"
]
