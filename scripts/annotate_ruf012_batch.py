"""
Batch annotate RUF012 (mutable class attributes) violations.

RUF012: Mutable class attributes should be annotated with typing.ClassVar
Pattern: Class-level mutable defaults (lists, dicts) without ClassVar annotation
Status: planned (type annotations need review)
"""

import json
import subprocess
from pathlib import Path


def get_ruf012_violations():
    """Get all RUF012 violations from ruff."""
    result = subprocess.run(
        ["ruff", "check", ".", "--output-format=json"], capture_output=True, text=True
    )
    if result.returncode in (0, 1):
        violations = json.loads(result.stdout) if result.stdout else []
        return [v for v in violations if v["code"] == "RUF012"]
    return []


def annotate_file(file_path: Path, violations_by_line: dict):
    """Add inline T4 annotations for RUF012 violations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"✗ {file_path}: {e}")
        return 0

    changes = 0
    file_id = str(file_path).replace("/", "_").replace(".", "_").replace("-", "_")

    for line_num in violations_by_line:
        if line_num > len(lines):
            continue

        line = lines[line_num - 1]

        # Skip if already annotated
        if "TODO[T4-ISSUE]" in line:
            continue

        annotation = {
            "code": "RUF012",
            "ticket": "GH-1031",
            "owner": "consciousness-team",
            "status": "planned",
            "reason": "Mutable class attribute needs ClassVar annotation for type safety",
            "estimate": "15m",
            "priority": "medium",
            "dependencies": "typing imports",
            "id": f"{file_id}_L{line_num}",
        }

        json_str = json.dumps(annotation, separators=(",", ":"), ensure_ascii=False)
        new_line = f"{line.rstrip()}  # TODO[T4-ISSUE]: {json_str}\n"
        lines[line_num - 1] = new_line
        changes += 1

    if changes > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✓ {file_path}: {changes} annotations")

    return changes


def main():
    """Annotate all RUF012 violations."""
    print("🔍 Finding RUF012 violations...")
    violations = get_ruf012_violations()
    print(f"📝 Found {len(violations)} RUF012 violations")

    # Group by file
    files_violations = {}
    for v in violations:
        file_path = Path(v["filename"])
        line_num = v["location"]["row"]

        if file_path not in files_violations:
            files_violations[file_path] = {}
        files_violations[file_path][line_num] = v

    total = 0
    for file_path, violations_by_line in files_violations.items():
        total += annotate_file(file_path, violations_by_line)

    print(f"\n✅ Annotated {total} RUF012 violations")


if __name__ == "__main__":
    main()
