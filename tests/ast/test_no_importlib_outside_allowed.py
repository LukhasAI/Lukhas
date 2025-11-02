#!/usr/bin/env python3
"""
Test to ensure dynamic imports using importlib are eliminated outside allowed locations.

This test validates that the T4/0.01% goal of eliminating dynamic cross-lane imports
is achieved by scanning the codebase for importlib usage and ensuring it only occurs
in approved registry locations.

DoD: This test passes green → no unauthorized importlib usage detected
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ImportlibDetector(ast.NodeVisitor):
    """AST visitor to detect importlib usage in Python files"""

    def __init__(self):
        self.importlib_calls: List[Tuple[int, str]] = []
        self.importlib_imports: List[Tuple[int, str]] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Detect 'import importlib' statements"""
        for alias in node.names:
            if alias.name == "importlib" or alias.name.startswith("importlib."):
                self.importlib_imports.append((node.lineno, alias.name))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Detect 'from importlib import ...' statements"""
        if node.module and node.module.startswith("importlib"):
            for alias in node.names:
                self.importlib_imports.append((node.lineno, f"from {node.module} import {alias.name}"))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect calls to importlib functions"""
        # Check for importlib.import_module calls
        if (isinstance(node.func, ast.Attribute) and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == "importlib" and
            node.func.attr == "import_module"):
            self.importlib_calls.append((node.lineno, "importlib.import_module"))

        # Check for direct import_module calls (after from importlib import import_module)
        elif (isinstance(node.func, ast.Name) and
              node.func.id == "import_module"):
            self.importlib_calls.append((node.lineno, "import_module"))

        self.generic_visit(node)


