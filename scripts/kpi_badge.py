#!/usr/bin/env python3
import json
import argparse
import sys

def color(ok):
    """Return appropriate color for badge status"""
    return "#2e7d32" if ok else "#c62828"

def verdict(k):
    """Determine overall KPI status from weekly/monthly/quarterly results"""
    # ok if weekly & monthly ok, and quarterly ok or skipped (treated as ok)
    w = k.get("weekly", {}).get("ok") is True
    m = k.get("monthly", {}).get("ok") is True
    q = k.get("quarterly", {})
    q_ok = q.get("ok") is True
    res = w and m and q_ok
    label = "backup"
    msg = "green" if res else "attention"
    return res, label, msg

def svg(label, msg, good):
    """Generate SVG badge with label and status message"""
    l, r = label, msg
    # rough sizes
    lw = 6 * len(l) + 20
    rw = 6 * len(r) + 20
    tw = lw + rw
    lc = "#555"
    rc = color(good)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="20" role="img" aria-label="{l}: {r}">
<linearGradient id="s" x2="0" y2="100%">
  <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
  <stop offset="1" stop-opacity=".1"/>
</linearGradient>
<mask id="m"><rect width="{tw}" height="20" rx="3" fill="#fff"/></mask>
<g mask="url(#m)">
  <rect width="{lw}" height="20" fill="{lc}"/>
  <rect x="{lw}" width="{rw}" height="20" fill="{rc}"/>
  <rect width="{tw}" height="20" fill="url(#s)"/>
</g>
<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
  <text x="{lw/2}" y="14">{l}</text>
  <text x="{lw + rw/2}" y="14">{r}</text>
</g>
</svg>'''

def main():
    ap = argparse.ArgumentParser(description="Generate KPI badge from backup results")
    ap.add_argument("--in", dest="inp", required=True, help="Input KPI JSON file")
    ap.add_argument("--out", dest="outp", required=True, help="Output SVG badge file")
    args = ap.parse_args()
    
    with open(args.inp, "r", encoding="utf-8") as f:
        kpi = json.load(f)
    
    ok, label, msg = verdict(kpi)
    
    with open(args.outp, "w", encoding="utf-8") as f:
        f.write(svg(label, msg, ok))
    
    print(json.dumps({"ok": True, "badge_ok": ok, "out": args.outp}))

if __name__ == "__main__":
    sys.exit(main())