#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
QI="$ROOT/qi"

mkdir -p "$QI/safety"

# --- New: qi/safety/pii.py ---
cat > "$QI/safety/pii.py" <<'PY'
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable

@dataclass
class PIIHit:
    kind: str
    value: str
    span: Tuple[int, int]

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE = re.compile(r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6})")
_IPv4  = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b")
_IPv6  = re.compile(r"\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b")
_SSN   = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")  # US-style; customize per jurisdiction
_CC    = re.compile(r"\b(?:\d[ -]*?){13,19}\b")  # candidate; will Luhn-check

_NAME_HINT = re.compile(r"\b(Name|Full Name|First Name|Last Name)\b:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)")

def _luhn(cc: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", cc)]
    if len(digits) < 13: return False
    total = 0
    odd = True
    for d in reversed(digits):
        if odd:
            total += d
        else:
            k = d * 2
            total += k - 9 if k > 9 else k
        odd = not odd
    return total % 10 == 0

def detect_pii(text: str) -> List[PIIHit]:
    hits: List[PIIHit] = []
    for m in _EMAIL.finditer(text):
        hits.append(PIIHit("email", m.group(0), (m.start(), m.end())))
    for m in _PHONE.finditer(text):
        val = m.group(0)
        if len(re.sub(r"\D","", val)) >= 7:
            hits.append(PIIHit("phone", val, (m.start(), m.end())))
    for m in _IPv4.finditer(text):
        hits.append(PIIHit("ip_v4", m.group(0), (m.start(), m.end())))
    for m in _IPv6.finditer(text):
        hits.append(PIIHit("ip_v6", m.group(0), (m.start(), m.end())))
    for m in _SSN.finditer(text):
        hits.append(PIIHit("ssn_like", m.group(0), (m.start(), m.end())))
    for m in _CC.finditer(text):
        cc = m.group(0)
        if _luhn(cc):
            hits.append(PIIHit("credit_card", cc, (m.start(), m.end())))
    for m in _NAME_HINT.finditer(text):
        hits.append(PIIHit("name_hint", m.group(2), (m.start(2), m.end(2))))
    return hits

def mask_pii(text: str, hits: Iterable[PIIHit], strategy: str = "hash") -> str:
    masked = text
    # replace from end to keep spans valid
    for h in sorted(hits, key=lambda x: x.span[0], reverse=True):
        replacement = f"[{h.kind.upper()}]"
        masked = masked[:h.span[0]] + replacement + masked[h.span[1]:]
    return masked
PY

# --- Update: qi/safety/teq_gate.py (adds PII detection + test runner) ---
python3 - <<'PY'
import io, os, sys, re
p = "/Users/agi_dev/LOCAL-REPOS/Lukhas/qi/safety/teq_gate.py"
src = open(p, "r", encoding="utf-8").read()

# Inject imports and new CLI options; add PII detection step and test runner
src = src.replace(
    'import argparse, os, json',
    'import argparse, os, json, glob, time, sys'
)

# Check if pii import already exists
if 'from .pii import' not in src:
    src = src.replace(
        'import yaml',
        'import yaml\ntry:\n    from .pii import detect_pii, mask_pii\nexcept ImportError:\n    from pii import detect_pii, mask_pii'
    )

# Add a helper to auto-detect PII in context["text"] if present
if "_content_policy(self, ctx: Dict[str, Any], categories: List[str]) -> Tuple[bool, str, str]:" in src and "AUTO-PII" not in src:
    src = src.replace(
        'def _content_policy(self, ctx: Dict[str, Any], categories: List[str]) -> Tuple[bool, str, str]:',
        '''def _content_policy(self, ctx: Dict[str, Any], categories: List[str]) -> Tuple[bool, str, str]:
        # AUTO-PII: opportunistically scan text to set pii flags
        txt = ctx.get("text") or ctx.get("input_text") or ""
        if txt:
            hits = detect_pii(txt)
            if hits:
                ctx.setdefault("pii", {})
                ctx["pii"]["_auto_hits"] = [{"kind": h.kind, "value": h.value, "span": h.span} for h in hits]
                if not ctx.get("pii_masked"):
                    return (False, "PII detected in content but not masked.", "Call mask_pii() or set pii_masked=true.")'''
    )

# Extend CLI: --run-tests to execute all tests in policy pack
if 'ap.add_argument("--task", required=True)' in src:
    src = src.replace(
        'ap.add_argument("--task", required=True)',
        'ap.add_argument("--task")'
    )

if 'ap.add_argument("--context", help="Path to JSON context", required=True)' in src:
    src = src.replace(
        'ap.add_argument("--context", help="Path to JSON context", required=True)',
        'ap.add_argument("--context", help="Path to JSON context")\n    ap.add_argument("--run-tests", action="store_true", help="Run policy-pack tests and exit")'
    )

# Replace main() to support tests
main_start = src.find("def main():")
main_end = src.find('\nif __name__ == "__main__":')
if main_start != -1 and main_end != -1:
    new_main = '''def main():
    ap = argparse.ArgumentParser(description="Lukhas TEQ Coupler")
    ap.add_argument("--policy-root", required=True, help="qi/safety/policy_packs")
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--task")
    ap.add_argument("--context", help="Path to JSON context")
    ap.add_argument("--run-tests", action="store_true", help="Run policy-pack tests and exit")
    args = ap.parse_args()

    gate = TEQCoupler(args.policy_root, jurisdiction=args.jurisdiction)

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
'''
    src = src[:main_start] + new_main + '\n' + src[main_end:]

open(p, "w", encoding="utf-8").write(src)
print("Patched:", p)
PY

# --- New: qi/safety/policy_test.py (optional direct runner) ---
cat > "$QI/safety/policy_test.py" <<'PY'
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
PY

echo "✅ TEQ+PII patch applied."