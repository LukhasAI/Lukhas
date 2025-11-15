# Lists "evolution" candidates: low coverage + high fan-in/hot paths (simple heuristics)
from __future__ import annotations

import json
import pathlib
import subprocess

from lukhas.security.safe_subprocess import safe_run_command


def _cov():
    p = pathlib.Path("reports/coverage.xml")
    if not p.exists():
        try:
            safe_run_command(["pytest", "--cov=.", "--cov-report=xml:reports/coverage.xml", "-q"], check=False)
        except Exception:
            pass
    from xml.etree import ElementTree as ET
    root = ET.parse("reports/coverage.xml").getroot()
    byfile = {}
    for f in root.iter("class"):
        fn = f.get("filename")
        if not fn: continue
        lines_valid = int(f.get("line-rate", "0").split(".")[0] or 0)  # coarse
        byfile[fn] = lines_valid
    return byfile

def main():
    cov = _cov()
    # naive "hotness" with git blame line counts
    result = safe_run_command(["git", "ls-files", "*.py"], check=True)
    files = result.stdout.splitlines()
    hot = []
    for f in files:
        try:
            # Get git blame output and count author lines
            blame_result = safe_run_command(["git", "blame", "--line-porcelain", "--", f], check=True)
            lines = sum(1 for line in blame_result.stdout.splitlines() if line.startswith("author "))
        except Exception:
            lines = 0
        hot.append((f, cov.get(f, 0), lines))
    # rank: low coverage first, then more lines (proxy for hotness)
    hot.sort(key=lambda t: (t[1], -t[2]))
    print(json.dumps([{"file": f, "coverage_score": c, "lines": n} for f, c, n in hot[:50]], indent=2))

if __name__ == "__main__":
    main()
