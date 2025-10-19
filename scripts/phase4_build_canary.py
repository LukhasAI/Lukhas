#!/usr/bin/env python3
"""
Build a deterministic canary set of manifest targets for Phase 4.

Usage:
    python scripts/phase4_build_canary.py --size 0.10 --out docs/audits/phase4_canary_list.txt

Notes:
- Works on *existing* manifests under ./manifests by default.
- Deterministic selection using SHA256(path) so repeated runs pick the same sample.
- Stratifies across top-level domains (e.g., consciousness/, identity/, governance/, labs/, core/, matriz/, api/).
"""
import argparse
import hashlib
from pathlib import Path
from collections import defaultdict

TOPS = {"consciousness","identity","governance","memory","core","labs","matriz","api"}

def sha_bucket(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--size", type=float, default=0.10, help="fraction 0..1 of total to include (default 0.10)")
    p.add_argument("--out", required=True, help="output filepath for the list")
    p.add_argument("--root", default="manifests", help="root folder to scan (default manifests)")
    args = p.parse_args()

    manifests = list(Path(args.root).rglob("module.manifest.json"))
    if not manifests:
        raise SystemExit(f"No manifests found under {args.root}")

    by_top = defaultdict(list)
    for m in manifests:
        rel = m.relative_to(args.root)
        parts = rel.parts
        top = parts[0] if parts else "unknown"
        key = str(rel.parent)  # e.g. consciousness/core
        by_top[top].append((key, str(m)))

    total = sum(len(v) for v in by_top.values())
    target_total = max(1, int(round(total * args.size)))

    # proportional per top-level, deterministic by hash
    picks = []
    allocated = 0
    for top, items in by_top.items():
        if top not in TOPS:
            continue
        need = int(round(len(items) / total * target_total))
        items_sorted = sorted(items, key=lambda kv: sha_bucket(kv[0]))
        picks.extend(items_sorted[:need])
        allocated += need

    # top up to exact target_total by global hash order
    if allocated < target_total:
        remaining = []
        for items in by_top.values():
            remaining.extend(items)
        chosen = {k for k, _ in picks}
        rest = [kv for kv in remaining if kv[0] not in chosen]
        rest_sorted = sorted(rest, key=lambda kv: sha_bucket(kv[0]))
        picks.extend(rest_sorted[: target_total - allocated])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for _key, mpath in sorted(picks, key=lambda kv: kv[0]):
            f.write(mpath + "\n")
    print(f"Wrote {len(picks)} canary items to {out}")

if __name__ == "__main__":
    main()
