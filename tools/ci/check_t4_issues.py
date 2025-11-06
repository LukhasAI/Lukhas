#!/usr/bin/env python3
"""
T4 Unified Validator - Production Lane Policy Enforcement

Validates TODO[T4-ISSUE] annotations across all violation types (F401, F821, B008, etc.).
Merges functionality from check_unused_imports_todo.py and check_lint_issues_todo.py.

Features:
- Validates unified TODO[T4-ISSUE] JSON annotations
- Accepts legacy formats but flags them as low-quality
- Computes weighted annotation quality score
- Enforces owner+ticket for planned/committed status
- Outputs comprehensive JSON metrics for CI/CD and dashboards

Usage:
  python3 tools/ci/check_t4_issues.py --paths lukhas core --json-only
  python3 tools/ci/check_t4_issues.py --paths lukhas --codes F821,F401,B008 --strict
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UNIFIED_TAG = "TODO[T4-ISSUE]"
UNIFIED_JSON_RE = re.compile(rf"#\s*{re.escape(UNIFIED_TAG)}\s*:\s*(\{{.*\}})\s*$")

# Legacy patterns (accepted but flagged as low-quality)
LEGACY_UNUSED_IMPORT = re.compile(r"#\s*TODO\[T4-UNUSED-IMPORT\]")
LEGACY_LINT_ISSUE = re.compile(r"#\s*TODO\[T4-LINT-ISSUE\]")

SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "labs", "reports"}
WAIVERS = REPO_ROOT / "AUDIT" / "waivers" / "unused_imports.yaml"

# Severity weights for quality scoring
SEVERITY_WEIGHTS = {
    "F821": 3,  # Undefined name - critical
    "F401": 3,  # Unused import - critical
    "B904": 2,  # Exception handling - high
    "B008": 2,  # Function call in default - high
    "RUF006": 2,  # Async task tracking - high
    "SIM102": 1,  # Collapsible if - medium
    "SIM105": 1,  # Contextlib suppress - medium
    "E702": 1,  # Multiple statements - low
    "B018": 1,  # Useless expression - low
}


def load_waivers() -> dict[str, set[int]]:
    """Load file/line waivers from YAML."""
    try:
        import yaml
    except ImportError:
        return {}

    if not WAIVERS.exists():
        return {}

    try:
        data = yaml.safe_load(WAIVERS.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

    waivers: dict[str, set[int]] = {}
    for item in data.get("waivers", []):
        file_path = (REPO_ROOT / item["file"]).resolve()
        waivers.setdefault(str(file_path), set()).add(int(item.get("line", 0)))

    return waivers


def parse_unified_annotation(line: str) -> dict | None:
    """Parse unified TODO[T4-ISSUE] JSON annotation."""
    match = UNIFIED_JSON_RE.search(line)
    if not match:
        return None

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def is_legacy_annotation(line: str) -> bool:
    """Check if line has legacy annotation format."""
    return bool(LEGACY_UNUSED_IMPORT.search(line) or LEGACY_LINT_ISSUE.search(line))


def validate_annotation(annotation: dict, code: str) -> list[str]:
    """
    Validate annotation structure and return list of quality issues.

    Rules:
    - Must have: id, code, reason, status
    - For planned/committed: must have owner+ticket
    - Reason cannot be generic
    """
    issues = []

    if not isinstance(annotation, dict):
        issues.append("annotation is not a JSON object")
        return issues

    # Required fields
    if not annotation.get("id"):
        issues.append("missing id field")

    if not annotation.get("code"):
        issues.append("missing code field")

    if not annotation.get("status"):
        issues.append("missing status field")

    # Reason validation
    reason = annotation.get("reason", "").strip().lower()
    generic_reasons = {
        "kept for future",
        "kept for future use",
        "kept for future use.",
        "todo",
        "fix me",
        "fixme",
    }

    if not reason:
        issues.append("missing or empty reason")
    elif reason in generic_reasons:
        issues.append(f"generic reason: '{reason}' - provide specific context")

    # Status-specific validation
    status = annotation.get("status")
    if status in ("planned", "committed"):
        if not annotation.get("owner"):
            issues.append(f"status='{status}' requires owner field")
        if not annotation.get("ticket"):
            issues.append(f"status='{status}' requires ticket field")

    # Code mismatch check
    if annotation.get("code") != code and annotation.get("code") != "UNKNOWN":
        issues.append(f"annotation code '{annotation.get('code')}' != ruff code '{code}'")

    return issues


def run_ruff(paths: list[str], codes: list[str] | None = None) -> dict:
    """Run ruff check and return structured findings."""
    code_selector = ",".join(codes) if codes else "F401,F821,B008,B904,B018,SIM102,SIM105,E701,E702,RUF006,RUF012"

    cmd = [
        "python3", "-m", "ruff", "check",
        "--select", code_selector,
        "--output-format", "json",
        *paths
    ]

    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    if proc.returncode not in (0, 1):  # 0=clean, 1=findings
        return {"error": f"ruff failed: {proc.stderr or proc.stdout}"}

    try:
        items = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse ruff output: {e}"}

    # Filter out skipped directories
    findings = []
    for item in items:
        file_path = (REPO_ROOT / item["filename"]).resolve()

        if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
            continue

        findings.append({
            "file": str(file_path.relative_to(REPO_ROOT)),
            "abs_path": str(file_path),
            "line": item["location"]["row"],
            "code": item["code"],
            "message": item["message"],
        })

    return {"findings": findings}


def compute_weighted_quality_score(annotations: list[dict]) -> dict:
    """
    Compute weighted annotation quality score with detailed breakdown.

    Quality = (weighted_good / weighted_total) * 100

    Good = has owner+ticket OR status not in (planned, committed)
    Weighted by severity of violation code
    """
    if not annotations:
        return {
            "score": 100.0,
            "weighted_good": 0,
            "weighted_total": 0,
            "breakdown": {
                "missing_owner": [],
                "missing_ticket": [],
                "generic_reason": [],
                "files_by_quality": {}
            }
        }

    weighted_good = 0
    weighted_total = 0
    missing_owner = []
    missing_ticket = []
    generic_reason = []
    file_quality = {}

    for annot in annotations:
        code = annot.get("code", "UNKNOWN")
        weight = SEVERITY_WEIGHTS.get(code, 1)
        weighted_total += weight

        status = annot.get("status")
        has_owner = bool(annot.get("owner"))
        has_ticket = bool(annot.get("ticket"))
        reason = annot.get("reason", "")
        file_path = annot.get("file", "unknown")
        line_num = annot.get("line", 0)

        # Track quality issues per file
        if file_path not in file_quality:
            file_quality[file_path] = {"good": 0, "total": 0, "weight": 0}
        file_quality[file_path]["total"] += 1
        file_quality[file_path]["weight"] += weight

        # Good if: (not planned/committed) OR (has both owner+ticket)
        is_good = status not in ("planned", "committed") or (has_owner and has_ticket)

        if is_good:
            weighted_good += weight
            file_quality[file_path]["good"] += 1
        else:
            # Track specific quality issues
            if status in ("planned", "committed"):
                if not has_owner:
                    missing_owner.append({
                        "file": file_path,
                        "line": line_num,
                        "code": code,
                        "status": status,
                        "id": annot.get("id", "UNKNOWN")
                    })
                if not has_ticket:
                    missing_ticket.append({
                        "file": file_path,
                        "line": line_num,
                        "code": code,
                        "status": status,
                        "id": annot.get("id", "UNKNOWN")
                    })

        # Check for generic reasons
        if any(generic in reason.lower() for generic in [
            "kept for future", "reserved", "todo", "fixme", "placeholder"
        ]):
            generic_reason.append({
                "file": file_path,
                "line": line_num,
                "code": code,
                "reason": reason,
                "id": annot.get("id", "UNKNOWN")
            })

    score = 100.0 * weighted_good / weighted_total if weighted_total > 0 else 100.0

    # Sort files by quality issues (worst first)
    files_by_quality = sorted(
        [(path, data["total"] - data["good"], data["weight"]) for path, data in file_quality.items()],
        key=lambda x: (x[1], x[2]),
        reverse=True
    )[:10]  # Top 10 worst files

    return {
        "score": round(score, 2),
        "weighted_good": weighted_good,
        "weighted_total": weighted_total,
        "breakdown": {
            "missing_owner_count": len(missing_owner),
            "missing_owner": missing_owner[:10],  # Top 10
            "missing_ticket_count": len(missing_ticket),
            "missing_ticket": missing_ticket[:10],  # Top 10
            "generic_reason_count": len(generic_reason),
            "generic_reason": generic_reason[:10],  # Top 10
            "files_by_quality": [
                {"file": path, "issues": issues, "weight": weight}
                for path, issues, weight in files_by_quality
            ],
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate T4 unified annotations and compute metrics"
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"],
        help="Paths to validate (default: production lanes)"
    )
    parser.add_argument(
        "--codes",
        help="Comma-separated lint codes to check (default: all common codes)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output JSON only (no human-readable text)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error on any unannotated or low-quality findings"
    )
    args = parser.parse_args()

    # Parse codes
    codes = args.codes.split(",") if args.codes else None

    # Validate paths exist
    valid_paths = []
    for path_str in args.paths:
        if path_str.strip() in SKIP_DIRS:
            continue

        abs_path = (REPO_ROOT / path_str).resolve()
        if abs_path.exists():
            valid_paths.append(str(abs_path.relative_to(REPO_ROOT)))

    if not valid_paths:
        result = {
            "status": "error",
            "message": "No valid production paths to validate",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Load waivers
    waivers = load_waivers()

    # Run ruff
    ruff_result = run_ruff(valid_paths, codes)

    if "error" in ruff_result:
        result = {
            "status": "error",
            "message": ruff_result["error"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    findings = ruff_result["findings"]

    # Process each finding
    unannotated = []
    legacy_annotations = []
    quality_issues = []
    valid_annotations = []

    counts_by_code: dict[str, int] = {}
    counts_by_status: dict[str, int] = {}

    for finding in findings:
        file_abs = Path(finding["abs_path"])
        code = finding["code"]
        line_num = finding["line"]

        # Count by code
        counts_by_code[code] = counts_by_code.get(code, 0) + 1

        # Check waivers
        if str(file_abs) in waivers:
            waiver_lines = waivers[str(file_abs)]
            if 0 in waiver_lines or line_num in waiver_lines:
                continue  # Waived

        # Read line
        try:
            lines = file_abs.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line_num < 1 or line_num > len(lines):
                unannotated.append({
                    "file": finding["file"],
                    "line": line_num,
                    "code": code,
                    "message": "line out of range"
                })
                continue

            line_content = lines[line_num - 1]
        except Exception as e:
            unannotated.append({
                "file": finding["file"],
                "line": line_num,
                "code": code,
                "message": f"unreadable: {e}"
            })
            continue

        # Parse annotation
        annotation = parse_unified_annotation(line_content)

        if annotation:
            # Valid unified annotation - add file/line context
            annotation_with_context = annotation.copy()
            annotation_with_context["file"] = finding["file"]
            annotation_with_context["line"] = line_num
            valid_annotations.append(annotation_with_context)

            # Count by status
            status = annotation.get("status", "unknown")
            counts_by_status[status] = counts_by_status.get(status, 0) + 1

            # Validate quality
            issues = validate_annotation(annotation, code)
            if issues:
                quality_issues.append({
                    "file": finding["file"],
                    "line": line_num,
                    "code": code,
                    "annotation_id": annotation.get("id"),
                    "issues": issues
                })

        elif is_legacy_annotation(line_content):
            # Legacy annotation detected
            legacy_annotations.append({
                "file": finding["file"],
                "line": line_num,
                "code": code,
                "message": "legacy annotation format - migrate to TODO[T4-ISSUE]"
            })

        else:
            # Unannotated
            unannotated.append({
                "file": finding["file"],
                "line": line_num,
                "code": code,
                "message": finding["message"]
            })

    # Compute metrics
    total_findings = len(findings)
    annotated_count = len(valid_annotations) + len(legacy_annotations)
    missing_count = len(unannotated)

    quality_score_data = compute_weighted_quality_score(valid_annotations)

    # Build result
    result = {
        "status": "pass" if missing_count == 0 and not quality_issues else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_findings": total_findings,
            "annotated": annotated_count,
            "unannotated": missing_count,
            "legacy_format": len(legacy_annotations),
            "quality_issues": len(quality_issues),
        },
        "metrics": {
            "annotation_quality_score": quality_score_data["score"],
            "weighted_good": quality_score_data["weighted_good"],
            "weighted_total": quality_score_data["weighted_total"],
            "quality_breakdown": quality_score_data["breakdown"],
            "counts_by_code": counts_by_code,
            "counts_by_status": counts_by_status,
        },
        "unannotated": unannotated,
        "legacy_annotations": legacy_annotations,
        "quality_issues": quality_issues,
    }

    # Output
    if args.json_only:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "="*60)
        print("🔍 T4 UNIFIED VALIDATOR - Production Lane Policy")
        print("="*60)
        print(json.dumps(result, indent=2))
        print("="*60)

        if result["status"] == "pass":
            print("✅ All findings properly annotated!")
        else:
            print(f"⚠️  {missing_count} unannotated + {len(quality_issues)} quality issues")
            print("💡 Run migrate_annotations.py for legacy formats")
            print("💡 Add owner+ticket for planned/committed items")

        # Quality breakdown summary
        breakdown = quality_score_data["breakdown"]
        if breakdown["missing_owner_count"] or breakdown["missing_ticket_count"] or breakdown["generic_reason_count"]:
            print("\n📊 Quality Score Breakdown:")
            print(f"   Score: {quality_score_data['score']:.1f}% " +
                  f"({quality_score_data['weighted_good']}/{quality_score_data['weighted_total']} weighted)")

            if breakdown["missing_owner_count"]:
                print(f"\n   ❌ Missing Owner: {breakdown['missing_owner_count']} annotations")
                for item in breakdown["missing_owner"][:3]:
                    print(f"      • {item['file']}:{item['line']} ({item['code']}) - {item['id']}")

            if breakdown["missing_ticket_count"]:
                print(f"\n   ❌ Missing Ticket: {breakdown['missing_ticket_count']} annotations")
                for item in breakdown["missing_ticket"][:3]:
                    print(f"      • {item['file']}:{item['line']} ({item['code']}) - {item['id']}")

            if breakdown["generic_reason_count"]:
                print(f"\n   ⚠️  Generic Reason: {breakdown['generic_reason_count']} annotations")
                for item in breakdown["generic_reason"][:3]:
                    print(f"      • {item['file']}:{item['line']}: \"{item['reason'][:50]}...\"")

            if breakdown["files_by_quality"]:
                print("\n   📁 Files Needing Attention (Top 5):")
                for file_data in breakdown["files_by_quality"][:5]:
                    print(f"      • {file_data['file']}: {file_data['issues']} issues " +
                          f"(weight: {file_data['weight']})")

    # Exit code
    if args.strict:
        sys.exit(0 if result["status"] == "pass" else 1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
