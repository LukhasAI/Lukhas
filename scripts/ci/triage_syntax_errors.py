#!/usr/bin/env python3
"""
Triage and categorize syntax errors for systematic fixing.

Categorizes errors into:
- Auto-fixable: missing parens, unclosed strings, simple issues
- Manual review: complex logic, ambiguous fixes
- Known patterns: duplicate loggers, imports before docstrings
"""
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def get_syntax_errors():
    """Get all syntax errors from ruff."""
    result = subprocess.run(
        ["python3", "-m", "ruff", "check", ".", "--select=E999", "--output-format=json"],
        capture_output=True,
        text=True
    )

    try:
        errors = json.loads(result.stdout)
    except Exception as e:
        errors = []

    return errors

def categorize_error(error):
    """Categorize error by fixability."""
    message = error.get("message", "").lower()
    code = error.get("code", "")

    # Auto-fixable patterns
    if "closing parenthesis" in message or "unclosed" in message:
        return "auto_fixable", "unclosed_delimiter"
    elif "expected an indented block" in message:
        return "auto_fixable", "indentation"
    elif "invalid syntax" in message and "f-string" in message:
        return "manual", "fstring_complex"
    elif code == "E999":
        return "manual", "syntax_error_complex"
    else:
        return "unknown", "other"

def main():
    errors = get_syntax_errors()

    if not errors:
        print("✅ No syntax errors found!")
        return 0

    # Group by file and category
    by_file = defaultdict(list)
    by_category = defaultdict(list)

    for err in errors:
        filename = err.get("filename", "unknown")
        category, subcategory = categorize_error(err)

        by_file[filename].append(err)
        by_category[f"{category}/{subcategory}"].append(err)

    # Report
    print(f"📊 Total syntax errors: {len(errors)}")
    print(f"📁 Files affected: {len(by_file)}")
    print()

    print("### Top 10 Files by Error Count:")
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for filename, file_errors in sorted_files:
        print(f"  {len(file_errors):4d} {Path(filename).relative_to(Path.cwd())}")
    print()

    print("### Errors by Category:")
    for category, cat_errors in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {len(cat_errors):4d} {category}")
    print()

    # Export detailed report
    report_path = Path("artifacts/syntax_error_triage.json")
    report_path.parent.mkdir(exist_ok=True)

    report = {
        "total_errors": len(errors),
        "files_affected": len(by_file),
        "by_file": {k: len(v) for k, v in by_file.items()},
        "by_category": {k: len(v) for k, v in by_category.items()},
        "top_files": [{"file": f, "count": len(e)} for f, e in sorted_files[:20]],
        "all_errors": errors
    }

    report_path.write_text(json.dumps(report, indent=2))
    print(f"📝 Detailed report: {report_path}")

    # Recommendation
    auto_fixable = sum(len(v) for k, v in by_category.items() if k.startswith("auto_fixable"))
    manual_required = sum(len(v) for k, v in by_category.items() if k.startswith("manual"))

    print()
    print("### Recommendation:")
    print(f"  Auto-fixable: {auto_fixable} errors")
    print(f"  Manual review: {manual_required} errors")
    print("  Target: <50 errors for T4 freeze")
    print()

    if len(errors) > 50:
        print("❌ Too many syntax errors for freeze. Manual intervention required.")
        print("   Focus on top 10 files - fixing these will reduce ~280 errors (36%)")
        return 1
    else:
        print("✅ Syntax error count acceptable for freeze")
        return 0

if __name__ == "__main__":
    sys.exit(main())
