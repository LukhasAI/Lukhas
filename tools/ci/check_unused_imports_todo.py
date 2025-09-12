#!/usr/bin/env python3
"""
🔍 T4 UNUSED IMPORTS VALIDATOR - Production Lane Policy Enforcement

Validates that all unused imports in production lanes are properly annotated.

- Runs ruff F401 to find unused imports in lukhas/ MATRIZ/ (production only)
- Checks each finding has a TODO[T4-UNUSED-IMPORT] annotation
- Outputs JSON report for CI/CD integration
- Enforces production lane policy (candidate/ experimental code exempt)
- Returns exit code 0 if all production imports properly annotated

⚛️ LUKHAS AI Trinity Framework Integration:
- 🧠 Consciousness: Validates conscious decisions about import preservation
- ⚛️ Identity: Ensures production code maintains identity standards
- 🛡️ Guardian: Protects production lanes from undocumented technical debt

Usage:
    python3 tools/ci/check_unused_imports_todo.py                    # Default: all production dirs
    python3 tools/ci/check_unused_imports_todo.py --paths lukhas     # Only lukhas/
    python3 tools/ci/check_unused_imports_todo.py --json-only        # Only JSON output
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
import re

# Repository structure
REPO = Path(__file__).resolve().parents[2]
TODO_TAG = "TODO[T4-UNUSED-IMPORT]"
INLINE_PATTERN = re.compile(rf"#\s*{re.escape(TODO_TAG)}")

# Production vs Experimental separation
SKIP_DIRS = {".git", ".venv", "node_modules", "archive", "quarantine", "candidate", "reports"}


def ruff_F401(paths):
    """Run ruff F401 on selected paths; return list[(abs_path, line, message)]."""
    cmd = ["python3", "-m", "ruff", "check", "--select", "F401", "--output-format", "json"] + list(paths)

    try:
        result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)

        if result.returncode not in (0, 1):  # 0 = clean, 1 = findings
            return {"error": f"ruff failed: {result.stderr or result.stdout}"}

        items = json.loads(result.stdout or "[]")

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        return {"error": f"Failed to run ruff or parse output: {e}"}

    findings = []
    for item in items:
        file_path = (REPO / item["filename"]).resolve()

        # Skip if any path segment is in SKIP_DIRS
        path_parts = set(Path(file_path).parts)
        if path_parts & SKIP_DIRS:
            continue

        findings.append(
            {
                "file": str(file_path.relative_to(REPO)),
                "line": item["location"]["row"],
                "message": item["message"],
                "abs_path": str(file_path),
            }
        )

    return {"findings": findings}


def check_annotation(file_path: str, line_no: int) -> bool:
    """Check if line has TODO[T4-UNUSED-IMPORT] annotation."""
    try:
        file_obj = Path(file_path)
        lines = file_obj.read_text(encoding="utf-8", errors="ignore").splitlines()

        idx = line_no - 1
        if idx < 0 or idx >= len(lines):
            return False

        return bool(INLINE_PATTERN.search(lines[idx]))

    except Exception:
        return False


def main():
    """Main T4 unused imports validator with production lane focus."""
    parser = argparse.ArgumentParser(
        description="T4 Unused Imports Validator - Production Lane Policy Enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/ci/check_unused_imports_todo.py                    # Default: lukhas MATRIZ
  python3 tools/ci/check_unused_imports_todo.py --paths lukhas     # Only lukhas/
  python3 tools/ci/check_unused_imports_todo.py --json-only        # Only JSON output
        """,
    )

    parser.add_argument(
        "--paths",
        nargs="+",
        default=["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"],
        help="Roots to validate (default: lukhas core api consciousness memory identity MATRIZ). 'candidate' is always skipped.",
    )
    parser.add_argument("--json-only", action="store_true", help="Output only JSON for CI/CD integration")

    args = parser.parse_args()

    # Resolve and filter paths that actually exist; skip disallowed roots
    valid_roots = []
    for path_arg in args.paths:
        if path_arg.strip() in SKIP_DIRS or path_arg.strip() == "candidate":
            continue

        abs_path = (REPO / path_arg).resolve()
        if abs_path.exists():
            rel_path = str(abs_path.relative_to(REPO))
            valid_roots.append(rel_path)

    if not valid_roots:
        result = {
            "status": "error",
            "message": "No valid production roots to validate",
            "unannotated": [],
            "summary": {"total": 0, "annotated": 0, "missing": 0},
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    if not args.json_only:
        print("🔍 T4 UNUSED IMPORTS VALIDATOR - Production Lane Policy")
        print("=" * 60)
        print(f"📁 Validating paths: {', '.join(valid_roots)}")

    # Get F401 findings
    ruff_result = ruff_F401(valid_roots)

    if "error" in ruff_result:
        result = {
            "status": "error",
            "message": ruff_result["error"],
            "unannotated": [],
            "summary": {"total": 0, "annotated": 0, "missing": 0},
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    findings = ruff_result["findings"]

    if not args.json_only:
        print(f"📊 Found {len(findings)} unused imports in production lanes")

    # Check annotations
    unannotated = []
    annotated_count = 0

    for finding in findings:
        has_annotation = check_annotation(finding["abs_path"], finding["line"])

        if has_annotation:
            annotated_count += 1
        else:
            unannotated.append({"file": finding["file"], "line": finding["line"], "message": finding["message"]})

    # Generate result
    total = len(findings)
    missing = len(unannotated)

    result = {
        "status": "pass" if missing == 0 else "fail",
        "message": f"Production lane policy: {annotated_count}/{total} imports properly annotated",
        "unannotated": unannotated,
        "summary": {"total": total, "annotated": annotated_count, "missing": missing},
    }

    # Output
    if args.json_only:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n📈 PRODUCTION LANE VALIDATION:")
        print(f"✅ Properly annotated: {annotated_count}")
        print(f"❌ Missing annotations: {missing}")

        if unannotated:
            print(f"\n🚨 UNANNOTATED IMPORTS (Production Lane Policy Violation):")
            for item in unannotated:
                print(f"  - {item['file']}:{item['line']} - {item['message']}")
            print(f"\n💡 Fix with: python3 tools/ci/mark_unused_imports_todo.py")
        else:
            print(f"\n🎯 All production lane imports properly documented!")

        print(f"\n📝 JSON Report:")
        print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if missing == 0 else 1)


if __name__ == "__main__":
    main()


def main():
    """Check that all unused imports are annotated with T4 TODO tags."""

    # Run ruff to get F401 findings
    cmd = ["python3", "-m", "ruff", "check", "--select", "F401", "--output-format", "json", "."]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode not in (0, 1):
            print(f"❌ ruff error: {result.stderr or result.stdout}", file=sys.stderr)
            return result.returncode

        findings = json.loads(result.stdout or "[]")

    except Exception as e:
        print(f"❌ Error running ruff check: {e}", file=sys.stderr)
        return 1

    # Check each finding for T4 annotation
    unannotated = []

    for finding in findings:
        file_path = pathlib.Path(finding["filename"])
        line_no = finding["location"]["row"]
        message = finding["message"]

        try:
            lines = file_path.read_text().splitlines()
            if line_no <= len(lines):
                line_content = lines[line_no - 1]

                if not TODO_PATTERN.search(line_content):
                    unannotated.append(f"{file_path}:{line_no} {message}")
            else:
                unannotated.append(f"{file_path}:{line_no} {message} (line out of range)")

        except Exception:
            unannotated.append(f"{file_path}:{line_no} {message} (unreadable)")

    # Report results
    if unannotated:
        print("❌ UNANNOTATED UNUSED IMPORTS FOUND:")
        print("These F401 errors must be annotated with TODO[T4-UNUSED-IMPORT] tags:")
        print()
        for error in unannotated:
            print(f"  {error}")
        print()
        print("🔧 Fix with: python3 tools/ci/mark_unused_imports_todo.py")
        return 1
    else:
        total_annotated = len(findings)
        if total_annotated > 0:
            print(f"✅ OK: All {total_annotated} unused imports are properly annotated with T4 TODO tags.")
        else:
            print("✅ OK: No unused imports found.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
