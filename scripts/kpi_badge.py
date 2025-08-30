#!/usr/bin/env python3
"""
Generate a simple SVG badge from backup KPI JSON.

Usage:
  python scripts/kpi_badge.py --in out/backup_kpi.json --out badges/backup_status.svg

Status logic:
  - green  = weekly.ok and monthly.ok
  - amber  = at least one of weekly.ok or monthly.ok is true (but not both)
  - red    = neither weekly nor monthly ok
If quarterly present and ok is false, downgrade one level (green->amber, amber->red).
"""

import argparse
import json
from pathlib import Path


def load_json(p: str) -> dict:
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def pick_status(kpi: dict) -> tuple[str, str]:
    w_ok = bool((kpi.get("weekly") or {}).get("ok"))
    m_ok = bool((kpi.get("monthly") or {}).get("ok"))
    q = kpi.get("quarterly") or {}
    q_present = bool(q.get("present"))
    q_ok = bool(q.get("ok"))

    # base from weekly/monthly
    if w_ok and m_ok:
        status = "green"
        label = "DR OK"
    elif w_ok or m_ok:
        status = "amber"
        label = "DR PARTIAL"
    else:
        status = "red"
        label = "DR FAIL"

    # downgrade for quarterly failure when present
    if q_present and not q_ok:
        if status == "green":
            status, label = "amber", "DR ATTENTION"
        elif status == "amber":
            status, label = "red", "DR FAIL"

    return status, label


def color_for(status: str) -> tuple[str, str]:
    if status == "green":
        return ("#2e7d32", "#ffffff")
    if status == "amber":
        return ("#f9a825", "#000000")
    if status == "red":
        return ("#c62828", "#ffffff")
    return ("#9e9e9e", "#ffffff")


def render_svg(label: str, status: str) -> str:
    bg, fg = color_for(status)
    # simple width calc: base + 8px per char
    w = max(120, 20 + len(label) * 8)
    h = 24
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' role='img' aria-label='{label}'>"
        f"<rect rx='4' width='{w}' height='{h}' fill='{bg}'/>"
        f"<g fill='{fg}' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Inter,sans-serif' font-size='12'>"
        f"<text x='{w / 2:.0f}' y='16' text-anchor='middle'>{label}</text>"
        f"</g></svg>"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    args = ap.parse_args()

    kpi = load_json(args.inp)
    status, label = pick_status(kpi)
    svg = render_svg(label, status)

    out_path = Path(args.outp)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    print(json.dumps({"ok": True, "status": status, "label": label, "out": str(out_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
