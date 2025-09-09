#!/usr/bin/env python3
"""
Migration script to update imports to use common utilities
"""
import re
from pathlib import Path


def update_imports_in_file(file_path: Path):
    """Update imports in a single file"""
    with open(file_path) as f:
        content = f.read()

    # Replace common patterns
    replacements = [
        # Logger imports
        (r"from .+ import get_logger", "from system.common.utils import get_logger"),
        (r"logger = logging.getLogger\(__name__\)", "logger = get_logger(__name__)"),
        # Config loading
        (
            r"with open\(.+\) as .+:\s*\n\s*.+ = json\.load\(.+\)",
            "config = load_config(config_path)",
        ),
    ]

    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True

    if modified:
        # Add import if needed
        if "from system.common.utils import" not in content:
            lines = content.split("\n")
            import_line = "from system.common.utils import get_logger, load_config\n"

            # Find where to insert import
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    lines.insert(i + 1, import_line)
                    break

            content = "\n".join(lines)

        with open(file_path, "w") as f:
            f.write(content)

        return True

    return False


def main():
    """Run migration"""
    root = Path("/Users/agi_dev/Lukhas")
    updated_files = []

    for py_file in root.rglob("*.py"):
        if update_imports_in_file(py_file):
            updated_files.append(py_file)

    print(f"Updated {len(updated_files)} files")


if __name__ == "__main__":
    main()