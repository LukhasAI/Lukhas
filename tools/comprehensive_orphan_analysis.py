#!/usr/bin/env python3
"""
Comprehensive Orphaned File/Directory Analysis for LUKHAS AI
Excludes libraries, virtual environments, and system files
Constellation Framework: ⚛️🧠🛡️
"""

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path


class ComprehensiveOrphanAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.all_python_files = set()
        self.imported_files = set()
        self.orphaned_files = set()

        # Directories to completely exclude from analysis
        self.excluded_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
            ".venv",
            "venv",
            "env",
            ".env",
            "virtualenv",
            "venvs",
            ".tox",
            "build",
            "dist",
            "egg-info",
            ".eggs",
            "node_modules",
            ".mypy_cache",
            ".ruff_cache",
            "site-packages",
            "lib",
            "lib64",
            "include",
            "bin",
            ".github",
            ".vscode",
            ".idea",
            ".DS_Store",
            "coverage",
            ".coverage",
            "wheels",
            ".wheelhouse",
            "pip-wheel-metadata",
            ".pip",
            "conda-meta",
            "pkgs",
            "envs",
            "Library",
            "Scripts",
            "DLLs",
            "migrations",
            "staticfiles",
            ".ipynb_checkpoints",
            ".nox",
            ".hypothesis",
            ".benchmarks",
            "test_results",
            "reports",
            "docs/_build",
            "target",
            "out",
            "output",
            "logs",
            "tmp",
            "temp",
            "cache",
            ".cache",
            "data",
            "backups",
            ".backups",
        }

        # File patterns that are system/library files
        self.excluded_patterns = {
            r"test_.*\.py$",  # Test files
            r"conftest\.py$",  # Pytest config
            r"setup\.py$",  # Setup files
            r"manage\.py$",  # Django manage
            r"wsgi\.py$",  # WSGI files
            r"asgi\.py$",  # ASGI files
            r"__version__\.py$",
            r"_version\.py$",
            r"\.pyc$",
            r"\.pyo$",
            r"\.pyd$",
            r"\.so$",
            r"\.egg$",
        }

        # Entry points for the LUKHAS system
        self.entry_points = {
            "main.py",
            "api/main.py",
            "serve/app.py",
            "orchestration/brain/primary_hub.py",
            "consciousness/unified/auto_consciousness.py",
        }

    def is_excluded_file(self, file_path: str) -> bool:
        """Check if file should be excluded based on patterns"""
        return any(re.search(pattern, file_path) for pattern in self.excluded_patterns)

    def is_library_import(self, import_name: str) -> bool:
        """Check if an import is from standard library or common packages"""
        # Python standard library modules (partial list)
        stdlib = {
            "os",
            "sys",
            "json",
            "re",
            "math",
            "random",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "typing",
            "pathlib",
            "urllib",
            "http",
            "email",
            "csv",
            "sqlite3",
            "hashlib",
            "logging",
            "argparse",
            "subprocess",
            "threading",
            "asyncio",
            "unittest",
            "doctest",
            "pdb",
            "pickle",
            "copy",
            "io",
            "time",
            "calendar",
            "decimal",
            "fractions",
            "statistics",
            "abc",
            "dataclasses",
            "enum",
            "types",
            "warnings",
            "weakref",
            "contextlib",
            "inspect",
            "traceback",
            "gc",
            "atexit",
            "builtins",
            "__future__",
            "__main__",
            "importlib",
        }

        # Common third-party packages
        third_party = {
            "numpy",
            "pandas",
            "matplotlib",
            "scipy",
            "sklearn",
            "tensorflow",
            "torch",
            "keras",
            "django",
            "flask",
            "fastapi",
            "requests",
            "urllib3",
            "beautifulsoup4",
            "selenium",
            "pytest",
            "setuptools",
            "pip",
            "wheel",
            "sqlalchemy",
            "pymongo",
            "redis",
            "celery",
            "pydantic",
            "uvicorn",
            "gunicorn",
            "aiohttp",
            "httpx",
            "openai",
            "anthropic",
            "langchain",
            "transformers",
            "pillow",
            "opencv",
            "nltk",
            "spacy",
            "streamlit",
            "gradio",
        }

        # Check if it's a standard or third-party library
        root_module = import_name.split(".")[0]
        return root_module in stdlib or root_module in third_party

    def find_all_python_files(self):
        """Find all Python files, excluding libraries and virtual environments"""
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            # Skip if we're in a library-like path
            root_path = Path(root)
            if any(excluded in root_path.parts for excluded in self.excluded_dirs):
                continue

            for file in files:
                if file.endswith(".py"):
                    full_path = root_path / file
                    relative_path = full_path.relative_to(self.root_path)

                    # Skip excluded patterns
                    if not self.is_excluded_file(str(relative_path)):
                        self.all_python_files.add(str(relative_path))

    def extract_imports(self, file_path: str) -> set[str]:
        """Extract imports from a Python file"""
        imports = set()
        full_path = self.root_path / file_path

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not self.is_library_import(alias.name):
                            imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not self.is_library_import(node.module):
                        imports.add(node.module)

        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            pass

        return imports

    def resolve_import_to_file(self, import_name: str) -> list[str]:
        """Resolve an import to actual file paths in our codebase"""
        possible_files = []

        # Skip library imports
        if self.is_library_import(import_name):
            return []

        parts = import_name.split(".")

        # Try as a module (directory with __init__.py)
        module_path = Path(*parts)
        init_file = module_path / "__init__.py"
        if (self.root_path / init_file).exists():
            possible_files.append(str(init_file))

        # Try as a direct file
        py_file = Path(*parts[:-1]) / f"{parts[-1]}.py" if len(parts) > 1 else Path(f"{parts[0]}.py")

        if (self.root_path / py_file).exists():
            possible_files.append(str(py_file))

        # Try with common project prefixes
        for prefix in ["lukhas", "lukhas"]:
            prefixed_import = f"{prefix}.{import_name}"
            parts = prefixed_import.split(".")

            module_path = Path(*parts)
            init_file = module_path / "__init__.py"
            if (self.root_path / init_file).exists():
                possible_files.append(str(init_file))

            py_file = Path(*parts[:-1]) / f"{parts[-1]}.py" if len(parts) > 1 else Path(f"{parts[0]}.py")

            if (self.root_path / py_file).exists():
                possible_files.append(str(py_file))

        return possible_files

    def analyze_imports(self):
        """Build import graph for all Python files"""
        import_graph = defaultdict(set)  # file -> files it imports
        imported_by = defaultdict(set)  # file -> files that import it

        for py_file in self.all_python_files:
            imports = self.extract_imports(py_file)

            for import_name in imports:
                resolved_files = self.resolve_import_to_file(import_name)
                for resolved_file in resolved_files:
                    if resolved_file in self.all_python_files:
                        import_graph[py_file].add(resolved_file)
                        imported_by[resolved_file].add(py_file)

        return import_graph, imported_by

    def find_reachable_files(self, import_graph: dict) -> set[str]:
        """Find all files reachable from entry points"""
        reachable = set()
        to_visit = list(self.entry_points)

        while to_visit:
            current = to_visit.pop()
            if current in reachable or current not in self.all_python_files:
                continue

            reachable.add(current)

            # Add all files imported by this file
            for imported_file in import_graph.get(current, set()):
                if imported_file not in reachable:
                    to_visit.append(imported_file)

        return reachable

    def categorize_by_directory(self, files: set[str]) -> dict[str, list[str]]:
        """Categorize files by their parent directory"""
        categories = defaultdict(list)

        for file in files:
            parts = Path(file).parts
            # Use first-level directory
            category = parts[0] if len(parts) > 1 else "root"
            categories[category].append(file)

        # Sort files within each category
        for category in categories:
            categories[category].sort()

        return dict(categories)

    def analyze_directory_usage(self) -> dict[str, dict]:
        """Analyze usage statistics for each directory"""
        dir_stats = defaultdict(
            lambda: {
                "total": 0,
                "used": 0,
                "orphaned": 0,
                "files": [],
                "orphaned_files": [],
            }
        )

        # Count all files
        for file in self.all_python_files:
            parts = Path(file).parts
            dir_name = parts[0] if len(parts) > 1 else "root"
            dir_stats[dir_name]["total"] += 1
            dir_stats[dir_name]["files"].append(file)

        # Count orphaned files
        for file in self.orphaned_files:
            parts = Path(file).parts
            dir_name = parts[0] if len(parts) > 1 else "root"
            dir_stats[dir_name]["orphaned"] += 1
            dir_stats[dir_name]["orphaned_files"].append(file)

        # Calculate used files
        for dir_name in dir_stats:
            dir_stats[dir_name]["used"] = dir_stats[dir_name]["total"] - dir_stats[dir_name]["orphaned"]
            dir_stats[dir_name]["usage_percentage"] = (
                (dir_stats[dir_name]["used"] / dir_stats[dir_name]["total"] * 100)
                if dir_stats[dir_name]["total"] > 0
                else 0
            )

        return dict(dir_stats)

    def identify_module_patterns(self, orphaned_by_dir: dict) -> dict[str, str]:
        """Identify patterns in orphaned modules to understand why they're unused"""
        patterns = {}

        for directory, files in orphaned_by_dir.items():
            if not files:
                continue

            # Analyze file naming patterns
            has_test = any("test" in f for f in files)
            has_example = any("example" in f or "demo" in f for f in files)
            has_backup = any("backup" in f or "old" in f or "copy" in f for f in files)
            has_experimental = any("experimental" in f or "draft" in f or "wip" in f for f in files)
            has_legacy = any("legacy" in f or "deprecated" in f for f in files)

            # Determine primary pattern
            if has_test:
                patterns[directory] = "test_files"
            elif has_example:
                patterns[directory] = "examples"
            elif has_backup:
                patterns[directory] = "backups"
            elif has_experimental:
                patterns[directory] = "experimental"
            elif has_legacy:
                patterns[directory] = "legacy"
            elif directory in ["CLAUDE_ARMY", "workspaces"]:
                patterns[directory] = "agent_workspaces"
            elif directory in ["NIAS_THEORY", "qim"]:
                patterns[directory] = "theoretical"
            elif directory in ["api", "serve", "bridge"]:
                patterns[directory] = "api_implementations"
            elif directory in ["branding", "docs", "documentation"]:
                patterns[directory] = "documentation"
            else:
                patterns[directory] = "unknown"

        return patterns

    def generate_report(self) -> dict:
        """Generate comprehensive orphan analysis report"""
        print("🔍 Finding all Python files (excluding libraries)...")
        self.find_all_python_files()

        print("📊 Analyzing import relationships...")
        import_graph, imported_by = self.analyze_imports()

        print("🌐 Finding reachable files from entry points...")
        reachable = self.find_reachable_files(import_graph)

        # Find orphaned files
        self.orphaned_files = self.all_python_files - reachable

        # Remove entry points from orphaned list
        self.orphaned_files -= self.entry_points

        # Categorize orphaned files by directory
        orphaned_by_dir = self.categorize_by_directory(self.orphaned_files)

        # Analyze directory usage
        dir_stats = self.analyze_directory_usage()

        # Identify patterns
        patterns = self.identify_module_patterns(orphaned_by_dir)

        # Build import statistics
        import_counts = defaultdict(int)
        for file, importers in imported_by.items():
            import_counts[file] = len(importers)

        most_imported = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        # Calculate statistics
        total_files = len(self.all_python_files)
        orphaned_count = len(self.orphaned_files)
        used_count = total_files - orphaned_count

        report = {
            "summary": {
                "total_python_files": total_files,
                "used_files": used_count,
                "orphaned_files": orphaned_count,
                "orphaned_percentage": ((orphaned_count / total_files * 100) if total_files > 0 else 0),
                "entry_points": list(self.entry_points),
                "analysis_timestamp": str(Path.cwd()),
            },
            "directory_statistics": dir_stats,
            "orphaned_by_directory": orphaned_by_dir,
            "directory_patterns": patterns,
            "most_imported_files": most_imported,
            "recommendations": self.generate_recommendations(dir_stats, patterns),
        }

        return report

    def generate_recommendations(self, dir_stats: dict, patterns: dict) -> list[dict]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        for directory, stats in dir_stats.items():
            if stats["orphaned"] == 0:
                continue

            pattern = patterns.get(directory, "unknown")
            orphan_pct = stats["usage_percentage"]

            if pattern == "agent_workspaces":
                recommendations.append(
                    {
                        "directory": directory,
                        "action": "ARCHIVE",
                        "reason": "Agent workspace experiments",
                        "priority": "low",
                        "files_affected": stats["orphaned"],
                    }
                )
            elif pattern == "theoretical":
                recommendations.append(
                    {
                        "directory": directory,
                        "action": "REVIEW",
                        "reason": "Theoretical/experimental code may contain innovations",
                        "priority": "medium",
                        "files_affected": stats["orphaned"],
                    }
                )
            elif pattern == "legacy":
                recommendations.append(
                    {
                        "directory": directory,
                        "action": "ARCHIVE",
                        "reason": "Legacy/deprecated implementations",
                        "priority": "medium",
                        "files_affected": stats["orphaned"],
                    }
                )
            elif pattern == "api_implementations" and orphan_pct < 50:
                recommendations.append(
                    {
                        "directory": directory,
                        "action": "INTEGRATE",
                        "reason": "Unused API implementations could be valuable",
                        "priority": "high",
                        "files_affected": stats["orphaned"],
                    }
                )
            elif orphan_pct < 20:
                recommendations.append(
                    {
                        "directory": directory,
                        "action": "KEEP",
                        "reason": f"High usage rate ({100 - orphan_pct:.1f}%)",
                        "priority": "low",
                        "files_affected": stats["orphaned"],
                    }
                )
            elif orphan_pct > 80:
                recommendations.append(
                    {
                        "directory": directory,
                        "action": "REVIEW",
                        "reason": f"Very low usage rate ({100 - orphan_pct:.1f}%)",
                        "priority": "high",
                        "files_affected": stats["orphaned"],
                    }
                )

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return recommendations


