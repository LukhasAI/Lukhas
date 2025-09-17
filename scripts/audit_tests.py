#!/usr/bin/env python3
"""
Test Collection Audit Script
T4-Approved: Simple exit code validation only, no auto-fix

Usage:
    python scripts/audit_tests.py

Returns:
    0: No collection errors
    Non-zero: Collection errors found
"""
import subprocess
import sys

def main():
    """Audit test collection - exit code based validation only"""
    print("🔍 Auditing test collection...")

    # Run pytest collection check
    result = subprocess.run(
        [".venv/bin/pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Test collection errors found")
        print("Fix manually by analyzing root causes:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)

    print("✅ No collection errors")
    return 0

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test Collection Audit Script (T4-Approved)
==========================================
Purpose:
  - Validate that pytest can COLLECT tests without errors.
  - Exit code ONLY is authoritative (no brittle regex parsing).
  - Never performs auto-fixes.

Usage:
  python scripts/audit_tests.py
  python scripts/audit_tests.py --save-errors test_errors.txt

Behavior:
  - Prefers local venv's pytest if present (.venv/bin/pytest).
  - Falls back to `python -m pytest` to avoid PATH issues.
  - Prints stdout/stderr only when collection fails.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _prefer_local_pytest() -> list[str]:
    """
    Return a command list to invoke pytest.

    Priority:
      1) .venv/bin/pytest if it exists and is executable
      2) python -m pytest (portable fallback)
    """
    repo_root = Path(__file__).resolve().parent.parent
    local = repo_root / ".venv" / "bin" / "pytest"
    if local.exists() and os.access(local, os.X_OK):
        return [str(local)]
    # Portable fallback (no reliance on PATH)
    return [sys.executable, "-m", "pytest"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit pytest collection (no auto-fix).")
    parser.add_argument(
        "--save-errors",
        metavar="PATH",
        default=None,
        help="Optional path to write full pytest output if collection fails."
    )
    args = parser.parse_args()

    cmd = _prefer_local_pytest() + ["--collect-only", "-q"]
    print("🔍 Auditing test collection…")
    print(f"▶ Running: {' '.join(cmd)}")

    # Keep environment deterministic; do NOT alter test behavior otherwise
    env = os.environ.copy()
    env.setdefault("PYTHONHASHSEED", "0")

    # Stream output only on failure; capture for optional saving
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Test collection errors found")
        if args.save_errors:
            out_path = Path(args.save_errors).expanduser().resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            out_path.write_text(
                f"# Pytest collection failure ({timestamp})\n\n"
                f"## Command\n{' '.join(cmd)}\n\n"
                f"## STDOUT\n{result.stdout}\n\n"
                f"## STDERR\n{result.stderr}\n"
            )
            print(f"📝 Full output saved to: {out_path}")
        else:
            # Print a concise hint and where to save details
            print("— stdout —")
            print(result.stdout.strip())
            print("— stderr —")
            print(result.stderr.strip())
            print("💡 Tip: re-run with `--save-errors test_errors.txt` to persist logs.")
        return result.returncode

    print("✅ No collection errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())