#!/usr/bin/env python3
"""
T4 TODO Marker - Annotate remaining TODO items with context and suggestions.

This script scans for TODO[T4-*] markers and enriches them with additional context,
suggestions, and tracking information.
"""

import argparse
import os
import re
import sys
from pathlib import Path

import tomli as tomllib


def load_t4_config() -> dict:
    """Load T4 autofix configuration."""
    config_path = Path(".t4autofix.toml")
    if not config_path.exists():
        print("❌ .t4autofix.toml not found. Run from repository root.")
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def find_todo_markers(file_path: str) -> list[dict]:
    """Find all TODO[T4-*] markers in a file."""
    todos = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Match TODO[T4-TYPE]: message patterns
            todo_pattern = r"#\s*TODO\[T4-(\w+)\]:\s*(.+)"
            match = re.search(todo_pattern, line)

            if match:
                todo_type = match.group(1)
                message = match.group(2).strip()

                todos.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "type": todo_type,
                        "message": message,
                        "full_line": line.strip(),
                        "context": get_function_context(lines, line_num),
                    }
                )

    except Exception as e:
        print(f"Warning: Failed to process {file_path}: {e}")

    return todos


def get_function_context(lines: list[str], line_num: int) -> str:
    """Get the function or class context for a TODO marker."""
    # Look backwards for function/class definition
    for i in range(line_num - 2, max(0, line_num - 20), -1):
        line = lines[i].strip()
        if line.startswith("def ") or line.startswith("class "):
            return line.split("(")[0].split(":")[0]
    return "global"


def suggest_autofix_pattern(todo_type: str, message: str, context: str) -> str:
    """Suggest specific autofix patterns based on TODO content."""
    suggestions = []

    # Common patterns and their fixes
    patterns = {
        "list comprehension": "Replace loop with [expr for item in items]",
        "pathlib": "Replace os.path with pathlib.Path",
        "f-string": 'Replace .format() with f"string"',
        "unused variable": "Remove or prefix with underscore",
        "type hint": "Add type annotations",
        "async": "Convert to async/await pattern",
    }

    message_lower = message.lower()
    for pattern, suggestion in patterns.items():
        if pattern in message_lower:
            suggestions.append(suggestion)

    # T4-AUTOFIX specific
    if todo_type == "AUTOFIX":
        if not suggestions:
            suggestions.append("Review code for safe automated transformations")
        suggestions.append("Can be fixed with ⌘⇧, in VS Code")

    # T4-MANUAL specific
    elif todo_type == "MANUAL":
        suggestions.append("Requires human review and decision")
        suggestions.append("Consider breaking into smaller T4-AUTOFIX items")

    # T4-RESEARCH specific
    elif todo_type == "RESEARCH":
        suggestions.append("Investigate options and document findings")
        suggestions.append("May become T4-MANUAL after research")

    # T4-SECURITY specific
    elif todo_type == "SECURITY":
        suggestions.append("Security-sensitive change - extra careful review")
        suggestions.append("Consider security implications and testing")

    return "; ".join(suggestions) if suggestions else "No specific suggestions"


def annotate_file(file_path: str, todos: list[dict], dry_run: bool = False) -> int:
    """Add annotations to TODO markers in a file."""
    if not todos:
        return 0

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return 0

    modifications = 0

    # Process in reverse order to maintain line numbers
    for todo in reversed(todos):
        line_idx = todo["line"] - 1

        # Check if already annotated
        if line_idx + 1 < len(lines) and "# T4-SUGGESTION:" in lines[line_idx + 1]:
            continue  # Already annotated

        # Generate suggestion
        suggest_autofix_pattern(todo["type"], todo["message"], todo["context"])

        # Create annotation comment
        indent = len(lines[line_idx]) - len(lines[line_idx].lstrip())
        annotation = " " * indent + ""

        # Insert annotation after TODO line
        lines.insert(line_idx + 1, annotation)
        modifications += 1

    # Write back if not dry run
    if not dry_run and modifications > 0:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"✅ Annotated {modifications} TODOs in {file_path}")
        except Exception as e:
            print(f"❌ Failed to write {file_path}: {e}")
            return 0
    elif dry_run and modifications > 0:
        print(f"📝 Would annotate {modifications} TODOs in {file_path}")

    return modifications


def generate_todo_report(all_todos: list[dict]) -> str:
    """Generate a comprehensive TODO report."""
    if not all_todos:
        return "No TODOs found."

    # Group by type
    by_type = {}
    for todo in all_todos:
        todo_type = todo["type"]
        if todo_type not in by_type:
            by_type[todo_type] = []
        by_type[todo_type].append(todo)

    # Generate report
    report_lines = [
        "# T4 TODO Analysis Report",
        f"Generated: {os.popen('date -u +%Y-%m-%dT%H:%M:%SZ').read().strip()}",
        "",
        "## Summary",
        f"Total TODOs: {len(all_todos)}",
    ]

    for todo_type, todos in sorted(by_type.items()):
        report_lines.append(f"- T4-{todo_type}: {len(todos)}")

    report_lines.append("")

    # Detailed breakdown
    for todo_type, todos in sorted(by_type.items()):
        report_lines.append("#")
        report_lines.append("")

        for todo in todos[:10]:  # Limit to first 10
            report_lines.append(f"- `{todo['file']}:{todo['line']}` - {todo['message']}")

        if len(todos) > 10:
            report_lines.append(f"- ... and {len(todos) - 10} more")

        report_lines.append("")

    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="T4 TODO Marker - Annotate TODO items with suggestions")
    parser.add_argument("paths", nargs="*", default=["."], help="Paths to scan for TODOs")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report only, no annotations",
    )
    parser.add_argument("--output", help="Write report to file")

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_t4_config()
        scope = config.get("scope", {})
        allow_patterns = scope.get("allow_patterns", [])
        deny_patterns = scope.get("deny_patterns", [])
    except Exception as e:
        print(f"❌ Failed to load T4 config: {e}")
        return 1

    # Find all Python files in allowed paths
    all_todos = []
    total_files = 0
    total_annotations = 0

    for path in args.paths:
        if os.path.isfile(path) and path.endswith(".py"):
            files_to_process = [path]
        else:
            files_to_process = []
            for root, dirs, files in os.walk(path):
                # Skip denied directories
                dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in deny_patterns)]

                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path)

                        # Check if file is allowed
                        allowed = False
                        if allow_patterns:
                            allowed = any(pattern in rel_path for pattern in allow_patterns)
                        else:
                            allowed = True

                        # Check if file is denied
                        denied = any(pattern in rel_path for pattern in deny_patterns)

                        if allowed and not denied:
                            files_to_process.append(file_path)

        # Process each file
        for file_path in files_to_process:
            total_files += 1
            todos = find_todo_markers(file_path)
            all_todos.extend(todos)

            if not args.report_only and todos:
                annotations = annotate_file(file_path, todos, args.dry_run)
                total_annotations += annotations

    # Generate and display report
    report = generate_todo_report(all_todos)

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
        print(f"📊 Report written to {args.output}")
    else:
        print("\n" + "=" * 50)
        print(report)

    # Summary
    print(f"\n🔍 Scanned {total_files} files")
    print(f"📝 Found {len(all_todos)} TODO markers")
    if not args.report_only:
        print(f"💡 Added {total_annotations} suggestions")

    return 0


if __name__ == "__main__":
    sys.exit(main())
