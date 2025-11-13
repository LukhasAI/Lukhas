"""
Batch annotate SIM105, E702, and SIM102 violations.

SIM105: Use contextlib.suppress instead of try-except-pass
E702: Multiple statements on one line (compound statement)
SIM102: Use a single if statement instead of nested if statements
"""

import json
import subprocess
from pathlib import Path


def get_violations(codes):
    """Get violations for specified codes from ruff."""
    result = subprocess.run(
        ["ruff", "check", ".", "--output-format=json"], capture_output=True, text=True
    )
    if result.returncode in (0, 1):
        violations = json.loads(result.stdout) if result.stdout else []
        return [v for v in violations if v["code"] in codes]
    return []


def get_annotation_for_code(code, file_id, line_num):
    """Get appropriate annotation for each violation code."""
    annotations = {
        "SIM105": {
            "code": "SIM105",
            "ticket": "GH-1031",
            "owner": "consciousness-team",
            "status": "planned",
            "reason": "try-except-pass pattern - consider contextlib.suppress for clarity",
            "estimate": "10m",
            "priority": "low",
            "dependencies": "contextlib",
            "id": f"{file_id}_L{line_num}",
        },
        "E702": {
            "code": "E702",
            "ticket": "GH-1031",
            "owner": "consciousness-team",
            "status": "planned",
            "reason": "Multiple statements on one line - split for readability",
            "estimate": "5m",
            "priority": "low",
            "dependencies": "none",
            "id": f"{file_id}_L{line_num}",
        },
        "SIM102": {
            "code": "SIM102",
            "ticket": "GH-1031",
            "owner": "consciousness-team",
            "status": "planned",
            "reason": "Nested if statements - can be collapsed with 'and' operator",
            "estimate": "5m",
            "priority": "low",
            "dependencies": "none",
            "id": f"{file_id}_L{line_num}",
        },
    }
    return annotations.get(code)


def annotate_file(file_path: Path, violations_by_line: dict):
    """Add inline T4 annotations for violations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"✗ {file_path}: {e}")
        return 0

    changes = 0
    file_id = str(file_path).replace("/", "_").replace(".", "_").replace("-", "_")

    for line_num, violation in violations_by_line.items():
        if line_num > len(lines):
            continue

        line = lines[line_num - 1]

        # Skip if already annotated
        if "TODO[T4-ISSUE]" in line:
            continue

        annotation = get_annotation_for_code(violation["code"], file_id, line_num)
        if not annotation:
            continue

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
    """Annotate all SIM105, E702, and SIM102 violations."""
    codes = ["SIM105", "E702", "SIM102"]
    print(f"🔍 Finding {', '.join(codes)} violations...")
    violations = get_violations(codes)

    # Count by code
    code_counts = {}
    for v in violations:
        code = v["code"]
        code_counts[code] = code_counts.get(code, 0) + 1

    print(
        f"📝 Found violations: {', '.join(f'{code}: {count}' for code, count in sorted(code_counts.items()))}"
    )

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

    print(f"\n✅ Annotated {total} violations")


if __name__ == "__main__":
    main()
