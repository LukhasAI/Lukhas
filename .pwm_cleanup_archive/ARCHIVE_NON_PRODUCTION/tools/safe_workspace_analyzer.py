#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Safe Workspace Analyzer

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

This tool provides a safe, analysis-only script to analyze the workspace
for potential issues without making any changes.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class SafeWorkspaceAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)

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

        # Directories to exclude from analysis
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
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            root_path = Path(root)
            if not files and not dirs:
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

        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                            compile(content, str(file_path), "exec")
                    except (SyntaxError, UnicodeDecodeError, PermissionError):
                        corrupted.append(file_path)
                    except Exception:
                        pass

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

    def categorize_root_files(self) -> Dict[str, List[Path]]:
        """Categorize root files by suggested destination."""
        categorized = {
            "docs": [],
            "docs/reports": [],
            "docs/progress": [],
            "docs/diagrams": [],
            "logs": [],
            "tests": [],
            "tools": [],
            "config": [],
            "scripts": [],
        }

        for item in self.root_path.iterdir():
            if item.is_file() and item.name not in self.root_essential_files:
                file_name = item.name.lower()
                file_ext = item.suffix.lower()

                # Categorize based on content
                if any(
                    keyword in file_name
                    for keyword in [
                        "readme",
                        "doc",
                        "guide",
                        "manual",
                        "vision",
                        "roadmap",
                    ]
                ):
                    categorized["docs"].append(item)
                elif any(
                    keyword in file_name
                    for keyword in ["investment", "showcase", "progress"]
                ):
                    categorized["docs/progress"].append(item)
                elif any(
                    keyword in file_name for keyword in ["task", "completion", "claude"]
                ):
                    categorized["docs/reports"].append(item)
                elif any(keyword in file_name for keyword in ["module", "graph"]):
                    categorized["docs/diagrams"].append(item)
                elif file_ext in [".log"] or "log" in file_name:
                    categorized["logs"].append(item)
                elif "test" in file_name or file_name.startswith("test_"):
                    categorized["tests"].append(item)
                elif file_ext in [".sh", ".bat", ".ps1"] or "script" in file_name:
                    categorized["scripts"].append(item)
                elif any(
                    keyword in file_name for keyword in ["config", "conf", "settings"]
                ) or file_ext in [".ini", ".conf", ".yaml", ".yml"]:
                    categorized["config"].append(item)
                else:
                    categorized["tools"].append(item)

        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}

    def analyze_only(self):
        """Run analysis and generate report - NO CHANGES MADE"""
        print("\n" + "=" * 70)
        print("🔍 SAFE WORKSPACE ANALYSIS - READ ONLY MODE")
        print("=" * 70)
        print("⚠️  This script will NOT make any changes to your workspace")
        print("   It only analyzes and reports what it finds")
        print("=" * 70)

        # Find issues
        logger.info("Scanning for empty directories...")
        empty_dirs = self.find_empty_directories()

        logger.info("Scanning for empty files...")
        empty_files = self.find_empty_files()

        logger.info("Scanning for corrupted files...")
        corrupted_files = self.find_corrupted_files()

        logger.info("Analyzing root directory organization...")
        root_files = self.categorize_root_files()

        # Generate report
        print("\n📊 ANALYSIS RESULTS:")
        print(f"   Empty directories: {len(empty_dirs)}")
        print(f"   Empty files: {len(empty_files)}")
        print(f"   Corrupted files: {len(corrupted_files)}")
        print(
            f"   Root files that could be organized: {sum(len(files) for files in root_files.values())}"
        )

        # Show empty directories (sample)
        if empty_dirs:
            print(f"\n📁 EMPTY DIRECTORIES ({len(empty_dirs)} found):")
            for i, dir_path in enumerate(empty_dirs[:10]):
                print(f"   {i+1}. {dir_path}")
            if len(empty_dirs) > 10:
                print(f"   ... and {len(empty_dirs) - 10} more")

        # Show empty files (sample)
        if empty_files:
            print(f"\n📄 EMPTY FILES ({len(empty_files)} found):")
            essential_empty = {"__init__.py", ".gitkeep", "py.typed"}
            regular_empty = [f for f in empty_files if f.name not in essential_empty]
            essential_count = len(empty_files) - len(regular_empty)

            for i, file_path in enumerate(regular_empty[:10]):
                print(f"   {i+1}. {file_path}")
            if len(regular_empty) > 10:
                print(f"   ... and {len(regular_empty) - 10} more regular empty files")
            if essential_count > 0:
                print(
                    f"   📌 {essential_count} essential empty files (would be preserved)"
                )

        # Show corrupted files
        if corrupted_files:
            print(f"\n⚠️  CORRUPTED FILES ({len(corrupted_files)} found):")
            for i, file_path in enumerate(corrupted_files[:10]):
                print(f"   {i+1}. {file_path}")
            if len(corrupted_files) > 10:
                print(f"   ... and {len(corrupted_files) - 10} more")

        # Show root file organization suggestions
        if root_files:
            print("\n📋 ROOT FILE ORGANIZATION SUGGESTIONS:")
            for destination, files in root_files.items():
                print(f"\n   📂 {destination}/ ({len(files)} files):")
                for file_path in files:
                    print(f"      • {file_path.name}")

        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE - NO CHANGES WERE MADE")
        print("   Review the suggestions above before deciding what to do")
        print("=" * 70)


def main():
    root_path = "/Users/agi_dev/Downloads/Consolidation-Repo"
    analyzer = SafeWorkspaceAnalyzer(root_path)
    analyzer.analyze_only()


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
