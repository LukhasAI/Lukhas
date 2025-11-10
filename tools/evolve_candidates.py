# Lists "evolution" candidates: low coverage + high fan-in/hot paths (simple heuristics)
from __future__ import annotations
import json, pathlib, subprocess

def _cov():
    p = pathlib.Path("reports/coverage.xml")
    if not p.exists():
        subprocess.run("pytest --cov=. --cov-report=xml:reports/coverage.xml -q", shell=True, check=False)
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
    files = subprocess.check_output("git ls-files '*.py'", shell=True, text=True).splitlines()
    hot = []
    for f in files:
        try:
            bl = subprocess.check_output(f"git blame --line-porcelain -- {f} | grep '^author ' | wc -l", shell=True, text=True)
            lines = int(bl.strip() or "0")
        except Exception:
            lines = 0
        hot.append((f, cov.get(f, 0), lines))
    # rank: low coverage first, then more lines (proxy for hotness)
    hot.sort(key=lambda t: (t[1], -t[2]))
    print(json.dumps([{"file": f, "coverage_score": c, "lines": n} for f, c, n in hot[:50]], indent=2))

if __name__ == "__main__":
    main()
