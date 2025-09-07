# path: qi/docs/model_safety_card.py
from __future__ import annotations

# Safe I/O
import builtins
import contextlib
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Optional

import streamlit as st

from consciousness.qi import qi

_ORIG_OPEN = builtins.open

# Jurisdiction diff support
try:
    from qi.docs.jurisdiction_diff import compute_overlay_diff
    from qi.risk.orchestrator_overlays import RiskOverlayManager

    _HAS_OVERLAYS = True
except ImportError:
    _HAS_OVERLAYS = False

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECDIR = os.path.join(STATE, "provenance", "exec_receipts")
EVALDIR = os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs")


def _read_json(path: str) -> dict:
    with _ORIG_OPEN(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _latest_eval() -> dict | None:
    import glob
    import os

    files = sorted(
        glob.glob(os.path.join(EVALDIR, "eval_*.json")),
        key=os.path.getmtime,
        reverse=True,
    )
    return _read_json(files[0]) if files else None


def _policy_fingerprint(policy_root: str, overlays_dir: str | None) -> str:
    import os

    h = hashlib.sha256()

    def add(fp):
        h.update(fp.encode())
        with contextlib.suppress(Exception):
            h.update(_ORIG_OPEN(fp, "rb").read())

    for root, _, files in os.walk(policy_root):
        for fn in sorted(files):
            if fn.endswith((".yaml", ".yml", ".json")):
                add(os.path.join(root, fn))
    if overlays_dir:
        ov = os.path.join(overlays_dir, "overlays.yaml")
        if os.path.exists(ov):
            add(ov)
    return h.hexdigest()


@dataclass
class Card:
    model_name: str
    version: str
    generated_at: float
    jurisdictions: list[str]
    policy_fingerprint: str
    eval_summary: dict
    safety_mechanisms: dict
    limitations: list[str]
    intended_use: list[str]
    prohibited_use: list[str]
    contact: str


def generate_card(
    *,
    model_name: str,
    version: str,
    policy_root: str,
    overlays: str | None,
    jurisdictions: list[str],
) -> dict:
    ev = _latest_eval() or {
        "summary": {"weighted_mean": None, "num_failures": None},
        "suite_id": None,
        "id": None,
    }
    card = Card(
        model_name=model_name,
        version=version,
        generated_at=time.time(),
        jurisdictions=jurisdictions,
        policy_fingerprint=_policy_fingerprint(policy_root, overlays),
        eval_summary={
            "suite_id": ev.get("suite_id"),
            "eval_id": ev.get("id"),
            "weighted_mean": (ev.get("summary") or {}).get("weighted_mean"),
            "num_failures": (ev.get("summary") or {}).get("num_failures"),
        },
        safety_mechanisms={
            "TEQ": "Task-specific Enforcement Queue with require_* checks",
            "Consent": "Signed ledger with freshness & field scopes",
            "Capabilities": "Deny-by-default leases (fs/net/api) with audit",
            "Provenance": "Signed Merkle receipts (W3C PROV-ish), Kafka/S3 sinks",
            "C-EVAL": "Continuous evaluation & drift gates",
        },
        limitations=[
            "May underperform on out-of-distribution inputs.",
            "Relies on policy pack coverage; gaps reduce enforcement efficacy.",
            "In-process sandboxing is not a kernel boundary; combine with OS sandboxing for untrusted binaries.",
        ],
        intended_use=[
            "Enterprise assistive workflows with auditable provenance.",
            "Research and analytics with privacy-preserving receipts.",
        ],
        prohibited_use=[
            "High-stakes medical/financial advice without a qualified human in the loop.",
            "Surveillance or privacy-invasive profiling without explicit consent and legal basis.",
        ],
        contact="security@lukhas.example",
    )
    return asdict(card)


def to_markdown(card: dict, *, jurisdiction_diffs: dict | None = None) -> str:
    jdiff = ""
    if jurisdiction_diffs:
        jdiff = "\n##"
    return f"""# Model & Safety Card — {card["model_name"]} (v{card["version"]})

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime(card["generated_at"]))}
**Jurisdictions:** {", ".join(card["jurisdictions"])}
**Policy Fingerprint:** `{card["policy_fingerprint"][:16]}…`

## Evaluation Summary
- Suite: `{card["eval_summary"].get("suite_id")}`
- Eval ID: `{card["eval_summary"].get("eval_id")}`
- Weighted Mean: `{card["eval_summary"].get("weighted_mean")}`
- Failures: `{card["eval_summary"].get("num_failures")}`

## Safety Mechanisms
- TEQ: {card["safety_mechanisms"]["TEQ"]}
- Consent: {card["safety_mechanisms"]["Consent"]}
- Capabilities: {card["safety_mechanisms"]["Capabilities"]}
- Provenance: {card["safety_mechanisms"]["Provenance"]}
- C-EVAL: {card["safety_mechanisms"]["C-EVAL"]}

## Intended Use
- {card["intended_use"][0]}
- {card["intended_use"][1]}

## Prohibited Use
- {card["prohibited_use"][0]}
- {card["prohibited_use"][1]}

## Limitations
- {card["limitations"][0]}
- {card["limitations"][1]}
- {card["limitations"][2]}

## Contact
{card["contact"]}
{jdiff}
"""


# ------------- CLI -------------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Lukhas Model & Safety Card generator")
    ap.add_argument("--model", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--overlays")
    ap.add_argument("--jurisdictions", nargs="+", default=["global", "eu", "us"])
    ap.add_argument(
        "--diff-jurisdictions",
        nargs="*",
        default=[],
        help="Pairs like j1:j2 (repeatable)",
    )
    ap.add_argument("--context", default=None, help="Optional context when diffing overlays")
    ap.add_argument("--out-json", default="ops/cards/model_safety_card.json")
    ap.add_argument("--out-md", default="ops/cards/model_safety_card.md")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)

    card = generate_card(
        model_name=args.model,
        version=args.version,
        policy_root=args.policy_root,
        overlays=args.overlays,
        jurisdictions=args.jurisdictions,
    )
    with _ORIG_OPEN(args.out_json, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)

    # Compute jurisdiction diffs if requested
    jdiff = None
    if args.diff_jurisdictions and _HAS_OVERLAYS:
        try:
            mgr = RiskOverlayManager(args.overlays or "qi/risk")
            jdiff = {}
            for pair in args.diff_jurisdictions:
                if ":" not in pair:
                    continue
                j1, j2 = pair.split(":", 1)
                jdiff[f"{j1}→{j2}"] = compute_overlay_diff(mgr, j1, j2, context=args.context)
        except Exception as e:
            jdiff = {"error": str(e)}

    md = to_markdown(card, jurisdiction_diffs=jdiff)
    with _ORIG_OPEN(args.out_md, "w", encoding="utf-8") as f:
        f.write(md)

    print(json.dumps({"json": args.out_json, "md": args.out_md}, indent=2))


if __name__ == "__main__":
    main()
