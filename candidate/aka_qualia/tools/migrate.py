#!/usr/bin/env python3
"""
Aka Qualia Database Migration Tool (C4.1)
==========================================

Creates database schema for scene persistence with PostgreSQL and SQLite support.
Follows Freud-2025 C4 specifications for consciousness memory architecture.

Usage:
    python -m candidate.aka_qualia.tools.migrate --dsn "sqlite:///./data/akaq.db"
    python -m candidate.aka_qualia.tools.migrate --dsn "postgresql://user:pass@host/db"
"""
import time
import streamlit as st

import argparse
import logging
from typing import Any
from urllib.parse import urlparse

try:
    from sqlalchemy import (
        JSON,
        Boolean,
        Column,
        DateTime,
        Float,
        Integer,
        MetaData,
        String,
        Table,
        Text,
        create_engine,
        text,
    )
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    raise ImportError("SQLAlchemy required. Install with: pip install sqlalchemy psycopg2-binary")

logger = logging.getLogger(__name__)

# Migration version for schema compatibility
MIGRATION_VERSION = "1.0.0"

# PostgreSQL schema with pgvector support
POSTGRESQL_SCHEMA = """
-- Aka Qualia Phenomenological Scene Storage (PostgreSQL + pgvector)
-- Migration Version: {version}

-- Enable pgvector extension for vector similarity operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Main scene storage table
CREATE TABLE IF NOT EXISTS akaq_scene (
    scene_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    ts TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Core phenomenological data
    subject VARCHAR(256),
    object VARCHAR(256),
    proto JSON NOT NULL,
    proto_vec vector(5),  -- 5D proto-qualia vector for similarity
    risk JSON NOT NULL,
    context JSON,

    -- Consciousness tracking
    transform_chain JSON,
    collapse_hash VARCHAR(64),

    -- Freud-2025 metrics
    drift_phi FLOAT,
    congruence_index FLOAT,
    neurosis_risk FLOAT,
    repair_delta FLOAT,
    sublimation_rate FLOAT,

    -- Energy accounting
    affect_energy_before FLOAT,
    affect_energy_after FLOAT,
    affect_energy_diff FLOAT,

    -- Versioning and metadata
    cfg_version VARCHAR(32),

    -- Indexes for performance
    INDEX(user_id),
    INDEX(ts),
    INDEX(drift_phi),
    INDEX(cfg_version)
);

-- GLYPH storage table (one-to-many with scenes)
CREATE TABLE IF NOT EXISTS akaq_glyph (
    glyph_id SERIAL PRIMARY KEY,
    scene_id VARCHAR(32) REFERENCES akaq_scene(scene_id) ON DELETE CASCADE,
    key VARCHAR(128) NOT NULL,
    attrs JSON,

    INDEX(scene_id),
    INDEX(key)
);

-- Vector similarity index for proto-qualia search
CREATE INDEX IF NOT EXISTS akaq_scene_proto_vec_idx ON akaq_scene
USING ivfflat (proto_vec vector_cosine_ops) WITH (lists = 100);

-- Compound indexes for common queries
CREATE INDEX IF NOT EXISTS akaq_scene_user_ts_idx ON akaq_scene(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS akaq_scene_drift_desc_idx ON akaq_scene(user_id, drift_phi DESC);
CREATE INDEX IF NOT EXISTS akaq_glyph_key_idx ON akaq_glyph(key, scene_id);
"""

# SQLite schema (no vector extension, app-side similarity)
SQLITE_SCHEMA = """
-- Aka Qualia Phenomenological Scene Storage (SQLite)
-- Migration Version: {version}

-- Main scene storage table
CREATE TABLE IF NOT EXISTS akaq_scene (
    scene_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subject TEXT,
    object TEXT,
    proto TEXT NOT NULL,
    proto_vec TEXT,
    risk TEXT NOT NULL,
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
    cfg_version TEXT
);

-- GLYPH storage table (one-to-many with scenes)
CREATE TABLE IF NOT EXISTS akaq_glyph (
    glyph_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scene_id TEXT REFERENCES akaq_scene(scene_id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    attrs TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_akaq_scene_user_id ON akaq_scene(user_id);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_ts ON akaq_scene(ts);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_user_ts ON akaq_scene(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_drift ON akaq_scene(user_id, drift_phi DESC);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_cfg ON akaq_scene(cfg_version);

CREATE INDEX IF NOT EXISTS idx_akaq_glyph_scene ON akaq_glyph(scene_id);
CREATE INDEX IF NOT EXISTS idx_akaq_glyph_key ON akaq_glyph(key);
CREATE INDEX IF NOT EXISTS idx_akaq_glyph_key_scene ON akaq_glyph(key, scene_id);

-- Enable foreign key constraints
PRAGMA foreign_keys=ON;
"""