def print_report(report: dict):
    """Print formatted report to console"""
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE ORPHAN ANALYSIS REPORT")
    print("=" * 80)

    # Summary
    summary = report["summary"]
    print("\n📊 SUMMARY")
    print(f"Total Python files (excluding libraries): {summary['total_python_files']}")
    print(f"Used files: {summary['used_files']}")
    print(f"Orphaned files: {summary['orphaned_files']}")
    print(f"Orphaned percentage: {summary['orphaned_percentage']:.1f}%")

    # Directory statistics
    print("\n📁 DIRECTORY STATISTICS")
    print("-" * 80)
    print(f"{'Directory':<30} {'Total':<10} {'Used':<10} {'Orphaned':<10} {'Usage %':<10}")
    print("-" * 80)

    dir_stats = report["directory_statistics"]
    # Sort by orphaned count descending
    sorted_dirs = sorted(dir_stats.items(), key=lambda x: x[1]["orphaned"], reverse=True)

    for directory, stats in sorted_dirs[:20]:
        if stats["total"] > 0:
            print(
                f"{directory:<30} {stats['total']:<10} {stats['used']:<10} "
                f"{stats['orphaned']:<10} {stats['usage_percentage']:<10.1f}"
            )

    # Pattern analysis
    print("\n🔍 DIRECTORY PATTERNS")
    print("-" * 80)
    patterns = report["directory_patterns"]
    pattern_counts = defaultdict(list)
    for directory, pattern in patterns.items():
        pattern_counts[pattern].append(directory)

    for pattern, dirs in sorted(pattern_counts.items()):
        print(f"\n{pattern.upper().replace('_', ' ')}:")
        for d in dirs[:5]:
            orphaned = dir_stats[d]["orphaned"]
            print(f"  - {d} ({orphaned} orphaned files)")

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 80)
    for rec in report["recommendations"][:10]:
        emoji = {"ARCHIVE": "📦", "REVIEW": "🔍", "INTEGRATE": "🔗", "KEEP": "✅"}.get(rec["action"], "❓")
        print(f"\n{emoji} {rec['directory']}")
        print(f"   Action: {rec['action']}")
        print(f"   Reason: {rec['reason']}")
        print(f"   Priority: {rec['priority'].upper()}")
        print(f"   Files affected: {rec['files_affected']}")

    # Most imported files
    print("\n⭐ MOST IMPORTED FILES")
    print("-" * 80)
    for file, count in report["most_imported_files"][:10]:
        print(f"{file:<60} ({count} imports)")


