#!/usr/bin/env python3
"""
Add `from __future__ import annotations` to files that use `|` union syntax
and do not already contain that future import.

Safe, idempotent: inserts at top after shebang/docstring. Skip files in release_artifacts and .git.
"""
import re
from pathlib import Path

ROOT = Path(".")
pattern_union = re.compile(r"\b[A-Za-z0-9_]+\s*\|\s*[A-Za-z0-9_]+")  # heuristic for 'A | B'
excluded_paths = ("release_artifacts", ".git", "__pycache__")

def file_uses_union(path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    return bool(pattern_union.search(text))

def has_future_annotations(text):
    return "from __future__ import annotations" in text

def insert_future(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    # skip module docstring
    if len(lines) > insert_at and (lines[insert_at].startswith('"""') or lines[insert_at].startswith("'''")):
        dq = lines[insert_at][:3]
        for i in range(insert_at + 1, len(lines)):
            if lines[i].strip().endswith(dq):
                insert_at = i + 1
                break
    new_lines = lines[:insert_at] + ["from __future__ import annotations", ""] + lines[insert_at:]
    path.write_text("\n".join(new_lines), encoding="utf-8")

def main():
    count = 0
    for p in ROOT.rglob("*.py"):
        s = str(p)
        if any(ex in s for ex in excluded_paths):
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if has_future_annotations(txt):
            continue
        if file_uses_union(p):
            insert_future(p)
            print(f"[ADD FUTURE] {p}")
            count += 1
    print(f"Added future annotations to {count} file(s).")

if __name__ == "__main__":
    main()
