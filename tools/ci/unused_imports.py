#!/usr/bin/env python3
"""
T4 unused-imports policy enforcer.

- Scans for Ruff F401 (unused imports) in selected roots (default: lukhas, MATRIZ)
- Skips noisy trees (candidate, archive, quarantine, .venv, node_modules, reports, .git)
- If a F401 is found, the tool:
  * adds an inline TODO tag (idempotent):  # TODO[T4-UNUSED-IMPORT]: <reason>
  * ensures a small header block exists at top of file once
  * logs each action to reports/todos/unused_imports.jsonl
- --strict: exits non-zero if any F401 remain unannotated (for CI fail)
- --dry-run: do not modify files, only print what would change
- Waivers file: AUDIT/waivers/unused_imports.yaml (optional)
"""

from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO / "reports" / "todos"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOG = REPORTS_DIR / "unused_imports.jsonl"
WAIVERS = REPO / "AUDIT" / "waivers" / "unused_imports.yaml"

DEFAULT_ROOTS = ["lukhas", "MATRIZ"]
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "candidate", "reports"}
HEADER_BLOCK = (
    "# ---\n"
    "# TODO[T4-UNUSED-IMPORT]: This file contains intentionally kept unused imports.\n"
    "# Provide a reason per line or remove when implemented.\n"
    "# ---\n"
)

TODO_TAG = "TODO[T4-UNUSED-IMPORT]"
INLINE_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}")
IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+.*)$")


def load_waivers() -> dict[str, set[int]]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    if not WAIVERS.exists():
        return {}
    try:
        data = yaml.safe_load(WAIVERS.read_text()) or {}
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
    return text if TODO_TAG in text else (HEADER_BLOCK + text)


def annotate_line(text: str, line_no: int, reason: str):
    lines = text.splitlines()
    idx = line_no - 1
    if idx < 0 or idx >= len(lines):
        return text, False
    line = lines[idx]
    if INLINE_RE.search(line):
        return text, False
    if not IMPORT_RE.match(line):
        return text, False
    lines[idx] = f"{line}  # {TODO_TAG}: {reason}"
    new_text = "\n".join(lines)
    if not text.endswith("\n"):
        new_text += "\n"
    return new_text, True


def main():
    ap = argparse.ArgumentParser(description="Annotate or enforce TODOs for unused imports (F401).")
    ap.add_argument("--paths", nargs="+", default=DEFAULT_ROOTS,
                    help="Roots to scan (default: lukhas MATRIZ).")
    ap.add_argument("--reason", default="kept pending MATRIZ wiring (document or remove)",
                    help="Reason appended to the TODO tag.")
    ap.add_argument("--strict", action="store_true",
                    help="Exit non-zero if any F401 remain unannotated.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Do not write changes; only print actions.")
    args = ap.parse_args()

    # Filter roots that exist and are not globally skipped
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

    # Track unannotated that remain (for --strict)
    remaining_unannotated: list[str] = []

    # Prepare log buffer
    existing_log = ""
    if LOG.exists():
        existing_log = LOG.read_text(encoding="utf-8", errors="ignore")

    edits = 0
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
        new_code, changed = annotate_line(code, line, args.reason)
        if changed:
            new_code = ensure_header(new_code)
            if args.dry_run:
                print(f"[DRY-RUN] Would annotate {file_path}:{line} -> {TODO_TAG}")
            else:
                file_path.write_text(new_code, encoding="utf-8")
            edits += 1
            entry = {
                "file": str(file_path.relative_to(REPO)),
                "line": line,
                "reason": args.reason,
                "message": msg,
            }
            existing_log += json.dumps(entry) + "\n"
        else:
            # Could not annotate (non-import line etc.)
            remaining_unannotated.append(f"{file_path}:{line} {msg}")

    if not args.dry_run:
        LOG.write_text(existing_log, encoding="utf-8")

    print(f"Annotated {edits} unused import(s). Log: {LOG}")
    if args.strict and remaining_unannotated:
        print("Unannotated F401 findings:", *remaining_unannotated, sep="\n")
        sys.exit(1)


if __name__ == "__main__":
    main()