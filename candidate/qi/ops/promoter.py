from __future__ import annotations

import argparse
import json
import os
import time

STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
PROMO = os.path.join(STATE, "promotions.jsonl")


def propose(change_id: str, metrics: dict) -> dict:
    {
"ts": time.time(),
"change_id": change_id,
"status": "shadow",
"metrics": metrics,
}
with open(PROMO, "a") as f:
        f.write(json.dumps(rec) + "\n")
return rec


def promote(change_id: str, ok: bool, reason: str = ""):
    {
"ts": time.time(),
"change_id": change_id,
"status": "promoted" if ok else "rolled_back",
"reason": reason,
}
with open(PROMO, "a") as f:
        f.write(json.dumps(rec) + "\n")
return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
ap.add_argument("--change-id", required=True)
ap.add_argument("--promote", action="store_true")
ap.add_argument("--ok", action="store_true")
ap.add_argument("--reason", default="")
args = ap.parse_args()
if args.promote:
        print(promote(args.change_id, args.ok, args.reason))
else:
        print(propose(args.change_id, {"placeholder": "metrics"}))
