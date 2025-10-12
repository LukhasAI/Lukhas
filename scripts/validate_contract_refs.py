#!/usr/bin/env python3
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = list(ROOT.rglob("module.manifest.json"))
CONTRACTS = {p.stem: p for p in (ROOT/"contracts").glob("*.json")}
ID_RE = re.compile(r"^[a-z0-9_.:-]+@v\d+$")

def main():
    failures = 0
    for mf in MANIFESTS:
        m = json.loads(mf.read_text(encoding="utf-8"))
        ev = m.get("observability",{}).get("events",{})
        for kind in ("publishes","subscribes"):
            for item in ev.get(kind, []):
                stem = item
                if not ID_RE.match(stem):
                    print(f"[FAIL] {mf}: invalid contract id: {stem}")
                    failures += 1
                    continue
                key = stem.split("@",1)[0]+"@"+stem.split("@",1)[1]
                if key not in CONTRACTS:
                    print(f"[FAIL] {mf}: unknown contract: {stem}")
                    failures += 1
    print("failures:", failures)
    if failures:
        sys.exit(1)

if __name__ == "__main__":
    main()
