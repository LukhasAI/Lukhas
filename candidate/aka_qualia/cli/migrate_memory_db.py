#!/usr/bin/env python3
"""
Wave C C4 Database Migration Tool

Manages database schema for the Aka Qualia memory system.
Supports SQLite and PostgreSQL with safe migration procedures.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_sql import SqlMemory
from sqlalchemy import create_engine, inspect, text


def get_current_schema_version(engine):
    """Get current schema version from metadata table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT version FROM akaq_schema_metadata
                ORDER BY applied_at DESC LIMIT 1
            """
                )
            )
            row = result.fetchone()
            return row[0] if row else None
    except Exception:
        # Table doesn't exist, schema version is 0
        return 0


def apply_migration_v1(engine):
    """Apply version 1 migration: create core tables."""
    print("  📋 Creating core tables (akaq_scene, akaq_glyph, akaq_memory_ops)")

    # Create memory client to apply migration
    memory = SqlMemory(engine=engine, rotate_salt="migration_salt", is_prod=False)
    memory._apply_migration()

    # Add schema metadata
    with engine.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS akaq_schema_metadata (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """
            )
        )

        conn.execute(
            text(
                """
            INSERT INTO akaq_schema_metadata (version, description)
            VALUES (1, 'Core tables: akaq_scene, akaq_glyph, akaq_memory_ops')
        """
            )
        )

        conn.commit()

    print("  ✅ Migration v1 applied successfully")


def verify_schema_integrity(engine):
    """Verify schema integrity and constraints."""
    print("  🔍 Verifying schema integrity...")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = [
        "akaq_scene",
        "akaq_glyph",
        "akaq_memory_ops",
        "akaq_schema_metadata",
    ]
    missing_tables = [table for table in required_tables if table not in tables]

    if missing_tables:
        print(f"  ❌ Missing tables: {missing_tables}")
        return False

    # Check foreign key constraints
    with engine.connect() as conn:
        # Verify scene-glyph relationship
        result = conn.execute(
            text(
                """
            SELECT COUNT(*) FROM akaq_glyph g
            LEFT JOIN akaq_scene s ON g.scene_id = s.scene_id
            WHERE s.scene_id IS NULL
        """
            )
        )
        orphaned_glyphs = result.scalar()

        if orphaned_glyphs > 0:
            print(f"  ⚠️  Found {orphaned_glyphs} orphaned glyphs")

    print("  ✅ Schema integrity verified")
    return True


def reset_database(engine, dry_run=False):
    """Reset database by dropping all tables."""
    if dry_run:
        print("  🔍 DRY RUN: Would drop all akaq_* tables")
        return

    print("  🗑️  Dropping all akaq_* tables...")

    with engine.connect() as conn:
        # Drop in correct order to handle foreign keys
        tables_to_drop = [
            "akaq_glyph",  # Has foreign key to akaq_scene
            "akaq_scene",
            "akaq_memory_ops",
            "akaq_schema_metadata",
        ]

        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"    ✅ Dropped {table}")
            except Exception as e:
                print(f"    ⚠️  Could not drop {table}: {e}")

        conn.commit()

    print("  ✅ Database reset completed")


def main():
    parser = argparse.ArgumentParser(
        description="Wave C C4 Database Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run migration
  python migrate_memory_db.py --db-url sqlite:///akaq_memory.db

  # Apply migration
  python migrate_memory_db.py --db-url sqlite:///akaq_memory.db --apply

  # Reset and migrate
  python migrate_memory_db.py --db-url sqlite:///akaq_memory.db --reset --apply

  # PostgreSQL
  python migrate_memory_db.py --db-url postgresql://user:pass@localhost/akaq_memory --apply
        """,
    )

    parser.add_argument(
        "--db-url",
        required=True,
        help="Database connection URL (sqlite:///path.db or postgresql://...)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply migrations (default: dry run)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database by dropping all tables first",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify schema integrity, no migrations",
    )

    args = parser.parse_args()

    print("🗄️  Wave C C4 Database Migration Tool")
    print(f"📡 Database: {args.db_url}")
    print(f"🎯 Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print()

    try:
        # Create engine
        engine = create_engine(args.db_url)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")

        if args.verify_only:
            verify_schema_integrity(engine)
            return

        # Reset if requested
        if args.reset:
            reset_database(engine, dry_run=not args.apply)

        # Check current schema version
        current_version = get_current_schema_version(engine)
        print(f"📊 Current schema version: {current_version}")

        # Apply migrations
        if current_version == 0:
            if args.apply:
                apply_migration_v1(engine)
                print("🚀 Migration to v1 completed")
            else:
                print("🔍 DRY RUN: Would apply migration v1 (core tables)")
        else:
            print("✅ Database is up to date")

        # Verify integrity
        if args.apply or current_version > 0:
            verify_schema_integrity(engine)

        print()
        print("🎯 Migration complete!")

        if not args.apply and current_version == 0:
            print("💡 Run with --apply to actually apply migrations")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
