#!/usr/bin/env python3
"""
Generate docs/CONSTELLATION_TOP.md + per-star pages from manifests.

Inputs:
  - scripts/top_config.json
  - scripts/star_canon.json
  - manifests/**/module.manifest.json

Outputs:
  - docs/CONSTELLATION_TOP.md
  - docs/stars/<star_slug>.md
"""
import datetime
import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "manifests"
DOCS = ROOT / "docs"
STARS_DIR = DOCS / "stars"
CONFIG = pathlib.Path(__file__).resolve().parent / "top_config.json"
CANON = pathlib.Path(__file__).resolve().parent / "star_canon.json"

def slug(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s.lower()

def load_manifests():
    for f in MANIFESTS.rglob("module.manifest.json"):
        try:
            yield f, json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue

def main():
    conf = json.loads(CONFIG.read_text(encoding="utf-8"))
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    order = conf.get("stars_order", canon.get("stars", []))
    stars_set = set(canon.get("stars", []))

    # Aggregate
    per_star = defaultdict(list)
    total = 0
    for path, m in load_manifests():
        total += 1
        star = (m.get("constellation_alignment", {}).get("primary_star")
                or "Supporting")
        if star not in stars_set and star != "Supporting":
            # normalize via aliases
            star = canon.get("aliases", {}).get(star, star)
        tier = m.get("testing", {}).get("quality_tier", "T4_experimental")
        fqn = m.get("module", {}).get("name") or m.get("module", {}).get("path")
        ctx = (path.parent / "lukhas_context.md").exists()
        info = {
            "fqn": fqn,
            "path": str(path.parent.relative_to(ROOT)),
            "tier": tier,
            "ctx": ctx,
            "matriz": ",".join(m.get("matriz_integration",{}).get("pipeline_nodes", []))
        }
        per_star[star].append(info)

    # Ensure dirs
    STARS_DIR.mkdir(parents=True, exist_ok=True)

    # Per star pages
    perstar_links = []
    for star in order:
        items = per_star.get(star, [])
        items.sort(key=lambda x: (x["tier"], x["fqn"]))
        star_slug = slug(star)
        out = STARS_DIR / f"{star_slug}.md"
        lines = [f"# {star}\n", f"_Generated {datetime.datetime.utcnow().isoformat()}Z_\n",
                 f"\n**Modules:** {len(items)}\n\n",
                 "| Tier | MATRIZ | Context | Module | Path |\n|---|---|---|---|---|\n"]
        for it in items:
            lines.append(f"| {it['tier']} | {it['matriz']} | {'✅' if it['ctx'] else '—'} | `{it['fqn']}` | `{it['path']}` |\n")
        out.write_text("".join(lines), encoding="utf-8")
        perstar_links.append(f"- [{star}](stars/{star_slug}.md) — {len(items)} modules")

    # Top summary
    md = [f"# {conf.get('title','Constellation Top')}\n",
          f"_Generated {datetime.datetime.utcnow().isoformat()}Z_\n\n",
          f"**Total manifests scanned:** {total}\n\n",
          "## Stars\n", "\n".join(perstar_links), "\n\n"]

    limit = conf.get("limit_per_star", 15)
    for section in conf.get("sections", []):
        name = section["name"]
        tiers = set(section.get("tiers", []))
        missing_ctx_only = section.get("missing_context_only", False)
        md.append(f"## {name}\n")
        for star in order:
            items = per_star.get(star, [])
            if tiers:
                items = [i for i in items if i["tier"] in tiers]
            if missing_ctx_only:
                items = [i for i in items if not i["ctx"]]
            if not items:
                continue
            md.append(f"\n### {star}\n")
            md.append("| Tier | MATRIZ | Context | Module | Path |\n|---|---|---|---|---|\n")
            for it in items[:limit]:
                md.append(f"| {it['tier']} | {it['matriz']} | {'✅' if it['ctx'] else '—'} | `{it['fqn']}` | `{it['path']}` |\n")
        md.append("\n")

    (DOCS / "CONSTELLATION_TOP.md").write_text("".join(md), encoding="utf-8")
    print("Generated docs/CONSTELLATION_TOP.md and docs/stars/*.md")

if __name__ == "__main__":
    main()
