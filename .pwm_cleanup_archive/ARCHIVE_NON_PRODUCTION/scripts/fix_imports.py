#!/usr/bin/env python3
"""
Fix import paths after lukhas module reorganization.
This script updates import statements to match the new module structure.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # Core imports
    r"from lukhas\.core\.": "from core.",
    r"from lukhas\.bio\.": "from bio.",
    r"from lukhas\.consciousness\.": "from consciousness.",
    r"from lukhas\.creativity\.": "from creativity.",
    r"from lukhas\.memory\.": "from memory.",
    r"from lukhas\.reasoning\.": "from reasoning.",
    r"from lukhas\.bridge\.": "from bridge.",
    r"from lukhas\.config\.": "from config.",
    r"from lukhas\.api\.": "from api.",
    r"from lukhas\.ethics\.": "from ethics.",
    r"from lukhas\.identity\.": "from identity.",
    r"from lukhas\.orchestration\.": "from orchestration.",
    r"from lukhas\.quantum\.": "from quantum.",
    r"from lukhas\.symbolic\.": "from symbolic.",
    r"from lukhas\.emotion\.": "from emotion.",
    r"from lukhas\.voice\.": "from voice.",
    r"from lukhas\.perception\.": "from perception.",
    r"from lukhas\.learning\.": "from learning.",
    r"from lukhas\.narrative\.": "from narrative.",
    r"from lukhas\.embodiment\.": "from embodiment.",
    r"from lukhas\.features\.": "from features.",
    r"from lukhas\.interfaces\.": "from interfaces.",
    r"from lukhas\.meta\.": "from meta.",
    r"from lukhas\.security\.": "from security.",
    r"from lukhas\.simulation\.": "from simulation.",
    r"from lukhas\.tagging\.": "from tagging.",
    r"from lukhas\.tools\.": "from tools.",
    r"from lukhas\.trace\.": "from trace.",
    # Direct lukhas imports
    r"import lukhas\.core": "import core",
    r"import lukhas\.bio": "import bio",
    r"import lukhas\.consciousness": "import consciousness",
    r"import lukhas\.creativity": "import creativity",
    r"import lukhas\.memory": "import memory",
    r"import lukhas\.reasoning": "import reasoning",
    r"import lukhas\.bridge": "import bridge",
    r"import lukhas\.config": "import config",
    r"import lukhas\.api": "import api",
    r"import lukhas\.ethics": "import ethics",
    r"import lukhas\.identity": "import identity",
    r"import lukhas\.orchestration": "import orchestration",
    r"import lukhas\.quantum": "import quantum",
    r"import lukhas\.symbolic": "import symbolic",
    r"import lukhas\.emotion": "import emotion",
    r"import lukhas\.voice": "import voice",
    r"import lukhas\.perception": "import perception",
    r"import lukhas\.learning": "import learning",
    r"import lukhas\.narrative": "import narrative",
    r"import lukhas\.embodiment": "import embodiment",
    r"import lukhas\.features": "import features",
    r"import lukhas\.interfaces": "import interfaces",
    r"import lukhas\.meta": "import meta",
    r"import lukhas\.security": "import security",
    r"import lukhas\.simulation": "import simulation",
    r"import lukhas\.tagging": "import tagging",
    r"import lukhas\.tools": "import tools",
    r"import lukhas\.trace": "import trace",
    # Special cases
    r"from ": "from ",
    r"import lukhas\s*$": "# import lukhas  # Module reorganized",
}


def fix_imports_in_file(filepath: Path) -> Tuple[bool, List[str]]:
    """Fix imports in a single Python file."""
    changes = []
    modified = False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes.append(f"Replaced '{old_pattern}' with '{new_pattern}'")

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            modified = True

    except Exception as e:
        changes.append(f"Error processing file: {e}")

    return modified, changes


def fix_relative_imports(filepath: Path) -> Tuple[bool, List[str]]:
    """Fix relative imports based on file location."""
    changes = []
    modified = False

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        file_dir = filepath.parent

        for line in lines:
            original_line = line

            # Check for relative imports that might need adjustment
            if line.strip().startswith(("from .", "from ..")):
                # Analyze the import and determine if it needs fixing
                if "lukhas" in line:
                    line = line.replace("lukhas.", "")
                    changes.append(
                        f"Fixed relative import: {original_line.strip()} -> {line.strip()}"
                    )

            new_lines.append(line)

        if new_lines != lines:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            modified = True

    except Exception as e:
        changes.append(f"Error processing relative imports: {e}")

    return modified, changes


def scan_and_fix_directory(
    directory: Path, dry_run: bool = False
) -> Dict[str, List[str]]:
    """Scan directory and fix all Python files."""
    results = {}

    for py_file in directory.rglob("*.py"):
        # Skip certain directories
        if any(
            skip in str(py_file)
            for skip in [".venv", "__pycache__", "node_modules", ".git"]
        ):
            continue

        if dry_run:
            # Just check, don't modify
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(py_file, encoding="latin-1") as f:
                        content = f.read()
                except Exception:
                    continue

            issues = []
            for old_pattern in IMPORT_MAPPINGS:
                if re.search(old_pattern, content):
                    issues.append(f"Found pattern: {old_pattern}")

            if issues:
                results[str(py_file)] = issues
        else:
            # Actually fix the imports
            modified1, changes1 = fix_imports_in_file(py_file)
            modified2, changes2 = fix_relative_imports(py_file)

            if modified1 or modified2:
                results[str(py_file)] = changes1 + changes2

    return results


def main():
    """Main function to run import fixes."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix import paths after lukhas module reorganization"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Only show what would be changed"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to scan (default: current directory)",
    )
    args = parser.parse_args()

    base_path = Path(args.path).resolve()
    print(f"Scanning directory: {base_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'FIXING IMPORTS'}")
    print("-" * 80)

    results = scan_and_fix_directory(base_path, args.dry_run)

    if results:
        print(f"\nFound issues in {len(results)} files:\n")
        for filepath, changes in sorted(results.items()):
            print(f"\n{filepath}:")
            for change in changes:
                print(f"  - {change}")
    else:
        print("\nNo import issues found!")

    print(f"\nTotal files with issues: {len(results)}")


if __name__ == "__main__":
    main()
