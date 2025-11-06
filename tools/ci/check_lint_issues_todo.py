#!/usr/bin/env python3
"""
T4 Lint Issues Validator: ensure every lint finding in production lanes is either:
- annotated with TODO[T4-LINT-ISSUE] structured JSON, or
- has been autofixed (no finding), or
- waived via AUDIT/waivers/unused_imports.yaml
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TODO_TAG = "TODO[T4-LINT-ISSUE]"
INLINE_JSON_RE = re.compile(rf"#\s*{re.escape(TODO_TAG)}\s*:\s*(\{{.*\}})\s*$")
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports"}
WAIVERS = REPO / "AUDIT" / "waivers" / "unused_imports.yaml"

def parse_inline_json(line: str):
    m = INLINE_JSON_RE.search(line)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None

def load_waivers():
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
    out = {}
    for it in data.get("waivers", []):
        p = (REPO / it["file"]).resolve()
        out.setdefault(str(p), set()).add(int(it.get("line", 0)))
    return out

def run_ruff_select(paths, codes):
    cmd = ["python3", "-m", "ruff", "check", "--select", ",".join(codes), "--output-format", "json", *paths]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if proc.returncode not in (0,1):
        return {"error": proc.stderr or proc.stdout}
    try:
        return {"items": json.loads(proc.stdout or "[]")}
    except Exception as e:
        return {"error": str(e)}

def validate_entry(entry):
    errors = []
    if not isinstance(entry, dict):
        errors.append("annotation is not JSON-object")
        return errors
    if "id" not in entry:
        errors.append("missing id")
    if "code" not in entry:
        errors.append("missing code")
    if "reason" not in entry or not entry["reason"]:
        errors.append("missing reason")
    if entry.get("status") in ("planned","committed") and (not entry.get("owner") or not entry.get("ticket")):
        errors.append("planned/committed must have owner and ticket")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", default=["lukhas","core","api","consciousness","memory","identity","MATRIZ"])
    parser.add_argument("--codes", required=False, default="F821,F401,B904,SIM102,F403,B008,B018,RUF012,RUF006,E701,E702,RUF001,E402,F811,B007,SIM117,SIM105,SIM115")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    roots = []
    for p in args.paths:
        abs_p = (REPO / p).resolve()
        if abs_p.exists():
            roots.append(str(abs_p.relative_to(REPO)))
    if not roots:
        print(json.dumps({"status":"error","message":"no roots"}))
        sys.exit(1)

    waivers = load_waivers()
    ruff_res = run_ruff_select(roots, codes)
    if "error" in ruff_res:
        print(json.dumps({"status":"error","message":ruff_res["error"]}, indent=2))
        sys.exit(1)
    items = ruff_res["items"]
    unannotated = []
    quality_issues = []
    annotated = 0

    for it in items:
        file_abs = (REPO / it["filename"]).resolve()
        if set(file_abs.parts) & SKIP_DIRS:
            continue
        file_str = str(file_abs.relative_to(REPO))
        line = it["location"]["row"]
        # waiver?
        if str(file_abs) in waivers and (0 in waivers[str(file_abs)] or line in waivers[str(file_abs)]):
            continue
        try:
            lines = file_abs.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line-1 >= len(lines):
                unannotated.append({"file":file_str,"line":line,"msg":"line out of range"})
                continue
            line_content = lines[line-1]
            entry = parse_inline_json(line_content)
            if not entry:
                # no structured annotation: flag it
                unannotated.append({"file":file_str,"line":line,"msg":it.get("message")})
            else:
                annotated += 1
                issues = validate_entry(entry)
                if issues:
                    quality_issues.append({"file":file_str,"line":line,"issues":issues})
        except Exception:
            unannotated.append({"file":file_str,"line":line,"msg":"unreadable"})

    res = {
        "status": "pass" if not unannotated and not quality_issues else "fail",
        "annotated": annotated,
        "missing": len(unannotated),
        "quality_issues_count": len(quality_issues),
        "unannotated": unannotated,
        "quality_issues": quality_issues
    }
    if args.json_only:
        print(json.dumps(res, indent=2))
    else:
        print(json.dumps(res, indent=2))
    sys.exit(0 if res["status"]=="pass" else 1)

if __name__ == "__main__":
    main()
