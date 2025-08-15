from __future__ import annotations
import argparse, os, json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import yaml

@dataclass
class GateResult:
    allowed: bool
    reasons: List[str]
    remedies: List[str]
    jurisdiction: str

class PolicyPack:
    def __init__(self, root: str):
        self.root = root
        self.policy = self._load_yaml(os.path.join(root, "policy.yaml"))
        self.mappings = self._load_yaml(os.path.join(root, "mappings.yaml"), default={"tasks": {}})
        self.tests = self._load_tests(os.path.join(root, "tests"))

    def _load_yaml(self, p: str, default=None):
        if not os.path.exists(p):
            return default
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_tests(self, folder: str) -> List[Dict[str, Any]]:
        out = []
        if not os.path.isdir(folder):
            return out
        for fn in os.listdir(folder):
            if fn.endswith(".yaml"):
                with open(os.path.join(folder, fn), "r", encoding="utf-8") as f:
                    out.append(yaml.safe_load(f))
        return out

class TEQCoupler:
    def __init__(self, policy_dir: str, jurisdiction: str = "global"):
        self.pack = PolicyPack(os.path.join(policy_dir, jurisdiction))
        self.jurisdiction = jurisdiction

    # ------------- Core gate -------------
    def run(self, task: str, context: Dict[str, Any]) -> GateResult:
        checks = self._checks_for_task(task)
        reasons, remedies = [], []

        for chk in checks:
            ok, reason, remedy = self._run_check(chk, context)
            if not ok:
                reasons.append(reason)
                if remedy:
                    remedies.append(remedy)

        allowed = len(reasons) == 0
        return GateResult(allowed=allowed, reasons=reasons, remedies=remedies, jurisdiction=self.jurisdiction)

    def _checks_for_task(self, task: str) -> List[Dict[str, Any]]:
        tasks = (self.pack.mappings or {}).get("tasks", {})
        generic = tasks.get("_default_", [])
        specific = tasks.get(task, [])
        return [*generic, *specific]

    # ------------- Built-in checks -------------
    def _run_check(self, chk: Dict[str, Any], ctx: Dict[str, Any]) -> Tuple[bool, str, str]:
        kind = chk.get("kind")
        if kind == "require_provenance":
            return self._has_provenance(ctx)
        if kind == "mask_pii":
            return self._mask_pii(ctx, fields=chk.get("fields", []))
        if kind == "content_policy":
            return self._content_policy(ctx, categories=chk.get("categories", []))
        if kind == "budget_limit":
            return self._budget_limit(ctx, max_tokens=chk.get("max_tokens"))
        if kind == "age_gate":
            return self._age_gate(ctx, min_age=chk.get("min_age", 18))
        return True, "", ""  # unknown checks pass (fail-open by design choice here; change to fail-closed if you prefer)

    # -- helpers
    def _has_provenance(self, ctx: Dict[str, Any]) -> Tuple[bool, str, str]:
        prov = ctx.get("provenance", {})
        ok = bool(prov.get("inputs")) and bool(prov.get("sources"))
        return (ok, "Missing provenance (inputs/sources).", "Attach inputs & sources with timestamps & hashes.")

    def _mask_pii(self, ctx: Dict[str, Any], fields: List[str]) -> Tuple[bool, str, str]:
        pii = ctx.get("pii", {})
        masked = ctx.get("pii_masked", False)
        if pii and not masked:
            return (False, "PII present but not masked.", f"Mask fields: {fields or list(pii.keys())} before processing.")
        return (True, "", "")

    def _content_policy(self, ctx: Dict[str, Any], categories: List[str]) -> Tuple[bool, str, str]:
        cats = set(categories or [])
        flagged = set(ctx.get("content_flags", []))
        blocked = cats & flagged
        if blocked:
            return (False, f"Content policy violation: {sorted(blocked)}.", "Route to human review or sanitize content.")
        return (True, "", "")

    def _budget_limit(self, ctx: Dict[str, Any], max_tokens: int | None) -> Tuple[bool, str, str]:
        if max_tokens is None:
            return (True, "", "")
        used = int(ctx.get("tokens_planned", 0))
        if used > max_tokens:
            return (False, f"Budget exceeded: {used}>{max_tokens}.", "Reduce context window or compress input.")
        return (True, "", "")

    def _age_gate(self, ctx: Dict[str, Any], min_age: int) -> Tuple[bool, str, str]:
        age = ctx.get("user_profile", {}).get("age")
        if age is None:
            return (True, "", "")  # unknown; choose your policy
        if age < min_age:
            return (False, f"Age-gate: user_age={age} < {min_age}.", "Block or switch to underage-safe flow.")
        return (True, "", "")

# ------------- CLI -------------
def main():
    ap = argparse.ArgumentParser(description="Lukhas TEQ Coupler")
    ap.add_argument("--policy-root", required=True, help="qi/safety/policy_packs")
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--task", required=True)
    ap.add_argument("--context", help="Path to JSON context", required=True)
    args = ap.parse_args()

    with open(args.context, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    gate = TEQCoupler(args.policy_root, jurisdiction=args.jurisdiction)
    res = gate.run(args.task, ctx)

    print(json.dumps({
        "allowed": res.allowed,
        "reasons": res.reasons,
        "remedies": res.remedies,
        "jurisdiction": res.jurisdiction
    }, indent=2))

if __name__ == "__main__":
    main()
