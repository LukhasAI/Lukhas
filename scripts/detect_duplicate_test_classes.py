#!/usr/bin/env python3
import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path


def find_test_classes(py: Path):
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            out.append((node.name, node.lineno))
    return out

def apply_renames(py: Path, dups: list[tuple[str,int,int]]):
    # dups: (orig_name, lineno, suffix_index)
    lines = py.read_text(encoding="utf-8").splitlines()
    for orig, lineno, idx in sorted(dups, key=lambda x: -x[1]):  # bottom-up edit
        line = lines[lineno-1]
        lines[lineno-1] = line.replace(f"class {orig}", f"class {orig}_{idx}")
    py.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser(description="Detect duplicate Test classes; optionally rename.")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--root", default="tests")
    args = ap.parse_args()

    root = Path(args.root)
    dup_total = 0
    for py in root.rglob("test*.py"):
        classes = find_test_classes(py)
        if not classes:
            continue
        counter = defaultdict(int)
        dups = []
        for name, lineno in classes:
            counter[name] += 1
            if counter[name] > 1:
                dups.append((name, lineno, counter[name]))  # suffix with 2,3,...
        if dups:
            dup_total += len(dups)
            print(f"[DUP] {py}: " + ", ".join([f"{n}@{ln}:{i}" for n,ln,i in dups]))
            if args.apply:
                apply_renames(py, dups)

    if args.apply:
        print(f"[OK] Renamed {dup_total} duplicate class occurrences.")
    else:
        if dup_total == 0:
            print("[OK] No duplicate test classes found.")
        else:
            print(f"[INFO] Found {dup_total} duplicates (run with --apply to rename).")

if __name__ == "__main__":
    sys.exit(main())
