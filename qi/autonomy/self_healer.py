# path: qi/autonomy/self_healer.py
from __future__ import annotations

# Safe IO (avoid sandbox recursion)
import builtins
import difflib
import fnmatch
import hashlib
import json
import os
import shutil
import time
from dataclasses import asdict, dataclass
from typing import Any

import yaml
import streamlit as st
from consciousness.qi import qi

_ORIG_OPEN = builtins.open
_ORIG_MAKEDIRS = os.makedirs

GOV_PATH = os.environ.get("LUKHAS_GOV_PATH", "ops/autonomy/governance.yaml")


def _load_governance() -> dict:
    try:
        return yaml.safe_load(_ORIG_OPEN(GOV_PATH, "r", encoding="utf-8")) or {}
    except Exception:
        return {}


STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
QDIR = os.path.join(STATE, "autonomy", "queue")
_ORIG_MAKEDIRS(QDIR, exist_ok=True)
PDIR = os.path.join(STATE, "autonomy", "proposals")
_ORIG_MAKEDIRS(PDIR, exist_ok=True)
ADIR = os.path.join(STATE, "audit")
_ORIG_MAKEDIRS(ADIR, exist_ok=True)

# Attestation hooks (optional)
try:
    from qi.ops.provenance import attest, merkle_chain

    _HAS_ATT = True
except Exception:
    _HAS_ATT = False

# Sandbox
try:
    from qi.ops.cap_sandbox import CapManager, EnvSpec, FsSpec, Sandbox, SandboxPlan

    _HAS_SANDBOX = True
except Exception:
    _HAS_SANDBOX = False

# Receipts
try:
    from qi.provenance.receipts_hub import emit_receipt

    _HAS_RECEIPTS = True
except Exception:
    _HAS_RECEIPTS = False


def _now() -> float:
    return time.time()


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


@dataclass
class ChangeProposal:
    id: str
    ts: float
    author: str  # "system:self-healer"
    risk: str  # "low"|"medium"|"high"
    ttl_sec: int
    kind: str  # e.g., "config_patch", "router_threshold", "eval_weight_adjust"
    target_path: str  # file to patch (for config/threshold kinds)
    current_checksum: str | None
    patch: dict[str, Any]  # structured change (not shell)
    rationale: str
    dry_run_diff: str | None = None
    attestation: dict[str, Any] | None = None


def _read_json(path: str) -> dict[str, Any]:
    with _ORIG_OPEN(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, obj: Any):
    _ORIG_MAKEDIRS(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _file_checksum(path: str) -> str | None:
    try:
        with _ORIG_OPEN(path, "rb") as f:
            import hashlib

            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def _diff(old: str, new: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile="before",
            tofile="after",
        )
    )


