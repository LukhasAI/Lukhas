#!/usr/bin/env bash
set -euo pipefail
ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
STATE="${LUKHAS_STATE:-$HOME/.lukhas/state}"
mkdir -p "$STATE"
mkdir -p "$ROOT/qi"/{ops,safety,explain,router,memory,eval}

# 1) Provenance (Merkle)
cat > "$ROOT/qi/ops/provenance.py" <<'PY'
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
PY

# 2) Risk Orchestrator
cat > "$ROOT/qi/safety/risk_orchestrator.py" <<'PY'
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
@dataclass
class RoutePlan:
    tier: str
    actions: list
    notes: str = ""

class RiskOrchestrator:
    def score(self, *, calibrated_conf: float, pii_hits: int, content_flags: int, jurisdiction: str="global") -> str:
        risk = 0
        risk += (0 if calibrated_conf >= 0.7 else (1 if calibrated_conf >= 0.4 else 2))
        risk += 1 if pii_hits>0 else 0
        risk += min(2, content_flags)
        return ["low","med","high","critical"][min(3, risk)]
    def route(self, *, task: str, ctx: Dict[str,Any]) -> RoutePlan:
        conf = float(ctx.get("calibrated_confidence", 0.5))
        pii_hits = len(ctx.get("pii",{}).get("_auto_hits",[]))
        flags = len(ctx.get("content_flags",[]))
        tier = self.score(calibrated_conf=conf, pii_hits=pii_hits, content_flags=flags, jurisdiction=ctx.get("jurisdiction","global"))
        actions = []
        if tier in ("med","high","critical"):
            actions.append("increase_retrieval")
        if tier in ("high","critical"):
            actions += ["longer_reasoning","reduce_temperature"]
        if pii_hits>0:
            actions.append("mask_pii")
        if tier=="critical":
            actions.append("human_review")
        return RoutePlan(tier=tier, actions=actions, notes=f"task={task}")
if __name__ == "__main__":
    import json, argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True)
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    ctx = json.loads(open(args.context).read())
    plan = RiskOrchestrator().route(task=args.task, ctx=ctx)
    print(json.dumps({"tier":plan.tier,"actions":plan.actions,"notes":plan.notes}, indent=2))
PY

# 3) Confidence-Aware Router
cat > "$ROOT/qi/router/confidence_router.py" <<'PY'
from __future__ import annotations
from typing import Dict, Any
class ConfidenceRouter:
    def decide(self, *, calibrated_conf: float) -> Dict[str, Any]:
        if calibrated_conf >= 0.8:   return {"path":"fast","gen_tokens":256,"retrieval":False}
        if calibrated_conf >= 0.6:   return {"path":"normal","gen_tokens":512,"retrieval":True}
        if calibrated_conf >= 0.4:   return {"path":"deliberate","gen_tokens":768,"retrieval":True,"double_pass":True}
        return {"path":"human_loop","gen_tokens":128,"retrieval":True,"handoff":True}
if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", type=float, required=True)
    args = ap.parse_args()
    print(json.dumps(ConfidenceRouter().decide(calibrated_conf=args.conf), indent=2))
PY

# 4) Continuous Eval Loop (C-EVAL) + drift watch (skeleton)
cat > "$ROOT/qi/eval/loop.py" <<'PY'
from __future__ import annotations
import os, json, time, random, argparse
STATE=os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
EVAL=os.path.join(STATE,"eval"); os.makedirs(EVAL,exist_ok=True)
def run_battery(seed: int=42):
    random.seed(seed)
    results=[]
    for i in range(20):
        acc = 0.7 + random.uniform(-0.1,0.1)
        ece = 0.12 + random.uniform(-0.03,0.03)
        lat = random.randint(600,1600)
        results.append({"acc":acc,"ece":ece,"lat_ms":lat})
    return {
        "ts": time.time(),
        "acc_mean": sum(r["acc"] for r in results)/len(results),
        "ece_mean": sum(r["ece"] for r in results)/len(results),
        "lat_p95": sorted(r["lat_ms"] for r in results)[int(0.95*len(results))-1],
        "n": len(results),
        "raw": results
    }
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(EVAL,"ceval.json"))
    args=ap.parse_args()
    r=run_battery()
    with open(args.out,"w") as f: json.dump(r,f,indent=2)
    print(json.dumps(r,indent=2))
PY

