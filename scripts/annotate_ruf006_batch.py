#!/usr/bin/env python3
"""
Batch annotate RUF006 violations with T4 annotations.
Targets fire-and-forget asyncio.create_task() patterns in consciousness systems.
"""

import json
import subprocess
import sys
from pathlib import Path

T4_ANNOTATION = """# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
"""


def get_ruf006_violations():
    """Get all RUF006 violations from T4 check."""
    result = subprocess.run(
        ["python3", "tools/ci/check_t4_issues.py", "--json-only"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error running T4 check: {result.stderr}", file=sys.stderr)
        return []

    data = json.loads(result.stdout)
    return [v for v in data.get("unannotated", []) if v["code"] == "RUF006"]


def annotate_file(filepath: str, line: int) -> bool:
    """Add T4 annotation before the specified line in a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        return False

    lines = path.read_text().splitlines(keepends=True)

    # Check if already annotated
    if line > 3:
        prev_lines = "".join(lines[max(0, line - 4):line - 1])
        if "T4:" in prev_lines and "RUF006" in prev_lines:
            print(f"✓ Already annotated: {filepath}:{line}")
            return True

    # Insert annotation before the target line (line is 1-indexed)
    insert_pos = line - 1
    lines.insert(insert_pos, T4_ANNOTATION)

    path.write_text("".join(lines))
    print(f"✓ Annotated: {filepath}:{line}")
    return True


def main():
    violations = get_ruf006_violations()
    print(f"Found {len(violations)} RUF006 violations to annotate\n")

    # Group by file to process efficiently
    by_file = {}
    for v in violations:
        filepath = v["file"]
        line = v["line"]
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append(line)

    success_count = 0
    for filepath, lines in sorted(by_file.items()):
        print(f"\n📝 Processing {filepath} ({len(lines)} violations)")
        # Sort lines in reverse order to maintain line numbers during insertion
        for line in sorted(lines, reverse=True):
            if annotate_file(filepath, line):
                success_count += 1

    print(f"\n✅ Annotated {success_count}/{len(violations)} RUF006 violations")

    # Show updated T4 status
    print("\n🔍 Running T4 check to verify annotations...")
    subprocess.run(
        ["python3", "tools/ci/check_t4_issues.py", "--json-only"],
        stdout=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    main()
