#!/usr/bin/env python3
"""
Root Directory Cleanup - Organizes files according to CLAUDE.md guidelines
"""
import streamlit as st
from datetime import timezone

import os
import shutil
from datetime import datetime
from pathlib import Path


class RootDirectoryCleaner:
    def __init__(self, timezone):
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.moves = []

        # Files that belong in root (per CLAUDE.md)
        self.allowed_root_files = {
            "CLAUDE.md",
            "README.md",
            "LICENSE",
            "requirements.txt",
            "requirements-test.txt",
            "package.json",
            "package-lock.json",
            "lukhas_config.yaml",
            ".gitignore",
            ".env.example",
            ".env",
            "main.py",  # Primary entry point
            "Makefile",
            "setup.py",
            "pyproject.toml",
        }

        # Directory mapping
        self.directory_map = {
            "docs/reports/status/": ["*_STATUS_REPORT.md", "*_STATUS_*.md"],
            "docs/reports/analysis/": [
                "*_REPORT.json",
                "*_ANALYSIS.json",
                "*_report.json",
            ],
            "docs/planning/": ["*_PLAN.md", "*_ROADMAP.md"],
            "tools/analysis/": ["_*.py", "*_analyzer.py", "*_finder.py"],
            "tools/scripts/": [
                "*_consolidator.py",
                "bootstrap.py",
                "health_monitor.py",
            ],
            "tests/": ["test_*.py"],
            "docs/": ["*.md", "*.txt"],  # General docs
        }

    def scan_root_directory(self):
        """Scan root directory for files that should be moved"""
        root_files = []

        for item in os.listdir("."):
            if os.path.isfile(item) and item not in self.allowed_root_files:
                root_files.append(item)

        print(f"Found {len(root_files)} files in root that should be moved")
        return root_files

    def categorize_file(self, filename):
        """Determine where a file should go"""
        # Check patterns
        for dest, patterns in self.directory_map.items():
            for pattern in patterns:
                if pattern.startswith("*") and pattern.endswith("*"):
                    # Contains pattern
                    if pattern[1:-1] in filename:
                        return dest
                elif pattern.startswith("*"):
                    # Ends with pattern
                    if filename.endswith(pattern[1:]):
                        return dest
                elif pattern.endswith("*"):
                    # Starts with pattern
                    if filename.startswith(pattern[:-1]):
                        return dest
                elif pattern == filename:
                    return dest

        # Default categorization
        if filename.endswith(".py"):
            if "test" in filename:
                return "tests/"
            else:
                return "tools/scripts/"
        elif filename.endswith((".md", ".txt")):
            return "docs/"
        elif filename.endswith(".json"):
            return "docs/reports/analysis/"
        else:
            return "misc/"

    def move_file(self, filename, destination):
        """Move a file to its proper location"""
        source = Path(filename)
        dest_dir = Path(destination)

        # Create destination directory if needed
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Determine target path
        target = dest_dir / filename

        # Handle conflicts
        if target.exists():
            # Add timestamp to avoid overwriting
            stem = target.stem
            suffix = target.suffix
            target = dest_dir / f"{stem}_{self.timestamp}{suffix}"

        try:
            shutil.move(str(source), str(target))
            self.moves.append(f"{filename} -> {target}")
            return True
        except Exception as e:
            print(f"Failed to move {filename}: {e}")
            return False

    def cleanup_empty_directories(self):
        """Remove empty directories"""
        removed = []

        for root, dirs, _files in os.walk(".", topdown=False):
            if root.startswith((".git", ".venv", "__pycache__")):
                continue

            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        removed.append(dir_path)
                except BaseException:
                    pass

        return removed

    def create_directory_structure(self):
        """Ensure proper directory structure exists"""
        directories = [
            "docs/reports/status",
            "docs/reports/analysis",
            "docs/planning",
            "docs/planning/completed",
            "docs/archive",
            "tools/analysis",
            "tools/scripts",
            "tools/documentation_suite",
            "tests/governance",
            "tests/security",
            "tests/integration",
            "misc",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        print(f"✅ Created/verified {len(directories)} directories")

    def generate_report(self):
        """Generate cleanup report"""
        report = f"""
# Root Directory Cleanup Report
Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}

## Files Moved: {len(self.moves)}

### Move Details:
"""
        for move in self.moves:
            report += f"- {move}\n"

        report += """
## Directory Structure:
- ✅ Proper directory structure created
- ✅ Files organized according to CLAUDE.md guidelines
- ✅ Root directory cleaned

## Next Steps:
1. Review moved files in their new locations
2. Update any import paths if needed
3. Commit changes with descriptive message
"""

        with open("docs/reports/status/ROOT_CLEANUP_REPORT.md", "w") as f:
            f.write(report)

        return report


def main():
    print("🧹 LUKHAS Root Directory Cleanup")
    print("=" * 50)

    cleaner = RootDirectoryCleaner()

    # Create directory structure
    print("\n📁 Creating directory structure...")
    cleaner.create_directory_structure()

    # Scan root
    print("\n🔍 Scanning root directory...")
    files_to_move = cleaner.scan_root_directory()

    if not files_to_move:
        print("✅ Root directory is already clean!")
        return

    # Move files
    print(f"\n📦 Moving {len(files_to_move)} files...")
    for filename in files_to_move:
        destination = cleaner.categorize_file(filename)
        print(f"  Moving {filename} -> {destination}")
        cleaner.move_file(filename, destination)

    # Cleanup empty directories
    print("\n🗑️  Cleaning up empty directories...")
    removed = cleaner.cleanup_empty_directories()
    if removed:
        print(f"  Removed {len(removed)} empty directories")

    # Generate report
    print("\n📋 Generating report...")
    cleaner.generate_report()

    print("\n✅ Cleanup Complete!")
    print(f"  - Files moved: {len(cleaner.moves)}")
    print("  - Report saved: docs/reports/status/ROOT_CLEANUP_REPORT.md")


if __name__ == "__main__":
    main()