def main():
    repo_root = Path(__file__).parent.parent
    analyzer = ComprehensiveOrphanAnalyzer(repo_root)

    print("🚀 Starting comprehensive orphan analysis...")
    print("⚠️  Excluding all library files, virtual environments, and system files")

    report = analyzer.generate_report()

    # Print report
    print_report(report)

    # Save detailed JSON report
    report_path = repo_root / "comprehensive_orphan_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n💾 Detailed report saved to: {report_path}")

    # Generate actionable summary
    print("\n" + "=" * 80)
    print("🎯 ACTIONABLE SUMMARY")
    print("=" * 80)

    high_priority = [r for r in report["recommendations"] if r["priority"] == "high"]
    if high_priority:
        print(f"\n🔴 HIGH PRIORITY ({len(high_priority)} directories):")
        for rec in high_priority:
            print(f"  - {rec['directory']}: {rec['action']} ({rec['files_affected']} files)")

    # Calculate potential cleanup
    archive_files = sum(
        report["directory_statistics"][r["directory"]]["orphaned"]
        for r in report["recommendations"]
        if r["action"] == "ARCHIVE"
    )

    print(f"\n📦 Potential cleanup: {archive_files} files can be safely archived")
    print(f"🔍 Files needing review: {report['summary']['orphaned_files'] - archive_files}")


if __name__ == "__main__":
    main()
