#!/usr/bin/env python3
"""
T4 Lint Annotator: run ruff for a set of codes and create structured inline annotations
for findings that need tracking.

Usage:
  python3 tools/ci/lint_annotator.py --paths lukhas core --codes F821,F403,B008 --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "reports" / "todos" / "lint_issues.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)

TODO_TAG = "TODO[T4-LINT-ISSUE]"
INLINE_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}\s*:\s*(\{{.*\}})\s*$")
IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+.*)$")

def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def make_id() -> str:
    return f"t4-lint-{uuid.uuid4().hex[:8]}"

def run_ruff_select(paths: list[str], codes: list[str]) -> list[dict]:
    cmd = ["python3", "-m", "ruff", "check", "--select", ",".join(codes), "--output-format", "json", *paths]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode not in (0,1):
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(proc.returncode)
    try:
        return json.loads(proc.stdout or "[]")
    except Exception:
        return []

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="+", default=["lukhas", "core"])
    ap.add_argument("--codes", required=True, help="Comma-separated list of codes to check (e.g., F821,F403,B008)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--annotate-all", action="store_true", help="Annotate even if ruff says autofixable")
    ap.add_argument("--owner", default=None)
    ap.add_argument("--ticket", default=None)
    return ap.parse_args()

def annotate_line(text: str, line_no: int, payload: dict):
    lines = text.splitlines()
    idx = line_no - 1
    if idx < 0 or idx >= len(lines):
        return text, False
    line = lines[idx]
    if INLINE_RE.search(line):
        return text, False
    json_compact = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    lines[idx] = f"{line}  # {TODO_TAG}: {json_compact}"
    new_text = "\n".join(lines)
    if not text.endswith("\n"):
        new_text += "\n"
    return new_text, True

def main():
    args = parse_args()
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    # Resolve roots
    roots = []
    for p in args.paths:
        p = p.strip()
        rp = (REPO / p).resolve()
        if rp.exists():
            roots.append(str(rp.relative_to(REPO)))
    if not roots:
        print("No valid roots. Exiting.")
        sys.exit(0)

    findings = run_ruff_select(roots, codes)
    edits = 0
    new_entries = []
    for it in findings:
        file_path = (REPO / it["filename"]).resolve()
        line = int(it["location"]["row"])
        msg = it.get("message", "")
        code = it.get("code") or it.get("message", "").split()[0]

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Skip if already annotated
        try:
            target_line = text.splitlines()[line-1]
            if INLINE_RE.search(target_line):
                continue
        except Exception:
            pass

        # Build payload
        payload = {
            "id": make_id(),
            "code": code,
            "reason": msg,
            "suggestion": None,
            "owner": args.owner,
            "ticket": args.ticket,
            "status": "reserved",
            "created_at": iso_now()
        }

        # Basic suggestion heuristics for certain codes
        if code == "F821":
            # suggest import if token looks like a module alias (heuristic)
            token = None
            try:
                token = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", target_line)[0]
            except Exception:
                token = None
            if token:
                payload["suggestion"] = f"Consider adding import for '{token}', or define it before use."
        elif code == "F401":
            payload["suggestion"] = "Import is unused; consider removing or mark by TODO[T4-UNUSED-IMPORT]."
        elif code.startswith("B") and code in ("B008", "B018", "B007"):
            payload["suggestion"] = "Refactor suggested: move default arg to None, avoid useless expression, don't use loop-control variable."
        # ... add more heuristics as needed

        new_text, changed = annotate_line(text, line, payload)
        if changed:
            if args.dry_run:
                print(f"[DRY] Would annotate {file_path}:{line} - {code} - {payload['reason']}")
            else:
                file_path.write_text(new_text, encoding="utf-8")
            edits += 1
            new_entries.append({
                "id": payload["id"], "file": str(file_path.relative_to(REPO)), "line": line,
                "code": payload["code"], "reason": payload["reason"], "status": payload["status"], "created_at": payload["created_at"]
            })

    if not args.dry_run and new_entries:
        with LOG.open("a", encoding="utf-8") as fh:
            for e in new_entries:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"Annotations created: {edits}")

if __name__ == "__main__":
    main()
