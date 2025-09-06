#!/usr/bin/env python3
"""CLI wrapper to run the ΛLens API in a predictable way.

Usage:
  python cli.py --host 0.0.0.0 --port 8000 --reload

This script ensures the repository root is on PYTHONPATH and launches Uvicorn
with the canonical application object (`main:app`).
"""

import argparse
import sys
from pathlib import Path


def add_repo_root_to_path():
    # Locate repo root by searching upward for pyproject.toml or .git
    p = Path(__file__).resolve()
    cur = p
    for _ in range(10):
        if (cur / "pyproject.toml").exists() or (cur / ".git").exists():
            sys.path.insert(0, str(cur))
            return
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback: insert a few parents up (repo layout known)
    sys.path.insert(0, str(p.parents[5]))


def main() -> None:
    parser = argparse.ArgumentParser(prog="λLens CLI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for dev")
    parser.add_argument("--workers", type=int, default=1, help="Number of Uvicorn workers")
    args = parser.parse_args()

    add_repo_root_to_path()

    # Import here so PYTHONPATH is set
    try:
        import uvicorn

        # main.py provides app as module-level `app`
        uvicorn.run(
            "products.intelligence.lens.api_new.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
        )
    except Exception as exc:
        print("Failed to start server:", exc)
        raise


if __name__ == "__main__":
    main()
