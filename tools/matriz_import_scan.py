#!/usr/bin/env python3
"""
MATRIZ Import Scanner

Analyzes Python import patterns to detect problematic imports and circular dependencies.
Focuses on detecting bad root patterns and module boundary violations.
"""

import argparse
import ast
import json
import pathlib
import sys
from collections import defaultdict
from typing import Any, Dict, List, Set


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""

    def __init__(self, module_path: str):
        self.module_path = module_path
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(
                {"type": "import", "module": alias.name, "name": alias.asname or alias.name, "line": node.lineno}
            )

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append(
                    {
                        "type": "from",
                        "module": node.module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "level": node.level,
                    }
                )


def extract_imports_from_file(file_path: pathlib.Path) -> List[Dict[str, Any]]:
    """Extract import statements from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        visitor = ImportVisitor(str(file_path))
        visitor.visit(tree)
        return visitor.imports

    except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
        return []


def find_python_files(root_path: pathlib.Path) -> List[pathlib.Path]:
    """Find all Python files in the codebase."""
    python_files = []

    # Key directories to scan
    scan_dirs = [
        root_path / "lukhas",
        root_path / "memory",
        root_path / "core",
        root_path / "bio",
        root_path / "branding",
        root_path / "labs",
        root_path / "governance",
        root_path / "identity",
        root_path / "api",
        root_path / "tools",
        root_path / "tests",
    ]

    for scan_dir in scan_dirs:
        if scan_dir.exists():
            python_files.extend(scan_dir.rglob("*.py"))

    return python_files


def detect_bad_root_imports(imports: List[Dict[str, Any]], file_path: str) -> List[Dict[str, Any]]:
    """Detect problematic root import patterns."""
    bad_imports = []

    for imp in imports:
        module = imp.get("module", "")

        # Bad patterns
        bad_patterns = ["lukhas.", "accepted.", "lukhas", "accepted"]

        for pattern in bad_patterns:
            if module.startswith(pattern):
                bad_imports.append(
                    {
                        "file": file_path,
                        "line": imp.get("line", 0),
                        "import_type": imp.get("type", "unknown"),
                        "module": module,
                        "pattern": pattern,
                        "issue": "bad_root_pattern",
                    }
                )

    return bad_imports


def build_dependency_graph(imports_by_file: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Set[str]]:
    """Build module dependency graph."""
    graph = defaultdict(set)

    for file_path, imports in imports_by_file.items():
        # Convert file path to module name
        if "/lukhas/" in file_path:
            # Convert path like lukhas/module/submodule.py to module.submodule
            parts = file_path.split("/lukhas/")[-1]
            if parts.endswith(".py"):
                parts = parts[:-3]
            current_module = "lukhas." + parts.replace("/", ".")
        else:
            current_module = file_path

        for imp in imports:
            module = imp.get("module", "")
            if module.startswith("lukhas."):
                graph[current_module].add(module)

    return graph


def detect_circular_imports(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detect circular import dependencies using DFS."""
    visited = set()
    rec_stack = set()
    cycles = []

    def dfs(node, path):
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return

        if node in visited:
            return

        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, set()):
            dfs(neighbor, path + [node])

        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles


def analyze_imports(root_path: pathlib.Path) -> Dict[str, Any]:
    """Perform comprehensive import analysis."""
    python_files = find_python_files(root_path)

    # Extract imports from all files
    imports_by_file = {}
    all_bad_imports = []

    for file_path in python_files:
        relative_path = str(file_path.relative_to(root_path))
        imports = extract_imports_from_file(file_path)
        imports_by_file[relative_path] = imports

        # Detect bad imports
        bad_imports = detect_bad_root_imports(imports, relative_path)
        all_bad_imports.extend(bad_imports)

    # Build dependency graph and detect cycles
    dependency_graph = build_dependency_graph(imports_by_file)
    circular_imports = detect_circular_imports(dependency_graph)

    # Summary statistics
    total_files = len(python_files)
    files_with_bad_imports = len(set(imp["file"] for imp in all_bad_imports))
    total_bad_imports = len(all_bad_imports)

    return {
        "timestamp": "2025-09-27T13:12:00Z",
        "summary": {
            "total_python_files": total_files,
            "files_with_bad_imports": files_with_bad_imports,
            "total_bad_imports": total_bad_imports,
            "circular_import_chains": len(circular_imports),
        },
        "bad_imports": all_bad_imports,
        "circular_imports": circular_imports,
        "dependency_graph": {k: list(v) for k, v in dependency_graph.items()},
        "files_scanned": len(imports_by_file),
    }


def main():
    parser = argparse.ArgumentParser(description="Scan for problematic import patterns")
    parser.add_argument("--root", default=".", help="Root directory to scan (default: current directory)")
    parser.add_argument("--output", default="artifacts/matriz_imports.json", help="Output file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    root_path = pathlib.Path(args.root).resolve()
    output_path = pathlib.Path(args.output)

    if args.verbose:
        print(f"Scanning imports in: {root_path}")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Analyze imports
    results = analyze_imports(root_path)

    # Write output
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    if args.verbose:
        print("Import analysis complete:")
        print(f"  Python files scanned: {results['summary']['total_python_files']}")
        print(f"  Bad import patterns: {results['summary']['total_bad_imports']}")
        print(f"  Files with issues: {results['summary']['files_with_bad_imports']}")
        print(f"  Circular import chains: {results['summary']['circular_import_chains']}")
        print(f"  Output written to: {output_path}")

        if results["bad_imports"]:
            print("\nTop 5 bad imports:")
            for imp in results["bad_imports"][:5]:
                print(f"  {imp['file']}:{imp['line']} - {imp['module']} ({imp['pattern']})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
