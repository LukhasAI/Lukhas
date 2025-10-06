#!/usr/bin/env python3
"""
Migrate documentation files to module-local docs/ directories.

Uses git mv for history preservation.
Creates redirect stubs at old paths.
Injects frontmatter if missing.

Only migrates files with confidence ≥0.80 from mapping.
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict

ART = Path("artifacts")
MAPPING_FILE = ART / "docs_mapping.json"
MIN_CONFIDENCE = 0.80


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
    stub_content = f"""# Moved to {new_path}

This file has been moved to a module-local docs directory.

**New location**: [{new_path}]({new_path.relative_to(old_path.parent)})

This redirect stub will be removed in a future release.
"""

    old_path.write_text(stub_content)
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
            continue

        # Skip if already in module directory
        if "docs" in file_path.parts and file_path.parts[file_path.parts.index("docs") - 1] == module:
            continue

        # Determine target path
        # If in docs/<module>/, move to <module>/docs/
        if "docs" in file_path.parts:
            docs_idx = file_path.parts.index("docs")
            if docs_idx + 1 < len(file_path.parts) and file_path.parts[docs_idx + 1] == module:
                # Already correctly structured as docs/<module>/...
                # Move to <module>/docs/...
                relative_parts = file_path.parts[docs_idx + 2:]  # Skip docs/<module>/
                new_path = Path(module) / "docs" / Path(*relative_parts) if relative_parts else Path(module) / "docs" / file_path.name
            else:
                # docs/ with no module subdirectory
                new_path = Path(module) / "docs" / file_path.name
        else:
            # Not in docs/ directory, just move to module/docs/
            new_path = Path(module) / "docs" / file_path.name

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
