#!/usr/bin/env python3
"""
Safe, data-driven codemod to migrate tests from lukhas.* to canonical imports.
Uses ledger plurality voting to rewrite only proven-reliable imports.
Supports dry-run (default) and --apply mode with backups.
"""
import argparse
import json
import re
import shutil
from pathlib import Path
from collections import defaultdict, Counter

LEDGER = Path("artifacts/lukhas_import_ledger.ndjson")

IMPORT_RE = re.compile(
    r'^(?P<indent>\s*)(from\s+|import\s+)(?P<mod>lukhas(?:\.[A-Za-z0-9_]+)+)',
    re.MULTILINE
)

def build_mapping(threshold=3):
    if not LEDGER.exists():
        raise SystemExit("ledger missing; run tests to populate.")
    votes = defaultdict(Counter)  # lukhas.mod -> canonical -> count
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        ev = json.loads(line)
        if ev.get("event") != "alias":
            continue
        l, r = ev.get("lukhas"), ev.get("real")
        votes[l][r] += 1
    mapping = {}
    for l, counts in votes.items():
        best, n = counts.most_common(1)[0]
        if n >= threshold:  # only rewrite if we have strong evidence
            mapping[l] = best
    return mapping

def rewrite_file(path: Path, mapping: dict, apply=False):
    src = text = path.read_text(errors="ignore")
    changed = False
    def subst(m):
        nonlocal changed
        mod = m.group("mod")
        if mod in mapping:
            changed = True
            new = mapping[mod]
            return f"{m.group('indent')}{m.group(0).strip().replace(mod, new)}"
        return m.group(0)
    new_text = IMPORT_RE.sub(subst, text)
    if changed and apply:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            shutil.copyfile(path, backup)
        path.write_text(new_text)
    return changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="apply changes (default dry-run)")
    ap.add_argument("--threshold", type=int, default=3)
    ap.add_argument("--root", default=".", help="search root")
    ap.add_argument("--glob", default="tests/**/*.py", help="files to rewrite")
    args = ap.parse_args()

    mapping = build_mapping(threshold=args.threshold)
    if not mapping:
        print("No strong mappings; nothing to rewrite.")
        return 0

    root = Path(args.root)
    files = list(root.glob(args.glob))
    touched = 0
    for f in files:
        if rewrite_file(f, mapping, apply=args.apply):
            touched += 1
            print(("REWRITE " if args.apply else "DRYRUN ") + str(f))
    print(f"✅ Done. Files {'rewritten' if args.apply else 'needing changes'}: {touched}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
