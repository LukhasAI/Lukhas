#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Workspace Cleanup and Organization

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

This tool provides a comprehensive workspace cleanup and organization script.
It finds empty directories, empty files, corrupted files, and organizes the workspace.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkspaceOrganizer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.empty_dirs: List[Path] = []
        self.empty_files: List[Path] = []
        self.corrupted_files: List[Path] = []
        self.root_files_to_organize: List[Path] = []

        # Files that should stay in root
        self.root_essential_files = {
            ".gitignore",
            ".env",
            ".env.example",
            ".dockerignore",
            ".flake8",
            ".markdownlint.json",
            ".pre-commit-config.yaml",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "requirements-test.txt",
            "pytest.ini",
            "Dockerfile",
            "docker-compose.yml",
            "MANIFEST.in",
        }

        # Directories to exclude from cleanup
        self.exclude_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            ".vscode",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
        }

    def find_empty_directories(self) -> List[Path]:
        """Find all empty directories."""
        empty_dirs = []
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            root_path = Path(root)
            if not files and not dirs:
                # Check if it's truly empty (no hidden files either)
                try:
                    if not any(root_path.iterdir()):
                        empty_dirs.append(root_path)
                except PermissionError:
                    continue
        return empty_dirs

    def find_empty_files(self) -> List[Path]:
        """Find all empty files."""
        empty_files = []
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                try:
                    if file_path.stat().st_size == 0:
                        empty_files.append(file_path)
                except (OSError, PermissionError):
                    continue
        return empty_files

    def find_corrupted_files(self) -> List[Path]:
        """Find potentially corrupted files."""
        corrupted = []

        # Check Python files for syntax errors
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                            # Try to compile
                            compile(content, str(file_path), "exec")
                    except (SyntaxError, UnicodeDecodeError, PermissionError):
                        corrupted.append(file_path)
                    except Exception:
                        # Other compilation errors
                        pass

                # Check JSON files
                elif file.endswith(".json"):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            json.load(f)
                    except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
                        corrupted.append(file_path)
                    except Exception:
                        pass

        return corrupted

    def categorize_root_files(self) -> List[Path]:
        """Find files in root that should be organized into directories."""
        files_to_organize = []

        for item in self.root_path.iterdir():
            if item.is_file() and item.name not in self.root_essential_files:
                files_to_organize.append(item)

        return files_to_organize

    def suggest_file_placement(self, file_path: Path) -> Path:
        """Suggest where a file should be moved based on its type and content."""
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()

        # Documentation files
        if any(
            keyword in file_name
            for keyword in ["readme", "doc", "guide", "manual", "vision", "roadmap"]
        ):
            return self.root_path / "docs"

        # Configuration files
        if any(
            keyword in file_name for keyword in ["config", "conf", "settings"]
        ) or file_ext in [".ini", ".conf", ".yaml", ".yml"]:
            return self.root_path / "config"

        # Log files
        if file_ext in [".log"] or "log" in file_name:
            return self.root_path / "logs"

        # Test files
        if "test" in file_name or file_name.startswith("test_"):
            return self.root_path / "tests"

        # Script files
        if file_ext in [".sh", ".bat", ".ps1"] or "script" in file_name:
            return self.root_path / "scripts"

        # Module/graph files
        if any(keyword in file_name for keyword in ["module", "graph"]):
            return self.root_path / "docs" / "diagrams"

        # Investment/showcase files
        if any(
            keyword in file_name for keyword in ["investment", "showcase", "progress"]
        ):
            return self.root_path / "docs" / "progress"

        # Task completion files
        if any(keyword in file_name for keyword in ["task", "completion", "claude"]):
            return self.root_path / "docs" / "reports"

        # Default to tools if unsure
        return self.root_path / "tools"

    def organize_file(self, file_path: Path, target_dir: Path) -> bool:
        """Move a file to the target directory."""
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / file_path.name

            # Handle name conflicts
            counter = 1
            while target_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                target_path = (
                    target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                )
                counter += 1

            shutil.move(str(file_path), str(target_path))
            logger.info(f"Moved {file_path.name} to {target_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to move {file_path}: {e}")
            return False

    def cleanup_empty_files(self, preserve_essential: bool = True) -> int:
        """Remove empty files, optionally preserving essential ones."""
        removed_count = 0
        essential_empty_files = {
            "__init__.py",  # Python package markers
            ".gitkeep",  # Git directory placeholders
            "py.typed",  # Type hint markers
        }

        for file_path in self.empty_files:
            # Skip essential empty files if preservation is enabled
            if preserve_essential and file_path.name in essential_empty_files:
                continue

            try:
                file_path.unlink()
                logger.info(f"Removed empty file: {file_path}")
                removed_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {e}")

        return removed_count

    def cleanup_empty_directories(self) -> int:
        """Remove empty directories."""
        removed_count = 0
        # Sort by depth (deepest first) to avoid issues with nested empty dirs
        sorted_dirs = sorted(self.empty_dirs, key=lambda x: len(x.parts), reverse=True)

        for dir_path in sorted_dirs:
            try:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.info(f"Removed empty directory: {dir_path}")
                    removed_count += 1
            except Exception as e:
                logger.error(f"Failed to remove {dir_path}: {e}")

        return removed_count

    def generate_report(self) -> Dict:
        """Generate a comprehensive report of the analysis."""
        return {
            "empty_directories": len(self.empty_dirs),
            "empty_files": len(self.empty_files),
            "corrupted_files": len(self.corrupted_files),
            "root_files_to_organize": len(self.root_files_to_organize),
            "empty_dirs_list": [str(p) for p in self.empty_dirs],
            "empty_files_list": [str(p) for p in self.empty_files],
            "corrupted_files_list": [str(p) for p in self.corrupted_files],
            "root_files_list": [str(p) for p in self.root_files_to_organize],
        }

    def run_analysis(self):
        """Run the complete analysis."""
        logger.info("Starting workspace analysis...")

        logger.info("Finding empty directories...")
        self.empty_dirs = self.find_empty_directories()

        logger.info("Finding empty files...")
        self.empty_files = self.find_empty_files()

        logger.info("Finding corrupted files...")
        self.corrupted_files = self.find_corrupted_files()

        logger.info("Categorizing root files...")
        self.root_files_to_organize = self.categorize_root_files()

        logger.info("Analysis complete!")

    def run_cleanup(
        self,
        organize_files: bool = True,
        remove_empty_files: bool = True,
        remove_empty_dirs: bool = True,
        preserve_essential_empty: bool = True,
    ):
        """Run the cleanup process."""
        logger.info("Starting cleanup process...")

        results = {
            "organized_files": 0,
            "removed_empty_files": 0,
            "removed_empty_dirs": 0,
        }

        # Organize root files
        if organize_files:
            logger.info("Organizing root files...")
            for file_path in self.root_files_to_organize:
                target_dir = self.suggest_file_placement(file_path)
                if self.organize_file(file_path, target_dir):
                    results["organized_files"] += 1

        # Remove empty files
        if remove_empty_files:
            logger.info("Removing empty files...")
            results["removed_empty_files"] = self.cleanup_empty_files(
                preserve_essential_empty
            )

        # Remove empty directories
        if remove_empty_dirs:
            logger.info("Removing empty directories...")
            results["removed_empty_dirs"] = self.cleanup_empty_directories()

        logger.info("Cleanup complete!")
        return results