def detect_database_driver(dsn: str) -> str:
    """Detect database driver from DSN"""
    parsed = urlparse(dsn)
    return parsed.scheme.lower()


def apply_migration(engine: Engine, config: dict[str, Any]) -> None:
    """Apply appropriate migration based on database driver"""
    driver = config["driver"]
    logging.info(f"Applying {driver} migration for Aka Qualia v{MIGRATION_VERSION}")

    try:
        with engine.begin() as conn:
            if driver == "postgresql":
                # Check pgvector availability
                try:
                    conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
                    logging.info("pgvector extension detected")
                except SQLAlchemyError:
                    logging.warning("pgvector not available - installing if possible")

                # Apply PostgreSQL schema
                schema_sql = POSTGRESQL_SCHEMA.format(version=MIGRATION_VERSION)
                # Execute as single statement to handle dependencies properly
                conn.execute(text(schema_sql))

                logging.info("PostgreSQL schema applied successfully")

            elif driver == "sqlite":
                # Apply SQLite schema statement by statement (SQLite needs this)
                schema_sql = SQLITE_SCHEMA.format(version=MIGRATION_VERSION)
                statements = []

                # Parse statements more carefully
                current_statement = []
                for line in schema_sql.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("--"):
                        continue

                    current_statement.append(line)

                    if line.endswith(";"):
                        statement = " ".join(current_statement).rstrip(";")
                        if statement:
                            statements.append(statement)
                        current_statement = []

                # Execute statements in order
                for statement in statements:
                    try:
                        conn.execute(text(statement))
                    except SQLAlchemyError as e:
                        if "already exists" in str(e):
                            logging.debug(f"Ignoring existing object: {e!s}")
                        else:
                            raise

                logging.info("SQLite schema applied successfully")

            else:
                raise ValueError(f"Unsupported database driver: {driver}")

            conn.commit()

    except SQLAlchemyError as e:
        logging.error(f"Migration failed: {e}")
        raise


def validate_schema(engine: Engine, config: dict[str, Any]) -> bool:
    """Validate that schema was applied correctly"""
    driver = config["driver"]

    try:
        with engine.begin() as conn:
            # Check main tables exist
            if driver == "postgresql":
                result = conn.execute(
                    text(
                        """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('akaq_scene', 'akaq_glyph')
                    ORDER BY table_name
                """
                    )
                )
            else:  # SQLite
                result = conn.execute(
                    text(
                        """
                    SELECT name FROM sqlite_master
                    WHERE type='table'
                    AND name IN ('akaq_scene', 'akaq_glyph')
                    ORDER BY name
                """
                    )
                )

            tables = [row[0] for row in result.fetchall()]
            expected = ["akaq_glyph", "akaq_scene"]

            if tables == expected:
                logging.info(f"Schema validation passed: {tables}")
                return True
            else:
                logging.error(f"Schema validation failed. Expected {expected}, got {tables}")
                return False

    except SQLAlchemyError as e:
        logging.error(f"Schema validation error: {e}")
        return False


def main():
    """CLI entry point for migration tool"""
    parser = argparse.ArgumentParser(description="Aka Qualia Database Migration Tool")
    parser.add_argument(
        "--dsn",
        required=True,
        help="Database connection string (e.g., sqlite:///./data/akaq.db)",
    )
    parser.add_argument("--validate", action="store_true", help="Validate schema after migration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Create engine and detect driver
    engine = create_engine(args.dsn)
    driver = detect_database_driver(args.dsn)
    config = {"driver": driver}

    logging.info(f"Starting migration for {driver} database")
    logging.info(f"DSN: {args.dsn}")

    try:
        # Apply migration
        apply_migration(engine, config)

        # Validate if requested
        if args.validate:
            if validate_schema(engine, config):
                logging.info("✅ Migration completed successfully")
            else:
                logging.error("❌ Migration validation failed")
                exit(1)
        else:
            logging.info("✅ Migration completed (use --validate to verify)")

    except Exception as e:
        logging.error(f"❌ Migration failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
