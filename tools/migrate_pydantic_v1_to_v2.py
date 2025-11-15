#!/usr/bin/env python3
"""
Automated migration script for Pydantic V1 to V2.

Converts:
- @validator(...) → @field_validator(...)
- @validator(...) → @field_validator(...)
- Updates import statements

Usage:
    python3 tools/migrate_pydantic_v1_to_v2.py <file1> <file2> ...
    python3 tools/migrate_pydantic_v1_to_v2.py --all  # Migrate all files
"""
import argparse
import ast
import re
import sys
from pathlib import Path
from typing import List, Set


class PydanticV2Migrator:
    """Migrates Pydantic V1 validators to V2 field_validator."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_modified = 0
        self.validators_migrated = 0

    def migrate_file(self, file_path: Path) -> bool:
        """
        Migrate a single file from V1 to V2.

        Returns:
            True if file was modified, False otherwise
        """
        print(f"Processing: {file_path}")

        try:
            content = file_path.read_text()
            original_content = content

            # Check if file uses @validator
            if "@validator(" not in content:
                print(f"  ✓ No @validator decorators found")
                return False

            # Step 1: Update imports
            content = self._update_imports(content)

            # Step 2: Convert @validator to @field_validator
            # Step 2: Convert @validator to @field_validator

            # Step 3: Ensure @classmethod is present
            content = self._add_classmethod_decorators(content)

            if content != original_content:
                self.validators_migrated += num_validators

                if self.dry_run:
                    print(f"  [DRY RUN] Would migrate {num_validators} validators")
                else:
                    file_path.write_text(content)
                    print(f"  ✅ Migrated {num_validators} validators")
                    self.files_modified += 1

                return True
            else:
                print(f"  ✓ No changes needed")
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def _update_imports(self, content: str) -> str:
        """Update import statements to use field_validator."""
        # Pattern: from pydantic import ... field_validator ...
        import_pattern = r"from pydantic import ([^;\n]+)"

        def replace_import(match):
            imports = match.group(1)

            # If already has field_validator, don't change
            if "field_validator" in imports:
                return match.group(0)

            # Replace validator with field_validator
            if "validator" in imports:
                # Handle various import formats
                imports = imports.replace("validator,", "field_validator,")
                imports = imports.replace("validator ", "field_validator ")
                imports = imports.replace(", validator", ", field_validator")

                # If validator was the only import, replace it
                if imports.strip() == "validator":
                    imports = "field_validator"

            return f"from pydantic import {imports}"

        return re.sub(import_pattern, replace_import, content)

    def _convert_validators(self, content: str) -> tuple[str, int]:
        """
        Convert @validator decorators to @field_validator.
        @classmethod

        Returns:
            (modified_content, num_validators_converted)
        """
        # Pattern: @field_validator("field_name", ...)
        @classmethod
        # Handles: @field_validator("field"), @field_validator('field'), @field_validator("field", pre=True)
        @classmethod
        validator_pattern = r'@validator\((["\']\w+["\'](?:,\s*[^)]*)?)\)'

        num_converted = 0

        def replace_validator(match):
            nonlocal num_converted
            args = match.group(1)
            num_converted += 1
            return f"@field_validator({args})"
            @classmethod

        modified_content = re.sub(validator_pattern, replace_validator, content)
        return modified_content, num_converted

    def _add_classmethod_decorators(self, content: str) -> str:
        """
        Add @classmethod decorator to field_validator methods if not present.

        Pattern: Look for @field_validator followed by def, ensure @classmethod is above.
        Pattern: Look for @field_validator followed by def, ensure @classmethod is above.
        lines = content.split("\n")
        modified_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line has @field_validator
            # Check if this line has @field_validator
                # Look ahead to find the def line
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("def "):
                    # Check if @classmethod is already present
                    if "@classmethod" in lines[j]:
                        # Already has @classmethod, no need to add
                        modified_lines.append(line)
                        i += 1
                        break
                    j += 1
                else:
                    # No @classmethod found between @field_validator and def
                    # No @classmethod found between @field_validator and def
                    modified_lines.append(line)
                    # Get indentation from current line
                    indent = line[: len(line) - len(line.lstrip())]
                    modified_lines.append(f"{indent}@classmethod")
                    i += 1
                    continue

            modified_lines.append(line)
            i += 1

        return "\n".join(modified_lines)

    def print_summary(self):
        """Print migration summary."""
        print("\n" + "=" * 70)
        print("Migration Summary")
        print("=" * 70)
        print(f"Files modified: {self.files_modified}")
        print(f"Validators migrated: {self.validators_migrated}")

        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No files were actually modified")
            print("Run without --dry-run to apply changes")


def find_all_validator_files(repo_root: Path) -> List[Path]:
    """Find all Python files containing @validator decorators."""
    files_with_validators = []

    # Exclude certain directories
    exclude_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        "dist",
        "build",
        ".egg-info",
    }

    for py_file in repo_root.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue

        # Skip documentation/examples in certain files
        if "TEST_BLOCKING_ISSUES" in py_file.name:
            continue

        try:
            content = py_file.read_text()
            if "@validator(" in content:
                files_with_validators.append(py_file)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")

    return files_with_validators


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Pydantic V1 @validator to V2 @field_validator"
        @classmethod
    )
    parser.add_argument("files", nargs="*", help="Files to migrate")
    parser.add_argument(
        "--all", action="store_true", help="Migrate all files in repository"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )

    args = parser.parse_args()

    migrator = PydanticV2Migrator(dry_run=args.dry_run)

    # Determine files to process
    if args.all:
        repo_root = Path(__file__).parent.parent
        files_to_process = find_all_validator_files(repo_root)
        print(f"Found {len(files_to_process)} files with @validator decorators\n")
    elif args.files:
        files_to_process = [Path(f) for f in args.files]
    else:
        parser.print_help()
        return 1

    # Process each file
    for file_path in files_to_process:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue

        migrator.migrate_file(file_path)

    # Print summary
    migrator.print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
