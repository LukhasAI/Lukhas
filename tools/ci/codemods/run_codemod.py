#!/usr/bin/env python3
"""
T4 Codemod Runner - Apply LibCST Transformers

Driver script for applying codemods from library.py.

Usage:
  # Remove specific unused import
  python3 tools/ci/codemods/run_codemod.py --transformer RemoveUnusedImport \
      --file lukhas/api.py --unused-names "Foo,Bar"

  # Fix all B904 in paths
  python3 tools/ci/codemods/run_codemod.py --transformer FixB904 \
      --paths lukhas core --dry-run

  # Fix RUF012 with backup
  python3 tools/ci/codemods/run_codemod.py --transformer FixRUF012 \
      --paths lukhas --backup
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import libcst as cst

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.ci.codemods.library import TRANSFORMERS


def apply_codemod(
    file_path: Path,
    transformer_class: type,
    transformer_kwargs: dict,
    dry_run: bool = False,
    backup: bool = False,
) -> tuple[bool, str]:
    """
    Apply codemod to single file.

    Returns:
      (changed, message)
    """
    try:
        source_code = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"failed to read: {e}"

    try:
        source_tree = cst.parse_module(source_code)
    except Exception as e:
        return False, f"parse error: {e}"

    # Apply transformer
    transformer = transformer_class(**transformer_kwargs)
    modified_tree = source_tree.visit(transformer)

    # Check if changed
    modified_code = modified_tree.code

    if modified_code == source_code:
        return False, "no changes"

    if dry_run:
        return True, "would modify (dry-run)"

    # Backup if requested
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        backup_path.write_text(source_code, encoding="utf-8")

    # Write modified
    file_path.write_text(modified_code, encoding="utf-8")

    return True, "modified"


def main():
    parser = argparse.ArgumentParser(description="Apply LibCST codemods to Python files")
    parser.add_argument(
        "--transformer",
        required=True,
        choices=list(TRANSFORMERS.keys()),
        help="Transformer to apply",
    )
    parser.add_argument("--file", type=Path, help="Single file to transform")
    parser.add_argument("--paths", nargs="+", help="Directories to search for Python files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying files"
    )
    parser.add_argument("--backup", action="store_true", help="Create .bak backup files")

    # Transformer-specific args
    parser.add_argument(
        "--unused-names", help="Comma-separated unused import names (for RemoveUnusedImport)"
    )
    parser.add_argument("--module-name", help="Module name for star import (for ConvertImportStar)")
    parser.add_argument(
        "--used-names", help="Comma-separated used names from star import (for ConvertImportStar)"
    )

    args = parser.parse_args()

    # Validate input
    if not args.file and not args.paths:
        parser.error("Must provide --file or --paths")

    # Prepare transformer kwargs
    transformer_class = TRANSFORMERS[args.transformer]
    transformer_kwargs = {}

    if args.transformer == "RemoveUnusedImport":
        if not args.unused_names:
            parser.error("RemoveUnusedImport requires --unused-names")
        transformer_kwargs["unused_names"] = set(args.unused_names.split(","))

    elif args.transformer == "ConvertImportStar":
        if not args.module_name or not args.used_names:
            parser.error("ConvertImportStar requires --module-name and --used-names")
        transformer_kwargs["module_name"] = args.module_name
        transformer_kwargs["used_names"] = set(args.used_names.split(","))

    # Collect files
    files_to_process: list[Path] = []

    if args.file:
        if not args.file.exists():
            print(f"❌ File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        files_to_process.append(args.file)

    if args.paths:
        for path_str in args.paths:
            path = REPO_ROOT / path_str
            if not path.exists():
                print(f"⚠️  Path not found: {path}", file=sys.stderr)
                continue

            if path.is_file():
                files_to_process.append(path)
            else:
                # Recursively find .py files
                files_to_process.extend(path.rglob("*.py"))

    if not files_to_process:
        print("❌ No Python files to process", file=sys.stderr)
        sys.exit(1)

    # Process files
    print(f"🔧 Applying {args.transformer} to {len(files_to_process)} files...")
    print("")

    modified_count = 0
    error_count = 0

    for file_path in files_to_process:
        relative_path = (
            file_path.relative_to(REPO_ROOT) if file_path.is_relative_to(REPO_ROOT) else file_path
        )

        changed, message = apply_codemod(
            file_path,
            transformer_class,
            transformer_kwargs,
            dry_run=args.dry_run,
            backup=args.backup,
        )

        if changed:
            modified_count += 1
            print(f"✅ {relative_path}: {message}")
        elif "error" in message or "failed" in message:
            error_count += 1
            print(f"❌ {relative_path}: {message}")
        else:
            # Skip unchanged files (reduce noise)
            pass

    print("")
    print("=" * 60)
    print("📊 Summary:")
    print(f"   Total files: {len(files_to_process)}")
    print(f"   Modified: {modified_count}")
    print(f"   Errors: {error_count}")
    print(f"   Unchanged: {len(files_to_process) - modified_count - error_count}")

    if args.dry_run:
        print("")
        print("💡 This was a dry-run. Use without --dry-run to apply changes.")

    if args.backup and modified_count > 0:
        print("")
        print("💾 Backup files created with .bak extension")

    print("=" * 60)

    sys.exit(0 if error_count == 0 else 1)


if __name__ == "__main__":
    main()
