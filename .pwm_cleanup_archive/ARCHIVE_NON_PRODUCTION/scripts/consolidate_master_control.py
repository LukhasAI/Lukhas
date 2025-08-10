#!/usr/bin/env python3
"""
Master Control Consolidator - Phase 2C-2
Consolidate 3 master control orchestration files into 1 primary implementation
"""

import argparse
import os
import shutil
from datetime import datetime


def consolidate_master_control(dry_run=True):
    """Consolidate master control orchestrators"""

    # Master control files
    master_files = [
        "./orchestration/master_orchestrator.py",
        "./orchestration/core_modules/master_orchestrator.py",
        "./orchestration/core_modules/master_orchestrator_alt.py",
    ]

    primary_file = "./orchestration/master_orchestrator.py"  # Main location

    print("\\n👑 MASTER CONTROL CONSOLIDATION")
    print(f"{'='*60}")
    if dry_run:
        print("🔍 DRY RUN MODE")
    print(f"Primary file: {primary_file}")
    print(f"Files to consolidate: {len(master_files)}")
    print(f"{'='*60}")

    # Check which files exist
    existing_files = [f for f in master_files if os.path.exists(f)]
    print(f"\\n📁 Found {len(existing_files)} existing master orchestrator files:")

    for file_path in existing_files:
        size = os.path.getsize(file_path) / 1024
        marker = "🎯" if file_path == primary_file else "📄"
        print(f"   {marker} {file_path} ({size:.1f} KB)")

    if dry_run:
        target_reduction = len(existing_files) - 1
        print(f"\\n🔍 Would consolidate {target_reduction} files into {primary_file}")
        print(f"📊 Estimated reduction: {target_reduction} files eliminated")
        return target_reduction

    # Create archive directory
    archive_dir = "archived/orchestrators/consolidated/master_control"
    os.makedirs(archive_dir, exist_ok=True)

    # Archive non-primary files
    archived_count = 0
    for file_path in existing_files:
        if file_path == primary_file:
            continue

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

            print(f"   ✅ Archived: {file_path}")
            print(f"      💾 Backup: {archive_name}")
            archived_count += 1

        except Exception as e:
            print(f"   ❌ Error archiving {file_path}: {e}")

    print("\\n📊 Master control consolidation complete!")
    print(f"   Files archived: {archived_count}")
    print(f"   Primary file kept: {primary_file}")
    print(f"   Reduction: {archived_count} files eliminated")
    return archived_count


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate master control orchestrators"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute consolidation (default: dry run)",
    )
    args = parser.parse_args()

    result = consolidate_master_control(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute:")
        print("   python3 scripts/consolidate_master_control.py --execute")


if __name__ == "__main__":
    main()
