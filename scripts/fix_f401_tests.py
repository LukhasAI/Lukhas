#!/usr/bin/env python3
# Fix F401 "imported but unused" only under tests/** using Ruff JSON as ground truth.
# Requires: ruff JSON report at docs/audits/ruff.json (or --ruff)
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import libcst as cst
import libcst.matchers as m


def load_json(p: Path): return json.loads(p.read_text(encoding="utf-8"))

def bucket_unused_by_file(ruff_events, root: Path) -> dict[str, set[str]]:
    unused: dict[str, set[str]] = {}
    for e in ruff_events:
        if e.get("code") != "F401":
            continue
        fn = e.get("filename")
        if not fn or "tests/" not in fn.replace("\\","/"):
            continue
        msg = e.get("message","")
        # Ruff message formats include "'name' imported but unused" (varies by font)
        # Try to extract symbol between quotes; fall back to last token heuristic.
        sym = None
        for q in ("'", "'", "'", """, """, "«", "»"):
            if q in msg:
                parts = msg.split(q)
                if len(parts) >= 3:
                    sym = parts[1]
                    break
        if not sym:
            # fallback: last word
            sym = msg.split()[-1]
        unused.setdefault(fn, set()).add(sym)
    return unused

class PruneImports(cst.CSTTransformer):
    def __init__(self, unused: set[str]):
        self.unused = unused
        self.changed = False

    def leave_Import(self, node: cst.Import, updated: cst.Import):
        # import a, b as c → drop only unused names
        new_names = []
        for alias in updated.names:
            name = alias.evaluated_name
            if name in self.unused:
                self.changed = True
                continue
            new_names.append(alias)
        if not new_names:
            self.changed = True
            return cst.RemoveFromParent()
        return updated.with_changes(names=new_names)

    def leave_ImportFrom(self, node: cst.ImportFrom, updated: cst.ImportFrom):
        # from x import a, b as c
        if m.matches(updated.names, m.ImportStar()):
            return updated  # never remove star
        kept = []
        for alias in updated.names:
            name = alias.evaluated_name
            if name in self.unused:
                self.changed = True
                continue
            kept.append(alias)
        if not kept:
            self.changed = True
            return cst.RemoveFromParent()
        return updated.with_changes(names=tuple(kept))

def run_file(path: Path, unused_names: set[str], apply: bool) -> bool:
    src = path.read_text(encoding="utf-8")
    mod = cst.parse_module(src)
    tx = PruneImports(unused_names)
    out = mod.visit(tx)
    if tx.changed and apply:
        path.write_text(out.code, encoding="utf-8")
    return tx.changed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruff", default="docs/audits/ruff.json")
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    events = load_json(Path(args.ruff))
    unused_by_file = bucket_unused_by_file(events, root)

    changed = 0
    for fn, names in sorted(unused_by_file.items()):
        p = (root / fn).resolve()
        if not p.exists():
            continue
        if run_file(p, names, args.apply):
            changed += 1
            print(f"[fix] {fn}: -{', -'.join(sorted(names))}")
    print(f"[OK] files changed: {changed}")
    sys.exit(0)

if __name__ == "__main__":
    main()
