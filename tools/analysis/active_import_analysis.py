#!/usr/bin/env python3
"""
🔍  Active Import Analysis Tool
=================================
Identifies import errors in the active LUKHAS  codebase (excluding archives).
"""

import ast
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ActiveImportAnalyzer:
    """Analyzes Python imports in active code only"""

    # Directories to exclude from analysis
    EXCLUDE_DIRS = {
        "._cleanup_archive",
        "archive",
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
    }

    # Active module directories
    ACTIVE_MODULES = {
        "api",
        "architectures",
        "bio",
        "bridge",
        "consciousness",
        "core",
        "creativity",
        "/Users/agi_dev/LOCAL-REPOS/Lukhas/deployment/platforms",
        "docs",
        "emotion",
        "ethics",
        "examples",
        "governance",
        "identity",
        "infra",
        "integration",
        "memory",
        "meta",
        "orchestration",
        "quantum",
        "reasoning",
        "recovery",
        "security",
        "tests",
        "tools",
        "trace",
        "unified",
        "vivox",
    }

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.import_errors: list[dict] = []
        self.import_graph: dict[str, set[str]] = defaultdict(set)
        self.missing_modules: set[str] = set()
        self.files_analyzed = 0

    def should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        # Check if in excluded directory
        for part in file_path.parts:
            if part in self.EXCLUDE_DIRS:
                return False

        # Check if in active module
        rel_path = file_path.relative_to(self.root_path)
        if rel_path.parts and rel_path.parts[0] not in self.ACTIVE_MODULES:
            # Allow root-level Python files
            if len(rel_path.parts) > 1:
                return False

        return True

    def analyze_file(self, file_path: Path) -> None:
        """Analyze imports in a single Python file"""
        if not self.should_analyze_file(file_path):
            return

        self.files_analyzed += 1

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.import_errors.append(
                    {
                        "file": str(file_path.relative_to(self.root_path)),
                        "error": f"Syntax error: {e}",
                        "line": e.lineno,
                        "type": "syntax",
                    }
                )
                return

            # Extract imports
            module_name = self._path_to_module(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import(file_path, alias.name, node.lineno, "absolute")
                        self.import_graph[module_name].add(alias.name)

                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.level == 0:  # Absolute import
                        module = node.module
                        import_type = "absolute"
                    else:  # Relative import
                        module = self._resolve_relative_import(file_path, node.module, node.level)
                        import_type = "relative"

                    self._check_import(file_path, module, node.lineno, import_type)
                    self.import_graph[module_name].add(module)

        except Exception as e:
            self.import_errors.append(
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "error": f"Failed to analyze: {e}",
                    "line": 0,
                    "type": "analysis_error",
                }
            )

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        rel_path = file_path.relative_to(self.root_path)
        parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        return ".".join(parts)

    def _resolve_relative_import(self, file_path: Path, module: Optional[str], level: int) -> str:
        """Resolve relative import to absolute module name"""
        current_parts = self._path_to_module(file_path).split(".")

        # Go up 'level' directories
        if level > len(current_parts):
            return module or ""

        base_parts = current_parts[:-level]

        if module:
            return ".".join(base_parts + module.split("."))
        else:
            return ".".join(base_parts)

    def _check_import(
        self, file_path: Path, module_name: str, line_no: int, import_type: str
    ) -> None:
        """Check if an import is valid"""
        # Skip built-in modules
        if module_name in sys.builtin_module_names:
            return

        # Check if it's a standard library module
        if self._is_stdlib_module(module_name):
            return

        # Check if it's an installed package
        if self._is_installed_package(module_name):
            return

        # Check if it's a local module
        if self._is_local_module(module_name):
            return

        # Import not found
        self.import_errors.append(
            {
                "file": str(file_path.relative_to(self.root_path)),
                "error": f"Cannot import '{module_name}'",
                "line": line_no,
                "module": module_name,
                "type": "missing_import",
                "import_type": import_type,
            }
        )
        self.missing_modules.add(module_name)

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Check if module is in standard library"""
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "time",
            "datetime",
            "random",
            "math",
            "collections",
            "itertools",
            "functools",
            "typing",
            "enum",
            "pathlib",
            "asyncio",
            "logging",
            "unittest",
            "abc",
            "re",
            "hashlib",
            "pickle",
            "tempfile",
            "shutil",
            "subprocess",
            "io",
            "threading",
            "queue",
            "copy",
            "warnings",
            "inspect",
            "contextlib",
            "dataclasses",
            "secrets",
            "uuid",
            "base64",
            "urllib",
            "http",
            "email",
            "mimetypes",
            "socketserver",
        }

        # Check top-level module
        top_module = module_name.split(".")[0]
        return top_module in stdlib_modules

    def _is_installed_package(self, module_name: str) -> bool:
        """Check if module is an installed package"""
        # Common packages we expect
        known_packages = {
            "numpy",
            "pandas",
            "scipy",
            "sklearn",
            "torch",
            "tensorflow",
            "flask",
            "fastapi",
            "uvicorn",
            "pydantic",
            "sqlalchemy",
            "pytest",
            "black",
            "flake8",
            "mypy",
            "aiofiles",
            "aiohttp",
            "requests",
            "matplotlib",
            "seaborn",
            "plotly",
            "streamlit",
            "openai",
            "transformers",
            "langchain",
            "pinecone",
            "redis",
        }

        top_module = module_name.split(".")[0]
        if top_module in known_packages:
            return True

        try:
            spec = importlib.util.find_spec(top_module)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def _is_local_module(self, module_name: str) -> bool:
        """Check if module exists locally in the project"""
        # Convert module name to potential file paths
        parts = module_name.split(".")

        # Check as package (__init__.py)
        package_path = self.root_path / Path(*parts) / "__init__.py"
        if package_path.exists():
            return True

        # Check as module (.py file)
        if parts:
            module_path = self.root_path / Path(*parts[:-1]) / f"{parts[-1]}.py"
            if module_path.exists():
                return True

        return False

    def analyze_directory(self, directory: Path) -> None:
        """Analyze all Python files in directory"""
        for py_file in directory.rglob("*.py"):
            self.analyze_file(py_file)

    def generate_report(self) -> dict:
        """Generate analysis report"""
        # Group errors by type
        errors_by_type = defaultdict(list)
        for error in self.import_errors:
            errors_by_type[error["type"]].append(error)

        # Group missing imports by module
        missing_by_module = defaultdict(list)
        for error in errors_by_type["missing_import"]:
            missing_by_module[error["module"]].append(
                {"file": error["file"], "line": error["line"]}
            )

        # Identify common missing patterns
        common_patterns = self._identify_common_patterns()

        return {
            "total_errors": len(self.import_errors),
            "files_analyzed": self.files_analyzed,
            "errors_by_type": dict(errors_by_type),
            "missing_modules": sorted(self.missing_modules),
            "missing_by_module": dict(missing_by_module),
            "common_patterns": common_patterns,
        }

    def _identify_common_patterns(self) -> dict[str, list[str]]:
        """Identify common patterns in missing imports"""
        patterns = {
            "moved_modules": [],
            "typos": [],
            "missing_init": [],
            "external_deps": [],
        }

        for module in self.missing_modules:
            # Check for common moved/renamed modules
            if module.startswith("lukhas."):
                patterns["moved_modules"].append(module)
            # Check for likely typos
            elif any(module.startswith(m + ".") for m in self.ACTIVE_MODULES):
                patterns["typos"].append(module)
            # Check for missing __init__.py
            elif "." in module and module.split(".")[0] in self.ACTIVE_MODULES:
                patterns["missing_init"].append(module)
            # External dependencies
            else:
                patterns["external_deps"].append(module)

        return patterns


def generate_fixes(report: dict) -> list[str]:
    """Generate fix suggestions based on report"""
    fixes = []

    # Fix syntax errors first
    if report["errors_by_type"].get("syntax"):
        fixes.append("# Fix syntax errors:")
        for error in report["errors_by_type"]["syntax"][:5]:
            fixes.append(f"  - {error['file']}:{error['line']}")

    # Fix missing __init__.py files
    init_needed = set()
    for module in report["common_patterns"]["missing_init"]:
        parts = module.split(".")
        for i in range(1, len(parts)):
            package = "/".join(parts[:i])
            init_needed.add(package)

    if init_needed:
        fixes.append("\n# Create missing __init__.py files:")
        for package in sorted(init_needed)[:10]:
            fixes.append(f"  touch {package}/__init__.py")

    # Fix moved modules
    if report["common_patterns"]["moved_modules"]:
        fixes.append("\n# Update import statements for moved modules:")
        for module in report["common_patterns"]["moved_modules"][:5]:
            if module.startswith("lukhas."):
                new_module = module.replace("lukhas.", "")
                fixes.append(f"  {module} → {new_module}")

    # Install missing external dependencies
    if report["common_patterns"]["external_deps"]:
        fixes.append("\n# Install missing external dependencies:")
        unique_deps = {m.split(".")[0] for m in report["common_patterns"]["external_deps"]}
        for dep in sorted(unique_deps)[:10]:
            fixes.append(f"  pip install {dep}")

    return fixes


def main():
    """Main analysis function"""
    print("🔍  Active Import Analysis")
    print("=" * 60)

    analyzer = ActiveImportAnalyzer(PROJECT_ROOT)

    # Analyze all Python files
    print("\n📂 Analyzing active Python files...")
    analyzer.analyze_directory(PROJECT_ROOT)

    # Generate report
    report = analyzer.generate_report()

    # Display results
    print("\n📊 Analysis Results:")
    print(f"   Files analyzed: {report['files_analyzed']}")
    print(f"   Total import errors: {report['total_errors']}")

    # Show errors by type
    for error_type, errors in report["errors_by_type"].items():
        if errors:
            print(f"\n❌ {error_type.replace('_', ' ').title()} ({len(errors)}):")
            for error in errors[:5]:
                print(f"   • {error['file']}:{error['line']} - {error['error']}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")

    # Show common patterns
    print("\n📋 Common Patterns:")
    for pattern, modules in report["common_patterns"].items():
        if modules:
            print(f"   {pattern.replace('_', ' ').title()}: {len(modules)}")

    # Generate and show fixes
    fixes = generate_fixes(report)
    if fixes:
        print("\n💡 Suggested Fixes:")
        print("\n".join(fixes))

    # Save detailed report
    import json

    report_path = (
        PROJECT_ROOT / "docs" / "reports" / "analysis" / "_ACTIVE_IMPORT_ANALYSIS_REPORT.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {report_path.relative_to(PROJECT_ROOT)}")

    return report["total_errors"]


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
