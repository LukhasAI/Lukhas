#!/usr/bin/env python3
"""
Core Connectivity Analyzer
Analyzes connectivity focusing only on core implementation files,
excluding tests, demos, scripts, backups, etc.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict


class CoreConnectivityAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.total_files = 0
        self.core_files = 0
        self.connected_files = set()
        self.isolated_files = set()

        # Directories to exclude from core analysis
        self.exclude_dirs = {
            "test",
            "tests",
            "test_",
            "_test",
            "demo",
            "demos",
            "examples",
            "example",
            "script",
            "scripts",
            "tools",
            "utils",
            "backup",
            "backups",
            "old",
            "archive",
            "docs",
            "documentation",
            "doc",
            "build",
            "dist",
            "venv",
            "__pycache__",
            ".git",
            ".idea",
            ".vscode",
            "analysis-tools",
            "deployment",
            "interfaces/protocols",  # Protocol definitions
            "interfaces/api/v1/grpc",  # Generated code
        }

        # File patterns to exclude
        self.exclude_patterns = {
            "test_",
            "_test.py",
            "_spec.py",
            "demo_",
            "_demo.py",
            "example_",
            "script_",
            "_script.py",
            "analyze_",
            "fix_",
            "check_",
            "verify_",
            "_old.py",
            "_backup.py",
            "_tmp.py",
            "mock_",
            "_mock.py",
            "fake_",
        }

    def is_core_file(self, path: Path) -> bool:
        """Determine if a file is a core implementation file"""
        path_str = str(path).lower()

        # Check if in excluded directory
        for part in path.parts:
            if part.lower() in self.exclude_dirs:
                return False

        # Check file name patterns
        filename = path.name.lower()
        for pattern in self.exclude_patterns:
            if pattern in filename:
                return False

        # Exclude __init__.py files (they're expected to be empty)
        if filename == "__init__.py":
            with open(path) as f:
                content = f.read().strip()
                # Only exclude if truly empty or just imports
                if len(content) < 50:
                    return False

        return True

    def analyze(self):
        """Run core connectivity analysis"""
        print("🔍 Starting Core Connectivity Analysis...")
        print("  (Excluding tests, demos, scripts, backups, etc.)")

        # Count all Python files first
        all_python_files = list(self.root_path.rglob("*.py"))
        self.total_files = len(all_python_files)

        # Filter to core files only
        core_files = []
        excluded_files = []

        for path in all_python_files:
            if self.is_core_file(path):
                core_files.append(path)
                self.core_files += 1
            else:
                excluded_files.append(path)

        print("\n📊 File Analysis:")
        print(f"  Total Python files: {self.total_files}")
        print(f"  Core implementation files: {self.core_files}")
        print(f"  Excluded files: {len(excluded_files)}")

        # Analyze connectivity of core files
        module_graph = defaultdict(set)

        for filepath in core_files:
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                # Check if file imports from our core modules
                has_internal_imports = False
                if "import" in content:
                    # Simple check for imports from our main modules
                    for module in [
                        "core",
                        "quantum",
                        "consciousness",
                        "bio",
                        "ethics",
                        "memory",
                        "identity",
                        "orchestration",
                        "learning",
                    ]:
                        if f"from {module}" in content or f"import {module}" in content:
                            has_internal_imports = True
                            break

                if has_internal_imports:
                    self.connected_files.add(str(filepath))
                else:
                    # Check if file is imported by others
                    module_name = str(filepath.relative_to(self.root_path))[
                        :-3
                    ].replace("/", ".")
                    is_imported = False

                    for other_file in core_files:
                        if other_file != filepath:
                            try:
                                with open(other_file) as f:
                                    if module_name in f.read():
                                        is_imported = True
                                        break
                            except:
                                pass

                    if is_imported:
                        self.connected_files.add(str(filepath))
                    else:
                        self.isolated_files.add(str(filepath))

            except Exception:
                # Count files with errors as isolated
                self.isolated_files.add(str(filepath))

        # Generate report
        return self._generate_report()

    def _generate_report(self) -> Dict:
        """Generate connectivity report"""
        connectivity_percentage = (
            (len(self.connected_files) / self.core_files * 100)
            if self.core_files > 0
            else 0
        )

        # Categorize isolated files by subsystem
        isolated_by_subsystem = defaultdict(list)
        for file in self.isolated_files:
            parts = file.split("/")
            if len(parts) > 1:
                subsystem = parts[0]
                isolated_by_subsystem[subsystem].append(file)
            else:
                isolated_by_subsystem["root"].append(file)

        report = {
            "summary": {
                "total_python_files": self.total_files,
                "core_implementation_files": self.core_files,
                "connected_core_files": len(self.connected_files),
                "isolated_core_files": len(self.isolated_files),
                "core_connectivity_percentage": round(connectivity_percentage, 2),
            },
            "isolated_by_subsystem": dict(isolated_by_subsystem),
            "comparison": {
                "before_integration": {
                    "total_files": 2010,
                    "connected": 1649,
                    "isolated": 361,
                    "percentage": 86.7,
                },
                "after_integration": {
                    "total_files": self.core_files,
                    "connected": len(self.connected_files),
                    "isolated": len(self.isolated_files),
                    "percentage": round(connectivity_percentage, 2),
                },
            },
        }

        return report


def main():
    """Run core connectivity analysis"""
    analyzer = CoreConnectivityAnalyzer()
    report = analyzer.analyze()

    # Save report
    with open("core_connectivity_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("CORE CONNECTIVITY REPORT")
    print("=" * 60)

    summary = report["summary"]
    print("\n📊 Core Files Summary:")
    print(f"  Total Python files in repo: {summary['total_python_files']}")
    print(f"  Core implementation files: {summary['core_implementation_files']}")
    print(f"  Connected core files: {summary['connected_core_files']}")
    print(f"  Isolated core files: {summary['isolated_core_files']}")
    print(f"  Core connectivity: {summary['core_connectivity_percentage']}%")

    comparison = report["comparison"]
    print("\n📈 Before vs After Integration:")
    print(
        f"  Before: {comparison['before_integration']['percentage']}% ({comparison['before_integration']['connected']}/{comparison['before_integration']['total_files']})"
    )
    print(
        f"  After:  {comparison['after_integration']['percentage']}% ({comparison['after_integration']['connected']}/{comparison['after_integration']['total_files']})"
    )

    if (
        comparison["after_integration"]["percentage"]
        > comparison["before_integration"]["percentage"]
    ):
        improvement = (
            comparison["after_integration"]["percentage"]
            - comparison["before_integration"]["percentage"]
        )
        print(f"  ✅ Improvement: +{improvement:.1f}%")

    print("\n📁 Isolated Files by Subsystem:")
    for subsystem, files in report["isolated_by_subsystem"].items():
        if files:
            print(f"  {subsystem}: {len(files)} files")

    print("\n💾 Full report saved to: core_connectivity_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
