"""
Batch annotate B008 (function-call-in-default-argument) violations.

B008: Do not perform function call in argument defaults
Pattern: FastAPI Depends() calls in route function parameters (intentional pattern)
Status: accepted (FastAPI dependency injection requirement)
"""

import json
import subprocess
from pathlib import Path


def get_b008_violations():
    """Get all B008 violations from ruff."""
    result = subprocess.run(
        ["ruff", "check", ".", "--output-format=json"],
        capture_output=True,
        text=True
    )
    if result.returncode in (0, 1):
        violations = json.loads(result.stdout) if result.stdout else []
        return [v for v in violations if v['code'] == 'B008']
    return []


def annotate_file(file_path: Path, violations_by_line: dict):
    """Add inline T4 annotations for B008 violations."""
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"✗ {file_path}: {e}")
        return 0

    changes = 0
    file_id = str(file_path).replace('/', '_').replace('.', '_').replace('-', '_')

    for line_num, violation in violations_by_line.items():
        if line_num > len(lines):
            continue

        line = lines[line_num - 1]

        # Skip if already annotated
        if 'TODO[T4-ISSUE]' in line:
            continue

        # Determine annotation based on message
        if 'Depends' in violation['message']:
            annotation = {
                "code": "B008",
                "ticket": "GH-1031",
                "owner": "matriz-team",
                "status": "accepted",
                "reason": "FastAPI dependency injection - Depends() in route parameters is required pattern",
                "estimate": "0h",
                "priority": "low",
                "dependencies": "none",
                "id": f"{file_id}_L{line_num}"
            }
        else:
            annotation = {
                "code": "B008",
                "ticket": "GH-1031",
                "owner": "consciousness-team",
                "status": "planned",
                "reason": "Function call in default argument - needs review for refactoring",
                "estimate": "30m",
                "priority": "medium",
                "dependencies": "none",
                "id": f"{file_id}_L{line_num}"
            }

        json_str = json.dumps(annotation, separators=(',', ':'), ensure_ascii=False)
        new_line = f"{line.rstrip()}  # TODO[T4-ISSUE]: {json_str}\n"
        lines[line_num - 1] = new_line
        changes += 1

    if changes > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✓ {file_path}: {changes} annotations")

    return changes


def main():
    """Annotate all B008 violations."""
    print("🔍 Finding B008 violations...")
    violations = get_b008_violations()
    print(f"📝 Found {len(violations)} B008 violations")

    # Group by file
    files_violations = {}
    for v in violations:
        file_path = Path(v['filename'])
        line_num = v['location']['row']

        if file_path not in files_violations:
            files_violations[file_path] = {}
        files_violations[file_path][line_num] = v

    total = 0
    for file_path, violations_by_line in files_violations.items():
        total += annotate_file(file_path, violations_by_line)

    print(f"\n✅ Annotated {total} B008 violations")


if __name__ == "__main__":
    main()
