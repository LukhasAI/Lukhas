#!/usr/bin/env python3
import csv
import datetime
import os
import re
import subprocess
import sys

SRC = "reports/audit/types/mypy.txt"
DST = "reports/audit/types/trends.csv"


def count_errors(content):
    lines = content.strip().splitlines()
    errors = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("Found ") or line.startswith("Success"):
            continue
        # Match: path:line:col: error_type: message [code]
        match = re.match(r"^([^:]+):(\d+):(\d+):\s*(\w+):\s*(.+?)(?:\s+\[([^\]]+)\])?$", line)
        if match:
            path = match.group(1)
            errors.append(path)

    total = len(errors)
    core = sum(1 for path in errors if path.startswith(("lukhas/", "MATRIZ/")))
    return core, total


def git(cmd):
    try:
        return subprocess.check_output(["git", *cmd], text=True).strip()
    except Exception:
        return ""


def main():
    if not os.path.exists(SRC):
        print(f"[mypy_trend] missing {SRC}", file=sys.stderr)
        return 2
    with open(SRC, encoding="utf-8") as f:
        content = f.read()

    core, total = count_errors(content)
    now = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    sha = git(["rev-parse", "--short", "HEAD"])
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"])

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    header = ["timestamp_utc", "commit", "branch", "core_errors", "total_errors"]
    write_header = not os.path.exists(DST) or os.path.getsize(DST) == 0

    with open(DST, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow([now, sha, branch, core, total])

    print(f"[mypy_trend] appended → {DST} | core={core} total={total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
