#!/usr/bin/env python3
"""
Convert T4 comment-style annotations to TODO[T4-ISSUE] JSON format.

Converts from:
# TODO[T4-ISSUE]: {"code": "B018", "ticket": "GH-1031", "owner": "matriz-team", "status": "accepted", "reason": "Module export validation - __all__ check for dynamic adapter loading", "estimate": "0h", "priority": "low", "dependencies": "none", "id": "scripts_convert_t4_annotations_py_L6"}

To:
# TODO[T4-ISSUE]: {"code": "B018", "ticket": "GH-1031", "owner": "matriz-team", "status": "accepted", "reason": "Module export validation - __all__ check for dynamic adapter loading", "estimate": "0h", "priority": "low", "dependencies": "none", "id": "scripts_convert_t4_annotations_py_L9"}
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def parse_multiline_annotation(lines, start_idx):
    """Parse multi-line T4 annotation starting at start_idx."""
    if not lines[start_idx].strip().startswith("# T4:"):
        return None, 0

    annotation = {}
    line_count = 0
    current_idx = start_idx

    # Parse first line: # T4: code=X | ticket=Y | ...
    first_line = lines[current_idx].strip()[5:].strip()  # Remove "# T4:"
    for part in first_line.split("|"):
        if "=" in part:
            key, value = part.split("=", 1)
            annotation[key.strip()] = value.strip()
    line_count += 1
    current_idx += 1

    # Parse continuation lines
    while current_idx < len(lines):
        line = lines[current_idx].strip()
        if not line.startswith("#"):
            break

        # Remove leading "# " and parse
        content = line[1:].strip()
        if ":" in content and not content.startswith("TODO"):
            key, value = content.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Handle multi-value fields like "estimate: 0h | priority: low"
            if "|" in value:
                for part in value.split("|"):
                    if ":" in part:
                        sub_key, sub_value = part.split(":", 1)
                        annotation[sub_key.strip()] = sub_value.strip()
                    else:
                        annotation[key] = value.split("|")[0].strip()
            else:
                annotation[key] = value

        line_count += 1
        current_idx += 1

    return annotation, line_count


def convert_file(filepath):
    """Convert all T4 annotations in a file."""
    content = filepath.read_text()
    lines = content.splitlines(keepends=True)

    new_lines = []
    i = 0
    converted = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a T4 annotation
        if line.strip().startswith("# T4:"):
            annotation, line_count = parse_multiline_annotation(lines, i)

            if annotation:
                # Add unique ID if missing
                if "id" not in annotation:
                    # Generate ID from filepath and line number
                    file_id = str(filepath.relative_to(REPO_ROOT)).replace("/", "_").replace(".", "_")
                    annotation["id"] = f"{file_id}_L{i+1}"

                # Create JSON annotation
                json_str = json.dumps(annotation, ensure_ascii=False)
                new_line = f"# TODO[T4-ISSUE]: {json_str}\n"
                new_lines.append(new_line)
                converted += 1

                # Skip original annotation lines
                i += line_count
                continue

        new_lines.append(line)
        i += 1

    if converted > 0:
        filepath.write_text("".join(new_lines))
        return converted

    return 0


def main():
    """Convert all T4 annotations in the repository."""
    python_files = []

    for pattern in ["**/*.py"]:
        for path in REPO_ROOT.rglob(pattern):
            # Skip excluded directories
            if any(excluded in path.parts for excluded in [".git", ".venv", "node_modules", "archive", "quarantine"]):
                continue
            python_files.append(path)

    total_converted = 0
    files_modified = 0

    for filepath in python_files:
        try:
            converted = convert_file(filepath)
            if converted > 0:
                total_converted += converted
                files_modified += 1
                print(f"✓ {filepath.relative_to(REPO_ROOT)}: {converted} annotations")
        except Exception as e:
            print(f"✗ Error processing {filepath.relative_to(REPO_ROOT)}: {e}")

    print(f"\n✅ Converted {total_converted} annotations in {files_modified} files")


if __name__ == "__main__":
    main()
