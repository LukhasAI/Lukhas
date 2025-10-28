#!/usr/bin/env python3
"""
Generate TODO inventory from codebase.

Parses TODO comments in various formats:
# See: https://github.com/LukhasAI/Lukhas/issues/609
- # TODO: message
# See: https://github.com/LukhasAI/Lukhas/issues/610
- /* TODO: message */

Output CSV: file,line,kind,priority,owner,scope,message

Usage:
    python3 generate_todo_inventory.py --output todo_inventory.csv
    python3 generate_todo_inventory.py --output todo_inventory.csv --priority HIGH
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List

# Patterns to match TODO comments
TODO_PATTERNS = [
    # Python/Shell: # TODO[...]: message
    re.compile(
        r"#\s*TODO\s*(?:\[([^\]]+)\])?\s*(?:\[([^\]]+)\])?\s*(?:\[([^\]]+)\])?\s*:?\s*(.+)",
        re.IGNORECASE,
    ),
    # JS/C/Java: // TODO[...]: message
    re.compile(
        r"//\s*TODO\s*(?:\[([^\]]+)\])?\s*(?:\[([^\]]+)\])?\s*(?:\[([^\]]+)\])?\s*:?\s*(.+)",
        re.IGNORECASE,
    ),
    # C-style: /* TODO: message */
    re.compile(
        r"/\*\s*TODO\s*(?:\[([^\]]+)\])?\s*(?:\[([^\]]+)\])?\s*(?:\[([^\]]+)\])?\s*:?\s*(.+?)\s*\*/",
        re.IGNORECASE,
    ),
]

# Security/safety keywords that require special handling
SECURITY_KEYWORDS = [
    "security",
    "privacy",
    "PII",
    "model-safety",
    "user data",
    "production-only",
    "auth",
    "encryption",
    "credential",
    "token",
    "password",
    "secret",
    "GDPR",
    "compliance",
]


def parse_todo_metadata(match_groups: tuple) -> Dict[str, str]:
    """Parse metadata from TODO comment groups."""
    metadata = {"priority": "MEDIUM", "owner": "", "scope": "", "kind": "TODO"}

    for group in match_groups[:3]:  # First 3 groups are metadata
        if not group:
            continue
        # Parse key:value pairs
        if ":" in group:
            key, value = group.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key in ("priority", "prio", "p"):
                metadata["priority"] = value.upper()
            elif key in ("owner", "assignee", "by"):
                metadata["owner"] = value
            elif key in ("scope", "area"):
                metadata["scope"] = value.upper()
            elif key in ("kind", "type"):
                metadata["kind"] = value.upper()
        else:
            # Assume it's a priority if it's HIGH/MEDIUM/LOW
            group_upper = group.upper()
            if group_upper in ("HIGH", "MEDIUM", "LOW", "CRITICAL"):
                metadata["priority"] = group_upper

    return metadata


def is_security_related(message: str) -> bool:
    """Check if TODO message contains security/safety keywords."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in SECURITY_KEYWORDS)


def scan_file(filepath: Path) -> List[Dict[str, str]]:
    """Scan a file for TODO comments and return structured data."""
    todos = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                for pattern in TODO_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        groups = match.groups()
                        message = groups[-1].strip()  # Last group is always the message
                        metadata = parse_todo_metadata(groups[:-1])

                        # Check for security keywords
                        if is_security_related(message):
                            metadata["scope"] = "SECURITY"
                            if metadata["priority"] == "MEDIUM":
                                metadata["priority"] = "HIGH"

                        todos.append(
                            {
                                "file": str(filepath),
                                "line": str(line_num),
                                "kind": metadata["kind"],
                                "priority": metadata["priority"],
                                "owner": metadata["owner"],
                                "scope": metadata["scope"],
                                "message": message,
                            }
                        )
                        break  # Only match first pattern per line
    except Exception as e:
        print(f"Warning: Could not scan {filepath}: {e}", file=sys.stderr)

    return todos


def main():
    parser = argparse.ArgumentParser(description="Generate TODO inventory from codebase")
    parser.add_argument("--output", default="todo_inventory.csv", help="Output CSV file")
    parser.add_argument(
        "--priority",
        choices=["HIGH", "MEDIUM", "LOW", "CRITICAL"],
        help="Filter by priority",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude patterns (can specify multiple times)",
    )
    parser.add_argument("--root", default=".", help="Root directory to scan")
    args = parser.parse_args()

    # Default exclusions
    default_excludes = [
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        "build",
        "dist",
        "*.egg-info",
        ".tox",
        "*.pyc",
        "*.pyo",
        "*.so",
        "*.dylib",
        ".DS_Store",
    ]
    excludes = set(default_excludes + args.exclude)

    root = Path(args.root).resolve()
    print(f"Scanning {root} for TODOs...", file=sys.stderr)

    all_todos = []
    scanned_count = 0

    # Scan Python, JS, TS, Shell, YAML, MD files
    extensions = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".sh",
        ".bash",
        ".zsh",
        ".yaml",
        ".yml",
        ".md",
    }

    for filepath in root.rglob("*"):
        # Skip if in excluded directory
        if any(exc in str(filepath) for exc in excludes):
            continue

        # Skip if not a file or wrong extension
        if not filepath.is_file() or filepath.suffix not in extensions:
            continue

        scanned_count += 1
        todos = scan_file(filepath)
        all_todos.extend(todos)

    # Filter by priority if specified
    if args.priority:
        all_todos = [t for t in all_todos if t["priority"] == args.priority]

    # Sort by priority (HIGH > MEDIUM > LOW) then by file
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_todos.sort(key=lambda t: (priority_order.get(t["priority"], 4), t["file"]))

    # Write CSV
    with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["file", "line", "kind", "priority", "owner", "scope", "message"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_todos)

    print(f"✅ Scanned {scanned_count} files", file=sys.stderr)
    print(f"✅ Found {len(all_todos)} TODOs", file=sys.stderr)
    print(f"✅ Written to {args.output}", file=sys.stderr)

    # Summary by priority
    by_priority = {}
    for todo in all_todos:
        p = todo["priority"]
        by_priority[p] = by_priority.get(p, 0) + 1

    print("\n📊 Summary by priority:", file=sys.stderr)
    for prio in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = by_priority.get(prio, 0)
        if count > 0:
            print(f"  {prio}: {count}", file=sys.stderr)

    # Warn about security TODOs
    security_count = sum(1 for t in all_todos if t["scope"] == "SECURITY")
    if security_count > 0:
        print(
            f"\n⚠️  {security_count} TODOs flagged as SECURITY-related (require special review)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
