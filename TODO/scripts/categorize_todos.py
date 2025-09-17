#!/usr/bin/env python3
"""
TODO/FIXME Categorization (T4 Utility)
======================================

Why this exists:
- Not to pad the repo, but to *triage real work*. We surface TODOs/FIXMEs/BUGs,
  categorize them into stable buckets, and optionally fail CI when the count
  crosses a threshold.

Principles:
- Zero impact on test collection (pure CLI script; no repo imports).
- Deterministic output (stable ordering).
- Useful by itself (Markdown or JSON reports).

Usage:
  python TODO/scripts/categorize_todos.py --format md --output TODO_REPORT.md
  python TODO/scripts/categorize_todos.py --format json --output todo_report.json
  python TODO/scripts/categorize_todos.py --fail-over 250   # non-zero exit if count > 250

Conventions (inline tagging):
  # TODO[contradiction]: resolve paradox in adapter
  # FIXME[clock]: remove busy-wait in tick loop

If no tag is present, we infer category from the file path (e.g., core/, matriz/, memory/, safety/).

Exit codes:
  0 = success
  2 = exceeded fail-over threshold
"""
from __future__ import annotations

__version__ = "1.0.0"  # T4-frozen CLI interface
__all__ = [
    "scan_repo",
    "summarize",
    "emit_md",
    "emit_json",
    "main",
]

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --- Config ------------------------------------------------------------------

# Directories to skip during scan
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env",
    "__pycache__", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache"
}

# File extensions to scan (keep it simple and fast)
SCAN_EXTS = {".py", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini"}

# Recognized inline tags (align with MATRIZ topics & subsystems)
KNOWN_TAGS = {
    # MATRIZ topics
    "contradiction", "resource", "trend", "breakthrough",
    # subsystems
    "clock", "memory", "consciousness", "governance", "identity", "orchestration",
    "router", "guardian", "metrics", "drift", "folds", "adapters"
}

# Path-based fallback categories
PATH_CATEGORIES = [
    ("matriz", "matriz"),
    ("core", "core"),
    ("memory", "memory"),
    ("safety", "safety"),
    ("storage", "storage"),
    ("dashboards", "observability"),
    ("tests", "tests"),
]

# Regex for TODO-like lines with optional [tag]
PATTERN = re.compile(r"""
    (?P<kind>TODO|FIXME|BUG)          # kind
    (?:\[(?P<tag>[a-zA-Z0-9_\-]+)\])? # optional [tag]
    \s*:\s*
    (?P<text>.+)                      # content
""", re.VERBOSE)

# --- Data --------------------------------------------------------------------

@dataclass
class TodoItem:
    path: str
    line: int
    kind: str
    tag: Optional[str]
    text: str
    category: str

# --- Helpers -----------------------------------------------------------------

def is_scannable(path: Path) -> bool:
    if path.is_dir():
        return False
    if path.suffix.lower() not in SCAN_EXTS:
        return False
    parts = set(p.name for p in path.parts)
    return not bool(SKIP_DIRS & parts)

def infer_category(path: Path, tag: Optional[str]) -> str:
    if tag and tag.lower() in KNOWN_TAGS:
        return tag.lower()
    for needle, cat in PATH_CATEGORIES:
        if f"/{needle}/" in f"/{path.as_posix()}/":
            return cat
    return "general"

def scan_repo(root: Path) -> List[TodoItem]:
    items: List[TodoItem] = []
    for p in sorted(root.rglob("*")):
        if not is_scannable(p):
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
            tag = m.group("tag")
            content = m.group("text").strip()
            category = infer_category(p, tag)
            items.append(TodoItem(
                path=str(p.relative_to(root)),
                line=i,
                kind=kind,
                tag=(tag.lower() if tag else None),
                text=content,
                category=category,
            ))
    # Stable order: category, path, line
    items.sort(key=lambda x: (x.category, x.path, x.line))
    return items

def summarize(items: List[TodoItem]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for it in items:
        counts[it.category] = counts.get(it.category, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (kv[0], kv[1])))

# --- Output ------------------------------------------------------------------

def emit_md(items: List[TodoItem]) -> str:
    counts = summarize(items)
    lines = []
    lines.append("# TODO/FIXME Report\n")
    lines.append("## Summary by Category\n")
    for cat, n in counts.items():
        lines.append(f"- **{cat}**: {n}")
    lines.append("\n---\n")
    lines.append("## Items\n")
    for it in items:
        tag = f"[{it.tag}]" if it.tag else ""
        lines.append(f"- `{it.path}:{it.line}` — **{it.kind}{tag}**: {it.text}  _(cat: {it.category})_")
    return "\n".join(lines) + "\n"

def emit_json(items: List[TodoItem]) -> str:
    return json.dumps({
        "summary": summarize(items),
        "items": [asdict(it) for it in items],
    }, indent=2, sort_keys=True)

# --- CLI ---------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Scan and categorize TODO/FIXME/BUG comments.")
    parser.add_argument("--root", default=".", help="Repository root to scan")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    parser.add_argument("--output", default="", help="Write to file; if empty, print to stdout")
    parser.add_argument("--fail-over", dest="fail_over", type=int, default=None,
                        help="If total items exceed this number, exit with code 2")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    items = scan_repo(root)

    out = emit_md(items) if args.format == "md" else emit_json(items)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)

    if args.fail_over is not None and len(items) > args.fail_over:
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
  
# New test file at tests/tools/test_categorize_todos.py

import textwrap
from pathlib import Path
from TODO.scripts.categorize_todos import scan_repo, summarize, emit_md, emit_json

def write(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(s).lstrip(), encoding="utf-8")

def test_scan_and_emit_md(tmp_path: Path):
    # Create a tiny repo snapshot
    write(tmp_path / "core/clock.py", "# TODO[clock]: tighten p95 math\nprint('ok')\n")
    write(tmp_path / "matriz/node.py", "# FIXME[adapters]: unify shim\n")
    write(tmp_path / "README.md", "Some doc\n# TODO: document drift config\n")

    items = scan_repo(tmp_path)
    # We expect three items with stable sorting by (category, path, line)
    assert len(items) == 3
    cats = [it.category for it in items]
    assert set(cats) >= {"core", "matriz", "general"}  # path fallback + tagged

    out = emit_md(items)
    assert "# TODO/FIXME Report" in out
    assert "## Summary by Category" in out
    # Every item should be rendered as a bullet line with path:line
    for it in items:
        assert f"`{it.path}:{it.line}`" in out

def test_scan_and_emit_json(tmp_path: Path):
    write(tmp_path / "safety/policy.py", "# BUG[governance]: missing check\n")
    items = scan_repo(tmp_path)
    js = emit_json(items)
    assert '"summary"' in js and '"items"' in js
    # Ensure we included the category and kind in JSON
    assert '"category"' in js and '"kind"' in js