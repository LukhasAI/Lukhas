#!/usr/bin/env python3
"""
Module: generate_badges.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Generate simple SVG badges for manifest and context coverage.

Usage:
  python scripts/generate_badges.py \
    --inventory docs/audits/COMPLETE_MODULE_INVENTORY.json \
    --manifests-root manifests \
    --out docs/audits
"""
import argparse
import json
import pathlib


def badge_svg(label, value, color):
    # ultra-simple badge
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="220" height="20">
  <linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
  <mask id="a"><rect width="220" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#a)">
    <rect width="120" height="20" fill="#555"/>
    <rect x="120" width="100" height="20" fill="{color}"/>
    <rect width="220" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="60" y="14">{label}</text>
    <text x="170" y="14">{value}</text>
  </g>
</svg>
"""

def pct_color(p):
    if p >= 90: return "#4c1"
    if p >= 70: return "#97CA00"
    if p >= 50: return "#dfb317"
    if p >= 30: return "#fe7d37"
    return "#e05d44"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--manifests-root", default="manifests")
    ap.add_argument("--out", default="docs/audits")
    args = ap.parse_args()

    inv = json.load(open(args.inventory, "r", encoding="utf-8"))
    total = int(inv.get("statistics", {}).get("total_modules", len(inv.get("inventory", [])) or 0))
    out_dir = pathlib.Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)

    # Manifest coverage
    manifests = list(pathlib.Path(args.manifests_root).rglob("module.manifest.json"))
    m_pct = round(100.0 * (len(manifests) / max(1, total)), 1)
    (out_dir / "manifest_coverage.svg").write_text(badge_svg("manifests", f"{m_pct}%", pct_color(m_pct)), encoding="utf-8")

    # Context coverage
    contexts = list(pathlib.Path(args.manifests_root).rglob("lukhas_context.md"))
    c_pct = round(100.0 * (len(contexts) / max(1, total)), 1)
    (out_dir / "context_coverage.svg").write_text(badge_svg("context", f"{c_pct}%", pct_color(c_pct)), encoding="utf-8")

    print(f"Badges → {out_dir}/manifest_coverage.svg, {out_dir}/context_coverage.svg")

if __name__ == "__main__":
    main()
