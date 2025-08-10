#!/usr/bin/env python3
"""
Step-by-step duplicate file analyzer
Shows each duplicate group with file contents for manual review
"""

import json
import os
from datetime import datetime
from typing import Any, Dict


class StepByStepAnalyzer:
    def __init__(self, analysis_file: str = "orchestrator_analysis_report.json"):
        self.analysis_file = analysis_file
        self.duplicates = {}

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

    def show_file_details(self, file_path: str) -> Dict[str, Any]:
        """Show detailed information about a file"""
        try:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                return {"path": file_path, "exists": False, "error": "File not found"}

            stat = os.stat(abs_path)
            with open(abs_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]

            # Extract key information
            classes = []
            functions = []
            imports = []

            for line in lines:
                stripped = line.strip()
                if stripped.startswith("class "):
                    class_name = (
                        stripped.split("(")[0].replace("class ", "").replace(":", "")
                    )
                    classes.append(class_name)
                elif stripped.startswith("def "):
                    func_name = stripped.split("(")[0].replace("def ", "")
                    functions.append(func_name)
                elif stripped.startswith("import ") or stripped.startswith("from "):
                    imports.append(
                        stripped[:60] + "..." if len(stripped) > 60 else stripped
                    )

            return {
                "path": file_path,
                "exists": True,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 1),
                "total_lines": len(lines),
                "code_lines": len(non_empty_lines),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "classes": classes[:5],  # First 5 classes
                "functions": functions[:10],  # First 10 functions
                "imports": imports[:8],  # First 8 imports
                "first_50_lines": lines[:50],
                "content_preview": (
                    content[:500] + "..." if len(content) > 500 else content
                ),
            }

        except Exception as e:
            return {"path": file_path, "exists": False, "error": str(e)}

    def analyze_duplicate_group(
        self, group_num: int, hash_key: str, dup_info: Dict[str, Any]
    ) -> None:
        """Analyze a single duplicate group"""
        files = dup_info["files"]
        if len(files) <= 1:
            return

        print("\n" + "=" * 100)
        print(
            f"📁 DUPLICATE GROUP {group_num}/{len(self.duplicates)} - Hash: {hash_key[:16]}..."
        )
        print("=" * 100)

        print(f"🔍 Found {len(files)} identical files:")

        file_details = []
        for file_path in files:
            details = self.show_file_details(file_path)
            file_details.append(details)

        # Sort by modification time (newest first)
        file_details.sort(key=lambda x: x.get("modified", "0000-00-00"), reverse=True)

        # Show comparison table
        print("\n📊 File Comparison:")
        print(f"{'#':<2} {'Path':<60} {'Size':<8} {'Lines':<6} {'Modified':<20}")
        print("-" * 100)

        for i, details in enumerate(file_details, 1):
            if details["exists"]:
                marker = "🟢" if i == 1 else "🔸"
                path_short = (
                    details["path"][-55:]
                    if len(details["path"]) > 55
                    else details["path"]
                )
                print(
                    f"{i:<2} {marker} {path_short:<58} {details['size_kb']:<6}KB {details['code_lines']:<6} {details['modified']}"
                )
            else:
                print(
                    f"{i:<2} ❌ {details['path']:<58} {'ERROR':<8} {'N/A':<6} {'File not found'}"
                )

        # Show content of first (newest) file
        if file_details and file_details[0]["exists"]:
            newest = file_details[0]
            print(
                f"\n📄 Content Preview (newest file: {os.path.basename(newest['path'])}):"
            )
            print("─" * 80)

            if newest.get("classes"):
                print(
                    f"🏗️  Classes: {', '.join(newest['classes'][:3])}{'...' if len(newest['classes']) > 3 else ''}"
                )

            if newest.get("functions"):
                print(
                    f"⚡ Functions: {', '.join(newest['functions'][:5])}{'...' if len(newest['functions']) > 5 else ''}"
                )

            if newest.get("imports"):
                print("📦 Key Imports:")
                for imp in newest["imports"][:5]:
                    print(f"    {imp}")

            print("\n📝 First 20 lines:")
            for i, line in enumerate(newest["first_50_lines"][:20], 1):
                print(f"{i:3d} │ {line.rstrip()}")

            if len(newest["first_50_lines"]) > 20:
                print(
                    f"... ({len(newest['first_50_lines']) - 20} more lines in preview)"
                )

        # Recommendation
        print("\n💡 RECOMMENDATION:")
        if file_details:
            # Prioritize Consolidation-Repo files
            consolidation_files = [
                d for d in file_details if "Consolidation-Repo" in d["path"]
            ]
            if consolidation_files:
                recommended = consolidation_files[0]  # Newest in Consolidation-Repo
                print(f"   ✅ KEEP: {recommended['path']} (Consolidation-Repo, newest)")
            else:
                recommended = file_details[0]  # Newest overall
                print(f"   ✅ KEEP: {recommended['path']} (newest)")

            to_remove = [d for d in file_details if d["path"] != recommended["path"]]
            for details in to_remove:
                if details["exists"]:
                    print(f"   ❌ REMOVE: {details['path']}")

        print("\n" + "─" * 80)

    def show_summary(self) -> None:
        """Show summary of all duplicate groups"""
        print("\n" + "=" * 100)
        print("📋 DUPLICATE GROUPS SUMMARY")
        print("=" * 100)

        groups_with_files = [
            (k, v) for k, v in self.duplicates.items() if len(v["files"]) > 1
        ]
        total_duplicates = sum(len(v["files"]) - 1 for k, v in groups_with_files)

        print(f"Total duplicate groups: {len(groups_with_files)}")
        print(f"Total files to remove: {total_duplicates}")
        print(f"Estimated space savings: {self._estimate_savings()} MB")

        # Show groups by size
        print("\n📊 Groups by file count:")
        group_sizes = {}
        for k, v in groups_with_files:
            size = len(v["files"])
            group_sizes[size] = group_sizes.get(size, 0) + 1

        for size in sorted(group_sizes.keys(), reverse=True):
            count = group_sizes[size]
            files_to_remove = count * (size - 1)
            print(
                f"   {size} files: {count} groups ({files_to_remove} files to remove)"
            )

    def _estimate_savings(self) -> float:
        """Estimate space savings from removing duplicates"""
        total_savings = 0

        for hash_key, dup_info in self.duplicates.items():
            files = dup_info["files"]
            if len(files) <= 1:
                continue

            # Get size of one file (they're identical)
            for file_path in files:
                try:
                    abs_path = os.path.abspath(file_path)
                    if os.path.exists(abs_path):
                        file_size = os.path.getsize(abs_path)
                        total_savings += file_size * (
                            len(files) - 1
                        )  # Save space from duplicates
                        break
                except:
                    continue

        return round(total_savings / 1024 / 1024, 2)

    def run_step_by_step_analysis(self, max_groups: int = None) -> None:
        """Run step-by-step analysis"""
        print("🎭 STEP-BY-STEP DUPLICATE FILE ANALYSIS")
        print("=" * 60)

        # Show summary first
        self.show_summary()

        # Analyze each group
        groups_with_files = [
            (k, v) for k, v in self.duplicates.items() if len(v["files"]) > 1
        ]

        if max_groups:
            groups_with_files = groups_with_files[:max_groups]
            print(f"\n📍 Showing first {max_groups} groups (use --all to see all)")

        for i, (hash_key, dup_info) in enumerate(groups_with_files, 1):
            self.analyze_duplicate_group(i, hash_key, dup_info)

        print("\n✅ Analysis complete!")
        if not max_groups:
            print(f"📊 Analyzed {len(groups_with_files)} duplicate groups")
        print("📄 Use the interactive remover to process these duplicates:")
        print("   python3 scripts/remove_duplicate_orchestrators.py --execute")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Step-by-step duplicate file analysis")
    parser.add_argument(
        "--analysis-file",
        default="orchestrator_analysis_report.json",
        help="Analysis report file",
    )
    parser.add_argument(
        "--max-groups",
        type=int,
        default=5,
        help="Maximum number of groups to show (default: 5, use 0 for all)",
    )
    parser.add_argument("--all", action="store_true", help="Show all groups")

    args = parser.parse_args()

    analyzer = StepByStepAnalyzer(args.analysis_file)

    if not analyzer.load_analysis():
        return 1

    if not analyzer.duplicates:
        print("🎉 No duplicate groups found!")
        return 0

    max_groups = None if args.all or args.max_groups == 0 else args.max_groups
    analyzer.run_step_by_step_analysis(max_groups)

    return 0


if __name__ == "__main__":
    exit(main())
