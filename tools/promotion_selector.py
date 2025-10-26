#!/usr/bin/env python3
"""
promotion_selector.py — 0.01% surgical picker for promoting files from legacy lanes
to canonical flat root under `Lukhas/`.

Goals
-----
- Read existing MATRIZ artifacts (if available) to rank candidate files by *impact now*.
- Fall back to filesystem discovery when artifacts are missing.
- Emit a deterministic, reviewable promotion plan (JSONL + Markdown summary).
- Remain idempotent and safe: this tool only *selects*; moving is done by a separate promoter.

Inputs (optional but leveraged when present)
-------------------------------------------
artifacts/matriz_imports.json        # import analysis with bad patterns and/or counts
artifacts/matriz_inventory.json      # modules and their paths
artifacts/where_is_which.csv         # human map for modules
artifacts/matriz_audit.json          # aggregated audit data

What this produces
------------------
artifacts/promotion_batch.plan.jsonl   # one JSON object per file with source → target
artifacts/promotion_selector.md        # human-readable summary + scoring rationale
artifacts/promotion_selector.csv       # CSV for spreadsheet review

Usage
-----
# Top 100 most impactful files under legacy lanes (default weights)
python3 tools/promotion_selector.py --top 100

# Focus only on specific modules
python3 tools/promotion_selector.py --top 50 --modules core,identity,api

# Custom weights
python3 tools/promotion_selector.py --weight-freq 0.6 --weight-recency 0.3 --weight-critical 0.1

# Dry-run (compute but do not write artifacts)
python3 tools/promotion_selector.py --top 25 --dry-run

Scoring model (interpretable)
-----------------------------
score = w_freq * normalized_import_frequency
      + w_recency * normalized_mtime
      + w_critical * critical_flag

Where:
- normalized_import_frequency ∈ [0,1] (from matriz_imports.json or inferred)
- normalized_mtime ∈ [0,1] (freshest → 1.0, oldest → 0)
- critical_flag ∈ {0,1} (1 if tagged critical in artifacts, or path heuristics)

Assumptions
-----------
- Legacy lanes live under any of:
    candidate/, LukhasCandidates/, Lukhas/lukhas/, Lukhas/accepted/
  (Promotion targets flatten to: Lukhas/<module>/<relative_path_from_module_root>)
- Module inferred from the first path component under the lane, e.g.:
    candidate/core/matriz_consciousness_integration.py
  → module = "core", target = Lukhas/core/matriz_consciousness_integration.py

This script never mutates code. It only selects and writes a plan.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import os
import pathlib
import re
import sys
import time
from typing import Dict, List, Optional

ROOT = pathlib.Path(".")
ART = ROOT / "artifacts"
LEGACY_LANES = [
    "labs",
    "LukhasCandidates",
    "Lukhas/lukhas",
    "Lukhas/accepted",
]

DEFAULT_TOP = 100


def _split_source_lane_module_rel(source_path: str):
    """Extract lane, module, and relative path from source.
    Handles patterns like: candidate/<module>/... or Lukhas/lukhas/<module>/...
    """
    parts = re.split(r"[\\/]", source_path)
    if len(parts) < 2:
        return None, None, ""
    lane = parts[0]
    module = parts[1]
    rel = "/".join(parts[2:]) if len(parts) > 2 else ""
    return lane, module, rel


def _compute_target(record: dict, layout: str, target_root: str) -> str:
    """Compute target path based on layout strategy."""
    # Ensure module + relpath present
    lane, mod_from_src, rel_from_src = _split_source_lane_module_rel(record["source"])
    mod = record.get("module") or mod_from_src or "unknown"
    rel = record.get("relpath") or record.get("rel_from_module") or rel_from_src or ""

    if layout == "legacy":
        # Use any legacy target already provided, else fallback
        tgt = record.get("legacy_target")
        if tgt:
            return tgt
        # Fallback to old behavior
        if rel:
            return f"Lukhas/{mod}/{rel}"
        else:
            base = os.path.basename(record["source"])
            return f"Lukhas/{mod}/{base}"

    # flat layout
    base = f"{target_root.rstrip('/')}/{mod}"
    return f"{base}/{rel}" if rel else f"{base}/"


@dataclasses.dataclass
class FileCandidate:
    source: str                   # legacy path (repo-relative)
    module: str                   # inferred module
    rel_from_module: str          # path relative to module root inside legacy lane
    lane: str                     # which legacy lane
    import_freq: float = 0.0      # raw count
    mtime: float = 0.0            # seconds since epoch
    critical: bool = False        # flag from artifacts or heuristics
    score: float = 0.0            # computed
    target: str = ""              # Lukhas/<module>/<rel_from_module>


def _read_json(path: pathlib.Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _discover_legacy_files(modules_filter: Optional[set]) -> List[FileCandidate]:
    out: List[FileCandidate] = []
    for lane in LEGACY_LANES:
        lane_path = ROOT / lane
        if not lane_path.exists():
            continue
        for p in lane_path.rglob("*"):
            if p.is_dir():
                continue
            if p.suffix in {".pyc", ".pyo"} or p.name.startswith("."):
                continue
            # infer module: first child of lane
            try:
                rel = p.relative_to(lane_path)
            except ValueError:
                continue
            parts = rel.parts
            if not parts:
                continue
            module = parts[0]
            if modules_filter and module not in modules_filter:
                continue
            rel_from_module = "/".join(parts[1:]) if len(parts) > 1 else p.name
            try:
                mt = p.stat().st_mtime
            except Exception:
                mt = 0.0
            fc = FileCandidate(
                source=str(p.as_posix()),
                module=module,
                rel_from_module=rel_from_module,
                lane=lane,
                import_freq=0.0,
                mtime=mt,
                critical=False,
            )
            out.append(fc)
    return out


def _index_import_frequencies() -> Dict[str, float]:
    """
    Returns a mapping from repo-relative path → import frequency (approx).
    Expects artifacts/matriz_imports.json if present. We support multiple loosely-structured schemas:
      - { "files": { "path": count, ... } }
      - [ { "path": "...", "count": 12 }, ... ]
      - { "imports": [ {"module": "candidate.core.x", "count": 5, "files": ["..."]}, ...] }
    If not present, we fallback to 0 for all, and later use recency + heuristics.
    """
    path2count: Dict[str, float] = {}
    j = _read_json(ART / "matriz_imports.json")
    if not j:
        return path2count

    # Pattern 1: files dict
    if isinstance(j, dict) and "files" in j and isinstance(j["files"], dict):
        for path, cnt in j["files"].items():
            if isinstance(cnt, (int, float)):
                path2count[path] = float(cnt)

    # Pattern 2: flat list of objects
    if isinstance(j, list):
        for row in j:
            if isinstance(row, dict):
                path = row.get("path")
                cnt = row.get("count")
                if isinstance(path, str) and isinstance(cnt, (int, float)):
                    path2count[path] = float(cnt)

    # Pattern 3: import-centric
    if isinstance(j, dict) and "imports" in j and isinstance(j["imports"], list):
        for imp in j["imports"]:
            imp.get("module")
            cnt = imp.get("count", 0)
            files = imp.get("files", []) or []
            if not isinstance(cnt, (int, float)):
                continue
            # Heuristic: distribute count equally across involved files
            w = float(cnt) / max(1, len(files))
            for f in files:
                if isinstance(f, str):
                    path2count[f] = path2count.get(f, 0.0) + w

    return path2count


def _index_critical_flags() -> Dict[str, bool]:
    """
    Pull best-effort critical flags from matriz_audit.json:
      - { "critical_files": ["pathA", "pathB", ...] }
      - Or entries with {"path": "...", "critical": true}
    """
    flags: Dict[str, bool] = {}
    j = _read_json(ART / "matriz_audit.json")
    if not j:
        return flags

    if isinstance(j, dict):
        crit = j.get("critical_files")
        if isinstance(crit, list):
            for p in crit:
                if isinstance(p, str):
                    flags[p] = True
        # Generic list
        items = j.get("items") or j.get("files")
        if isinstance(items, list):
            for row in items:
                if isinstance(row, dict):
                    p = row.get("path")
                    c = bool(row.get("critical", False))
                    if isinstance(p, str) and c:
                        flags[p] = True
    elif isinstance(j, list):
        for row in j:
            if isinstance(row, dict):
                p = row.get("path")
                c = bool(row.get("critical", False))
                if isinstance(p, str) and c:
                    flags[p] = True
    return flags


def _normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    if math.isclose(vmin, vmax):
        return [0.5 for _ in values]  # flat distribution
    return [(v - vmin) / (vmax - vmin) for v in values]


def select_candidates(top: int,
                      modules_filter: Optional[set],
                      w_freq: float,
                      w_recency: float,
                      w_critical: float,
                      layout: str = "flat",
                      target_root: str = "Lukhas") -> List[FileCandidate]:
    files = _discover_legacy_files(modules_filter)
    if not files:
        return []

    freq_index = _index_import_frequencies()
    crit_index = _index_critical_flags()

    # Attach frequencies/critical flags
    for fc in files:
        # try exact path match; fallback to basename hit from index
        fc.import_freq = float(freq_index.get(fc.source, 0.0))
        if fc.import_freq == 0.0:
            # light heuristic: if index keyed by file basenames
            base = os.path.basename(fc.source)
            fc.import_freq = float(freq_index.get(base, 0.0))
        fc.critical = bool(crit_index.get(fc.source, False))

    # Normalization buckets
    freq_norm = _normalize([f.import_freq for f in files])
    mtime_norm = _normalize([f.mtime for f in files])
    for i, f in enumerate(files):
        nf = freq_norm[i] if freq_norm else 0.0
        nt = mtime_norm[i] if mtime_norm else 0.0
        cc = 1.0 if f.critical else 0.0
        f.score = (w_freq * nf) + (w_recency * nt) + (w_critical * cc)
        # build target path using layout strategy
        record = {
            "source": f.source,
            "module": f.module,
            "rel_from_module": f.rel_from_module,
            "relpath": f.rel_from_module
        }
        f.target = _compute_target(record, layout, target_root)

    files.sort(key=lambda x: x.score, reverse=True)
    return files[:top]


def _write_plan_jsonl(rows: List[FileCandidate], path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            obj = {
                "source": r.source,
                "lane": r.lane,
                "module": r.module,
                "rel_from_module": r.rel_from_module,
                "target": r.target,
                "score": round(r.score, 6),
                "import_freq": r.import_freq,
                "mtime": r.mtime,
                "critical": r.critical,
                "relpath": r.rel_from_module,  # Include for compatibility
            }
            f.write(json.dumps(obj) + "\n")


def _write_plan_md(rows: List[FileCandidate], path: pathlib.Path,
                   params: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Promotion Selector — Batch Plan")
    lines.append("")
    lines.append(f"_Generated:_ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append("")
    lines.append("**Parameters:**  " + ", ".join([f"{k}={v}" for k, v in params.items()]))
    lines.append("")
    lines.append("| Rank | Score | Source (lane) | Module | → Target | ImportFreq | mtime | Critical |")
    lines.append("|---:|---:|---|---|---|---:|---:|---|")
    for i, r in enumerate(rows, 1):
        lines.append(f"| {i} | {r.score:.3f} | `{r.source}` ({r.lane}) | `{r.module}` | `{r.target}` | {int(r.import_freq)} | {int(r.mtime)} | {r.critical} |")
    lines.append("")
    lines.append("> This plan is *selection only*. Use your promoter to apply moves with `git mv` and run MATRIZ validation.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_plan_csv(rows: List[FileCandidate], path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "score", "source", "lane", "module", "rel_from_module", "target", "import_freq", "mtime", "critical"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, f"{r.score:.6f}", r.source, r.lane, r.module, r.rel_from_module, r.target, int(r.import_freq), int(r.mtime), int(r.critical)])


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Select top-N legacy files to promote into Lukhas/ flat root.")
    ap.add_argument("--top", type=int, default=DEFAULT_TOP, help=f"How many files to select (default {DEFAULT_TOP})")
    ap.add_argument("--modules", type=str, default="", help="Comma-separated allowlist of modules to consider (e.g., core,identity,api)")
    ap.add_argument("--weight-freq", type=float, default=0.7, help="Weight for import frequency")
    ap.add_argument("--weight-recency", type=float, default=0.2, help="Weight for file recency (mtime)")
    ap.add_argument("--weight-critical", type=float, default=0.1, help="Weight for critical flag")
    ap.add_argument("--layout", choices=["flat", "legacy"], default="flat",
                    help="Target layout for moves (default: flat)")
    ap.add_argument("--target-root", default="Lukhas",
                    help="Root folder for flat layout (default: Lukhas)")
    ap.add_argument("--dry-run", action="store_true", help="Compute but do not write artifact files")
    ap.add_argument("--out-jsonl", type=str, default="artifacts/promotion_batch.plan.jsonl", help="Output JSONL plan path")
    ap.add_argument("--out-md", type=str, default="artifacts/promotion_selector.md", help="Output Markdown summary path")
    ap.add_argument("--out-csv", type=str, default="artifacts/promotion_selector.csv", help="Output CSV path")
    args = ap.parse_args(argv)

    modules_filter = set([m.strip() for m in args.modules.split(",") if m.strip()]) or None

    rows = select_candidates(
        top=max(1, args.top),
        modules_filter=modules_filter,
        w_freq=args.weight_freq,
        w_recency=args.weight_recency,
        w_critical=args.weight_critical,
        layout=args.layout,
        target_root=args.target_root,
    )

    if not rows:
        print("No legacy files discovered under known lanes; nothing to select.")
        return 0

    if args.dry_run:
        for i, r in enumerate(rows, 1):
            print(f"{i:3d}. {r.source}  →  {r.target}  (score={r.score:.3f}, freq={r.import_freq:.0f}, critical={r.critical})")
        return 0

    _write_plan_jsonl(rows, ROOT / args.out_jsonl)
    _write_plan_md(rows, ROOT / args.out_md, params={
        "top": str(args.top),
        "modules": ",".join(sorted(modules_filter)) if modules_filter else "*",
        "weights": f"freq={args.weight_freq}, recency={args.weight_recency}, critical={args.weight_critical}",
    })
    _write_plan_csv(rows, ROOT / args.out_csv)

    print(f"Wrote: {args.out_jsonl}")
    print(f"Wrote: {args.out_md}")
    print(f"Wrote: {args.out_csv}")
    print("Next: feed the JSONL plan into your promoter (git mv + MATRIZ validation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
