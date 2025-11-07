"""
Move TODO[T4-ISSUE] annotations from separate lines to inline with the violation.

The T4 system expects annotations on the SAME LINE as the violation, not on a separate line.
"""

import json
import re
import subprocess
from pathlib import Path


def get_violations():
    """Get all ruff violations with their exact line numbers."""
    result = subprocess.run(
        ["ruff", "check", ".", "--output-format=json"],
        capture_output=True,
        text=True
    )
    if result.returncode in (0, 1):  # 0 = no violations, 1 = violations found
        return json.loads(result.stdout) if result.stdout else []
    return []

def inline_annotations_in_file(file_path: Path, violations_by_line: dict):
    """Move annotations from line before to inline with the violation."""
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"✗ {file_path}: read error: {e}")
        return 0

    annotation_pattern = re.compile(r'^#\s*TODO\[T4-ISSUE\]:\s*(\{.*\})\s*$')
    changes = 0
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = annotation_pattern.match(line.strip())

        # Check if this line is an annotation on its own line
        if match and i + 1 < len(lines):
            annotation_json = match.group(1)
            next_line = lines[i + 1]
            next_line_num = i + 2  # 1-indexed

            # Check if the next line has a violation
            if next_line_num in violations_by_line:
                # Move annotation inline with the next line
                next_line_stripped = next_line.rstrip()
                inline_line = f"{next_line_stripped}  # TODO[T4-ISSUE]: {annotation_json}\n"
                new_lines.append(inline_line)
                changes += 1
                i += 2  # Skip both annotation line and next line
                continue

        new_lines.append(line)
        i += 1

    if changes > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✓ {file_path}: {changes} annotations inlined")

    return changes

def main():
    """Inline all TODO[T4-ISSUE] annotations in the repository."""
    print("🔍 Getting violations from ruff...")
    violations = get_violations()

    # Group violations by file and line
    files_with_violations = {}
    for v in violations:
        file_path = Path(v['filename'])
        line_num = v['location']['row']

        if file_path not in files_with_violations:
            files_with_violations[file_path] = {}
        files_with_violations[file_path][line_num] = v

    print(f"📝 Found {len(violations)} violations in {len(files_with_violations)} files")

    total_changes = 0
    for file_path, violations_by_line in files_with_violations.items():
        changes = inline_annotations_in_file(file_path, violations_by_line)
        total_changes += changes

    print(f"\n✅ Inlined {total_changes} annotations")

if __name__ == "__main__":
    main()
