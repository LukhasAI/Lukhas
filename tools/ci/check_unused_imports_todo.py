#!/usr/bin/env python3
"""
T4 UNUSED IMPORTS VALIDATOR - Production Lane Policy Enforcement

- Runs ruff F401 to find unused imports in selected roots (default: production lanes)
- Checks each finding has a TODO[T4-UNUSED-IMPORT] structured JSON annotation (or acceptable legacy tag)
- Outputs JSON report for CI/CD integration
- Enforces production lane policy (candidate/experimental code exempt)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODO_TAG = "TODO[T4-UNUSED-IMPORT]"
INLINE_JSON_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}\s*:\s*(\{{.*\}})\s*$")
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports"}
WAIVERS = REPO / "audit" / "waivers" / "unused_imports.yaml"

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

def parse_inline_json(line: str):
    m = INLINE_JSON_RE.search(line)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None

def validate_entry(entry: dict):
    errors = []
    if not isinstance(entry, dict):
        errors.append("annotation is not a JSON object")
        return errors
    if "id" not in entry:
        errors.append("missing id")
    reason = entry.get("reason", "")
    if not reason or not isinstance(reason, str) or reason.strip().lower() in ("kept for future", "kept for future use", "kept for future use."):
        errors.append("reason missing or generic")
    if "status" not in entry:
        errors.append("missing status")
    if entry.get("status") in ("planned", "committed"):
        if not entry.get("owner"):
            errors.append("planned/committed entries must have owner")
        if not entry.get("ticket"):
            errors.append("planned/committed entries must have ticket")
    return errors

def ruff_F401(paths):
    cmd = ["python3", "-m", "ruff", "check", "--select", "F401", "--output-format", "json", *list(paths)]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    if proc.returncode not in (0, 1):
        return {"error": f"ruff failed: {proc.stderr or proc.stdout}"}
    try:
        items = json.loads(proc.stdout or "[]")
    except Exception as e:
        return {"error": f"Failed to parse ruff output: {e}"}
    findings = []
    for item in items:
        file_path = (REPO / item["filename"]).resolve()
        # Skip if any path segment is in SKIP_DIRS
        if set(file_path.parts) & SKIP_DIRS:
            continue
        findings.append(
            {
                "file": str(file_path.relative_to(REPO)),
                "abs_path": str(file_path),
                "line": item["location"]["row"],
                "message": item["message"],
            }
        )
    return {"findings": findings}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", default=["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"])
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    valid_roots = []
    for path_arg in args.paths:
        if path_arg.strip() in SKIP_DIRS or path_arg.strip() == "labs":
            continue
        abs_path = (REPO / path_arg).resolve()
        if abs_path.exists():
            valid_roots.append(str(abs_path.relative_to(REPO)))

    if not valid_roots:
        result = {"status": "error", "message": "No valid production roots to validate", "unannotated": [], "summary": {"total": 0, "annotated": 0, "missing": 0}}
        print(json.dumps(result, indent=2))
        sys.exit(1)

    waivers = load_waivers()
    ruff_result = ruff_F401(valid_roots)
    if "error" in ruff_result:
        result = {"status": "error", "message": ruff_result["error"], "unannotated": [], "summary": {"total": 0, "annotated": 0, "missing": 0}}
        print(json.dumps(result, indent=2))
        sys.exit(1)

    findings = ruff_result["findings"]

    unannotated = []
    annotated_count = 0
    quality_issues = []

    for f in findings:
        file_abs = Path(f["abs_path"])
        # Waiver: if file is waived (0) or that exact line is waived, skip
        if str(file_abs) in waivers and (0 in waivers[str(file_abs)] or f["line"] in waivers[str(file_abs)]):
            continue
        try:
            lines = file_abs.read_text(encoding="utf-8", errors="ignore").splitlines()
            idx = f["line"] - 1
            if idx < 0 or idx >= len(lines):
                unannotated.append({"file": f["file"], "line": f["line"], "message": "line out of range"})
                continue
            line_content = lines[idx]
            entry = parse_inline_json(line_content)
            if not entry:
                # Accept legacy non-JSON that contains TODO[T4-UNUSED-IMPORT] but flag as low-quality
                if "TODO[T4-UNUSED-IMPORT]" in line_content:
                    annotated_count += 1
                    quality_issues.append({"file": f["file"], "line": f["line"], "issues": ["legacy annotation (non-structured) - migrate to structured JSON"]})
                else:
                    unannotated.append({"file": f["file"], "line": f["line"], "message": f["message"]})
            else:
                annotated_count += 1
                issues = validate_entry(entry)
                if issues:
                    quality_issues.append({"file": f["file"], "line": f["line"], "issues": issues})
        except Exception:
            unannotated.append({"file": f["file"], "line": f["line"], "message": "unreadable"})

    total = len(findings)
    missing = len(unannotated)

    result = {
        "status": "pass" if missing == 0 and not quality_issues else "fail",
        "message": f"Production lane policy: {annotated_count}/{total} imports properly annotated",
        "annotated": annotated_count,
        "total": total,
        "missing": missing,
        "quality_issues_count": len(quality_issues),
        "unannotated": unannotated,
        "quality_issues": quality_issues,
    }

    if args.json_only:
        print(json.dumps(result, indent=2))
    else:
        print("\n🔍 T4 UNUSED IMPORTS VALIDATOR - Production Lane Policy")
        print("=" * 60)
        print(json.dumps(result, indent=2))

    sys.exit(0 if result["status"] == "pass" else 1)

if __name__ == "__main__":
    main()
