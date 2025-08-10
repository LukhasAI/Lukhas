#!/usr/bin/env python3
"""
Brain/Cognitive Consolidator - Phase 2B-2
Consolidate 7 brain/cognitive orchestration files into 1 primary implementation
"""

import argparse
import os
import shutil
from datetime import datetime


def consolidate_brain_cognitive(dry_run=True):
    """Consolidate brain/cognitive orchestrators"""

    # Find brain orchestrator files
    brain_files = []
    for root, dirs, files in os.walk("."):
        if "archived" in root:
            continue
        for file in files:
            if (
                file.endswith(".py")
                and "orchestrat" in file.lower()
                and ("brain" in root.lower() or "cognitive" in file.lower())
            ):
                full_path = os.path.join(root, file)
                brain_files.append(full_path)

    # Add any specific brain orchestrators we know about
    potential_files = [
        "./orchestration/brain/core/orchestrator.py",
        "./orchestration/brain/meta/cognition/orchestrator.py",
        "./orchestration/brain/orchestration/orchestrator.py",
        "./orchestration/brain/orchestration/orchestrator_core.py",
        "./orchestration/brain/orchestrator.py",
        "./orchestration/migrated/brain_orchestrator.py",
        "./orchestration/agents/meta_cognitive_orchestrator.py",
        "./orchestration/agents/meta_cognitive_orchestrator_alt.py",
    ]

    for file_path in potential_files:
        if os.path.exists(file_path) and file_path not in brain_files:
            brain_files.append(file_path)

    brain_files = sorted(list(set(brain_files)))

    # Choose primary file (largest or most comprehensive)
    primary_file = None
    if brain_files:
        # Find the largest file as primary
        largest_size = 0
        for file_path in brain_files:
            try:
                size = os.path.getsize(file_path)
                if size > largest_size:
                    largest_size = size
                    primary_file = file_path
            except:
                continue

    if not primary_file:
        print("❌ No brain orchestrator files found")
        return

    print("\\n🧠 BRAIN/COGNITIVE CONSOLIDATION")
    print(f"{'='*60}")
    if dry_run:
        print("🔍 DRY RUN MODE")
    print(f"Primary file: {primary_file}")
    print(f"Files to consolidate: {len(brain_files)}")
    print(f"{'='*60}")

    # Show all files
    print(f"\\n📁 Found {len(brain_files)} existing brain orchestrator files:")

    for file_path in brain_files:
        size = os.path.getsize(file_path) / 1024
        marker = "🎯" if file_path == primary_file else "📄"
        print(f"   {marker} {file_path} ({size:.1f} KB)")

    if dry_run:
        target_reduction = len(brain_files) - 1
        print(f"\\n🔍 Would consolidate {target_reduction} files into {primary_file}")
        print(f"📊 Estimated reduction: {target_reduction} files eliminated")
        return

    # Create archive directory
    archive_dir = "archived/orchestrators/consolidated/brain_cognitive"
    os.makedirs(archive_dir, exist_ok=True)

    # Archive non-primary files
    archived_count = 0
    for file_path in brain_files:
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

    print("\\n📊 Brain/cognitive consolidation complete!")
    print(f"   Files archived: {archived_count}")
    print(f"   Primary file kept: {primary_file}")
    print(f"   Reduction: {archived_count} files eliminated")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate brain/cognitive orchestrators"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute consolidation (default: dry run)",
    )
    args = parser.parse_args()

    consolidate_brain_cognitive(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute:")
        print("   python3 scripts/consolidate_brain_cognitive.py --execute")


if __name__ == "__main__":
    main()