def _attest(steps: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not _HAS_ATT:
        return None
    try:
        ch = merkle_chain(steps)
        at = attest(ch, tag="selfheal")
        return {
            "chain_path": at.chain_path,
            "signature_b64": at.signature_b64,
            "public_key_b64": at.public_key_b64,
            "root_hash": at.root_hash,
        }
    except Exception:
        return None


# ---------- Observer & Planner ----------
def observe_signals(
    eval_dir: str = os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs"),
) -> dict[str, Any]:
    """Read latest eval + drift to produce a compact signal summary."""
    try:
        from pathlib import Path

        files = sorted(Path(eval_dir).glob("eval_*.json"), key=os.path.getmtime, reverse=True)
        latest = _read_json(str(files[0])) if files else None
    except Exception:
        latest = None
    sig = {
        "t": _now(),
        "eval_weighted_mean": (latest or {}).get("summary", {}).get("weighted_mean"),
        "eval_failures": (latest or {}).get("summary", {}).get("num_failures"),
        "suite_id": (latest or {}).get("suite_id"),
        "eval_id": (latest or {}).get("id"),
    }
    _audit("observe", sig)
    return sig


def _path_allowed(path: str, allowed: list[str] | None, denied: list[str] | None) -> bool:
    ap = os.path.abspath(path)
    if denied:
        for patt in denied:
            if fnmatch.fnmatch(ap, os.path.abspath(patt).replace("\\", "/")):
                return False
    if not allowed:
        return True
    return any(fnmatch.fnmatch(ap, os.path.abspath(patt).replace("\\", "/")) for patt in allowed)


def plan_proposals(signals: dict[str, Any], *, config_targets: list[str]) -> list[ChangeProposal]:
    """Heuristic planner: if mean below SLA or failures >0, propose gentle nudges."""
    gov = _load_governance()
    rule = gov.get("change_kinds", {}).get("config_patch") or {}
    allowed = rule.get("allowed_paths")
    denied = rule.get("deny_paths")
    ttl = int(rule.get("ttl_sec", 3600))
    risk_class = str(rule.get("risk", "medium"))

    props: list[ChangeProposal] = []
    mean = signals.get("eval_weighted_mean") or 1.0
    fails = signals.get("eval_failures") or 0
    signals.get("suite_id") or "unknown"

    if mean < 0.85 or fails > 0:
        # Example: propose to slightly increase safety threshold or adjust eval weights
        target = config_targets[0] if config_targets else "qi/safety/policy_packs/global/mappings.yaml"
        if not _path_allowed(target, allowed, denied):
            _audit("proposal_denied_by_governance", {"target": target})
            return props

        cur_sum = _file_checksum(target)
        patch = {"router": {"task_specific": {"risk_bias": min(1.0, 0.1 + max(0, (0.85 - mean)))}}}
        rationale = f"Weighted mean {mean:.3f}, failures {fails}; propose biasing safer routes slightly."
        pid = _sha({"target": target, "patch": patch, "t": int(_now())})
        prop = ChangeProposal(
            id=pid,
            ts=_now(),
            author="system:self-healer",
            risk=risk_class,
            ttl_sec=ttl,
            kind="config_patch",
            target_path=target,
            current_checksum=cur_sum,
            patch=patch,
            rationale=rationale,
        )
        # produce dry-run diff
        try:
            old = _ORIG_OPEN(target, "r", encoding="utf-8").read()
            try:
                import yaml

                loaded = yaml.safe_load(old) or {}
                # naive merge
                from copy import deepcopy

                def deep_merge(a, b):
                    if isinstance(a, dict) and isinstance(b, dict):
                        out = deepcopy(a)
                        for k, v in b.items():
                            out[k] = deep_merge(out.get(k), v)
                        return out
                    return b if b is not None else a

                new = yaml.safe_dump(deep_merge(loaded, patch), sort_keys=False)
                prop.dry_run_diff = _diff(old, new)
            except Exception:
                # fallback to JSON
                loaded = json.loads(old) if old.strip() else {}
                from copy import deepcopy

                def deep_merge(a, b):
                    if isinstance(a, dict) and isinstance(b, dict):
                        out = deepcopy(a)
                        for k, v in b.items():
                            out[k] = deep_merge(out.get(k), v)
                        return out
                    return b if b is not None else a

                new = json.dumps(deep_merge(loaded, patch), indent=2)
                prop.dry_run_diff = _diff(old, new)
        except Exception:
            prop.dry_run_diff = None

        # attestation
        prop.attestation = _attest(
            [
                {"phase": "plan", "signals": signals},
                {"phase": "patch", "target": target, "patch": patch},
            ]
        )
        props.append(prop)

    for p in props:
        _queue_proposal(p)
    return props


# ---------- Queue & Audit ----------
def _queue_proposal(p: ChangeProposal):
    qpath = os.path.join(QDIR, f"{p.id}.json")
    _write_json(qpath, asdict(p))
    _audit("proposal_queued", {"id": p.id, "target": p.target_path, "risk": p.risk})


def _audit(kind: str, rec: dict[str, Any]):
    try:
        with _ORIG_OPEN(os.path.join(ADIR, "selfheal.jsonl"), "a", encoding="utf-8") as f:
            rec = {"ts": _now(), "kind": kind, **rec}
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


# ---------- Approval & Apply ----------
def list_proposals() -> list[dict[str, Any]]:
    out = []
    for fn in sorted(os.listdir(QDIR)):
        if not fn.endswith(".json"):
            continue
        try:
            out.append(_read_json(os.path.join(QDIR, fn)))
        except Exception:
            continue
    return out


def _required_reviewers(kind: str) -> int:
    gov = _load_governance()
    return int(gov.get("change_kinds", {}).get(kind, {}).get("reviewers_required", 1))


def approve(proposal_id: str, approver: str, reason: str = "") -> dict[str, Any]:
    p = _read_json(os.path.join(QDIR, f"{proposal_id}.json"))
    ap_path = os.path.join(PDIR, f"{proposal_id}.approval.json")
    approvals = {
        "status": "pending",
        "approvers": [],
        "ts": _now(),
        "kind": p.get("kind"),
    }
    if os.path.exists(ap_path):
        approvals = _read_json(ap_path)
    if approver in approvals.get("approvers", []):
        return approvals  # idempotent
    approvals.setdefault("approvers", []).append(approver)
    need = _required_reviewers(p.get("kind", "config_patch"))
    approvals["status"] = "approved" if len(approvals["approvers"]) >= need else "pending"
    _write_json(ap_path, approvals)
    _audit(
        "proposal_approved",
        {"id": proposal_id, "approver": approver, "status": approvals["status"]},
    )
    return approvals


def reject(proposal_id: str, approver: str, reason: str = "") -> dict[str, Any]:
    _read_json(os.path.join(QDIR, f"{proposal_id}.json"))
    ack = {
        "id": proposal_id,
        "status": "rejected",
        "approver": approver,
        "reason": reason,
        "ts": _now(),
    }
    _write_json(os.path.join(PDIR, f"{proposal_id}.approval.json"), ack)
    _audit("proposal_rejected", {"id": proposal_id, "approver": approver})
    return ack


def _approved(proposal_id: str) -> bool:
    ap = os.path.join(PDIR, f"{proposal_id}.approval.json")
    if not os.path.exists(ap):
        return False
    j = _read_json(ap)
    need = _required_reviewers(j.get("kind", "config_patch"))
    return j.get("status") == "approved" and len(j.get("approvers", [])) >= need


def apply(proposal_id: str, subject_user: str = "system") -> dict[str, Any]:
    """
    Apply only if approved and within TTL. Uses sandbox w/ FS caps for target_path.
    """
    p = _read_json(os.path.join(QDIR, f"{proposal_id}.json"))
    if not _approved(proposal_id):
        raise RuntimeError("proposal not approved")
    if _now() - float(p["ts"]) > float(p.get("ttl_sec", 0)):
        raise RuntimeError("proposal expired")

    target = p["target_path"]
    backup = target + f".bak.{int(_now())}"

    # Re-check governance before applying
    gov = _load_governance()
    rule = gov.get("change_kinds", {}).get(p.get("kind", "config_patch")) or {}
    if not _path_allowed(target, rule.get("allowed_paths"), rule.get("deny_paths")):
        raise RuntimeError("governance denies writes to target path")

    if _HAS_SANDBOX:
        mgr = CapManager()
        # require fs write lease for target dir
        mgr.grant(
            subject=f"user:{subject_user}",
            caps=[
                f"fs:write:{os.path.abspath(target)}",
                f"fs:read:{os.path.abspath(target)}",
            ],
            ttl_sec=600,
        )

        plan = SandboxPlan(
            subject=f"user:{subject_user}",
            env=EnvSpec(allow=["PATH", "HOME"], inject={}),
            fs=FsSpec(read=[target, backup], write=[target, backup]),
            require=[f"fs:write:{target}"],
            meta={"proposal": proposal_id},
        )
        sb = Sandbox(mgr)

        # Apply patch: naive deep merge for JSON/YAML files
        with sb.activate(plan):
            _apply_patch(target, backup, p["patch"])
    else:
        # Fallback without sandbox
        _apply_patch(target, backup, p["patch"])

    # Emit an execution receipt for the change
    if _HAS_RECEIPTS:
        try:
            rec = emit_receipt(
                artifact_sha=_sha({"proposal": proposal_id, "target": target}),
                artifact_mime="application/json",
                artifact_size=len(open(target, "rb").read()),
                storage_url=f"file://{os.path.abspath(target)}",
                run_id=f"selfheal-{proposal_id}",
                task="self_heal_apply",
                started_at=p["ts"],
                ended_at=_now(),
                user_id=subject_user,
                jurisdiction="ops",
                context="config_change",
                policy_decision_id=None,
                consent_receipt_id=None,
                capability_lease_ids=[],
                risk_flags=["config_change"],
                tokens_in=0,
                tokens_out=0,
            )
            receipt_id = rec["id"]
        except Exception:
            receipt_id = None
    else:
        receipt_id = None

    _audit("proposal_applied", {"id": proposal_id, "target": target, "backup": backup})
    return {
        "ok": True,
        "proposal": proposal_id,
        "backup": backup,
        "receipt_id": receipt_id,
    }


def _apply_patch(target: str, backup: str, patch: dict[str, Any]):
    """Apply configuration patch with backup and rollback."""
    try:
        old = _ORIG_OPEN(target, "r", encoding="utf-8").read()
        try:
            import yaml

            data = yaml.safe_load(old)
        except Exception:
            data = json.loads(old) if old.strip() else {}

        from copy import deepcopy

        def deep_merge(a, b):
            if isinstance(a, dict) and isinstance(b, dict):
                out = deepcopy(a)
                for k, v in b.items():
                    out[k] = deep_merge(out.get(k), v)
                return out
            return b if b is not None else a

        new_data = deep_merge(data, patch)

        # backup then write
        shutil.copyfile(target, backup)
        try:
            if target.endswith((".yaml", ".yml")):
                import yaml

                txt = yaml.safe_dump(new_data, sort_keys=False)
            else:
                txt = json.dumps(new_data, indent=2)
            with _ORIG_OPEN(target, "w", encoding="utf-8") as f:
                f.write(txt)
        except Exception:
            # rollback
            shutil.copyfile(backup, target)
            raise
    except Exception as e:
        raise RuntimeError(f"Failed to apply patch: {e}")


# ---------- CLI ----------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Lukhas Self-Healer (propose/approve/apply)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("observe")
    s1.add_argument("--eval-dir", default=os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs"))

    s2 = sub.add_parser("plan")
    s2.add_argument("--targets", nargs="+", default=["qi/safety/policy_packs/global/mappings.yaml"])

    sub.add_parser("list")

    s4 = sub.add_parser("approve")
    s4.add_argument("--id", required=True)
    s4.add_argument("--by", required=True)
    s4.add_argument("--reason", default="")

    s5 = sub.add_parser("reject")
    s5.add_argument("--id", required=True)
    s5.add_argument("--by", required=True)
    s5.add_argument("--reason", default="")

    s6 = sub.add_parser("apply")
    s6.add_argument("--id", required=True)
    s6.add_argument("--as-user", default="ops")

    args = ap.parse_args()
    if args.cmd == "observe":
        print(json.dumps(observe_signals(args.eval_dir), indent=2))
        return
    if args.cmd == "plan":
        sig = observe_signals()
        props = plan_proposals(sig, config_targets=args.targets)
        print(json.dumps([asdict(p) for p in props], indent=2))
        return
    if args.cmd == "list":
        print(json.dumps(list_proposals(), indent=2))
        return
    if args.cmd == "approve":
        print(json.dumps(approve(args.id, args.by, args.reason), indent=2))
        return
    if args.cmd == "reject":
        print(json.dumps(reject(args.id, args.by, args.reason), indent=2))
        return
    if args.cmd == "apply":
        print(json.dumps(apply(args.id, args.as_user), indent=2))
        return


if __name__ == "__main__":
    main()