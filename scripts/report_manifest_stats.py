#!/usr/bin/env python3
"""
Compute manifest stats (per star, per tier, context coverage) and export:
- docs/audits/manifest_stats.json
- docs/audits/manifest_stats.md

Usage:
  python scripts/report_manifest_stats.py [--manifests manifests] [--out docs/audits]
"""
import json, pathlib, datetime, collections

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--out", default="docs/audits")
    args = ap.parse_args()

    root = pathlib.Path(".").resolve()
    mroot = (root / args.manifests)
    outdir = (root / args.out); outdir.mkdir(parents=True, exist_ok=True)

    records = []
    total = 0
    stars = collections.Counter()
    tiers = collections.Counter()
    context_yes = 0

    for mf in mroot.rglob("module.manifest.json"):
        total += 1
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        star = (m.get("constellation_alignment", {}) or {}).get("primary_star") or "Supporting"
        tier = (m.get("testing", {}) or {}).get("quality_tier") or "T4_experimental"
        ctx = (mf.parent / "lukhas_context.md").exists()

        stars[star] += 1
        tiers[tier] += 1
        if ctx: context_yes += 1

        records.append({
            "path": str(mf.parent),
            "module": m.get("module", {}).get("name") or m.get("module", {}).get("path"),
            "star": star,
            "tier": tier,
            "has_context": ctx,
            "matriz_nodes": (m.get("matriz_integration", {}) or {}).get("pipeline_nodes", []),
        })

    context_pct = round(100.0 * context_yes / max(1, total), 1)

    data = {
        "generated_at": datetime.datetime.utcnow().isoformat()+"Z",
        "total_manifests": total,
        "by_star": stars,
        "by_tier": tiers,
        "context_coverage_pct": context_pct,
        "sample": records[:30],
    }

    # JSON
    (outdir / "manifest_stats.json").write_text(
        json.dumps(data, indent=2, default=lambda x: dict(x) if isinstance(x, collections.Counter) else x),
        encoding="utf-8"
    )

    # Markdown
    md = []
    md.append(f"# Manifest Stats\n\n_Generated {data['generated_at']}_\n\n")
    md.append(f"- **Total manifests:** {total}\n")
    md.append(f"- **Context coverage:** {context_pct}%\n\n")

    md.append("## By Star\n\n| Star | Count |\n|---|---:|\n")
    for star, cnt in stars.most_common():
        md.append(f"| {star} | {cnt} |\n")

    md.append("\n## By Tier\n\n| Tier | Count |\n|---|---:|\n")
    for tier, cnt in tiers.most_common():
        md.append(f"| {tier} | {cnt} |\n")

    (outdir / "manifest_stats.md").write_text("".join(md), encoding="utf-8")
    print("Wrote docs/audits/manifest_stats.{json,md}")

if __name__ == "__main__":
    main()
