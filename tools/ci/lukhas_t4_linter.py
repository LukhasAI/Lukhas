#!/usr/bin/env python3
"""
LUKHAS T4 Architectural Linter
================================

Extends T4 Lint Platform with LUKHAS-specific architectural rules:
- LUKHAS001: Trinity Framework import boundary violations
- LUKHAS003: TODO/FIXME comments requiring task queueing

Integrates with T4 annotation system using TODO[T4-LINT-ISSUE] format.

Usage:
    # Annotate violations
    python3 tools/ci/lukhas_t4_linter.py --paths candidate lukhas core --dry-run

    # Auto-annotate with owner/ticket
    python3 tools/ci/lukhas_t4_linter.py --paths candidate --owner jules --ticket LUKHAS-42

    # CI integration
    python3 tools/ci/lukhas_t4_linter.py --strict

Design:
- Uses AST parsing for LUKHAS001 (Trinity violations)
- Uses regex for LUKHAS003 (TODO comments)
- Outputs T4-compatible inline annotations
- Logs to Intent Registry (reports/todos/lint_issues.jsonl)
- Compatible with T4 autofix workflows
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "reports" / "todos" / "lint_issues.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)

TODO_TAG = "TODO[T4-LINT-ISSUE]"
INLINE_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}\s*:\s*(\{{.*\}})\s*$")


def iso_now():
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_id() -> str:
    """Generate unique T4 lint issue ID."""
    return f"t4-lukhas-{uuid.uuid4().hex[:8]}"


class LUKHAS001Checker(ast.NodeVisitor):
    """
    Check LUKHAS001: Trinity Framework import boundary violations.

    Trinity lanes:
    - candidate/ → CAN import: core/, matriz/, universal_language/
    - candidate/ → CANNOT import: lukhas/ (production)
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[dict] = []
        self.in_candidate_lane = "candidate/" in str(file_path)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self._check_import(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self._check_import(node.module, node.lineno)
        self.generic_visit(node)

    def _check_import(self, module_name: str, line: int):
        """Check if import violates Trinity Framework boundaries."""
        if not self.in_candidate_lane:
            return

        # LUKHAS001: candidate/ → lukhas/ import (FORBIDDEN)
        if module_name.startswith("lukhas.") or module_name == "lukhas":
            self.violations.append({
                "file": self.file_path,
                "line": line,
                "code": "LUKHAS001",
                "message": f"Trinity Framework violation: candidate/ cannot import from {module_name}",
                "suggestion": f"Move {module_name} code to core/ or use registry pattern for dynamic loading"
            })


def check_lukhas001(file_path: Path) -> list[dict]:
    """
    Check file for LUKHAS001 violations.

    Returns:
        List of violation dicts with file, line, code, message, suggestion
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content, filename=str(file_path))
        checker = LUKHAS001Checker(file_path)
        checker.visit(tree)
        return checker.violations
    except SyntaxError:
        # File has syntax errors - skip (will be caught by other linters)
        return []
    except Exception as e:
        print(f"Error checking {file_path}: {e}", file=sys.stderr)
        return []


def check_lukhas003(file_path: Path) -> list[dict]:
    """
    Check LUKHAS003: TODO/FIXME comments in production code.

    Returns:
        List of violation dicts
    """
    # Only flag TODOs in production code (not tests, scripts, etc.)
    path_str = str(file_path)
    skip_patterns = [
        "/tests/", "/test_", "/docs/", "/scripts/", "/examples/",
        "/.venv/", "/venv/", "__pycache__", ".pyc", "/archive/", "/quarantine/"
    ]

    if any(pattern in path_str for pattern in skip_patterns):
        return []

    todo_pattern = re.compile(
        r'#\s*(TODO|FIXME|HACK|XXX)\s*:?\s*(.+)',
        re.IGNORECASE
    )

    violations = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Skip if already has T4-LINT-ISSUE annotation
            if INLINE_RE.search(line):
                continue

            match = todo_pattern.search(line)
            if match:
                keyword = match.group(1)
                description = match.group(2).strip()

                violations.append({
                    "file": file_path,
                    "line": line_num,
                    "code": "LUKHAS003",
                    "message": f"{keyword} comment should be tracked: {description[:80]}",
                    "suggestion": "Convert to T4-LINT-ISSUE annotation or create GitHub issue"
                })

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)

    return violations


def annotate_line(text: str, line_no: int, payload: dict) -> tuple[str, bool]:
    """
    Add T4-LINT-ISSUE annotation to a specific line.

    Returns:
        (new_text, was_modified)
    """
    lines = text.splitlines()
    idx = line_no - 1

    if idx < 0 or idx >= len(lines):
        return text, False

    line = lines[idx]

    # Skip if already annotated
    if INLINE_RE.search(line):
        return text, False

    # Create compact JSON annotation
    json_compact = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    lines[idx] = f"{line}  # {TODO_TAG}: {json_compact}"

    new_text = "\n".join(lines)
    if not text.endswith("\n"):
        new_text += "\n"

    return new_text, True


def lint_file(file_path: Path) -> list[dict]:
    """
    Lint single file for all LUKHAS architectural violations.

    Returns:
        List of violations found
    """
    violations = []

    # Check LUKHAS001 (Trinity Framework imports)
    violations.extend(check_lukhas001(file_path))

    # Check LUKHAS003 (TODO comments)
    violations.extend(check_lukhas003(file_path))

    return violations


def lint_directory(directory: Path) -> list[dict]:
    """
    Recursively lint all Python files in directory.

    Returns:
        List of all violations found
    """
    violations = []

    exclude_patterns = [
        ".venv", "venv", "__pycache__", ".pytest_cache",
        "node_modules", ".git", "dist", "build", "*.egg-info",
        "archive", "quarantine"
    ]

    for py_file in directory.rglob("*.py"):
        # Skip excluded paths
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        file_violations = lint_file(py_file)
        violations.extend(file_violations)

    return violations


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LUKHAS T4 Architectural Linter"
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["candidate", "lukhas", "core", "bridge"],
        help="Directories to lint"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be annotated without modifying files"
    )
    parser.add_argument(
        "--owner",
        default=None,
        help="Owner for T4 annotations (default: None = reserved)"
    )
    parser.add_argument(
        "--ticket",
        default=None,
        help="Ticket/issue number for T4 annotations"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if violations found (CI mode)"
    )

    args = parser.parse_args()

    # Resolve paths
    roots = []
    for p in args.paths:
        rp = (REPO / p).resolve()
        if rp.exists():
            roots.append(rp)

    if not roots:
        print("No valid paths found. Exiting.")
        sys.exit(0)

    # Collect all violations
    all_violations = []
    for root in roots:
        if root.is_file():
            all_violations.extend(lint_file(root))
        elif root.is_dir():
            all_violations.extend(lint_directory(root))

    if not all_violations:
        print("✅ No LUKHAS architectural violations found")
        sys.exit(0)

    # Group by severity
    errors = [v for v in all_violations if v["code"] == "LUKHAS001"]
    warnings = [v for v in all_violations if v["code"] == "LUKHAS003"]

    print("\n🛡️ LUKHAS T4 Architectural Linter Results")
    print("=" * 60)

    # Annotate violations
    edits = 0
    new_entries = []

    for v in all_violations:
        file_path = v["file"]
        line = v["line"]

        # Build T4 annotation payload
        payload = {
            "id": make_id(),
            "code": v["code"],
            "reason": v["message"],
            "suggestion": v.get("suggestion"),
            "owner": args.owner,
            "ticket": args.ticket,
            "status": "planned" if (args.owner and args.ticket) else "reserved",
            "created_at": iso_now()
        }

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            new_text, changed = annotate_line(text, line, payload)

            if changed:
                if args.dry_run:
                    print(f"[DRY] {file_path}:{line} - {v['code']} - {v['message']}")
                else:
                    file_path.write_text(new_text, encoding="utf-8")
                    print(f"✏️  {file_path.relative_to(REPO)}:{line} - {v['code']}")

                edits += 1
                new_entries.append({
                    "id": payload["id"],
                    "file": str(file_path.relative_to(REPO)),
                    "line": line,
                    "code": payload["code"],
                    "reason": payload["reason"],
                    "status": payload["status"],
                    "created_at": payload["created_at"]
                })

        except Exception as e:
            print(f"Error annotating {file_path}:{line} - {e}", file=sys.stderr)

    # Log to Intent Registry
    if not args.dry_run and new_entries:
        with LOG.open("a", encoding="utf-8") as fh:
            for e in new_entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(f"\n{'=' * 60}")
    print(f"Total: {len(errors)} LUKHAS001 errors, {len(warnings)} LUKHAS003 warnings")
    print(f"Annotations created: {edits}")

    if errors:
        print("\n❌ CRITICAL architectural violations detected!")
        print(f"   {len(errors)} Trinity Framework import boundary violations")

        if args.strict:
            sys.exit(1)

    if warnings:
        print(f"\n⚠️  {len(warnings)} TODO comments flagged for tracking")


if __name__ == "__main__":
    main()