def main():
    root_path = "/Users/agi_dev/Downloads/Consolidation-Repo"
    organizer = WorkspaceOrganizer(root_path)

    # Run analysis
    organizer.run_analysis()

    # Generate report
    report = organizer.generate_report()

    print("\n" + "=" * 60)
    print("WORKSPACE ANALYSIS REPORT")
    print("=" * 60)
    print(f"Empty directories found: {report['empty_directories']}")
    print(f"Empty files found: {report['empty_files']}")
    print(f"Corrupted files found: {report['corrupted_files']}")
    print(f"Root files to organize: {report['root_files_to_organize']}")

    # Show some examples
    if report["empty_dirs_list"]:
        print("\nSample empty directories:")
        for dir_path in report["empty_dirs_list"][:5]:
            print(f"  - {dir_path}")
        if len(report["empty_dirs_list"]) > 5:
            print(f"  ... and {len(report['empty_dirs_list']) - 5} more")

    if report["corrupted_files_list"]:
        print("\nCorrupted files:")
        for file_path in report["corrupted_files_list"]:
            print(f"  - {file_path}")

    if report["root_files_list"]:
        print("\nRoot files that can be organized:")
        for file_path in report["root_files_list"]:
            print(f"  - {file_path}")

    # Ask for confirmation before cleanup
    print("\n" + "=" * 60)
    response = input("Do you want to proceed with cleanup? (y/N): ").strip().lower()

    if response == "y":
        cleanup_results = organizer.run_cleanup(
            organize_files=True,
            remove_empty_files=True,
            remove_empty_dirs=True,
            preserve_essential_empty=True,
        )

        print("\n" + "=" * 60)
        print("CLEANUP RESULTS")
        print("=" * 60)
        print(f"Files organized: {cleanup_results['organized_files']}")
        print(f"Empty files removed: {cleanup_results['removed_empty_files']}")
        print(f"Empty directories removed: {cleanup_results['removed_empty_dirs']}")
    else:
        print("Cleanup cancelled.")


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
