#!/usr/bin/env python3
"""
Update all Python imports to use the new poetry system location
"""

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def update_imports(root_dir):
    """Update poetry-related imports in Python files"""

    old_imports = [
        (
            r"from consciousness\.creativity import advanced_haiku_generator",
            "from branding.poetry.soul import Soul as advanced_haiku_generator",  # ΛTAG: import_update
        ),
        (r"from branding.poetry import (.*)", r"from branding.poetry import \1"),
        (r"import poetry\.", "import branding.poetry."),
    ]

    updated_files = []

    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environments and git
        dirs[:] = [d for d in dirs if d not in {".venv", ".git", "node_modules", "__pycache__"}]

        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file

                try:
                    with open(filepath) as f:
                        content = f.read()

                    original_content = content
                    for old_pattern, new_pattern in old_imports:
                        content = re.sub(old_pattern, new_pattern, content)

                    if content != original_content:
                        with open(filepath, "w") as f:
                            f.write(content)
                        updated_files.append(str(filepath))

                except FileNotFoundError:
                    logger.warning(f"File not found: {filepath}")
                except PermissionError:
                    logger.warning(f"Permission denied accessing: {filepath}")
                except UnicodeDecodeError:
                    logger.warning(f"Unable to decode file as UTF-8: {filepath}")
                except Exception as e:
                    logger.error(f"Unexpected error processing {filepath}: {e}")

    return updated_files


if __name__ == "__main__":
    print("Updating poetry imports...")
    updated = update_imports("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    if updated:
        print(f"\nUpdated {len(updated)} files:")
        for file in updated:
            print(f"  - {file}")
    else:
        print("No files needed updating")
