#!/usr/bin/env python3
"""
T4 structured unused-imports annotator.

- Scans for Ruff F401 in selected roots (default: lukhas, MATRIZ)
- Skips noisy trees (candidate, archive, quarantine, .venv, node_modules, reports, .git)
- If an F401 is found, adds an inline structured JSON TODO tag:
  # TODO[T4-UNUSED-IMPORT]: {"id":"t4-...", "reason":"...", ...}
- Ensures a small header block exists at top of file once
- Logs each action to reports/todos/unused_imports.jsonl
- --dry-run: preview only
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
REPORTS_DIR = REPO / "reports" / "todos"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOG = REPORTS_DIR / "unused_imports.jsonl"
WAIVERS = REPO / "audit" / "waivers" / "unused_imports.yaml"

DEFAULT_ROOTS = ["lukhas", "MATRIZ"]
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports"}
HEADER_BLOCK = (
    "# ---\n"
    "# TODO[T4-UNUSED-IMPORT]: Structured JSON annotation required.\n"
    "# Schema: id, reason_category, reason, owner, ticket, eta, status, created_at\n"
    "# ---\n"
)

UNUSED_IMPORT_TAG = "TODO[T4-UNUSED-IMPORT]"
# Matches: "# TODO[T4-UNUSED-IMPORT]: {...}" capturing the {...}
INLINE_RE = re.compile(rf"#\s*{re.escape(UNUSED_IMPORT_TAG)}\s*:\s*(\{{.*\}})\s*$")
IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+.*)$")

def load_waivers() -> dict[str, set[int]]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not WAIVERS.exists():
        return {}
    try:
        data = yaml.safe_load(WAIVERS.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    out: dict[str, set[int]] = {}
    for it in data.get("waivers", []):
        p = (REPO / it["file"]).resolve()
        out.setdefault(str(p), set()).add(int(it.get("line", 0)))
    return out

def run_ruff_f401(paths: list[str]) -> list[dict]:
    cmd = ["python3", "-m", "ruff", "check", "--select", "F401", "--output-format", "json", *paths]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    if proc.returncode not in (0, 1):  # 0=clean, 1=findings
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(proc.returncode)
    try:
        return json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return []

def path_is_skipped(p: Path) -> bool:
    parts = set(p.parts)
    return bool(parts & SKIP_DIRS)

def ensure_header(text: str) -> str:
    return text if UNUSED_IMPORT_TAG in text else (HEADER_BLOCK + text)

def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def make_id() -> str:
    return f"t4-{uuid.uuid4().hex[:8]}"

def annotate_line_structured(text: str, line_no: int, reason: str, reason_category: str = "OTHER", owner: str | None = None, ticket: str | None = None, eta: str | None = None):
    lines = text.splitlines()
    idx = line_no - 1
    if idx < 0 or idx >= len(lines):
        return text, False, None
    line = lines[idx]
    if INLINE_RE.search(line):
        # Already has a structured inline annotation
        return text, False, None
    if not IMPORT_RE.match(line):
        return text, False, None

    entry = {
        "id": make_id(),
        "reason_category": reason_category,
        "reason": reason,
        "owner": owner,
        "ticket": ticket,
        "eta": eta,
        "status": "reserved",
        "created_at": iso_now(),
    }
    json_compact = json.dumps(entry, separators=(",", ":"), ensure_ascii=False)
    lines[idx] = f"{line}  # {UNUSED_IMPORT_TAG}: {json_compact}"
    new_text = "\n".join(lines)
    if not text.endswith("\n"):
        new_text += "\n"
    return new_text, True, entry

def main():
    ap = argparse.ArgumentParser(description="Annotate or enforce tracking tags for unused imports (F401).")
    ap.add_argument("--paths", nargs="+", default=DEFAULT_ROOTS, help="Roots to scan (default: lukhas MATRIZ).")
    ap.add_argument(
        "--reason",
        default="kept pending MATRIZ wiring (document or remove)",
        help="Reason appended to the tracking tag.",
    )
    ap.add_argument("--reason_category", default="CORE_INFRA", help="Reason category for the structured annotation.")
    ap.add_argument("--owner", default=None, help="Optional owner handle (e.g., @alice).")
    ap.add_argument("--ticket", default=None, help="Optional ticket reference (e.g., GH-123).")
    ap.add_argument("--eta", default=None, help="Optional ETA in YYYY-MM-DD.")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero if any F401 remain unannotated.")
    ap.add_argument("--dry-run", action="store_true", help="Do not write changes; only print actions.")
    args = ap.parse_args()

    # Resolve roots: filter non-existing or skipped
    roots: list[str] = []
    for root_path in args.paths:
        root_path = root_path.strip()
        if not root_path or root_path in SKIP_DIRS:
            continue
        abs_r = (REPO / root_path).resolve()
        if abs_r.exists():
            roots.append(str(abs_r.relative_to(REPO)))

    if not roots:
        print("No valid roots to scan. Exiting.")
        sys.exit(0)

    waivers = load_waivers()
    findings = run_ruff_f401(roots)

    remaining_unannotated: list[str] = []

    edits = 0
    new_entries: list[dict] = []

    for it in findings:
        file_path = (REPO / it["filename"]).resolve()
        line = int(it["location"]["row"])
        msg = it.get("message", "F401 unused import")

        if path_is_skipped(file_path):
            continue
        # Waivers: file-level (line=0) or specific line
        if str(file_path) in waivers and (0 in waivers[str(file_path)] or line in waivers[str(file_path)]):
            continue

        try:
            code = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            remaining_unannotated.append(f"{file_path}:{line} {msg} (unreadable)")
            continue

        # Already annotated?
        try:
            target_line = code.splitlines()[line - 1]
            already = bool(INLINE_RE.search(target_line)) or not IMPORT_RE.match(target_line)
        except Exception:
            already = False

        if already:
            continue

        # Annotate
        new_code, changed, entry = annotate_line_structured(
            code,
            line,
            reason=args.reason,
            reason_category=args.reason_category,
            owner=args.owner,
            ticket=args.ticket,
            eta=args.eta,
        )
        if changed:
            new_code = ensure_header(new_code)
            if args.dry_run:
                print(f"[DRY-RUN] Would annotate {file_path}:{line} -> {UNUSED_IMPORT_TAG} id={entry.get('id')}")
            else:
                try:
                    file_path.write_text(new_code, encoding="utf-8")
                except Exception as e:
                    remaining_unannotated.append(f"{file_path}:{line} {msg} (write-failed: {e})")
                    continue
            edits += 1

            log_entry = {
                "id": entry.get("id"),
                "file": str(file_path.relative_to(REPO)),
                "line": line,
                "reason_category": entry.get("reason_category"),
                "reason": entry.get("reason"),
                "owner": entry.get("owner"),
                "ticket": entry.get("ticket"),
                "eta": entry.get("eta"),
                "status": entry.get("status"),
                "message": msg,
                "timestamp": entry.get("created_at"),
                "tool": "T4-unused-imports-annotator",
            }
            new_entries.append(log_entry)
        else:
            remaining_unannotated.append(f"{file_path}:{line} {msg} (could not annotate)")

    # Append to log in an idempotent way
    if not args.dry_run:
        try:
            with LOG.open("a", encoding="utf-8") as fh:
                for e in new_entries:
                    fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        except Exception as e:
            print("Failed to write log:", e, file=sys.stderr)

    print(f"Annotated {edits} unused import(s). Log: {LOG}")
    if args.strict and remaining_unannotated:
        print("Unannotated F401 findings:", *remaining_unannotated, sep="\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
