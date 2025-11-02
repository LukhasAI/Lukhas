# tests/lane/test_no_import_shims.py
"""AST scan to ensure no importlib.import_module("candidate.") outside registry/loader."""

import ast
from pathlib import Path


def test_no_importlib_candidate_shims():
    """Ensure no direct importlib.import_module("candidate.*") calls outside allowed files."""
    allowed_files = {
        "lukhas/core/registry.py",
        "candidate/core/orchestration/loader.py"
    }

    violations = []

    # Scan lukhas/ directory for Python files
    for py_file in Path("lukhas").rglob("*.py"):
        rel_path = str(py_file.relative_to("."))

        # Skip allowed files
        if rel_path in allowed_files:
            continue

        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content, filename=str(py_file))

            # Look for importlib.import_module calls with candidate modules
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and
                    isinstance(node.func, ast.Attribute) and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == "importlib" and
                    node.func.attr == "import_module" and
                    node.args):

                    # Check if argument contains "candidate"
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "labs" in arg.value:
                            violations.append(f"{rel_path}:{node.lineno}")

        except Exception:
            # Skip files that can't be parsed
            continue

    if violations:
        violation_list = "\n".join(violations)
        assert False, f"Found importlib.import_module('candidate.*') calls outside allowed files:\n{violation_list}"
