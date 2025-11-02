#!/usr/bin/env python3
"""
Standalone TODO/FIXME Categorization utility (extracted from TODO/scripts/categorize_todos.py)

This file is intentionally standalone so we can commit it as a single, reviewable unit
without modifying tracked files that are marked assume-unchanged in some developer
worktrees.

Usage:
  python tools/todo_categorize.py --root . --format md --output TODO_REPORT.md
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from typing import Iterator, List, Optional, Sequence

# --- Config ------------------------------------------------------------------
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env",
    "__pycache__", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache"
}

SCAN_EXTS = {".py", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini"}
PRIORITY_LEVELS: Sequence[str] = ("CRITICAL", "HIGH", "MED", "LOW")

PATTERN = re.compile(r"(?P<kind>TODO|FIXME|BUG)(?:\[(?P<tag>[a-zA-Z0-9_\-]+)\])?\s*:\s*(?P<text>.+)")

@dataclass(frozen=True)
class TODORecord:
    file: str
    line: str
    text: str
    priority: str

    def normalized(self) -> "TODORecord":
        return TODORecord(file=self.file.replace('\\\\', '/'), line=str(self.line), text=self.text.strip(), priority=self.priority)


def normalize_path(path: str | Path) -> str:
    if isinstance(path, Path):
        path_str = path.as_posix()
    else:
        path_str = path.replace("\\", "/")
    while path_str.startswith("./"):
        path_str = path_str[2:]
    return path_str


def _strip_todo_prefix(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^(#\s*)?(TODO|FIXME|BUG)(\[[^\]]+\])?\s*:?(\s*)", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def extract_todo_context(todo_line: str) -> tuple[str, str, str]:
    raw = todo_line.strip()
    if not raw:
        raise ValueError("Empty TODO line")
    file_part, sep, remainder = raw.partition(":")
    if not sep:
        raise ValueError(f"Unable to parse TODO line: {todo_line!r}")
    line_part, sep, text_part = remainder.partition(":")
    if not sep:
        raise ValueError(f"Unable to parse TODO line: {todo_line!r}")
    text = _strip_todo_prefix(text_part)
    return normalize_path(file_part), line_part.strip(), text


def _iter_scannable_files(project_root: Path) -> Iterator[Path]:
    root = project_root.resolve()
    for current_dir, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(current_dir) / name
            if path.suffix.lower() not in SCAN_EXTS:
                continue
            yield path


def scan_repo(root: Path) -> List[TODORecord]:
    items: List[TODORecord] = []
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            m = PATTERN.search(line)
            if not m:
                continue
            kind = m.group("kind")
            content = m.group("text").strip()
            items.append(TODORecord(file=str(p.relative_to(root)), line=str(i), text=content, priority="MED"))
    return items


def emit_md(items: List[TODORecord]) -> str:
    lines = ["# TODO/FIXME Report", "", "## Items", ""]
    for it in items:
        lines.append(f"- `{it.file}:{it.line}` — **{it.text}**")
    return "\n".join(lines) + "\n"


def emit_json(items: List[TODORecord]) -> str:
    return json.dumps({"items": [asdict(it) for it in items]}, indent=2)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Scan and categorize TODO/FIXME/BUG comments.")
    parser.add_argument("--root", default=".", help="Repository root to scan")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--output", default="", help="Write to file; if empty, print to stdout")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    items = scan_repo(root)

    out = emit_md(items) if args.format == "md" else emit_json(items)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
