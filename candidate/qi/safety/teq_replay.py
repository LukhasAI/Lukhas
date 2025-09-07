# path: qi/safety/teq_replay.py
from __future__ import annotations

import argparse

# Use original open (avoids recursion if sandbox is active)
import builtins
import glob
import hashlib
import json
import os
from typing import Any
import streamlit as st
from typing import Optional
from consciousness.qi import qi

_ORIG_OPEN = builtins.open

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECEIPTS_DIR = os.path.join(STATE, "provenance", "exec_receipts")

# Optional deps we may verify with
try:
    from qi.ops.provenance import verify as verify_att  # verifies *.att.json signature

    _HAS_VERIFY = True
except Exception:
    _HAS_VERIFY = False


def _read_json(path: str) -> dict[str, Any]:
    with _ORIG_OPEN(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_receipt(receipt_id: str | None, path: str | None) -> dict[str, Any]:
    if path:
        return _read_json(path)
    if not receipt_id:
        raise FileNotFoundError("Provide --id or --receipt")
    p = os.path.join(RECEIPTS_DIR, f"{receipt_id}.json")
    if not os.path.exists(p):
        # try prefix match
        cand = sorted(glob.glob(os.path.join(RECEIPTS_DIR, f"{receipt_id}*.json")))
        if not cand:
            raise FileNotFoundError(f"Receipt not found: {p}")
        p = cand[0]
    return _read_json(p)


def _policy_fingerprint(policy_root: str, overlays_dir: str | None) -> str:
    """Stable hash over the policy pack + overlays (filenames + contents)."""
    h = hashlib.sha256()

    def add_file(fp: str):
        h.update(fp.encode())
        try:
            with _ORIG_OPEN(fp, "rb") as f:
                h.update(f.read())
        except Exception:
            pass

    for root, _, files in os.walk(policy_root):
        for fn in sorted(files):
            if fn.endswith((".yaml", ".yml", ".json")):
                add_file(os.path.join(root, fn))
    if overlays_dir:
        ov = os.path.join(overlays_dir, "overlays.yaml")
        if os.path.exists(ov):
            add_file(ov)
    return h.hexdigest()


def _verify_attestation_pointer(att: dict[str, Any] | None) -> bool | None:
    if not att or not _HAS_VERIFY:
        return None
    path = att.get("chain_path")
    if not path:
        return None
    attj = path + ".att.json"
    try:
        return bool(verify_att(attj))
    except Exception:
        return False


def _build_teq_context(receipt: dict[str, Any], provenance_record: dict[str, Any] | None) -> dict[str, Any]:
    """Construct a minimal context consistent with your TEQ checks."""
    user_id = None
    for a in receipt.get("agents", []):
        if a.get("role") == "user" and a.get("id", "").startswith("agent:user:"):
            user_id = a["id"].split("agent:user:")[-1]
            break

    ctx = {
        "text": "",  # TEQ rules shouldn't require plaintext here; provenance policy guards that separately
        "pii": {},
        "pii_masked": True,
        "tokens_planned": receipt.get("tokens_out") or 0,
        "user_profile": {"user_id": user_id},
        "provenance": {
            "inputs": ["receipt"],
            "sources": ["internal"],
        },
        # Let require_provenance_record pass with just the SHA:
        "provenance_record_sha": ((provenance_record or {}).get("artifact_sha256") if provenance_record else None),
    }
    return ctx


def _load_provenance_record(artifact_sha: str | None) -> dict[str, Any] | None:
    if not artifact_sha:
        return None
    try:
        from qi.safety.provenance_uploader import load_record_by_sha

        return load_record_by_sha(artifact_sha)
    except Exception:
        return None


def _task_from_receipt(
    receipt: dict[str, Any],
) -> tuple[str, str | None, str | None, str | None]:
    act = receipt.get("activity", {})
    task = act.get("type") or "unknown"
    jurisdiction = act.get("jurisdiction")
    context = act.get("context")
    user = None
    for a in receipt.get("agents", []):
        if a.get("role") == "user" and a.get("id", "").startswith("agent:user:"):
            user = a["id"].split("agent:user:", 1)[-1]
            break
    return task, jurisdiction, context, user


def _run_teq(policy_root: str, jurisdiction: str | None, task: str, ctx: dict[str, Any]) -> dict[str, Any]:
    from qi.safety.teq_gate import TEQCoupler

    teq = TEQCoupler(policy_dir=policy_root, jurisdiction=jurisdiction or "global")
    res = teq.run(task=task, context=ctx)
    # Standardize
    out = {
        "allowed": bool(getattr(res, "allowed", False)),
        "reasons": list(getattr(res, "reasons", [])),
        "checks": getattr(res, "checks", None),
    }
    return out


def _pretty_table(d: dict[str, Any]) -> str:
    allowed = "✅ ALLOWED" if d["replay"]["allowed"] else "❌ BLOCKED"
    lines = [
        "# TEQ Replay",
        f"- Task: `{d['task']}`   Jurisdiction: `{d.get('jurisdiction') or 'global'}`   Context: `{d.get('context'} or '-'}`",
        f"- Receipt ID: `{d['receipt_id']}`   Artifact SHA: `{d.get('artifact_sha'} or '-'}`",
        f"- Receipt attestation: {'✅ verified' if d.get('receipt_attestation_ok') else ('—' if d.get('receipt_attestation_ok') is None else '❌ failed'}",
        f"- Provenance attestation: {'✅ verified' if d.get('provenance_attestation_ok') else ('—' if d.get('provenance_attestation_ok') is None else '❌ failed'}",
        f"- Policy fingerprint: `{d['policy_fingerprint'][:16]}…`",
        "",
        f"**Replay verdict:** {allowed}",
        "",
        "## Reasons",
    ]
    reasons = d["replay"].get("reasons") or []
    if reasons:
        for r in reasons:
            if isinstance(r, dict):
                lines.append(f"- {r.get('kind', '?')}: {r.get('reason', ''}")
            else:
                lines.append(f"- {r}")
    else:
        lines.append("- (none)")
    return "\n".join(lines)


def replay_from_receipt(
    *,
    receipt: dict[str, Any],
    policy_root: str,
    overlays_dir: str | None,
    verify_receipt_attestation: bool = False,
    verify_provenance_attestation: bool = False,
) -> dict[str, Any]:
    task, jurisdiction, context, _user = _task_from_receipt(receipt)

    artifact_sha = (receipt.get("entity") or {}).get("digest_sha256")
    prov = _load_provenance_record(artifact_sha)

    ctx = _build_teq_context(receipt, prov)
    # If we can't load provenance, TEQ's require_provenance_record will fail as expected.
    replay = _run_teq(policy_root, jurisdiction, task, ctx)

    policy_fp = _policy_fingerprint(policy_root, overlays_dir)

    out = {
        "task": task,
        "jurisdiction": jurisdiction,
        "context": context,
        "receipt_id": receipt.get("id"),
        "artifact_sha": artifact_sha,
        "policy_fingerprint": policy_fp,
        "replay": replay,
        "receipt_attestation_ok": (
            _verify_attestation_pointer(receipt.get("attestation")) if verify_receipt_attestation else None
        ),
        "provenance_attestation_ok": (
            _verify_attestation_pointer((prov or {}).get("attestation"))
            if (verify_provenance_attestation and prov)
            else None
        ),
    }
    return out


# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Lukhas TEQ Policy Replay")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--id", help="Receipt ID (from exec_receipts)")
    g.add_argument("--receipt", help="Path to a receipt JSON file")
    ap.add_argument("--policy-root", required=True, help="Path to policy_packs root")
    ap.add_argument("--overlays", help="Path to overlays dir (with overlays.yaml)", default=None)
    ap.add_argument("--verify-att", action="store_true", help="Verify receipt attestation signature")
    ap.add_argument(
        "--verify-prov-att",
        action="store_true",
        help="Verify provenance attestation signature",
    )
    ap.add_argument("--json", action="store_true", help="Output JSON only")
    args = ap.parse_args()

    r = _load_receipt(args.id, args.receipt)
    rep = replay_from_receipt(
        receipt=r,
        policy_root=args.policy_root,
        overlays_dir=args.overlays,
        verify_receipt_attestation=args.verify_att,
        verify_provenance_attestation=args.verify_prov_att,
    )

    if args.json:
        print(json.dumps(rep, indent=2))
        return
    print(_pretty_table(rep))


if __name__ == "__main__":
    main()
