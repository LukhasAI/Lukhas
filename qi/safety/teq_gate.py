from __future__ import annotations
import argparse, os, json, glob, time, sys
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import yaml
try:
    from .pii import detect_pii, mask_pii
except ImportError:
    from pii import detect_pii, mask_pii

# Optional consent integration
try:
    from qi.memory.consent_guard import ConsentGuard, require_consent
    CONSENT_AVAILABLE = True
except ImportError:
    CONSENT_AVAILABLE = False

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
    def __init__(self, policy_dir: str, jurisdiction: str = "global", consent_storage: str | None = None):
        self.pack = PolicyPack(os.path.join(policy_dir, jurisdiction))
        self.jurisdiction = jurisdiction
        self.consent_guard = None
        if CONSENT_AVAILABLE and consent_storage:
            self.consent_guard = ConsentGuard(consent_storage)

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
        if kind == "require_consent":
            return self._require_consent(ctx, purpose=chk.get("purpose", "data_processing"))
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
        # AUTO-PII: opportunistically scan text to set pii flags
        txt = ctx.get("text") or ctx.get("input_text") or ""
        if txt:
            hits = detect_pii(txt)
            if hits:
                ctx.setdefault("pii", {})
                ctx["pii"]["_auto_hits"] = [{"kind": h.kind, "value": h.value, "span": h.span} for h in hits]
                if not ctx.get("pii_masked"):
                    return (False, "PII detected in content but not masked.", "Call mask_pii() or set pii_masked=true.")
        cats = set(categories or [])
        flagged = set(ctx.get("content_flags", []))
        blocked = cats & flagged
        if blocked:
            return (False, f"Content policy violation: {sorted(blocked)}.", "Route to human review or sanitize content.")
        return (True, "", "")

    def _budget_limit(self, ctx: Dict[str, Any], max_tokens: int | None) -> Tuple[bool, str, str]:
        # AUTO-BUDGET: if no tokens_planned, estimate via Budgeter (best-effort)
        if max_tokens is None:
            return (True, "", "")
        used = int(ctx.get("tokens_planned", -1))
        if used < 0:
            try:
                from qi.ops.budgeter import Budgeter
                text = ctx.get("text") or ctx.get("input_text") or ""
                plan = Budgeter().plan(text=text)
                used = int(plan.get("tokens_planned", 0))
                ctx["tokens_planned"] = used
            except Exception:
                used = 0
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
    
    def _require_consent(self, ctx: Dict[str, Any], purpose: str) -> Tuple[bool, str, str]:
        """Check if user has valid consent for the specified purpose"""
        if not self.consent_guard:
            # No consent system configured, pass through
            return (True, "", "")
        
        user_id = ctx.get("user_id") or ctx.get("user_profile", {}).get("id")
        if not user_id:
            return (False, "No user_id found in context", "Add user_id to context")
        
        allowed, reason = require_consent(self.consent_guard, user_id, purpose)
        if allowed:
            return (True, "", "")
        else:
            return (False, f"Consent required: {reason}", f"Request consent for purpose: {purpose}")

# ------------- CLI -------------
def main():
    ap = argparse.ArgumentParser(description="Lukhas TEQ Coupler")
    ap.add_argument("--policy-root", required=True, help="qi/safety/policy_packs")
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--task")
    ap.add_argument("--context", help="Path to JSON context")
    ap.add_argument("--run-tests", action="store_true", help="Run policy-pack tests and exit")
    ap.add_argument("--consent-storage", help="Path to consent ledger (enables consent checks)")
    args = ap.parse_args()

    gate = TEQCoupler(args.policy_root, jurisdiction=args.jurisdiction, consent_storage=args.consent_storage)

    # Test runner mode
    if args.run_tests:
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
        sys.exit(0 if summary["passed"] == summary["total"] else 1)

    # Single-run mode
    if not args.task or not args.context:
        raise SystemExit("Provide --task and --context, or use --run-tests.")

    with open(args.context, "r", encoding="utf-8") as f:
        ctx = json.load(f)
    res = gate.run(args.task, ctx)
    print(json.dumps({
        "allowed": res.allowed,
        "reasons": res.reasons,
        "remedies": res.remedies,
        "jurisdiction": res.jurisdiction
    }, indent=2))


if __name__ == "__main__":
    main()
