from __future__ import annotations
import argparse, os, glob, json, time
import yaml
from .teq_gate import TEQCoupler

def main():
    ap = argparse.ArgumentParser(description="Policy Pack Test Runner")
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    args = ap.parse_args()

    gate = TEQCoupler(args.policy_root, jurisdiction=args.jurisdiction)
    pack_dir = os.path.join(args.policy_root, args.jurisdiction, "tests")
    tests = sorted(glob.glob(os.path.join(pack_dir, "*.yaml")))
    results = []
    for tpath in tests:
        with open(tpath, "r", encoding="utf-8") as f:
            case = yaml.safe_load(f)
        task = case.get("task")
        ctx = case.get("context", {})
        want = bool(case.get("expect_allowed", True))
        res = gate.run(task, ctx)
        ok = (res.allowed == want)
        results.append({
            "file": os.path.basename(tpath),
            "task": task,
            "expected": want,
            "got": res.allowed,
            "pass": ok,
            "reasons": res.reasons,
            "remedies": res.remedies
        })
    summary = {
        "jurisdiction": args.jurisdiction,
        "total": len(results),
        "passed": sum(1 for r in results if r["pass"]),
        "failed": [r for r in results if not r["pass"]],
        "timestamp": time.time()
    }
    print(json.dumps({"results": results, "summary": summary}, indent=2))
    raise SystemExit(0 if summary["passed"] == summary["total"] else 1)

if __name__ == "__main__":
    main()
