"""
Fail PRs that exceed patch-size caps, touch protected files, or add risky exception patterns.
Intended for CI use. Exits nonzero on violation.

Env/Args:
  --base <sha>   Base commit (default: origin/main)
  --head <sha>   Head commit (default: HEAD)
  --protected .lukhas/protected-files.yml
  --max-files 2
  --max-lines 40
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Final

yaml: Any | None
try:
    yaml = importlib.import_module("yaml")
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None

RISKY_EXCEPT_RE = re.compile(r'^\+\s*except(\s+Exception)?\s*:', re.IGNORECASE)

def sh(cmd: str) -> str:
    out = subprocess.check_output(cmd, shell=True, text=True)
    return out.strip()

def list_changed_files(base: str, head: str) -> list[str]:
    return sh(f"git diff --name-only --diff-filter=ACMRT {base}...{head}").splitlines()

def diff_stats(base: str, head: str, paths: Sequence[str]) -> int:
    if not paths:
        return 0
    out = sh(f"git diff --unified=0 {base}...{head} -- " + " ".join(paths))
    added = sum(1 for line in out.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in out.splitlines() if line.startswith("-") and not line.startswith("---"))
    return added + removed

def risky_exception_added(base: str, head: str) -> bool:
    out = sh(f"git diff {base}...{head}")
    return any(RISKY_EXCEPT_RE.search(line) for line in out.splitlines())

def any_protected_touched(changed: list[str], protected_globs: list[str]) -> list[str]:
    from fnmatch import fnmatch
    hit = []
    for f in changed:
        for g in protected_globs:
            if fnmatch(f, g):
                hit.append(f)
    return sorted(set(hit))

DEFAULT_LARGE_IMPORT_WHITELIST: Final[str] = ".lukhas/large-import-whitelist.yml"


def _parse_pattern_lines(text: str) -> list[str]:
    entries: list[str] = []
    include_section = True
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.endswith(":"):
            key = line[:-1].strip()
            include_section = key in {"whitelist", "paths", "files"}
            continue

        if not include_section:
            continue

        item = line[1:].strip() if line.startswith("-") else line

        if item:
            entries.append(item)

    return entries


def load_whitelist(path: str | None) -> set[str]:
    if not path:
        return set()

    wf = Path(path)
    if not wf.exists():
        raise FileNotFoundError(f"Whitelist file not found: {path}")

    text = wf.read_text()
    entries: list[str] = []

    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            data = None
        if isinstance(data, list):
            entries = [str(item).strip() for item in data if str(item).strip()]
        elif isinstance(data, dict):
            for key in ("whitelist", "paths", "files"):
                value = data.get(key)
                if isinstance(value, list):
                    entries = [str(item).strip() for item in value if str(item).strip()]
                    break

    if not entries:
        entries = _parse_pattern_lines(text)

    return set(entries)


def partition_whitelisted(files: Sequence[str], patterns: Iterable[str]) -> tuple[list[str], list[str]]:
    pattern_list = list(patterns)
    if not pattern_list:
        return list(files), []

    kept: list[str] = []
    whitelisted: list[str] = []
    seen: set[str] = set()

    for name in files:
        if any(fnmatch(name, pattern) for pattern in pattern_list):
            if name not in seen:
                whitelisted.append(name)
                seen.add(name)
            continue
        kept.append(name)

    return kept, whitelisted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("BASE_SHA", "origin/main"))
    ap.add_argument("--head", default=os.environ.get("HEAD_SHA", "HEAD"))
    ap.add_argument("--protected", default=".lukhas/protected-files.yml")
    ap.add_argument("--max-files", type=int, default=2)
    ap.add_argument("--max-lines", type=int, default=40)
    ap.add_argument("--whitelist-file", default=None)
    ap.add_argument(
        "--allow-large-imports",
        action="store_true",
        help=(
            "Allow files matching the large import whitelist to bypass patch "
            "caps. The whitelist is loaded from "
            f"{DEFAULT_LARGE_IMPORT_WHITELIST}."
        ),
    )
    args = ap.parse_args()

    changed = list_changed_files(args.base, args.head)
    try:
        whitelist_patterns = load_whitelist(args.whitelist_file)
    except FileNotFoundError as err:
        print(str(err), file=sys.stderr)
        sys.exit(2)

    large_import_patterns: set[str] = set()
    if args.allow_large_imports:
        try:
            large_import_patterns = load_whitelist(DEFAULT_LARGE_IMPORT_WHITELIST)
        except FileNotFoundError:
            print(
                "Large import whitelist not found: "
                f"{DEFAULT_LARGE_IMPORT_WHITELIST}",
                file=sys.stderr,
            )
            sys.exit(2)

    combined_patterns = whitelist_patterns | large_import_patterns
    filtered_changed, whitelisted_files = partition_whitelisted(changed, combined_patterns)

    total_files = len(changed)
    total_lines = diff_stats(args.base, args.head, changed)
    counted_files = len(filtered_changed)
    counted_lines = total_lines if filtered_changed == changed else diff_stats(args.base, args.head, filtered_changed)

    protected: list[str] = []
    pf = Path(args.protected)
    if pf.exists():
        if yaml is not None:
            protected = yaml.safe_load(pf.read_text()) or []
        else:
            protected = _parse_pattern_lines(pf.read_text())

    touched = any_protected_touched(changed, protected)
    risky = risky_exception_added(args.base, args.head)

    large_import_matches = [
        name
        for name in whitelisted_files
        if any(fnmatch(name, pattern) for pattern in large_import_patterns)
    ]

    result = {
        "base": args.base, "head": args.head,
        "changed_files": total_files, "changed_lines": total_lines,
        "counted_files": counted_files, "counted_lines": counted_lines,
        "max_files": args.max_files, "max_lines": args.max_lines,
        "whitelist_file": args.whitelist_file,
        "whitelist_patterns": sorted(combined_patterns),
        "whitelisted_files": whitelisted_files,
        "allow_large_imports": args.allow_large_imports,
        "large_import_whitelist": sorted(large_import_patterns),
        "large_import_whitelisted_files": large_import_matches,
        "protected_hits": touched, "risky_exception_added": risky,
        "status": "ok"
    }

    violations = []
    if counted_files > args.max_files:
        violations.append(f"Changed files (excluding whitelist) {counted_files} > max {args.max_files}")
    if counted_lines > args.max_lines:
        violations.append(f"Changed lines (excluding whitelist) {counted_lines} > max {args.max_lines}")
    if touched:
        violations.append(f"Touched protected paths: {', '.join(touched)}")
    if risky:
        violations.append("Introduced broad 'except' clause (policy forbids).")

    if violations:
        result["status"] = "fail"
        print(json.dumps(result, indent=2))
        print("\nPolicy violations:\n- " + "\n- ".join(violations))
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
