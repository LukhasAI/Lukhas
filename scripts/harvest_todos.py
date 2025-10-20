#!/usr/bin/env python3
"""
Harvest real TODO/FIXME items into a CSV for triage, skipping known fake/linter "TODO" noise.

Outputs: docs/audits/todos.csv with columns:
path,line,kind,owner_hint,priority,tag,text

Kinds: general|specialist|fixme
Owner hints: extracted from TODO[AREA:specialist] (e.g., QUANTUM-BIO → quantum-bio)
Priority: inferred from tokens (P0/P1/P2/P3/HIGH/LOW); default P2 for specialist, P3 otherwise.
Tag: free-form tag parsed from bracket or None.

Usage:
  python3 scripts/harvest_todos.py --roots lukhas labs packages tools tests docs --out docs/audits/todos.csv
"""
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path

# Recognize TODO flavors
RX_TODO = re.compile(r'(?i)\bTODO\b(?P<bracket>\[[^\]]+\])?(?P<colon>[:：]\s*|$)')
RX_FIXME = re.compile(r'(?i)\bFIXME\b[:：]?\s*')
# Specialist marker: TODO[AREA:specialist]
RX_SPECIALIST = re.compile(r'(?i)TODO\[(?P<area>[A-Z0-9\-_/]+)\s*:\s*specialist\]')
# Priority hints
RX_PRIORITY = re.compile(r'(?i)\b(P0|P1|P2|P3|BLOCKER|HIGH|LOW|TRIVIAL)\b')
# Known fake TODO noise we must skip completely
RX_FAKE = re.compile(r'(?i)#\s*noqa:\s*(F821|invalid-syntax)\s*#\s*TODO:|REALITY_TODO')

TEXT_SUFFIXES = {
    ".py",".md",".markdown",".txt",".rst",".ini",".cfg",".conf",".toml",".yaml",".yml",".json",
    ".js",".jsx",".ts",".tsx",".sh",".bash",".zsh",".ps1",".sql",".proto",".java",".kt",".go"
}
EXCLUDE_DIRS = {".git","venv",".venv","node_modules","dist","build","__pycache__",
                ".mypy_cache",".ruff_cache",".pytest_cache",".tox",".idea",".vscode",".DS_Store"}

def priority_from_text(text:str, specialist:bool)->str:
    m = RX_PRIORITY.search(text or "")
    if m:
        tok = m.group(1).upper()
        if tok in {"BLOCKER","HIGH"}: return "P0" if tok=="BLOCKER" else "P1"
        if tok in {"LOW","TRIVIAL"}: return "P3"
        return tok
    return "P2" if specialist else "P3"

def is_text_file(path:Path)->bool:
    return path.suffix in TEXT_SUFFIXES

def scan_file(path:Path):
    items = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return items
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        if RX_FAKE.search(raw):
            # skip fake/linter TODO scaffolds & legacy trackers
            continue
        kind = None
        specialist = False
        owner_hint = ""
        tag = ""

        if RX_FIXME.search(raw):
            kind = "fixme"
        m = RX_TODO.search(raw)
        if m:
            kind = kind or "general"
            br = (m.group("bracket") or "").strip("[]").strip()
            if br:
                tag = br
            sm = RX_SPECIALIST.search(raw)
            if sm:
                specialist = True
                owner_hint = sm.group("area").lower()
                kind = "specialist"

            prio = priority_from_text(raw, specialist)
            text_part = raw
            # Attempt to keep only content after TODO/FIXME marker for readability
            try:
                # split on first occurrence of "TODO" or "FIXME"
                split_point = None
                mt = re.search(r'(?i)TODO|FIXME', raw)
                if mt: split_point = mt.end()
                text_part = raw[split_point:].strip() if split_point else raw
            except Exception:
                pass

            items.append({
                "path": str(path),
                "line": idx,
                "kind": kind,
                "owner_hint": owner_hint,
                "priority": prio,
                "tag": tag,
                "text": text_part
            })
        elif kind == "fixme":
            prio = priority_from_text(raw, False)
            items.append({
                "path": str(path),
                "line": idx,
                "kind": "fixme",
                "owner_hint": "",
                "priority": prio,
                "tag": "",
                "text": raw
            })
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="+", default=["lukhas","labs","packages","tools","tests","docs"])
    ap.add_argument("--out", default="docs/audits/todos.csv")
    args = ap.parse_args()

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for root in args.roots:
        base = Path(root)
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                if p.name in EXCLUDE_DIRS:
                    continue
                # skip hidden dirs
                if p.name.startswith("."):
                    continue
                continue
            if not is_text_file(p):
                continue
            # skip hidden files
            if any(seg.startswith(".") for seg in p.parts):
                continue
            rows.extend(scan_file(p))

    # de-duplicate exact duplicates (path,line,text)
    seen = set()
    dedup = []
    for r in rows:
        key = (r["path"], r["line"], r["text"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)

    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path","line","kind","owner_hint","priority","tag","text"])
        w.writeheader()
        w.writerows(dedup)

    print(f"[OK] wrote {outp} ({len(dedup)} items)")

if __name__ == "__main__":
    sys.exit(main() or 0)
