#!/usr/bin/env python3
"""
Migrate documentation files to module-local docs/ directories.

Uses git mv for history preservation.
Creates redirect stubs at old paths.
Injects frontmatter if missing.

Only migrates files with confidence ≥0.80 from mapping.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

ART = Path("artifacts")
MAPPING_FILE = ART / "docs_mapping.json"
MIN_CONFIDENCE = 0.80

PROTECTED_ROOTS = {
    "docs/_generated",
    "docs/ADR",
    "docs/architecture",
    "docs/research",
    "docs/domain_strategy",
    "docs/collaboration",
    "docs/roadmap",
    "docs/releases",
    "docs/mcp",
    "docs/observability",
}


def posix_relpath(dst: Path, src_dir: Path) -> str:
    """Return a POSIX-style relative path from src_dir → dst."""
    rel = os.path.relpath(dst.as_posix(), start=src_dir.as_posix())
    return rel.replace("\\", "/")


def should_skip_root_doc(file_path: Path) -> bool:
    """Check if file is in a protected root doc directory."""
    path_str = str(file_path)
    return any(path_str.startswith(prefix) for prefix in PROTECTED_ROOTS)


def already_in_correct_location(file_path: Path, module_path: str) -> bool:
    """Check if file is already in the correct module/docs/ location."""
    try:
        parts = file_path.parts
        if "docs" in parts:
            docs_idx = parts.index("docs")
            if docs_idx > 0:
                current_module = str(Path(*parts[:docs_idx]))
                return current_module == module_path
        return False
    except Exception:
        return False


def load_mapping() -> Dict[str, Dict]:
    """Load docs mapping from artifacts."""
    if not MAPPING_FILE.exists():
        print(f"❌ Mapping file not found: {MAPPING_FILE}")
        print("   Run: make docs-map first")
        sys.exit(1)

    return json.loads(MAPPING_FILE.read_text())


def inject_frontmatter(file_path: Path, module: str):
    """Inject frontmatter if missing."""
    content = file_path.read_text()

    # Skip if already has frontmatter
    if content.startswith("---"):
        return

    # Extract title from first heading or filename
    title = file_path.stem.replace("_", " ").replace("-", " ").title()
    for line in content.splitlines()[:10]:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    frontmatter = f"""---
module: {module}
title: {title}
---

"""

    file_path.write_text(frontmatter + content)
    print(f"  ✅ Injected frontmatter: {file_path}")


def create_redirect_stub(old_path: Path, new_path: Path):
    """Create a redirect stub at the old path."""
    # Only create stubs for items originally under root docs/
    if not old_path.as_posix().startswith("docs/"):
        return
    # Skip protected roots
    if should_skip_root_doc(old_path):
        return

    src_dir = old_path.parent
    rel = posix_relpath(new_path, src_dir)
    ts = datetime.now().isoformat(timespec="seconds")

    stub_content = f"""---
redirect: true
moved_to: "{rel}"
moved_at: "{ts}"
---

> This document was moved to `{rel}` to colocate module docs.
> Redirect created by T4/0.01% migration toolchain.
"""

    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text(stub_content, encoding="utf-8")
    print(f"  📍 Created redirect stub: {old_path}")


def git_mv(old_path: Path, new_path: Path) -> bool:
    """Move file using git mv (preserves history)."""
    try:
        # Ensure target directory exists
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Use git mv for history preservation
        result = subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            capture_output=True,
            text=True,
            check=True
        )

        return True

    except subprocess.CalledProcessError as e:
        print(f"  ❌ git mv failed: {e.stderr}")
        return False


def migrate_docs(mapping: Dict[str, Dict], dry_run: bool = False):
    """Migrate documentation files based on mapping."""
    moved_count = 0
    skipped_count = 0

    for file_path_str, info in mapping.items():
        file_path = Path(file_path_str)

        # Skip low confidence items
        if info["confidence"] < MIN_CONFIDENCE:
            skipped_count += 1
            continue

        module = info["module"]

        # Skip root module (stays in docs/)
        if module == "root":
            skipped_count += 1
            continue

        # Normalize module path (convert dots to slashes)
        module_path = module.replace(".", "/")

        # Skip protected root docs
        if should_skip_root_doc(file_path):
            skipped_count += 1
            if dry_run:
                print(f"⏭️  SKIP (protected): {file_path}")
            continue

        # Skip if already in correct location
        if already_in_correct_location(file_path, module_path):
            skipped_count += 1
            if dry_run:
                print(f"✓  OK (already correct): {file_path}")
            continue

        # Compute target: <module_path>/docs/<filename>
        new_path = Path(module_path) / "docs" / file_path.name

        # Skip if target already exists (duplicate)
        if new_path.exists():
            skipped_count += 1
            if dry_run:
                print(f"⚠️  SKIP (duplicate exists): {file_path} (target: {new_path})")
            continue

        if dry_run:
            print(f"📋 Would move: {file_path} → {new_path} (confidence: {info['confidence']}, strategy: {info['strategy']})")
            continue

        print(f"🔄 Migrating: {file_path} → {new_path}")

        # Perform git mv
        if git_mv(file_path, new_path):
            # Inject frontmatter if missing
            inject_frontmatter(new_path, module)

            # Create redirect stub
            create_redirect_stub(file_path, new_path)

            moved_count += 1
        else:
            print(f"  ⚠️  Failed to move: {file_path}")
            skipped_count += 1

    return moved_count, skipped_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migrate docs to module-local directories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    args = parser.parse_args()

    print("📦 Loading documentation mapping...")
    mapping = load_mapping()

    # Filter high-confidence items
    high_confidence = {k: v for k, v in mapping.items() if v["confidence"] >= MIN_CONFIDENCE}
    total = len(mapping)
    eligible = len([v for v in high_confidence.values() if v["module"] != "root"])

    print(f"📊 Total files: {total}")
    print(f"   High confidence (≥{MIN_CONFIDENCE}): {len(high_confidence)} ({len(high_confidence)/total*100:.1f}%)")
    print(f"   Eligible for migration: {eligible}")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")

    moved, skipped = migrate_docs(mapping, dry_run=args.dry_run)

    print(f"\n✅ Migration complete!")
    print(f"   Moved: {moved} files")
    print(f"   Skipped: {skipped} files")

    if args.dry_run:
        print("\n💡 Run without --dry-run to execute migration")

    return 0


if __name__ == "__main__":
    sys.exit(main())
