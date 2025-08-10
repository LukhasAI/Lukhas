#!/usr/bin/env python3
"""
Bio Systems Consolidator - Phase 2B-2
Consolidate 9 bio system orchestration files into 1 primary implementation
"""

import argparse
import os
import shutil
from datetime import datetime


def consolidate_bio_systems(dry_run=True):
    """Consolidate bio systems orchestrators"""

    # Bio systems files from analysis
    bio_files = [
        "./quantum/bio_multi_orchestrator.py",
        "./quantum/systems/bio_integration/multi_orchestrator.py",
        "./orchestration/bio_symbolic_orchestrator.py",
        "./bio/systems/orchestration/oscillator_orchestrator.py",
        "./bio/systems/orchestration/bio_orchestrator.py",
        "./bio/symbolic/bio_symbolic_orchestrator.py",
        "./bio/systems/orchestration/identity_aware_bio_orchestrator.py",
        "./voice/bio_core/oscillator/orchestrator.py",
        "./bio/systems/orchestration/base_orchestrator.py",
    ]

    primary_file = "./quantum/bio_multi_orchestrator.py"

    print("\\n🧬 BIO SYSTEMS CONSOLIDATION")
    print(f"{'='*60}")
    if dry_run:
        print("🔍 DRY RUN MODE")
    print(f"Primary file: {primary_file}")
    print(f"Files to consolidate: {len(bio_files)}")
    print(f"{'='*60}")

    # Check which files exist
    existing_files = [f for f in bio_files if os.path.exists(f)]
    print(f"\\n📁 Found {len(existing_files)} existing bio orchestrator files:")

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
    archive_dir = "archived/orchestrators/consolidated/bio_systems"
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

    print("\\n📊 Bio systems consolidation complete!")
    print(f"   Files archived: {archived_count}")
    print(f"   Primary file kept: {primary_file}")
    print(f"   Reduction: {archived_count} files eliminated")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate bio systems orchestrators"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute consolidation (default: dry run)",
    )
    args = parser.parse_args()

    consolidate_bio_systems(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute:")
        print("   python3 scripts/consolidate_bio_systems.py --execute")


if __name__ == "__main__":
    main()
