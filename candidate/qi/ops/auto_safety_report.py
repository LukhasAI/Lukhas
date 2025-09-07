# path: qi/ops/auto_safety_report.py
from __future__ import annotations

# Safe I/O
import builtins
import contextlib
import glob
import hashlib
import json
import os
import statistics
import time
import streamlit as st
from consciousness.qi import qi

_ORIG_OPEN = builtins.open

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECDIR = os.path.join(STATE, "provenance", "exec_receipts")
EVALDIR = os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs")
OUTDIR = os.environ.get("LUKHAS_REPORT_DIR", "ops/reports")
os.makedirs(OUTDIR, exist_ok=True)


def _read_json(path: str) -> dict:
    with _ORIG_OPEN(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _latest_eval() -> dict | None:
    files = sorted(glob.glob(os.path.join(EVALDIR, "eval_*.json")), key=os.path.getmtime, reverse=True)
    return _read_json(files[0]) if files else None


def _recent_receipts(n: int = 500) -> list[dict]:
    paths = sorted(glob.glob(os.path.join(RECDIR, "*.json")), key=os.path.getmtime, reverse=True)[:n]
    out = []
    for p in paths:
        with contextlib.suppress(Exception):
            out.append(_read_json(p))
    return out


def _policy_fingerprint(policy_root: str, overlays: str | None) -> str:
    h = hashlib.sha256()

    def add(fp):
        h.update(fp.encode())
        with contextlib.suppress(Exception):
            h.update(_ORIG_OPEN(fp, "rb").read())

    for root, _, files in os.walk(policy_root):
        for fn in sorted(files):
            if fn.endswith((".yaml", ".yml", ".json")):
                add(os.path.join(root, fn))
    if overlays:
        ov = os.path.join(overlays, "overlays.yaml")
        if os.path.exists(ov):
            add(ov)
    return h.hexdigest()


def _mk_markdown(policy_root: str, overlays: str | None, window: int) -> str:
    now = time.gmtime()
    ts = time.strftime("%Y-%m-%d %H:%M:%SZ", now)
    ev = _latest_eval()
    recs = _recent_receipts(window)
    # volume & risk stats
    total = len(recs)
    by_task = {}
    risk_counts = {}
    lats = []
    for r in recs:
        t = (r.get("activity") or {}).get("type") or "unknown"
        by_task[t] = by_task.get(t, 0) + 1
        for rf in r.get("risk_flags", []) or []:
            risk_counts[rf] = risk_counts.get(rf, 0) + 1
        if r.get("latency_ms") is not None:
            lats.append(r["latency_ms"])
    lat_p50 = int(statistics.median(lats)) if lats else None
    lat_p95 = int(sorted(lats)[int(0.95 * len(lats)) - 1]) if lats else None

    md = []
    md.append("# Nightly Safety Report")
    md.append(f"**Generated:** {ts}")
    md.append(f"**Policy Fingerprint:** `{_policy_fingerprint(policy_root, overlays}[:16]}…`")
    md.append("")
    md.append("## Evaluation")
    if ev:
        md.append(f"- Suite: `{ev.get('suite_id'}`")
        md.append(f"- Eval ID: `{ev.get('id'}`")
        md.append(f"- Weighted Mean: **{(ev.get('summary'} or {}).get('weighted_mean')}**")
        md.append(f"- Failures: **{(ev.get('summary'} or {}).get('num_failures')}**")
    else:
        md.append("- No eval runs found.")
    md.append("")
    md.append("## Receipts")
    md.append(f"- Total receipts: **{total}**")
    md.append(f"- Median latency: **{lat_p50 if lat_p50 is not None else '—'} ms**")
    md.append(f"- p95 latency: **{lat_p95 if lat_p95 is not None else '—'} ms**")
    if by_task:
        md.append("- By task:")
        for k, v in sorted(by_task.items(), key=lambda x: -x[1])[:12]:
            md.append(f"  - `{k}`: {v}")
    if risk_counts:
        md.append("- Risk flags:")
        for k, v in sorted(risk_counts.items(), key=lambda x: -x[1])[:12]:
            md.append(f"  - `{k}`: {v}")
    md.append("")
    md.append("> Note: receipt content is privacy-minimized (hashes only). See trace drill-down for details.")
    return "\n".join(md)


def _write(path: str, txt: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _ORIG_OPEN(path, "w", encoding="utf-8") as f:
        f.write(txt)


def _post_slack(markdown: str) -> str | None:
    url = os.environ.get("SLACK_WEBHOOK_URL")
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL", "#lukhas-safety")
    title = os.environ.get("SLACK_TITLE", "LUKHΛS Nightly Safety Report")
    if url:
        import json as _json
        import urllib.request

        req = urllib.request.Request(
            url,
            method="POST",
            data=_json.dumps({"text": f"*{title}*\n{markdown}"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return f"webhook {resp.status}"
    if bot_token:
        try:
            from slack_sdk import WebClient  # pip install slack_sdk
        except Exception:
            return None
        client = WebClient(token=bot_token)
        client.chat_postMessage(channel=channel, text=f"*{title}*\n{markdown}")
        return "bot ok"
    return None


def generate_report(policy_root: str, overlays: str | None, window: int = 500) -> str:
    md = _mk_markdown(policy_root, overlays, window)
    fname = f"safety_report_{time.strftime('%Y%m%d'}.md"
    path = os.path.join(OUTDIR, fname)
    _write(path, md)
    _post_slack(md)
    return path


# ------------- CLI -------------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Nightly Auto-Safety Report")
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--overlays")
    ap.add_argument("--window", type=int, default=500)
    args = ap.parse_args()
    p = generate_report(args.policy_root, args.overlays, args.window)
    print(json.dumps({"report": p}, indent=2))


if __name__ == "__main__":
    main()
