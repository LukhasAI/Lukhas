#!/usr/bin/env python3#!/usr/bin/env python3

""""""

AST-safe rewriter to replace legacy `matriz` imports with `MATRIZ`.AST-safe import rewriter: matriz → MATRIZ



This version produces formal unified-diff patch files (git-applyable), a per-fileThis script uses Python's AST to safely rewrite imports without touching

patch set under `artifacts/patches/`, an aggregated `artifacts/matriz_migration.patch`,comments, strings, or other code. It only modifies actual import statements.

and a `migration-summary.md` describing the changes.

Usage:

Key features:    # Dry run (preview changes)

- Dry-run mode (default) writes artifacts only and does not change files.    python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run

- --apply writes files and creates backups (`.bak`). Requires --confirm-apply.

- --git-apply attempts to `git apply` the aggregated patch after verifying a clean working tree; it will create a branch `migration/matriz-YYYYMMDD`.    # Apply changes

- Filters by path patterns (defaults to production/test lanes).    python3 scripts/consolidation/rewrite_matriz_imports.py

- Skips files in exclusion directories (.git, .venv, build, dist, third_party, artifacts).

    # Specific directory

Requirements: libcst, Python 3.8+    python3 scripts/consolidation/rewrite_matriz_imports.py --path candidate/



Usage examples:Safety features:

  # Dry run across production lanes- AST-based parsing (no blind regex)

  python rewrite_matriz_imports.py --path lukhas core tests --dry-run- Backup files created (.bak)

- Dry-run mode for preview

  # Create patches and apply changes to files (writes backups)- Skips files with syntax errors

  python rewrite_matriz_imports.py --path lukhas --apply --confirm-apply- Detailed change report

"""

  # Create patches and apply via git (safe) on a new branch

  python rewrite_matriz_imports.py --path core tests --git-applyimport ast

"""import os

import argparseimport sys

import datetimeimport argparse

import difflibfrom pathlib import Path

import jsonfrom typing import List, Tuple

import os

import shutil# Configuration

import subprocessOLD_MODULE = "matriz"

import sysNEW_MODULE = "MATRIZ"

from pathlib import Path

from typing import List, Optional

class ImportRewriter(ast.NodeTransformer):

import libcst as cst    """AST transformer that rewrites matriz → MATRIZ imports."""

from libcst import Name as CSTName

    def __init__(self):

EXCLUDE_DIRS = {".git", "artifacts", "dist", "build", "third_party", "__pycache__", ".venv"}        self.changes = []

DEFAULT_LANES = ["lukhas", "core", "serve", "tests"]

    def visit_Import(self, node):

        """Rewrite 'import matriz' → 'import MATRIZ'"""

def is_excluded(path: Path) -> bool:        for alias in node.names:

    for part in path.parts:            if alias.name == OLD_MODULE:

        if part in EXCLUDE_DIRS:                self.changes.append(f"Line {node.lineno}: import {OLD_MODULE} → import {NEW_MODULE}")

            return True                alias.name = NEW_MODULE

    return False            elif alias.name.startswith(OLD_MODULE + "."):

                old_name = alias.name

                alias.name = NEW_MODULE + alias.name[len(OLD_MODULE):]

class MatrizRewriter(cst.CSTTransformer):                self.changes.append(f"Line {node.lineno}: import {old_name} → import {alias.name}")

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:        return node

        new_names = []

        changed = False    def visit_ImportFrom(self, node):

        for alias in updated_node.names:        """Rewrite 'from matriz import ...' → 'from MATRIZ import ...'"""

            name_value = getattr(alias.name, "value", None)        if node.module == OLD_MODULE:

            if name_value == "matriz":            self.changes.append(f"Line {node.lineno}: from {OLD_MODULE} → from {NEW_MODULE}")

                new_alias = alias.with_changes(name=cst.CSTNode(CSTName("MATRIZ")) if False else cst.Name("MATRIZ"))            node.module = NEW_MODULE

                new_names.append(new_alias)        elif node.module and node.module.startswith(OLD_MODULE + "."):

                changed = True            old_module = node.module

            else:            node.module = NEW_MODULE + node.module[len(OLD_MODULE):]

                new_names.append(alias)            self.changes.append(f"Line {node.lineno}: from {old_module} → from {node.module}")

        if changed:        return node

            return updated_node.with_changes(names=new_names)

        return updated_node

