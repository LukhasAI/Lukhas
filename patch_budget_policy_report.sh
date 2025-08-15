#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
QI="$ROOT/qi"
STATE="${LUKHAS_STATE:-$HOME/.lukhas/state}"

mkdir -p "$QI/ops" "$QI/safety" "$STATE"

# --- New: qi/ops/budgeter.py ---
cat > "$QI/ops/budgeter.py" <<'PY'
from __future__ import annotations
import os, json, time, math
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
BUDGET_FILE = os.path.join(STATE, "budget_state.json")
CONF_FILE   = os.path.join(STATE, "budget_config.json")

@dataclass
class BudgetConfig:
    default_token_cap: int = 200_000     # per-run soft cap
    default_latency_ms: int = 10_000
    user_overrides: Dict[str, Dict[str, Any]] = None  # {user_id: {"token_cap":..., "latency_ms":...}}
    task_overrides: Dict[str, Dict[str, Any]] = None  # {task: {...}}
    model_costs: Dict[str, Dict[str, float]] = None   # {model: {"tok_per_char": 0.35, "lat_ms_per_tok": 0.02}}

    def to_dict(self):
        return {
            "default_token_cap": self.default_token_cap,
            "default_latency_ms": self.default_latency_ms,
            "user_overrides": self.user_overrides or {},
            "task_overrides": self.task_overrides or {},
            "model_costs": self.model_costs or {"default":{"tok_per_char":0.35,"lat_ms_per_tok":0.02}}
        }

