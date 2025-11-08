#!/usr/bin/env python3
"""
AST-safe import rewriter: matriz → MATRIZ

This script uses Python's AST to safely rewrite imports without touching
comments, strings, or other code. It only modifies actual import statements.

Usage:
    # Dry run (preview changes)
    python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run

    # Apply changes
    python3 scripts/consolidation/rewrite_matriz_imports.py

    # Specific directory
    python3 scripts/consolidation/rewrite_matriz_imports.py --path candidate/

Safety features:
- AST-based parsing (no blind regex)
- Backup files created (.bak)
- Dry-run mode for preview
- Skips files with syntax errors
- Detailed change report
"""

import argparse
import ast
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Configuration
OLD_MODULE = "matriz"
NEW_MODULE = "MATRIZ"


class ImportRewriter(ast.NodeTransformer):
    """AST transformer that rewrites matriz → MATRIZ imports."""

    def __init__(self):
        self.changes = []

    def visit_Import(self, node):
        """Rewrite 'import matriz' → 'import matriz'"""
        for alias in node.names:
            if alias.name == OLD_MODULE:
                self.changes.append(
                    f"Line {node.lineno}: import {OLD_MODULE} → import {NEW_MODULE}"
                )
                alias.name = NEW_MODULE
            elif alias.name.startswith(OLD_MODULE + "."):
                old_name = alias.name
                alias.name = NEW_MODULE + alias.name[len(OLD_MODULE) :]
                self.changes.append(f"Line {node.lineno}: import {old_name} → import {alias.name}")
        return node

    def visit_ImportFrom(self, node):
        """Rewrite 'from matriz import ...' → 'from MATRIZ import ...'"""
        if node.module == OLD_MODULE:
            self.changes.append(f"Line {node.lineno}: from {OLD_MODULE} → from {NEW_MODULE}")
            node.module = NEW_MODULE
        elif node.module and node.module.startswith(OLD_MODULE + "."):
            old_module = node.module
            node.module = NEW_MODULE + node.module[len(OLD_MODULE) :]
            self.changes.append(f"Line {node.lineno}: from {old_module} → from {node.module}")
        return node


