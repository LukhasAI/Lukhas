#!/usr/bin/env python3
"""
Find isolated modules (no imports or no importers).

Scans Python files and identifies:
- "No incoming" - modules that no one imports (possibly unused)
- "No outgoing" - modules that don't import anything (leaf modules)

Excludes: tests/, docs/, __pycache__, fixtures, setup.py
"""
import ast
from collections import defaultdict
from pathlib import Path


def get_imports(file_path: Path) -> set[str]:
    """Extract all import statements from a Python file."""
    try:
        tree = ast.parse(file_path.read_text())
    except Exception:
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])

    return imports


def should_skip(path: Path) -> bool:
    """Check if path should be excluded from analysis."""
    parts = path.parts
    skip_patterns = {
        "tests",
        "docs",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        ".git",
        "fixtures",
    }
    return any(p in skip_patterns or p.startswith(".") for p in parts)


def module_name_from_path(path: Path, root: Path) -> str:
    """Convert file path to Python module name."""
    rel = path.relative_to(root)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    elif parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]

    return ".".join(parts) if parts else ""


def main():
    root = Path(__file__).parent.parent
    python_files = [p for p in root.rglob("*.py") if not should_skip(p) and p.name != "setup.py"]

    # Build import graph
    module_imports = {}  # module -> set of modules it imports
    all_modules = set()

    for py_file in python_files:
        mod_name = module_name_from_path(py_file, root)
        if not mod_name or mod_name.startswith("."):
            continue

        all_modules.add(mod_name)
        imports = get_imports(py_file)
        module_imports[mod_name] = imports

    # Calculate incoming/outgoing counts
    incoming = defaultdict(int)
    outgoing = defaultdict(int)

    for mod, imports in module_imports.items():
        outgoing[mod] = len(imports)
        for imported in imports:
            if imported in all_modules:
                incoming[imported] += 1

    # Find isolated modules
    no_incoming = []
    no_outgoing = []

    for mod in sorted(all_modules):
        if incoming[mod] == 0 and not mod.startswith("serve"):  # serve.main is entrypoint
            no_incoming.append(mod)
        if outgoing[mod] == 0:
            no_outgoing.append(mod)

    # Output results
    print("# Isolated Modules Report\n")
    print(f"**Total modules analyzed**: {len(all_modules)}\n")

    print(f"## No Incoming ({len(no_incoming)})")
    print("*Modules that nothing imports (possibly unused or entrypoints)*\n")
    for mod in no_incoming[:50]:  # Limit to 50
        print(f"- {mod}")
    if len(no_incoming) > 50:
        print(f"\n*... and {len(no_incoming) - 50} more*\n")

    print(f"\n## No Outgoing ({len(no_outgoing)})")
    print("*Modules that import nothing (leaf modules)*\n")
    for mod in no_outgoing[:50]:  # Limit to 50
        print(f"- {mod}")
    if len(no_outgoing) > 50:
        print(f"\n*... and {len(no_outgoing) - 50} more*")


if __name__ == "__main__":
    main()
