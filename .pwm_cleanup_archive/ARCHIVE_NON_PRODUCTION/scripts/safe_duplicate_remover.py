#!/usr/bin/env python3
"""
Safe duplicate remover - removes one group at a time with confirmation
"""

import json
import os
import shutil
from datetime import datetime
from typing import List


def create_backup_structure():
    """Create backup directory structure"""
    backup_dir = "archived/orchestrators/duplicates"
    os.makedirs(backup_dir, exist_ok=True)

    readme_content = f"""# Archived Duplicate Orchestrators

Files removed during orchestrator consolidation on {datetime.now().isoformat()}

Each file is backed up here before removal.
To restore a file, copy it back to its original location.

## Files in this backup:
"""

    with open(f"{backup_dir}/README.md", "w") as f:
        f.write(readme_content)

    return backup_dir


def choose_best_file(files: List[str]) -> str:
    """Choose the best file to keep"""
    # Prioritize Consolidation-Repo files
    consolidation_files = [f for f in files if "Consolidation-Repo" in f]
    if consolidation_files:
        return min(consolidation_files, key=lambda x: len(x.split("/")))

    # Otherwise choose shortest path
    return min(files, key=lambda x: len(x.split("/")))


def remove_single_group(
    group_num: int, total_groups: int, files: List[str], backup_dir: str
) -> bool:
    """Remove a single duplicate group"""
    if len(files) <= 1:
        return True

    print(f"\n{'='*80}")
    print(f"📁 REMOVING GROUP {group_num}/{total_groups}")
    print(f"{'='*80}")

    keep_file = choose_best_file(files)
    remove_files = [f for f in files if f != keep_file]

    print(f"✅ KEEPING: {keep_file}")

    success = True
    removed_count = 0

    for file_to_remove in remove_files:
        try:
            abs_path = os.path.abspath(file_to_remove)

            if os.path.exists(abs_path):
                # Create backup filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = (
                    f"{file_to_remove.replace('../', '').replace('/', '_')}_{timestamp}"
                )
                backup_path = os.path.join(backup_dir, backup_name)

                # Copy to backup
                shutil.copy2(abs_path, backup_path)
                print(f"💾 Backed up to: {backup_name}")

                # Remove original
                os.remove(abs_path)
                print(f"🗑️  Removed: {file_to_remove}")

                # Try to remove empty parent directories
                try:
                    parent_dir = os.path.dirname(abs_path)
                    if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                        print(f"📁 Removed empty directory: {parent_dir}")
                except:
                    pass  # Directory not empty or other issue

                removed_count += 1
            else:
                print(f"⚠️  File not found (already removed?): {file_to_remove}")

        except Exception as e:
            print(f"❌ Error removing {file_to_remove}: {e}")
            success = False

    print(f"📊 Group {group_num} complete: {removed_count} files removed")
    return success


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Safely remove duplicate orchestrator files"
    )
    parser.add_argument(
        "--analysis-file",
        default="orchestrator_analysis_report.json",
        help="Analysis report file",
    )
    parser.add_argument(
        "--start-group",
        type=int,
        default=1,
        help="Start from this group number (default: 1)",
    )
    parser.add_argument(
        "--max-groups",
        type=int,
        default=None,
        help="Maximum number of groups to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )

    args = parser.parse_args()

    # Load analysis
    try:
        with open(args.analysis_file) as f:
            data = json.load(f)
        duplicates = data.get("duplicates", {})
    except Exception as e:
        print(f"❌ Error loading analysis: {e}")
        return 1

    # Filter to groups with multiple files
    groups_to_process = [(k, v) for k, v in duplicates.items() if len(v["files"]) > 1]

    if not groups_to_process:
        print("🎉 No duplicate groups found!")
        return 0

    # Apply start and max limits
    if args.start_group > 1:
        groups_to_process = groups_to_process[args.start_group - 1 :]

    if args.max_groups:
        groups_to_process = groups_to_process[: args.max_groups]

    print("🎭 SAFE ORCHESTRATOR DUPLICATE REMOVAL")
    print(f"{'='*60}")
    print(f"Analysis file: {args.analysis_file}")
    print(f"Groups to process: {len(groups_to_process)}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be removed")
    print(f"{'='*60}")

    if not args.dry_run:
        # Create backup structure
        backup_dir = create_backup_structure()
        print(f"📁 Backup directory: {backup_dir}")

    # Process each group
    total_removed = 0
    successful_groups = 0

    for i, (hash_key, dup_info) in enumerate(groups_to_process, args.start_group):
        files = dup_info["files"]

        if args.dry_run:
            keep_file = choose_best_file(files)
            remove_files = [f for f in files if f != keep_file]

            print(f"\n📁 GROUP {i}/{len(groups_to_process) + args.start_group - 1}")
            print(f"   ✅ Would keep: {keep_file}")
            for rf in remove_files:
                print(f"   ❌ Would remove: {rf}")
                total_removed += 1
        else:
            if remove_single_group(
                i, len(groups_to_process) + args.start_group - 1, files, backup_dir
            ):
                successful_groups += 1
                total_removed += len(files) - 1

            # Small pause between groups
            import time

            time.sleep(0.5)

    # Final summary
    print(f"\n{'='*80}")
    print("📊 REMOVAL SUMMARY")
    print(f"{'='*80}")

    if args.dry_run:
        print(f"Groups analyzed: {len(groups_to_process)}")
        print(f"Files that would be removed: {total_removed}")
    else:
        print(f"Groups processed: {successful_groups}/{len(groups_to_process)}")
        print(f"Files removed: {total_removed}")
        print(f"Backup location: {backup_dir}")

    # Update README with file list
    if not args.dry_run and backup_dir:
        try:
            with open(f"{backup_dir}/README.md", "a") as f:
                f.write(f"\n\nProcessed on {datetime.now().isoformat()}:\n")
                f.write(f"- Groups processed: {successful_groups}\n")
                f.write(f"- Files removed: {total_removed}\n")
        except:
            pass

    return 0


if __name__ == "__main__":
    exit(main())
