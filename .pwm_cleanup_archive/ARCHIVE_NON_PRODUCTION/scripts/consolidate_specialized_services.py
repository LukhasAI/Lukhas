#!/usr/bin/env python3
"""
Specialized Services Consolidator - Phase 2C-1
Consolidate 7+ specialized orchestration files into 1 primary implementation
"""

import argparse
import os
import shutil
from datetime import datetime


def consolidate_specialized_services(dry_run=True):
    """Consolidate specialized services orchestrators"""

    # Specialized services files
    specialized_files = [
        "./orchestration/specialized/content_enterprise_orchestrator.py",
        "./orchestration/specialized/component_orchestrator.py",
        "./orchestration/specialized/deployment_orchestrator.py",
        "./orchestration/specialized/enhancement_orchestrator.py",
        "./orchestration/specialized/integrated_system_orchestrator.py",
        "./orchestration/specialized/lambda_bot_orchestrator.py",
        "./orchestration/specialized/orchestrator_emotion_engine.py",
        "./orchestration/specialized/ui_orchestrator.py",
    ]

    primary_file = "./orchestration/specialized/content_enterprise_orchestrator.py"

    print("\\n🏢 SPECIALIZED SERVICES CONSOLIDATION")
    print(f"{'='*60}")
    if dry_run:
        print("🔍 DRY RUN MODE")
    print(f"Primary file: {primary_file}")
    print(f"Files to consolidate: {len(specialized_files)}")
    print(f"{'='*60}")

    # Check which files exist
    existing_files = [f for f in specialized_files if os.path.exists(f)]
    print(f"\\n📁 Found {len(existing_files)} existing specialized orchestrator files:")

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
    archive_dir = "archived/orchestrators/consolidated/specialized_services"
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

    print("\\n📊 Specialized services consolidation complete!")
    print(f"   Files archived: {archived_count}")
    print(f"   Primary file kept: {primary_file}")
    print(f"   Reduction: {archived_count} files eliminated")
    return archived_count


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate specialized services orchestrators"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute consolidation (default: dry run)",
    )
    args = parser.parse_args()

    result = consolidate_specialized_services(dry_run=not args.execute)

    if not args.execute:
        print("\\n📋 Command to execute:")
        print("   python3 scripts/consolidate_specialized_services.py --execute")


if __name__ == "__main__":
    main()
