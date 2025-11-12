#!/usr/bin/env python3
# scripts/dream_validate_pr.py
"""
CLI: dream validation gate used by CI for PRs.
Usage:
  python3 scripts/dream_validate_pr.py --prompts bench/prompts_fixed.json --max-drift 0.15
"""
import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator.guardian_orchestrator import GuardianOrchestrator
from core.qrg.signing import generate_private_key, private_key_to_pem


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompts", required=True)
    p.add_argument("--max-drift", type=float, default=0.15)
    args = p.parse_args()
    prompts = json.load(open(args.prompts))
    # demo private key generation (CI should use proper key)
    priv = generate_private_key()
    priv_pem = private_key_to_pem(priv)
    go = GuardianOrchestrator(priv_pem, drift_budget=args.max_drift)
    res = go.dream_validate(prompts, seed_shift=1)
    print(json.dumps({"drift": res["drift"]}, indent=2))
    if res["drift"] > args.max_drift:
        print(f"DRIFT_FAIL: {res['drift']:.4f} > {args.max_drift:.4f}")
        raise SystemExit(2)
    print("DRIFT_OK")
    return 0

if __name__ == "__main__":
    main()
