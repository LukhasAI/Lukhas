#!/usr/bin/env python3
"""
Module: analyze_ruff_errors.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
LUKHAS Ruff Error Analysis Tool
Categorizes and prioritizes syntax errors from ruff check JSON output
"""

import json
from collections import Counter, defaultdict


def analyze_ruff_errors():
    # Get the JSON data from ruff check (passed via stdin)
    try:
        # Run ruff check and get JSON output
        import subprocess

        result = subprocess.run(
            ["python3", "-m", "ruff", "check", "candidate/", "--output-format=json"], capture_output=True, text=True
        )
        errors_data = (json.loads(result.stdout) if result.stdout else []) if result.returncode != 0 else []
    except Exception as e:
        print(f"Error running ruff check: {e}")
        return

    # Initialize counters
    error_by_type = Counter()
    error_by_file = Counter()
    syntax_errors = []
    style_errors = []
    performance_errors = []
    other_errors = []

    # Categorize errors
    for error in errors_data:
        filename = error["filename"]
        code = error.get("code")
        message = error["message"]

        # Count by file
        error_by_file[filename] += 1

        # Categorize by type
        if code is None:  # Syntax errors have no code
            syntax_errors.append(error)
            if "SyntaxError" in message:
                if "Expected" in message:
                    error_by_type["Syntax: Missing Token"] += 1
                elif "f-string" in message.lower():
                    error_by_type["Syntax: F-String Error"] += 1
                else:
                    error_by_type["Syntax: Other"] += 1
            else:
                error_by_type["Syntax: Parse Error"] += 1
        elif code.startswith("E"):
            style_errors.append(error)
            if code == "E501":
                error_by_type["Style: Line Too Long"] += 1
            else:
                error_by_type[f"Style: {code}"] += 1
        elif code.startswith("PERF"):
            performance_errors.append(error)
            error_by_type[f"Performance: {code}"] += 1
        else:
            other_errors.append(error)
            error_by_type[f"Other: {code}"] += 1

    # Print analysis
    print("# LUKHAS Codebase Ruff Error Analysis")
    print("=" * 50)
    print()

    print("## 1. SUMMARY STATISTICS")
    print(f"Total Errors: {len(errors_data)}")
    print(f"- Syntax Errors: {len(syntax_errors)} (CRITICAL)")
    print(f"- Style Errors: {len(style_errors)} (LOW)")
    print(f"- Performance Issues: {len(performance_errors)} (MEDIUM)")
    print(f"- Other Issues: {len(other_errors)} (VARIES)")
    print()

    print("## 2. ERROR BREAKDOWN BY TYPE")
    for error_type, count in error_by_type.most_common():
        priority = "🔴 CRITICAL" if "Syntax" in error_type else "🟡 MEDIUM" if "Performance" in error_type else "🟢 LOW"
        print(f"{priority} {error_type}: {count}")
    print()

    print("## 3. FILES WITH MOST ERRORS (Top 15)")
    for filename, count in error_by_file.most_common(15):
        short_path = filename.replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
        print(f"{count:3d} errors - {short_path}")
    print()

    print("## 4. SYNTAX ERRORS (CRITICAL - FIX FIRST)")
    if syntax_errors:
        syntax_by_file = defaultdict(list)
        for error in syntax_errors:
            short_path = error["filename"].replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
            syntax_by_file[short_path].append(error)

        for filename, file_errors in sorted(syntax_by_file.items()):
            print(f"\n### {filename} ({len(file_errors)} syntax errors)")
            for error in file_errors[:3]:  # Show first 3 per file
                line = error["location"]["row"]
                col = error["location"]["column"]
                msg = error["message"]
                print(f"  Line {line}, Col {col}: {msg}")
            if len(file_errors) > 3:
                print(f"  ... and {len(file_errors) - 3} more syntax errors")
    else:
        print("✅ No syntax errors found!")
    print()

    print("## 5. PRIORITY ASSESSMENT")
    print()
    print("### 🔴 CRITICAL (Fix Immediately)")
    print("- Syntax errors prevent code execution")
    print("- F-string formatting issues")
    print("- Missing brackets/quotes")
    print(f"- Total Critical: {len(syntax_errors)}")
    print()

    print("### 🟡 MEDIUM (Fix Next)")
    print("- Performance issues (PERF codes)")
    print("- Undefined variables (F821)")
    print("- Unused imports/variables")
    print(
        f"- Total Medium: {len(performance_errors) + len([e for e in other_errors if e.get('code', '').startswith('F')])}"
    )
    print()

    print("### 🟢 LOW (Fix When Time Permits)")
    print("- Line length (E501)")
    print("- Code style issues")
    print("- Ambiguous unicode characters")
    print(f"- Total Low: {len(style_errors)}")
    print()

    print("## 6. RECOMMENDED FIX ORDER")
    print("1. Fix all syntax errors (prevents execution)")
    print("2. Fix undefined name errors (F821) - runtime failures")
    print("3. Address performance issues if in hot paths")
    print("4. Clean up style issues with auto-formatters")
    print("5. Review ambiguous unicode characters")

    # Show specific syntax error patterns
    if syntax_errors:
        print()
        print("## 7. COMMON SYNTAX ERROR PATTERNS")

        f_string_errors = [e for e in syntax_errors if "f-string" in e["message"].lower()]
        bracket_errors = [
            e for e in syntax_errors if any(x in e["message"] for x in ["Expected", "found", "bracket", "brace"])
        ]

        if f_string_errors:
            print(f"\n### F-String Errors ({len(f_string_errors)})")
            for error in f_string_errors[:3]:
                short_path = error["filename"].replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
                line = error["location"]["row"]
                print(f"  {short_path}:{line} - {error['message']}")

        if bracket_errors:
            print(f"\n### Bracket/Token Errors ({len(bracket_errors)})")
            for error in bracket_errors[:3]:
                short_path = error["filename"].replace("/Users/agi_dev/LOCAL-REPOS/Lukhas/", "")
                line = error["location"]["row"]
                print(f"  {short_path}:{line} - {error['message']}")


if __name__ == "__main__":
    analyze_ruff_errors()
