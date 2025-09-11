#!/usr/bin/env python3
"""
Merge Strategic + Neutral audit markdowns into a single, ranked action queue
and supporting artifacts (scoreboard, contradictions, evidence ledger).

Usage examples:
  # Explicit inputs
  python merge_audits.py \
    --strategic reports/audit/strategic_20250910T143306Z.md \
    --neutral   reports/audit/neutral_20250910T143306Z.md \
    --out-dir   reports/audit/merged

  # Auto-detect most recent audit files in reports/audit/
  python merge_audits.py --auto --out-dir reports/audit/merged
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# ---- Parsers ---------------------------------------------------------------

FINDING_ROW = re.compile(
    r"^\|\s*(?P<cat>[^|]+?)\s*\|\s*(?P<file>[^|]+?)\s*\|\s*(?P<ev>[^|]+?)\s*\|\s*(?P<risk>[^|]+?)\s*\|\s*(?P<when>[^|]+?)\s*\|\s*$",
    re.IGNORECASE,
)

CIT_HEADER = re.compile(r"^\s*File:\s*(?P<path>[^:]+):(?P<start>\d+)-(?P<end>\d+)\s*$")
SCOREBOARD_LINE = re.compile(r"^\s*([A-Za-z][A-Za-z _/+:-]+?)\s*:\s*(Red|Yellow|Green)\s*$", re.IGNORECASE)

SEV_WEIGHT = {"red": 3.0, "yellow": 2.0, "green": 1.0}
EFF_PENALTY = {"fix now": -2.0, "now": -2.0, "later": -1.0}
CONFIDENCE_BONUS_PER_CIT = 0.25


def load_text(p: Path | str) -> str:
    from pathlib import Path

    if isinstance(p, str):
        p = Path(p)
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return ""


def auto_detect_audit_files(root: Path) -> tuple[Path | None, Path | None]:
    """
    Pick the newest strategic_*.md and neutral_*.md under root (lexicographic then mtime).
    """
    if not root.exists():
        return None, None
    strategic = sorted(root.glob("strategic_*.md"), key=lambda p: (p.name, p.stat().st_mtime), reverse=True)
    neutral = sorted(root.glob("neutral_*.md"), key=lambda p: (p.name, p.stat().st_mtime), reverse=True)
    return (strategic[0] if strategic else None, neutral[0] if neutral else None)


def parse_findings_table(md: str):
    """
    Parse a markdown findings table plus following citation blocks.

    Expected table columns: Category | File | Evidence (line range) | Risk | Fix Now/Later
    Each row may be followed by one or more code citation blocks in this format:

      File: path/to/file.py:12-27
      ```code
      <up to 20 lines>
      ```

    Returns: list of dicts with keys:
      category, file, risk, when, citations=[{path, range, snippet}]
    """
    findings = []
    lines = md.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        m = FINDING_ROW.match(lines[i])
        if m:
            row = {
                "category": m.group("cat").strip(),
                "file": m.group("file").strip(),
                "risk": m.group("risk").strip(),
                "when": m.group("when").strip(),
                "citations": [],
            }
            j = i + 1
            while j < n:
                # Stop if next table row or new header
                if FINDING_ROW.match(lines[j]) or lines[j].startswith("#"):
                    break
                h = CIT_HEADER.match(lines[j])
                if h:
                    path = h.group("path").strip()
                    rng = f"{int(h.group('start'))}-{int(h.group('end'))}"
                    # Expect code fence next
                    k = j + 1
                    snippet = []
                    if k < n and lines[k].strip().startswith("```"):
                        k += 1
                        while k < n and not lines[k].strip().startswith("```"):
                            snippet.append(lines[k])
                            k += 1
                        j = k + 1
                    else:
                        j = j + 1
                    row["citations"].append({"path": path, "range": rng, "snippet": "\n".join(snippet[:20])})
                    continue
                j += 1
            findings.append(row)
            i = j
        else:
            i += 1

    # Filter out table headers and separator rows
    filtered_findings = []
    for finding in findings:
        # Skip header rows (Category, File, etc.)
        if finding["category"].strip().lower() in ["category", "---"]:
            continue
        # Skip rows where file is "File" or "---"
        if finding["file"].strip().lower() in ["file", "---"]:
            continue
        filtered_findings.append(finding)

    return filtered_findings


def parse_scoreboard(md: str) -> dict:
    board = {}
    for line in md.splitlines():
        m = SCOREBOARD_LINE.match(line)
        if m:
            raw_key = m.group(1).strip().lower()
            k = re.sub(r"[\s/:-]+", "_", raw_key)
            v = m.group(2).capitalize()
            board[k] = v
    return board


def worse_color(a: str | None, b: str | None) -> str | None:
    order = {"Red": 3, "Yellow": 2, "Green": 1}
    if a is None:
        return b
    if b is None:
        return a
    return a if order.get(a, 0) >= order.get(b, 0) else b


def score_item(item: dict) -> float:
    sev = SEV_WEIGHT.get(item.get("risk", "").lower(), 1.0)
    eff = EFF_PENALTY.get(item.get("when", "").lower(), 0.0)
    conf = CONFIDENCE_BONUS_PER_CIT * len(item.get("citations", []))
    return round(sev + conf + eff, 2)


def merge_findings(strategic: list[dict], neutral: list[dict]) -> list[dict]:
    """
    Deduplicate by (file, category). Merge citations, keep worst risk, prefer 'Fix Now'.
    """
    index: dict[tuple[str, str], dict] = {}
    for src, items in (("strategic", strategic), ("neutral", neutral)):
        for it in items:
            key = (it.get("file", "").lower(), it.get("category", "").lower())
            existing = index.get(key)
            if not existing:
                it["_sources"] = {src}
                index[key] = it
                continue
            # merge
            existing["_sources"].add(src)
            existing["citations"].extend(it.get("citations", []))
            existing["risk"] = max(
                [existing.get("risk", ""), it.get("risk", "")], key=lambda r: SEV_WEIGHT.get(r.lower(), 0)
            )
            if "now" in it.get("when", "").lower():
                existing["when"] = it.get("when", "")
    out = list(index.values())
    for o in out:
        o["_score"] = score_item(o)
        o["_sources"] = sorted(o["_sources"])
    out.sort(key=lambda d: (-d["_score"], d.get("file", "")))
    return out


# ---- Main ------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategic", help="path to strategic findings markdown")
    ap.add_argument("--neutral", help="path to neutral findings markdown")
    ap.add_argument(
        "--auto", action="store_true", help="auto-detect latest strategic_*.md and neutral_*.md in reports/audit/"
    )
    ap.add_argument("--out-dir", default="reports/audit/merged", help="output directory")
    args = ap.parse_args()

    audit_dir = Path("reports/audit")
    if args.auto:
        s_path, n_path = auto_detect_audit_files(audit_dir)
        if not s_path or not n_path:
            print(
                "ERROR: --auto could not find both strategic_*.md and neutral_*.md under reports/audit/",
                file=sys.stderr,
            )
            sys.exit(2)
    else:
        if not args.strategic or not args.neutral:
            print("ERROR: provide --strategic and --neutral, or use --auto", file=sys.stderr)
            sys.exit(2)
        s_path, n_path = Path(args.strategic), Path(args.neutral)

    s_md = load_text(s_path)
    n_md = load_text(n_path)
    if not s_md or not n_md:
        print("ERROR: one or both input files are empty / unreadable", file=sys.stderr)
        sys.exit(2)

    # Parse sections
    s_find = parse_findings_table(s_md)
    n_find = parse_findings_table(n_md)
    merged = merge_findings(s_find, n_find)

    # Parse scoreboards (optional)
    s_board = parse_scoreboard(s_md)
    n_board = parse_scoreboard(n_md)
    all_keys = set(s_board) | set(n_board)
    merged_board = {k: worse_color(s_board.get(k), n_board.get(k)) for k in sorted(all_keys)}

    outdir = Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Write action_queue.md
    aq = outdir / "action_queue.md"
    with aq.open("w", encoding="utf-8") as f:
        f.write("# Ranked Action Queue\n\n")
        f.write("| Rank | Score | Category | File | Fix | Sources |\n|---:|---:|---|---|---|---|\n")
        for i, m in enumerate(merged, 1):
            f.write(
                f"| {i} | {m.get('_score',0)} | {m.get('category','')} | {m.get('file','')} | {m.get('when','')} | {','.join(m.get('_sources',[]))} |\n"
            )
        f.write("\n> Score = severity(3/2/1) + 0.25×citations − effort(now:-2,later:-1)\n")

    # Write evidence_ledger.csv
    ev = outdir / "evidence_ledger.csv"
    with ev.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "file", "risk", "when", "citation_path", "line_range"])
        for m in merged:
            cits = m.get("citations", [])
            if not cits:
                w.writerow([m.get("category", ""), m.get("file", ""), m.get("risk", ""), m.get("when", ""), "", ""])
            for c in cits:
                w.writerow(
                    [
                        m.get("category", ""),
                        m.get("file", ""),
                        m.get("risk", ""),
                        m.get("when", ""),
                        c.get("path", ""),
                        c.get("range", ""),
                    ]
                )

    # Write scoreboard.json
    (outdir / "scoreboard.json").write_text(json.dumps(merged_board, indent=2), encoding="utf-8")

    # Contradictions: if same (file,category) appears Green in one and Red/Yellow in the other
    def map_risk(findings: list[dict]) -> dict[tuple[str, str], str]:
        return {(f.get("file", "").lower(), f.get("category", "").lower()): f.get("risk", "") for f in findings}

    s_map, n_map = map_risk(s_find), map_risk(n_find)
    contra = []
    keys = sorted(set(s_map) | set(n_map))
    for k in keys:
        a, b = s_map.get(k, "").capitalize(), n_map.get(k, "").capitalize()
        if not a or not b or a == b:
            continue
        if "Green" in (a, b) and ("Red" in (a, b) or "Yellow" in (a, b)):
            contra.append({"file": k[0], "category": k[1], "strategic": a, "neutral": b})

    (outdir / "contradictions.json").write_text(json.dumps(contra, indent=2), encoding="utf-8")

    # Friendly contradictions.md for humans
    cm = outdir / "contradictions.md"
    if contra:
        lines = ["# Contradictions\n"]
        for c in contra:
            lines.append(f"- **{c['file']}** / {c['category']}: strategic={c['strategic']} vs neutral={c['neutral']}")
        cm.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        cm.write_text("# Contradictions\n\n_None_\n", encoding="utf-8")

    print(f"OK: wrote {aq}, {ev}, scoreboard.json, contradictions.(json|md)")
    print(f"Inputs: {s_path} | {n_path}")
    print(f"Output dir: {outdir}")


if __name__ == "__main__":
    main()
