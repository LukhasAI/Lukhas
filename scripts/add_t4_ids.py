#!/usr/bin/env python3
"""
Add missing 'id' field to TODO[T4-ISSUE] annotations.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TODO_RE = re.compile(r'#\s*TODO\[T4-ISSUE\]\s*:\s*(\{.*\})\s*$')

def add_ids_to_file(filepath):
    """Add id field to all TODO[T4-ISSUE] annotations in a file."""
    content = filepath.read_text()
    lines = content.splitlines(keepends=True)

    new_lines = []
    modified = 0
    file_id = str(filepath.relative_to(REPO_ROOT)).replace("/", "_").replace(".", "_")

    for i, line in enumerate(lines):
        match = TODO_RE.search(line)
        if match:
            try:
                annotation = json.loads(match.group(1))
                if "id" not in annotation:
                    # Add unique ID
                    annotation["id"] = f"{file_id}_L{i+1}"
                    json_str = json.dumps(annotation, ensure_ascii=False)
                    new_line = f"# TODO[T4-ISSUE]: {json_str}\n"
                    new_lines.append(new_line)
                    modified += 1
                    continue
            except json.JSONDecodeError:
                pass

        new_lines.append(line)

    if modified > 0:
        filepath.write_text("".join(new_lines))
        return modified

    return 0


def main():
    """Add IDs to all TODO[T4-ISSUE] annotations in the repository."""
    python_files = []

    for pattern in ["**/*.py"]:
        for path in REPO_ROOT.rglob(pattern):
            if any(excluded in path.parts for excluded in [".git", ".venv", "node_modules", "archive", "quarantine"]):
                continue
            python_files.append(path)

    total_modified = 0
    files_modified = 0

    for filepath in python_files:
        try:
            modified = add_ids_to_file(filepath)
            if modified > 0:
                total_modified += modified
                files_modified += 1
                print(f"✓ {filepath.relative_to(REPO_ROOT)}: {modified} IDs added")
        except Exception as e:
            print(f"✗ Error processing {filepath.relative_to(REPO_ROOT)}: {e}")

    print(f"\n✅ Added {total_modified} IDs in {files_modified} files")


if __name__ == "__main__":
    main()