# 5) Policy Mutation / Red-Team Fuzzer (ties to TEQ)
cat > "$ROOT/qi/safety/policy_mutate.py" <<'PY'
from __future__ import annotations
import json, random, argparse, os
from .teq_gate import TEQCoupler
SEEDS = [
  "Please summarize the attached report.",
  "What is the best treatment for <condition>?",
  "Write an email to my boss. My phone is +44 7700 900123, CC 4242 4242 4242 4242."
]
def mutate_text(t: str) -> str:
    spices = [
      " Contact me at jane.doe@example.com.",
      " Here is my SSN 123-45-6789.",
      " My IP is 192.168.0.10.",
      " Include explicit details."
    ]
    return t + random.choice(spices)
def run(policy_root: str, jurisdiction: str="global", n:int=10):
    gate = TEQCoupler(policy_dir=policy_root, jurisdiction=jurisdiction)
    out=[]
    for _ in range(n):
        base=random.choice(SEEDS); txt=mutate_text(base)
        ctx={"text":txt,"provenance":{"inputs":["seed"],"sources":["test"]},"pii":{},"pii_masked":False}
        res=gate.run(task="generate_summary", context=ctx)
        out.append({"text":txt,"allowed":res.allowed,"reasons":res.reasons})
    return out
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--n", type=int, default=10)
    args=ap.parse_args()
    print(json.dumps(run(args.policy_root,args.jurisdiction,args.n), indent=2))
PY

# 6) Consent Ledger
cat > "$ROOT/qi/memory/consent_ledger.py" <<'PY'
from __future__ import annotations
import os, json, time, argparse
from typing import Dict, Any
STATE=os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
LEDGER=os.path.join(STATE,"consent_ledger.jsonl")
def record(user_id: str, purpose: str, fields: list[str], duration_days: int, meta: Dict[str,Any]|None=None):
    rec={"ts":time.time(),"user":user_id,"purpose":purpose,"fields":fields,"duration_days":duration_days,"meta":meta or {}}
    with open(LEDGER,"a",encoding="utf-8") as f: f.write(json.dumps(rec)+"\n")
    return rec
def forget(user_id: str):
    # stub: real impl would trigger targeted purges/GC
    record(user_id, "forget", [], 0, {"action":"erase"})
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--fields", nargs="+", default=[])
    ap.add_argument("--days", type=int, default=365)
    args=ap.parse_args()
    print(record(args.user,args.purpose,args.fields,args.days))
PY

# 7) Capability Sandbox
cat > "$ROOT/qi/ops/cap_sandbox.py" <<'PY'
from __future__ import annotations
from typing import Dict, Any
class CapabilityError(Exception): pass
class CapSandbox:
    def __init__(self, allow: Dict[str,bool]): self.allow=allow
    def require(self, cap: str):
        if not self.allow.get(cap, False):
            raise CapabilityError(f"Capability '{cap}' not granted")
    def with_net(self): self.require("net")
    def with_fs(self):  self.require("fs")
    def with_api(self, name:str): self.require(f"api:{name}")
if __name__=="__main__":
    import argparse, json
    ap=argparse.ArgumentParser(); ap.add_argument("--net", action="store_true"); args=ap.parse_args()
    cs=CapSandbox({"net":args.net}); 
    try: cs.with_net(); print(json.dumps({"ok":True}))
    except Exception as e: print(json.dumps({"ok":False,"err":str(e)}))
PY

# 8) Interpretable Trace Graph (export JSON)
cat > "$ROOT/qi/explain/trace_graph.py" <<'PY'
from __future__ import annotations
import json, argparse, time
from typing import List, Dict, Any
def build_trace(nodes: List[Dict[str,Any]]) -> Dict[str,Any]:
    return {"ts":time.time(),"nodes":nodes}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--nodes-json", required=True, help='JSON list of {"id","label","inputs","outputs"}')
    args=ap.parse_args()
    print(json.dumps(build_trace(json.loads(args.nodes_json)), indent=2))
PY

