#!/usr/bin/env python3
"""List active repo-local locks."""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

LOCK_DIR = ".dev/locks"


def parse_iso(timestamp: Optional[str]) -> Optional[datetime]:
    if not timestamp:
        return None
    try:
        return datetime.fromisoformat(timestamp)
    except Exception:
        return None


def main() -> int:
    if not os.path.isdir(LOCK_DIR):
        print("(no locks dir)")
        return 0

    rows: list[tuple[str, str, str, str, int]] = []
    for name in sorted(os.listdir(LOCK_DIR)):
        if not name.endswith(".lock"):
            continue
        path = os.path.join(LOCK_DIR, name)
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception:
            data = {}

        key = data.get("key") or name[:-5]
        owner = data.get("owner") or "unknown"
        branch = data.get("branch") or ""
        expires_at = parse_iso(data.get("expires_at"))
        now = datetime.now(timezone.utc)
        remaining = int((expires_at - now).total_seconds()) if expires_at else -1
        state = "EXPIRED" if remaining < 0 else "HELD"
        rows.append((key, owner, branch, state, remaining))

    if not rows:
        print("(no active locks)")
        return 0

    print(f"{'KEY':24} {'OWNER':20} {'BRANCH':28} {'STATE':8} {'TTL(s)':7}")
    for key, owner, branch, state, ttl in rows:
        ttl_str = str(ttl) if ttl >= 0 else "-"
        print(f"{key:24} {owner:20} {branch:28} {state:8} {ttl_str:7}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
