#!/usr/bin/env python3
"""
Find Unused Files in LUKHAS Codebase
Identifies Python files that are never imported by any other file.
"""
import ast
import json
import os
from pathlib import Path
from typing import Dict, List, Set


class UnusedFileFinder:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.all_python_files = set()
        self.imported_files = set()
        self.import_map = {}  # file -> list of files it imports

    def get_module_path_from_import(
        self, import_name: str, current_file: Path
    ) -> Set[str]:
        """Convert import statement to possible file paths."""
        possible_paths = set()

        # Convert module.submodule to file paths
        parts = import_name.split(".")

        # Try as a module path
        module_path = os.path.join(*parts) + ".py"
        possible_paths.add(module_path)

        # Try as a package __init__.py
        package_path = os.path.join(*parts, "__init__.py")
        possible_paths.add(package_path)

        # Try relative to current file
        if current_file.parent != self.root_path:
            rel_dir = current_file.parent
            rel_module = rel_dir / (parts[-1] + ".py")
            if rel_module.exists():
                rel_path = rel_module.relative_to(self.root_path)
                possible_paths.add(str(rel_path))

        return possible_paths

    def extract_imports(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file."""
        imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        # Handle relative imports
                        if node.level > 0:
                            # Relative import
                            parent_parts = str(
                                file_path.parent.relative_to(self.root_path)
                            ).split("/")
                            if node.level <= len(parent_parts):
                                base = ".".join(
                                    parent_parts[: len(parent_parts) - node.level + 1]
                                )
                                if node.module:
                                    imports.append(f"{base}.{node.module}")
                                else:
                                    imports.append(base)
        except:
            pass  # Skip files with syntax errors

        return imports

    def scan_codebase(self):
        """Scan all Python files and track imports."""
        # Find all Python files
        for py_file in self.root_path.rglob("*.py"):
            # Skip certain directories
            if any(
                skip in str(py_file)
                for skip in [
                    "__pycache__",
                    ".git",
                    "venv",
                    ".venv",
                    "build",
                    "dist",
                    ".egg-info",
                    "node_modules",
                ]
            ):
                continue

            rel_path = py_file.relative_to(self.root_path)
            self.all_python_files.add(str(rel_path))

            # Extract imports
            imports = self.extract_imports(py_file)
            self.import_map[str(rel_path)] = imports

            # Track which files are imported
            for imp in imports:
                possible_paths = self.get_module_path_from_import(imp, py_file)
                for path in possible_paths:
                    self.imported_files.add(path)

    def find_unused_files(self) -> Dict:
        """Find files that are never imported."""
        # Special files that are entry points (not imported but used)
        entry_points = {
            "main.py",
            "app.py",
            "run.py",
            "manage.py",
            "setup.py",
            "conftest.py",
            "__main__.py",
        }

        # Files that are unused
        unused_files = []

        for file_path in self.all_python_files:
            file_name = os.path.basename(file_path)

            # Skip test files (they're run, not imported)
            if "test_" in file_name or "_test.py" in file_name:
                continue

            # Skip example files
            if "example" in file_path or "demo" in file_path:
                continue

            # Skip scripts (they're executed directly)
            if file_path.startswith("scripts/"):
                continue

            # Skip entry points
            if file_name in entry_points:
                continue

            # Check if file is imported anywhere
            if file_path not in self.imported_files:
                # Also check without .py extension
                module_path = file_path[:-3] if file_path.endswith(".py") else file_path
                module_as_import = module_path.replace("/", ".")

                # Check if any file imports this module
                is_imported = False
                for imports in self.import_map.values():
                    if any(
                        module_as_import in imp or module_path in imp for imp in imports
                    ):
                        is_imported = True
                        break

                if not is_imported:
                    unused_files.append(file_path)

        # Categorize unused files
        categorized = {
            "benchmarks": [],
            "tests": [],
            "tools": [],
            "examples": [],
            "core_modules": [],
            "other": [],
        }

        for file_path in sorted(unused_files):
            if file_path.startswith("benchmarks/"):
                categorized["benchmarks"].append(file_path)
            elif file_path.startswith("tests/"):
                categorized["tests"].append(file_path)
            elif file_path.startswith("tools/"):
                categorized["tools"].append(file_path)
            elif file_path.startswith("examples/"):
                categorized["examples"].append(file_path)
            elif any(
                file_path.startswith(f"{module}/")
                for module in [
                    "core",
                    "memory",
                    "consciousness",
                    "learning",
                    "identity",
                    "orchestration",
                    "api",
                    "bio",
                    "symbolic",
                    "quantum",
                ]
            ):
                categorized["core_modules"].append(file_path)
            else:
                categorized["other"].append(file_path)

        return {
            "total_files": len(self.all_python_files),
            "unused_files": len(unused_files),
            "usage_rate": 1 - (len(unused_files) / len(self.all_python_files)),
            "categorized": categorized,
            "unused_list": unused_files[:50],  # First 50 for review
        }


def main():
    """Main entry point."""
    root_path = Path(__file__).parent.parent

    print("🔍 Finding unused files in LUKHAS codebase...")

    finder = UnusedFileFinder(root_path)
    finder.scan_codebase()

    report = finder.find_unused_files()

    # Save report
    report_path = root_path / "scripts" / "unused_files_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 Unused Files Report")
    print("=" * 50)
    print(f"Total Python files: {report['total_files']}")
    print(f"Unused files: {report['unused_files']}")
    print(f"Usage rate: {report['usage_rate']:.1%}")

    print("\n📁 Unused files by category:")
    for category, files in report["categorized"].items():
        if files:
            print(f"\n{category.upper()} ({len(files)} files):")
            for f in files[:5]:  # Show first 5
                print(f"  - {f}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")

    print(f"\n📄 Full report saved to: {report_path}")

    # Show most concerning unused files (core modules)
    if report["categorized"]["core_modules"]:
        print("\n⚠️  WARNING: Unused files in core modules:")
        for f in report["categorized"]["core_modules"][:10]:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