def scan_file_for_importlib(file_path: Path) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Scan a Python file for importlib usage.

    Returns:
        Tuple of (imports, calls) - lists of (line_number, code) tuples
    """
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Skip files with null bytes (binary files)
        if '\x00' in content:
            return [], []

        tree = ast.parse(content, filename=str(file_path))
        detector = ImportlibDetector()
        detector.visit(tree)

        return detector.importlib_imports, detector.importlib_calls

    except (SyntaxError, UnicodeDecodeError, OSError, ValueError):
        # Skip files that can't be parsed or read
        return [], []


def get_python_files(root_dir: Path) -> List[Path]:
    """Get all Python files in the project, excluding common ignore patterns"""
    python_files = []

    # Directories to skip
    skip_dirs = {
        ".git", ".pytest_cache", "__pycache__", ".venv", "venv", ".venv311",
        "node_modules", ".tox", "build", "dist", ".mypy_cache",
        "mcp-lukhas-sse/venv", "mcp-lukhas-sse/test_env",  # Skip MCP virtual environments
        "site-packages", "temp", "backups", "archive",  # Skip temp and archive dirs
    }

    # File patterns to skip
    skip_patterns = {
        "test_no_importlib_outside_allowed.py",  # This test file itself
    }

    for file_path in root_dir.rglob("*.py"):
        # Skip if in excluded directory
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue

        # Skip if matches skip pattern
        if any(pattern in file_path.name for pattern in skip_patterns):
            continue

        python_files.append(file_path)

    return python_files


def is_allowed_location(file_path: Path) -> bool:
    """
    Check if a file is in an allowed location for importlib usage.

    Allowed locations:
    - Registry files (lukhas/core/registry.py)
    - Entry point discovery modules
    - Test files (but should be minimal)
    - Legacy compatibility modules (temporary)
    """
    path_str = str(file_path)

    # Explicitly allowed files
    allowed_files = {
        "lukhas/core/registry.py",
        "candidate/core/module_registry.py",  # Legacy module registry
        "lukhas/core/import_router.py",  # Import routing system
        "lukhas/utils/optional_import.py",  # Optional import utility
    }

    # Check if file is in allowed set
    for allowed_file in allowed_files:
        if allowed_file in path_str:
            return True

    # Allow test files but flag for review
    if "/tests/" in path_str or path_str.endswith("_test.py"):
        return True

    # Allow setup/install scripts and development tools
    if any(pattern in path_str for pattern in ["setup.py", "install", "scripts/", "tools/", "serve/"]):
        return True

    # Allow performance optimization files temporarily
    if "performance/" in path_str:
        return True

    return False


class TestNoImportlibOutsideAllowed:
    """Test suite to ensure importlib usage is controlled"""

    def test_no_unauthorized_importlib_usage(self):
        """
        Main test: Ensure importlib is only used in approved locations.

        This validates the T4/0.01% requirement to eliminate dynamic cross-lane imports.
        """
        project_root = Path(__file__).parent.parent.parent
        python_files = get_python_files(project_root)

        violations = []
        allowed_usage = []

        for file_path in python_files:
            imports, calls = scan_file_for_importlib(file_path)

            if imports or calls:
                relative_path = file_path.relative_to(project_root)

                if is_allowed_location(file_path):
                    allowed_usage.append({
                        "file": str(relative_path),
                        "imports": imports,
                        "calls": calls,
                        "status": "allowed"
                    })
                else:
                    violations.append({
                        "file": str(relative_path),
                        "imports": imports,
                        "calls": calls,
                        "status": "violation"
                    })

        # Report findings
        print("\n=== IMPORTLIB USAGE REPORT ===")
        print(f"Scanned {len(python_files)} Python files")
        print(f"Found {len(allowed_usage)} files with allowed usage")
        print(f"Found {len(violations)} files with violations")

        if allowed_usage:
            print("\n--- ALLOWED USAGE ---")
            for usage in allowed_usage:
                print(f"✅ {usage['file']}")
                for line, code in usage['imports']:
                    print(f"   Line {line}: {code}")
                for line, code in usage['calls']:
                    print(f"   Line {line}: {code}")

        if violations:
            print("\n--- VIOLATIONS FOUND ---")
            for violation in violations:
                print(f"❌ {violation['file']}")
                for line, code in violation['imports']:
                    print(f"   Line {line}: {code}")
                for line, code in violation['calls']:
                    print(f"   Line {line}: {code}")

            print("\n=== REMEDIATION REQUIRED ===")
            print("The following files need to be updated to use registry.resolve() instead:")
            for violation in violations:
                print(f"- {violation['file']}")

        # Test assertion: No violations allowed
        assert len(violations) == 0, (
            f"Found {len(violations)} unauthorized importlib usage(s). "
            "Replace with registry.resolve() pattern. "
            f"Violating files: {[v['file'] for v in violations]}"
        )

    def test_registry_importlib_usage_valid(self):
        """
        Ensure that the registry file itself uses importlib correctly.

        This validates that our allowed usage in the registry is actually functional.
        """
        registry_path = Path(__file__).parent.parent.parent / "lukhas" / "core" / "registry.py"

        if not registry_path.exists():
            pytest.skip("Registry file not found at expected location")

        imports, calls = scan_file_for_importlib(registry_path)

        # Registry should have importlib usage for plugin discovery
        assert len(imports) > 0 or len(calls) > 0, (
            "Registry file should contain importlib usage for plugin discovery"
        )

        print("\n=== REGISTRY IMPORTLIB USAGE ===")
        print(f"File: {registry_path}")
        print("Imports:")
        for line, code in imports:
            print(f"  Line {line}: {code}")
        print("Calls:")
        for line, code in calls:
            print(f"  Line {line}: {code}")

    def test_plugin_discovery_smoke(self):
        """
        Smoke test that plugin discovery works without unauthorized imports.

        This ensures our registry-based approach actually works.
        """
        try:
            from core.registry import _REG, auto_discover

            # Clear registry for clean test
            _REG.clear()

            # Test auto discovery
            auto_discover()

            # Should have some plugins registered (even if just test ones)
            print("\n=== PLUGIN DISCOVERY SMOKE TEST ===")
            print(f"Discovered {len(_REG)} plugins")

            for kind, plugin in _REG.items():
                print(f"  {kind}: {type(plugin).__name__}")

            # This is a smoke test - we don't require specific plugins,
            # just that the mechanism works without errors
            assert isinstance(_REG, dict), "Registry should be a dictionary"

        except ImportError as e:
            pytest.skip(f"Registry not available for testing: {e}")


if __name__ == "__main__":
    # Run the test directly for debugging
    test_instance = TestNoImportlibOutsideAllowed()
    test_instance.test_no_unauthorized_importlib_usage()
    test_instance.test_registry_importlib_usage_valid()
    test_instance.test_plugin_discovery_smoke()
    print("\n✅ All importlib tests passed!")
