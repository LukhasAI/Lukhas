#!/usr/bin/env python3
"""
Wave C C4 GDPR Article 17 User Erasure Tool

Removes all user data from the Aka Qualia memory system in compliance
with GDPR Article 17 (Right to Erasure). Provides comprehensive logging
and verification of data removal.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_sql import SqlMemory
from sqlalchemy import create_engine, text


def count_user_data(engine, user_id_hash):
    """Count all data associated with a user."""
    with engine.connect() as conn:
        # Count scenes
        scene_count = conn.execute(
            text("""
            SELECT COUNT(*) FROM akaq_scene WHERE user_id = :user_id
        """),
            {"user_id": user_id_hash},
        ).scalar()

        # Count glyphs (via scenes)
        glyph_count = conn.execute(
            text("""
            SELECT COUNT(*) FROM akaq_glyph g
            JOIN akaq_scene s USING(scene_id)
            WHERE s.user_id = :user_id
        """),
            {"user_id": user_id_hash},
        ).scalar()

        # Count memory operations
        ops_count = conn.execute(
            text("""
            SELECT COUNT(*) FROM akaq_memory_ops WHERE user_id = :user_id
        """),
            {"user_id": user_id_hash},
        ).scalar()

    return {
        "scenes": scene_count,
        "glyphs": glyph_count,
        "memory_ops": ops_count,
        "total": scene_count + glyph_count + ops_count,
    }


def get_sample_scene_ids(engine, user_id_hash, limit=5):
    """Get sample scene IDs for verification."""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT scene_id, subject, created_at 
            FROM akaq_scene 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT :limit
        """),
            {"user_id": user_id_hash, "limit": limit},
        )

        return [{"scene_id": row[0], "subject": row[1], "created_at": row[2]} for row in result.fetchall()]


def erase_user_data(memory_client, user_id, dry_run=False):
    """Erase all user data using the memory client."""
    if dry_run:
        print("  🔍 DRY RUN: Would call memory.delete_user()")
        return 0

    print("  🗑️  Calling memory.delete_user()...")
    deleted_count = memory_client.delete_user(user_id)
    print(f"  ✅ Deleted {deleted_count} records")

    return deleted_count


def verify_erasure(engine, user_id_hash):
    """Verify all user data has been removed."""
    print("  🔍 Verifying complete erasure...")

    remaining_data = count_user_data(engine, user_id_hash)

    if remaining_data["total"] == 0:
        print("  ✅ Complete erasure verified - no user data remaining")
        return True
    else:
        print("  ❌ Erasure incomplete:")
        for data_type, count in remaining_data.items():
            if count > 0:
                print(f"    - {data_type}: {count} records remain")
        return False


def log_erasure_audit(engine, user_id, user_id_hash, deleted_count, success):
    """Log the erasure operation for audit trail."""
    with engine.connect() as conn:
        conn.execute(
            text("""
            INSERT INTO akaq_memory_ops (operation, user_id, metadata, timestamp)
            VALUES ('gdpr_erasure', :user_id_hash, :metadata, :timestamp)
        """),
            {
                "user_id_hash": user_id_hash,
                "metadata": f"{{'original_user_id': '{user_id}', 'deleted_count': {deleted_count}, 'success': {success}}}",
                "timestamp": datetime.now(timezone.utc),
            },
        )
        conn.commit()

    print("  📝 Audit trail logged for user erasure")


def main():
    parser = argparse.ArgumentParser(
        description="Wave C C4 GDPR Article 17 User Erasure Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run erasure
  python gdpr_erase_user.py --user-id user123 --db-url sqlite:///akaq_memory.db --dry-run
  
  # Execute erasure
  python gdpr_erase_user.py --user-id user123 --db-url sqlite:///akaq_memory.db
  
  # PostgreSQL with production salt
  python gdpr_erase_user.py --user-id user123 --db-url postgresql://user:pass@localhost/akaq --salt prod_salt
        """,
    )

    parser.add_argument("--user-id", required=True, help="User ID to erase (will be hashed in production mode)")
    parser.add_argument("--db-url", required=True, help="Database connection URL")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--salt", default="dev_salt", help="Salt for user ID hashing (default: dev_salt)")
    parser.add_argument("--prod-mode", action="store_true", help="Enable production mode (user ID hashing)")

    args = parser.parse_args()

    print("🛡️  Wave C C4 GDPR Article 17 User Erasure Tool")
    print(f"👤 User ID: {args.user_id}")
    print(f"📡 Database: {args.db_url}")
    print(f"🎯 Mode: {'DRY RUN' if args.dry_run else 'EXECUTE ERASURE'}")
    print(f"🔒 Production mode: {'ON (user ID will be hashed)' if args.prod_mode else 'OFF (plain user ID)'}")
    print()

    try:
        # Create engine and memory client
        engine = create_engine(args.db_url)
        memory = SqlMemory(engine=engine, rotate_salt=args.salt, is_prod=args.prod_mode)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")

        # Get user ID hash for direct queries
        user_id_hash = memory._hash_user_id(args.user_id) if args.prod_mode else args.user_id
        print(f"🔑 User identifier: {'<hashed>' if args.prod_mode else args.user_id}")

        # Count existing data
        print("📊 Analyzing user data...")
        data_counts = count_user_data(engine, user_id_hash)

        if data_counts["total"] == 0:
            print("  ℹ️  No data found for this user - nothing to erase")
            return 0

        print("  📋 Found data to erase:")
        print(f"    - Scenes: {data_counts['scenes']}")
        print(f"    - Glyphs: {data_counts['glyphs']}")
        print(f"    - Memory ops: {data_counts['memory_ops']}")
        print(f"    - Total records: {data_counts['total']}")

        # Show sample data
        if data_counts["scenes"] > 0:
            print("  📄 Sample scenes:")
            sample_scenes = get_sample_scene_ids(engine, user_id_hash)
            for scene in sample_scenes:
                print(f"    - {scene['scene_id']}: '{scene['subject']}' ({scene['created_at']})")

        print()

        if not args.dry_run:
            # Confirm erasure
            confirm = input("⚠️  This will PERMANENTLY DELETE all user data. Continue? (yes/no): ")
            if confirm.lower() not in ["yes", "y"]:
                print("🚫 Erasure cancelled by user")
                return 1

        # Perform erasure
        print("🗑️  Performing user data erasure...")
        deleted_count = erase_user_data(memory, args.user_id, dry_run=args.dry_run)

        if not args.dry_run:
            # Verify erasure
            success = verify_erasure(engine, user_id_hash)

            # Log audit trail
            log_erasure_audit(engine, args.user_id, user_id_hash, deleted_count, success)

            if success:
                print()
                print("✅ GDPR Article 17 erasure completed successfully!")
                print(f"📝 {deleted_count} records removed")
                print("🔍 Verification: No user data remaining")
                print("📋 Audit trail: Logged in akaq_memory_ops")
            else:
                print()
                print("❌ Erasure incomplete - manual investigation required")
                return 1
        else:
            print()
            print("🔍 DRY RUN completed - no actual data was deleted")
            print("💡 Run without --dry-run to perform actual erasure")

    except Exception as e:
        print(f"❌ Erasure failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
