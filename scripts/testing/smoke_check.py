#!/usr/bin/env python3
"""
Simple smoke checks for local/dev environments.

Checks:
- Health endpoint `/healthz` on a configurable base URL.

Usage:
  python3 scripts/testing/smoke_check.py [--base-url http://localhost:8000] [--json out/smoke.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

try:
    import requests
except Exception:
    print("requests not available; install via requirements-test.txt", file=sys.stderr)
    sys.exit(2)


def check_health(base_url: str, timeout: float = 2.0) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/healthz"
    try:
        r = requests.get(url, timeout=timeout)
        return {
            "check": "healthz",
            "url": url,
            "status_code": r.status_code,
            "ok": r.ok and r.status_code == 200,
            "body": (r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text),
        }
    except Exception as e:
        return {"check": "healthz", "url": url, "ok": False, "error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="LUKHAS smoke checks")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--json", dest="json_out", default=None, help="Write JSON results to file")
    args = parser.parse_args()

    results = {
        "base_url": args.base_url,
        "checks": [],
        "ok": True,
    }

    health = check_health(args.base_url)
    results["checks"].append(health)
    results["ok"] = results["ok"] and bool(health.get("ok"))

    # Write JSON if requested
    if args.json_out:
        try:
            os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to write JSON results: {e}", file=sys.stderr)

    # Human-readable output
    for c in results["checks"]:
        status = "PASS" if c.get("ok") else "FAIL"
        print(f"[{status}] {c.get('check')} -> {c.get('url')} ({c.get('status_code', 'n/a'})")

    return 0 if results["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