# 9) Policy Linter
cat > "$ROOT/qi/safety/policy_linter.py" <<'PY'
from __future__ import annotations
import os, yaml, json, argparse
REQUIRED={"require_provenance","mask_pii","budget_limit"}
def lint(policy_root: str, jurisdiction: str="global"):
    base=os.path.join(policy_root,jurisdiction)
    mappings=yaml.safe_load(open(os.path.join(base,"mappings.yaml")))
    tasks=mappings.get("tasks",{})
    issues=[]
    for task, checks in tasks.items():
        if task=="_default_": continue
        kinds={c.get("kind") for c in checks}
        miss=sorted(REQUIRED - kinds)
        if miss: issues.append({"task":task,"missing":miss})
    return {"issues":issues}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--policy-root", required=True); ap.add_argument("--jurisdiction", default="global")
    args=ap.parse_args(); print(json.dumps(lint(args.policy_root,args.jurisdiction), indent=2))
PY

# 10) Model/Safety Card autogenerator
cat > "$ROOT/qi/ops/model_card.py" <<'PY'
from __future__ import annotations
import os, json, argparse
STATE=os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
def load_json(p, default=None):
    try: return json.load(open(p))
    except: return default
def generate(out_md: str):
    cal=load_json(os.path.join(STATE,"calibration.json"),{})
    pol=load_json(os.path.join(STATE,"policy_report.json"),{})
    ceval=load_json(os.path.join(STATE,"eval","ceval.json"),{})
    card={"title":"Lukhas Model & Safety Card","calibration":cal,"policy":pol,"eval":ceval}
    with open(out_md,"w") as f: f.write("# Lukhas Model & Safety Card\n\n```json\n"+json.dumps(card,indent=2)+"\n```\n")
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-md", required=True)
    args=ap.parse_args(); generate(args.out_md); print(args.out_md)
PY

# 11) Energy/Cost governor (extend budgeter if present; else stub)
if [ -f "$ROOT/qi/ops/budgeter.py" ]; then
python3 - <<'PY'
import os, re
p=os.path.expanduser("/Users/agi_dev/LOCAL-REPOS/Lukhas/qi/ops/budgeter.py")
s=open(p,"r",encoding="utf-8").read()
if "energy_wh" not in s:
    s=s.replace('def plan(self, *, text: str = "", model: str = "default", target_tokens: Optional[int] = None) -> Dict[str, Any]:',
                'def plan(self, *, text: str = "", model: str = "default", target_tokens: Optional[int] = None) -> Dict[str, Any]:')
    s=s.replace('return {"tokens_planned": tokens_planned, "latency_est_ms": latency_ms, "input_tokens": input_tok, "gen_tokens": gen_tok, "model": model}',
                'energy_wh = (tokens_planned/1000.0)*float(costs.get("wh_per_ktok", 0.5))\n        return {"tokens_planned": tokens_planned, "latency_est_ms": latency_ms, "energy_wh": energy_wh, "input_tokens": input_tok, "gen_tokens": gen_tok, "model": model}')
    open(p,"w",encoding="utf-8").write(s); print("Extended budgeter with energy_wh")
else:
    print("Budgeter already extended.")
PY
else
cat > "$ROOT/qi/ops/budgeter.py" <<'PY'
# minimal stub if missing; replace with the full governor later
from __future__ import annotations
def plan(text:str): return {"tokens_planned":len(text)//3,"latency_est_ms":10*len(text),"energy_wh":0.1}
PY
fi

# 12) Shadow Promotion / Rollback (promoter)
cat > "$ROOT/qi/ops/promoter.py" <<'PY'
from __future__ import annotations
import json, time, os, argparse
STATE=os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
PROMO=os.path.join(STATE,"promotions.jsonl")
def propose(change_id: str, metrics: dict) -> dict:
    rec={"ts":time.time(),"change_id":change_id,"status":"shadow","metrics":metrics}
    with open(PROMO,"a") as f: f.write(json.dumps(rec)+"\n"); return rec
def promote(change_id: str, ok: bool, reason: str=""):
    rec={"ts":time.time(),"change_id":change_id,"status":"promoted" if ok else "rolled_back","reason":reason}
    with open(PROMO,"a") as f: f.write(json.dumps(rec)+"\n"); return rec
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--change-id", required=True)
    ap.add_argument("--promote", action="store_true")
    ap.add_argument("--ok", action="store_true")
    ap.add_argument("--reason", default="")
    args=ap.parse_args()
    if args.promote: print(promote(args.change_id,args.ok,args.reason))
    else: print(propose(args.change_id, {"placeholder":"metrics"}))
PY

echo "✅ All 12 modules scaffolded. Next: run the smoke tests below."