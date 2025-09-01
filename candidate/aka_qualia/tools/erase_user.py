#!/usr/bin/env python3
"""
GDPR-Compliant User Data Erasure Tool (C4.1)
=============================================

Implements "right to erasure" for Aka Qualia consciousness data.
Safely deletes all user scenes, glyphs, and associated metadata.

Usage:
    python -m candidate.aka_qualia.tools.erase_user --dsn "sqlite:///data/akaq.db" --user-id user123
    python -m candidate.aka_qualia.tools.erase_user --dsn "postgresql://..." --user-id user123 --audit
"""

import argparse
import json
import logging
from datetime import datetime
from typing import Any, Dict

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    raise ImportError("SQLAlchemy required. Install with: pip install sqlalchemy")

logger = logging.getLogger(__name__)


def count_user_data(engine: Engine, user_id: str) -> Dict[str, int]:
    """Count user data before deletion for audit purposes"""
    try:
        with engine.begin() as conn:
            # Count scenes
            scene_result = conn.execute(
                text("SELECT COUNT(*) FROM akaq_scene WHERE user_id = :user_id"), {"user_id": user_id}
            )
            scene_count = scene_result.scalar()

            # Count glyphs (via scenes)
            glyph_result = conn.execute(
                text("""
                    SELECT COUNT(*) FROM akaq_glyph g
                    JOIN akaq_scene s ON g.scene_id = s.scene_id
                    WHERE s.user_id = :user_id
                """),
                {"user_id": user_id},
            )
            glyph_count = glyph_result.scalar()

            return {"scenes": scene_count, "glyphs": glyph_count, "total_records": scene_count + glyph_count}

    except SQLAlchemyError as e:
        logger.error(f"Failed to count user data: {e}")
        raise


def delete_user_data(engine: Engine, user_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Delete all user data with cascade (scenes -> glyphs)"""
    try:
        with engine.begin() as conn:
            if dry_run:
                # For dry run, just count what would be deleted
                count_data = count_user_data(engine, user_id)
                return {
                    "dry_run": True,
                    "user_id": user_id,
                    "would_delete": count_data,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Get pre-deletion counts for audit
            pre_count = count_user_data(engine, user_id)

            # Perform actual deletion (cascades to glyphs via foreign key)
            delete_result = conn.execute(text("DELETE FROM akaq_scene WHERE user_id = :user_id"), {"user_id": user_id})

            rows_deleted = delete_result.rowcount
            conn.commit()

            return {
                "dry_run": False,
                "user_id": user_id,
                "pre_deletion_count": pre_count,
                "scenes_deleted": rows_deleted,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
            }

    except SQLAlchemyError as e:
        logger.error(f"Failed to delete user data: {e}")
        raise


def verify_deletion(engine: Engine, user_id: str) -> bool:
    """Verify that all user data has been successfully deleted"""
    try:
        post_count = count_user_data(engine, user_id)
        return post_count["total_records"] == 0
    except SQLAlchemyError as e:
        logger.error(f"Failed to verify deletion: {e}")
        return False


def log_audit_entry(audit_result: Dict[str, Any], audit_file: str = None) -> None:
    """Log audit entry for GDPR compliance"""
    if audit_file:
        try:
            with open(audit_file, "a") as f:
                f.write(json.dumps(audit_result) + "\n")
            logger.info(f"Audit entry logged to {audit_file}")
        except OSError as e:
            logger.error(f"Failed to write audit log: {e}")
    else:
        logger.info(f"Audit entry: {json.dumps(audit_result, indent=2)}")


def main():
    """CLI entry point for user data erasure"""
    parser = argparse.ArgumentParser(description="GDPR-Compliant User Data Erasure Tool")
    parser.add_argument("--dsn", required=True, help="Database connection string")
    parser.add_argument("--user-id", required=True, help="User ID to erase data for")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    parser.add_argument("--audit", action="store_true", help="Enable audit logging")
    parser.add_argument("--audit-file", help="Audit log file path (default: print to console)")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Create database engine
    engine = create_engine(args.dsn)

    logger.info("GDPR User Data Erasure Tool")
    logger.info(f"DSN: {args.dsn}")
    logger.info(f"User ID: {args.user_id}")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE DELETION'}")

    try:
        # First, count existing data
        existing_data = count_user_data(engine, args.user_id)

        if existing_data["total_records"] == 0:
            logger.info(f"✅ No data found for user {args.user_id}")
            return

        logger.info(f"Found data for user {args.user_id}:")
        logger.info(f"  - Scenes: {existing_data['scenes']}")
        logger.info(f"  - Glyphs: {existing_data['glyphs']}")
        logger.info(f"  - Total records: {existing_data['total_records']}")

        # Confirmation for live deletion
        if not args.dry_run and not args.confirm:
            response = input(f"\n⚠️  This will PERMANENTLY delete all data for user {args.user_id}. Continue? [y/N]: ")
            if response.lower() != "y":
                logger.info("❌ Deletion cancelled by user")
                return

        # Perform deletion (or dry run)
        result = delete_user_data(engine, args.user_id, dry_run=args.dry_run)

        if args.dry_run:
            logger.info("🔍 DRY RUN - Would delete:")
            logger.info(f"  - Scenes: {result['would_delete']['scenes']}")
            logger.info(f"  - Glyphs: {result['would_delete']['glyphs']}")
            logger.info(f"  - Total: {result['would_delete']['total_records']} records")
        else:
            # Verify deletion
            verification_passed = verify_deletion(engine, args.user_id)
            result["verification_passed"] = verification_passed

            if verification_passed:
                logger.info(f"✅ Successfully deleted {result['scenes_deleted']} scenes")
                logger.info("✅ Verification passed - no remaining data")
            else:
                logger.error("❌ Verification failed - some data may remain")
                result["status"] = "verification_failed"

        # Log audit entry if requested
        if args.audit:
            log_audit_entry(result, args.audit_file)

        if not args.dry_run and result.get("verification_passed", False):
            logger.info(f"🎯 GDPR erasure completed successfully for user {args.user_id}")

    except Exception as e:
        logger.error(f"❌ Erasure failed: {e}")

        if args.audit:
            error_result = {
                "dry_run": args.dry_run,
                "user_id": args.user_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
            log_audit_entry(error_result, args.audit_file)

        exit(1)


if __name__ == "__main__":
    main()
