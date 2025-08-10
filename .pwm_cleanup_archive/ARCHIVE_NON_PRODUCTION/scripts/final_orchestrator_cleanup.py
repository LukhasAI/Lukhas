#!/usr/bin/env python3
"""
Final Orchestrator Cleanup - Phase 2C-5
Clean up remaining demo files, duplicates, and utilities
"""

import argparse
import os
import shutil
from datetime import datetime


def final_orchestrator_cleanup(dry_run=True):
    """Final cleanup of remaining orchestrator files"""

    # Files to clean up
    cleanup_files = [
        "./examples/orchestration/demo_agent_orchestration.py",  # Demo file
        "./orchestration/swarm_orchestration_adapter.py",  # Duplicate swarm
        "./core/swarm_identity_orchestrator.py",  # Duplicate swarm
        "./quantum/dast_orchestrator.py",  # Duplicate DAST
    ]

    print("\\n🧹 FINAL ORCHESTRATOR CLEANUP")
    print(f"{'='*60}")
    if dry_run:
        print("🔍 DRY RUN MODE")
    print(f"Files to clean up: {len(cleanup_files)}")
    print(f"{'='*60}")

    # Check which files exist
    existing_files = [f for f in cleanup_files if os.path.exists(f)]
    print(f"\\n📁 Found {len(existing_files)} files for final cleanup:")

    for file_path in existing_files:
        size = os.path.getsize(file_path) / 1024
        reason = ""
        if "demo" in file_path:
            reason = "(demo file)"
        elif (
            "swarm" in file_path
            and "adapter" in file_path
            or "swarm_identity" in file_path
        ):
            reason = "(swarm duplicate)"
        elif "quantum/dast" in file_path:
            reason = "(DAST duplicate)"

        print(f"   📄 {file_path} ({size:.1f} KB) {reason}")

    if dry_run:
        print(f"\\n🔍 Would clean up {len(existing_files)} files")
        print(f"📊 Estimated reduction: {len(existing_files)} files eliminated")
        return len(existing_files)

    # Create archive directory
    archive_dir = "archived/orchestrators/final_cleanup"
    os.makedirs(archive_dir, exist_ok=True)

    # Archive cleanup files
    archived_count = 0
    for file_path in existing_files:
        try:
            # Create archive filename
            file_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{file_name}_{timestamp}"
            archive_path = os.path.join(archive_dir, archive_name)

            # Copy to archive
            shutil.copy2(file_path, archive_path)

            # Remove original
            os.remove(file_path)

            print(f"   ✅ Cleaned up: {file_path}")
            print(f"      💾 Backup: {archive_name}")
            archived_count += 1

        except Exception as e:
            print(f"   ❌ Error cleaning up {file_path}: {e}")

    print("\\n📊 Final cleanup complete!")
    print(f"   Files cleaned up: {archived_count}")
    print(f"   Reduction: {archived_count} files eliminated")
    return archived_count


def main():
    parser = argparse.ArgumentParser(description="Final orchestrator cleanup")
    parser.add_argument(
        "--execute", action="store_true", help="Execute cleanup (default: dry run)"
    )
    args = parser.parse_args()

    result = final_orchestrator_cleanup(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute:")
        print("   python3 scripts/final_orchestrator_cleanup.py --execute")


if __name__ == "__main__":
    main()
