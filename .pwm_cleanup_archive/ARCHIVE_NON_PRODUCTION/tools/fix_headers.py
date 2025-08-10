#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Header Fix Tool

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This tool updates incorrect LUKHAS definitions in file headers across the codebase.

For more information, visit: https://lukhas.ai
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# ΛTRACE: Header fix tool initialization
# ΛORIGIN_AGENT: Claude
# ΛTASK_ID: LUKHAS-HEADER-FIX-001

# Patterns to match incorrect headers
INCORRECT_PATTERNS = [
    (
        r"lukhas \(lukhas Universal Knowledge & Holistic AI System\)",
        "LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)",
    ),
    (r"LUKHlukhasS", "LUKHAS"),
    (r"lukhasI", "AI"),
    (
        r"LUKHAS AI \(LUKHAS Universal Knowledge & Holistic AI System\)",
        "LUKHAS AI (Logical Unified Knowledge Hyper-Adaptable System)",
    ),
    (
        r"LUKHlukhasS lukhasI \(LUKHlukhasS Universal Knowledge & Holistic lukhasI System\)",
        "LUKHAS AI (Logical Unified Knowledge Hyper-Adaptable System)",
    ),
    (
        r"LUKHAS \(LUKHAS Universal Knowledge & Holistic AI System\)",
        "LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)",
    ),
]

# Standard header template for Python files
PYTHON_HEADER_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - {module_name}

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

{description}

For more information, visit: https://lukhas.ai
"""

'''


def extract_module_info(filepath: Path, content: str) -> Tuple[str, str]:
    """Extract module name and description from file content."""
    module_name = filepath.stem.replace("_", " ").title()

    # Try to extract existing description from docstring
    docstring_match = re.search(r'"""[\s\S]*?"""', content)
    if docstring_match:
        docstring = docstring_match.group()
        lines = docstring.split("\n")
        # Look for description lines (skip first and last)
        desc_lines = []
        for line in lines[1:-1]:
            line = line.strip()
            if line and not any(
                x in line.lower() for x in ["copyright", "license", "author", "lukhas"]
            ):
                desc_lines.append(line)
        if desc_lines:
            description = " ".join(desc_lines[:2])  # Take first 2 lines
        else:
            description = f"Module for {module_name.lower()} functionality"
    else:
        description = f"Module for {module_name.lower()} functionality"

    return module_name, description


def fix_file_header(filepath: Path, dry_run: bool = False) -> bool:
    """Fix header in a single file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    original_content = content

    # Apply all pattern replacements
    for pattern, replacement in INCORRECT_PATTERNS:
        content = re.sub(pattern, replacement, content)

    # Check if file needs a complete header replacement
    needs_new_header = False
    if '"""' in content[:500]:  # Check if docstring exists in first 500 chars
        # Check if it has the old incorrect definition
        if "Universal Knowledge & Holistic" in content[:500]:
            needs_new_header = True

    if needs_new_header:
        # Extract module info
        module_name, description = extract_module_info(filepath, content)

        # Find where the old docstring ends
        docstring_match = re.search(r'"""[\s\S]*?"""', content)
        if docstring_match:
            # Get content after the old docstring
            after_docstring = content[docstring_match.end() :]

            # Build new header
            new_header = PYTHON_HEADER_TEMPLATE.format(
                module_name=module_name, description=description
            )

            # Combine new header with rest of file
            content = new_header + after_docstring.lstrip()

    # Check if changes were made
    if content != original_content:
        if not dry_run:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Fixed: {filepath}")
                return True
            except Exception as e:
                print(f"❌ Error writing {filepath}: {e}")
                return False
        else:
            print(f"Would fix: {filepath}")
            return True

    return False


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory."""
    return list(directory.rglob("*.py"))


def main():
    """Main function to fix all headers."""
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run = True
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        dry_run = False
        print("🔧 FIXING MODE - Files will be updated")

    lukhas_dir = Path(__file__).parent.parent  # Go up from tools to lukhas
    python_files = find_python_files(lukhas_dir)

    print(f"\n📊 Found {len(python_files)} Python files to check")

    fixed_count = 0
    error_count = 0

    for filepath in python_files:
        # Skip this script itself
        if filepath.name == "fix_lukhas_headers.py":
            continue

        if fix_file_header(filepath, dry_run):
            fixed_count += 1

    print("\n📈 Summary:")
    print(f"  - Files checked: {len(python_files)}")
    print(f"  - Files fixed: {fixed_count}")
    print(f"  - Errors: {error_count}")

    if dry_run and fixed_count > 0:
        print("\n💡 Run without --dry-run to apply changes")


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
