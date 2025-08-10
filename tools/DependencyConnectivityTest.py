#!/usr/bin/env python3
"""
lukhas SYSTEM DEPENDENCY & CONNECTIVITY TEST
=======================================
Analyzes the lukhas system for dependency issues and connectivity problems.
"""

import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path


class LambdaDependencyAnalyzer:

    def __init__(self, lambda_root):
        self.lambda_root = Path(lambda_root)
        self.python_files = []
        self.imports = defaultdict(set)
        self.local_imports = defaultdict(set)
        self.external_imports = defaultdict(set)
        self.broken_imports = defaultdict(set)
        self.isolated_files = set()
        self.connectivity_map = defaultdict(set)

    def scan_python_files(self):
        """Scan all Python files in the lukhas system."""
        print("🔍 Scanning Python files in lukhas system...")
        for file_path in self.lambda_root.rglob("*.py"):
            if "__pycache__" not in str(file_path):
                self.python_files.append(file_path)
        print(f"📊 Found {len(self.python_files)} Python files")
        return self.python_files

    def extract_imports(self, file_path):
        """Extract imports from a Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse with AST for accurate import detection
            try:
                tree = ast.parse(content)
                imports = set()

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module)

                return imports
            except SyntaxError:
                # Fallback to regex if AST parsing fails
                return self.extract_imports_regex(content)

        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return set()

    def extract_imports_regex(self, content):
        """Fallback regex-based import extraction."""
        imports = set()

        # Match import statements
        import_patterns = [
            r"^\s*import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)",
            r"^\s*from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import",
        ]

        for line in content.split("\n"):
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.add(match.group(1))

        return imports

    def analyze_imports(self):
        """Analyze all imports in the system."""
        print("🔗 Analyzing imports and dependencies...")

        for file_path in self.python_files:
            rel_path = file_path.relative_to(self.lambda_root)
            imports = self.extract_imports(file_path)
            self.imports[str(rel_path)] = imports

            # Categorize imports
            for imp in imports:
                if self.is_local_import(imp, rel_path):
                    self.local_imports[str(rel_path)].add(imp)
                else:
                    self.external_imports[str(rel_path)].add(imp)

    def is_local_import(self, import_name, file_path):
        """Check if import is local to the lukhas system."""
        # Common lukhas system module prefixes
        unicode_prefixes = [
            "agent",
            "auth",
            "bio",
            "brain",
            "connectivity",
            "governance",
            "Lukhas_ID",
            "interface",
            "orchestration",
            "vision",
            "voice",
            "applications",
            "tests",
            "config",
            "shared",
            "meta",
        ]

        for prefix in unicode_prefixes:
            if import_name.startswith(prefix):
                return True

        # Check relative imports
        return bool(import_name.startswith("."))

    def check_broken_imports(self):
        """Check for broken local imports."""
        print("🔍 Checking for broken imports...")

        for file_path, imports in self.local_imports.items():
            for imp in imports:
                if not self.import_exists(imp):
                    self.broken_imports[file_path].add(imp)

    def import_exists(self, import_name):
        """Check if a local import actually exists."""
        # Convert import to file path
        parts = import_name.split(".")

        # Try different combinations
        possible_paths = [
            Path(*parts) / "__init__.py",
            Path(*parts).with_suffix(".py"),
            Path(*parts[:-1]) / f"{parts[-1]}.py",
        ]

        for path in possible_paths:
            full_path = self.lambda_root / path
            if full_path.exists():
                return True

        return False

    def find_isolated_files(self):
        """Find files that are not imported by any other file."""
        print("🏝️  Finding isolated files...")

        all_files = {str(f.relative_to(self.lambda_root)) for f in self.python_files}
        imported_files = set()

        # Collect all locally imported modules
        for imports in self.local_imports.values():
            for imp in imports:
                # Convert import to potential file paths
                parts = imp.split(".")
                possible_files = [
                    f"{'/'.join(parts)}.py",
                    f"{'/'.join(parts)}/__init__.py",
                ]
                imported_files.update(possible_files)

        # Find files not imported anywhere
        for file_path in all_files:
            file_imported = False
            for imported in imported_files:
                if file_path.endswith(imported.replace("/", os.sep)):
                    file_imported = True
                    break

            if not file_imported and not file_path.endswith("__init__.py"):
                self.isolated_files.add(file_path)

    def build_connectivity_map(self):
        """Build a connectivity map showing file relationships."""
        print("🗺️  Building connectivity map...")

        for file_path, imports in self.local_imports.items():
            for imp in imports:
                self.connectivity_map[file_path].add(imp)

    def generate_report(self):
        """Generate comprehensive dependency report."""
        report = {
            "timestamp": "2025-06-08",
            "total_files": len(self.python_files),
            "total_imports": sum(len(imports) for imports in self.imports.values()),
            "local_imports": sum(
                len(imports) for imports in self.local_imports.values()
            ),
            "external_imports": sum(
                len(imports) for imports in self.external_imports.values()
            ),
            "broken_imports_count": sum(
                len(broken) for broken in self.broken_imports.values()
            ),
            "isolated_files_count": len(self.isolated_files),
            "summary": {
                "files_analyzed": len(self.python_files),
                "connectivity_health": (
                    "GOOD" if len(self.broken_imports) < 10 else "NEEDS_ATTENTION"
                ),
                "isolation_level": "LOW" if len(self.isolated_files) < 50 else "HIGH",
            },
            "details": {
                "broken_imports": dict(self.broken_imports),
                "isolated_files": list(self.isolated_files),
                "top_importers": self.get_top_importers(),
                "dependency_clusters": self.get_dependency_clusters(),
            },
        }

        return report

    def get_top_importers(self):
        """Get files with most imports."""
        import_counts = {file: len(imports) for file, imports in self.imports.items()}
        return sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    def get_dependency_clusters(self):
        """Identify dependency clusters."""
        clusters = defaultdict(list)
        for file_path in self.python_files:
            rel_path = file_path.relative_to(self.lambda_root)
            module = str(rel_path).split("/")[0] if "/" in str(rel_path) else "root"
            clusters[module].append(str(rel_path))
        return dict(clusters)

    def print_summary(self, report):
        """Print a summary of the analysis."""
        print("\n" + "=" * 60)
        print("🎯 lukhas SYSTEM DEPENDENCY & CONNECTIVITY ANALYSIS")
        print("=" * 60)
        print(f"📊 Total Python Files: {report['total_files']}")
        print(f"🔗 Total Imports: {report['total_imports']}")
        print(f"🏠 Local Imports: {report['local_imports']}")
        print(f"🌐 External Imports: {report['external_imports']}")
        print(f"❌ Broken Imports: {report['broken_imports_count']}")
        print(f"🏝️  Isolated Files: {report['isolated_files_count']}")

        print(f"\n🏥 System Health: {report['summary']['connectivity_health']}")
        print(f"🔍 Isolation Level: {report['summary']['isolation_level']}")

        if report["details"]["broken_imports"]:
            print("\n⚠️  BROKEN IMPORTS:")
            for file, broken in list(report["details"]["broken_imports"].items())[:5]:
                print(f"   📄 {file}: {', '.join(list(broken)[:3])}")

        if report["details"]["isolated_files"]:
            print("\n🏝️  ISOLATED FILES (showing first 10):")
            for file in list(report["details"]["isolated_files"])[:10]:
                print(f"   📄 {file}")

        print("\n📈 TOP IMPORTERS:")
        for file, count in report["details"]["top_importers"][:5]:
            print(f"   📄 {file}: {count} imports")


def main():
    lambda_root = Path.cwd()  # Assumes we're running from system directory

    analyzer = LambdaDependencyAnalyzer(lambda_root)

    # Run analysis
    analyzer.scan_python_files()
    analyzer.analyze_imports()
    analyzer.check_broken_imports()
    analyzer.find_isolated_files()
    analyzer.build_connectivity_map()

    # Generate and display report
    report = analyzer.generate_report()
    analyzer.print_summary(report)

    # Save detailed report
    with open("lambda_dependency_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("\n💾 Detailed report saved to: lambda_dependency_report.json")

    return report


if __name__ == "__main__":
    main()
