# path: qi/trace/trace_graph.py
from __future__ import annotations

import argparse

# Use original open to avoid sandbox recursion
import builtins
import json
import os
from typing import Any

_ORIG_OPEN = builtins.open

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECEIPTS_DIR = os.path.join(STATE, "provenance", "exec_receipts")


def _read_json(path: str) -> dict[str, Any]:
    with _ORIG_OPEN(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_receipt(receipt_id: str | None = None, receipt_path: str | None = None) -> dict[str, Any]:
    if receipt_path:
        return _read_json(receipt_path)
    if not receipt_id:
        raise FileNotFoundError("Provide --receipt-id or --receipt-path")
    p = os.path.join(RECEIPTS_DIR, f"{receipt_id}.json")
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return _read_json(p)


def _load_prov(artifact_sha: str | None) -> dict[str, Any] | None:
    if not artifact_sha:
        return None
    try:
        from qi.safety.provenance_uploader import load_record_by_sha

        return load_record_by_sha(artifact_sha)
    except Exception:
        return None


def _teq_replay(receipt: dict[str, Any], policy_root: str, overlays_dir: str | None) -> dict[str, Any]:
    from qi.safety.teq_replay import replay_from_receipt

    return replay_from_receipt(
        receipt=receipt,
        policy_root=policy_root,
        overlays_dir=overlays_dir,
        verify_receipt_attestation=False,
        verify_provenance_attestation=False,
    )


def _fmt_ts(ts: float) -> str:
    try:
        import datetime as _dt

        return _dt.datetime.utcfromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%SZ")
    except Exception:
        return str(ts)


def build_dot(
    *,
    receipt: dict[str, Any],
    prov: dict[str, Any] | None,
    replay: dict[str, Any] | None = None,
    link_base: str | None = None,  # e.g., http://127.0.0.1:8095 (receipts API)
    prov_base: str | None = None,  # e.g., http://127.0.0.1:8088 (provenance proxy)
) -> str:
    """
    Returns Graphviz DOT with clickable nodes. Caller can render to SVG/PNG.
    """
    rid = receipt.get("id")
    ent = receipt.get("entity", {}) or {}
    act = receipt.get("activity", {}) or {}
    ags = receipt.get("agents", []) or []

    sha = ent.get("digest_sha256")
    mime = ent.get("mime_type")
    size = ent.get("size_bytes")
    created = receipt.get("created_at")
    task = act.get("type")
    run_id = (act.get("id") or "").replace("activity:run:", "")
    juris = act.get("jurisdiction") or "global"
    ctx = act.get("context") or "-"
    latency = receipt.get("latency_ms")
    tokens_in = receipt.get("tokens_in")
    tokens_out = receipt.get("tokens_out")
    risk_flags = receipt.get("risk_flags") or []
    policy_id = receipt.get("policy_decision_id")
    consent_id = receipt.get("consent_receipt_id")
    leases = receipt.get("capability_lease_ids") or []

    # Click targets
    rec_url = f"{link_base.rstrip('/')}/receipts/{rid}" if (link_base and rid) else None
    prov_url = f"{prov_base.rstrip('/')}/provenance/{sha}/link" if (prov_base and sha) else None

    # Begin DOT
    lines: list[str] = []
    lines.append("digraph lukhas_trace {")
    lines.append("  rankdir=LR;")
    lines.append('  node [shape=box, style="rounded,filled", color="#444444", fillcolor="#F7F9FB", fontname="Inter"];')
    lines.append('  edge [color="#999999"];')

    # Clusters: Activity (run), Entity (artifact), Policy/TEQ, Consent/Cap
    # Activity cluster
    act_label = f"""<<b>Activity</b><br/>
task: <i>{task}</i><br/>
run: {run_id}<br/>
jurisdiction: {juris}<br/>
context: {ctx}<br/>
latency: {latency or '-'} ms | tokens: {tokens_in or 0}→{tokens_out or 0}<br/>
created: {_fmt_ts(created)}
>"""
    lines.append('  subgraph cluster_activity { label="Execution"; color="#DDE7F0";}')
    lines.append(f'    activity [label={act_label}, URL="{rec_url or ""}", target="_blank"];')
    # Agents
    for i, a in enumerate(ags):
        role = a.get("role")
        aid = a.get("id", "")
        label = aid.replace("agent:", "")
        node_name = f"agent{i}"
        node_label = f"<<b>Agent</b><br/>{role}<br/>{label}>"
        lines.append(f'    {node_name} [label={node_label}, shape=component, fillcolor="#EEF6F8"];')
        lines.append(f'    {node_name} -> activity [label="participatedIn", color="#B0C4D9"];')
    lines.append("  }")

    # Entity cluster
    ent_label = f"""<<b>Artifact</b><br/>
sha: <i>{sha or "-"}</i><br/>
mime: {mime or "-"} | size: {size or "-"}<br/>>"""
    lines.append('  subgraph cluster_entity { label="Artifact"; color="#DDE7F0";}')
    if prov_url:
        lines.append(f'    entity [label={ent_label}, URL="{prov_url}", target="_blank", fillcolor="#F3FBF6"];')
    else:
        lines.append(f'    entity [label={ent_label}, fillcolor="#F3FBF6"];')
    lines.append("  }")

    # Policy/TEQ cluster
    verdict = None
    reasons = []
    if replay:
        verdict = "✅ ALLOWED" if replay.get("replay", {}).get("allowed") else "❌ BLOCKED"
        for r in replay.get("replay", {}).get("reasons") or []:
            if isinstance(r, dict):
                reasons.append(f"{r.get('kind','?')}: {r.get('reason','')}")
            else:
                reasons.append(str(r))
    teq_lines = "<br/>".join([verdict or "(no replay)", *list(reasons[:6])])
    pol_label = f"""<<b>TEQ Policy</b><br/>{pol_id_or_dash(policy_id)}<br/>{escape_html(teq_lines)}>"""
    lines.append('  subgraph cluster_policy { label="Policy & Decision"; color="#DDE7F0";}')
    lines.append(f'    teq [label={pol_label}, fillcolor="#FFF8F0"];')
    lines.append("  }")

    # Consent & capabilities cluster
    cc = []
    if consent_id:
        cc.append(f"consent: {consent_id}")
    if leases:
        cc.append(f"leases: {len(leases)}")
    if risk_flags:
        cc.append("risk: " + ", ".join(risk_flags[:4]))
    cc_label = "<br/>".join(cc) or "(none)"
    lines.append('  subgraph cluster_cons { label="Consent & Capabilities"; color="#DDE7F0";}')
    lines.append(f'    cons [label=<<b>Controls</b><br/>{escape_html(cc_label)}>, fillcolor="#F4EFFA"];')
    lines.append("  }")

    # Edges across clusters
    lines.append('  activity -> entity [label="generated", color="#8FBF92"];')
    lines.append('  teq -> activity [label="gated", color="#F0B172"];')
    lines.append('  cons -> teq [label="referenced", color="#C2A4E4"];')

    # Provenance attestation nodes (optional)
    if receipt.get("attestation"):
        lines.append(
            f'  rec_att [label=<<b>Receipt Attestation</b><br/>{escape_html(receipt["attestation"].get("root_hash","")[:16])}...>, shape=note, fillcolor="#EAF7FF"];'
        )
        lines.append('  rec_att -> teq [label="binds", color="#7FB3E6"];')
    if prov and prov.get("attestation"):
        lines.append(
            f'  prov_att [label=<<b>Provenance Attestation</b><br/>{escape_html(prov["attestation"].get("root_hash","")[:16])}...>, shape=note, fillcolor="#EAF7FF"];'
        )
        lines.append('  prov_att -> entity [label="binds", color="#7FB3E6"];')

    lines.append("}")
    return "\n".join(lines)


def pol_id_or_dash(pid: str | None) -> str:
    return f"policy: {pid}" if pid else "policy: -"


def escape_html(s: str | None) -> str:
    if s is None:
        return ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(dot_src: str, out_path: str) -> str:
    try:
        from graphviz import Source  # pip install graphviz (and OS graphviz)
    except Exception as e:
        raise RuntimeError("graphviz python package required: pip install graphviz; also install OS graphviz") from e
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    s = Source(dot_src)
    svg = s.pipe(format="svg")
    with _ORIG_OPEN(out_path, "wb") as f:
        f.write(svg)
    return out_path


# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Lukhas Trace Graph (SVG)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--receipt-id")
    g.add_argument("--receipt-path")
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--overlays", default=None)
    ap.add_argument("--out", default=os.path.join(STATE, "provenance", "exec_receipts", "trace.svg"))
    ap.add_argument("--link-base", help="Receipts API base (for clickable nodes), e.g. http://127.0.0.1:8095")
    ap.add_argument("--prov-base", help="Provenance Proxy base, e.g. http://127.0.0.1:8088")
    args = ap.parse_args()

    r = _load_receipt(args.receipt_id, args.receipt_path)
    prov = _load_prov((r.get("entity") or {}).get("digest_sha256"))
    rep = _teq_replay(r, args.policy_root, args.overlays)

    dot = build_dot(receipt=r, prov=prov, replay=rep, link_base=args.link_base, prov_base=args.prov_base)
    path = render_svg(dot, args.out)
    print(path)


if __name__ == "__main__":
    main()
