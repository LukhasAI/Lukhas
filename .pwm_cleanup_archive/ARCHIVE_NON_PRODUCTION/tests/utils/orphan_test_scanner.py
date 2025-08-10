#!/usr/bin/env python3
"""
Orphan Test Scanner
ΛTAG: codex, tests
Scans the repository for test files lacking assertions or containing pass stubs.
Results are appended to docs/audit/ORPHAN_SCAN.md
"""

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_PATTERNS = ["test_*.py", "*_test.py"]


def has_asserts(node: ast.FunctionDef) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Assert):
            return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr.startswith("assert"):
                return True
    return False


def scan_file(path: Path):
    stubs = []
    try:
        content = path.read_text()
        tree = ast.parse(content)
    except SyntaxError as e:
        return [("SYNTAX_ERROR", str(e))]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                stubs.append((node.name, "pass"))
            elif not has_asserts(node):
                stubs.append((node.name, "no_asserts"))
        if isinstance(node, ast.ClassDef):
            for fn in node.body:
                if isinstance(fn, ast.FunctionDef) and fn.name.startswith("test"):
                    if len(fn.body) == 1 and isinstance(fn.body[0], ast.Pass):
                        stubs.append((f"{node.name}.{fn.name}", "pass"))
                    elif not has_asserts(fn):
                        stubs.append((f"{node.name}.{fn.name}", "no_asserts"))
    return stubs


def scan_repo(root: Path):
    files = []
    for pattern in TEST_PATTERNS:
        files.extend(root.rglob(pattern))
    results = {}
    for f in files:
        stubs = scan_file(f)
        if stubs:
            results[str(f.relative_to(root))] = stubs
    return results


def update_report(results):
    report_path = REPO_ROOT / "docs" / "audit" / "ORPHAN_SCAN.md"
    report_lines = ["# Orphan Scan", ""]
    if not results:
        report_lines.append("No orphan or stub tests found.")
    else:
        for file, issues in sorted(results.items()):
            for test_name, reason in issues:
                report_lines.append(f"- `{file}::{test_name}` - {reason}")
    report_path.write_text("\n".join(report_lines))
    print(f"Report written to {report_path}")


def main():
    results = scan_repo(REPO_ROOT)
    update_report(results)


if __name__ == "__main__":
    main()
