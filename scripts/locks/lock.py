#!/usr/bin/env python3
"""Acquire or refresh a lightweight repo-local lock."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

LOCK_DIR = ".dev/locks"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def load(path: str) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or refresh a lightweight repo-local lock."
    )
    parser.add_argument("--key", required=True, help="Logical area name, e.g. hotpaths-b1")
    parser.add_argument("--owner", required=True, help="Human-readable owner")
    parser.add_argument("--branch", default="", help="Git branch owning the work")
    parser.add_argument("--ttl", type=int, default=3600, help="TTL seconds (default 3600)")
    args = parser.parse_args()

    os.makedirs(LOCK_DIR, exist_ok=True)
    path = os.path.join(LOCK_DIR, f"{args.key}.lock")

    now = now_utc()
    data = load(path)
    if data:
        try:
            exp = datetime.fromisoformat(data.get("expires_at"))
        except Exception:
            exp = None
        if exp and exp > now:
            print(
                f"[LOCK] '{args.key}' already held by {data.get('owner')} until {data.get('expires_at')}",
                file=sys.stderr,
            )
            return 2

    expires = now + timedelta(seconds=args.ttl)
    payload = {
        "key": args.key,
        "owner": args.owner,
        "branch": args.branch,
        "pid": os.getpid(),
        "created_at": iso(now),
        "ttl_seconds": args.ttl,
        "expires_at": iso(expires),
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"[LOCK] acquired '{args.key}' for {args.owner} until {payload['expires_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
