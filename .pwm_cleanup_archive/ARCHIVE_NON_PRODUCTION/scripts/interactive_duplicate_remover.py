#!/usr/bin/env python3
"""
Interactive duplicate orchestrator file remover
Shows each file's content and asks for confirmation before removal
"""

import argparse
import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List


class InteractiveDuplicateRemover:
    def __init__(self, analysis_file: str = "orchestrator_analysis_report.json"):
        self.analysis_file = analysis_file
        self.duplicates = {}
        self.removed_files = []
        self.kept_files = []
        self.skipped_groups = []

    def load_analysis(self) -> bool:
        """Load the orchestrator analysis report"""
        try:
            with open(self.analysis_file) as f:
                data = json.load(f)

            self.duplicates = data.get("duplicates", {})
            print(f"📊 Loaded analysis with {len(self.duplicates)} duplicate groups")
            return True

        except Exception as e:
            print(f"❌ Error loading analysis: {e}")
            return False

    def show_file_preview(self, file_path: str, lines: int = 20) -> None:
        """Show preview of file content"""
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                print(f"   ⚠️  File not found: {file_path}")
                return

            with open(abs_path, encoding="utf-8", errors="ignore") as f:
                content_lines = f.readlines()

            file_size = os.path.getsize(abs_path)
            print(f"   📄 File: {file_path}")
            print(f"   📏 Size: {file_size:,} bytes ({len(content_lines):,} lines)")
            print(
                f"   📅 Modified: {datetime.fromtimestamp(os.path.getmtime(abs_path)).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"   👀 Preview (first {lines} lines):")
            print("   " + "─" * 60)

            for i, line in enumerate(content_lines[:lines], 1):
                print(f"   {i:3d} │ {line.rstrip()}")

            if len(content_lines) > lines:
                print(f"   ... ({len(content_lines) - lines} more lines)")

            print("   " + "─" * 60)

        except Exception as e:
            print(f"   ❌ Error reading file: {e}")

    def compare_files_content(self, files: List[str]) -> None:
        """Compare key characteristics of duplicate files"""
        print(f"\n🔍 Comparing {len(files)} duplicate files:")

        file_stats = []
        for file_path in files:
            try:
                abs_path = os.path.abspath(file_path)
                if os.path.exists(abs_path):
                    stat = os.stat(abs_path)
                    with open(abs_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    file_stats.append(
                        {
                            "path": file_path,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "lines": len(content.split("\n")),
                            "first_100_chars": content[:100].replace("\n", "\\n"),
                        }
                    )
                else:
                    file_stats.append(
                        {
                            "path": file_path,
                            "size": 0,
                            "modified": None,
                            "lines": 0,
                            "first_100_chars": "FILE NOT FOUND",
                        }
                    )
            except Exception as e:
                file_stats.append(
                    {
                        "path": file_path,
                        "size": 0,
                        "modified": None,
                        "lines": 0,
                        "first_100_chars": f"ERROR: {e}",
                    }
                )

        # Sort by modification time (newest first)
        file_stats.sort(key=lambda x: x["modified"] or datetime.min, reverse=True)

        for i, stat in enumerate(file_stats):
            marker = "🟢 NEWEST" if i == 0 else f"🔸 #{i+1}"
            mod_time = (
                stat["modified"].strftime("%Y-%m-%d %H:%M:%S")
                if stat["modified"]
                else "Unknown"
            )

            print(f"\n   {marker} {stat['path']}")
            print(
                f"       Size: {stat['size']:,} bytes | Lines: {stat['lines']:,} | Modified: {mod_time}"
            )
            print(f"       Content start: {stat['first_100_chars'][:80]}...")

    def choose_best_file(self, files: List[str]) -> str:
        """Choose the best file to keep from a group of duplicates"""
        # Prioritize files in Consolidation-Repo over others
        consolidation_files = [f for f in files if "Consolidation-Repo" in f]
        if consolidation_files:
            # Among Consolidation-Repo files, prefer shorter paths (less nested)
            return min(consolidation_files, key=lambda x: len(x.split("/")))

        # If no Consolidation-Repo files, prefer shorter paths
        return min(files, key=lambda x: len(x.split("/")))

    def process_duplicate_group(
        self, group_num: int, hash_key: str, dup_info: Dict[str, Any]
    ) -> bool:
        """Process a single duplicate group interactively"""
        files = dup_info["files"]
        if len(files) <= 1:
            return True

        print("\n" + "=" * 80)
        print(f"📁 DUPLICATE GROUP {group_num}/{len(self.duplicates)}")
        print("=" * 80)

        # Compare files
        self.compare_files_content(files)

        # Suggest best file to keep
        suggested_keep = self.choose_best_file(files)
        to_remove = [f for f in files if f != suggested_keep]

        print("\n💡 SUGGESTION:")
        print(f"   ✅ KEEP: {suggested_keep}")
        for file_to_remove in to_remove:
            print(f"   ❌ REMOVE: {file_to_remove}")

        while True:
            print("\n❓ What would you like to do?")
            print(f"   1. Accept suggestion (keep {os.path.basename(suggested_keep)})")
            print("   2. Choose different file to keep")
            print("   3. Show file preview")
            print("   4. Skip this group")
            print("   5. Quit")

            choice = input("Enter choice (1-5): ").strip()

            if choice == "1":
                # Accept suggestion
                return self._remove_files(suggested_keep, to_remove)

            elif choice == "2":
                # Choose different file
                print("\n📋 Available files:")
                for i, file_path in enumerate(files, 1):
                    print(f"   {i}. {file_path}")

                try:
                    file_choice = (
                        int(input(f"Choose file to KEEP (1-{len(files)}): ")) - 1
                    )
                    if 0 <= file_choice < len(files):
                        chosen_keep = files[file_choice]
                        chosen_remove = [f for f in files if f != chosen_keep]
                        return self._remove_files(chosen_keep, chosen_remove)
                    else:
                        print("❌ Invalid choice")
                        continue
                except ValueError:
                    print("❌ Please enter a number")
                    continue

            elif choice == "3":
                # Show file preview
                print("\n📋 Choose file to preview:")
                for i, file_path in enumerate(files, 1):
                    print(f"   {i}. {file_path}")

                try:
                    preview_choice = (
                        int(input(f"Enter file number (1-{len(files)}): ")) - 1
                    )
                    if 0 <= preview_choice < len(files):
                        self.show_file_preview(files[preview_choice], lines=30)
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Please enter a number")
                continue

            elif choice == "4":
                # Skip this group
                print("⏭️  Skipping this duplicate group")
                self.skipped_groups.append(hash_key)
                return True

            elif choice == "5":
                # Quit
                print("🛑 Quitting...")
                return False

            else:
                print("❌ Invalid choice, please try again")
                continue

    def _remove_files(self, keep_file: str, remove_files: List[str]) -> bool:
        """Remove the specified files"""
        print(f"\n🗑️  Removing {len(remove_files)} duplicate files...")

        # Create backup directory
        backup_dir = "archived/orchestrators/duplicates"
        os.makedirs(backup_dir, exist_ok=True)

        self.kept_files.append(keep_file)

        for file_to_remove in remove_files:
            try:
                abs_path = os.path.abspath(file_to_remove)

                if os.path.exists(abs_path):
                    # Create backup
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{file_to_remove.replace('../', '').replace('/', '_')}_{timestamp}"
                    backup_path = os.path.join(backup_dir, backup_name)

                    shutil.copy2(abs_path, backup_path)
                    os.remove(abs_path)

                    print(f"   ✅ Removed: {file_to_remove}")
                    print(f"      💾 Backup: {backup_path}")

                    self.removed_files.append(file_to_remove)
                else:
                    print(f"   ⚠️  File not found: {file_to_remove}")

            except Exception as e:
                print(f"   ❌ Error removing {file_to_remove}: {e}")

        return True

    def create_archive_structure(self) -> None:
        """Create archive directory structure"""
        archive_dirs = [
            "archived/orchestrators/duplicates",
            "archived/orchestrators/variants",
            "archived/orchestrators/experimental",
            "archived/orchestrators/examples",
        ]

        for dir_path in archive_dirs:
            os.makedirs(dir_path, exist_ok=True)

        # Create README
        readme_content = f"""# Archived Orchestrators

This directory contains orchestrator files that were removed during consolidation.

## Structure:

- `duplicates/` - Exact duplicate files (byte-for-byte identical)
- `variants/` - Alternative implementations of the same concept
- `experimental/` - Development/test versions
- `examples/` - Demo and example implementations

## Restoration:

To restore a file, copy it back to its original location and update imports.

## Generated by:

`scripts/interactive_duplicate_remover.py` on {datetime.now().isoformat()}

## Session Summary:

- Duplicate groups processed: {len(self.duplicates) - len(self.skipped_groups)}
- Groups skipped: {len(self.skipped_groups)}
- Files removed: {len(self.removed_files)}
- Files kept: {len(self.kept_files)}
"""

        with open("archived/orchestrators/README.md", "w") as f:
            f.write(readme_content)

    def generate_report(self) -> None:
        """Generate removal report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_file": self.analysis_file,
            "total_duplicate_groups": len(self.duplicates),
            "groups_processed": len(self.duplicates) - len(self.skipped_groups),
            "groups_skipped": len(self.skipped_groups),
            "files_removed": len(self.removed_files),
            "files_kept": len(self.kept_files),
            "removed_files": self.removed_files,
            "kept_files": self.kept_files,
            "skipped_groups": self.skipped_groups,
        }

        report_file = f"orchestrator_removal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")

    def run_interactive_removal(self) -> bool:
        """Run the interactive removal process"""
        print("\n🎭 INTERACTIVE ORCHESTRATOR DUPLICATE REMOVAL")
        print("=" * 60)
        print(
            "This tool will show you each duplicate group and let you decide what to remove."
        )
        print(
            "You can preview files, choose which one to keep, or skip groups entirely."
        )
        print(
            "All removed files will be backed up to archived/orchestrators/duplicates/"
        )

        input("\n📍 Press Enter to start...")

        # Create archive structure
        self.create_archive_structure()

        # Process each duplicate group
        group_num = 1
        for hash_key, dup_info in self.duplicates.items():
            if len(dup_info["files"]) <= 1:
                continue

            if not self.process_duplicate_group(group_num, hash_key, dup_info):
                print("\n🛑 Process terminated by user")
                break

            group_num += 1

        # Show final summary
        print("\n" + "=" * 80)
        print("📊 REMOVAL SUMMARY")
        print("=" * 80)
        print(f"Groups processed: {len(self.duplicates) - len(self.skipped_groups)}")
        print(f"Groups skipped: {len(self.skipped_groups)}")
        print(f"Files removed: {len(self.removed_files)}")
        print(f"Files kept: {len(self.kept_files)}")

        if self.removed_files:
            print("\n🗑️  Files removed:")
            for removed in self.removed_files:
                print(f"   - {removed}")

        if self.kept_files:
            print("\n✅ Files kept:")
            for kept in self.kept_files:
                print(f"   - {kept}")

        # Generate report
        self.generate_report()

        return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Interactively remove duplicate orchestrator files"
    )
    parser.add_argument(
        "--analysis-file",
        default="orchestrator_analysis_report.json",
        help="Analysis report file",
    )

    args = parser.parse_args()

    remover = InteractiveDuplicateRemover(args.analysis_file)

    if not remover.load_analysis():
        return 1

    if not remover.duplicates:
        print("🎉 No duplicate groups found!")
        return 0

    # Run interactive removal
    remover.run_interactive_removal()

    return 0


if __name__ == "__main__":
    exit(main())
