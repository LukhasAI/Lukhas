#!/usr/bin/env python3
"""
Root Directory Audit and Reorganization Plan
Analyzes root-level directories and proposes a reorganization plan.
"""

import contextlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class RootDirectoryAuditor:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path.cwd()
        self.core_modules = [
            "core",
            "consciousness",
            "memory",
            "qi",
            "emotion",
            "governance",
            "bridge",
        ]
        self.essential_root = {
            ".git",
            ".github",
            ".venv",
            "docs",
            "tests",
            "tools",
            "config",
            "requirements.txt",
            "README.md",
            "LICENSE",
            "main.py",
            ".env.example",
        }
        self.categories: dict[str, list[str]] = {
            "core_modules": [],
            "should_be_submodules": [],
            "tools_and_utils": [],
            "documentation": [],
            "testing": [],
            "deployment": [],
            "archive_candidates": [],
            "unknown_purpose": [],
        }
        self.directory_analysis: dict[str, dict[str, Any]] = {}

    def analyze_root(self) -> dict[str, Any]:
        items = [p.name for p in self.repo_root.iterdir() if p.is_dir() and not p.name.startswith(".")]
        for name in sorted(items):
            self.analyze_directory(name)
        return self.generate_reorganization_plan()

    def analyze_directory(self, directory: str) -> None:
        path = self.repo_root / directory
        analysis = {
            "name": directory,
            "size_mb": self.get_directory_size(path),
            "file_count": self.count_files(path),
            "has_init": (path / "__init__.py").exists(),
            "has_readme": (path / "README.md").exists(),
            "has_tests": self.has_tests(path),
            "suggested_action": "",
            "suggested_location": "",
            "reason": "",
        }

        if directory in self.core_modules:
            self.categories["core_modules"].append(directory)
            analysis["suggested_action"] = "ENHANCE"
            analysis["reason"] = "Core module: add docs/tests/examples"
        elif directory in [
            "api",
            "architectures",
            "bio",
            "creativity",
            "dream",
            "ethics",
            "identity",
            "learning",
            "orchestration",
            "reasoning",
            "symbolic",
            "voice",
        ]:
            self.categories["should_be_submodules"].append(directory)
            target = self.suggest_module_for_directory(directory)
            analysis["suggested_action"] = "MERGE"
            analysis["suggested_location"] = target
            analysis["reason"] = f"Belongs under {target}"
        elif directory in ["tools", "analysis_tools", "healing"]:
            self.categories["tools_and_utils"].append(directory)
            analysis["suggested_action"] = "CONSOLIDATE"
            analysis["suggested_location"] = "tools/"
            analysis["reason"] = "Utility/tool — consolidate"
        elif directory in ["docs", "deployment", "config"]:
            self.categories["documentation"].append(directory)
            analysis["suggested_action"] = "KEEP"
            analysis["reason"] = "Essential root directory"
        elif directory in ["tests", "red_team", "compliance"]:
            self.categories["testing"].append(directory)
            analysis["suggested_action"] = "REORGANIZE"
            analysis["suggested_location"] = "tests/"
            analysis["reason"] = "Consolidate testing"
        elif directory in ["misc", "trace", "_context_", "security"]:
            self.categories["archive_candidates"].append(directory)
            analysis["suggested_action"] = "ARCHIVE"
            analysis["reason"] = "Unclear purpose"
        else:
            self.categories["unknown_purpose"].append(directory)
            analysis["suggested_action"] = "REVIEW"
            analysis["reason"] = "Unknown purpose"

        self.directory_analysis[directory] = analysis

    @staticmethod
    def suggest_module_for_directory(directory: str) -> str:
        mappings = {
            "api": "bridge",
            "architectures": "core",
            "bio": "qi",
            "creativity": "consciousness",
            "dream": "consciousness",
            "ethics": "governance",
            "identity": "governance",
            "learning": "memory",
            "orchestration": "core",
            "reasoning": "consciousness",
            "symbolic": "core",
            "voice": "bridge",
        }
        return mappings.get(directory, "core")

    @staticmethod
    def get_directory_size(path: Path) -> float:
        total = 0
        for dirpath, _dirnames, filenames in os.walk(path):
            for filename in filenames:
                fp = Path(dirpath) / filename
                with contextlib.suppress(Exception):
                    total += fp.stat().st_size
        return round(total / 1024 / 1024, 2)

    @staticmethod
    def count_files(path: Path) -> int:
        count = 0
        for _dirpath, _dirs, files in os.walk(path):
            count += sum(1 for f in files if f.endswith(".py"))
        return count

    @staticmethod
    def has_tests(path: Path) -> bool:
        if (path / "tests").exists():
            return True
        for _root, _dirs, files in os.walk(path):
            if any(f.startswith("test_") and f.endswith(".py") for f in files):
                return True
        return False

    def generate_reorganization_plan(self) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_directories": len(self.directory_analysis),
                "core_modules": len(self.categories["core_modules"]),
                "to_merge": len(self.categories["should_be_submodules"]),
                "to_archive": len(self.categories["archive_candidates"]),
                "to_review": len(self.categories["unknown_purpose"]),
            },
            "categories": self.categories,
            "detailed_analysis": self.directory_analysis,
            "actions": self.create_action_plan(),
        }

    def create_action_plan(self) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        for module in self.categories["core_modules"]:
            actions.append(
                {
                    "priority": 1,
                    "action": "ENHANCE_MODULE",
                    "target": module,
                    "tasks": [
                        f"Create {module}/README.md",
                        f"Add tests in {module}/tests/",
                        f"Add examples in {module}/examples/",
                    ],
                }
            )
        for directory in self.categories["should_be_submodules"]:
            target = self.suggest_module_for_directory(directory)
            actions.append(
                {
                    "priority": 2,
                    "action": "MERGE_DIRECTORY",
                    "target": directory,
                    "destination": target,
                }
            )
        return actions


def main() -> None:
    auditor = RootDirectoryAuditor()
    plan = auditor.analyze_root()
    out = Path("docs/reports/analysis/root_reorg_plan.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2))
    print(f"📄 Plan saved to {out}")


if __name__ == "__main__":
    main()
