"""
Enhanced storage backend for feedback system.

Provides production-ready features:
- Connection pooling for better performance
- Batch operations for bulk inserts/updates
- Data retention policies with automatic cleanup
- Query optimization with prepared statements
- Transaction management for ACID guarantees
- Comprehensive error handling
- Backup and recovery utilities
- Performance monitoring

Task 2.3: Feedback Backend Storage (20 hours)
"""

import json
import logging
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator, Optional
from queue import Queue
import threading

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Configuration for feedback storage backend."""

    db_path: Path
    max_connections: int = 5  # Connection pool size
    connection_timeout: float = 30.0  # Seconds
    retention_days: int = 365  # Keep feedback for 1 year
    backup_interval_hours: int = 24  # Backup every 24 hours
    enable_wal_mode: bool = True  # Write-Ahead Logging for better concurrency
    enable_auto_vacuum: bool = True  # Automatic database cleanup
    checkpoint_interval: int = 1000  # WAL checkpoint every N transactions


class ConnectionPool:
    """
    Thread-safe connection pool for SQLite.

    Manages a pool of database connections to avoid repeated open/close overhead.
    """

    def __init__(self, db_path: Path, max_connections: int = 5, timeout: float = 30.0):
        """
        Initialize connection pool.

        Args:
            db_path: Path to SQLite database
            max_connections: Maximum number of pooled connections
            timeout: Connection timeout in seconds
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._created_connections = 0

        logger.info(f"Initialized connection pool: {max_connections} connections, timeout={timeout}s")

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimizations."""
        # Allow connection to be used across threads (for connection pool)
        conn = sqlite3.connect(str(self.db_path), timeout=self.timeout, check_same_thread=False)

        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")

        # Optimize performance
        conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety and performance
        conn.execute("PRAGMA cache_size=10000")  # 10MB cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")

        # Row factory for dict-like access
        conn.row_factory = sqlite3.Row

        logger.debug(f"Created new database connection: {self._created_connections + 1}")
        return conn

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """
        Get a connection from the pool (context manager).

        Yields:
            Database connection

        Example:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM feedback_cards")
        """
        conn = None
        try:
            # Try to get existing connection from pool
            try:
                conn = self._pool.get(block=False)
                logger.debug("Reused pooled connection")
            except:
                # Create new connection if pool is empty and under limit
                with self._lock:
                    if self._created_connections < self.max_connections:
                        conn = self._create_connection()
                        self._created_connections += 1
                    else:
                        # Wait for available connection
                        logger.debug("Waiting for available connection...")
                        conn = self._pool.get(timeout=self.timeout)

            yield conn

        finally:
            # Return connection to pool
            if conn:
                try:
                    # Rollback any uncommitted transactions
                    conn.rollback()
                    self._pool.put(conn, block=False)
                    logger.debug("Returned connection to pool")
                except:
                    # Pool is full or connection is broken, close it
                    conn.close()
                    with self._lock:
                        self._created_connections -= 1
                    logger.debug("Closed excess connection")

    def close_all(self):
        """Close all connections in the pool."""
        logger.info("Closing all pooled connections...")
        while not self._pool.empty():
            try:
                conn = self._pool.get(block=False)
                conn.close()
                with self._lock:
                    self._created_connections -= 1
            except:
                break
        logger.info(f"Closed {self._created_connections} connections")


class FeedbackStorageBackend:
    """
    Production-ready storage backend for feedback system.

    Features:
    - Connection pooling for performance
    - Batch operations for bulk processing
    - Data retention with automatic cleanup
    - Transaction management
    - Backup and recovery
    - Performance monitoring
    """

    def __init__(self, config: StorageConfig):
        """
        Initialize storage backend.

        Args:
            config: Storage configuration
        """
        self.config = config
        self.pool = ConnectionPool(
            config.db_path, max_connections=config.max_connections, timeout=config.connection_timeout
        )

        # Performance metrics
        self.metrics = {
            "queries_total": 0,
            "queries_success": 0,
            "queries_error": 0,
            "batch_operations": 0,
            "cleanup_runs": 0,
            "backups_created": 0,
        }

        # Initialize database schema
        self._init_schema()

        # Schedule background tasks
        self._last_cleanup = time.time()
        self._last_backup = time.time()
        self._transaction_count = 0

        logger.info(f"FeedbackStorageBackend initialized: {config.db_path}")

    def _init_schema(self):
        """Initialize database schema with optimizations."""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()

            # Create feedback table (if not exists)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback_cards (
                    card_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    interaction_id TEXT,
                    timestamp REAL NOT NULL,
                    user_input TEXT,
                    ai_response TEXT,
                    system_state TEXT,
                    feedback_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    prompt TEXT,
                    options TEXT,
                    rating INTEGER,
                    preference TEXT,
                    correction TEXT,
                    annotation TEXT,
                    validated INTEGER,
                    freeform_text TEXT,
                    user_id TEXT,
                    model_version TEXT,
                    experiment_id TEXT,
                    tags TEXT,
                    processed INTEGER DEFAULT 0,
                    impact_score REAL DEFAULT 0.0,
                    applied_to_training INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_session ON feedback_cards(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_user ON feedback_cards(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_category ON feedback_cards(category)",
                "CREATE INDEX IF NOT EXISTS idx_processed ON feedback_cards(processed)",
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback_cards(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_impact ON feedback_cards(impact_score DESC)",
                "CREATE INDEX IF NOT EXISTS idx_training ON feedback_cards(applied_to_training)",
                # Composite indexes for common queries
                "CREATE INDEX IF NOT EXISTS idx_user_timestamp ON feedback_cards(user_id, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_processed_impact ON feedback_cards(processed, impact_score DESC)",
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            # Create metadata table for system state
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS storage_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            logger.info("Database schema initialized with optimizations")

    def insert_feedback(self, card_data: dict[str, Any]) -> bool:
        """
        Insert a single feedback card.

        Args:
            card_data: Feedback card data dictionary

        Returns:
            True if successful
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO feedback_cards (
                        card_id, session_id, interaction_id, timestamp,
                        user_input, ai_response, system_state,
                        feedback_type, category, prompt, options,
                        rating, preference, correction, annotation,
                        validated, freeform_text,
                        user_id, model_version, experiment_id, tags,
                        processed, impact_score, applied_to_training
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        card_data.get("card_id"),
                        card_data.get("session_id"),
                        card_data.get("interaction_id"),
                        card_data.get("timestamp"),
                        card_data.get("user_input"),
                        card_data.get("ai_response"),
                        json.dumps(card_data.get("system_state", {})),
                        card_data.get("feedback_type"),
                        card_data.get("category"),
                        card_data.get("prompt"),
                        json.dumps(card_data.get("options", [])),
                        card_data.get("rating"),
                        card_data.get("preference"),
                        card_data.get("correction"),
                        card_data.get("annotation"),
                        card_data.get("validated"),
                        card_data.get("freeform_text"),
                        card_data.get("user_id"),
                        card_data.get("model_version"),
                        card_data.get("experiment_id"),
                        json.dumps(list(card_data.get("tags", []))),
                        card_data.get("processed", 0),
                        card_data.get("impact_score", 0.0),
                        card_data.get("applied_to_training", 0),
                    ),
                )

                conn.commit()
                self.metrics["queries_success"] += 1
                self.metrics["queries_total"] += 1
                self._transaction_count += 1

                self._maybe_checkpoint(conn)
                return True

        except Exception as e:
            logger.error(f"Error inserting feedback card: {e}", exc_info=True)
            self.metrics["queries_error"] += 1
            self.metrics["queries_total"] += 1
            return False

    def insert_batch(self, cards_data: list[dict[str, Any]]) -> int:
        """
        Insert multiple feedback cards in a single transaction.

        Args:
            cards_data: List of feedback card data dictionaries

        Returns:
            Number of cards successfully inserted
        """
        if not cards_data:
            return 0

        inserted = 0

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()

                for card_data in cards_data:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO feedback_cards (
                                card_id, session_id, interaction_id, timestamp,
                                user_input, ai_response, system_state,
                                feedback_type, category, prompt, options,
                                rating, preference, correction, annotation,
                                validated, freeform_text,
                                user_id, model_version, experiment_id, tags,
                                processed, impact_score, applied_to_training
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                card_data.get("card_id"),
                                card_data.get("session_id"),
                                card_data.get("interaction_id"),
                                card_data.get("timestamp"),
                                card_data.get("user_input"),
                                card_data.get("ai_response"),
                                json.dumps(card_data.get("system_state", {})),
                                card_data.get("feedback_type"),
                                card_data.get("category"),
                                card_data.get("prompt"),
                                json.dumps(card_data.get("options", [])),
                                card_data.get("rating"),
                                card_data.get("preference"),
                                card_data.get("correction"),
                                card_data.get("annotation"),
                                card_data.get("validated"),
                                card_data.get("freeform_text"),
                                card_data.get("user_id"),
                                card_data.get("model_version"),
                                card_data.get("experiment_id"),
                                json.dumps(list(card_data.get("tags", []))),
                                card_data.get("processed", 0),
                                card_data.get("impact_score", 0.0),
                                card_data.get("applied_to_training", 0),
                            ),
                        )
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"Failed to insert card {card_data.get('card_id')}: {e}")
                        continue

                conn.commit()
                self.metrics["batch_operations"] += 1
                self.metrics["queries_success"] += inserted
                self.metrics["queries_total"] += len(cards_data)
                self._transaction_count += 1

                logger.info(f"Batch inserted {inserted}/{len(cards_data)} feedback cards")

                self._maybe_checkpoint(conn)
                return inserted

        except Exception as e:
            logger.error(f"Error in batch insert: {e}", exc_info=True)
            self.metrics["queries_error"] += len(cards_data)
            self.metrics["queries_total"] += len(cards_data)
            return inserted

    def update_batch(self, updates: list[tuple[dict[str, Any], str]]) -> int:
        """
        Update multiple feedback cards in a single transaction.

        Args:
            updates: List of (update_data, card_id) tuples

        Returns:
            Number of cards successfully updated
        """
        if not updates:
            return 0

        updated = 0

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()

                for update_data, card_id in updates:
                    # Build dynamic UPDATE query
                    set_clauses = []
                    params = []

                    for key, value in update_data.items():
                        set_clauses.append(f"{key} = ?")
                        params.append(value)

                    if not set_clauses:
                        continue

                    params.append(card_id)
                    query = f"UPDATE feedback_cards SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE card_id = ?"

                    cursor.execute(query, params)
                    updated += cursor.rowcount

                conn.commit()
                self.metrics["batch_operations"] += 1
                self.metrics["queries_success"] += updated
                logger.info(f"Batch updated {updated}/{len(updates)} feedback cards")

                self._transaction_count += 1
                self._maybe_checkpoint(conn)
                return updated

        except Exception as e:
            logger.error(f"Error in batch update: {e}", exc_info=True)
            self.metrics["queries_error"] += len(updates)
            return updated

    def cleanup_old_data(self, retention_days: Optional[int] = None) -> int:
        """
        Remove feedback cards older than retention period.

        Args:
            retention_days: Days to keep data (uses config default if None)

        Returns:
            Number of records deleted
        """
        retention_days = retention_days or self.config.retention_days
        cutoff_timestamp = time.time() - (retention_days * 86400)

        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()

                # Delete old records
                cursor.execute(
                    """
                    DELETE FROM feedback_cards
                    WHERE timestamp < ?
                    AND applied_to_training = 1
                """,
                    (cutoff_timestamp,),
                )

                deleted = cursor.rowcount
                conn.commit()

                self.metrics["cleanup_runs"] += 1
                self._last_cleanup = time.time()

                logger.info(f"Cleaned up {deleted} feedback cards older than {retention_days} days")

                # Vacuum to reclaim space (if auto_vacuum is disabled)
                if not self.config.enable_auto_vacuum:
                    cursor.execute("VACUUM")
                    logger.info("Database vacuumed")

                return deleted

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}", exc_info=True)
            return 0

    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create a backup of the database.

        Args:
            backup_path: Optional custom backup path

        Returns:
            True if backup successful
        """
        if backup_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_path = self.config.db_path.parent / f"feedback_backup_{timestamp}.db"

        try:
            with self.pool.get_connection() as conn:
                # Use SQLite backup API
                backup_conn = sqlite3.connect(str(backup_path))
                conn.backup(backup_conn)
                backup_conn.close()

                self.metrics["backups_created"] += 1
                self._last_backup = time.time()

                logger.info(f"Database backed up to: {backup_path}")
                return True

        except Exception as e:
            logger.error(f"Error creating backup: {e}", exc_info=True)
            return False

    def _maybe_checkpoint(self, conn: sqlite3.Connection):
        """Perform WAL checkpoint if needed."""
        if self._transaction_count >= self.config.checkpoint_interval:
            try:
                conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                self._transaction_count = 0
                logger.debug("WAL checkpoint performed")
            except Exception as e:
                logger.warning(f"WAL checkpoint failed: {e}")

    def maybe_run_maintenance(self):
        """Run periodic maintenance tasks (cleanup, backup)."""
        current_time = time.time()

        # Cleanup old data
        cleanup_interval = 86400  # Daily
        if current_time - self._last_cleanup > cleanup_interval:
            self.cleanup_old_data()

        # Backup database
        backup_interval = self.config.backup_interval_hours * 3600
        if current_time - self._last_backup > backup_interval:
            self.backup_database()

    def get_metrics(self) -> dict[str, Any]:
        """Get storage performance metrics."""
        return {
            **self.metrics,
            "success_rate": self.metrics["queries_success"] / max(self.metrics["queries_total"], 1),
            "pool_size": self.pool._created_connections,
            "last_cleanup": self._last_cleanup,
            "last_backup": self._last_backup,
        }

    def close(self):
        """Close all connections and cleanup resources."""
        logger.info("Closing feedback storage backend...")
        self.pool.close_all()
        logger.info("Feedback storage backend closed")
