#!/usr/bin/env python3
"""
Dry-run autofix for a list of files. Prints diffs using ruff --fix --diff
and autoflake to show proposed changes without applying them.

Usage:
  python3 scripts/t4_dryrun_autofix.py /tmp/t4_batch2_candidates.txt --limit 20
"""

import argparse
import shlex
import subprocess
from pathlib import Path


def run(cmd):
    print(">>>", cmd)
    p = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    print(p.stdout)
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    files = [l.strip() for l in Path(args.candidates).read_text().splitlines() if l.strip()]
    files = files[: args.limit]

    for f in files:
        print(f"\n{'=' * 80}")
        print(f"== DRY-RUN FILE: {f}")
        print(f"{'=' * 80}")

        # ruff diff (will not write)
        result = run(f"python3 -m ruff check --fix --select F401 {f} --diff")
        if result == 0:
            print("✅ No F401 errors or fixes would be applied")
        else:
            print("⚠️  Changes would be applied (see diff above)")

    print("\n" + "=" * 80)
    print("Dry-run complete. Inspect diffs above.")
    print("=" * 80)


if __name__ == "__main__":
    main()
