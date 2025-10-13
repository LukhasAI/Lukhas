#!/usr/bin/env python3
"""Release a repo-local lock."""

import argparse
import json
import os
import sys

LOCK_DIR = ".dev/locks"


def main() -> int:
    parser = argparse.ArgumentParser(description="Release a repo-local lock.")
    parser.add_argument("--key", required=True)
    parser.add_argument("--owner", default="", help="Owner name (required unless --force)")
    parser.add_argument("--force", action="store_true", help="Force unlock even if owner mismatches")
    args = parser.parse_args()

    path = os.path.join(LOCK_DIR, f"{args.key}.lock")
    if not os.path.exists(path):
        print(f"[LOCK] '{args.key}' not found; nothing to unlock")
        return 0

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        data = {}

    current_owner = data.get("owner")
    if not args.force and args.owner and current_owner and args.owner != current_owner:
        print(
            f"[LOCK] '{args.key}' held by {current_owner}, not {args.owner}. Use --force if needed.",
            file=sys.stderr,
        )
        return 3

    os.remove(path)
    print(f"[LOCK] released '{args.key}'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
