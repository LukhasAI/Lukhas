#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, time
from pathlib import Path

REQUIRED_ARTIFACT_SUFFIXES = [
  "perf_e2e_bootstrap.json",
  "guardian_validation.json",
  "telemetry_contracts.json",
  "resilience_validation.json",
]

def find_module_manifest(mod: str) -> Path|None:
    # allow either per-module manifest or a top-level mapping later
    expected = Path(*mod.split(".")) / "module.lane.yaml"
    for root in ("lukhas", "candidate", ".",):
        p = Path(root) / expected
        if p.exists():
            return p
    return None

def collect_artifacts(mod: str):
    ap = Path("artifacts")
    if not ap.exists(): return []
    pat = re.compile(re.escape(mod.replace(".","_")) + r".*(validation|perf|contracts|resilience).*\.json$")
    return [p for p in ap.glob("*.json") if pat.search(p.name)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modules", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    report = {"ts": int(time.time()), "modules": []}

    for mod in args.modules:
        manifest = find_module_manifest(mod)
        arts = collect_artifacts(mod)
        found_suffixes = {suf: any(a.name.endswith(suf) for a in arts) for suf in REQUIRED_ARTIFACT_SUFFIXES}
        ready = manifest is not None and all(found_suffixes.values())
        report["modules"].append({
            "module": mod,
            "manifest": str(manifest) if manifest else None,
            "artifacts": [a.name for a in arts],
            "required_artifacts_ok": found_suffixes,
            "ready_for_promotion": bool(ready)
        })

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"[ok] readiness report → {args.out}")

if __name__ == "__main__":
    main()