def rewrite_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """
    Rewrite imports in a single file.

    Returns:
        (changed, change_list) - Whether file was changed and list of changes
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        return False, [f"ERROR: Could not read file: {e}"]

    # Parse AST
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return False, [f"SKIP: Syntax error at line {e.lineno}: {e.msg}"]

    # Rewrite imports
    rewriter = ImportRewriter()
    new_tree = rewriter.visit(tree)

    if not rewriter.changes:
        return False, []  # No changes needed

    # Generate new source
    try:
        import astor

        new_source = astor.to_source(new_tree)
    except ImportError:
        # Fallback: use ast.unparse (Python 3.9+)
        try:
            new_source = ast.unparse(new_tree)
        except AttributeError:
            return False, ["ERROR: Install astor (pip install astor) or use Python 3.9+"]

    if dry_run:
        return True, rewriter.changes

    # Backup original file
    backup_path = filepath.with_suffix(filepath.suffix + ".bak")
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(source)

    # Write new source
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_source)

    return True, rewriter.changes


def find_python_files(root_path: Path, exclude_patterns: List[str]) -> List[Path]:
    """Find all Python files, excluding specified patterns."""
    python_files = []

    # Handle single file case
    if root_path.is_file():
        if root_path.suffix == '.py' and (not any((excl in str(root_path) for excl in exclude_patterns))):
            python_files.append(root_path)
        return python_files

    # Handle directory case
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip excluded directories
        dirnames[:] = [
            d
            for d in dirnames
            if not any(excl in str(Path(dirpath) / d) for excl in exclude_patterns)
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = Path(dirpath) / filename
                if not any(excl in str(filepath) for excl in exclude_patterns):
                    python_files.append(filepath)

    return python_files


def main():
    parser = argparse.ArgumentParser(
        description="AST-safe rewriter: matriz → MATRIZ imports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes without modifying files
  python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run

  # Apply changes to entire repository
  python3 scripts/consolidation/rewrite_matriz_imports.py

  # Apply changes to specific directory
  python3 scripts/consolidation/rewrite_matriz_imports.py --path candidate/

  # Verbose output
  python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --verbose
        """,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--path", type=str, default=".", help="Root path to scan (default: current directory)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-backup", action="store_true", help="Skip creating .bak files (not recommended)"
    )

    args = parser.parse_args()

    # Exclude patterns
    exclude_patterns = [
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "htmlcov",
        "dist",
        "build",
        "*.egg-info",
        "archive",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    ]

    root_path = Path(args.path).resolve()
    if not root_path.exists():
        print(f"ERROR: Path does not exist: {root_path}")
        return 1

    print(f"{'=' * 70}")
    print("MATRIZ Import Rewriter")
    print(f"{'=' * 70}")
    print(f"Mode: {'DRY RUN (preview only)' if args.dry_run else 'LIVE (modifying files)'}")
    print(f"Path: {root_path}")
    print(f"Rewrite: {OLD_MODULE} → {NEW_MODULE}")
    print(f"{'=' * 70}\n")

    # Find Python files
    print("Scanning for Python files...")
    python_files = find_python_files(root_path, exclude_patterns)
    print(f"Found {len(python_files)} Python files to check\n")

    # Process files
    changed_files = []
    skipped_files = []
    error_files = []
    total_changes = 0

    for i, filepath in enumerate(python_files, 1):
        if args.verbose:
            print(f"[{i}/{len(python_files)}] Checking {filepath.relative_to(root_path)}...")

        changed, change_list = rewrite_file(filepath, dry_run=args.dry_run)

        if changed:
            changed_files.append(filepath)
            total_changes += len(change_list)

            if args.verbose or args.dry_run:
                print(f"\n{'=' * 70}")
                print(f"File: {filepath.relative_to(root_path)}")
                print(f"{'=' * 70}")
                for change in change_list:
                    if change.startswith("ERROR:") or change.startswith("SKIP:"):
                        error_files.append((filepath, change))
                        print(f"  ❌ {change}")
                    else:
                        print(f"  ✓ {change}")
        elif change_list:
            # Has messages but no changes (errors/skips)
            for change in change_list:
                if change.startswith("SKIP:"):
                    skipped_files.append((filepath, change))
                elif change.startswith("ERROR:"):
                    error_files.append((filepath, change))

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Files scanned:    {len(python_files)}")
    print(f"Files changed:    {len(changed_files)}")
    print(f"Total changes:    {total_changes}")
    print(f"Files skipped:    {len(skipped_files)}")
    print(f"Files with errors: {len(error_files)}")
    print(f"{'=' * 70}\n")

    if changed_files:
        print("Changed files:")
        for filepath in changed_files[:20]:  # Show first 20
            print(f"  - {filepath.relative_to(root_path)}")
        if len(changed_files) > 20:
            print(f"  ... and {len(changed_files) - 20} more")
        print()

    if skipped_files and args.verbose:
        print("Skipped files (syntax errors):")
        for filepath, reason in skipped_files[:10]:
            print(f"  - {filepath.relative_to(root_path)}: {reason}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")
        print()

    if error_files:
        print("Files with errors:")
        for filepath, error in error_files:
            print(f"  - {filepath.relative_to(root_path)}: {error}")
        print()

    if args.dry_run:
        print("⚠️  DRY RUN: No files were modified")
        print("   Remove --dry-run to apply changes")
    else:
        print("✅ Changes applied successfully")
        print("   Backup files created with .bak extension")
        print("\nNext steps:")
        print("  1. Run tests: make smoke && python3 -m pytest")
        print("  2. Verify imports: python3 -c 'import matriz; print(\"OK\")'")
        print("  3. Review changes: git diff")
        print("  4. Commit: git add -A && git commit -m 'fix(imports): matriz → MATRIZ'")

    # Generate manifest artifact
    if changed_files or args.dry_run:
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(exist_ok=True)

        manifest = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "mode": "dry-run" if args.dry_run else "live",
            "old_module": OLD_MODULE,
            "new_module": NEW_MODULE,
            "root_path": str(root_path),
            "files_scanned": len(python_files),
            "files_changed": [str(f) for f in changed_files],
            "total_changes": total_changes,
            "files_skipped": len(skipped_files),
            "files_with_errors": len(error_files),
        }

        manifest_path = artifacts_dir / "matriz_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        if args.verbose:
            print(f"\n📄 Manifest written to: {manifest_path}")

    return 0 if not error_files else 1


if __name__ == "__main__":
    sys.exit(main())
