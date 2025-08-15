from __future__ import annotations
import os, json, time, hashlib, argparse
from typing import Any, Dict, List
STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
PROV_DIR = os.path.join(STATE, "prov"); os.makedirs(PROV_DIR, exist_ok=True)

def _h(v: Any) -> str:
    b = json.dumps(v, sort_keys=True, ensure_ascii=False).encode("utf-8") if not isinstance(v,(bytes,bytearray)) else v
    return hashlib.sha256(b).hexdigest()

def merkle_chain(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prev = None
    out = []
    for s in steps:
        body = {k:v for k,v in s.items() if k != "prev"}
        node = {"ts": time.time(), "body": body, "prev": prev}
        node["hash"] = _h(node["body"] | ({"prev": prev} if prev else {}))
        prev = node["hash"]; out.append(node)
    return out

def attest(chain: List[Dict[str, Any]], tag: str) -> str:
    path = os.path.join(PROV_DIR, f"{int(time.time())}_{tag}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for n in chain: f.write(json.dumps(n, ensure_ascii=False)+"\n")
    return path

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Provenance logger")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--step", action="append", help="JSON dict per step", required=True)
    args = ap.parse_args()
    steps = [json.loads(s) for s in args.step]
    print(attest(merkle_chain(steps), args.tag))