def rewrite_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:    """

        module = updated_node.module    Rewrite imports in a single file.

        if module is not None:

            module_name = getattr(module, "value", None)    Returns:

            if module_name == "matriz":        (changed, change_list) - Whether file was changed and list of changes

                return updated_node.with_changes(module=cst.Name("MATRIZ"))    """

        return updated_node    try:

        with open(filepath, 'r', encoding='utf-8') as f:

            source = f.read()

def find_py_files(paths: List[str]) -> List[Path]:    except (UnicodeDecodeError, PermissionError) as e:

    files = []        return False, [f"ERROR: Could not read file: {e}"]

    for p in paths:

        path = Path(p)    # Parse AST

        if path.is_file() and path.suffix == ".py":    try:

            if not is_excluded(path):        tree = ast.parse(source, filename=str(filepath))

                files.append(path)    except SyntaxError as e:

        elif path.is_dir():        return False, [f"SKIP: Syntax error at line {e.lineno}: {e.msg}"]

            for f in path.rglob("*.py"):

                if not is_excluded(f):    # Rewrite imports

                    files.append(f)    rewriter = ImportRewriter()

        else:    new_tree = rewriter.visit(tree)

            # interpret as glob relative to repo root

            for f in Path(".").glob(p):    if not rewriter.changes:

                if f.is_file() and f.suffix == ".py" and not is_excluded(f):        return False, []  # No changes needed

                    files.append(f)

    unique = sorted(set(files))    # Generate new source

    return unique    try:

        import astor

        new_source = astor.to_source(new_tree)

def generate_unified_diff(orig: str, new: str, path: Path) -> str:    except ImportError:

    orig_lines = orig.splitlines(keepends=True)        # Fallback: use ast.unparse (Python 3.9+)

    new_lines = new.splitlines(keepends=True)        try:

    diff = difflib.unified_diff(orig_lines, new_lines, fromfile=str(path), tofile=str(path), lineterm="")            new_source = ast.unparse(new_tree)

    return "\n".join(list(diff)) + "\n"        except AttributeError:

            return False, ["ERROR: Install astor (pip install astor) or use Python 3.9+"]



def ensure_artifacts():    if dry_run:

    art = Path("artifacts")        return True, rewriter.changes

    art.mkdir(exist_ok=True)

    (art / "patches").mkdir(parents=True, exist_ok=True)    # Backup original file

    backup_path = filepath.with_suffix(filepath.suffix + '.bak')

    with open(backup_path, 'w', encoding='utf-8') as f:

def make_safe_patch_filename(path: Path) -> str:        f.write(source)

    rel = os.path.relpath(path, Path("."))

    name = rel.replace(os.sep, "__").replace(":", "_")    # Write new source

    return name + ".patch"    with open(filepath, 'w', encoding='utf-8') as f:

        f.write(new_source)



def write_per_file_patches(patches: List[dict], aggregated_patch_path: Path):    return True, rewriter.changes

    for p in patches:

        safe = make_safe_patch_filename(Path(p["file"]))

        out = Path("artifacts/patches") / safedef find_python_files(root_path: Path, exclude_patterns: List[str]) -> List[Path]:

        out.write_text(p["diff"], encoding="utf-8")    """Find all Python files, excluding specified patterns."""

    agg = []    python_files = []

    for p in patches:

        agg.append(p["diff"])    for dirpath, dirnames, filenames in os.walk(root_path):

    aggregated_patch_path.write_text("\n".join(agg), encoding="utf-8")        # Skip excluded directories

        dirnames[:] = [d for d in dirnames if not any(excl in str(Path(dirpath) / d) for excl in exclude_patterns)]



