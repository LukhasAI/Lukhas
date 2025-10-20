#!/usr/bin/env python3
"""
Migrate legacy lukhas_context.md files to YAML front-matter.

For each lukhas_context.md under manifests/**:
- If already has a front-matter block (--- ... ---) at top, skip.
- Parse legacy header fields (Star, MATRIZ Nodes, Colony) when present.
- Read sibling module.manifest.json to fill required keys: tier, owner, matriz nodes (fallback to parsed).
- Prepend YAML front-matter:
    required keys: star, tier, matriz (list), owner
    recommended: module, colony, manifest_path
- Preserve the existing markdown body (with legacy header lines removed).

Exit non-zero if any files fail to process.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
FM_BOUNDARY = re.compile(r"^\s*---\s*$")


def has_front_matter(text: str) -> bool:
    lines = text.splitlines()
    if not lines:
        return False
    if not FM_BOUNDARY.match(lines[0]):
        return False
    # find end within first 200 lines
    for i in range(1, min(len(lines), 200)):
        if FM_BOUNDARY.match(lines[i]):
            return True
    return False


def read_manifest(md_path: pathlib.Path) -> Optional[Dict]:
    mf = md_path.parent / "module.manifest.json"
    if not mf.exists():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return None


def parse_legacy_header(text: str) -> Dict[str, Optional[str]]:
    """Lightweight parse of first ~40 lines for legacy header fields."""
    fields = {"star": None, "matriz": None, "colony": None, "title": None}
    lines = text.splitlines()
    for line in lines[:40]:
        if not fields["title"] and line.startswith("# "):
            fields["title"] = line[2:].strip()
        m = re.match(r"\*\*Star\*\*:\s*(.+)\s*$", line)
        if m:
            fields["star"] = m.group(1).strip()
            continue
        m = re.match(r"\*\*MATRIZ Nodes\*\*:\s*(.+)\s*$", line)
        if m:
            fields["matriz"] = m.group(1).strip()
            continue
        m = re.match(r"\*\*Colony\*\*:\s*(.+)\s*$", line)
        if m:
            fields["colony"] = m.group(1).strip()
            continue
    return fields


def sanitize_nodes(nodes_str: Optional[str]) -> List[str]:
    if not nodes_str:
        return []
    # split on commas or whitespace
    parts = re.split(r"[\s,]+", nodes_str)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def to_front_matter(data: Dict[str, object]) -> str:
    # minimal YAML writer for simple scalars and str lists
    lines = ["---"]
    for k in ("module", "star", "tier", "owner", "colony", "manifest_path"):
        v = data.get(k)
        if v is None:
            continue
        lines.append(f"{k}: {v}")
    matriz = data.get("matriz") or []
    if matriz:
        arr = ", ".join(str(x) for x in matriz)
        lines.append(f"matriz: [{arr}]")
    else:
        lines.append("matriz: []")
    lines.append("---")
    return "\n".join(lines) + "\n"


def remove_legacy_header(text: str) -> str:
    """Drop the legacy three lines if present; keep rest intact."""
    lines = text.splitlines()
    keep: List[str] = []
    skip_prefixes = (
        "**Star**:",
        "**MATRIZ Nodes**:",
        "**Colony**:",
    )
    skipped = 0
    for i, line in enumerate(lines):
        if i < 40 and (line.startswith(skip_prefixes) or line.strip() == ""):
            # allow skipping empty lines immediately following header block
            skipped += 1
            continue
        keep = lines[i:]
        break
    return "\n".join(keep).lstrip("\n") + ("\n" if keep else "")


def migrate_one(md_path: pathlib.Path) -> Optional[str]:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    if has_front_matter(text):
        return None  # already good

    legacy = parse_legacy_header(text)
    manifest = read_manifest(md_path) or {}

    module = (manifest.get("module", {}) or {}).get("name") or legacy.get("title") or md_path.parent.name
    tier = (manifest.get("testing", {}) or {}).get("quality_tier") or "T4_experimental"
    owner = (manifest.get("metadata", {}) or {}).get("owner") or "unassigned"
    star = legacy.get("star") or (manifest.get("constellation_alignment", {}) or {}).get("primary_star") or "Supporting"
    matriz_nodes = (manifest.get("matriz_integration", {}) or {}).get("pipeline_nodes") or sanitize_nodes(legacy.get("matriz"))
    colony = legacy.get("colony") or (manifest.get("module", {}) or {}).get("colony")

    fm = {
        "module": module,
        "star": star,
        "tier": tier,
        "owner": owner,
        "matriz": matriz_nodes or [],
        "colony": colony or "",
        "manifest_path": str(md_path.parent / "module.manifest.json"),
    }

    header = to_front_matter(fm)
    body = remove_legacy_header(text)
    return header + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "manifests"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    files = sorted(root.rglob("lukhas_context.md"))
    changed = 0
    failed = 0
    for p in files:
        try:
            new_text = migrate_one(p)
        except Exception as e:
            print(f"[ERROR] {p}: {e}")
            failed += 1
            continue
        if new_text is None:
            continue
        if args.dry_run:
            print(f"[DRY] Would add front-matter: {p}")
        else:
            p.write_text(new_text, encoding="utf-8")
            print(f"[OK] Front-matter added: {p}")
        changed += 1

    print(f"Changed: {changed} | Failed: {failed} | Total scanned: {len(files)}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

