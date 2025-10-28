#!/usr/bin/env python3
"""
Fail CI if Ruff E402 count increases relative to baseline.

Usage:
  python fail_on_delta.py --ruff-output artifacts/.../ruff_e402.txt --baseline-file .github/import_health/baseline_e402_count.txt --fail-if-increase
"""

import argparse
import sys
from pathlib import Path

def count_e402_from_ruff_file(path: Path) -> int:
    # ruff output file — we'll count lines or parse numbers.
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return 0
    # If ruff printed statistics only
    # Fallback: count lines with "E402"
    lines = text.splitlines()
    count = 0
    for line in lines:
        if "E402" in line:
            # format: path:line:col: E402 ...
            count += 1
    # If file contains a single number, try parse
    if count == 0:
        try:
            return int(text.strip())
        except Exception:
            return 0
    return count

def read_baseline(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return int(path.read_text().strip())
    except Exception:
        return 0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ruff-output", required=True, help="path to ruff e402 output")
    p.add_argument("--baseline-file", required=True, help="path to baseline file with integer")
    p.add_argument("--fail-if-increase", action="store_true")
    args = p.parse_args()
    ruff_count = count_e402_from_ruff_file(Path(args.ruff_output))
    baseline = read_baseline(Path(args.baseline_file))
    print(f"Ruff E402 count: {ruff_count}, baseline: {baseline}")
    if args.fail_if_increase and ruff_count > baseline:
        print("E402 count increased. Failing CI.")
        sys.exit(1)
    print("E402 delta OK.")
    sys.exit(0)

if __name__ == "__main__":
    main()