def _load_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def _save_json(path: str, obj: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

class Budgeter:
    """
    Lightweight cost governor. Tracks rolling usage and estimates planned cost.
    - plan(text, model, target_tokens) -> dict with tokens_planned, latency_est_ms
    - check(user, task, plan) -> dict with 'ok' and 'reason' if exceeded
    - commit(user, task, actual_tokens, latency_ms) -> record usage
    """
    def __init__(self):
        self.conf = BudgetConfig(**_load_json(CONF_FILE, {}))
        self.state = _load_json(BUDGET_FILE, {"runs": []})  # append-only ring in real life

    def save(self):
        _save_json(CONF_FILE, self.conf.to_dict())
        _save_json(BUDGET_FILE, self.state)

    # ---- planning ----
    def plan(self, *, text: str = "", model: str = "default", target_tokens: Optional[int] = None) -> Dict[str, Any]:
        costs = (self.conf.model_costs or {}).get(model) or (self.conf.model_costs or {})["default"]
        tok_per_char = float(costs.get("tok_per_char", 0.35))
        lat_per_tok  = float(costs.get("lat_ms_per_tok", 0.02))

        input_tok = math.ceil(len(text) * tok_per_char)
        gen_tok   = int(target_tokens or max(256, input_tok // 2))
        tokens_planned = input_tok + gen_tok
        latency_ms = int(tokens_planned * lat_per_tok)

        return {"tokens_planned": tokens_planned, "latency_est_ms": latency_ms, "input_tokens": input_tok, "gen_tokens": gen_tok, "model": model}

    # ---- limits ----
    def _caps(self, user_id: Optional[str], task: Optional[str]) -> Dict[str, int]:
        cap = self.conf.default_token_cap
        lat = self.conf.default_latency_ms
        if task and (self.conf.task_overrides or {}).get(task):
            t = self.conf.task_overrides[task]
            cap = int(t.get("token_cap", cap))
            lat = int(t.get("latency_ms", lat))
        if user_id and (self.conf.user_overrides or {}).get(user_id):
            u = self.conf.user_overrides[user_id]
            cap = int(u.get("token_cap", cap))
            lat = int(u.get("latency_ms", lat))
        return {"token_cap": cap, "latency_ms": lat}

    def check(self, *, user_id: Optional[str], task: Optional[str], plan: Dict[str, Any]) -> Dict[str, Any]:
        caps = self._caps(user_id, task)
        reasons = []
        if plan["tokens_planned"] > caps["token_cap"]:
            reasons.append(f"tokens_planned {plan['tokens_planned']} > cap {caps['token_cap']}")
        if plan["latency_est_ms"] > caps["latency_ms"]:
            reasons.append(f"latency_est_ms {plan['latency_est_ms']} > cap {caps['latency_ms']}")
        return {"ok": not reasons, "reasons": reasons, "caps": caps}

    # ---- accounting ----
    def commit(self, *, user_id: Optional[str], task: Optional[str], actual_tokens: int, latency_ms: int, meta: Dict[str, Any] | None=None):
        self.state["runs"].append({
            "ts": time.time(), "user": user_id, "task": task,
            "tokens": int(actual_tokens), "latency_ms": int(latency_ms),
            "meta": meta or {}
        })
        # in a real system, consider trimming old entries or summarising
        self.save()

# CLI convenience
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Lukhas Budget Governor")
    ap.add_argument("--plan-text", default="")
    ap.add_argument("--model", default="default")
    ap.add_argument("--target-tokens", type=int)
    ap.add_argument("--user")
    ap.add_argument("--task")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--actual-tokens", type=int, default=0)
    ap.add_argument("--latency-ms", type=int, default=0)
    args = ap.parse_args()

    b = Budgeter()
    plan = b.plan(text=args.plan_text, model=args.model, target_tokens=args.target_tokens)
    verdict = b.check(user_id=args.user, task=args.task, plan=plan)
    out = {"plan": plan, "verdict": verdict}
    print(json.dumps(out, indent=2))
    if args.commit:
        b.commit(user_id=args.user, task=args.task, actual_tokens=args.actual_tokens or plan["tokens_planned"], latency_ms=args.latency_ms or plan["latency_est_ms"])
        print("Committed usage.")
PY

# --- New: qi/safety/policy_report.py ---
cat > "$QI/safety/policy_report.py" <<'PY'
from __future__ import annotations
import os, json, glob
from typing import Dict, List, Any
import yaml

CHECK_KINDS = {"require_provenance","mask_pii","budget_limit","age_gate","content_policy"}

def load_pack(policy_root: str, jurisdiction: str = "global") -> Dict[str, Any]:
    base = os.path.join(policy_root, jurisdiction)
    with open(os.path.join(base, "policy.yaml"), "r", encoding="utf-8") as f:
        policy = yaml.safe_load(f)
    with open(os.path.join(base, "mappings.yaml"), "r", encoding="utf-8") as f:
        mappings = yaml.safe_load(f)
    return {"root": base, "policy": policy, "mappings": mappings}

def coverage_matrix(mappings: Dict[str, Any]) -> Dict[str, List[str]]:
    tasks = mappings.get("tasks", {})
    out: Dict[str, List[str]] = {}
    for task, checks in tasks.items():
        if task == "_default_":
            continue
        kinds = [c.get("kind") for c in checks]
        out[task] = kinds
    return out

def gap_analysis(matrix: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    gaps = []
    for task, kinds in matrix.items():
        kset = set(kinds)
        if "mask_pii" not in kset:
            gaps.append({"task": task, "gap": "no_mask_pii"})
        if "require_provenance" not in kset:
            gaps.append({"task": task, "gap": "no_provenance"})
        # Example additional checks you may require:
        # if task seems medical and content_policy(medical_high_risk) not present:
        if "medical" in task and "content_policy" not in kset:
            gaps.append({"task": task, "gap": "no_medical_policy"})
    return gaps

def to_markdown(matrix: Dict[str, List[str]], gaps: List[Dict[str, Any]]) -> str:
    lines = ["# Policy Coverage Report", "", "## Task → Checks", "", "| Task | Checks |", "|---|---|"]
    for task, kinds in sorted(matrix.items()):
        lines.append(f"| `{task}` | {', '.join(sorted(kinds))} |")
    lines += ["", "## Gaps", "", "| Task | Gap |", "|---|---|"]
    if not gaps:
        lines.append("| ✓ | No gaps detected |")
    else:
        for g in gaps:
            lines.append(f"| `{g['task']}` | {g['gap']} |")
    return "\n".join(lines)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Policy Coverage Reporter")
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    args = ap.parse_args()

    pack = load_pack(args.policy_root, args.jurisdiction)
    matrix = coverage_matrix(pack["mappings"])
    gaps = gap_analysis(matrix)
    report = {"jurisdiction": args.jurisdiction, "matrix": matrix, "gaps": gaps}

    print(json.dumps(report, indent=2))
    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    if args.out_md:
        md = to_markdown(matrix, gaps)
        os.makedirs(os.path.dirname(args.out_md), exist_ok=True)
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md)
PY

# --- TEQ: tiny optional hook to pull plan if tokens_planned missing ---
python3 - <<'PY'
import re, io, os, sys
p = "/Users/agi_dev/LOCAL-REPOS/Lukhas/qi/safety/teq_gate.py"
src = open(p, "r", encoding="utf-8").read()
needle = 'def _budget_limit(self, ctx: Dict[str, Any], max_tokens: int | None) -> Tuple[bool, str, str]:'
if needle in src and "AUTO-BUDGET" not in src:
    src = src.replace(
        needle,
        needle + '\n        # AUTO-BUDGET: if no tokens_planned, estimate via Budgeter (best-effort)'
    )
    src = src.replace(
        'if max_tokens is None:\n            return (True, "", "")\n        used = int(ctx.get("tokens_planned", 0))',
        'if max_tokens is None:\n            return (True, "", "")\n        used = int(ctx.get("tokens_planned", -1))\n        if used < 0:\n            try:\n                from qi.ops.budgeter import Budgeter\n                text = ctx.get("text") or ctx.get("input_text") or ""\n                plan = Budgeter().plan(text=text)\n                used = int(plan.get("tokens_planned", 0))\n                ctx["tokens_planned"] = used\n            except Exception:\n                used = 0'
    )
    open(p, "w", encoding="utf-8").write(src)
    print("Patched AUTO-BUDGET into teq_gate.py")
else:
    print("AUTO-BUDGET already present or teq_gate.py not found.")
PY

echo "✅ Budgeter + Policy Report patch applied."