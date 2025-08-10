#!/usr/bin/env python3
"""
Memory Management Consolidator - Phase 2B-2
Consolidate 7 memory management orchestration files into 1 primary implementation
"""

import argparse
import os
import shutil
from datetime import datetime


def consolidate_memory_management(dry_run=True):
    """Consolidate memory management orchestrators"""

    # Memory management files from analysis
    memory_files = [
        "./memory/core/unified_memory_orchestrator.py",
        "./memory/consolidation/consolidation_orchestrator.py",
        "./orchestration/migrated/memory_integration_orchestrator.py",
        "./features/memory/integration_orchestrator.py",
        "./memory/systems/memory_orchestrator.py",
        "./orchestration/migrated/memory_orchestrator.py",
        "./memory/systems/orchestrator.py",
    ]

    primary_file = "./memory/core/unified_memory_orchestrator.py"

    print("\\n🧠 MEMORY MANAGEMENT CONSOLIDATION")
    print(f"{'='*60}")
    if dry_run:
        print("🔍 DRY RUN MODE")
    print(f"Primary file: {primary_file}")
    print(f"Files to consolidate: {len(memory_files)}")
    print(f"{'='*60}")

    # Check which files exist
    existing_files = [f for f in memory_files if os.path.exists(f)]
    print(f"\\n📁 Found {len(existing_files)} existing memory orchestrator files:")

    for file_path in existing_files:
        size = os.path.getsize(file_path) / 1024
        print(f"   📄 {file_path} ({size:.1f} KB)")

    if dry_run:
        print(
            f"\\n🔍 Would consolidate {len(existing_files)-1} files into {primary_file}"
        )
        print(f"📊 Estimated reduction: {len(existing_files)-1} files eliminated")
        return

    # Create archive directory
    archive_dir = "archived/orchestrators/consolidated/memory_management"
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

    print("\\n📊 Memory management consolidation complete!")
    print(f"   Files archived: {archived_count}")
    print(f"   Primary file kept: {primary_file}")
    print(f"   Reduction: {archived_count} files eliminated")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate memory management orchestrators"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute consolidation (default: dry run)",
    )
    args = parser.parse_args()

    consolidate_memory_management(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute:")
        print("   python3 scripts/consolidate_memory_management.py --execute")


if __name__ == "__main__":
    main()
