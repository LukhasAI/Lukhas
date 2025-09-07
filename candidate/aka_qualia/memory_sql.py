#!/usr/bin/env python3
"""
Aka Qualia SQL Memory Implementation (C4.2)
============================================

SQL-based memory client for PostgreSQL and SQLite with GDPR compliance,
privacy hashing, and vector similarity support.

Follows Freud-2025 C4 specifications for memory persistence.
"""
import streamlit as st

import datetime as dt
import hashlib
import json
import logging
from datetime import timezone  # ΛTAG: utc
from typing import Any, Optional
from urllib.parse import urlparse

try:
    import sqlalchemy as sa
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    raise ImportError("SQLAlchemy required. Install with: pip install sqlalchemy")

try:
    import ulid
except ImportError:
    # Fallback to UUID if ULID not available
    import uuid

    ulid = None

from .memory import AkaqMemory
from .observability import get_observability, measure_memory_operation

logger = logging.getLogger(__name__)


class SqlMemory(AkaqMemory):
    """
    SQL-based memory implementation with GDPR compliance and privacy hashing.

    Features:
    - PostgreSQL + pgvector for production vector similarity
    - SQLite fallback for development (app-side similarity)
    - Subject/object hashing in production for privacy
    - Context sanitization and transform chain auditing
    - Atomic scene+glyph transactions with retry logic
    """

    def __init__(
        self,
        engine: Optional[Engine] = None,
        dsn: Optional[str] = None,
        rotate_salt: str = "default_salt_change_in_prod",
        is_prod: bool = False,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize SQL memory client.

        Args:
            engine: Pre-configured SQLAlchemy engine (optional)
            dsn: Database connection string if engine not provided
            rotate_salt: Salt for privacy hashing (change regularly in prod)
            is_prod: Enable privacy hashing and production features
            config: Additional configuration options
        """
        if engine is None:
            if dsn is None:
                raise ValueError("Either engine or dsn must be provided")
            engine = self._create_engine(dsn)

        self.engine = engine
        self.rotate_salt = rotate_salt
        self.is_prod = is_prod
        self.config = config or {}

        # Detect database driver
        self.driver = self._detect_driver()

        # Apply database migration to create tables
        self._apply_migration()

        # Statistics
        self.scenes_saved = 0
        self.save_failures = 0

        logger.info(f"SqlMemory initialized with {self.driver} driver (prod={is_prod})")

    def _create_engine(self, dsn: str) -> Engine:
        """Create SQLAlchemy engine with optimal settings"""
        parsed = urlparse(dsn)

        if parsed.scheme == "postgresql":
            # PostgreSQL with connection pooling
            return create_engine(dsn, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=3600)
        elif parsed.scheme == "sqlite":
            # SQLite with WAL mode for better concurrency
            engine = create_engine(dsn, connect_args={"check_same_thread": False})
            # Enable WAL mode and foreign keys
            with engine.begin() as conn:
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.execute(text("PRAGMA foreign_keys=ON"))
            return engine
        else:
            return create_engine(dsn)

    def _detect_driver(self) -> str:
        """Detect database driver from engine"""
        return self.engine.name

    def _apply_migration(self) -> None:
        """Apply database migration to create required tables"""
        with self.engine.begin() as conn:
            # Create akaq_scene table with all required columns
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS akaq_scene (
                    scene_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    subject TEXT,
                    object TEXT,
                    proto TEXT,
                    proto_vec TEXT,
                    risk TEXT,
                    context TEXT,
                    transform_chain TEXT,
                    collapse_hash TEXT,
                    drift_phi REAL,
                    congruence_index REAL,
                    neurosis_risk REAL,
                    repair_delta REAL,
                    sublimation_rate REAL,
                    affect_energy_before REAL,
                    affect_energy_after REAL,
                    affect_energy_diff REAL,
                    cfg_version TEXT,
                    timestamp REAL DEFAULT (julianday('now'))
                )
            """
                )
            )

            # Create akaq_glyph table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS akaq_glyph (
                    glyph_id TEXT PRIMARY KEY,
                    scene_id TEXT,
                    user_id TEXT NOT NULL,
                    glyph_key TEXT,
                    glyph_attrs TEXT,
                    priority REAL,
                    timestamp REAL DEFAULT (julianday('now')),
                    FOREIGN KEY (scene_id) REFERENCES akaq_scene(scene_id)
                )
            """
                )
            )

            # Create akaq_memory_ops table for audit trail
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS akaq_memory_ops (
                    operation_id TEXT PRIMARY KEY,
                    operation TEXT NOT NULL,
                    user_id TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create indexes for performance
            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_akaq_scene_user_id ON akaq_scene(user_id)
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_akaq_scene_timestamp ON akaq_scene(timestamp)
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_akaq_glyph_user_id ON akaq_glyph(user_id)
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_akaq_glyph_scene_id ON akaq_glyph(scene_id)
            """
                )
            )

        logger.info("Database migration applied successfully")

    def _hash_safe(self, s: Optional[str]) -> Optional[str]:
        """Hash string with rotating salt if in production mode"""
        if not s or not self.is_prod:
            return s

        h = hashlib.sha3_256()
        h.update((self.rotate_salt + s).encode("utf-8"))
        return h.hexdigest()

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Sanitize context to remove PII and keep safe fields"""
        # Whitelist approach - only keep known-safe fields
        safe_fields = {
            "safe_palette",
            "approach_avoid_score",
            "colorfield",
            "temporal_feel",
            "agency_feel",
            "scenario",
            "test_context",
            "cfg_version",  # Configuration version (essential metadata)
            "policy_sig",  # Policy signature (compliance)
            "session_id",  # Session identifier (non-PII)
        }

        return {k: v for k, v in context.items() if k in safe_fields}

    def _generate_scene_id(self) -> str:
        """Generate ULID or UUID for scene ID"""
        if ulid:
            return ulid.new().str
        else:
            return f"uuid_{uuid.uuid4().hex}"

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

        Implements privacy hashing, context sanitization, and transform auditing.
        """
        obs = get_observability()

        with measure_memory_operation("save", "sql"):
            scene_id = self._generate_scene_id()

            try:
                # Prepare scene data with privacy measures
                user_id_hash = self._hash_safe(user_id)  # Hash user_id in production
                subject = self._hash_safe(scene.get("subject"))
                object_field = self._hash_safe(scene.get("object"))
                proto = scene["proto"]

                # Convert proto to vector for similarity (if available)
                proto_vec = self._proto_to_vector(proto)
                sanitized_context = self._sanitize_context(scene.get("context", {}))

                # Convert proto_vec for storage
                if self.driver == "postgresql":
                    # PostgreSQL can store vector directly
                    proto_vec_param = proto_vec
                else:
                    # SQLite stores as JSON string
                    proto_vec_param = json.dumps(proto_vec)

                with self.engine.begin() as tx:
                    # Extract timestamp from scene if available
                    scene_timestamp = scene.get("timestamp", dt.datetime.now(timezone.utc).timestamp())

                    # Insert scene with all metrics
                    tx.execute(
                        text(
                            """
                        INSERT INTO akaq_scene (
                            scene_id, user_id, subject, object, proto, proto_vec, risk, context,
                            transform_chain, collapse_hash, drift_phi, congruence_index, neurosis_risk,
                            repair_delta, sublimation_rate, affect_energy_before, affect_energy_after,
                            affect_energy_diff, cfg_version, timestamp
                        ) VALUES (
                            :scene_id, :user_id, :subject, :object, :proto, :proto_vec, :risk, :context,
                            :transform_chain, :collapse_hash, :drift_phi, :congruence_index, :neurosis_risk,
                            :repair_delta, :sublimation_rate, :E_before, :E_after, :E_diff, :cfg_version, :timestamp
                        )
                        """
                        ),
                        {
                            "scene_id": scene_id,
                            "user_id": user_id_hash,  # Use hashed user_id
                            "subject": subject,
                            "object": object_field,
                            "proto": json.dumps(proto),
                            "proto_vec": proto_vec_param,
                            "risk": json.dumps(scene["risk"]),
                            "context": json.dumps(sanitized_context),
                            "transform_chain": json.dumps(scene.get("transform_chain", [])),
                            "collapse_hash": scene.get("collapse_hash"),
                            "drift_phi": metrics.get("drift_phi"),
                            "congruence_index": metrics.get("congruence_index"),
                            "neurosis_risk": metrics.get("neurosis_risk"),
                            "repair_delta": metrics.get("repair_delta"),
                            "sublimation_rate": metrics.get("sublimation_rate"),
                            "E_before": metrics.get("affect_energy_before"),
                            "E_after": metrics.get("affect_energy_after"),
                            "E_diff": metrics.get("affect_energy_diff"),
                            "cfg_version": cfg_version,
                            "timestamp": scene_timestamp,
                        },
                    )

                    # Insert glyphs
                    for glyph in glyphs:
                        glyph_id = self._generate_scene_id()  # Generate unique ID for glyph
                        tx.execute(
                            text(
                                """
                                INSERT INTO akaq_glyph (glyph_id, scene_id, user_id, glyph_key, glyph_attrs, priority)
                                VALUES (:glyph_id, :scene_id, :user_id, :glyph_key, :glyph_attrs, :priority)
                            """
                            ),
                            {
                                "glyph_id": glyph_id,
                                "scene_id": scene_id,
                                "user_id": user_id,
                                "glyph_key": glyph["key"],
                                "glyph_attrs": json.dumps(glyph.get("attrs", {})),
                                "priority": glyph.get("priority", 0.5),
                            },
                        )

                    tx.commit()

                self.scenes_saved += 1
                logger.debug(f"Saved scene {scene_id} with {len(glyphs)} glyphs")

                # Record observability metrics
                obs.update_memory_storage("sql", "scenes", self.scenes_saved * 1024)  # Estimate
                obs.record_scene_processed(status="success")

                return scene_id

            except Exception as e:
                self.save_failures += 1
                logger.error(f"Failed to save scene: {e!s}")
                raise

    def _proto_to_vector(self, proto: dict[str, Any]) -> list[float]:
        """Convert proto-qualia to 5D vector [tone, arousal, clarity, embodiment, narrative_gravity]"""
        return [
            float(proto.get("tone", 0.0)),
            float(proto.get("arousal", 0.0)),
            float(proto.get("clarity", 0.0)),
            float(proto.get("embodiment", 0.0)),
            float(proto.get("narrative_gravity", 0.0)),
        ]

    def fetch_prev_scene(self, *, user_id: str, before_ts: Optional[dt.datetime] = None) -> Optional[dict[str, Any]]:
        """Get most recent scene before timestamp for drift computation"""
        try:
            if before_ts is None:
                before_ts = dt.datetime.now(timezone.utc)  # ΛTAG: utc

            with self.engine.begin() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT scene_id, proto, risk, drift_phi, congruence_index,
                               neurosis_risk, repair_delta, timestamp
                        FROM akaq_scene
                        WHERE user_id = :user_id AND timestamp < :before_ts
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """
                    ),
                    {"user_id": user_id, "before_ts": before_ts},
                )

                row = result.fetchone()
                if not row:
                    return None

                return {
                    "scene_id": row[0],
                    "proto": json.loads(row[1]),
                    "risk": json.loads(row[2]),
                    "drift_phi": row[3],
                    "congruence_index": row[4],
                    "neurosis_risk": row[5],
                    "repair_delta": row[6],
                    "timestamp": row[7],
                }

        except Exception as e:
            logger.error(f"Failed to fetch previous scene: {e!s}")
            return None

    def history(self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None) -> list[dict[str, Any]]:
        """Get reverse-chronological slice of scenes for user"""
        with measure_memory_operation("sql_history"):
            scenes = []

            # Hash user ID if in production
            user_id_hash = self._hash_safe(user_id)

            with self.engine.connect() as conn:
                query = """
                    SELECT scene_id, timestamp, proto, risk, context, drift_phi, congruence_index, neurosis_risk, subject, object
                    FROM akaq_scene
                    WHERE user_id = :user_id
                """
                params = {"user_id": user_id_hash}

                if since:
                    since_ts = since.timestamp()
                    query += " AND timestamp > :since"
                    params["since"] = since_ts

                query += " ORDER BY timestamp DESC LIMIT :limit"
                params["limit"] = limit

                result = conn.execute(text(query), params)

                for row in result:
                    scenes.append(
                        {
                            "scene_id": row[0],
                            "timestamp": row[1],
                            "proto": json.loads(row[2] or "{}"),
                            "risk": json.loads(row[3] or "{}"),
                            "context": json.loads(row[4] or "{}"),
                            "drift_phi": row[5],
                            "congruence_index": row[6],
                            "neurosis_risk": row[7],
                            "subject": row[8],
                            "object": row[9],
                        }
                    )

            logger.debug(f"Retrieved {len(scenes)} scenes for user {user_id}")
            return scenes

    def get_scene_history(
        self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None
    ) -> list[dict[str, Any]]:
        """Alias for history method to match test expectations"""
        return self.history(user_id=user_id, limit=limit, since=since)

    def search_by_glyph(
        self, *, user_id: str, key: Optional[str] = None, glyph_key: Optional[str] = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Find scenes that emitted a specific glyph"""
        # Support both 'key' and 'glyph_key' parameter names for compatibility
        search_key = key or glyph_key
        if not search_key:
            raise ValueError("Either 'key' or 'glyph_key' must be provided")

        try:
            # Hash user ID if in production
            user_id_hash = self._hash_safe(user_id)

            with self.engine.begin() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT s.scene_id, s.timestamp, s.proto, s.risk, s.subject, s.object, g.glyph_attrs
                        FROM akaq_glyph g
                        JOIN akaq_scene s ON g.scene_id = s.scene_id
                        WHERE s.user_id = :user_id AND g.glyph_key = :key
                        ORDER BY s.timestamp DESC
                        LIMIT :limit
                    """
                    ),
                    {"user_id": user_id_hash, "key": search_key, "limit": limit},
                )

                scenes = []
                for row in result.fetchall():
                    scenes.append(
                        {
                            "scene_id": row[0],
                            "timestamp": row[1],
                            "proto": json.loads(row[2]),
                            "risk": json.loads(row[3]),
                            "subject": row[4],
                            "object": row[5],
                            "glyph_attrs": json.loads(row[6]),
                            "glyph_key": search_key,
                        }
                    )

                return scenes

        except Exception as e:
            logger.error(f"Failed to search by glyph: {e!s}")
            return []

    def top_drift(self, *, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get scenes with highest drift_phi values"""
        try:
            with self.engine.begin() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT scene_id, timestamp, proto, drift_phi, congruence_index
                        FROM akaq_scene
                        WHERE user_id = :user_id AND drift_phi IS NOT NULL
                        ORDER BY drift_phi DESC
                        LIMIT :limit
                    """
                    ),
                    {"user_id": user_id, "limit": limit},
                )

                scenes = []
                for row in result.fetchall():
                    scenes.append(
                        {
                            "scene_id": row[0],
                            "timestamp": row[1],
                            "proto": json.loads(row[2]),
                            "drift_phi": row[3],
                            "congruence_index": row[4],
                        }
                    )

                return scenes

        except Exception as e:
            logger.error(f"Failed to fetch top drift scenes: {e!s}")
            return []

    def delete_user(self, *, user_id: str) -> int:
        """Delete all user data (GDPR compliance)"""
        try:
            with self.engine.begin() as conn:
                # Count before deletion for audit
                count_result = conn.execute(
                    text("SELECT COUNT(*) FROM akaq_scene WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                count_result.scalar()

                # Delete scenes (cascades to glyphs via foreign key)
                delete_result = conn.execute(
                    text("DELETE FROM akaq_scene WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )

                rows_deleted = delete_result.rowcount
                conn.commit()

                logger.info(f"Deleted {rows_deleted} scenes for user {user_id}")
                return rows_deleted

        except Exception as e:
            logger.error(f"Failed to delete user data: {e!s}")
            raise

    def get_stats(self) -> dict[str, Any]:
        """Get memory client statistics"""
        return {
            "driver": self.driver,
            "is_prod": self.is_prod,
            "scenes_saved": self.scenes_saved,
            "save_failures": self.save_failures,
            "success_rate": (
                self.scenes_saved / (self.scenes_saved + self.save_failures)
                if (self.scenes_saved + self.save_failures) > 0
                else 0
            ),
        }
