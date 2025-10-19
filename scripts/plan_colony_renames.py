#!/usr/bin/env python3
"""
Module: plan_colony_renames.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Plan colony (lane) renames without touching the tree.

- Scans for lane-ish dirs (candidate/, legacy lucas/, nested pockets)
- Proposes target colony paths (labs/, lukhas/* per brand map)
- Writes CSV: docs/audits/colony/colony_renames_<stamp>.csv
- Prints exact `git mv` commands (DRY-RUN ONLY)

Usage:
  python3 scripts/plan_colony_renames.py [--root .] [--stamp 2025-10-14T18-03-17Z]
"""
import argparse, csv, os, re, sys, time
from pathlib import Path
from typing import Optional, Tuple

BRAND_MAP = {
    "candidate": "labs",
    "lucas": "lukhas",
    "Lucas": "lukhas",
    "LUCAS": "lukhas",
}

SKIP_DIRS = {
    ".git", ".github", ".venv", "venv", "__pycache__", "node_modules",
    "docs/postman", "docs/audits", "docs/releases",
    "examples", "scripts", ".dev", ".idea", ".vscode",
}

def stamp_now():
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())

def looks_laneish(p: Path) -> bool:
    name = p.name
    if name in BRAND_MAP:
        return True
    # nested pockets like src/candidate/, libs/lucas/
    return any(tok in BRAND_MAP for tok in name.split("-"))

def propose_target(p: Path) -> Optional[Tuple[str, str]]:
    name = p.name
    if name in BRAND_MAP:
        return (str(p), str(p.with_name(BRAND_MAP[name])))
    # Heuristic: lucas.* top-level packages → lukhas.*
    if name.startswith("lucas") and p.is_dir():
        return (str(p), str(p.with_name(re.sub(r"^lucas", "lukhas", name))))
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--stamp", default=stamp_now())
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = root / "docs" / "audits" / "colony"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"colony_renames_{args.stamp}.csv"

    proposals = []
    for base, dirs, files in os.walk(root):
        base_p = Path(base)
        # prune
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for d in list(dirs):
            p = base_p / d
            if looks_laneish(p):
                target = propose_target(p)
                if target and target[0] != target[1]:
                    reason = "brand/colony normalization"
                    proposals.append((*target, reason))

    proposals.sort(key=lambda t: t[0])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["old_path", "new_path", "reason"])
        for old, new, reason in proposals:
            w.writerow([old, new, reason])

    print(f"# Dry-run colony rename plan → {csv_path}")
    print("# Proposed commands (not executed):")
    for old, new, _ in proposals:
        print(f"git mv {old} {new}")

    if not proposals:
        print("# No lane-ish directories found that require renaming.")

if __name__ == "__main__":
    sys.exit(main())
