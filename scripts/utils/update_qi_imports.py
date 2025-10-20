#!/usr/bin/env python3
"""Module docstring."""
import os
import re


def update_file(filepath):
    """Update imports in a single file."""
    with open(filepath) as f:
        content = f.read()

    original = content

    # Update import patterns
    patterns = [
        (r"from qim\.", "from qi."),
        (r"import qi\.", "import qi."),
        (r"from qi ", "from qi "),
        (r"import qi\b", "import qi"),
        (r"from quantum\.", "from qi."),
        (r"import qi\.", "import qi."),
        (r"from qi ", "from qi "),
        (r"import qi\b", "import qi"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(filepath, "w") as f:
            f.write(content)
        return True
    return False


# Find all Python files
updated_files = []
for root, dirs, files in os.walk("."):
    # Skip hidden directories and qim/quantum dirs
    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["qim", "quantum"]]

    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            if update_file(filepath):
                updated_files.append(filepath)

print(f"Updated {len(updated_files)} files:")
for f in updated_files[:10]:
    print(f"  {f}")
if len(updated_files) > 10:
    print(f"  ... and {len(updated_files) - 10} more")