def apply_patches_write_files(patches: List[dict], confirm: bool):        for filename in filenames:

    if not confirm:            if filename.endswith('.py'):

        raise RuntimeError("--apply requires --confirm-apply for safety")                filepath = Path(dirpath) / filename

    for p in patches:                if not any(excl in str(filepath) for excl in exclude_patterns):

        fpath = Path(p["file"])                    python_files.append(filepath)

        backup = fpath.with_suffix(fpath.suffix + ".bak")

        shutil.copy2(fpath, backup)    return python_files

        fpath.write_text(p["new"], encoding="utf-8")

        print(f"[APPLIED] Wrote {fpath} (backup at {backup})")

def main():

    parser = argparse.ArgumentParser(

def git_apply_patch(aggregated_patch: Path, branch_name: str) -> None:        description="AST-safe rewriter: matriz → MATRIZ imports",

    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)        formatter_class=argparse.RawDescriptionHelpFormatter,

    if res.returncode != 0:        epilog="""

        raise RuntimeError("git status failed: " + res.stderr)Examples:

    if res.stdout.strip() != "":  # Preview changes without modifying files

        raise RuntimeError("Working tree not clean. Please commit or stash changes before git-apply.")  python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run

    res = subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True, text=True)

    if res.returncode != 0:  # Apply changes to entire repository

        raise RuntimeError("git checkout failed: " + res.stderr)  python3 scripts/consolidation/rewrite_matriz_imports.py

    res = subprocess.run(["git", "apply", "--index", str(aggregated_patch)], capture_output=True, text=True)

    if res.returncode != 0:  # Apply changes to specific directory

        raise RuntimeError("git apply failed: " + res.stderr)  python3 scripts/consolidation/rewrite_matriz_imports.py --path candidate/

    print(f"Applied patch to branch {branch_name}. Staged changes are ready for commit.")

  # Verbose output

  python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --verbose

def build_migration_summary(patches: List[dict], output: Path, lanes: List[str]):        """

    total = len(patches)    )

    files = [p["file"] for p in patches]    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')

    now = datetime.datetime.utcnow().isoformat() + "Z"    parser.add_argument('--path', type=str, default='.', help='Root path to scan (default: current directory)')

    md = [f"# MATRIZ Migration Summary\n", f"\nGenerated: {now}\n", f"\nLanes: {', '.join(lanes)}\n", f"\nFiles changed: {total}\n\n"]    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    md.append("## Files\n")    parser.add_argument('--no-backup', action='store_true', help='Skip creating .bak files (not recommended)')

    for f in files:

        md.append(f"- {f}\n")    args = parser.parse_args()

    output.write_text("\n".join(md), encoding="utf-8")

    print(f"Wrote migration summary to {output}")    # Exclude patterns

    exclude_patterns = [

        '.git', '__pycache__', 'node_modules', '.venv', 'venv',

def main(argv: Optional[List[str]] = None):        'htmlcov', 'dist', 'build', '*.egg-info', 'archive',

    p = argparse.ArgumentParser()        '.pytest_cache', '.mypy_cache', '.ruff_cache'

    p.add_argument("--path", "-p", nargs="+", default=DEFAULT_LANES,    ]

                   help="Files or directories to process (defaults to production/test lanes)")

    p.add_argument("--dry-run", action="store_true", help="Only write artifacts; do not change files")    root_path = Path(args.path).resolve()

    p.add_argument("--apply", action="store_true", help="Write changes to files (creates .bak). Requires --confirm-apply")    if not root_path.exists():

    p.add_argument("--confirm-apply", action="store_true", help="Confirm destructive apply when --apply is used")        print(f"ERROR: Path does not exist: {root_path}")

    p.add_argument("--git-apply", action="store_true", help="Attempt to apply aggregated patch via git on a new branch")        return 1

    p.add_argument("--output", default="artifacts/matriz_migration.patch", help="Aggregated patch output path")

    p.add_argument("--verbose", action="store_true")    print(f"{'='*70}")

    args = p.parse_args(argv)    print(f"MATRIZ Import Rewriter")

    print(f"{'='*70}")

    ensure_artifacts()    print(f"Mode: {'DRY RUN (preview only)' if args.dry_run else 'LIVE (modifying files)'}")

    print(f"Path: {root_path}")

    files = find_py_files(args.path)    print(f"Rewrite: {OLD_MODULE} → {NEW_MODULE}")

    if args.verbose:    print(f"{'='*70}\n")

        print(f"Found {len(files)} .py files to analyze")

    # Find Python files

    patches = []    print("Scanning for Python files...")

    rewriter = MatrizRewriter()    python_files = find_python_files(root_path, exclude_patterns)

    for f in files:    print(f"Found {len(python_files)} Python files to check\n")

        try:

            src = f.read_text(encoding="utf-8")    # Process files

        except Exception as e:    changed_files = []

            print(f"Skipping {f}: read error {e}")    skipped_files = []

            continue    error_files = []

        try:    total_changes = 0

            tree = cst.parse_module(src)

            new_tree = tree.visit(rewriter)    for i, filepath in enumerate(python_files, 1):

            new_code = new_tree.code        if args.verbose:

        except Exception as e:            print(f"[{i}/{len(python_files)}] Checking {filepath.relative_to(root_path)}...")

            print(f"Skipping {f}: parse/transform error {e}")

            continue        changed, change_list = rewrite_file(filepath, dry_run=args.dry_run)

        if new_code != src:

            diff = generate_unified_diff(src, new_code, f)        if changed:

            patches.append({"file": str(f), "diff": diff, "new": new_code})            changed_files.append(filepath)

            if args.verbose:            total_changes += len(change_list)

                print(f"Planned change for {f}")

    if not patches:            if args.verbose or args.dry_run:

        print("No matriz imports found to migrate. Nothing to do.")                print(f"\n{'='*70}")

        sys.exit(0)                print(f"File: {filepath.relative_to(root_path)}")

                print(f"{'='*70}")

    aggregated_patch_path = Path(args.output)                for change in change_list:

    write_per_file_patches(patches, aggregated_patch_path)                    if change.startswith("ERROR:") or change.startswith("SKIP:"):

                        error_files.append((filepath, change))

    summary_path = Path("artifacts/migration-summary.md")                        print(f"  ❌ {change}")

    build_migration_summary(patches, summary_path, args.path)                    else:

                        print(f"  ✓ {change}")

    print(f"Wrote {len(patches)} per-file patches to artifacts/patches/ and aggregated patch to {aggregated_patch_path}")        elif change_list:

            # Has messages but no changes (errors/skips)

    if args.apply:            for change in change_list:

        if not args.confirm_apply:                if change.startswith("SKIP:"):

            raise RuntimeError("--apply requires --confirm-apply for safety. Re-run with --confirm-apply to proceed.")                    skipped_files.append((filepath, change))

        print("Applying patches to files (backups created). This is destructive.")                elif change.startswith("ERROR:"):

        apply_patches_write_files(patches, confirm=args.confirm_apply)                    error_files.append((filepath, change))



    if args.git_apply:    # Summary

        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")    print(f"\n{'='*70}")

        branch = f"migration/matriz-{ts}"    print(f"SUMMARY")

        git_apply_patch(aggregated_patch_path, branch)    print(f"{'='*70}")

    print(f"Files scanned:    {len(python_files)}")

    manifest = {"files_changed": [p["file"] for p in patches], "count": len(patches)}    print(f"Files changed:    {len(changed_files)}")

    Path("artifacts/matriz_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")    print(f"Total changes:    {total_changes}")

    print("Wrote artifacts/matriz_manifest.json")    print(f"Files skipped:    {len(skipped_files)}")

    print(f"Files with errors: {len(error_files)}")

    print(f"{'='*70}\n")

if __name__ == "__main__":

    main()    if changed_files:

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
        print(f"   Backup files created with .bak extension")
        print(f"\nNext steps:")
        print(f"  1. Run tests: make smoke && python3 -m pytest")
        print(f"  2. Verify imports: python3 -c 'import MATRIZ; print(\"OK\")'")
        print(f"  3. Review changes: git diff")
        print(f"  4. Commit: git add -A && git commit -m 'fix(imports): matriz → MATRIZ'")

    return 0 if not error_files else 1


if __name__ == '__main__':
    sys.exit(main())
